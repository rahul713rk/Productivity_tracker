import time
from pynput import keyboard, mouse
import threading

class Stopwatch_Helper:
    def __init__(self):
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.lap_times = []
        self.last_time = 0
        self.key_count = 0
        self.click_count = 0


    def export_variables(self):
        print(self.elapsed_time , self.key_count , self.click_count)
        return self.elapsed_time , self.key_count , self.click_count

    def update_time(self):
        """Update the elapsed time if the stopwatch is running."""
        if self.running:
            self.elapsed_time = time.perf_counter() - self.start_time
            threading.Timer(0.1, self.update_time).start()  # Call every 100ms

    def start(self):
        """Start or resume the stopwatch."""
        if not self.running:
            self.start_time = time.perf_counter() - self.elapsed_time
            self.running = True
            self.update_time()

    def stop(self):
        """Stop the stopwatch."""
        if self.running:
            self.running = False

    def reset(self):
        """Reset the stopwatch and clear lap times."""
        self.running = False
        self.elapsed_time = 0
        self.lap_times.clear()

    def record_lap(self):
        """Record a lap time."""
        if self.running:
            lap_time = self.elapsed_time - self.last_time if self.lap_times else self.elapsed_time
            self.last_time = self.elapsed_time
            self.lap_times.append(lap_time)
            # Limit to the latest 5 laps
            if len(self.lap_times) > 5:
                self.lap_times.pop(0)

    def get_lap_times(self):
        """Return a list of formatted lap times."""
        return [self.format_time(lap) for lap in self.lap_times]

    def format_time(self, seconds):
        """Format time in 'mm:ss' format."""
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes):02}:{int(seconds):02}"

    def on_key_press(self, key):
        """Increment key press count."""
        self.key_count += 1

    def on_click(self, x, y, button, pressed):
        """Increment mouse click count if a button is pressed."""
        if pressed:
            self.click_count += 1

    def start_tracking(self):
        """Start tracking key presses and mouse clicks."""
        keyboard_listener = keyboard.Listener(on_press=lambda key: self.on_key_press(key) if self.running else None)
        mouse_listener = mouse.Listener(on_click=lambda x, y, button, pressed: self.on_click(x, y, button, pressed) if self.running else None)

        # Start listeners in separate threads
        threading.Thread(target=keyboard_listener.start, daemon=True).start()
        threading.Thread(target=mouse_listener.start, daemon=True).start()
