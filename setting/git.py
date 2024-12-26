from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel, filedialog
import subprocess
import json
import os
from pathlib import Path
import sys

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
            res = Path(sys.executable).parent
            print("Root file Path",res)
            return res
        else:
            # If running as script
            res = Path(__file__).parent.parent
            print("Root file Path",res)
            return res

    def _get_config_path(self):
        """Get the absolute path for the config file"""
        config_dir = self.app_root / "resources" / "others"
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
            
            if default_config['username'] != "":
                print("Git Configure Data Loaded from json file")
                self.data = True
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
            for key, value in default_config.items():
                setattr(self, key, value)

    def save_config(self, username, email, repo_name, token):
        """Save Git credentials to a config file"""
        try:
            
            # Ensure the config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
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
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            raise

    def verify_git_installation(self):
        """Verify that Git is installed and accessible"""
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True)
            print('Git is already installed')
            return True
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Git is not installed or not accessible")
            return False
        except FileNotFoundError:
            messagebox.showerror("Error", "Git executable not found in system PATH")
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
            
            print('Saving Git config with username and email')
            
            # Initialize repository if needed
            repo_path = Path(self.local_path)
            if not (repo_path / '.git').exists():
                self.initialize_repository()
            
            return True
                
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Git configuration failed: {e.stderr}")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Git setup error: {str(e)}")
            return False
    
    def get_remote_url(self):
        remote_url = f"https://{self.username}:{self.token}@github.com/{self.username}/{self.repo_name}.git"
        return remote_url

    def initialize_repository(self):
        """Initialize a new Git repository and set up remote"""
        try:
            repo_path = Path(self.local_path)
            os.chdir(repo_path)

            # Create README if it doesn't exist
            readme_path = repo_path / 'README.md'
            if not repo_path.is_dir():
                repo_path.mkdir(parents=True, exist_ok=True)
                print('Creating directory')
            if not readme_path.exists():
                readme_path.write_text("# Repository\nInitial commit")
                print('Creating Readme.md')

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
            messagebox.showerror("Error", f"Repository initialization failed: {e.stderr}")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Repository initialization error: {str(e)}")
            return False

    def commit_and_push(self, commit_message=None):
        """Perform Git commit and push using Personal Access Token for authentication"""
        if self.data == True:
            if messagebox.askyesno("Confirm" , "Do u want to commit and push into github ?"):
                try:
                    if not self.verify_git_installation():
                        return False
                    
                    repo_path = Path(self.local_path)
                    if not (repo_path / '.git').exists():
                        self.initialize_repository()

                    repo_path = Path(self.local_path)
                    if not repo_path.is_dir():
                        raise FileNotFoundError(f"Invalid repository path: {repo_path}")

                    os.chdir(repo_path)

                    # Check for changes
                    result = subprocess.run(['git', 'status', '--porcelain'], 
                                        capture_output=True, text=True, check=True)
                    print('checking status')
                    if not result.stdout.strip():
                        messagebox.showinfo("Info", "No changes to commit")
                        return True

                    # Add all changes
                    subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
                    print("Git Add")

                    # Get commit message
                    date = datetime.now().strftime('%Y-%m-%d')
                    # if not commit_message:
                    #     commit_message = simpledialog.askstring(
                    #         "Commit Message", 
                    #         "Enter commit message:",
                    #         initialvalue= f'{date} : Auto Commit'
                    #     )
                    #     if not commit_message:
                    #         return False

                    # Commit changes

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
                            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
                            return False
                    print('Git push')

                    messagebox.showinfo("Success", "Changes pushed to GitHub successfully!")
                    return True
                    
                except subprocess.CalledProcessError as e:
                    error_msg = e.stderr if hasattr(e, 'stderr') else str(e)
                    messagebox.showerror("Error", f"Git operation failed: {error_msg}")
                    return False
                except Exception as e:
                    messagebox.showerror("Error", f"Unexpected error: {str(e)}")
                    return False


class GitApp:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Initialize GitHandler
        self.git_handler = GitHandler()

        # Setup styles
        self.setup_styles()

        # Create Widgets
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'))
        style.configure('Status.TLabel', font=('Helvetica', 12, 'italic'))

    def create_widgets(self):
        # Title
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill='x', pady=(0, 10))
        title_label = ttk.Label(title_frame, text="Git Auto-Commit", style='Title.TLabel')
        title_label.pack(side='left')

        # Status Label
        self.status_label = ttk.Label(self.frame, text="", style='Status.TLabel')
        self.status_label.pack(pady=10)

        # Update status
        self.update_status()

        # Buttons frame
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(fill='x', pady=10)

        # Link Account Button
        link_button = ttk.Button(buttons_frame, text="Link Account", command=self.open_account_popup)
        link_button.pack(side='left', padx=5)

        # Commit & Push Button
        push_button = ttk.Button(buttons_frame, text="Commit & Push", 
                               command=lambda: self.git_handler.commit_and_push())
        push_button.pack(side='left', padx=5)

    def update_status(self):
        """Update status label based on Git configuration"""
        if self.git_handler.username and self.git_handler.repo_name:
            status_text = (f"Linked Account: {self.git_handler.username}\n"
                         f"Repository: {self.git_handler.repo_name}")
            self.status_label.config(text=status_text)
        else:
            self.status_label.config(text="No account linked")

    def open_account_popup(self):
        """Open a pop-up window for Git account setup"""
        popup = Toplevel(self.parent)
        popup.title("Link Git Account")
        popup.geometry("500x400")

        # Create main frame with padding
        main_frame = ttk.Frame(popup, padding="10")
        main_frame.pack(fill='both', expand=True)

        # Username
        ttk.Label(main_frame, text="Git Username:").pack(pady=5)
        username_entry = ttk.Entry(main_frame, width=50)
        username_entry.pack(pady=5)
        username_entry.insert(0, self.git_handler.username)

        # Email
        ttk.Label(main_frame, text="Git Email:").pack(pady=5)
        email_entry = ttk.Entry(main_frame, width=50)
        email_entry.pack(pady=5)
        email_entry.insert(0, self.git_handler.email)

        # Repository Name
        ttk.Label(main_frame, text="Repository Name:").pack(pady=5)
        repo_name_entry = ttk.Entry(main_frame, width=50)
        repo_name_entry.pack(pady=5)
        repo_name_entry.insert(0, self.git_handler.repo_name)

        # Access Token
        ttk.Label(main_frame, text="GitHub Token:").pack(pady=5)
        token_entry = ttk.Entry(main_frame, show='*', width=50)
        token_entry.pack(pady=5)
        token_entry.insert(0, self.git_handler.token)

        def save_details():
            try:
                username = username_entry.get().strip()
                email = email_entry.get().strip()
                repo_name = repo_name_entry.get().strip()
                token = token_entry.get().strip()

                if not all([username, email, repo_name, token]):
                    messagebox.showwarning("Warning", "All fields are required!")
                    return


                self.git_handler.save_config('', '', '', '')
                self.git_handler.save_config(username, email, repo_name, token)
                self.git_handler.setup_git()
                self.update_status()
                popup.destroy()
                messagebox.showinfo("Success", "Account linked successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")

        # Save Button
        ttk.Button(main_frame, text="Save", command=save_details).pack(pady=20)