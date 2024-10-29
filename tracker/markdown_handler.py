from datetime import datetime
import os
class MarkdownHandler:
    def __init__(self):
        os.makedirs('./resources/db', exist_ok=True)
        self.filename = './resources/db/daily.md'
        
    def update_todo_list(self, tasks , stats):

        date = datetime.now().strftime('%Y-%m-%d')
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
