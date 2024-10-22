import sqlite3
from datetime import datetime
import os

os.makedirs("./resources/db", exist_ok=True)
filename = "./resources/db/main.db"
conn = sqlite3.connect(filename)
cursor = conn.cursor()


def save_daily_data(elapsed_time):

    from tracker.activity_tracker import key_count, click_count

    date = datetime.now().strftime("%Y-%m-%d")

    # Convert elapsed time from seconds to minutes
    elapsed_time_minutes = round(elapsed_time / 60, 2)

    # Use INSERT OR REPLACE to update the data if the date already exists
    self.cursor.execute(
        """
        INSERT INTO activity (date, keys_pressed, mouse_clicks, time) 
        VALUES (?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET 
            keys_pressed = keys_pressed + ?,
            mouse_clicks = mouse_clicks + ?,
            time = time + ?  -- Update total elapsed time in minutes
    """,
        (
            date,
            key_count,
            click_count,
            elapsed_time_minutes,
            key_count,
            click_count,
            elapsed_time_minutes,
        ),
    )

    conn.commit()
    print("Data updated!")
