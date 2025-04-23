from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                               QPushButton, QTreeView, QMenu, QInputDialog, QMessageBox, 
                               QStyledItemDelegate, QAbstractItemView, QHeaderView , QDialog)
from PySide6.QtCore import Qt, QModelIndex, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction
from .database import Database

class Todo(QWidget):
    task_updated = Signal()  # Signal to notify when tasks are updated
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Todo List")
        self.db = Database()
        self.setup_ui()
        self.load_tasks()
        self.task_updated.connect(self.load_tasks)

    def setup_ui(self):
        """Setup the main user interface"""
        self.layout = QVBoxLayout(self)
        self.setMinimumSize(800, 600)
        
        # Title
        title_label = QLabel("Todo List", self)
        title_label.setStyleSheet("font: bold 20px; margin-bottom: 10px;")
        self.layout.addWidget(title_label)
        
        # Input area
        self.setup_input_area()
        
        # Task views
        self.setup_task_views()
        
        # Buttons
        self.setup_buttons()

    def setup_input_area(self):
        """Setup the input area for new tasks"""
        input_layout = QHBoxLayout()
        
        # Task entry
        self.task_entry = QLineEdit(self)
        self.task_entry.setPlaceholderText("Enter new task...")
        self.task_entry.returnPressed.connect(self.add_task)
        input_layout.addWidget(self.task_entry, stretch=4)
        
        # Category selection
        self.category_combo = QComboBox(self)
        self.category_combo.addItems(self.get_categories())
        input_layout.addWidget(self.category_combo, stretch=2)
        
        # Priority selection
        self.priority_combo = QComboBox(self)
        self.priority_combo.addItems(['High', 'Medium', 'Low'])
        input_layout.addWidget(self.priority_combo, stretch=1)
        
        self.layout.addLayout(input_layout)

    def setup_task_views(self):
        """Setup the task tree views"""
        # Main task view (pending/working tasks)
        self.main_tree = self.create_task_tree("Active Tasks")
        self.layout.addWidget(self.main_tree, stretch=2)
        
        # Done task view
        self.done_tree = self.create_task_tree("Completed Tasks")
        self.layout.addWidget(self.done_tree, stretch=1)
        
        # Connect context menus
        self.main_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.main_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.done_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.done_tree.customContextMenuRequested.connect(self.show_context_menu)

    def create_task_tree(self, title):
        """Create a configured task tree view"""
        tree = QTreeView(self)
        tree.setModel(QStandardItemModel(0, 4, tree))
        tree.model().setHorizontalHeaderLabels(['Title', 'Category', 'Priority', 'Status'])
        
        # Tree configuration
        tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        tree.setSelectionMode(QAbstractItemView.SingleSelection)
        tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tree.setAlternatingRowColors(True)
        tree.setSortingEnabled(True)
        
        # Header configuration
        header = tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Title column stretches
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        return tree

    def setup_buttons(self):
        """Setup the action buttons"""
        buttons_layout = QHBoxLayout()
        
        # Button creation helper
        def create_button(text, slot, tooltip=None):
            btn = QPushButton(text, self)
            btn.clicked.connect(slot)
            if tooltip:
                btn.setToolTip(tooltip)
            return btn
        
        # Add buttons
        buttons = [
            ("Add Task", self.add_task, "Add a new task"),
            ("Delete Task", self.delete_task, "Delete selected task"),
            ("Mark Complete", lambda: self.change_status("Done"), "Mark task as complete"),
            ("Add Category", self.add_category, "Add a new category"),
            ("Delete Category", self.delete_category, "Delete selected category"),
            ("Refresh", self.load_tasks, "Refresh task list")
        ]
        
        for text, slot, tooltip in buttons:
            buttons_layout.addWidget(create_button(text, slot, tooltip))
        
        self.layout.addLayout(buttons_layout)

    def show_context_menu(self, position):
        """Show context menu for the selected task"""
        tree = self.sender()
        selected_indexes = tree.selectionModel().selectedRows()
        
        if not selected_indexes:
            return
            
        menu = QMenu()
        
        # Status actions
        status_actions = [
            ("Set Pending", "Pending"),
            ("Set Working", "Working"),
            ("Set Done", "Done")
        ]
        
        for text, status in status_actions:
            action = QAction(text, self)
            action.triggered.connect(lambda _, s=status: self.change_status(s))
            menu.addAction(action)
        
        # Edit action
        edit_action = QAction("Edit Task", self)
        edit_action.triggered.connect(self.edit_task)
        menu.addAction(edit_action)
        
        # Delete action
        delete_action = QAction("Delete Task", self)
        delete_action.triggered.connect(self.delete_task)
        menu.addAction(delete_action)
        
        menu.exec_(tree.viewport().mapToGlobal(position))

    def edit_task(self):
        """Edit the selected task"""
        tree = self.main_tree if self.main_tree.selectionModel().hasSelection() else self.done_tree
        selected_index = tree.selectionModel().selectedRows()[0]
        model = tree.model()
        
        # Get current values
        title_item = model.item(selected_index.row(), 0)
        category_item = model.item(selected_index.row(), 1)
        priority_item = model.item(selected_index.row(), 2)
        
        # Create edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Task")
        layout = QVBoxLayout(dialog)
        
        # Title input
        title_edit = QLineEdit(title_item.text(), dialog)
        layout.addWidget(QLabel("Task Title:"))
        layout.addWidget(title_edit)
        
        # Category selection
        category_combo = QComboBox(dialog)
        category_combo.addItems(self.get_categories())
        category_combo.setCurrentText(category_item.text())
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(category_combo)
        
        # Priority selection
        priority_combo = QComboBox(dialog)
        priority_combo.addItems(['High', 'Medium', 'Low'])
        priority_combo.setCurrentText(priority_item.text())
        layout.addWidget(QLabel("Priority:"))
        layout.addWidget(priority_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save", dialog)
        save_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel", dialog)
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # Update the task in database
            task_id = title_item.data(Qt.UserRole)  # Assuming we store task ID in UserRole
            new_title = title_edit.text().strip()
            new_category = category_combo.currentText()
            new_priority = priority_combo.currentText()
            
            if new_title:
                self.db.update_task(task_id, new_title, new_category, new_priority)
                self.task_updated.emit()
            else:
                QMessageBox.warning(self, "Warning", "Task title cannot be empty")

    def add_task(self):
        """Add a new task to the list"""
        title = self.task_entry.text().strip()
        category = self.category_combo.currentText()
        priority = self.priority_combo.currentText()
        
        if title:
            self.db.add_task(title, category, priority, "Pending")
            self.task_entry.clear()
            self.task_updated.emit()
        else:
            QMessageBox.warning(self, "Warning", "Please enter a task title.")

    def add_category(self):
        """Add a new category"""
        category, ok = QInputDialog.getText(
            self, 
            "Add Category", 
            "Enter new category name:",
            QLineEdit.Normal
        )
        
        if ok and category:
            if category in self.get_categories():
                QMessageBox.warning(self, "Warning", "Category already exists")
                return
                
            self.db.add_category(category)
            self.category_combo.addItem(category)
            self.category_combo.setCurrentText(category)
            QMessageBox.information(self, "Success", "Category added successfully!")

    def change_status(self, new_status):
        """Change status of the selected task"""
        tree = self.main_tree if self.main_tree.selectionModel().hasSelection() else self.done_tree
        selected_index = tree.selectionModel().selectedRows()[0]
        task_id = tree.model().item(selected_index.row(), 0).data(Qt.UserRole)
        
        self.db.update_task_status(task_id, new_status)
        self.task_updated.emit()

    def delete_task(self):
        """Delete the selected task"""
        tree = self.main_tree if self.main_tree.selectionModel().hasSelection() else self.done_tree
        selected_index = tree.selectionModel().selectedRows()[0]
        task_id = tree.model().item(selected_index.row(), 0).data(Qt.UserRole)
        
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete", 
            "Are you sure you want to delete this task?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.db.delete_task(task_id)
            self.task_updated.emit()

    def delete_category(self):
        """Delete the selected category"""
        category = self.category_combo.currentText()
        
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Delete category '{category}' and all its tasks?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.db.delete_category(category)
            self.category_combo.removeItem(self.category_combo.currentIndex())
            self.task_updated.emit()

    def load_tasks(self):
        """Load tasks from database into the views"""
        # Clear current views
        self.main_tree.model().removeRows(0, self.main_tree.model().rowCount())
        self.done_tree.model().removeRows(0, self.done_tree.model().rowCount())
        
        # Load tasks from database
        tasks = self.db.get_today_tasks()
        
        for task in tasks:
            task_id, title, category, priority, status , *rest = task
            model = self.main_tree.model() if status != 'Done' else self.done_tree.model()
            
            # Create items for each column
            items = [
                QStandardItem(title),
                QStandardItem(category),
                QStandardItem(priority),
                QStandardItem(status)
            ]
            
            # Store task ID in the first item's UserRole
            items[0].setData(task_id, Qt.UserRole)
            
            # Set priority-based coloring
            if priority == "High":
                items[0].setForeground(Qt.red)
            elif priority == "Medium":
                items[0].setForeground(Qt.darkYellow)
            
            # Add row to model
            model.appendRow(items)

    def get_categories(self):
        """Get current categories from database"""
        return self.db.get_categories()

    def closeEvent(self, event):
        """Clean up when closing the application"""
        self.db.close()
        super().closeEvent(event)