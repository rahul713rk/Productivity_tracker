from datetime import datetime
from pathlib import Path
import json
import os
import subprocess
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QLineEdit, QMessageBox, QDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class GitHandler:
    def __init__(self):
        # Get the application's root directory
        self.local_path = os.path.abspath("./resources/db/Daily_update/")
        self.app_root = self._get_app_root()
        self.config_path = self._get_config_path()
        self.data = False
        self.load_config()

    def _get_app_root(self):
        """Get the absolute path of the application root directory"""
        if getattr(sys, 'frozen', False):
            # If running as compiled executable
            return Path(sys.executable).parent
        else:
            # If running as script
            return Path(__file__).parent.parent

    def _get_config_path(self):
        """Get the absolute path for the config file"""
        config_dir = self.app_root / "resources" / "others"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "git_config.json"

    def load_config(self):
        """Load Git credentials from a config file"""
        default_config = {
            "username": "",
            "email": "",
            "repo_name": "", 
            "token": ""
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Update with new fields while preserving existing ones
                    default_config.update(config)
            
            for key, value in default_config.items():
                setattr(self, key, value)
            
            if default_config['username']:
                print("Git Configuration Data Loaded from json file")
                self.data = True
                
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load configuration: {str(e)}")
            for key, value in default_config.items():
                setattr(self, key, value)

    def save_config(self, username, email, repo_name, token):
        """Save Git credentials to a config file"""
        try:
            config_data = {
                "username": username,
                "email": email,
                "repo_name": repo_name,
                "token": token
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=4)
                
            # Update instance variables
            for key, value in config_data.items():
                setattr(self, key, value)
            
            print("Git Configuration saved")
            return True
                
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save configuration: {str(e)}")
            return False

    def verify_git_installation(self):
        """Verify that Git is installed and accessible"""
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True)
            print('Git is installed')
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            QMessageBox.critical(None, "Error", "Git is not installed or not accessible")
            return False

    def setup_git(self):
        """Configure Git with saved username and email"""
        try:
            if not self.verify_git_installation():
                return False

            if not self.username or not self.email:
                raise ValueError("Git username and email are required")
            
            # Set git configurations
            subprocess.run(['git', 'config', '--global', 'user.name', self.username], 
                         check=True, capture_output=True, text=True)
            subprocess.run(['git', 'config', '--global', 'user.email', self.email], 
                         check=True, capture_output=True, text=True)
            
            print('Git config set with username and email')
            
            # Initialize repository if needed
            repo_path = Path(self.local_path)
            if not (repo_path / '.git').exists():
                self.initialize_repository()
            
            return True
                
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(None, "Error", f"Git configuration failed: {e.stderr}")
            return False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Git setup error: {str(e)}")
            return False
    
    def get_remote_url(self):
        """Construct the remote URL for the repository"""
        return f"https://{self.username}:{self.token}@github.com/{self.username}/{self.repo_name}.git"

    def initialize_repository(self):
        """Initialize a new Git repository and set up remote"""
        try:
            repo_path = Path(self.local_path)
            if not repo_path.is_dir():
                QMessageBox.critical(None, "Error", "Add task and then commit")
                return False

            os.chdir(repo_path)

            # Initialize new repository
            subprocess.run(['git', 'init'], check=True, capture_output=True)
            print('Git init .. ')

            # Set main as default branch
            subprocess.run(['git', 'branch', '-M', 'main'], 
                        check=True, capture_output=True)
            print('Git branch -M main')

            # Initial commit
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            print("Git Add")
            subprocess.run(['git', 'commit', '-m', "Initial commit"], 
                        check=True, capture_output=True)
            print('Git Commit (initial)')

            # Set up remote and pull
            subprocess.run(['git', 'remote', 'add', 'origin', self.get_remote_url()], 
                        check=True, capture_output=True)
            print('Git remote add origin')

            return True

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(None, "Error", f"Repository initialization failed: {e.stderr}")
            return False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Repository initialization error: {str(e)}")
            return False

    def commit_and_push(self):
        """Perform Git commit and push using Personal Access Token for authentication"""
        if not self.data:
            QMessageBox.warning(None, "Warning", "Please configure Git account first")
            return False

        reply = QMessageBox.question(
            None, 
            "Confirm", 
            "Do you want to commit and push to GitHub?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return False

        try:
            if not self.verify_git_installation():
                return False
            
            repo_path = Path(self.local_path)
            if not (repo_path / '.git').exists():
                if not self.initialize_repository():
                    QMessageBox.critical(None, "Error", f"Invalid repository path: {repo_path}")
                    return False

            os.chdir(repo_path)

            # Check for changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                capture_output=True, text=True, check=True)
            print('Checking status')
            if not result.stdout.strip():
                QMessageBox.information(None, "Info", "No changes to commit")
                return True

            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            print("Git Add")

            # Commit changes
            date = datetime.now().strftime('%Y-%m-%d')
            commit_message = f'{date} : Auto Commit'
            subprocess.run(['git', 'commit', '-m', commit_message], 
                        check=True, capture_output=True)
            print('Git Commit (Auto)')

            # Set up environment for authentication
            git_env = {
                **os.environ,
                'GIT_ASKPASS': 'echo',
                'GIT_USERNAME': self.username,
                'GIT_PASSWORD': self.token
            }

            # Push to remote using token
            push_result = subprocess.run(
                ['git', 'push', '-u', 'origin', 'main'],
                env=git_env,
                capture_output=True,
                text=True
            )

            if push_result.returncode != 0:
                try:
                    subprocess.run(['git', 'push', 'origin', 'main', '--force'], check=True)
                    print('Git push --force')
                except subprocess.CalledProcessError as e:
                    QMessageBox.critical(None, "Error", f"Unexpected error: {str(e)}")
                    return False
            print('Git push')

            QMessageBox.information(None, "Success", "Changes pushed to GitHub successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            QMessageBox.critical(None, "Error", f"Git operation failed: {error_msg}")
            return False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Unexpected error: {str(e)}")
            return False


class AccountDialog(QDialog):
    """Dialog for entering Git account information"""
    def __init__(self, git_handler, parent=None):
        super().__init__(parent)
        self.git_handler = git_handler
        self.setWindowTitle("Link Git Account")
        self.setModal(True)
        self.resize(400, 300)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Username
        layout.addWidget(QLabel("Git Username:"))
        self.username_entry = QLineEdit()
        self.username_entry.setText(self.git_handler.username)
        layout.addWidget(self.username_entry)
        
        # Email
        layout.addWidget(QLabel("Git Email:"))
        self.email_entry = QLineEdit()
        self.email_entry.setText(self.git_handler.email)
        layout.addWidget(self.email_entry)
        
        # Repository Name
        layout.addWidget(QLabel("Repository Name:"))
        self.repo_entry = QLineEdit()
        self.repo_entry.setText(self.git_handler.repo_name)
        layout.addWidget(self.repo_entry)
        
        # Access Token
        layout.addWidget(QLabel("GitHub Token:"))
        self.token_entry = QLineEdit()
        self.token_entry.setEchoMode(QLineEdit.Password)
        self.token_entry.setText(self.git_handler.token)
        layout.addWidget(self.token_entry)
        
        # Save Button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_details)
        layout.addWidget(save_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        
    def save_details(self):
        username = self.username_entry.text().strip()
        email = self.email_entry.text().strip()
        repo_name = self.repo_entry.text().strip()
        token = self.token_entry.text().strip()

        if not all([username, email, repo_name, token]):
            QMessageBox.warning(self, "Warning", "All fields are required!")
            return

        if self.git_handler.save_config(username, email, repo_name, token):
            self.git_handler.setup_git()
            self.accept()


class GitApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git Auto-Commit")
        self.resize(500, 300)
        
        # Initialize GitHandler
        self.git_handler = GitHandler()
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        
        self.init_ui()
        
    def init_ui(self):
        # Title
        title_label = QLabel("Git Auto-Commit")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title_label)
        
        # Status Label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.update_status()
        self.main_layout.addWidget(self.status_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        link_btn = QPushButton("Link Account")
        link_btn.clicked.connect(self.open_account_dialog)
        buttons_layout.addWidget(link_btn)
        
        push_btn = QPushButton("Commit & Push")
        push_btn.clicked.connect(self.git_handler.commit_and_push)
        buttons_layout.addWidget(push_btn)
        
        self.main_layout.addLayout(buttons_layout)
        
    def update_status(self):
        """Update status label based on Git configuration"""
        if self.git_handler.username and self.git_handler.repo_name:
            status_text = (f"Linked Account: {self.git_handler.username}\n"
                         f"Repository: {self.git_handler.repo_name}")
        else:
            status_text = "No account linked"
            
        self.status_label.setText(status_text)
        
    def open_account_dialog(self):
        """Open the account configuration dialog"""
        dialog = AccountDialog(self.git_handler, self)
        if dialog.exec() == QDialog.Accepted:
            self.update_status()


