import tkinter as tk
from tkinter import ttk
import time



class StopwatchApp:
    def __init__(self, parent):
        self.parent = parent

        # Stopwatch variables
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.lap_times = []
        self.last_time = 0
        self.key_count = 0
        self.click_count = 0

        # Create the GUI
        self.setup_ui()

    def setup_ui(self):
        """Setup the entire user interface."""
        self.frame = tk.Frame(self.parent)
        self.frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill='x', pady=(0, 10))
        title_label = ttk.Label(title_frame, text="Stopwatch", font=('Helvetica', 20, 'bold'))
        title_label.pack(side='left')

        # Timer display
        
        self.label = tk.Label(self.frame, text="00:00:00", font=("Helvetica", 48))
        self.label.pack(pady=10)

        # Control buttons
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

        # Lap display
        self.lap_listbox = tk.Listbox(self.frame, font=("Helvetica", 14), width=30)
        self.lap_listbox.pack(pady=10)

        # Activity counters
        self.counter_frame = tk.Frame(self.frame)
        self.counter_frame.pack(pady=5)
        self.key_count_label = tk.Label(self.counter_frame, text=f"Keys: {self.key_count}", font=("Helvetica", 16))
        self.key_count_label.pack(side="left", padx=10)
        self.click_count_label = tk.Label(self.counter_frame, text=f"Clicks: {self.click_count}", font=("Helvetica", 16))
        self.click_count_label.pack(side="left", padx=10)

        # Schedule updates
        self.update_timer_display()
        self.update_counts()

    def start(self):
        """Start the stopwatch."""
        if not self.running:
            self.start_time = time.perf_counter() - self.elapsed_time
            self.running = True
            self.update_timer_display()  # Start updating the timer display

    def stop(self):
        """Stop the stopwatch."""
        self.running = False

    def reset(self):
        """Reset the stopwatch and clear lap times."""
        self.running = False
        self.elapsed_time = 0
        self.lap_times.clear()
        self.update_lap_display()
        self.label.config(text="00:00:00")

    def record_lap(self):
        """Record a lap time."""
        if self.running:
            lap_time = self.elapsed_time - self.last_time if self.lap_times else self.elapsed_time
            self.last_time = self.elapsed_time
            self.lap_times.append(lap_time)
            # Limit to the latest 5 laps
            if len(self.lap_times) > 5:
                self.lap_times.pop(0)
            self.update_lap_display()

    def update_lap_display(self):
        """Update the lap records in the listbox."""
        self.lap_listbox.delete(0, tk.END)  # Clear current list
        for i, lap in enumerate(self.lap_times):
            formatted_time = self.format_time(lap)
            self.lap_listbox.insert(tk.END, f"Lap {i + 1}: {formatted_time}")

    def update_counts(self):
        """Update key and click counts every second."""
        from .activity_tracker import get_count
        self.key_count, self.click_count = get_count()
        self.key_count_label.config(text=f"Keys: {self.key_count}")
        self.click_count_label.config(text=f"Clicks: {self.click_count}")
        self.parent.after(1000, self.update_counts)  # Update every second

    def update_timer_display(self):
        """Update the timer display."""
        if self.running:
            self.elapsed_time = time.perf_counter() - self.start_time
            hours, remainder = divmod(self.elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_format = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            self.label.config(text=time_format)
        self.parent.after(100, self.update_timer_display)  # Update every 100 ms

    def format_time(self, seconds):
        """Format time in 'mm:ss' format."""
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes):02}:{int(seconds):02}"
    
    def export_vars(self):
        res = [self.elapsed_time , self.key_count , self.click_count]
        # print(res)
        return res