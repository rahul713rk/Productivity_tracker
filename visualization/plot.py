import plotly.express as px
import pandas as pd
import sqlite3
import webbrowser
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Global variable to store the HTML file path
PLOT_FILE = './resources/db/activity_tracker_graph.html'
DATABASE_FILE = './resources/db/main.db'

PLOT_FILE_PATH = os.path.abspath(PLOT_FILE)
DATABASE_PATH = os.path.abspath(DATABASE_FILE)


def fetch_data_from_db():
    """Fetch data from the SQLite database."""
    # os.makedirs('./resources/db', exist_ok=True)
    if not os.path.exists(DATABASE_PATH):
        return pd.DataFrame(columns=['date', 'keys_pressed', 'mouse_clicks', 'time'])
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Update SQL query to include time
    cursor.execute('SELECT date, keys_pressed, mouse_clicks, time FROM activity')
    data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Create a DataFrame
    df = pd.DataFrame(data, columns=['date', 'keys_pressed', 'mouse_clicks', 'time'])
    df['date'] = pd.to_datetime(df['date'])
    return df


def generate_plot(df, graph_type):
    """Generate the plot based on the selected graph type."""
    if graph_type == 'Line':
        fig = px.line(df, x='date', y=['keys_pressed', 'mouse_clicks', 'time'],
                      title='Activity Tracker', labels={'value': 'Count/Time (minutes)', 'date': 'Date'},
                      template='plotly_white')
    elif graph_type == 'Bar':
        fig = px.bar(df, x='date', y=['keys_pressed', 'mouse_clicks', 'time'],
                     title='Activity Tracker', labels={'value': 'Count/Time (minutes)', 'date': 'Date'},
                     template='plotly_white', barmode='group')
    else:  # Default to 'Area'
        fig = px.area(df, x='date', y=['keys_pressed', 'mouse_clicks', 'time'],
                      title='Activity Tracker', labels={'value': 'Count/Time (minutes)', 'date': 'Date'},
                      template='plotly_white')

    # Update layout to start axes from 0
    fig.update_layout(yaxis=dict(range=[0, df[['keys_pressed', 'mouse_clicks', 'time']].max().max() + 1]),
                      xaxis=dict(range=[df['date'].min(), df['date'].max()]))
    return fig


def save_plot_as_html(fig):
    """Save the plot as an HTML file."""
    fig.write_html(PLOT_FILE_PATH)
    webbrowser.open(f'file://{os.path.realpath(PLOT_FILE_PATH)}')


def delete_html_file():
    """Delete the HTML file if it exists."""
    if os.path.exists(PLOT_FILE_PATH):
        os.remove(PLOT_FILE_PATH)
        print("HTML file deleted successfully.")
    else:
        print("No HTML file to delete.")


def delete_database(tree, refresh_callback):
    """Delete the Database if it exists."""
    if messagebox.askyesno("Confirm Delete", "Delete this Database?"):
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)
            print("Database deleted successfully.")
            refresh_callback(tree)  # Refresh the data after deletion
        else:
            print("No Database to delete.")


def refresh_data(tree):
    """Refresh the Treeview with updated data."""
    df = fetch_data_from_db()

    # Clear the Treeview
    for item in tree.get_children():
        tree.delete(item)

    # Filter for the last 10 days of data
    last_10_days = df[df['date'] >= (df['date'].max() - pd.Timedelta(days=10))]

    # Insert the new data
    for _, row in last_10_days.iterrows():
        tree.insert('', 'end', values=(row['date'], row['keys_pressed'], row['mouse_clicks'], row['time']))


def show_graph(parent):
    # Fetch data from the database
    df = fetch_data_from_db()

    # Create a Frame for the DataFrame display
    df_frame = ttk.Frame(parent)
    df_frame.pack(pady=10, padx=10, fill='both', expand=True)

    # Create a Treeview to display the last 10 days data
    tree = ttk.Treeview(df_frame, columns=('Date', 'Keys Pressed', 'Mouse Clicks', 'Time (minutes)'), show='headings')
    tree.heading('Date', text='Date')
    tree.heading('Keys Pressed', text='Keys Pressed')
    tree.heading('Mouse Clicks', text='Mouse Clicks')
    tree.heading('Time (minutes)', text='Time (minutes)')
    tree.pack(side='left', fill='both', expand=True)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(df_frame, orient='vertical', command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

    # Initial population of data in the Treeview
    refresh_data(tree)

    # Create a Frame for controls
    control_frame = ttk.Frame(parent)
    control_frame.pack(pady=5)

    # Dropdown for graph type
    graph_type_var = tk.StringVar(value='Line')
    graph_type_dropdown = ttk.Combobox(control_frame, textvariable=graph_type_var,
                                       values=['Area', 'Line', 'Bar'], state='readonly')
    graph_type_dropdown.pack(side='left', padx=5)

    # Create a button to generate and open the plot in the web browser
    def on_open_graph():
        fig = generate_plot(fetch_data_from_db(), graph_type_var.get())
        save_plot_as_html(fig)

    open_button = tk.Button(control_frame, text="Open Graph", command=on_open_graph)
    open_button.pack(side='left', padx=5)

    # Create a button to delete the HTML file
    delete_button = tk.Button(control_frame, text="Delete HTML", command=delete_html_file)
    delete_button.pack(side='left', padx=5)

    # Create a button to delete the database
    delete_db_button = tk.Button(control_frame, text="Delete Database",
                                 command=lambda: delete_database(tree, refresh_data))
    delete_db_button.pack(side='left', padx=5)

