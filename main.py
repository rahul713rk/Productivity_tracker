import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QGroupBox, QListWidget, QMessageBox
)
from view.stopwatch_view import StopwatchView
from controller.activivty_tracker import start_tracking, stop_tracking

# if __name__ == "__main__":
#     app = QApplication(sys.argv)    
#     window = StopwatchView()
#     start_tracking(window.controller)
#     window.show()
#     app.aboutToQuit.connect(stop_tracking)
#     sys.exit(app.exec())



from PySide6.QtWidgets import QApplication
from view.todo_view import TodoView
from controller.todo_helper import TodoHelper
# from tracker.todo import Todo

if __name__ == "__main__":
    app = QApplication([])
    
    main_window = QWidget()
    main_window.setWindowTitle("Productivity Tracker")
    tab1 = QHBoxLayout(main_window)
    stopwatch = StopwatchView()
    view = TodoView()
    start_tracking(stopwatch.controller)

    tab1.addWidget(stopwatch)
    tab1.addWidget(view)

    main_window.show()

    app.aboutToQuit.connect(stop_tracking)
    app.exec()

    # controller.close_resources()
