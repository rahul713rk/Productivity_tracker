import os
import traceback
import webbrowser
from typing import List, Dict, Any

import pandas as pd
import numpy as np
import plotly.express as px

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QComboBox, QPushButton,QLineEdit, QMessageBox, 
    QFileDialog, QMenu, QStatusBar, QGroupBox , QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from view.style import StyleUtils
from model.database import Database
from controller.dataset_view_helper import DatabaseError , DatabaseManager , DataTreeView , EditTaskDialog

class DataViewerApp(QMainWindow):
    """Main application window for data viewing and analysis."""

    def __init__(self):
        super().__init__()
        self._init_state()
        self._setup_ui()
        self._setup_connections()
        self._load_initial_data()

    def _init_state(self) -> None:
        """Initialize application state."""
        self.df = pd.DataFrame()
        self.original_df = pd.DataFrame()
        self.date_columns: List[str] = []
        self.graph_file_path = './assets/resource/data/graph.html'
        self.db_manager = DatabaseManager()

    def _setup_ui(self):
        """Set up the main window UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Control panel with scroll
        self.control_panel = self._create_control_panel()
        control_scroll = QScrollArea()
        control_scroll.setWidgetResizable(True)
        control_scroll.setWidget(self.control_panel) 
        control_scroll.setFixedWidth(320)
        splitter.addWidget(control_scroll)

        # Data panel with scroll
        self.data_panel = self._create_data_panel()
        data_scroll = QScrollArea()
        data_scroll.setWidgetResizable(True)
        data_scroll.setWidget(self.data_panel)
        splitter.addWidget(data_scroll)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)


    def _create_control_panel(self) -> QGroupBox:
        """Create and return the control panel."""
        panel = QGroupBox("⚙️ Control Panel")
        StyleUtils.style_groupbox(panel)
        panel.setMaximumWidth(300)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Add control sections
        self._add_table_controls(layout)
        self._add_statistical_controls(layout)
        self._add_search_controls(layout)
        self._add_graph_controls(layout)
        self._add_other_controls(layout)
        
        layout.addStretch()
        return panel

    def _create_data_panel(self) -> QGroupBox:
        """Create and return the data panel."""
        panel = QGroupBox("📖 Data")
        StyleUtils.style_groupbox(panel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.tree_view = DataTreeView()
        layout.addWidget(self.tree_view)
        
        return panel

    def _add_table_controls(self, layout: QVBoxLayout) -> None:
        """Add table selection controls."""
        group = QGroupBox("")
        StyleUtils.style_groupbox(group)
        group_layout = QVBoxLayout(group)
        
        table_label = QLabel("Select Table")
        StyleUtils.style_badge(table_label)
        self.table_combo = QComboBox()
        StyleUtils.style_dropdown(self.table_combo)
        
        column_label = QLabel("Select Column")
        StyleUtils.style_badge(column_label)
        self.column_combo = QComboBox()
        StyleUtils.style_dropdown(self.column_combo)
        
        group_layout.addWidget(table_label)
        group_layout.addWidget(self.table_combo)
        group_layout.addWidget(column_label)
        group_layout.addWidget(self.column_combo)
        
        layout.addWidget(group)

    def _add_statistical_controls(self, layout: QVBoxLayout) -> None:
        """Add statistical analysis controls."""
        group = QGroupBox("")
        group_layout = QVBoxLayout(group)
        
        func_label = QLabel("Select Function")
        StyleUtils.style_badge(func_label)
        self.func_combo = QComboBox()
        StyleUtils.style_dropdown(self.func_combo)
        self.func_combo.addItems([
            "Count", "Min", "Max", "Mean", 
            "Median", "Sum", "Unique Count"
        ])
        
        self.apply_func_btn = QPushButton("Apply")        
        group_layout.addWidget(func_label)
        group_layout.addWidget(self.func_combo)
        group_layout.addWidget(self.apply_func_btn)
        
        layout.addWidget(group)

    def _add_search_controls(self, layout: QVBoxLayout) -> None:
        """Add search controls."""
        group = QGroupBox("")
        StyleUtils.style_groupbox(group)
        group_layout = QVBoxLayout(group)
        
        search_label = QLabel("Search")
        StyleUtils.style_badge(search_label)
        self.search_input = QLineEdit()
        StyleUtils.style_text_input(self.search_input)
        self.search_input.setPlaceholderText("Search across all columns...")
        
        group_layout.addWidget(search_label)
        group_layout.addWidget(self.search_input)
        
        layout.addWidget(group)

    def _add_graph_controls(self, layout: QVBoxLayout) -> None:
        """Add graph controls."""
        group = QGroupBox("")
        StyleUtils.style_groupbox(group)
        group_layout = QVBoxLayout(group)
        
        # X and Y column selection
        xy_layout = QHBoxLayout()
        
        x_group = QVBoxLayout()
        x_label = QLabel("X Column")
        StyleUtils.style_badge(x_label)
        self.x_col_combo = QComboBox()
        StyleUtils.style_pill_dropdown(self.x_col_combo)
        x_group.addWidget(x_label)
        x_group.addWidget(self.x_col_combo)
        
        y_group = QVBoxLayout()
        y_label = QLabel("Y Column")
        StyleUtils.style_badge(y_label)
        self.y_col_combo = QComboBox()
        StyleUtils.style_pill_dropdown(self.y_col_combo)
        y_group.addWidget(y_label)
        y_group.addWidget(self.y_col_combo)
        
        xy_layout.addLayout(x_group)
        xy_layout.addLayout(y_group)
        group_layout.addLayout(xy_layout)
        
        # Graph type selection
        type_label = QLabel("Graph Type")
        StyleUtils.style_badge(type_label)
        self.graph_type_combo = QComboBox()
        StyleUtils.style_dropdown(self.graph_type_combo)
        self.graph_type_combo.addItems(["Line", "Area", "Bar"])
        
        self.show_graph_btn = QPushButton("Show Graph")        
        group_layout.addWidget(type_label)
        group_layout.addWidget(self.graph_type_combo)
        group_layout.addWidget(self.show_graph_btn)
        
        layout.addWidget(group)

    def _add_other_controls(self, layout: QVBoxLayout) -> None:
        """Add export and reset controls."""
        group = QGroupBox("")
        StyleUtils.style_groupbox(group)
        group_layout = QVBoxLayout(group)
        
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

    def _setup_connections(self) -> None:
        """Set up all signal-slot connections."""
        self.table_combo.currentTextChanged.connect(self.load_data)
        self.apply_func_btn.clicked.connect(self.apply_aggregation)
        self.search_input.textChanged.connect(self.on_search)
        self.show_graph_btn.clicked.connect(self.save_plot_as_html)
        self.export_btn.clicked.connect(self.export_data)
        self.reset_btn.clicked.connect(self.reset_view)
        self.del_db_btn.clicked.connect(self.delete_database)
        self.del_graph_btn.clicked.connect(self.delete_html_files)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

    def _load_initial_data(self) -> None:
        """Load initial data when application starts."""
        try:
            tables = self.db_manager.get_tables()
            self.table_combo.addItems(tables)
            
            if tables and len(tables) > 2:
                self.table_combo.setCurrentText(tables[2])
        except DatabaseError as e:
            self._show_error(f"Failed to load tables: {str(e)}")

    def load_data(self, table_name: str) -> None:
        """Load data from the specified table."""
        if not table_name:
            return
            
        try:
            self.date_columns = self.db_manager.detect_date_columns(table_name)
            self.df = self.db_manager.get_table_data(table_name, self.date_columns)
            self.original_df = self.df.copy()
            
            self._update_column_menus()
            self.tree_view.display_dataframe(self.df)
            self._update_status(f"Loaded {len(self.df)} records")
            
        except DatabaseError as e:
            self._show_error(f"Failed to load data: {str(e)}")

    def _update_column_menus(self) -> None:
        """Update all column selection menus."""
        column_names = list(self.df.columns)
        
        for combo in [self.column_combo, self.x_col_combo, self.y_col_combo]:
            combo.clear()
            combo.addItems(column_names)

    def show_context_menu(self, position) -> None:
        """Show context menu for editing tasks."""
        if self.table_combo.currentText() != 'tasks':
            return
            
        task_data = self.tree_view.get_selected_row_data()
        if not task_data:
            return
            
        menu = QMenu()
        
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(lambda: self._edit_task(task_data))
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self._delete_task(task_data['id']))
        menu.addAction(delete_action)

        menu.exec_(self.tree_view.viewport().mapToGlobal(position))
        self.reset_view()

    def _edit_task(self, task_data: Dict[str, Any]) -> None:
        """Edit the selected task."""
        dialog = EditTaskDialog(task_data, self)
        dialog.task_updated.connect(self.reset_view)
        dialog.exec_()

    def _delete_task(self, task_id: str) -> None:
        """Delete the selected task after confirmation."""
        reply = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this task?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_task(task_id)
                self.reset_view()
                self._update_status("Task deleted successfully")
            except DatabaseError as e:
                self._show_error(f"Failed to delete task: {str(e)}")

    def apply_aggregation(self) -> None:
        """Apply the selected aggregation function to the data."""
        col = self.column_combo.currentText()
        agg_func = self.func_combo.currentText()
        
        if not (col and agg_func):
            self._show_warning("Please select both a column and aggregation function")
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
                
            self.df = result.reset_index()
            self.df.columns = ['Statistic', 'Value']
            
            self.tree_view.display_dataframe(self.df)
            self._update_status(f"Applied {agg_func} on {col}")
            
        except Exception as e:
            self._show_error(f"Error applying aggregation: {str(e)}")

    def on_search(self, text: str) -> None:
        """Filter data based on search text."""
        search_text = text.lower().strip()
        
        if search_text:
            mask = self.original_df.apply(
                lambda row: any(
                    search_text in str(val).lower() 
                    for val in row if pd.notna(val)
                ), 
                axis=1
            )
            self.df = self.original_df[mask].copy()
        else:
            self.df = self.original_df.copy()
        
        self.tree_view.display_dataframe(self.df)
        self._update_status(f"Found {len(self.df)} matching records")

    def export_data(self) -> None:
        """Export data to CSV or Excel file."""
        try:
            filename, selected_filter = QFileDialog.getSaveFileName(
                self, "Export Data", "", "CSV Files (*.csv);;Excel Files (*.xlsx)"
            )
            
            if not filename:
                return
            
            export_df = self.df.copy()
            
            # Convert datetime columns to string for export
            for col in self.date_columns:
                if col in export_df.columns:
                    export_df[col] = export_df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            
            if selected_filter == "CSV Files (*.csv)":
                if not filename.endswith('.csv'):
                    filename += '.csv'
                export_df.to_csv(filename, index=False)
            else:
                if not filename.endswith('.xlsx'):
                    filename += '.xlsx'
                export_df.to_excel(filename, index=False)
            
            self._update_status(f"Data exported to {filename}")
            QMessageBox.information(self, "Export Successful", f"Data exported to {filename}")
            
        except Exception as e:
            self._show_error(f"Error exporting data: {str(e)}")

    def reset_view(self) -> None:
        """Reset the view to show original data."""
        self.df = self.original_df.copy()
        self.search_input.clear()
        self.load_data(self.table_combo.currentText())
        self._update_status("Reset")

    def generate_graph(self):
        """Generate a Plotly graph based on current selections."""
        graph_type = self.graph_type_combo.currentText()
        x_col = self.x_col_combo.currentText()
        y_col = self.y_col_combo.currentText()

        if not x_col or not y_col:
            self._show_warning("Please select both X and Y columns")
            return None

        title = f'Productivity Tracker\n({graph_type} Graph)'
        labels = {y_col: y_col, x_col: x_col}
        
        if x_col == y_col or graph_type == 'Bar':
            return px.bar(self.original_df, x=x_col, y=y_col,
                         title=title, labels=labels, template='seaborn')
        elif graph_type == 'Line':
            return px.line(self.original_df, x=x_col, y=y_col,
                         title=title, labels=labels, template='seaborn')
        else:  # Area graph
            return px.area(self.original_df, x=x_col, y=y_col,
                         title=title, labels=labels, template='seaborn')

    def save_plot_as_html(self) -> None:
        """Save the plot as HTML and open in browser."""
        fig = self.generate_graph()
        if fig is None:
            return
            
        try:
            fig.write_html(self.graph_file_path)
            webbrowser.open(f'file://{os.path.realpath(self.graph_file_path)}')
        except Exception as e:
            self._show_error(f"Failed to save plot: {str(e)}")

    def delete_html_files(self) -> None:
        """Delete the graph HTML file after confirmation."""
        reply = QMessageBox.question(
            self, "Confirm Delete", "Delete this graph file?", QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(self.graph_file_path):
                    os.remove(self.graph_file_path)
                    self._update_status("Graph file deleted")
                else:
                    self._update_status("No graph file to delete")
            except Exception as e:
                self._show_error(f"Failed to delete graph file: {str(e)}")

    def delete_database(self) -> None:
        """Delete the database file after confirmation."""
        reply = QMessageBox.question(
            self, "Confirm Delete", "Delete the database?", QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(self.db_manager.db_path):
                    os.remove(self.db_manager.db_path)
                    data = Database()
                    self._update_status("Database deleted")
                    self.reset_view()
                    data.close()
                else:
                    self._update_status("No database to delete")
            except Exception as e:
                self._show_error(f"Failed to delete database: {str(e)}")

    def _update_status(self, message: str) -> None:
        """Update the status bar message."""
        self.status_bar.showMessage(message)

    def _show_warning(self, message: str) -> None:
        """Show a warning message dialog."""
        QMessageBox.warning(self, "Warning", message)

    def _show_error(self, message: str) -> None:
        """Show an error message dialog and log it."""
        QMessageBox.critical(self, "Error", message)
        print(f"Error: {message}")
        traceback.print_exc()
        self.reset_view()
