import tkinter as tk
from tkinter import ttk
from visualization.plot import show_graph
from tracker.database import Database
from tracker.stopwatch import StopwatchApp
from tracker.todo import Todo
from tracker.markdown_handler import MarkdownHandler
from tracker.activity_tracker import start_tracking , stop_tracking
from setting.git import GitApp 

class ProductivityTracker:
    def __init__(self):
        # Main Window
        self.root = tk.Tk()
        self.root.title("Productivity Tracker")
        self.root.geometry("900x700")
        # self.root.wm_state('normal')

        # Tab Control
        tab_control = ttk.Notebook(self.root)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab3 = ttk.Frame(tab_control)

        tab_control.add(tab1, text="Stopwatch & To-Do List")
        tab_control.add(tab2, text="Visualization")
        tab_control.add(tab3 , text= "Accounts")
        tab_control.pack(expand=1, fill='both')

        # Stopwatch and To-Do List
        self.stopwatch = StopwatchApp(tab1)
        self.todo_list = Todo(tab1)
        start_tracking(self.stopwatch)
        self.db = Database()
        self.markdown = MarkdownHandler()

        # Visualization
        show_graph(tab2)
        

        # Setting
        self.setting = GitApp(tab3)


        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Handle app closure gracefully."""

        # Save data
        self.db.save_daily_data(data=self.stopwatch.export_vars())
        self.markdown.markdown_helper()

        # Close resources from TodoList
        self.todo_list.close_resources()
        stop_tracking()
        self.db.close()

        self.setting.git_handler.commit_and_push()
        # Destroy the main window
        self.root.destroy()

    def run(self):
        """Run the Tkinter main loop."""
        self.root.mainloop()


if __name__ == "__main__":
    app = ProductivityTracker()
    app.run()
