import tkinter as tk
from .stopwatch_helper import Stopwatch_Helper
from tkinter import ttk

class Stopwatch_interface:
    def __init__(self, parent):
        self.parent = parent
        self.helper = Stopwatch_Helper()

        # Main frame
        self.frame = tk.Frame(parent)
        self.frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Create components through modular functions
        self.timer_display()
        self.button_controls()
        self.lap_display()
        self.activity_counters()

        # Start tracking and update counts
        self.helper.start_tracking()
        self.update_counts()
        self.update_timer_display()  # Start timer display updates

    def timer_display(self):
        """Create and display the stopwatch timer."""
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill='x', pady=(0, 10))

        title_label = ttk.Label(title_frame, text="Stopwatch",
                                font=('Helvetica', 16, 'bold'))
        title_label.pack(side='left')
        self.label = tk.Label(self.frame, text="00:00:00", font=("Helvetica", 48))
        self.label.pack(pady=10)

    def button_controls(self):
        """Create and display control buttons."""
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(pady=5)

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side="left", padx=5)
        self.reset_button.config(state='disabled')

        self.lap_button = tk.Button(self.button_frame, text="Lap", command=self.record_lap)
        self.lap_button.pack(side="left", padx=5)

    def lap_display(self):
        """Create and display the lap records."""
        self.lap_listbox = tk.Listbox(self.frame, font=("Helvetica", 14), width=30)
        self.lap_listbox.pack(pady=10)

    def activity_counters(self):
        """Create and display key and click counters."""
        self.counter_frame = tk.Frame(self.frame)
        self.counter_frame.pack(pady=5)

        self.key_count_label = tk.Label(self.counter_frame, text=f"Keys: {self.helper.key_count}", font=("Helvetica", 14))
        self.key_count_label.pack(side="left", padx=10)

        self.click_count_label = tk.Label(self.counter_frame, text=f"Clicks: {self.helper.click_count}", font=("Helvetica", 14))
        self.click_count_label.pack(side="left", padx=10)

    def start(self):
        """Start the stopwatch."""
        self.helper.start()
        self.update_timer_display()  # Start updating the timer display

    def stop(self):
        """Stop the stopwatch."""
        self.helper.stop()

    def reset(self):
        """Reset the stopwatch."""
        self.reset_button.config(state="disabled")
        self.helper.reset()
        self.lap_listbox.delete(0, tk.END)  # Clear lap records
        self.label.config(text="00:00:00")  # Reset the timer display

    def record_lap(self):
        """Record a lap time."""
        self.helper.record_lap()
        self.update_lap_display()

    def update_lap_display(self):
        """Update the lap records in the listbox."""
        self.lap_listbox.delete(0, tk.END)  # Clear current list
        for i, lap in enumerate(self.helper.lap_times):
            self.lap_listbox.insert(tk.END, f"Lap {i + 1}: {self.helper.format_time(lap)}")

    def update_counts(self):
        """Update key and click counts every second."""
        self.key_count_label.config(text=f"Keys: {self.helper.key_count}")
        self.click_count_label.config(text=f"Clicks: {self.helper.click_count}")
        self.parent.after(1000, self.update_counts)  # Update every second

    def update_timer_display(self):
        """Update the timer display."""
        if self.helper.running:  # Update only if the stopwatch is running
            elapsed_time = self.helper.elapsed_time  # Get the elapsed time
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_format = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            self.label.config(text=time_format)  # Update the timer label
        self.parent.after(100, self.update_timer_display)  # Update every 100 ms

# if __name__ == "__main__":
#     root = tk.Tk()
#     stopwatch = Stopwatch_interface(root)
#     root.title("Stopwatch")
#     root.geometry("400x500")
#     root.mainloop()
