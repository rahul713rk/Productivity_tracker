from model.git_model import GitHandler
from PySide6.QtWidgets import QApplication, QMessageBox

class GitController:
    def __init__(self):
        self.model = GitHandler()

    def get_username(self):
        return self.model.username

    def get_email(self):
        return self.model.email

    def get_repo_name(self):
        return self.model.repo_name

    def get_token(self):
        return self.model.token

    def save_config(self, username, email, repo_name, token):
        return self.model.save_config(username, email, repo_name, token)

    def setup_git(self):
        return self.model.setup_git()

    def commit_and_push(self):
        return self.model.commit_and_push()

    def get_status_text(self):
        if self.model.username and self.model.repo_name:
            return f"Linked Account: {self.model.username}\nRepository: {self.model.repo_name}"
        else:
            return "No account linked"
