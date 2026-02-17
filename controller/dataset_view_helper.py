import sqlite3
import os

from datetime import datetime
from typing import Optional, List, Dict, Any

import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout,QLabel, QComboBox, QTreeView,
    QHeaderView,QLineEdit, QMessageBox, 
    QDialog, QFormLayout, QDialogButtonBox, QDateEdit,QCheckBox
)
from PySide6.QtCore import Qt, Signal, QDate, QAbstractTableModel, QModelIndex
from view.style import StyleUtils
from controller.path_manager import path_manager


class DataTreeModel(QAbstractTableModel):
    """A model to display pandas DataFrame in a QTreeView with proper typing."""
    
    def __init__(self, data: pd.DataFrame = pd.DataFrame(), parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._data = data

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of rows in the model."""
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of columns in the model."""
        return len(self._data.columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Optional[str]:
        """Return the data for the given role and index."""
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        value = self._data.iloc[index.row(), index.column()]
        if pd.isna(value):
            return ""
        if isinstance(value, (pd.Timestamp, datetime)):
            return value.strftime("%Y-%m-%d")
        return str(value)

    def headerData(self, section: int, orientation: Qt.Orientation, 
                 role: int = Qt.DisplayRole) -> Optional[str]:
        """Return the header data for the given section, orientation and role."""
        if role != Qt.DisplayRole:
            return None
        return str(self._data.columns[section]) if orientation == Qt.Horizontal else str(section + 1)

    def set_data(self, data: pd.DataFrame) -> None:
        """Set new data for the model."""
        self.beginResetModel()
        self._data = data
        # add items to the row 
        self.endResetModel()

    def get_data(self) -> pd.DataFrame:
        """Get the current DataFrame."""
        return self._data


class DataTreeView(QTreeView):
    """A custom tree view for displaying tabular data with enhanced features."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        self._model = DataTreeModel()
        self.setModel(self._model)

    def _setup_ui(self) -> None:
        """Configure the view's appearance and behavior."""
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setUniformRowHeights(True)
        self.setSelectionMode(QTreeView.SingleSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionsClickable(True)

    def display_dataframe(self, df: pd.DataFrame) -> None:
        """Display a pandas DataFrame in the view."""
        self._model.set_data(df)
        self._resize_columns()

    def _resize_columns(self) -> None:
        """Resize columns to fit content."""
        for i in range(self._model.columnCount()):
            self.resizeColumnToContents(i)

    def get_selected_row_data(self) -> Dict[str, Any]:
        """Get data from the currently selected row."""
        index = self.currentIndex()
        if not index.isValid():
            return {}
            
        model = self.model()
        return {
            str(model.headerData(i, Qt.Horizontal)): model.data(model.index(index.row(), i))
            for i in range(model.columnCount())
        }


class EditTaskDialog(QDialog):
    """A dialog for editing task information with validation."""
    
    task_updated = Signal()
    
    def __init__(self, task_data: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.task_id = task_data.get('id', '')
        self.categories: List[str] = []
        
        self._init_ui()
        self._load_data(task_data)
        self.setWindowTitle(f"✏️ Edit Task (ID 👉🏼 {self.task_id})")
        self.resize(400, 500)

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        StyleUtils.style_text_input(self.title_edit)
        form_layout.addRow("Title:", self.title_edit)
        
        self.category_combo = QComboBox()
        StyleUtils.style_dropdown(self.category_combo)
        form_layout.addRow("Category:", self.category_combo)
        
        self.priority_combo = QComboBox()
        StyleUtils.style_dropdown(self.priority_combo)
        self.priority_combo.addItems(["High", "Medium", "Low"])
        form_layout.addRow("Priority:", self.priority_combo)

        self.status_combo = QComboBox()
        StyleUtils.style_dropdown(self.status_combo)
        self.status_combo.addItems(["Pending", "Working", "Completed"])
        form_layout.addRow("Status:", self.status_combo)
        
        self.create_date_edit = QDateEdit()
        StyleUtils.style_date_edit(self.create_date_edit)
        self.create_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.create_date_edit.setCalendarPopup(True)
        form_layout.addRow("Created Date:", self.create_date_edit)

        self.complete_checkbox_combo = QCheckBox("Edit Completed Date")
        self.complete_checkbox_combo.toggled.connect(
                lambda: self.completed_date_edit.setEnabled(self.complete_checkbox_combo.isChecked())
            )
        form_layout.addRow(self.complete_checkbox_combo)

        self.completed_date_edit = QDateEdit()
        StyleUtils.style_date_edit(self.completed_date_edit)
        self.completed_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.completed_date_edit.setCalendarPopup(True)
        self.completed_date_edit.setEnabled(False)
        form_layout.addRow("Completed Date:", self.completed_date_edit)
        
        layout.addLayout(form_layout)

        self.info = QLabel("Note: Completed Date is optional. \n Will only update if Status is Completed.")
        layout.addWidget(self.info)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._validate_and_update)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def is_completed(self) -> bool:
        """Check if the task is marked as completed."""
        if self.status_combo.currentText() == "Completed" and self.complete_checkbox_combo.isChecked():
            return True
        return False
    def _load_data(self, task_data: Dict[str, Any]) -> None:
        """Load task data into the form."""
        self.title_edit.setText(task_data.get('title', ''))
        self.priority_combo.setCurrentText(task_data.get('priority', 'Medium'))
        self.status_combo.setCurrentText(task_data.get('status', 'Pending'))
        
        self._set_date(self.create_date_edit, task_data.get('created_date', ''))
        self._set_date(self.completed_date_edit, task_data.get('completed_date', ''))
        
        self._load_categories(task_data.get('category', ''))

    def _set_date(self, date_edit: QDateEdit, date_str: str) -> None:
        """Set date in QDateEdit from string."""
        date = QDate.fromString(date_str, "yyyy-MM-dd")
        if date.isValid():
            date_edit.setDate(date)
        else:
            date_edit.setDate(QDate.currentDate())
            date_edit.clear()

    def _load_categories(self, current_category: str) -> None:
        """Load categories from database and select current one."""
        try:
            with sqlite3.connect(path_manager.get_path('db')) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM categories")
                self.categories = [row[0] for row in cursor.fetchall()]
            
            self.category_combo.clear()
            self.category_combo.addItems(self.categories)
            
            if current_category in self.categories:
                self.category_combo.setCurrentText(current_category)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load categories: {str(e)}")

    def _validate_and_update(self) -> None:
        """Validate inputs and update task if valid."""
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Warning", "Title cannot be empty")
            return
            
        self._update_task(self.is_completed())

    def _update_task(self, has_completed_date: bool = True) -> None:
        """Update the task in the database, optionally including completed_date."""
        try:
            with sqlite3.connect(path_manager.get_path('db')) as conn:
                cursor = conn.cursor()

                # Get category ID
                cursor.execute("SELECT id FROM categories WHERE name = ?", 
                            (self.category_combo.currentText(),))
                category_id = cursor.fetchone()[0]

                # Common fields
                title = self.title_edit.text().strip()
                priority = self.priority_combo.currentText()
                status = self.status_combo.currentText()
                created_date = self.create_date_edit.date().toString("yyyy-MM-dd")

                # Prepare query
                if has_completed_date and self.completed_date_edit.date().isValid():
                    completed_date = self.completed_date_edit.date().toString("yyyy-MM-dd")
                    query = """
                        UPDATE tasks 
                        SET title = ?, category_id = ?, priority = ?, status = ?,
                            created_date = ?, completed_date = ?
                        WHERE id = ?
                    """
                    params = (title, category_id, priority, status, created_date, completed_date, self.task_id)
                else:
                    query = """
                        UPDATE tasks 
                        SET title = ?, category_id = ?, priority = ?, status = ?,
                            created_date = ?, completed_date = NULL
                        WHERE id = ?
                    """
                    params = (title, category_id, priority, status, created_date, self.task_id)

                cursor.execute(query, params)
                conn.commit()

            self.task_updated.emit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update task: {str(e)}")


class DatabaseManager:
    """Handles all database operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path if db_path else path_manager.get_path('db')
        
    def get_tables(self) -> List[str]:
        """Get list of all tables in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                return [table[0] for table in cursor.fetchall()]
        except Exception as e:
            raise DatabaseError(f"Failed to get tables: {str(e)}")

    def get_table_data(self, table_name: str, date_columns: List[str] = None) -> pd.DataFrame:
        """
        Get data from a table with optional date parsing.
        
        Args:
            table_name: Name of the table to query
            date_columns: List of columns that should be parsed as dates
            
        Returns:
            DataFrame containing the table data
        """
        try:
            query = self._build_query(table_name)
            return pd.read_sql_query(
                query, 
                sqlite3.connect(self.db_path),
                parse_dates=date_columns or []
            )
        except Exception as e:
            raise DatabaseError(f"Failed to get table data: {str(e)}")

    def _build_query(self, table_name: str) -> str:
        """Build appropriate SQL query for the table."""
        if table_name == 'tasks':
            return """
                SELECT tasks.*, categories.name as category_name 
                FROM tasks 
                LEFT JOIN categories ON tasks.category_id = categories.id
                """
        return f"SELECT * FROM {table_name}"

    def detect_date_columns(self, table_name: str) -> List[str]:
        """Detect columns that contain date/datetime data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                return [
                    col[1] for col in cursor.fetchall()
                    if any(date_type in str(col[2]).lower() 
                      for date_type in ['date', 'time', 'timestamp'])
                ]
        except Exception as e:
            raise DatabaseError(f"Error detecting date columns: {str(e)}")

    def delete_task(self, task_id: str) -> None:
        """Delete a task from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
        except Exception as e:
            raise DatabaseError(f"Failed to delete task: {str(e)}")


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass

