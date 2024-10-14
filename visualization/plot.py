import plotly.express as px
import pandas as pd
import sqlite3
import webbrowser
import os
import tkinter as tk
from tkinter import ttk

def show_graph(parent):
    conn = sqlite3.connect('activity_tracker.db')
    cursor = conn.cursor()

    # Update SQL query to include time
    cursor.execute('SELECT date, keys_pressed, mouse_clicks, time FROM activity')
    data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Create a DataFrame
    df = pd.DataFrame(data, columns=['date', 'keys_pressed', 'mouse_clicks', 'time'])

    # Convert 'date' to datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Filter for the last 10 days of data
    last_10_days = df[df['date'] >= (df['date'].max() - pd.Timedelta(days=10))]

    # Create the plot
    fig = px.line(df, x='date', y=['keys_pressed', 'mouse_clicks', 'time'], 
                  title='Activity Tracker', 
                  labels={'value': 'Count/Time (minutes)', 'date': 'Date'},
                  template='plotly_white')

    # Update layout to start axes from 0
    fig.update_layout(yaxis=dict(range=[0, df[['keys_pressed', 'mouse_clicks', 'time']].max().max() + 1]),
                                  xaxis=dict(range=[df['date'].min(), df['date'].max()]))

    # Save the plot as an HTML file
    plot_file = 'activity_tracker_graph.html'
    fig.write_html(plot_file)

    # Create a Frame for the DataFrame display
    df_frame = ttk.Frame(parent)
    df_frame.pack(pady=10, padx=10, fill='both', expand=True)

    # Create a Treeview to display the last 10 days data
    tree = ttk.Treeview(df_frame, columns=('Date', 'Keys Pressed', 'Mouse Clicks', 'Time (minutes)'), show='headings')
    tree.heading('Date', text='Date')
    tree.heading('Keys Pressed', text='Keys Pressed')
    tree.heading('Mouse Clicks', text='Mouse Clicks')
    tree.heading('Time (minutes)', text='Time (minutes)')  # New heading for time

    # Insert the last 10 days of data into the Treeview
    for _, row in last_10_days.iterrows():
        tree.insert('', 'end', values=(row['date'], row['keys_pressed'], row['mouse_clicks'], row['time']))

    tree.pack(side='left', fill='both', expand=True)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(df_frame, orient='vertical', command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

    # Create a button to open the plot in the web browser
    open_button = tk.Button(parent, text="Open Graph in Browser", command=lambda: webbrowser.open('file://' + os.path.realpath(plot_file)))
    open_button.pack(pady=5)
