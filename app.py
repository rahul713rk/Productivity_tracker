from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QSplitter
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSettings, QRect
import sys
import logging
from tracker.database import Database
from tracker.stopwatch import StopwatchApp
from tracker.todo import Todo
from tracker.markdown_handler import MarkdownHandler
from tracker.activity_tracker import start_tracking, stop_tracking
from setting.git import GitApp
from setting.dataviewer import DataViewerApp
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

class ProductivityTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productivity Tracker")

        # Load window configuration from QSettings

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)
        # self.settings = QSettings("Company", "ProductivityTracker")
        # self.load_window_settings()

        # Set window icon
        icon_path = Path(__file__).parent / "resources" / "others" / "icon.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Central widget and tab layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        self.tab_widget.addTab(self.tab1, "Stopwatch & To-Do List")
        self.tab_widget.addTab(self.tab2, "Database")
        self.tab_widget.addTab(self.tab3, "Accounts")

        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()

    def setup_tab1(self):
        splitter = QSplitter(Qt.Horizontal)
        self.stopwatch = StopwatchApp()
        self.todo_list = Todo()

        splitter.addWidget(self.stopwatch)
        splitter.addWidget(self.todo_list)

        # Optional: Set initial splitter sizes
        splitter.setSizes([600, 400])

        tab1_layout = QVBoxLayout(self.tab1)
        tab1_layout.addWidget(splitter)

        start_tracking(self.stopwatch)

    def setup_tab2(self):
        layout = QVBoxLayout(self.tab2)
        self.viewer = DataViewerApp()
        layout.addWidget(self.viewer)

    def setup_tab3(self):
        layout = QVBoxLayout(self.tab3)
        self.setting = GitApp()
        layout.addWidget(self.setting)

    def load_window_settings(self):
        """Load window size, position, and last tab used from settings."""
        window_geometry = self.settings.value("geometry", QRect(100, 100, 800, 600))
        self.setGeometry(window_geometry)
        last_tab = self.settings.value("lastTab", 0)
        print(f"Last tab index: {last_tab}")
        self.tab_widget.setCurrentIndex(last_tab)

    def save_window_settings(self):
        """Save window size, position, and last tab used to settings."""
        self.settings.setValue("geometry", self.geometry())
        self.settings.setValue("lastTab", self.tab_widget.currentIndex())

    def closeEvent(self, event):
        """Gracefully handle app closure."""
        self.db = Database()
        self.markdown = MarkdownHandler()
        self.db.save_daily_data(data=self.stopwatch.export_vars())
        self.markdown.markdown_helper()

        self.todo_list.close_resources()
        stop_tracking()
        self.db.close()
        self.setting.git_handler.commit_and_push()

        # Log closure
        logger.info("App closed and resources saved.")

        # Save window settings before exit
        self.save_window_settings()

        event.accept()

def main():
    app = QApplication(sys.argv)
    tracker = ProductivityTracker()
    tracker.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
