from PySide6.QtWidgets import (QApplication, QMainWindow, 
                               QTabWidget, QWidget, QLabel, 
                               QHBoxLayout , QScrollArea)

from view.stopwatch_view import StopwatchView
from view.todo_view import TodoView
# from view.dataset_view import DataViewerApp
from view.dataset_view import DataViewerApp
# from view.git_view import GitView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Productivity Tracker")
        # self.setGeometry(100, 100, 400, 300)
        
        # Create the tab widget
        self.StopwatchView = StopwatchView()
        self.TodoView = TodoView()
        self.DataViewerView = DataViewerApp()
        # self.GitView = GitView()


        tabs = QTabWidget()

        
        tab2 = self.DataViewerView
        # tab3 = self.GitView

        # Add tabs to the tab widget
        tabs.addTab(self.tab1_setup(), "Home")
        tabs.addTab(tab2, "Dataset")
        # tabs.addTab(tab3, "Git")
        
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
    
    
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()