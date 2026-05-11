import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import QMessageBox

from controller.path_manager import path_manager

logger = path_manager.get_logger("GitHandler")

class GitHandler:
    def __init__(self):
        self.local_path = path_manager.get_path('daily_update')
        self.config_path = path_manager.get_path('git_config')
        self.data = False
        logger.info(f"GitHandler initialized with local_path: {self.local_path}")
        self.load_config()


    def load_config(self):
        default_config = {
            "username": "",
            "email": "",
            "repo_name": "",
            "token": ""
        }

        if not os.path.exists(self.config_path):
            logger.info("Config file missing, using defaults")
            for key, value in default_config.items():
                setattr(self, key, value)
            return

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                default_config.update(config)

            for key, value in default_config.items():
                setattr(self, key, value)

            if default_config['username']:
                logger.info("Git Configuration Data Loaded from json file")
                self.data = True

        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not load git config, using defaults: {e}")
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

            logger.info("Git Configuration saved")
            return True

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save configuration: {str(e)}")
            return False

    @staticmethod
    def verify_git_installation():
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True)
            logger.info('Git is installed')
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            QMessageBox.critical(None, "Error", "Git is not installed or not accessible")
            return False

    def _run_git_command(self, args, env=None, error_msg="Git command failed"):
        """Helper to run git commands with consistent error handling."""
        try:
            # Always run in local_path synchronously
            result = subprocess.run(
                args,
                cwd=self.local_path,
                env=env or os.environ,
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug(f"Executed command: {' '.join(args)}")
            return result
        except subprocess.CalledProcessError as e:
            err = e.stderr.strip() if e.stderr else str(e)
            logger.error(f"{error_msg}: {err}")
            raise Exception(f"{error_msg}: {err}")

    def setup_git(self):
        try:
            if not self.verify_git_installation():
                return False

            if not self.username or not self.email:
                raise ValueError("Git username and email are required")

            # Set global config
            subprocess.run(['git', 'config', '--global', 'user.name', self.username], check=True)
            subprocess.run(['git', 'config', '--global', 'user.email', self.email], check=True)

            logger.info(f"Git global config set for {self.username}")

            repo_path = Path(self.local_path)
            if not (repo_path / '.git').exists():
                self.initialize_repository()

            return True

        except Exception as e:
            QMessageBox.critical(None, "Git Setup Error", str(e))
            return False

    def get_remote_url(self):
        return f"https://{self.username}:{self.token}@github.com/{self.username}/{self.repo_name}.git"

    def initialize_repository(self):
        try:
            repo_path = Path(self.local_path)
            if not repo_path.exists():
                repo_path.mkdir(parents=True, exist_ok=True)
            
            # Use helper to run commands in the correct CWD
            self._run_git_command(['git', 'init'], error_msg="Init failed")
            self._run_git_command(['git', 'branch', '-M', 'main'], error_msg="Branch naming failed")
            
            # Check if there are files to add (excluding .git)
            if any(f for f in repo_path.iterdir() if f.name != '.git'):
                self._run_git_command(['git', 'add', '.'], error_msg="Add failed")
                self._run_git_command(['git', 'commit', '-m', "Initial commit"], error_msg="Initial commit failed")
            
            # Remote setup
            try:
                self._run_git_command(['git', 'remote', 'add', 'origin', self.get_remote_url()], error_msg="Remote add failed")
            except Exception:
                # If origin exists, update it
                self._run_git_command(['git', 'remote', 'set-url', 'origin', self.get_remote_url()], error_msg="Remote set-url failed")
            
            logger.info("Git repository initialized successfully")
            return True

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Repository initialization error: {str(e)}")
            return False

    def commit_and_push(self):
        if not self.data:
            return False

        reply = QMessageBox.question(
            None, "Confirm", "Do you want to commit and push to GitHub?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes: return False

        try:
            if not self.verify_git_installation(): return False

            repo_path = Path(self.local_path)
            if not (repo_path / '.git').exists():
                if not self.initialize_repository(): return False

            # Check status
            status = self._run_git_command(['git', 'status', '--porcelain'], error_msg="Status check failed")
            if not status.stdout.strip():
                QMessageBox.information(None, "Info", "No changes to commit")
                return True

            git_env = {**os.environ, 'GIT_ASKPASS': 'echo', 'GIT_USERNAME': self.username, 'GIT_PASSWORD': self.token}

            # Stash, Fetch, Rebase, Pop
            logger.info("Performing sync with remote...")
            self._run_git_command(['git', 'stash'], env=git_env, error_msg="Stash failed")
            
            try:
                self._run_git_command(['git', 'fetch', 'origin', 'main'], env=git_env, error_msg="Fetch failed")
                self._run_git_command(['git', 'rebase', 'origin/main'], env=git_env, error_msg="Rebase failed")
            except Exception as e:
                self._run_git_command(['git', 'rebase', '--abort'], env=git_env)
                self._run_git_command(['git', 'stash', 'pop'], env=git_env)
                raise e

            self._run_git_command(['git', 'stash', 'pop'], env=git_env, error_msg="Stash pop failed")

            # Add, Commit, Push
            self._run_git_command(['git', 'add', '.'], env=git_env, error_msg="Add files failed")
            
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f'Productivity Update: {date}'
            self._run_git_command(['git', 'commit', '-m', commit_msg], env=git_env, error_msg="Commit failed")
            
            self._run_git_command(['git', 'push', 'origin', 'main'], env=git_env, error_msg="Push failed")

            QMessageBox.information(None, "Success", "Changes pushed to GitHub successfully!")
            return True

        except Exception as e:
            QMessageBox.critical(None, "Git Sync Error", str(e))
            return False

    def silent_commit_and_push(self):
        """Performs Git sync without prompting the GUI (safe for background threads)."""
        if not self.data:
            return False

        try:
            if not self.verify_git_installation(): return False

            repo_path = Path(self.local_path)
            if not (repo_path / '.git').exists():
                # initialize_repository has info QMessageBoxes, but inside a thread they fail.
                # However, usually the repo is initialized by the time we quit. 
                # For safety, let's just create it directly if possible.
                pass # Skipping init for silent sync to avoid UI freezes

            status = self._run_git_command(['git', 'status', '--porcelain'], error_msg="Status check failed")
            if not status.stdout.strip():
                return True

            git_env = {**os.environ, 'GIT_ASKPASS': 'echo', 'GIT_USERNAME': self.username, 'GIT_PASSWORD': self.token}
            self._run_git_command(['git', 'stash'], env=git_env, error_msg="Stash failed")
            
            try:
                self._run_git_command(['git', 'fetch', 'origin', 'main'], env=git_env, error_msg="Fetch failed")
                self._run_git_command(['git', 'rebase', 'origin/main'], env=git_env, error_msg="Rebase failed")
            except Exception as e:
                self._run_git_command(['git', 'rebase', '--abort'], env=git_env)
                self._run_git_command(['git', 'stash', 'pop'], env=git_env)
                raise e

            self._run_git_command(['git', 'stash', 'pop'], env=git_env, error_msg="Stash pop failed")
            self._run_git_command(['git', 'add', '.'], env=git_env, error_msg="Add files failed")
            
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f'Productivity Update: {date}'
            self._run_git_command(['git', 'commit', '-m', commit_msg], env=git_env, error_msg="Commit failed")
            self._run_git_command(['git', 'push', 'origin', 'main'], env=git_env, error_msg="Push failed")
            return True
        except Exception as e:
            logger.error(f"Silent Sync Error: {e}")
            raise e