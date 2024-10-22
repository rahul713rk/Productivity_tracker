# todo_list.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkfont
from .todo_database import TodoDatabase
from .markdown_handler import MarkdownHandler

class TodoList:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Initialize database and markdown handler
        self.db = TodoDatabase()
        self.md_handler = MarkdownHandler()

        # Setup styles
        self.setup_styles()

        # Create widgets
        self.create_widgets()

        # Load tasks
        self.load_tasks()

    def setup_styles(self):
        style = ttk.Style()
        style.configure('Priority.High.TLabel', foreground='red')
        style.configure('Priority.Medium.TLabel', foreground='orange')
        style.configure('Priority.Low.TLabel', foreground='green')

    def create_widgets(self):
        # Title
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill='x', pady=(0, 10))

        title_label = ttk.Label(title_frame, text="Enhanced Todo List",
                                font=('Helvetica', 16, 'bold'))
        title_label.pack(side='left')

        # Input area
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(fill='x', pady=5)

        # Task entry
        self.task_entry = ttk.Entry(input_frame, width=30)
        self.task_entry.pack(side='left', padx=5)
        self.task_entry.bind("<Return>", lambda e: self.add_task())

        # Category selection
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var,
                                           values=self.db.get_categories(), width=15)
        self.category_combo.pack(side='left', padx=5)
        self.category_combo.set('Personal')  # Default category

        # Priority selection
        self.priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(input_frame, textvariable=self.priority_var,
                                      values=['High', 'Medium', 'Low'], width=10)
        priority_combo.pack(side='left', padx=5)
        priority_combo.set('Medium')  # Default priority

        # Buttons frame
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(fill='x', pady=5)

        # Add task button
        add_button = ttk.Button(buttons_frame, text="Add Task", command=self.add_task)
        add_button.pack(side='left', padx=5)

        # Add category button
        add_cat_button = ttk.Button(buttons_frame, text="Add Category",
                                    command=self.add_category)
        add_cat_button.pack(side='left', padx=5)

        # Delete task button
        delete_button = ttk.Button(buttons_frame, text="Delete Task",
                                   command=self.delete_task)
        delete_button.pack(side='left', padx=5)

        # Task list
        self.tree = ttk.Treeview(self.frame, columns=('Title', 'Category', 'Priority', 'Status'),
                                 show='headings', height=15)

        # Configure columns
        self.tree.heading('Title', text='Title')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Priority', text='Priority')
        self.tree.heading('Status', text='Status')

        self.tree.column('Title', width=200)
        self.tree.column('Category', width=100)
        self.tree.column('Priority', width=70)
        self.tree.column('Status', width=70)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical",
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Right-click menu for status change
        self.create_context_menu()

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Set Pending",
                                      command=lambda: self.change_status("Pending"))
        self.context_menu.add_command(label="Set Working",
                                      command=lambda: self.change_status("Working"))
        self.context_menu.add_command(label="Set Done",
                                      command=lambda: self.change_status("Done"))

        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def add_task(self):
        title = self.task_entry.get().strip()
        if title:
            category = self.category_var.get()
            priority = self.priority_var.get()
            self.db.add_task(title, category, priority, "Pending")
            self.task_entry.delete(0, tk.END)
            self.load_tasks()
        else:
            messagebox.showwarning("Warning", "Please enter a task title.")

    def add_category(self):
        category = simpledialog.askstring("Add Category", "Enter new category name:")
        if category and self.db.add_category(category):
            self.category_combo['values'] = self.db.get_categories()
            messagebox.showinfo("Success", "Category added successfully!")

    def change_status(self, new_status):
        selected_item = self.tree.selection()
        if selected_item:
            item_id = selected_item[0]
            task_id = self.tree.item(item_id)['values'][4]
            self.db.update_task_status(task_id, new_status)
            self.load_tasks()

    def delete_task(self):
        selected_item = self.tree.selection()
        if selected_item and messagebox.askyesno("Confirm Delete", "Delete this task?"):
            item_id = selected_item[0]
            task_id = self.tree.item(item_id)['values'][4]
            self.db.delete_task(task_id)
            self.load_tasks()

    def load_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        tasks = self.db.get_all_tasks()
        for task in tasks:
            values = (task[1], task[2], task[3], task[4], task[0])
            self.tree.insert('', 'end', values=values, tags=(task[3],))
        stats = self.db.get_latest_stats()
        self.md_handler.update_todo_list(tasks , stats)

    def close_resources(self):
        self.db.close()