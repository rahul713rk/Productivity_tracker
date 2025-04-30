from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
                               QPushButton, QTreeView, QMenu, QInputDialog, QMessageBox,
                               QStyledItemDelegate, QAbstractItemView, QHeaderView, QDialog ,
                                 QGroupBox , QFrame , QStyle )
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction, QIcon , QColor
from view.tree_view import create_task_tree
from controller.todo_helper import TodoHelper
from view.task_edit_view import Edit_Task
from view.style import StyleUtils

class TodoView(QWidget):
    task_updated = Signal()  # Signal to notify when tasks are updated

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setWindowTitle("Todo List")
        self.helper = TodoHelper()
        self.setup_ui()
        self.load_tasks()
        self.task_updated.connect(self.load_tasks)

    def setup_ui(self):
        """Setup the main user interface"""
        self.layout = QVBoxLayout(self)
        # Title
        todo_controller_group = QGroupBox("Todo List")
        StyleUtils.style_groupbox(todo_controller_group)
        self.todo_controller_layout = QVBoxLayout(todo_controller_group)

        # Input area
        self.setup_input_area()

        # Buttons
        self.setup_buttons()

        self.layout.addWidget(todo_controller_group)

        # Task views
        task_group = QGroupBox("Tasks")
        StyleUtils.style_groupbox(task_group)
        self.main_task_layout = QVBoxLayout(task_group)
        self.setup_task_views()
        self.layout.addWidget(task_group)    

    def setup_input_area(self):
        """Setup the input area for new tasks"""
        input_layout = QHBoxLayout()

        # Task entry
        self.task_entry = QLineEdit(self)
        StyleUtils.style_text_input(self.task_entry)
        self.task_entry.setPlaceholderText("Enter new task...")

        self.task_entry.returnPressed.connect(self.add_task)

        input_layout.addWidget(self.task_entry, stretch=4)

        # Category selection
        self.category_combo = QComboBox(self)
        StyleUtils.style_dropdown(self.category_combo)
        self.category_combo.addItems(self.helper.get_categories())
        input_layout.addWidget(self.category_combo, stretch=2)

        # Priority selection
        self.priority_combo = QComboBox(self)
        StyleUtils.style_dropdown(self.priority_combo )
        self.priority_combo.addItems(['High', 'Medium', 'Low'])
        input_layout.addWidget(self.priority_combo, stretch=1)

        self.todo_controller_layout.addLayout(input_layout)

    def setup_task_views(self):
        """Setup the main task views with consistent styling and layout"""
        # Create a container frame for all task views
        tasks_container = QFrame()
        tasks_container.setFrameShape(QFrame.NoFrame)
        self.main_task_layout.addWidget(tasks_container, stretch=1)
        
        # Main layout for task views
        self.task_layout = QVBoxLayout(tasks_container)
        self.task_layout.setContentsMargins(0, 0, 0, 0)
        self.task_layout.setSpacing(2)
        
        # Create and style the active tasks view
        self.setup_task_view(
            title="Active Tasks",
            view_type="active",
            stretch=2
        )
        
        # Create and style the completed tasks view
        self.setup_task_view(
            title="Completed Tasks",
            view_type="completed",
            stretch=1
        )
        
        # Connect context menus to both views
        self.connect_context_menus()

    def setup_task_view(self, title: str, view_type: str, stretch: int = 1):
        """
        Create and configure a single task view with consistent styling
        
        Args:
            title: Title for the task view
            view_type: Type of view ('active' or 'completed')
            stretch: Stretch factor for the view
        """
        # Create container group box
        header = self.create_fancy_header(title, view_type)
        group = QGroupBox()
        group.setTitle("")  # Or you can skip setTitle if you're using a custom header
        StyleUtils.style_groupbox(group)

        group_layout = QVBoxLayout(group)
        group_layout.addWidget(header)

        tree = create_task_tree()
        group_layout.addWidget(tree)
        
        self.task_layout.addWidget(group, stretch=stretch)

        # Store reference to the tree
        if view_type == "active":
            self.main_tree = tree
        else:
            self.Completed_tree = tree

    def create_fancy_header(self, title: str, icon_type: str) -> QWidget:
        """Create a fancy header with an icon and title"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        icon = QLabel()
        icon.setPixmap(self.style().standardIcon(
            QStyle.SP_ArrowForward if icon_type == "active" else QStyle.SP_DialogOkButton
        ).pixmap(16, 16))
        header_layout.addWidget(icon)

        label = QLabel(title)
        header_layout.addWidget(label, stretch=1)

        return header_widget

    def connect_context_menus(self):
        """Connect context menus to both task views"""
        for tree in [self.main_tree, self.Completed_tree]:
            tree.setContextMenuPolicy(Qt.CustomContextMenu)
            tree.customContextMenuRequested.connect(self.show_context_menu)

    def setup_buttons(self):
        """Setup the action buttons"""
        buttons_layout = QHBoxLayout()

        # Button creation helper
        def create_button(text, slot, tooltip=None):
            btn = QPushButton(text, self)
            StyleUtils.style_primary_button(btn)
            btn.clicked.connect(slot)
            if tooltip:
                btn.setToolTip(tooltip)
            return btn

        # Add buttons
        buttons = [
            ("Add Task", self.add_task, "Add a new task"),
            ("Add Category", self.add_category, "Add a new category"),
            ("Delete Category", self.delete_category, "Delete selected category"),
            ("Refresh", self.load_tasks, "Refresh task list")
        ]

        for text, slot, tooltip in buttons:
            buttons_layout.addWidget(create_button(text, slot, tooltip))

        self.todo_controller_layout.addLayout(buttons_layout)

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
            ("Set Completed", "Completed")
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
        tree = self.main_tree if self.main_tree.selectionModel().hasSelection() else self.Completed_tree
        selected_index = tree.selectionModel().selectedRows()[0]
        model = tree.model()
        
        # Prepare task data
        task_data = {
            'task_id': model.item(selected_index.row(), 0).data(Qt.UserRole),
            'title': model.item(selected_index.row(), 0).text(),
            'category': model.item(selected_index.row(), 1).text(),
            'priority': model.item(selected_index.row(), 2).text()
        }
        
        # Create and show edit dialog
        dialog = Edit_Task(
            self,
            task_data=task_data,
            categories=self.helper.get_categories()
        )
        
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.get_updated_data()
            self.helper.update_task(
                updated_data['task_id'],
                updated_data['title'],
                updated_data['category'],
                updated_data['priority']
            )
            self.task_updated.emit()

    def add_task(self):
        """Add a new task to the list"""
        title = self.task_entry.text().strip()
        category = self.category_combo.currentText()
        priority = self.priority_combo.currentText()

        if title:
            self.helper.add_task(title, category, priority, "Pending")
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
            if category in self.helper.get_categories():
                QMessageBox.warning(self, "Warning", "Category already exists")
                return

            self.helper.add_category(category)
            self.category_combo.addItem(category)
            self.category_combo.setCurrentText(category)
            QMessageBox.information(self, "Success", "Category added successfully!")

    def change_status(self, new_status):
        """Change status of the selected task"""
        tree = self.main_tree if self.main_tree.selectionModel().hasSelection() else self.Completed_tree
        selected_index = tree.selectionModel().selectedRows()[0]
        task_id = tree.model().item(selected_index.row(), 0).data(Qt.UserRole)

        self.helper.update_task_status(task_id, new_status)
        self.task_updated.emit()

    def delete_task(self ,task_id = None):
        """Delete the selected task"""
        if task_id is None:
            tree = self.main_tree if self.main_tree.selectionModel().hasSelection() else self.Completed_tree
            selected_index = tree.selectionModel().selectedRows()[0]
            task_id = tree.model().item(selected_index.row(), 0).data(Qt.UserRole)

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this task?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.helper.delete_task(task_id)
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
            self.helper.delete_category(category)
            self.category_combo.removeItem(self.category_combo.currentIndex())
            self.task_updated.emit()

    def load_tasks(self):
        """Load tasks from database into the views"""
        # Clear current views
        self.main_tree.model().removeRows(0, self.main_tree.model().rowCount())
        self.Completed_tree.model().removeRows(0, self.Completed_tree.model().rowCount())

        # Load tasks from database
        tasks = self.helper.get_today_tasks()

        for task in tasks:
            task_id, title, category, priority, status, *rest = task
            model = self.main_tree.model() if status != 'Completed' else self.Completed_tree.model()

            # Create items for each column (without buttons)
            items = [
                QStandardItem(title),
                QStandardItem(category),
                QStandardItem(priority),
                QStandardItem(status),
                QStandardItem(),  # Placeholder for delete button
                QStandardItem(),  # Placeholder for complete/pending button
                QStandardItem(),  # Placeholder for edit button
            ]

            # Store task ID in the first item's UserRole
            items[0].setData(task_id, Qt.UserRole)

            # Set priority-based coloring
            for i in range(0,4):
                if priority == "High":
                    items[i].setForeground(Qt.black)
                    items[i].setBackground(QColor("#e57373"))  # Soft red 
                elif priority == "Medium":
                    items[i].setForeground(Qt.black)
                    items[i].setBackground(QColor("#fff176"))  # Soft yellow
                elif priority == "Low":
                    items[i].setForeground(Qt.black)
                    items[i].setBackground(QColor("#aed581"))  # Soft green
                
                if i == 0:
                    items[i].setToolTip(title)

            # Add row to model
            model.appendRow(items)
            
            # Get the row index
            row = model.rowCount() - 1
            
            # Add buttons to the view using setIndexWidget
            tree = self.main_tree if status != 'Completed' else self.Completed_tree
            
            # Delete button
            delete_button = QPushButton()
            StyleUtils.style_icon_button(delete_button, QIcon("./assets/images/icons/bin.png"))
            delete_button.clicked.connect(lambda _, id=task_id: self.delete_task(id))
            delete_button.setToolTip("Delete Task")
            tree.setIndexWidget(model.index(row, 4), delete_button)

            # Complete/Pending button
            if status != 'Completed':
                complete_button = QPushButton()
                StyleUtils.style_icon_button(complete_button, QIcon("./assets/images/icons/complete.png"))
                complete_button.clicked.connect(lambda _, id=task_id: self.change_status("Completed"))
                complete_button.setToolTip("Mark as Complete")
                tree.setIndexWidget(model.index(row, 5), complete_button)
            else:
                pending_button = QPushButton()
                StyleUtils.style_icon_button(pending_button, QIcon("./assets/images/icons/upload-file.png"))
                pending_button.clicked.connect(lambda _, id=task_id: self.change_status("Pending"))
                pending_button.setToolTip("Mark as Pending")
                tree.setIndexWidget(model.index(row, 5), pending_button)

            # Edit button
            edit_button = QPushButton()
            StyleUtils.style_icon_button(edit_button, QIcon("./assets/images/icons/edit.png"))
            edit_button.clicked.connect(self.edit_task)
            edit_button.setToolTip("Edit Task")
            tree.setIndexWidget(model.index(row, 6), edit_button)

    def closeEvent(self, event):
        """Clean up when closing the application"""
        self.helper.close()
        super().closeEvent(event)
