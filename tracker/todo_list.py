import tkinter as tk
from tkinter import messagebox, font

class TodoList:
    def __init__(self, parent):
        self.tasks = []
        self.frame = tk.Frame(parent)
        self.frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Title Label
        self.title_label = tk.Label(self.frame, text="To-Do List", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=(0, 10))

        # Listbox with Scrollbar
        self.listbox_frame = tk.Frame(self.frame)
        self.listbox_frame.pack()

        self.listbox = tk.Listbox(self.listbox_frame, height=10, width=30, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        self.scrollbar = tk.Scrollbar(self.listbox_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        # Entry for new tasks
        self.entry = tk.Entry(self.frame, width=30)
        self.entry.pack(pady=(5, 10))
        self.entry.bind("<Return>", lambda event: self.add_task())  # Add task on Enter

        # Buttons
        self.add_button = tk.Button(self.frame, text="Add Task", command=self.add_task)
        self.add_button.pack(pady=(0, 5))

        self.delete_button = tk.Button(self.frame, text="Delete Task", command=self.delete_task)
        self.delete_button.pack(pady=(0, 10))

        # Task Counter
        self.task_count_label = tk.Label(self.frame, text="Total Tasks: 0", font=("Helvetica", 10))
        self.task_count_label.pack()

        self.entry.focus()  # Set focus on entry widget

    def add_task(self):
        task = self.entry.get().strip()
        if task:
            self.tasks.append(task)
            self.listbox.insert(tk.END, task)
            self.entry.delete(0, tk.END)
            self.update_task_count()
            self.entry.focus()  # Focus back on entry
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    def delete_task(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.tasks.pop(index)
            self.listbox.delete(index)
            self.update_task_count()
        else:
            messagebox.showwarning("Warning", "You must select a task to delete.")

    def update_task_count(self):
        count = len(self.tasks)
        self.task_count_label.config(text=f"Total Tasks: {count}")

# Example Usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Enhanced To-Do List")
    todo_list = TodoList(root)
    root.mainloop()
