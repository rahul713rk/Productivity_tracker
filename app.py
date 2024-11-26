import tkinter as tk
from tkinter import ttk
from visualization.plot import show_graph
from tracker.database import Database
from tracker.stopwatch import StopwatchApp
from tracker.todo import Todo
from tracker.markdown_handler import MarkdownHandler
from tracker.activity_tracker import start_tracking , stop_tracking
from setting.git import GitApp 
from setting.dataviewer import DataViewerApp

class ProductivityTracker:
    def __init__(self):
        # Main Window
        self.root = tk.Tk()
        self.root.title("Productivity Tracker")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = int(screen_width * 1)
        window_height = int(screen_height * 1)
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        # self.root.wm_state('normal')

        # Tab Control
        tab_control = ttk.Notebook(self.root)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab3 = ttk.Frame(tab_control)
        tab4 = ttk.Frame(tab_control)

        tab_control.add(tab1, text="Stopwatch & To-Do List")
        tab_control.add(tab2, text="Visualization")
        tab_control.add(tab3 , text= 'Database')
        tab_control.add(tab4 , text= "Accounts")
        
        tab_control.pack(expand=1, fill='both')

        self.stopwatch = StopwatchApp(tab1)
        self.todo_list = Todo(tab1)
        start_tracking(self.stopwatch)
        self.db = Database()
        self.markdown = MarkdownHandler()

        show_graph(tab2)
        
        self.Viewer = DataViewerApp(tab3)

        self.setting = GitApp(tab4)


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
