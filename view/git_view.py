from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit, QDialog , QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from view.style import StyleUtils
from controller.git_controller import GitController

class AccountDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Link Git Account")
        self.setModal(True)
        # self.resize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Git Username:"))
        self.username_entry = QLineEdit()
        StyleUtils.style_text_input(self.username_entry)
        self.username_entry.setPlaceholderText("Enter your GitHub username")
        self.username_entry.setText(self.controller.get_username())
        layout.addWidget(self.username_entry)

        layout.addWidget(QLabel("Git Email:"))
        self.email_entry = QLineEdit()
        StyleUtils.style_text_input(self.email_entry)
        self.email_entry.setPlaceholderText("Enter your GitHub email")
        self.email_entry.setText(self.controller.get_email())
        layout.addWidget(self.email_entry)

        layout.addWidget(QLabel("Repository Name:"))
        self.repo_entry = QLineEdit()
        StyleUtils.style_text_input(self.repo_entry)
        self.repo_entry.setPlaceholderText("Enter your GitHub repository name")
        self.repo_entry.setText(self.controller.get_repo_name())
        layout.addWidget(self.repo_entry)

        layout.addWidget(QLabel("GitHub Token:"))
        self.token_entry = QLineEdit()
        StyleUtils.style_text_input(self.token_entry)
        self.token_entry.setPlaceholderText("Enter your GitHub token")
        self.token_entry.setEchoMode(QLineEdit.Password)
        self.token_entry.setText(self.controller.get_token())
        layout.addWidget(self.token_entry)

        save_btn = QPushButton("Save")
        StyleUtils.style_primary_button(save_btn)
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

        if self.controller.save_config(username, email, repo_name, token):
            self.controller.setup_git()
            self.accept()

class GitView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = GitController()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        self.init_ui()

    def init_ui(self):
        title_label = QLabel("Git Auto-Commit")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title_label)

        self.status_label = QLabel()
        # StyleUtils.style_lable(self.status_label)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.update_status()
        self.main_layout.addWidget(self.status_label)

        buttons_layout = QHBoxLayout()

        link_btn = QPushButton("Link Account")
        StyleUtils.style_primary_button(link_btn)
        link_btn.clicked.connect(self.open_account_dialog)
        buttons_layout.addWidget(link_btn)

        push_btn = QPushButton("Commit and Push")
        StyleUtils.style_primary_button(push_btn)
        push_btn.clicked.connect(self.controller.commit_and_push)
        buttons_layout.addWidget(push_btn)

        self.main_layout.addLayout(buttons_layout)

    def update_status(self):
        status_text = self.controller.get_status_text()
        self.status_label.setText(status_text)

    def open_account_dialog(self):
        dialog = AccountDialog(self.controller, self)
        if dialog.exec() == QDialog.Accepted:
            self.update_status()
