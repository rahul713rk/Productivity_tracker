from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QComboBox, QPushButton, 
    QMessageBox
)
from PySide6.QtCore import Qt
from view.style import StyleUtils

class Edit_Task(QDialog):
    def __init__(self, parent=None, task_data=None, categories=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Task")
        self.task_data = task_data
        self.categories = categories or []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the edit task dialog UI"""
        self.layout = QVBoxLayout(self)
        
        # Title input
        self.title_edit = QLineEdit(self.task_data['title'], self)
        StyleUtils.style_text_input(self.title_edit)

        self.layout.addWidget(self.setup_label("Task Title"))
        self.layout.addWidget(self.title_edit)
        
        # Category selection
        self.category_combo = QComboBox(self)
        StyleUtils.style_dropdown(self.category_combo)
        self.category_combo.addItems(self.categories)
        self.category_combo.setCurrentText(self.task_data['category'])
        self.layout.addWidget(self.setup_label("Category"))
        self.layout.addWidget(self.category_combo)
        
        # Priority selection
        self.priority_combo = QComboBox(self)
        StyleUtils.style_dropdown(self.priority_combo)
        self.priority_combo.addItems(['High', 'Medium', 'Low'])
        self.priority_combo.setCurrentText(self.task_data['priority'])
        self.layout.addWidget(self.setup_label("Priority"))
        self.layout.addWidget(self.priority_combo)
        
        # Buttons
        self.setup_buttons()
    
    def setup_label(self, text):
        """Setup a label with the given text"""
        label = QLabel(text)
        StyleUtils.style_lable(label)
        return label
        
    def setup_buttons(self):
        """Setup the dialog buttons"""
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save", self)
        StyleUtils.style_primary_button(self.save_button)
        self.save_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel", self)
        StyleUtils.style_primary_button(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)
        
    def get_updated_data(self):
        """Return the updated task data"""
        return {
            'task_id': self.task_data['task_id'],
            'title': self.title_edit.text().strip(),
            'category': self.category_combo.currentText(),
            'priority': self.priority_combo.currentText()
        }
        
    def validate(self):
        """Validate the input before accepting"""
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Warning", "Task title cannot be empty")
            return False
        return True
        
    def accept(self):
        """Override accept to include validation"""
        if self.validate():
            super().accept()