import controller.path_manager
from PySide6.QtWidgets import (QApplication, QMainWindow, 
                               QTabWidget, QWidget, QLabel, 
                               QHBoxLayout , QScrollArea , QMessageBox)

from view.stopwatch_view import StopwatchView
from view.todo_view import TodoView
from view.dataset_view import DataViewerApp
from view.git_view import GitView
from controller.activivty_tracker import start_tracking  , stop_tracking
from model.database import Database
from model.markdown import MarkdownHandler

import threading
from PySide6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Productivity Tracker")
        
        # Create the tab widget
        self.StopwatchView = StopwatchView()
        start_tracking(self.StopwatchView.controller)
        self.TodoView = TodoView()
        self.DataViewerView = DataViewerApp()
        self.GitView = GitView()


        tabs = QTabWidget()

        
        tab2 = self.DataViewerView
        tab3 = self.GitView

        # Add tabs to the tab widget
        tabs.addTab(self.tab1_setup(), "Home")
        tabs.addTab(tab2, "Dataset")
        tabs.addTab(tab3, "Git")
        
        # Set the central widget
        self.setCentralWidget(tabs)

        # Check for Wayland permissions
        self.check_wayland_permissions()

        # Initialize Auto-save timer (5 minutes)
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.process)
        self.autosave_timer.start(600000) # 600,000 ms = 10 minutes
    
    def check_wayland_permissions(self):
        import os
        from controller.activivty_tracker import check_permissions, request_permission_fix
        
        if os.environ.get('XDG_SESSION_TYPE') == 'wayland' and not check_permissions():
            reply = QMessageBox.warning(
                self,
                "Permissions Required",
                "Activity tracking requires access to input devices on Wayland.\n\n"
                "Would you like to automatically add your user to the 'input' group?\n"
                "(Note: You will need to Log Out and Log In after this for it to work.)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if request_permission_fix():
                    QMessageBox.information(
                        self,
                        "Success",
                        "Permission fixed! Please Log Out and Log Back In to enable tracking."
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to fix permissions. Please run the command manually: \n"
                        "sudo usermod -aG input $USER"
                    )
    

    def tab1_setup(self):
        """Setup the first tab with Stopwatch and Todo views."""
        tab1 = QWidget()
        tab1_layout = QHBoxLayout(tab1)
        
        # Add Stopwatch and Todo views to the layout
        tab1_layout.addWidget(self.StopwatchView)
        tab1_layout.addWidget(self.TodoView)
        return tab1
    

    def process(self):
        self.markdown = MarkdownHandler()
        self.TodoView.helper.db.save_daily_data(data=self.StopwatchView.controller.export_vars())
        self.markdown.markdown_helper()

        
    def close(self):
        self.process()
        self.StopwatchView.camera_model.stop_camera()
        self.TodoView.helper.close()
        stop_tracking()
        
        # Best solution: Use a thread for Git operations to avoid UI hang
        threading.Thread(target=self.GitView.controller.commit_and_push, daemon=True).start()
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.close()
            event.accept()
        else:
            event.ignore()
    
    
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()