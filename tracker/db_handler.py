import sqlite3
from datetime import datetime
from tracker.activity_tracker import key_count, click_count

# Initialize SQLite DB
conn = sqlite3.connect('activity_tracker.db')
cursor = conn.cursor()

# Create the table with `date` as the PRIMARY KEY
cursor.execute('''
CREATE TABLE IF NOT EXISTS activity (
    date TEXT PRIMARY KEY, 
    keys_pressed INTEGER, 
    mouse_clicks INTEGER,
    time REAL DEFAULT 0  -- Column for total time elapsed in minutes
)
''')
conn.commit()

def save_daily_data(elapsed_time):
    
    from tracker.activity_tracker import key_count, click_count
    date = datetime.now().strftime('%Y-%m-%d')
    
    # Convert elapsed time from seconds to minutes
    elapsed_time_minutes = round(elapsed_time / 60 , 2)

    # Use INSERT OR REPLACE to update the data if the date already exists
    cursor.execute('''
        INSERT INTO activity (date, keys_pressed, mouse_clicks, time) 
        VALUES (?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET 
            keys_pressed = keys_pressed + ?,
            mouse_clicks = mouse_clicks + ?,
            time = time + ?  -- Update total elapsed time in minutes
    ''', (date, key_count, click_count, elapsed_time_minutes, key_count, click_count, elapsed_time_minutes))
    
    conn.commit()
    print("Data updated!")
