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
    

    def tab1_setup(self):
        """Setup the first tab with Stopwatch and Todo views."""
        tab1 = QWidget()
        tab1_layout = QHBoxLayout(tab1)
        
        # Add Stopwatch and Todo views to the layout
        tab1_layout.addWidget(self.StopwatchView)
        tab1_layout.addWidget(self.TodoView)
        self.setCentralWidget(tab1)
        return tab1
    

    def process(self):
        self.markdown = MarkdownHandler()
        self.TodoView.helper.db.save_daily_data(data=self.StopwatchView.controller.export_vars())
        self.markdown.markdown_helper()

        
    def close(self):
        self.process()
        self.TodoView.helper.close()
        stop_tracking()
        self.GitView.controller.commit_and_push()
    
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