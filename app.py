import tkinter as tk
from tkinter import ttk
from visualization.plot import show_graph
from tracker.database import Database
from tracker.stopwatch_interface import Stopwatch_interface
from tracker.todo_interface import Todo_interface

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
        self.stopwatch = Stopwatch_interface(tab1)
        self.todo_list = Todo_interface(tab1)
        self.db = Database()

        # Visualization
        show_graph(tab2)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Handle app closure gracefully."""

        # Save data
        self.db.save_daily_data()

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
