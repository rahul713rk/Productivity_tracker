import sys
import time
import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout, QGroupBox, QListWidget, QListWidgetItem, QMessageBox

import mediapipe as mp

class StopwatchApp(QWidget):
    def __init__(self):
        super().__init__()

        # Stopwatch variables
        self.running = False
        self.color_mode = "RGB"
        self.start_time = 0
        self.elapsed_time = 0
        self.lap_times = []
        self.last_time = 0
        self.key_count = 0
        self.click_count = 0

        # Face detection variables
        self.cap = None
        self.face_detected = False
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.7)

        # Setup UI
        self.setup_ui()
        self.initialize_camera()

        # Timer for stopwatch update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer_display)
        self.timer.start(100)  # 100 ms timer for updating the stopwatch

    def setup_ui(self):
        """Setup the entire user interface."""
        self.setWindowTitle("Stopwatch App")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout(self)

        # Stopwatch title and timer display
        self.title_label = QLabel("Stopwatch", self)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.timer_label = QLabel("00:00:00", self)
        self.timer_label.setStyleSheet("font-size: 48px;")

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.timer_label)

        # Controls (Start, Stop, Reset, Lap)
        control_group = QGroupBox("Controls", self)
        control_layout = QHBoxLayout(control_group)

        self.start_button = QPushButton("Start", self)
        self.stop_button = QPushButton("Stop", self)
        self.reset_button = QPushButton("Reset", self)
        self.lap_button = QPushButton("Lap", self)

        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)
        self.reset_button.clicked.connect(self.reset)
        self.lap_button.clicked.connect(self.record_lap)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.reset_button)
        control_layout.addWidget(self.lap_button)

        main_layout.addWidget(control_group)

        # Lap records
        self.lap_list_widget = QListWidget(self)
        main_layout.addWidget(self.lap_list_widget)

        # Activity Tracker (Key presses and mouse clicks)
        activity_group = QGroupBox("Activity Tracker", self)
        activity_layout = QHBoxLayout(activity_group)

        self.key_count_label = QLabel(f"Keys: {self.key_count}", self)
        self.click_count_label = QLabel(f"Clicks: {self.click_count}", self)

        activity_layout.addWidget(self.key_count_label)
        activity_layout.addWidget(self.click_count_label)

        main_layout.addWidget(activity_group)

        # Camera Feed
        self.cam_label = QLabel("Start Camera", self)
        self.cam_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.cam_label)

        self.camera_controls = QHBoxLayout()
        self.start_camera_button = QPushButton("Start Camera", self)
        self.stop_camera_button = QPushButton("Stop Camera", self)
        self.toggle_color_button = QPushButton("Toggle Color Mode", self)

        self.start_camera_button.clicked.connect(self.start_camera)
        self.stop_camera_button.clicked.connect(self.stop_camera)
        self.toggle_color_button.clicked.connect(self.toggle_color_mode)


        self.camera_controls.addWidget(self.start_camera_button)
        self.camera_controls.addWidget(self.stop_camera_button)
        self.camera_controls.addWidget(self.toggle_color_button)

        main_layout.addLayout(self.camera_controls)

        self.setLayout(main_layout)

    def initialize_camera(self):
        """Initialize the camera."""
        if self.cap is None:
            try:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise ValueError("Camera not accessible.")
            except Exception:
                self.cap = None
                self.cam_label.setText("Camera not available")
                self.start_camera_button.setDisabled(True)
                self.stop_camera_button.setDisabled(True)

    def start_camera(self):
        """Start the camera feed."""
        try:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.start_camera_button.setDisabled(True)
                self.stop_camera_button.setEnabled(True)
                self.update_camera_feed()
        except Exception:
            print("Camera error")

    def stop_camera(self):
        """Stop the camera feed."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        self.start_camera_button.setEnabled(True)
        self.stop_camera_button.setDisabled(True)
        self.cam_label.clear()

    def toggle_color_mode(self):
            """Toggle between RGB and Grayscale mode."""
            if self.color_mode == "RGB":
                self.color_mode = "Grayscale"
            else:
                self.color_mode = "RGB"
            print(f"Color Mode changed to: {self.color_mode}")

    def update_camera_feed(self):
        """Update the video feed."""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert the frame based on the color mode selected
                if self.color_mode == "RGB":
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

                # Perform face detection
                results = self.face_detection.process(rgb_frame)

                if results.detections:
                    self.face_detected = True
                    for detection in results.detections:
                        bboxC = detection.location_data.relative_bounding_box
                        ih, iw, _ = frame.shape
                        x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                else:
                    self.face_detected = False

                # Resize the frame and convert it to QImage for display
                frame = cv2.resize(frame, (300, 200))
                if self.color_mode == "RGB":
                    qt_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                else:
                    qt_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_Grayscale8)  # Grayscale format

                # Display the image
                pixmap = QPixmap(qt_image)
                self.cam_label.setPixmap(pixmap)

            # Start or stop the stopwatch based on face detection
            if self.face_detected:
                self.start()
            else:
                self.stop()

        # Update the camera feed every 50 ms
        if self.cap and self.cap.isOpened():
            QTimer.singleShot(50, self.update_camera_feed)

    def start(self):
        """Start the stopwatch."""
        if not self.running:
            self.start_time = time.perf_counter() - self.elapsed_time
            self.running = True

    def stop(self):
        """Stop the stopwatch."""
        self.running = False

    def reset(self):
        """Reset the stopwatch."""
        reply = QMessageBox.question(self, "Confirmation", "Do you want to reset?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.running = False
            self.elapsed_time = 0
            self.lap_times.clear()
            self.update_lap_display()
            self.timer_label.setText("00:00:00")

    def record_lap(self):
        """Record a lap time."""
        if self.running:
            lap_time = self.elapsed_time - self.last_time if self.lap_times else self.elapsed_time
            self.last_time = self.elapsed_time
            self.lap_times.append(lap_time)
            if len(self.lap_times) > 5:
                self.lap_times.pop(0)
            self.update_lap_display()

    def update_lap_display(self):
        """Update lap records."""
        self.lap_list_widget.clear()
        for i, lap in enumerate(self.lap_times):
            formatted_time = self.format_time(lap)
            self.lap_list_widget.addItem(f"Lap {i + 1}: {formatted_time}")

    def update_counts(self):
        """Update key and click counts."""
        from .activity_tracker import get_count
        self.key_count, self.click_count = get_count()
        self.key_count_label.setText(f"Keys: {self.key_count}")
        self.click_count_label.setText(f"Clicks: {self.click_count}")
        QTimer.singleShot(1000, self.update_counts)  # Update every second

    def update_timer_display(self):
        """Update the timer display."""
        if self.running:
            self.elapsed_time = time.perf_counter() - self.start_time
            hours, remainder = divmod(self.elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_format = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            self.timer_label.setText(time_format)

    def format_time(self, seconds):
        """Format time in 'mm:ss' format."""
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes):02}:{int(seconds):02}"

    def export_vars(self):
        """Export relevant variables."""
        return [self.elapsed_time, self.key_count, self.click_count]

    def __del__(self):
        """Release the camera on cleanup."""
        if self.cap:
            self.cap.release()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StopwatchApp()
    window.show()
    sys.exit(app.exec())
