import sqlite3
from datetime import datetime
import os


class Database:
    def __init__(self):
        os.makedirs("./resources/db", exist_ok=True)
        filename = "./resources/db/main.db"
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Create categories table
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )"""
        )

        # Create tasks table with foreign key to categories
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category_id INTEGER,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            created_date TEXT NOT NULL,
            completed_date TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )"""
        )

        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS activity (
            date TEXT PRIMARY KEY, 
            keys_pressed INTEGER DEFAULT 0, 
            mouse_clicks INTEGER DEFAULT 0,
            time REAL DEFAULT 0  -- Column for total time elapsed in minutes
        )
        """
        )

        # Insert default categories
        default_categories = ["Coding", "Reading"]
        for category in default_categories:
            self.cursor.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,)
            )

        self.conn.commit()

    def add_task(self, title, category, priority, status):
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get category_id
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        result = self.cursor.fetchone()
        category_id = result[0] if result else None

        self.cursor.execute(
            """
        INSERT INTO tasks (title, category_id, priority, status, created_date)
        VALUES (?, ?, ?, ?, ?)
        """,
            (title, category_id, priority, status, created_date),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update_task_status(self, task_id, new_status):
        completed_date = (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if new_status == "Done"
            else None
        )
        self.cursor.execute(
            """
        UPDATE tasks 
        SET status = ?, completed_date = ?
        WHERE id = ?
        """,
            (new_status, completed_date, task_id),
        )
        self.conn.commit()

    def get_today_tasks(self):
        today_date = datetime.today().strftime("%Y-%m-%d")

        # Execute the query with a WHERE clause for today's date
        self.cursor.execute(
            """
            SELECT tasks.id, tasks.title, categories.name, tasks.priority, tasks.status, 
           tasks.created_date, tasks.completed_date
            FROM tasks
            LEFT JOIN categories ON tasks.category_id = categories.id
            WHERE DATE(tasks.created_date) = ?
            ORDER BY 
            CASE tasks.priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
                END,
            tasks.created_date DESC
            """,
            (today_date,),
        )
        return self.cursor.fetchall()

    def get_all_tasks(self):
        # Execute the query with a WHERE clause for today's date
        self.cursor.execute(
            """
            SELECT tasks.id, tasks.title, categories.name, tasks.priority, tasks.status, 
           tasks.created_date, tasks.completed_date
            FROM tasks
            LEFT JOIN categories ON tasks.category_id = categories.id
            WHERE DATE(tasks.created_date) = ?
            ORDER BY 
            CASE tasks.priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
                END,
            tasks.created_date DESC
            """,
        )
        return self.cursor.fetchall()

    def get_today_stats(self):
        today_date = datetime.today().strftime("%Y-%m-%d")

        # Execute the query with a WHERE clause for today's date
        self.cursor.execute(
            """
                SELECT keys_pressed , mouse_clicks , time 
                FROM activity
                WHERE DATE(activity.date) = ?
                """,
            (today_date,),
        )
        stats = self.cursor.fetchall()
        return stats[0] if len(stats) != 0 else None

    def get_categories(self):
        self.cursor.execute("SELECT name FROM categories")
        return [row[0] for row in self.cursor.fetchall()]

    def add_category(self, category_name):
        try:
            self.cursor.execute(
                "INSERT INTO categories (name) VALUES (?)", (category_name,)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def save_daily_data(self, data):
        date = datetime.now().strftime("%Y-%m-%d")
        time, key_count, click_count = data

        print(time, " : ", key_count, " : ", click_count)

        # Convert elapsed time from seconds to minutes
        elapsed_time_minutes = round(time / 60, 2)

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

        self.conn.commit()
        print("Data updated!")
