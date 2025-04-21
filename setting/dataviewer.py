import sqlite3
import os
import traceback
import webbrowser
from datetime import datetime
from typing import Optional, List, Dict, Any

import pandas as pd
import numpy as np
import plotly.express as px

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QLineEdit, QMessageBox, QFileDialog, QMenu, QStatusBar, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QAction

from tracker.database import Database


class DataViewerApp(QMainWindow):
    """An advanced PySide6 application for comprehensive data viewing and analysis."""

    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle("Data Viewer")
        self.resize(1200, 800)
        
        # Initialize state
        self.df = pd.DataFrame()
        self.original_df = pd.DataFrame()
        self.current_sort_column: Optional[str] = None
        self.sort_ascending: bool = True
        self.date_columns: List[str] = []
        
        # Path for files
        self.graph_file_path = os.path.abspath('./resources/db/graph.html')
        self.database_file_path = os.path.abspath('./resources/db/main.db')
        
        # Create UI
        self.create_widgets()
        self.setup_connections()
        
        # Load initial data
        self.load_tables()

    def create_widgets(self):
        """Create and configure all UI widgets."""
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Splitter for left/right panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left control panel
        self.control_panel = QWidget()
        self.control_panel.setMaximumWidth(300)
        control_layout = QVBoxLayout(self.control_panel)
        control_layout.setContentsMargins(5, 5, 5, 5)
        
        # Right data panel
        self.data_panel = QWidget()
        data_layout = QVBoxLayout(self.data_panel)
        data_layout.setContentsMargins(5, 5, 5, 5)
        
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.data_panel)
        
        # Create sections
        self.create_table_controls(control_layout)
        self.create_statistical_controls(control_layout)
        self.create_search_controls(control_layout)
        self.create_graph_controls(control_layout)
        self.create_other_controls(control_layout)
        
        # Create data view
        self.create_data_view(data_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add stretch to push controls up
        control_layout.addStretch()

    def create_table_controls(self, layout):
        """Create table selection and sorting controls."""
        group = QFrame()
        group.setFrameShape(QFrame.StyledPanel)
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(5, 5, 5, 5)
        
        # Table selection
        table_label = QLabel("Select Table:")
        self.table_combo = QComboBox()
        group_layout.addWidget(table_label)
        group_layout.addWidget(self.table_combo)
        
        # Column selection
        column_label = QLabel("Select Column:")
        self.column_combo = QComboBox()
        group_layout.addWidget(column_label)
        group_layout.addWidget(self.column_combo)
        
        # Sorting buttons
        sort_layout = QHBoxLayout()
        self.asc_sort_btn = QPushButton("▲ Ascending")
        self.desc_sort_btn = QPushButton("▼ Descending")
        sort_layout.addWidget(self.asc_sort_btn)
        sort_layout.addWidget(self.desc_sort_btn)
        
        group_layout.addLayout(sort_layout)
        layout.addWidget(group)

    def create_statistical_controls(self, layout):
        """Create statistical analysis controls."""
        group = QFrame()
        group.setFrameShape(QFrame.StyledPanel)
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(5, 5, 5, 5)
        
        # Aggregation function selection
        func_label = QLabel("Select Function:")
        self.func_combo = QComboBox()
        self.func_combo.addItems([
            "Count", "Min", "Max", "Mean", 
            "Median", "Sum", "Unique Count"
        ])
        
        # Apply button
        self.apply_func_btn = QPushButton("Apply")
        
        group_layout.addWidget(func_label)
        group_layout.addWidget(self.func_combo)
        group_layout.addWidget(self.apply_func_btn)
        
        layout.addWidget(group)

    def create_search_controls(self, layout):
        """Create search controls."""
        group = QFrame()
        group.setFrameShape(QFrame.StyledPanel)
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(5, 5, 5, 5)
        
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search across all columns...")
        
        group_layout.addWidget(search_label)
        group_layout.addWidget(self.search_input)
        
        layout.addWidget(group)

    def create_graph_controls(self, layout):
        """Create graph controls."""
        group = QFrame()
        group.setFrameShape(QFrame.StyledPanel)
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(5, 5, 5, 5)
        
        # X and Y column selection
        xy_layout = QHBoxLayout()
        
        x_group = QVBoxLayout()
        x_label = QLabel("X Column:")
        self.x_col_combo = QComboBox()
        x_group.addWidget(x_label)
        x_group.addWidget(self.x_col_combo)
        
        y_group = QVBoxLayout()
        y_label = QLabel("Y Column:")
        self.y_col_combo = QComboBox()
        y_group.addWidget(y_label)
        y_group.addWidget(self.y_col_combo)
        
        xy_layout.addLayout(x_group)
        xy_layout.addLayout(y_group)
        group_layout.addLayout(xy_layout)
        
        # Graph type selection
        type_label = QLabel("Graph Type:")
        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(["Line", "Area", "Bar"])
        
        # Show graph button
        self.show_graph_btn = QPushButton("Show Graph")
        
        group_layout.addWidget(type_label)
        group_layout.addWidget(self.graph_type_combo)
        group_layout.addWidget(self.show_graph_btn)
        
        layout.addWidget(group)

    def create_other_controls(self, layout):
        """Create export and reset controls."""
        group = QFrame()
        group.setFrameShape(QFrame.StyledPanel)
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(5, 5, 5, 5)
        
        # Button layout
        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export to CSV")
        self.reset_btn = QPushButton("Reset View")
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.reset_btn)
        
        # Delete buttons
        del_layout = QHBoxLayout()
        self.del_db_btn = QPushButton("Delete Database")
        self.del_graph_btn = QPushButton("Delete Graph")
        del_layout.addWidget(self.del_db_btn)
        del_layout.addWidget(self.del_graph_btn)
        
        group_layout.addLayout(btn_layout)
        group_layout.addLayout(del_layout)
        layout.addWidget(group)

    def create_data_view(self, layout):
        """Create the main data viewing area."""
        self.tree_widget = QTreeWidget()
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setSortingEnabled(True)
        self.tree_widget.setUniformRowHeights(True)
        self.tree_widget.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Configure header
        header = self.tree_widget.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionsClickable(True)
        
        layout.addWidget(self.tree_widget)

    def setup_connections(self):
        """Set up all signal-slot connections."""
        # Table controls
        self.table_combo.currentTextChanged.connect(self.load_data)
        self.asc_sort_btn.clicked.connect(lambda: self.sort_by_column(ascending=True))
        self.desc_sort_btn.clicked.connect(lambda: self.sort_by_column(ascending=False))
        
        # Statistical controls
        self.apply_func_btn.clicked.connect(self.apply_advanced_aggregation)
        
        # Search controls
        self.search_input.textChanged.connect(self.on_search)
        
        # Graph controls
        self.show_graph_btn.clicked.connect(self.save_plot_as_html)
        
        # Other controls
        self.export_btn.clicked.connect(self.export_data)
        self.reset_btn.clicked.connect(self.reset_view)
        self.del_db_btn.clicked.connect(self.delete_database)
        self.del_graph_btn.clicked.connect(self.delete_html_files)
        
        # Tree widget connections
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.tree_widget.header().sectionClicked.connect(self.on_header_clicked)

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

    def load_data(self, table_name: str) -> None:
        """Load data from SQL database with proper datetime handling."""
        if not table_name:
            return
            
        try:
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
                sqlite3.connect(self.database_file_path),
                parse_dates=self.date_columns
            )
            
            # Store original data
            self.original_df = self.df.copy()
            
            # Update column menus
            column_names = list(self.df.columns)
            self.column_combo.clear()
            self.column_combo.addItems(column_names)
            
            self.x_col_combo.clear()
            self.x_col_combo.addItems(column_names)
            
            self.y_col_combo.clear()
            self.y_col_combo.addItems(column_names)
            
            # Display data
            self.display_dataframe()
            self.update_status(f"Loaded {len(self.df)} records successfully")
            
        except Exception as e:
            self.show_error(f"Failed to load data: {str(e)}")

    def load_tables(self):
        """Load available tables from the database."""
        try:
            conn = sqlite3.connect(self.database_file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            conn.close()
            
            # Update table combobox
            self.table_combo.clear()
            self.table_combo.addItems(tables)
            
            # Set default table if available
            if tables and len(tables) > 2:
                self.table_combo.setCurrentText(tables[2])
                
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
        """Display the current DataFrame in the TreeWidget."""
        self.tree_widget.clear()
        
        # Set columns
        self.tree_widget.setColumnCount(len(self.df.columns))
        self.tree_widget.setHeaderLabels(list(self.df.columns))
        
        # Add data rows
        for _, row in self.df.iterrows():
            item = QTreeWidgetItem()
            for i, val in enumerate(row):
                item.setText(i, self.format_cell_value(val))
            self.tree_widget.addTopLevelItem(item)
        
        # Resize columns to content
        for i in range(self.tree_widget.columnCount()):
            self.tree_widget.resizeColumnToContents(i)

    def sort_by_column(self, column: Optional[str] = None, ascending: bool = True) -> None:
        """Sort the DataFrame by the selected column with proper datetime handling."""
        # If no column provided, use the currently selected column
        if column is None:
            column = self.column_combo.currentText()
        
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

    def on_header_clicked(self, logical_index: int):
        """Handle header clicks for sorting."""
        column = self.tree_widget.headerItem().text(logical_index)
        self.sort_by_column(column)

    def apply_advanced_aggregation(self) -> None:
        """Enhanced aggregation with more statistical functions."""
        col = self.column_combo.currentText()
        agg_func = self.func_combo.currentText()
        
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

    def on_search(self, text: str) -> None:
        """Search across all columns for the given text."""
        try:
            search_text = text.lower().strip()
            
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
            self.update_status(f"Found {len(self.df)} matching records")
            
        except Exception as e:
            # Reset the view and show error message
            self.reset_view()
            self.show_error(f"Search error: {str(e)}")
            print(f"Search error: {str(e)}")
            traceback.print_exc()

    def export_data(self) -> None:
        """Export data to CSV or Excel file."""
        try:
            filename, selected_filter = QFileDialog.getSaveFileName(
                self,
                "Export Data",
                "",
                "CSV Files (*.csv);;Excel Files (*.xlsx)",
                options=QFileDialog.Options()
            )
            
            if not filename:
                return
            
            export_df = self.df.copy()
            
            # Convert datetime columns to string for export
            for col in self.date_columns:
                export_df[col] = export_df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            
            # Determine file type and export accordingly
            if selected_filter == "CSV Files (*.csv)":
                if not filename.endswith('.csv'):
                    filename += '.csv'
                export_df.to_csv(filename, index=False)
            else:
                if not filename.endswith('.xlsx'):
                    filename += '.xlsx'
                export_df.to_excel(filename, index=False)
            
            self.update_status(f"Data exported to {filename}")
            QMessageBox.information(self, "Export Successful", f"Data exported to {filename}")
            
        except Exception as e:
            self.show_error(f"Error exporting data: {str(e)}")

    def update_status(self, message: str) -> None:
        """Update the status bar message."""
        self.status_bar.showMessage(message)

    def show_warning(self, message: str) -> None:
        """Show a warning message dialog."""
        QMessageBox.warning(self, "Warning", message)

    def show_error(self, message: str) -> None:
        """Show an error message dialog."""
        QMessageBox.critical(self, "Error", message)
        print(f"Error: {message}")
        self.reset_view()

    def reset_view(self) -> None:
        """Reset the view to show original data."""
        self.refresh_data()
        self.df = self.original_df.copy()
        self.search_input.clear()
        self.display_dataframe()
        self.update_status("View reset to original data")

    def generate_graph(self):
        """Generate the plotly graph based on current selections."""
        graph_type = self.graph_type_combo.currentText()
        df = self.original_df
        x_col = self.x_col_combo.currentText()
        y_col = self.y_col_combo.currentText()

        if not x_col or not y_col:
            self.show_warning("Please select both X and Y columns")
            return None

        if x_col == y_col:
            fig = px.bar(df, x=x_col, y=y_col,
                        title='Productivity Tracker\n(Bar Graph)', 
                        labels={y_col: f'{y_col}', x_col: f'{x_col}'},
                        template='seaborn')
        else:
            if graph_type == 'Line':
                fig = px.line(df, x=x_col, y=y_col,
                            title='Productivity Tracker\n(Line Graph)', 
                            labels={y_col: f'{y_col}', x_col: f'{x_col}'},
                            template='seaborn')
            elif graph_type == 'Area':
                fig = px.area(df, x=x_col, y=y_col,
                            title='Productivity Tracker\n(Area Graph)', 
                            labels={y_col: f'{y_col}', x_col: f'{x_col}'},
                            template='seaborn')
            else:
                fig = px.bar(df, x=x_col, y=y_col,
                            title='Productivity Tracker\n(Bar Graph)', 
                            labels={y_col: f'{y_col}', x_col: f'{x_col}'},
                            template='seaborn')

        return fig

    def save_plot_as_html(self):
        """Save the plot as HTML and open in browser."""
        fig = self.generate_graph()
        if fig is None:
            return
            
        fig.write_html(self.graph_file_path)
        webbrowser.open(f'file://{os.path.realpath(self.graph_file_path)}')

    def delete_html_files(self):
        """Delete the graph HTML file."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Do you want to delete this graph file?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if os.path.exists(self.graph_file_path):
                os.remove(self.graph_file_path)
                self.update_status("Graph file deleted")
            else:
                self.update_status("No graph file to delete")

    def delete_database(self):
        """Delete the database file."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Do you want to delete the database?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if os.path.exists(self.database_file_path):
                os.remove(self.database_file_path)
                self.update_status("Database deleted")
                self.reset_view()
            else:
                self.update_status("No database to delete")

    def refresh_data(self):
        """Refresh the data from the database."""
        data = Database()
        self.load_tables()

    def show_context_menu(self, position):
        """Show context menu for editing tasks."""
        table_name = self.table_combo.currentText()
        if table_name != 'tasks':
            return
            
        item = self.tree_widget.itemAt(position)
        if not item:
            return
            
        # Create context menu
        menu = QMenu()
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(lambda: self.edit_task(item))
        menu.addAction(edit_action)
        
        # Show the menu
        menu.exec_(self.tree_widget.viewport().mapToGlobal(position))

    def edit_task(self, item):
        """Edit the selected task."""
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Task")
        dialog.resize(400, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Get task data from the selected item
        task_id = item.text(0)  # Assuming ID is in first column
        title = item.text(1)
        category = item.text(7)  # Adjust indices based on your actual columns
        priority = item.text(3)
        date_str = item.text(5)
        
        # Create form widgets
        form_layout = QFormLayout()
        
        self.title_edit = QLineEdit(title)
        form_layout.addRow("Title:", self.title_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.get_categories())
        self.category_combo.setCurrentText(category)
        form_layout.addRow("Category:", self.category_combo)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])
        self.priority_combo.setCurrentText(priority)
        form_layout.addRow("Priority:", self.priority_combo)
        
        self.date_edit = QDateEdit()
        date = QDate.fromString(date_str, "yyyy-MM-dd")
        self.date_edit.setDate(date)
        form_layout.addRow("Date:", self.date_edit)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.update_task(dialog, task_id))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.exec_()

    def update_task(self, dialog, task_id):
        """Update the task in the database."""
        title = self.title_edit.text().strip()
        category = self.category_combo.currentText()
        priority = self.priority_combo.currentText()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        
        if not title:
            QMessageBox.warning(self, "Warning", "Title cannot be empty")
            return
            
        try:
            conn = sqlite3.connect(self.database_file_path)
            cursor = conn.cursor()
            
            # First get category ID
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
            category_id = cursor.fetchone()[0]
            
            # Update the task
            cursor.execute(
                """
                UPDATE tasks 
                SET title = ?, category_id = ?, priority = ?, created_date = ?
                WHERE id = ?
                """,
                (title, category_id, priority, date, task_id)
            )
            
            conn.commit()
            conn.close()
            
            self.reset_view()
            dialog.accept()
            
        except Exception as e:
            self.show_error(f"Failed to update task: {str(e)}")

    def get_categories(self):
        """Get list of categories from database."""
        try:
            conn = sqlite3.connect(self.database_file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories")
            categories = [row[0] for row in cursor.fetchall()]
            conn.close()
            return categories
        except Exception as e:
            self.show_error(f"Failed to load categories: {str(e)}")
            return []

