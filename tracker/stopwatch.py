import tkinter as tk
from tkinter import ttk , messagebox
import time
import cv2
from PIL import Image, ImageTk ,ImageDraw



class StopwatchApp:
    def __init__(self, root):
        self.parent = root

        # Stopwatch variables
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.lap_times = []
        self.last_time = 0
        self.key_count = 0
        self.click_count = 0

        # Face detection variables
        self.cap = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_detected = False

        # Create the GUI
        self.setup_ui()

        self.initialize_camera()


    def setup_ui(self):
        """Setup the entire user interface."""
        self.frame = tk.Frame(self.parent , width=25)
        self.frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)

        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill='x', pady=(0, 10))
        title_label = ttk.Label(title_frame, text="Stopwatch", font=('Helvetica', 20, 'bold'))
        title_label.pack(side='left')

        # Timer display
        self.label = tk.Label(self.frame, text="00:00:00", font=("Helvetica", 48))
        self.label.pack(pady=10)

        # Control buttons
        self.frame_2  = ttk.LabelFrame(self.frame , text='Controls')
        self.frame_2.pack(fill='x' , padx=5 , pady=5)

        self.lap_frame = ttk.LabelFrame(self.frame_2 , text="Lap Records")
        self.lap_frame.pack(side='left' , fill= 'none' , padx=10 , pady=5)

        self.button_frame = ttk.Frame(self.frame_2)
        self.button_frame.pack(side='right',pady=5, padx=10)

        self.button_frame1 = ttk.Frame(self.button_frame)
        self.button_frame1.pack(pady=5)

        self.button_frame2 = ttk.Frame(self.button_frame)
        self.button_frame2.pack(pady=5)

        self.start_button = ttk.Button(self.button_frame1, text="Start", command=self.start)
        self.start_button.pack(side="left", padx=5)
        self.stop_button = ttk.Button(self.button_frame1, text="Stop", command=self.stop)
        self.stop_button.pack(side="right", padx=5)
        self.reset_button = ttk.Button(self.button_frame2, text="Reset", command=self.reset)
        self.reset_button.pack(side="left", padx=5)
        self.lap_button = ttk.Button(self.button_frame2, text="Lap", command=self.record_lap)
        self.lap_button.pack(side="right", padx=5)

        # Lap display
        
        self.lap_listbox = tk.Listbox(self.lap_frame, font=("Helvetica", 14), width=15 , height=5)
        self.lap_listbox.pack(pady=10 )


        # Activity counters
        self.counter_frame = ttk.LabelFrame(self.frame , text='Activity Tracker')
        self.counter_frame.pack(pady=5 , fill='x')
        self.key_count_label = ttk.Label(self.counter_frame, text=f"Keys: {self.key_count}", font=("Helvetica", 16))
        self.key_count_label.pack(side="left", padx=10)
        self.click_count_label = ttk.Label(self.counter_frame, text=f"Clicks: {self.click_count}", font=("Helvetica", 16))
        self.click_count_label.pack(side="left", padx=10)

        # Video feed frame
        self.cam_frame = ttk.LabelFrame(self.frame, text="Camera")
        self.cam_frame.pack(fill="both", expand=False)

        # Inner frame to contain video feed
        self.video_frame = ttk.Label(self.cam_frame, text="Start the Camera", font=("Helvetica", 14))
        self.video_frame.pack(fill="both", expand=False)

        # Toggle camera button
        self.camera_button_frame = ttk.Frame(self.cam_frame)
        self.camera_button_frame.pack(fill='x' , side='bottom' , pady=5)

        self.start_camera_button = ttk.Button(self.camera_button_frame,
                                        text='Start Camera',
                                        command=self.start_camera)
        self.start_camera_button.pack(pady=5, side='left')

        self.stop_camera_button = ttk.Button(self.camera_button_frame,
                                        text='Stop Camera',
                                        command=self.stop_camera)
        self.stop_camera_button.pack(pady=5, side='right')

        # Schedule updates
        self.update_timer_display()
        self.update_counts()
        self.update_camera_feed()

    def initialize_camera(self):
        """Check if the camera is available and initialize."""
        if self.cap is None:
            try:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise ValueError("Camera not accessible.")
            except Exception:
                self.cap = None
                self.video_frame.config(text="Camera not available")
                self.start_camera_button.config(state="disabled")
                self.stop_camera_button.config(state='disabled')


    def start_camera(self):
        """Start the camera and initialize the video feed."""
        try:
            self.cap = cv2.VideoCapture(0)
        except Exception:
            print("error camera is not starting")
        if self.cap.isOpened():
            self.start_camera_button.config(state='disabled')
            self.stop_camera_button.config(state='normal')
            self.update_camera_feed()

    def stop_camera(self):
        """Stop the camera and display a placeholder."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        self.start_camera_button.config(state='normal')
        self.stop_camera_button.config(state='disabled')
        self.video_frame.imgtk = None
        self.video_frame.config(image=None)
        # self.video_frame.config(text="Camera Feed")

    def update_camera_feed(self):
        """Update the video feed and detect faces."""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                self.face_detected = len(faces) > 0
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                frame = cv2.resize(frame, (300, 200))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(frame))
                self.video_frame.imgtk = img
                self.video_frame.config(image=img)
            if self.face_detected:
                self.start()
            else:
                self.stop()
        if self.cap and self.cap.isOpened():
            self.parent.after(50, self.update_camera_feed)

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
        if messagebox.askyesno("Confirmation " , 'Do you want to Reset ? '):
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
    
    def __del__(self):
        if self.cap:
            self.cap.release()