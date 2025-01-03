from datetime import datetime
import os
from .database import Database

class MarkdownHandler:
    def __init__(self):
        self.db = Database()
        abs_path = os.path.abspath("./resources/db/Daily_update")
        os.makedirs(abs_path, exist_ok=True)
        self.filename = os.path.join(abs_path, "README.md")
        
    
    def markdown_helper(self):
        task = self.db.get_today_tasks()
        stats = self.db.get_today_stats()
        self.update_todo_list(tasks=task , stats=stats)
        print("Markdown updated!")
        
    def update_todo_list(self, tasks , stats):

        date = datetime.now().strftime('%Y-%m-%d')
        # print(self.filename)
        # print(os.getcwd())
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write(f"# Todo List | Date : {date} \n\n")
            if stats is not None:
                keys , clicks , time = stats
                f.write(f"Keys : {keys} | Clicks : {clicks} | Time (in Minutes) : {time}")
            f.write("## Tasks Overview\n\n")
            
            # Group tasks by status
            status_groups = {'Pending': [], 'Working': [], 'Done': []}
            for task in tasks:
                task_id, title, category, priority, status, created, completed = task
                status_groups[status].append(task)

            # Write tasks by status
            for status, tasks_list in status_groups.items():
                f.write(f"### {status}\n")
                if tasks_list:
                    f.write("| Title | Category | Priority | Created | Completed |\n")
                    f.write("|-------|----------|----------|----------|------------|\n")
                    for task in tasks_list:
                        task_id, title, category, priority, status, created, completed = task
                        completed_date = completed if completed else '-'
                        f.write(f"| {title} | {category} | {priority} | {created} | {completed_date} |\n")
                else:
                    f.write("No tasks in this status.\n")
                f.write("\n")
