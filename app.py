# app.py

import tkinter as tk
from tkinter import ttk
from tracker.stopwatch import Stopwatch
from tracker.activity_tracker import start_tracking
from tracker.db_handler import save_daily_data
from visualization.plot import show_graph
from tracker.todo_list import TodoList
from tracker.todo_database import TodoDatabase

class ProductivityTracker:
    def __init__(self):
        # Main Window
        self.root = tk.Tk()
        self.root.title("Productivity Tracker")
        self.root.geometry("800x400")

        # Tab Control
        tab_control = ttk.Notebook(self.root)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)

        tab_control.add(tab1, text="Stopwatch & To-Do List")
        tab_control.add(tab2, text="Visualization")
        tab_control.pack(expand=1, fill='both')

        # Stopwatch and To-Do List
        self.stopwatch = Stopwatch(tab1)
        self.todo_list = TodoList(tab1)
        self.db = TodoDatabase()

        # Visualization
        show_graph(tab2)

        # Start Tracking when Stopwatch runs
        start_tracking(self.stopwatch)

        # Save data and close resources when the app is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Handle app closure gracefully."""
        elapsed_time = self.stopwatch.get_elapsed_time()

        # Save data
        self.db.save_daily_data(elapsed_time)

        # Close resources from TodoList
        self.todo_list.close_resources()

        # Destroy the main window
        self.root.destroy()

    def run(self):
        """Run the Tkinter main loop."""
        self.root.mainloop()


if __name__ == "__main__":
    app = ProductivityTracker()
    app.run()
