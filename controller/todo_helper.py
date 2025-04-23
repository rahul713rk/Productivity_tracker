from model.database import Database
from PySide6.QtWidgets import (QStyledItemDelegate , QApplication , QStyle)
from PySide6.QtCore import Qt , QEvent 
from PySide6.QtGui import QIcon 

class TodoHelper:
    def __init__(self):
        self.db = Database()

    @staticmethod
    def get_categories():
        """Get current categories from database"""
        return Database().get_categories()

    @staticmethod
    def add_task(title, category, priority, status):
        """Add a new task to the database"""
        Database().add_task(title, category, priority, status)

    @staticmethod
    def update_task(task_id, title, category, priority):
        """Update an existing task in the database"""
        Database().update_task(task_id, title, category, priority)

    @staticmethod
    def update_task_status(task_id, status):
        """Update the status of a task in the database"""
        Database().update_task_status(task_id, status)

    @staticmethod
    def delete_task(task_id):
        """Delete a task from the database"""
        Database().delete_task(task_id)

    @staticmethod
    def add_category(category):
        """Add a new category to the database"""
        Database().add_category(category)

    @staticmethod
    def delete_category(category):
        """Delete a category from the database"""
        Database().delete_category(category)

    @staticmethod
    def get_today_tasks():
        """Get today's tasks from the database"""
        return Database().get_today_tasks()

    def close(self):
        """Close the database connection"""
        self.db.close()

