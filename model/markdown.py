import os
from datetime import datetime
from .database import Database


from controller.path_manager import path_manager

logger = path_manager.get_logger("MarkdownHandler")

class MarkdownHandler:
    def __init__(self, db=None, markdown_path=None):
        # Use an existing Database object or create a new one
        self.db = db if db else Database()
        
        self.filename = markdown_path if markdown_path else path_manager.get_path('markdown')
        logger.info(f"MarkdownHandler initialized with path: {self.filename}")
    
    def markdown_helper(self):
        """Main method to update the markdown file."""
        tasks = self.db.get_today_tasks()
        stats = self.db.get_today_stats()
        self.update_todo_list(tasks=tasks, stats=stats)
        logger.info("Markdown updated!")
    
    def update_todo_list(self, tasks, stats):
        """Update the markdown file with today's tasks and statistics."""
        date = datetime.now().strftime('%Y-%m-%d')
        with open(self.filename, 'w', encoding='utf-8') as f:
            # Add the title and date
            f.write(f"# Todo List | Date: {date}\n\n")
            
            # Add stats if available
            if stats is not None:
                keys, clicks, time = stats
                f.write(f"**Stats for today**:\n")
                f.write(f"- **Keys Pressed**: {keys}\n")
                f.write(f"- **Mouse Clicks**: {clicks}\n")
                f.write(f"- **Time Spent (Minutes)**: {time}\n")
            else:
                f.write("**No statistics available for today.**\n")
            
            f.write("\n## Tasks Overview\n\n")
            
            # Group tasks by their status
            status_groups = {'Pending': [], 'Working': [], 'Completed': []}
            for task in tasks:
                task_id, title, category, priority, status, created, completed = task
                status_groups[status].append(task)

            # Write tasks by status
            for status, tasks_list in status_groups.items():
                f.write(f"### {status} Tasks\n")
                if tasks_list:
                    f.write("| **Title** | **Category** | **Priority** | **Created** | **Completed** |\n")
                    f.write("|-----------|--------------|--------------|-------------|----------------|\n")
                    for task in tasks_list:
                        task_id, title, category, priority, status, created, completed = task
                        completed_date = completed if completed else '-'
                        f.write(f"| {title} | {category} | {priority} | {created} | {completed_date} |\n")
                else:
                    f.write("No tasks in this status.\n")
                f.write("\n")
    
    def get_task_statuses(self, tasks):
        """Helper function to group tasks by status."""
        status_groups = {'Pending': [], 'Working': [], 'Completed': []}
        for task in tasks:
            task_id, title, category, priority, status, created, completed = task
            status_groups[status].append(task)
        return status_groups
