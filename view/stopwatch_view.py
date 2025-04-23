import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap , QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QGroupBox, QListWidget, QMessageBox
)
from controller.stopwatch_helper import StopwatchController
from controller.camera_model_helper import CameraModel
from view.style import StyleUtils

class StopwatchView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = StopwatchController(self)
        self.camera_model = CameraModel(self)
        self.setup_ui()
        self.update_counts()

    def setup_ui(self):
        """Setup the entire user interface."""
        self.setWindowTitle("Stopwatch App")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout(self)

        # Stopwatch title and timer display
        stopwatch_group = QGroupBox("Stopwatch", self)
        StyleUtils.style_groupbox(stopwatch_group)

        stopwatch_layout = QHBoxLayout(stopwatch_group)

        self.timer_label = QLabel("00:00:00", self)
        self.timer_label.setStyleSheet("font-size: 48px;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        stopwatch_layout.addWidget(self.timer_label)

        main_layout.addWidget(stopwatch_group)

        # Controls (Start, Stop, Reset, Lap)
        control_group = QGroupBox("Controls", self)
        StyleUtils.style_groupbox(control_group)
        control_layout = QHBoxLayout(control_group)

        self.start_button = QPushButton("Start", self)
        self.stop_button = QPushButton("Stop", self)
        self.reset_button = QPushButton("Reset", self)
        self.lap_button = QPushButton("Lap", self)


        StyleUtils.style_primary_button(self.start_button)
        StyleUtils.style_primary_button(self.stop_button)
        StyleUtils.style_primary_button(self.reset_button)
        StyleUtils.style_primary_button(self.lap_button)

        self.start_button.clicked.connect(self.controller.start)
        self.stop_button.clicked.connect(self.controller.stop)
        self.reset_button.clicked.connect(self.controller.reset)
        self.lap_button.clicked.connect(self.controller.record_lap)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.reset_button)
        control_layout.addWidget(self.lap_button)

        main_layout.addWidget(control_group)

        # Lap records
        lap_group = QGroupBox("Lap", self)
        StyleUtils.style_groupbox(lap_group)

        lap_layout = QHBoxLayout(lap_group)

        self.lap_list_widget = QListWidget(self)
        StyleUtils.style_list_widget(self.lap_list_widget)

        lap_layout.addWidget(self.lap_list_widget)
        main_layout.addWidget(lap_group)

        # Activity Tracker (Key presses and mouse clicks)
        activity_group = QGroupBox("Activity Tracker", self)
        StyleUtils.style_groupbox(activity_group)
        activity_layout = QHBoxLayout(activity_group)

        self.key_count_label = QLabel(f"Keys: {self.controller.key_count}", self)
        self.click_count_label = QLabel(f"Clicks: {self.controller.click_count}", self)

        activity_layout.addWidget(self.key_count_label)
        activity_layout.addWidget(self.click_count_label)

        main_layout.addWidget(activity_group)

        # Camera Feed

        camera_group = QGroupBox("Camera Feed", self)
        StyleUtils.style_groupbox(camera_group)
        camera_layout = QVBoxLayout(camera_group)
        self.cam_label = QLabel("", self)
        self.cam_label.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(self.cam_label)

        camera_buttons_layout = QHBoxLayout()

        self.start_camera_button = QPushButton("", self)
        self.stop_camera_button = QPushButton("", self)

        on_camera_icon = QIcon("./assets/images/icons/video-camera.png")
        off_camera_icon = QIcon("./assets/images/icons/cam_stop.png")

        StyleUtils.style_primary_button(self.start_camera_button, on_camera_icon , icon_size=25)
        StyleUtils.style_primary_button(self.stop_camera_button, off_camera_icon , icon_size=25)

        self.start_camera_button.clicked.connect(self.camera_model.start_camera)
        self.stop_camera_button.clicked.connect(self.camera_model.stop_camera)

        camera_buttons_layout.addWidget(self.start_camera_button)
        camera_buttons_layout.addWidget(self.stop_camera_button)
        camera_layout.addLayout(camera_buttons_layout)

        main_layout.addWidget(camera_group)

        self.setLayout(main_layout)

    def update_counts(self):
        """Update key and click counts."""
        self.controller.update_counts()
        QTimer.singleShot(1000, self.update_counts)  # Update every second

    def update_timer_display(self, time_str):
        """Update the timer display."""
        self.timer_label.setText(time_str)

    def update_lap_display(self, lap_times):
        """Update lap records."""
        self.lap_list_widget.clear()
        for i, lap in enumerate(lap_times):
            formatted_time = self.controller.format_time(lap)
            self.lap_list_widget.addItem(f"Lap {i + 1}: {formatted_time}")

    def update_camera_feed(self, frame):
        """Update the camera feed."""
        qt_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap(qt_image)
        self.cam_label.setPixmap(pixmap)

    def update_activity_tracker(self, key_count, click_count):
        """Update the activity tracker labels."""
        self.key_count_label.setText(f"Keys: {key_count}")
        self.click_count_label.setText(f"Clicks: {click_count}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StopwatchView()
    window.show()
    sys.exit(app.exec())
