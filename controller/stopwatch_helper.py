import time
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

class StopwatchController:
    def __init__(self, view):
        self.view = view
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.lap_times = []
        self.last_time = 0
        self.key_count = 0
        self.click_count = 0

        # Timer for stopwatch and counts update
        self.timer = QTimer(self.view)
        self.timer.timeout.connect(self.update_timer_display)
        self.timer.timeout.connect(self.update_counts)
        self.timer.start(100)  # 100 ms timer for updating the stopwatch

    def isRunning(self):
        """Check if the stopwatch is running."""
        return self.running
    def start(self):
        """Start the stopwatch."""
        if not self.running:
            self.start_time = time.perf_counter() - self.elapsed_time
            self.running = True

    def stop(self):
        """Stop the stopwatch."""
        self.running = False

    def reset(self):
        """Reset the stopwatch."""
        reply = QMessageBox.question(self.view, "Confirmation", "Do you want to reset?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.running = False
            self.elapsed_time = 0
            self.lap_times.clear()
            self.view.update_lap_display(self.lap_times)
            self.view.update_timer_display("00:00:00")

    def record_lap(self):
        """Record a lap time."""
        if self.running:
            lap_time = self.elapsed_time - self.last_time if self.lap_times else self.elapsed_time
            self.last_time = self.elapsed_time
            self.lap_times.append(lap_time)
            if len(self.lap_times) > 10:
                self.lap_times.pop(0)
            self.view.update_lap_display(self.lap_times)

    def update_timer_display(self):
        """Update the timer display."""
        if self.running:
            self.elapsed_time = time.perf_counter() - self.start_time
            time_str = self.format_time(self.elapsed_time)
            self.view.update_timer_display(time_str)

    @staticmethod
    def format_time(seconds):
        """Format time in 'hh:mm:ss' format."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def update_counts(self):
        """Update key and click counts."""
        from controller.activivty_tracker import get_count
        self.key_count, self.click_count = get_count()
        self.view.update_activity_tracker(self.key_count, self.click_count)

    def export_vars(self):
        """Export relevant variables."""
        return [self.elapsed_time, self.key_count, self.click_count]
