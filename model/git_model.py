import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import QMessageBox

class GitHandler:
    def __init__(self):
        self.local_path = './assets/resource/Daily_Update'
        self.config_path = './assets/resource/data/git_config.json'
        self.data = False
        self.load_config()


    def load_config(self):
        default_config = {
            "username": "",
            "email": "",
            "repo_name": "",
            "token": ""
        }

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
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
        try:
            config_data = {
                "username": username,
                "email": email,
                "repo_name": repo_name,
                "token": token
            }

            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=4)

            for key, value in config_data.items():
                setattr(self, key, value)

            print("Git Configuration saved")
            return True

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save configuration: {str(e)}")
            return False

    @staticmethod
    def verify_git_installation():
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True)
            print('Git is installed')
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            QMessageBox.critical(None, "Error", "Git is not installed or not accessible")
            return False

    def setup_git(self):
        try:
            if not self.verify_git_installation():
                return False

            if not self.username or not self.email:
                raise ValueError("Git username and email are required")

            subprocess.run(['git', 'config', '--global', 'user.name', self.username],
                           check=True, capture_output=True, text=True)
            subprocess.run(['git', 'config', '--global', 'user.email', self.email],
                           check=True, capture_output=True, text=True)

            print('Git config set with username and email')

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
        return f"https://{self.username}:{self.token}@github.com/{self.username}/{self.repo_name}.git"

    def initialize_repository(self):
        try:
            repo_path = Path(self.local_path)
            if not repo_path.is_dir():
                QMessageBox.critical(None, "Error", "Add task and then commit")
                return False

            os.chdir(repo_path)

            subprocess.run(['git', 'init'], check=True, capture_output=True)
            print('Git init .. ')

            subprocess.run(['git', 'branch', '-M', 'main'],
                           check=True, capture_output=True)
            print('Git branch -M main')

            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            print("Git Add")
            subprocess.run(['git', 'commit', '-m', "Initial commit"],
                           check=True, capture_output=True)
            print('Git Commit (initial)')

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
        if not self.data:
            # QMessageBox.warning(None, "Warning", "Please configure Git account first")
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

            # Check if there are changes to commit
            result = subprocess.run(['git', 'status', '--porcelain'],
                                capture_output=True, text=True, check=True)
            if not result.stdout.strip():
                QMessageBox.information(None, "Info", "No changes to commit")
                return True

            # Set up git environment with credentials
            git_env = {
                **os.environ,
                'GIT_ASKPASS': 'echo',
                'GIT_USERNAME': self.username,
                'GIT_PASSWORD': self.token
            }

            # Stash any uncommitted changes (just in case)
            subprocess.run(['git', 'stash'], env=git_env, check=True, capture_output=True)

            try:
                # Fetch and rebase instead of pull to have cleaner history
                subprocess.run(['git', 'fetch', 'origin', 'main'], 
                            env=git_env, check=True, capture_output=True)
                subprocess.run(['git', 'rebase', 'origin/main'], 
                            env=git_env, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                # If rebase fails, abort it and notify user
                subprocess.run(['git', 'rebase', '--abort'], 
                            env=git_env, capture_output=True)
                QMessageBox.critical(None, "Error", 
                                f"Failed to rebase: {e.stderr if e.stderr else 'Merge conflicts detected'}")
                subprocess.run(['git', 'stash', 'pop'], env=git_env, capture_output=True)
                return False

            # Pop any stashed changes
            subprocess.run(['git', 'stash', 'pop'], env=git_env, capture_output=True)

            # Add and commit local changes
            subprocess.run(['git', 'add', '.'], env=git_env, check=True, capture_output=True)
            
            date = datetime.now().strftime('%Y-%m-%d')
            commit_message = f'{date} : Auto Commit'
            subprocess.run(['git', 'commit', '-m', commit_message],
                        env=git_env, check=True, capture_output=True)

            # Push changes
            push_result = subprocess.run(
                ['git', 'push', 'origin', 'main'],
                env=git_env,
                capture_output=True,
                text=True
            )

            if push_result.returncode != 0:
                QMessageBox.critical(None, "Error", 
                                f"Push failed: {push_result.stderr if push_result.stderr else 'Unknown error'}")
                return False

            QMessageBox.information(None, "Success", "Changes pushed to GitHub successfully!")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            QMessageBox.critical(None, "Error", f"Git operation failed: {error_msg}")
            return False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Unexpected error: {str(e)}")
            return False