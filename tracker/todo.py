from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                               QPushButton, QTreeView, QMenu, QInputDialog, QMessageBox, 
                               QStyledItemDelegate, QItemDelegate, QDialog, QFrame)
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from .database import Database

class Todo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Todo List")
        self.db = Database()

        # Setup layout
        self.layout = QVBoxLayout(self)

        self.setup_styles()
        self.create_widgets()
        self.load_tasks()

    def setup_styles(self):
        # You can add QSS styling here if necessary
        pass

    def create_widgets(self):
        # Title
        title_label = QLabel("Todo List", self)
        title_label.setStyleSheet("font: bold 20px;")
        self.layout.addWidget(title_label)

        # Input area
        input_layout = QHBoxLayout()
        self.layout.addLayout(input_layout)
        
        self.input_frame_func(input_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        self.layout.addLayout(buttons_layout)

        # Add task button
        add_button = QPushButton("Add Task", self)
        add_button.clicked.connect(self.add_task)
        buttons_layout.addWidget(add_button)

        # Delete task button
        delete_button = QPushButton("Delete Task", self)
        delete_button.clicked.connect(self.delete_task)
        buttons_layout.addWidget(delete_button)

        # Add category button
        add_cat_button = QPushButton("Add Category", self)
        add_cat_button.clicked.connect(self.add_category)
        buttons_layout.addWidget(add_cat_button)

        # Delete category button
        delete_cat_button = QPushButton("Delete Category", self)
        delete_cat_button.clicked.connect(self.delete_category)
        buttons_layout.addWidget(delete_cat_button)

        # Refresh button
        refresh_button = QPushButton("Refresh", self)
        refresh_button.clicked.connect(self.load_tasks)
        buttons_layout.addWidget(refresh_button)

        # Task Frame (Main and Done Task Frames)
        self.main_tree = self.create_tree_view("Task List", 12)
        self.layout.addWidget(self.main_tree)

        self.done_tree = self.create_tree_view("Task Completed", 4)
        self.layout.addWidget(self.done_tree)

        # Context menu setup
        # self.create_context_menu()

    def input_frame_func(self, layout):
        # Task entry
        self.task_entry = QLineEdit(self)
        self.task_entry.returnPressed.connect(self.add_task)
        layout.addWidget(self.task_entry)

        # Category selection
        self.category_combo = QComboBox(self)
        self.category_combo.addItems(self.get_categories())
        layout.addWidget(self.category_combo)

        # Priority selection
        self.priority_combo = QComboBox(self)
        self.priority_combo.addItems(['High', 'Medium', 'Low'])
        layout.addWidget(self.priority_combo)

    def create_tree_view(self, title, height):
        model = QStandardItemModel(height, 4, self)
        model.setHorizontalHeaderLabels(['Title', 'Category', 'Priority', 'Status'])

        tree = QTreeView(self)
        tree.setModel(model)
        tree.setSelectionMode(QTreeView.SingleSelection)
        tree.setContextMenuPolicy(Qt.CustomContextMenu)
        tree.customContextMenuRequested.connect(self.show_context_menu)

        return tree

    def create_context_menu(self, event):
        context_menu = QMenu(self)

        set_pending_action = context_menu.addAction("Set Pending")
        set_pending_action.triggered.connect(lambda: self.change_status("Pending"))

        set_working_action = context_menu.addAction("Set Working")
        set_working_action.triggered.connect(lambda: self.change_status("Working"))

        set_done_action = context_menu.addAction("Set Done")
        set_done_action.triggered.connect(lambda: self.change_status("Done"))

        edit_action = context_menu.addAction("Edit")
        edit_action.triggered.connect(self.edit_task)

        context_menu.exec_(event.globalPos())

    def show_context_menu(self, event):
        item = self.main_tree.selectionModel().selectedIndexes()
        if item:
            self.context_menu.exec_(event.globalPos())

    def edit_task(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Task")

        task_title, ok = QInputDialog.getText(dialog, "Edit Task", "Task Title:")
        if ok:
            # Edit task in the DB
            pass  # Implement the update functionality here

    def add_task(self):
        title = self.task_entry.text().strip()
        category = self.category_combo.currentText()
        priority = self.priority_combo.currentText()

        if title:
            self.db.add_task(title, category, priority, "Pending")
            self.load_tasks()
        else:
            QMessageBox.warning(self, "Warning", "Please enter a task title.")

    def add_category(self):
        category, ok = QInputDialog.getText(self, "Add Category", "Enter new category name:")
        if ok and category:
            self.db.add_category(category)
            self.category_combo.addItem(category)
            QMessageBox.information(self, "Success", "Category added successfully!")

    def change_status(self, new_status):
        selected_item = self.main_tree.selectionModel().selectedIndexes()
        if selected_item:
            task_id = selected_item[0].data()
            self.db.update_task_status(task_id, new_status)
            self.load_tasks()

    def delete_task(self):
        selected_item = self.main_tree.selectionModel().selectedIndexes()
        if selected_item:
            task_id = selected_item[0].data()
            confirm = QMessageBox.question(self, "Confirm Delete", "Delete this task?")
            if confirm == QMessageBox.Yes:
                self.db.delete_task(task_id)
                self.load_tasks()

    def delete_category(self):
        selected_category = self.category_combo.currentText()
        confirm = QMessageBox.question(self, "Confirm Delete", f"Delete category '{selected_category}'?")
        if confirm == QMessageBox.Yes:
            self.db.delete_category(selected_category)
            self.category_combo.removeItem(self.category_combo.currentIndex())

    def load_tasks(self):
        # Clear trees
        self.clear_tree(self.main_tree)
        self.clear_tree(self.done_tree)

        tasks = self.db.get_today_tasks()
        for task in tasks:
            # Add to appropriate tree based on status
            model = self.main_tree.model() if task[4] != 'Done' else self.done_tree.model()
            row = [task[1], task[2], task[3], task[4]]
            self.add_task_to_tree(model, row)

    def clear_tree(self, tree):
        model = tree.model()
        model.removeRows(0, model.rowCount())

    def add_task_to_tree(self, model, row):
        items = [QStandardItem(field) for field in row]
        model.appendRow(items)

    def get_categories(self):
        return self.db.get_categories()

    def close_resources(self):
        self.db.close()
