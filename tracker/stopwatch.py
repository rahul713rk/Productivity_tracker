import tkinter as tk
import time
from tracker.activity_tracker import key_count, click_count  # Import global counters

class Stopwatch:
    def __init__(self, master):
        self.master = master
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.lap_times = []
        self.last_time = 0

        # Create a frame for layout
        self.frame = tk.Frame(master)
        self.frame.pack(side="left", fill="both", expand=True)

        # Create a frame for the time and activity counters
        self.info_frame = tk.Frame(self.frame)
        self.info_frame.pack(pady=10)

        # Label to display elapsed time
        self.label = tk.Label(self.info_frame, text="00:00:00", font=("Helvetica", 48))
        self.label.pack(side="left")

        # Labels for key count and click count
        self.key_count_label = tk.Label(self.info_frame, text=f"Keys: {key_count}", font=("Helvetica", 14))
        self.key_count_label.pack(side="left", padx=10)

        self.click_count_label = tk.Label(self.info_frame, text=f"Clicks: {click_count}", font=("Helvetica", 14))
        self.click_count_label.pack(side="left", padx=10)

        # Create a frame for buttons
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack()

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side="left", padx=5)

        self.lap_button = tk.Button(self.button_frame, text="Lap", command=self.record_lap)
        self.lap_button.pack(side="left", padx=5)

        # Listbox to display lap times
        self.lap_listbox = tk.Listbox(self.frame, font=("Helvetica", 14), width=20)
        self.lap_listbox.pack(pady=10)

        # Update key and click counts every second
        self.update_counts()

    def update_counts(self):
        # Update the labels for key and click counts from the global variables
        from tracker.activity_tracker import key_count, click_count  # Re-import to get latest values
        self.key_count_label.config(text=f"Keys: {key_count}")
        self.click_count_label.config(text=f"Clicks: {click_count}")

        # Call this method every second to update counts
        self.master.after(1000, self.update_counts)

    def update_time(self):
        if self.running:
            self.elapsed_time = time.perf_counter() - self.start_time
            hours, remainder = divmod(self.elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_format = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            self.label.config(text=time_format)
            self.master.after(100, self.update_time)

    def start(self):
        if not self.running:
            self.start_time = time.perf_counter() - self.elapsed_time
            self.running = True
            self.update_time()

    def stop(self):
        if self.running:
            self.running = False

    def reset(self):
        self.running = False
        self.elapsed_time = 0
        self.label.config(text="00:00:00")
        self.lap_times.clear()
        self.lap_listbox.delete(0, tk.END)  # Clear the Listbox

    def record_lap(self):
        if self.running:
            # Calculate lap time as the difference from the last lap
            if not self.lap_times:
                lap_time = self.elapsed_time  # First lap
                self.last_time = self.elapsed_time
            else:
                lap_time = self.elapsed_time - self.last_time  # Current lap minus previous laps
                self.last_time = self.elapsed_time

            # Store the current lap time in the lap_times list
            self.lap_times.append(lap_time)

            # Limit to 5 laps in the Listbox
            if len(self.lap_times) > 5:
                self.lap_times.pop(0)  # Remove the oldest lap from the lap_times list

            # Clear and update the Listbox
            self.lap_listbox.delete(0, tk.END)  # Clear the Listbox
            for i, lap in enumerate(self.lap_times):
                self.lap_listbox.insert(tk.END, f"Lap {i + 1}: {self.format_time(lap)}")

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes)}m {int(seconds)}s"
    
    def get_elapsed_time(self):
        return self.elapsed_time  # Return elapsed time in seconds

if __name__ == "__main__":
    root = tk.Tk()
    stopwatch = Stopwatch(root)
    root.title("Stopwatch")
    root.geometry("400x400")
    root.mainloop()
