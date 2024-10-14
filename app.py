import tkinter as tk
from tkinter import ttk
from tracker.stopwatch import Stopwatch
from tracker.todo_list import TodoList
from tracker.activity_tracker import start_tracking
from tracker.db_handler import save_daily_data
from visualization.plot import show_graph

# Main Window
root = tk.Tk()
root.title("Productivity Tracker")
root.geometry("800x400")

# Tab Control
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)

tab_control.add(tab1, text="Stopwatch & To-Do List")
tab_control.add(tab2, text="Visualization")
tab_control.pack(expand=1, fill='both')

# Stopwatch and To-Do List
stopwatch = Stopwatch(tab1)
todo_list = TodoList(tab1)

# Visualization
show_graph(tab2)

# Start Tracking when Stopwatch runs
start_tracking(stopwatch)

# Save data when closing the app
# Save data when closing the app
root.protocol("WM_DELETE_WINDOW", lambda: (save_daily_data(stopwatch.get_elapsed_time()), root.destroy()))

root.mainloop()
