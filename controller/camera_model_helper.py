import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PySide6.QtCore import QTimer

from controller.path_manager import path_manager

logger = path_manager.get_logger("CameraModel")

class CameraModel:
    def __init__(self, view):
        self.view = view
        self.cap = None
        self.face_detected = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_feed)
        
        # Initialize MediaPipe face detection
        model_path = path_manager.get_path('face_model')
        logger.info(f"Loading face detection model from: {model_path}")
        self.mp_face_detection = vision.FaceDetector.create_from_options(
            vision.FaceDetectorOptions(
                base_options=python.BaseOptions(
                    model_asset_path=model_path
                ),
                min_detection_confidence=0.7
            )
        )
        
        # Safe initialization of camera
        self.safe_initialize_camera()

    def safe_initialize_camera(self):
        """Initialize camera with safe checks for view components."""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise ValueError("Camera not accessible.")
            
            # Safely set UI elements if they exist
            if hasattr(self.view, 'start_camera_button'):
                self.view.start_camera_button.setEnabled(True)
            if hasattr(self.view, 'stop_camera_button'):
                self.view.stop_camera_button.setDisabled(True)
                
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            self.cap = None
            if hasattr(self.view, 'cam_label'):
                self.view.cam_label.setText("Camera not available")
            if hasattr(self.view, 'start_camera_button'):
                self.view.start_camera_button.setDisabled(True)
            if hasattr(self.view, 'stop_camera_button'):
                self.view.stop_camera_button.setDisabled(True)

    def start_camera(self):
        """Start the camera feed."""
        if self.cap is None:
            self.safe_initialize_camera()
        
        if self.cap and self.cap.isOpened():
            if hasattr(self.view, 'start_camera_button'):
                self.view.start_camera_button.setDisabled(True)
            if hasattr(self.view, 'stop_camera_button'):
                self.view.stop_camera_button.setEnabled(True)
            self.timer.start(50)  # Update every 50ms

    def stop_camera(self):
        """Stop the camera feed."""
        try:
            if hasattr(self, 'timer') and self.timer.isActive():
                self.timer.stop()
        except RuntimeError:
            pass  # Timer might already be deleted
            
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        
        if hasattr(self.view, 'controller'):
            self.view.controller.stop()
            
        if hasattr(self.view, 'start_camera_button'):
            self.view.start_camera_button.setEnabled(True)
        if hasattr(self.view, 'stop_camera_button'):
            self.view.stop_camera_button.setDisabled(True)
        if hasattr(self.view, 'cam_label'):
            self.view.cam_label.clear()


    def update_camera_feed(self):
        """Update the video feed with optimized color processing and face detection."""
        if self.cap is None or not self.cap.isOpened():
            return

        try:
            # Capture frame
            ret, frame = self.cap.read()
            if not ret:
                logger.error("Failed to capture frame")
                return

            # Convert BGR to RGB properly
            processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
            # Face detection (MediaPipe expects RGB)
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=processed_frame)
            results = self.mp_face_detection.detect(image)
                
            # Draw detections on original frame (BGR for OpenCV drawing)
            if results.detections:
                self.face_detected = True
                for detection in results.detections:
                    bbox = detection.bounding_box
                    x = bbox.origin_x
                    y = bbox.origin_y
                    w = bbox.width
                    h = bbox.height
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            else:
                self.face_detected = False
                
            # For display, we'll use the RGB frame with detections
            display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
            # Resize for display
            display_frame = cv2.resize(display_frame, (300, 200))

            # Update view
            if hasattr(self.view, 'update_camera_feed'):
                self.view.update_camera_feed(display_frame)

            # Control stopwatch
            if hasattr(self.view, 'controller'):
                if self.face_detected:
                    self.view.controller.start()
                else:
                    self.view.controller.stop()

        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            self.stop_camera()

    def cleanup(self):
        """Explicit cleanup method to call when done."""
        self.stop_camera()
        if hasattr(self, 'mp_face_detection'):
            self.mp_face_detection.close()

    def __del__(self):
        """Fallback cleanup if explicit cleanup wasn't called."""
        try:
            self.cleanup()
        except Exception:
            pass  # Prevent any exceptions during garbage collection