import sqlite3
import tkinter as tk
from tkinter import Toplevel, ttk, messagebox, filedialog
import traceback
import pandas as pd
import numpy as np
from typing import Optional, Any, Dict, List
from datetime import datetime
from tkinter.scrolledtext import ScrolledText
import plotly.express as px
import webbrowser
import os
from tkcalendar import Calendar

from tracker.database import Database

class DataViewerApp:
    """An advanced Tkinter application for comprehensive data viewing and analysis."""

    def __init__(self, root):
        self.root = root
        
        # Setup main containers
        self.setup_layout()
        
        # Initialize state
        self.df = pd.DataFrame()
        self.original_df = pd.DataFrame()
        self.current_sort_column: Optional[str] = None
        self.sort_ascending: bool = True
        
        # Store date columns for proper handling
        self.date_columns: List[str] = []

        # Path for files
        self.graph_file_path = os.path.abspath('./resources/db/graph.html')
        self.database_file_path = os.path.abspath('./resources/db/main.db')
        
        # Create UI Components
        self.create_widgets()
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
        
        # Load available tables
        self.load_tables()

    def setup_layout(self) -> None:
        """Create and configure the main application layout with improved styling."""
        self.style = ttk.Style()
        self.style.theme_use('clam')  # More modern theme
        
        # Main frame with padding
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.pack(fill="both", expand=True)
        
        # Split into control and data frames
        self.control_frame = ttk.Frame(self.frame, width=250)
        self.control_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        self.data_frame = ttk.Frame(self.frame)
        self.data_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Enhanced status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=2)

    def detect_date_columns(self, table_name: str) -> List[str]:
        """Detect columns that contain date/datetime data."""
        try:
            conn = sqlite3.connect('./resources/db/main.db')
            cursor = conn.cursor()
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Look for date-related column types
            date_columns = [
                col[1] for col in columns 
                if any(date_type in str(col[2]).lower() 
                      for date_type in ['date', 'time', 'timestamp'])
            ]
            
            conn.close()
            return date_columns
            
        except Exception as e:
            self.show_error(f"Error detecting date columns: {str(e)}")
            return []

    def load_data(self, event=None) -> None:
        """Load data from SQL database with proper datetime handling."""
        try:
            table_name = self.table_var.get()
            if not table_name:
                return
            
            conn = sqlite3.connect(self.database_file_path)
            
            # Detect date columns first
            self.date_columns = self.detect_date_columns(table_name)
            
            # Special handling for tasks table with join
            if table_name == 'tasks':
                query = """
                SELECT tasks.*, categories.name as category_name 
                FROM tasks 
                LEFT JOIN categories ON tasks.category_id = categories.id
                """
            else:
                query = f"SELECT * FROM {table_name}"
            
            self.df = pd.read_sql_query(
                query, 
                conn,
                parse_dates=self.date_columns
            )
            
            # Store original data
            self.original_df = self.df.copy()
            
            conn.close()
            
            # Update column menu
            column_name = list(self.df.columns)
            self.column_menu['values'] = column_name
            self.x_col_menu['values'] = column_name
            self.y_col_menu['values'] = column_name
            
            # Display data
            self.display_dataframe()
            self.create_context_menu()
            self.update_status(f"Loaded {len(self.df)} records successfully")
            
        except Exception as e:
            self.show_error(f"Failed to load data: {str(e)}")

    def load_tables(self):
        """Improved table loading with error handling and async-like behavior."""
        try:
            conn = sqlite3.connect(self.database_file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            conn.close()
            
            # Update table combobox
            self.table_combo['values'] = tables
            
            # Optional: set first table as default if exists
            if tables:
                self.table_var.set(tables[2])
                self.load_data()
                
        except Exception as e:
            self.show_error(f"Failed to load tables: {str(e)}")

    def format_cell_value(self, value: Any) -> str:
        """Format cell values for display, with special handling for datetime."""
        if pd.isna(value):
            return ""
        elif isinstance(value, (pd.Timestamp, datetime)):
            return value.strftime("%Y-%m-%d")
        return str(value)

    def display_dataframe(self) -> None:
        """Display the current DataFrame in the Treeview with formatted datetime values."""
        # Clear existing items
        self.tree.delete(*self.tree.get_children())
        
        # Configure columns
        self.tree["columns"] = list(self.df.columns)
        self.tree["show"] = "headings"
        
        # Set column headings and adjust widths
        for col in self.df.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            
            # Calculate maximum width based on column content
            if col in self.date_columns:
                # Use fixed width for date columns
                width = 150
            else:
                max_width = max(
                    len(str(col)),
                    self.df[col].apply(lambda x: len(self.format_cell_value(x))).max() 
                    if len(self.df) > 0 else 0
                )
                width = min(max_width * 10, 300)
            
            self.tree.column(col, width=width)
        
        # Insert data with formatted values
        for idx, row in self.df.iterrows():
            values = [self.format_cell_value(val) for val in row]
            self.tree.insert("", "end", values=values)

    def create_widgets(self) -> None:
        """Create and configure all UI widgets with improved layout and functionality."""
        # Create control panels
        self.create_data_controls()
        self.create_statistical_controls()
        self.create_graph_controls()
        self.create_search_panel()
        self.create_other_controls()

        # Create data view
        self.create_data_view()

    def create_data_view(self) -> None:
        """Create the main data viewing area with Treeview."""
        # Create Treeview with scrollbars
        self.tree_frame = ttk.Frame(self.data_frame)
        self.tree_frame.pack(fill="both", expand=True)
        
        self.tree = ttk.Treeview(self.tree_frame)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        
        # Configure Treeview
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)

    def create_data_controls(self) -> None:
        """Create data manipulation control section."""
        controls_frame = ttk.LabelFrame(self.control_frame, text="Table Controls")
        controls_frame.pack(fill="x", pady=10)

        combo_frame = ttk.Frame(controls_frame)
        combo_frame.pack(fill="x" , pady=5)

        table_frame = ttk.Frame(combo_frame)
        table_frame.pack(fill='x' ,pady=3, padx=3 , side='left')

        column_frame = ttk.Frame(combo_frame)
        column_frame.pack(fill='x' ,pady=3, padx=3 , side='right')

        ttk.Label(table_frame, text="Select Table").pack(padx = 3)
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(
            table_frame, 
            textvariable=self.table_var, 
            state="readonly",
            width=12
        )
        self.table_combo.pack(side='left',padx=3)
        self.table_combo.bind('<<ComboboxSelected>>', self.load_data)
        
        # Column selection for sorting and operations
        ttk.Label(column_frame, text="Select Column").pack(padx = 3)
        self.column_var = tk.StringVar()
        self.column_menu = ttk.Combobox(
            column_frame,
            textvariable=self.column_var,
            state="readonly",
            width=12
        )
        self.column_menu.pack(side='left',padx=3)
        
        # Sorting buttons
        sort_frame = ttk.Frame(controls_frame)
        sort_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(sort_frame,text="Sorting").pack(pady=(0,3))
        ttk.Button(
            sort_frame, 
            text="▲ Ascending", 
            command=lambda: self.sort_by_column(ascending=True),
            width=12
        ).pack(side="left", padx=2)
        
        ttk.Button(
            sort_frame, 
            text="▼ Descending", 
            command=lambda: self.sort_by_column(ascending=False),
            width=12
        ).pack(side="right", padx=2)

    def sort_by_column(self, column: Optional[str] = None, ascending: bool = True) -> None:
        """Sort the DataFrame by the selected column with proper datetime handling."""
        # If no column provided, use the currently selected column
        if column is None:
            column = self.column_var.get()
        
        if not column:
            self.show_warning("Please select a column to sort by")
            return
            
        try:
            # Handle datetime sorting
            if column in self.date_columns:
                # Ensure column is in datetime format before sorting
                self.df[column] = pd.to_datetime(self.df[column])
            
            self.df = self.df.sort_values(by=column, ascending=ascending)
            self.display_dataframe()
            self.update_status(f"Sorted by {column} ({'Ascending' if ascending else 'Descending'})")
            
        except Exception as e:
            self.show_error(f"Error sorting data: {str(e)}")

    def create_statistical_controls(self) -> None:
        """Create advanced statistical analysis controls."""
        stats_frame = ttk.LabelFrame(self.control_frame, text="Statistical Analysis")
        stats_frame.pack(fill="x", pady=10 , padx=3)
        
        combo_frame = ttk.Frame(stats_frame)
        combo_frame.pack(padx=3 , pady=3 , fill='x' , side='left')

        # Aggregation dropdown
        ttk.Label(combo_frame, text="Select Function").pack(padx=3)
        self.agg_var = tk.StringVar()
        self.agg_menu = ttk.Combobox(
            combo_frame,
            textvariable=self.agg_var,
            values=[
                "Count", "Min", "Max", "Mean", 
                "Median", "Sum", 
                "Unique Count"
            ],
            state="readonly",
            width=12
        )
        self.agg_menu.pack(padx=3)
        
        # Apply aggregation button
        ttk.Button(
            stats_frame, 
            text="Apply", 
            command=self.apply_advanced_aggregation
        ).pack(padx=3,pady=3 , side='right')

    def create_search_panel(self) -> None:
        """Simplified search panel with only contains search."""
        search_frame = ttk.LabelFrame(self.control_frame, text="Search")
        search_frame.pack(fill="x", pady=5 , padx=5)
        
        self.search_var = tk.StringVar()
        
        # Search entry
        search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var, 
            width=20
        )
        search_entry.pack(pady=5)
        
        # Add trace to trigger search on typing
        self.search_var.trace('w', self.on_search)

    def on_search(self, *args) -> None:
        """Simplified search method that checks if search text is contained in any column."""
        try:
            search_text = self.search_var.get().lower().strip()
            
            if search_text:
                # Reset index of original DataFrame to ensure consistent indexing
                original_df_reset = self.original_df.reset_index(drop=True)
                
                # Create a mask for rows containing the search text
                mask = original_df_reset.apply(
                    lambda row: any(
                        search_text in str(val).lower() 
                        for val in row if pd.notna(val)
                    ), 
                    axis=1
                )
                
                # Filter the DataFrame
                self.df = original_df_reset[mask].copy()
            else:
                # Reset to original data if search is empty
                self.df = self.original_df.copy()
            
            # Display the filtered data
            self.display_dataframe()
            
            # Update status with number of matching records
            self.update_status(f"Found {len(self.df)} matching records")
            
        except Exception as e:
            # Reset the view and show error message
            self.reset_view()
            self.show_error(f"Search error: {str(e)}")
            print(f"Search error: {str(e)}")
            traceback.print_exc()  # Print full traceback for debugging

    def create_other_controls(self) -> None:
        """Create export , reset and delete controls."""
        other_frame = ttk.LabelFrame(self.control_frame , text='Other Controls')
        other_frame.pack(fill='x' , padx=3 , pady=3)

        export_frame = ttk.Frame(other_frame)
        export_frame.pack(fill="x", pady=5)

        delete_frame = ttk.Frame(other_frame)
        delete_frame.pack(fill='x' , pady=5)
        
        ttk.Button(
            export_frame, 
            text="Export to CSV", 
            command=self.export_data
        ).pack(side="left", padx=5, expand=True)
        
        ttk.Button(
            export_frame, 
            text="Reset View", 
            command=self.reset_view
        ).pack(side="right", padx=5, expand=True)

        ttk.Button(
            delete_frame, 
            text="Delete\nDatabase",
            command=self.delete_database
        ).pack(side="left", padx=5, expand=True)
        
        ttk.Button(
            delete_frame, 
            text="Delete\nGraph",
            command=self.delete_html_files
        ).pack(side='right', padx=5, expand=True)

    def apply_advanced_aggregation(self) -> None:
        """Enhanced aggregation with more statistical functions."""
        col = self.column_var.get()
        agg_func = self.agg_var.get()
        
        if not (col and agg_func):
            self.show_warning("Please select both a column and aggregation function")
            return
            
        try:
            if agg_func == "Count":
                result = self.df[col].value_counts()
            elif agg_func == "Unique Count":
                result = pd.Series([self.df[col].nunique()], index=['Unique Count'])
            elif agg_func == "Median":
                result = pd.Series([self.df[col].median()], index=['Median'])
            elif agg_func == "Std Dev":
                result = pd.Series([self.df[col].std()], index=['Std Deviation'])
            elif agg_func == "Variance":
                result = pd.Series([self.df[col].var()], index=['Variance'])
            else:
                result = pd.Series([getattr(self.df[col], agg_func.lower())()], index=[agg_func])
                
            # Create new DataFrame for display
            self.df = result.reset_index()
            self.df.columns = ['Statistic', 'Value']
            
            self.display_dataframe()
            self.update_status(f"Applied {agg_func} aggregation on {col}")
            
        except Exception as e:
            self.show_error(f"Error applying aggregation: {str(e)}")

    def export_data(self) -> None:
        """Enhanced export with user file selection."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")],
                title="Export Data"
            )
            
            if not filename:
                return
            
            export_df = self.df.copy()
            
            # Convert datetime columns to string for export
            for col in self.date_columns:
                export_df[col] = export_df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            
            # Determine file type and export accordingly
            if filename.endswith('.csv'):
                export_df.to_csv(filename, index=False)
            elif filename.endswith('.xlsx'):
                export_df.to_excel(filename, index=False)
            
            self.update_status(f"Data exported to {filename}")
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            
        except Exception as e:
            self.show_error(f"Error exporting data: {str(e)}")

    def setup_shortcuts(self) -> None:
        """Enhanced keyboard shortcuts."""
        shortcut_map = {
            '<Control-r>': self.reset_view,
            '<Control-e>': self.export_data,
            '<Control-f>': lambda: self.search_var.set(''),
            '<Control-s>': lambda: self.table_combo.event_generate('<<ComboboxSelected>>'),
            '<Control-a>': self.apply_advanced_aggregation
        }
        
        for shortcut, action in shortcut_map.items():
            self.root.bind(shortcut, lambda e, a=action: a())

    def update_status(self, message: str) -> None:
        """Update the status bar message."""
        self.status_var.set(message)

    def show_warning(self, message: str) -> None:
        """Show a warning message dialog."""
        messagebox.showwarning("Warning", message)

    def show_error(self, message: str) -> None:
        """Show an error message dialog."""
        messagebox.showerror("Error", message)
        # Optional: log the error
        print(f"Error: {message}")
        self.reset_view()

    def reset_view(self) -> None:
        """Reset the view to show original data."""
        self.refresh_data()
        self.df = self.original_df.copy()
        self.search_var.set('')
        self.display_dataframe()
        self.update_status("View reset to original data")

    def create_graph_controls(self):
        graph_frame = ttk.LabelFrame(self.control_frame , text = 'Graph Controls')
        graph_frame.pack(fill='x' , pady=5)

        combo_frame =  ttk.Frame(graph_frame)
        combo_frame.pack(fill='x' , pady=5)

        x_combo_frame = ttk.Frame(combo_frame)
        x_combo_frame.pack(fill='x' , side='left' , pady = 3 , padx=3)

        y_combo_frame = ttk.Frame(combo_frame)
        y_combo_frame.pack(fill='x' , side='right' , pady = 3 , padx=3)

        ttk.Label(x_combo_frame , text='X-Column').pack(padx=3)
        self.x_col_var = tk.StringVar()
        self.x_col_menu = ttk.Combobox(
            x_combo_frame,
            textvariable=self.x_col_var,
            state='readonly',
            width=12
        )
        self.x_col_menu.pack(side = 'left' , padx=3)


        ttk.Label(y_combo_frame , text='Y-Column').pack(padx=3)
        self.y_col_var = tk.StringVar()
        self.y_col_menu = ttk.Combobox(
            y_combo_frame,
            textvariable=self.y_col_var,
            state='readonly',
            width=12
        )
        self.y_col_menu.pack(side = 'left' , padx=3)


        button_frame = ttk.Frame(graph_frame)
        button_frame.pack(fill='x' , pady=5)

        graph_type_frame = ttk.Frame(button_frame)
        graph_type_frame.pack(fill='x' , side='left' , pady = 3 , padx=3)


        ttk.Label(graph_type_frame , text='Graph Type').pack(padx=3)
        self.graph_type = tk.StringVar()
        self.graph_type_menu = ttk.Combobox(
            graph_type_frame,
            textvariable=self.graph_type,
            values=['Line' , 'Area' , 'Bar'],
            state='readonly',
            width=12
        )
        self.graph_type_menu.pack(side = 'left' , padx=3)

        ttk.Button(
            button_frame, 
            text="Show\nGraph",
            command=self.save_plot_as_html 
        ).pack(padx=3,pady=5 , side='right')

    def generate_graph(self):
        graph_type = self.graph_type.get()
        df = self.original_df
        x_col = self.x_col_var.get()
        y_col = self.y_col_var.get()

        if x_col == y_col:
            fig = px.bar(df , x = x_col , y = y_col ,
                          title='Productivity Tracker\n(Bar Graph)' , labels={y_col : f'{y_col}' , x_col : f'{x_col}'},
                          template='seaborn')
        else:
            if graph_type == 'Line':
                fig = px.line(df , x = x_col , y = y_col ,
                            title='Productivity Tracker\n(Line Graph)' , labels={y_col : f'{y_col}' , x_col : f'{x_col}'},
                            template='seaborn')
            elif graph_type == 'Area':
                fig = px.area(df , x = x_col , y = y_col ,
                            title='Productivity Tracker\n(Area Graph)' , labels={y_col : f'{y_col}' , x_col : f'{x_col}'},
                            template='seaborn')
            else:
                fig = px.bar(df , x = x_col , y = y_col ,
                            title='Productivity Tracker\n(Bar Graph)' , labels={y_col : f'{y_col}' , x_col : f'{x_col}'},
                            template='seaborn')

        return fig
    
    def save_plot_as_html(self):
        fig = self.generate_graph()
        fig.write_html(self.graph_file_path)
        webbrowser.open(f'file://{os.path.realpath(self.graph_file_path)}')

    def delete_html_files(self):
        if messagebox.askyesno("Confirm Delete" , "Do you want delete this graph file?"):
            if os.path.exists(self.graph_file_path):
                os.remove(self.graph_file_path)
                print("Graph File ⥤ Deleted")
            else:
                print("No File to Delete")

    def delete_database(self):
        if messagebox.askyesno("Confirm Delete" , "Do you want delete the Database?"):
            if os.path.exists(self.database_file_path):
                os.remove(self.database_file_path)
                print("Database ⥤ Deleted")
                self.reset_view()
            else:
                print("No Database To Delete")
    
    def refresh_data(self):
        data = Database()
        self.load_tables()

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Edit", command=lambda: self.edit_task())
        self.tree.bind("<Button-3>", lambda e: self.show_context_menu(e, self.tree))
    
    def show_context_menu(self, event, tree):
        try:
            table_name = self.table_var.get()
            if table_name == 'tasks':
                tree.selection_set(tree.identify_row(event.y))
                self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def edit_frame(self, frame):
        # Task entry
        task_label = ttk.Label(frame, text='Title')
        task_label.pack(padx=5, pady=5)

        self.task_entry = ttk.Entry(frame, width=30)
        self.task_entry.pack(padx=5, pady=5)

        # Category selection
        category_label = ttk.Label(frame, text='Category')
        category_label.pack(padx=5, pady=5)

        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(frame, textvariable=self.category_var,
                                        values=self.get_categories(), width=15)
        self.category_combo.pack(padx=5, pady=5)

        # Priority selection
        priority_label = ttk.Label(frame, text='Priority')
        priority_label.pack(padx=5, pady=5)
        self.priority_var = tk.StringVar()
        self.priority_combo = ttk.Combobox(frame, textvariable=self.priority_var,
                                        values=['High', 'Medium', 'Low'], width=10)
        self.priority_combo.pack(padx=5, pady=5)

        # date selection
        date_label = ttk.Label(frame, text='Select Date')
        date_label.pack(padx=5, pady=5)

        self.calendar = Calendar(frame, selectmode='day',
                                year=datetime.now().year,
                                month=datetime.now().month,
                                day=datetime.now().day ,date_pattern='yyyy-mm-dd')
        self.calendar.pack(padx=5, pady=5)
    
    def edit_task(self):
        """Open a pop-up window for Git account setup"""
        self.title_popup = Toplevel(self.root)
        self.title_popup.title("Edit Task")
        self.title_popup.geometry("500x600")

        selected_tree = self.tree
        selected_item = selected_tree.selection()

        if selected_item:
            dic = {}
            item_id = selected_item[0]
            dic['task_id'] = selected_tree.item(item_id)['values'][0]  # Fetch hidden ID
            dic['title'] = selected_tree.item(item_id)['values'][1]
            dic['category'] = selected_tree.item(item_id)['values'][7]
            dic['priority'] = selected_tree.item(item_id)['values'][3]
            dic['date'] = selected_tree.item(item_id)['values'][5]

        # Create main frame with padding
        main_frame = ttk.Frame(self.title_popup, padding="10")
        main_frame.pack(padx=5 , pady=5, fill='x')

        self.edit_frame(main_frame)
        self.task_entry.insert(0,dic['title'])
        self.category_combo.set(dic['category'])
        self.priority_combo.set(dic['priority'])
        self.calendar.selection_set(date=dic['date'])

        def update_task():
            title = self.task_entry.get().strip()
            category = self.category_combo.get().strip()
            priority = self.priority_combo.get().strip()
            created_date = self.calendar.get_date()

            if (title != None) and (category != None) and (priority != None) and (created_date != None):
                try:
                    conn = sqlite3.connect(self.database_file_path)
                    self.cursor = conn.cursor()
                    self.cursor.execute(
                                            """
                                        UPDATE tasks 
                                        SET created_date = ?
                                        WHERE id = ?
                                        """,
                                            (created_date, dic['task_id']),
                                        )
                    conn.commit()
                    conn.close()
                    self.task_entry.delete(0 , tk.END)
                    self.reset_view()
                    self.title_popup.destroy()

                except Exception as e:
                    self.show_error(f"Failed to load tables: {str(e)}")
        
        ttk.Button(main_frame, text="Update", command=update_task).pack(pady=20)

    def get_categories(self):
        conn = sqlite3.connect(self.database_file_path)
        self.cursor = conn.cursor()
        self.cursor.execute("SELECT name FROM categories")
        category = [row[0] for row in self.cursor.fetchall()]
        conn.close()
        return category