import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import traceback
import pandas as pd
import numpy as np
from typing import Optional, Any, Dict, List
from datetime import datetime
from tkinter.scrolledtext import ScrolledText

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
            
            conn = sqlite3.connect('./resources/db/main.db')
            
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
            self.column_menu['values'] = list(self.df.columns)
            
            # Display data
            self.display_dataframe()
            self.update_status(f"Loaded {len(self.df)} records successfully")
            
        except Exception as e:
            self.show_error(f"Failed to load data: {str(e)}")

    def load_tables(self):
        """Improved table loading with error handling and async-like behavior."""
        try:
            conn = sqlite3.connect('./resources/db/main.db')
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
        self.create_search_panel()
        self.create_export_controls()

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

        ttk.Label(controls_frame, text="Select Table:").pack(pady=(5,0))
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(
            controls_frame, 
            textvariable=self.table_var, 
            state="readonly",
            width=12
        )
        self.table_combo.pack(pady=5)
        self.table_combo.bind('<<ComboboxSelected>>', self.load_data)
        
        # Column selection for sorting and operations
        ttk.Label(controls_frame, text="Select Column:").pack(pady=(5,0))
        self.column_var = tk.StringVar()
        self.column_menu = ttk.Combobox(
            controls_frame,
            textvariable=self.column_var,
            state="readonly",
            width=12
        )
        self.column_menu.pack(pady=5)
        
        # Sorting buttons
        sort_frame = ttk.Frame(controls_frame)
        sort_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(
            sort_frame, 
            text="▲ Ascending", 
            command=lambda: self.sort_by_column(ascending=True),
            width=10
        ).pack(side="left", padx=2)
        
        ttk.Button(
            sort_frame, 
            text="▼ Descending", 
            command=lambda: self.sort_by_column(ascending=False),
            width=10
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
        stats_frame.pack(fill="x", pady=10)
        
        # Aggregation dropdown
        ttk.Label(stats_frame, text="Aggregation Function:").pack(pady=(5,0))
        self.agg_var = tk.StringVar()
        self.agg_menu = ttk.Combobox(
            stats_frame,
            textvariable=self.agg_var,
            values=[
                "Count", "Min", "Max", "Mean", 
                "Median", "Sum", 
                "Unique Count"
            ],
            state="readonly",
            width=25
        )
        self.agg_menu.pack(pady=5)
        
        # Apply aggregation button
        ttk.Button(
            stats_frame, 
            text="Apply Statistical Analysis", 
            command=self.apply_advanced_aggregation
        ).pack(pady=5)

    def create_search_panel(self) -> None:
        """Simplified search panel with only contains search."""
        search_frame = ttk.LabelFrame(self.control_frame, text="Search")
        search_frame.pack(fill="x", pady=10)
        
        self.search_var = tk.StringVar()
        
        # Search entry
        ttk.Label(search_frame, text="Search :").pack(pady=(5,0))
        search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var, 
            width=30
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

    def create_export_controls(self) -> None:
        """Create export and reset controls."""
        export_frame = ttk.Frame(self.control_frame)
        export_frame.pack(fill="x", pady=10)
        
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
        self.df = self.original_df.copy()
        self.search_var.set('')
        self.column_var.set('')
        self.display_dataframe()
        self.update_status("View reset to original data")

    def plot(self):
        pass