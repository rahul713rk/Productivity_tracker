from model.database import Database
from PySide6.QtWidgets import (QStyledItemDelegate , QApplication , QStyle)
from PySide6.QtCore import Qt , QEvent 
from PySide6.QtGui import QIcon 

class TodoHelper:
    def __init__(self):
        self.db = Database()

    def get_categories(self):
        """Get current categories from database"""
        return self.db.get_categories()

    def add_task(self, title, category, priority, status):
        """Add a new task to the database"""
        self.db.add_task(title, category, priority, status)

    def update_task(self, task_id, title, category, priority):
        """Update an existing task in the database"""
        self.db.update_task(task_id, title, category, priority)

    def update_task_status(self, task_id, status):
        """Update the status of a task in the database"""
        self.db.update_task_status(task_id, status)

    def delete_task(self, task_id):
        """Delete a task from the database"""
        self.db.delete_task(task_id)

    def add_category(self, category):
        """Add a new category to the database"""
        self.db.add_category(category)

    def delete_category(self, category):
        """Delete a category from the database"""
        self.db.delete_category(category)

    def get_today_tasks(self):
        """Get today's tasks from the database"""
        return self.db.get_today_tasks()

    def close(self):
        """Close the database connection"""
        self.db.close()

