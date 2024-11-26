import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from .database import Database

class Todo:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Initialize database and markdown handler
        self.db = Database()
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

        title_label = ttk.Label(title_frame, text="Todo List", font=('Helvetica', 20, 'bold'))
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
                                           values=self.get_categories(), width=15)
        self.category_combo.pack(side='left', padx=5)
        self.category_combo.set('Personal')  # Default category

        # Priority selection
        self.priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(input_frame, textvariable=self.priority_var,
                                      values=['High', 'Medium', 'Low'], width=10)
        priority_combo.pack(side='left', padx=5)
        priority_combo.set('Low')  # Default priority

        # Buttons frame
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(fill='x', pady=5)

        # Add task button
        add_button = ttk.Button(buttons_frame, text="Add Task", command=self.add_task)
        add_button.pack(side='left', padx=5)

        # Delete task button
        delete_button = ttk.Button(buttons_frame, text="Delete Task", command=self.delete_task)
        delete_button.pack(side='left', padx=5)

        # Add category button
        add_cat_button = ttk.Button(buttons_frame, text="Add Category", command=self.add_category)
        add_cat_button.pack(side='left', padx=5)

        # Delete category button
        delete_cat_button = ttk.Button(buttons_frame , text="Delete Category" , command=self.delete_category)
        delete_cat_button.pack(side='left',padx=5)

        # Task Frame
        main_task_frame = ttk.Frame(self.frame)
        main_task_frame.pack(fill='both' , expand=True)

        done_task_frame = ttk.Frame(self.frame)
        done_task_frame.pack(fill='both' , expand=True)

        # Task Tables
        self.main_tree = self.create_tree_table(main_task_frame ,"Task List", height=12)
        self.main_tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.done_tree = self.create_tree_table(done_task_frame ,"Task Completed", height=4)
        self.done_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # Right-click menu for status change
        self.create_context_menu()
    
    def create_tree_table(self , frame , title = 'None' ,  height = 15):
        title_label = ttk.Label(frame, text=title, font=('Helvetica', 15, 'bold'))
        title_label.pack(side='top' , padx=5 , pady=5)

        tree = ttk.Treeview(frame, columns=('Title', 'Category', 'Priority', 'Status'),
                                 show='headings', height=height)

        # Configure columns
        tree.heading('Title', text='Title')
        tree.heading('Category', text='Category')
        tree.heading('Priority', text='Priority')
        tree.heading('Status', text='Status')

        tree.column('Title', width=200)
        tree.column('Category', width=100)
        tree.column('Priority', width=70)
        tree.column('Status', width=70)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        return tree


    def create_context_menu(self):
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Set Pending", command=lambda: self.change_status("Pending"))
        self.context_menu.add_command(label="Set Working", command=lambda: self.change_status("Working"))
        self.context_menu.add_command(label="Set Done", command=lambda: self.change_status("Done"))

        # Bind context menu to both trees
        self.main_tree.bind("<Button-3>", lambda e: self.show_context_menu(e, self.main_tree))
        self.done_tree.bind("<Button-3>", lambda e: self.show_context_menu(e, self.done_tree))

    def show_context_menu(self, event, tree):
        try:
            tree.selection_set(tree.identify_row(event.y))
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()


    def add_task(self):
        title = self.task_entry.get().strip()
        category = self.category_var.get()
        priority = self.priority_var.get()
        
        if title:
            self.db.add_task(title, category, priority, "Pending")
            self.task_entry.delete(0, tk.END)
            self.load_tasks()
        else:
            messagebox.showwarning("Warning", "Please enter a task title.")

    def add_category(self):
        category = simpledialog.askstring("Add Category", "Enter new category name:")
        if category:
            self.db.add_category(category)
            self.category_combo['values'] = self.get_categories()
            messagebox.showinfo("Success", "Category added successfully!")

    def change_status(self, new_status):
        # Determine which tree is currently selected
        selected_tree = self.main_tree if self.main_tree.selection() else self.done_tree
        selected_item = selected_tree.selection()

        if selected_item:
            item_id = selected_item[0]
            task_id = selected_tree.item(item_id)['values'][4]  # Fetch hidden ID
            current_status = selected_tree.item(item_id)['values'][3]  # Current Status

            # Only update if there's an actual status change
            if current_status != new_status:
                self.db.update_task_status(task_id, new_status)
                self.load_tasks()  # Refresh the display


    def delete_task(self):
        selected_tree = self.main_tree if self.main_tree.selection() else self.done_tree
        selected_item = selected_tree.selection()

        if selected_item:
            item_id = selected_item[0]
            task_id = selected_tree.item(item_id)['values'][4]  # Fetch hidden ID

            if messagebox.askyesno("Confirm Delete", "Delete this task?"):
                self.db.delete_task(task_id)
                self.load_tasks()  # Refresh lists after deletion


    def delete_category(self):
        selected_category = self.category_var.get()

        if messagebox.askyesno("Confirm Delete", f"Delete category '{selected_category}'?"):
            self.db.delete_category(selected_category)  # Delete from the database
            print(f"Category '{selected_category}' deleted successfully.")
            self.refresh_categories()
        else:
            print('Category deletion canceled.')
    

    def refresh_categories(self):
        """Refresh the categories in the Combobox after deletion."""
        updated_categories = self.get_categories()
        self.category_combo['values'] = updated_categories

        # Optionally, set the Combobox to a default value
        if "Personal" in updated_categories:
            self.category_combo.set("Personal")
        elif updated_categories:
            self.category_combo.set(updated_categories[0])
        else:
            self.category_combo.set('')

    def load_tasks(self):
        # Clear both trees
        for tree in [self.main_tree, self.done_tree]:
            for item in tree.get_children():
                tree.delete(item)

        # Fetch tasks from the database
        tasks = self.db.get_today_tasks()
        
        # Separate tasks based on their status
        for task in tasks:
            values = (task[1], task[2], task[3], task[4], task[0])  # Title, Category, Priority, Status, ID
            if task[4] == 'Done':
                self.done_tree.insert('', 'end', values=values, tags=(task[3],))
            else:
                self.main_tree.insert('', 'end', values=values, tags=(task[3],))



    def get_categories(self):
        return self.db.get_categories()

    def close_resources(self):
        self.db.close()
