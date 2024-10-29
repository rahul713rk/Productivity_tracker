# todo_helper.py

from .database import Database
from .markdown_handler import MarkdownHandler

class TodoHelper:
    def __init__(self):
        self.db = Database()
        self.md_handler = MarkdownHandler()

    def add_task(self, title, category, priority):
        if title:
            self.db.add_task(title, category, priority, "Pending")
            return True
        return False

    def add_category(self, category):
        return self.db.add_category(category)

    def change_status(self, task_id, new_status):
        self.db.update_task_status(task_id, new_status)

    def delete_task(self, task_id):
        self.db.delete_task(task_id)

    def load_tasks(self):
        return self.db.get_all_tasks()

    def get_categories(self):
        return self.db.get_categories()

    def get_latest_stats(self):
        return self.db.get_latest_stats()

    def close_resources(self):
        self.db.close()
