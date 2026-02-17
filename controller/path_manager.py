import os
import sys
import logging
from pathlib import Path

class PathManager:
    """
    Manages all paths for the application, ensuring they work correctly both 
    in development (python main.py) and as a standalone binary (Nuitka).
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PathManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        # 1. Determine the base directory
        # If running as a standalone app (e.g., from Nuitka)
        if getattr(sys, 'frozen', False):
            # For Nuitka/PyInstaller, the executable location
            self.app_dir = Path(sys.executable).parent
        else:
            # For development, the current script's parent's parent (assuming it's in controller/)
            self.app_dir = Path(__file__).parent.parent.absolute()

        # 2. Define Assets Directory
        # The user wants "assets" directory structure to be preserved outside the binary
        self.assets_dir = self.app_dir / "assets"
        
        # Ensure directories exist
        self.resource_dir = self.assets_dir / "resource"
        self.data_dir = self.resource_dir / "data"
        self.update_dir = self.resource_dir / "Daily_Update"
        self.logs_dir = self.assets_dir / "logs"
        self.images_dir = self.assets_dir / "images"
        
        for d in [self.assets_dir, self.resource_dir, self.data_dir, self.update_dir, self.logs_dir, self.images_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
        # 3. Specific File Paths
        self.db_path = self.data_dir / "main.db"
        self.git_config_path = self.data_dir / "git_config.json"
        self.markdown_path = self.update_dir / "README.md"
        self.face_model_path = self.assets_dir / "blaze_face_short_range.tflite"
        self.log_file = self.logs_dir / "app.log"
        self.graph_html = self.data_dir / "graph.html"
        
        # 4. Setup Logging
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("ProductivityTracker")
        self.logger.info(f"Initialized PathManager. App Dir: {self.app_dir}")

    def get_path(self, path_type):
        paths = {
            'db': str(self.db_path),
            'git_config': str(self.git_config_path),
            'markdown': str(self.markdown_path),
            'face_model': str(self.face_model_path),
            'daily_update': str(self.update_dir),
            'assets': str(self.assets_dir),
            'logs': str(self.log_file),
            'graph': str(self.graph_html)
        }
        return paths.get(path_type)

    def get_icon_path(self, icon_name):
        """Returns the absolute path for an icon in assets/images/icons/."""
        return str(self.images_dir / "icons" / icon_name)

    def get_logger(self, name):
        return logging.getLogger(f"ProductivityTracker.{name}")

# Global instance for easy access
path_manager = PathManager()
