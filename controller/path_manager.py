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
        # 1. Determine the Base Directories
        
        # A. Static App Directory (Read-only assets)
        if getattr(sys, 'frozen', False):
            # For Nuitka/PyInstaller, the executable location
            self.app_dir = Path(sys.executable).parent
        else:
            # For development, the current script's parent's parent
            self.app_dir = Path(__file__).parent.parent.absolute()

        # B. User Data Directory (Writable configs, DB, Logs)
        # Use XDG_DATA_HOME if available, else fallback to ~/.local/share/
        data_home = os.environ.get('XDG_DATA_HOME')
        if data_home:
            self.user_data_dir = Path(data_home) / "productivity-tracker"
        else:
            self.user_data_dir = Path.home() / ".local" / "share" / "productivity-tracker"

        config_home = os.environ.get('XDG_CONFIG_HOME')
        if config_home:
            self.user_config_dir = Path(config_home) / "productivity-tracker"
        else:
            self.user_config_dir = Path.home() / ".config" / "productivity-tracker"
        
        # 2. Define Assets Directory (Read-only)
        self.assets_dir = self.app_dir / "assets"
        self.images_dir = self.assets_dir / "images"
        self.face_model_path = self.assets_dir / "blaze_face_short_range.tflite"

        # 3. Define Resource Directories (Writable)
        # We migrate these to user_data_dir to avoid PermissionErrors in /opt/
        self.writable_resource_dir = self.user_data_dir / "resource"
        self.data_dir = self.writable_resource_dir / "data"
        self.update_dir = self.writable_resource_dir / "Daily_Update"
        self.logs_dir = self.user_data_dir / "logs"
        
        # Ensure writable directories exist
        for d in [self.user_data_dir, self.user_config_dir, self.writable_resource_dir, self.data_dir, self.update_dir, self.logs_dir]:
            try:
                d.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                # If we can't create the directory, we might be in trouble
                # We'll print to stderr as a last resort
                print(f"CRITICAL: Failed to create directory {d}: {e}", file=sys.stderr)
            
        # 4. Specific File Paths
        self.db_path = self.data_dir / "main.db"
        self.git_config_path = self.user_config_dir / "git_config.json"
        self.markdown_path = self.update_dir / "README.md"
        self.log_file = self.logs_dir / "app.log"
        self.graph_html = self.data_dir / "graph.html"
        
        # 5. Setup Logging
        self._setup_logging()

        # 6. Ensure critical files exist with default content
        self._create_default_files()

    def _create_default_files(self):
        """Creates default files if they don't exist to prevent IOErrors."""
        import json
        
        # Default Git Config
        if not self.git_config_path.exists():
            default_git = {
                "username": "",
                "email": "",
                "repo_name": "",
                "token": ""
            }
            try:
                with open(self.git_config_path, 'w') as f:
                    json.dump(default_git, f, indent=4)
                self.logger.info(f"Created default git config at {self.git_config_path}")
            except Exception as e:
                # We use print here because logging might not be fully initialized or we want to avoid recursion
                print(f"Error creating default git config: {e}")

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
        self.logger.info(f"Initialized PathManager.")
        self.logger.info(f"App Directory (read-only assets): {self.app_dir}")
        self.logger.info(f"User Data Directory (writable): {self.user_data_dir}")
        self.logger.info(f"Config Directory (writable): {self.user_config_dir}")
        self.logger.info(f"Log File: {self.log_file}")

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
