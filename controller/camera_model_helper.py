import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PySide6.QtCore import QObject, Signal, QThread, QTimer, Qt

from controller.path_manager import path_manager

logger = path_manager.get_logger("CameraModel")

class CameraWorker(QObject):
    """Worker class to handle camera capture and face detection in a background thread."""
    frame_ready = Signal(np.ndarray)
    face_status_changed = Signal(bool)
    error_occurred = Signal(str)

    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path
        self.cap = None
        self.running = False
        self.detector = None
        self._last_face_status = False

    def initialize_detector(self):
        """Initialize MediaPipe detector in the worker thread."""
        try:
            options = vision.FaceDetectorOptions(
                base_options=python.BaseOptions(model_asset_path=self.model_path),
                min_detection_confidence=0.7
            )
            self.detector = vision.FaceDetector.create_from_options(options)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Detector init failed: {e}")
            return False

    def start(self):
        if self.cap is not None:
            return
            
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.error_occurred.emit("Could not open camera.")
            self.cap = None
            return

        # Lower resolution at capture level for performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.running = True
        self.run_loop()

    def run_loop(self):
        """Main processing loop."""
        if not self.detector and not self.initialize_detector():
            return

        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                continue

            # 1. OPTIMIZATION: Resize IMMEDIATELY to reduce pixels processed in next steps
            # 320x240 is enough for face detection at desk distance
            small_frame = cv2.resize(frame, (320, 240))
            
            # 2. OPTIMIZATION: Convert once and use for both detection and display
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # 3. Detect
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            results = self.detector.detect(mp_image)
            
            face_detected = bool(results.detections)
            
            # 4. Draw directly on the working RGB frame if face found
            if face_detected:
                for detection in results.detections:
                    bbox = detection.bounding_box
                    start_point = (bbox.origin_x, bbox.origin_y)
                    end_point = (bbox.origin_x + bbox.width, bbox.origin_y + bbox.height)
                    cv2.rectangle(rgb_frame, start_point, end_point, (0, 255, 0), 2)

            # 5. Emit results
            self.frame_ready.emit(rgb_frame)
            if face_detected != self._last_face_status:
                self.face_status_changed.emit(face_detected)
                self._last_face_status = face_detected

        self.cleanup()

    def stop(self):
        self.running = False

    def cleanup(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.detector:
            self.detector.close()
            self.detector = None

class CameraModel(QObject):
    """Optimized coordinator for camera and face detection using background threads."""
    
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.thread = None
        self.worker = None
        self.model_path = path_manager.get_path('face_model')
        
    def start_camera(self):
        """Sets up and starts the background camera thread."""
        if self.thread and self.thread.isRunning():
            return

        self.thread = QThread()
        self.worker = CameraWorker(self.model_path)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.start)
        self.worker.frame_ready.connect(self.view.update_camera_feed)
        self.worker.face_status_changed.connect(self._handle_face_status)
        self.worker.error_occurred.connect(self._handle_error)
        
        # Ensure cleanup
        self.worker.error_occurred.connect(self.stop_camera)

        self.thread.start()
        
        if hasattr(self.view, 'start_camera_button'):
            self.view.start_camera_button.setDisabled(True)
        if hasattr(self.view, 'stop_camera_button'):
            self.view.stop_camera_button.setEnabled(True)

    def stop_camera(self):
        """Gracefully stops the worker thread."""
        try:
            # 1. Disconnect signal first to prevent last frame from overriding the clear
            if self.worker:
                try:
                    self.worker.frame_ready.disconnect()
                except (TypeError, RuntimeError):
                    pass

            # 2. Clear the frame from view immediately
            if hasattr(self.view, 'cam_label'):
                self.view.cam_label.clear()
                self.view.cam_label.setText("Camera Stopped")
                self.view.cam_label.setAlignment(Qt.AlignCenter)

            # 3. Signal worker to stop
            if self.worker:
                self.worker.stop()

            # 4. Gracefully stop thread with timeout
            if self.thread and self.thread.isRunning():
                self.thread.quit()
                if not self.thread.wait(2000):  # Wait max 2 seconds
                    logger.warning("Camera thread did not stop gracefully, terminating...")
                    self.thread.terminate()
                    self.thread.wait()
        except Exception as e:
            logger.error(f"Error during camera shutdown: {e}")
        finally:
            self.thread = None
            self.worker = None

            if hasattr(self.view, 'controller'):
                self.view.controller.stop()
            if hasattr(self.view, 'start_camera_button'):
                self.view.start_camera_button.setEnabled(True)
            if hasattr(self.view, 'stop_camera_button'):
                self.view.stop_camera_button.setDisabled(True)

    def _handle_face_status(self, is_detected):
        """Update the stopwatch controller based on face detection."""
        if hasattr(self.view, 'controller'):
            if is_detected:
                self.view.controller.start()
            else:
                self.view.controller.stop()

    def _handle_error(self, message):
        logger.error(message)
        if hasattr(self.view, 'cam_label'):
            self.view.cam_label.setText("Camera Error")

    def cleanup(self):
        self.stop_camera()