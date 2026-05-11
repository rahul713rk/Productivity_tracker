import os
from typing import List, Dict, Any

import pandas as pd
import numpy as np

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QComboBox, QPushButton, QLineEdit, QMessageBox,
    QFileDialog, QMenu, QStatusBar, QGroupBox, QScrollArea,
    QStackedWidget
)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QAction, QPainter, QColor, QFont
from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QBarSeries, QBarSet,
    QBarCategoryAxis, QValueAxis, QAreaSeries, QSplineSeries
)

from view.style import StyleUtils
from model.database import Database
from controller.dataset_view_helper import DatabaseError, DatabaseManager, DataTreeView, EditTaskDialog
from controller.path_manager import path_manager

logger = path_manager.get_logger("DataViewerApp")

# ─────────────────────────────────────────────────────────────────────────────
# Toggle Button Bar
# ─────────────────────────────────────────────────────────────────────────────

_TOGGLE_ACTIVE = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 28px;
        font-size: 14px;
        font-weight: bold;
        border-radius: 4px;
    }
"""
_TOGGLE_INACTIVE = """
    QPushButton {
        background-color: #e0e0e0;
        color: #555;
        border: none;
        padding: 8px 28px;
        font-size: 14px;
        font-weight: bold;
        border-radius: 4px;
    }
    QPushButton:hover { background-color: #c8c8c8; }
"""


class DataViewerApp(QMainWindow):
    """Main application window for data viewing and analysis."""

    # indices for QStackedWidgets
    _DATA_IDX = 0
    _GRAPH_IDX = 1

    def __init__(self):
        super().__init__()
        self._init_state()
        self._setup_ui()
        self._setup_connections()
        self._load_initial_data()

    # ─────────────────────────────────── state ─────────────────────────────────

    def _init_state(self) -> None:
        self.df = pd.DataFrame()
        self.original_df = pd.DataFrame()
        self.date_columns: List[str] = []
        self.db_manager = DatabaseManager()
        logger.info("DataViewerApp initialized.")

    # ─────────────────────────────────── UI setup ──────────────────────────────

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(5, 5, 5, 5)
        root_layout.setSpacing(4)

        # ── Top toggle bar ──────────────────────────────────────────────────
        toggle_bar = QWidget()
        toggle_layout = QHBoxLayout(toggle_bar)
        toggle_layout.setContentsMargins(0, 0, 0, 0)

        self.data_btn = QPushButton("📋  Data")
        self.graph_btn = QPushButton("📊  Graph")
        self.data_btn.setCursor(Qt.PointingHandCursor)
        self.graph_btn.setCursor(Qt.PointingHandCursor)

        toggle_layout.addStretch()
        toggle_layout.addWidget(self.data_btn)
        toggle_layout.addWidget(self.graph_btn)
        toggle_layout.addStretch()
        root_layout.addWidget(toggle_bar)

        # ── Splitter (left panel + right stacked) ───────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        root_layout.addWidget(splitter, 1)

        # Left stacked: context-sensitive controls
        self.left_stack = QStackedWidget()
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(self.left_stack)
        left_scroll.setFixedWidth(320)
        splitter.addWidget(left_scroll)

        self._data_controls = self._create_data_controls()
        self._graph_controls = self._create_graph_controls()
        self.left_stack.addWidget(self._data_controls)   # index 0 = DATA
        self.left_stack.addWidget(self._graph_controls)  # index 1 = GRAPH

        # Right stacked: data table / chart
        self.right_stack = QStackedWidget()
        splitter.addWidget(self.right_stack)

        self.right_stack.addWidget(self._create_data_panel())   # index 0
        self.right_stack.addWidget(self._create_graph_panel())  # index 1

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Start in Data mode
        self._switch_to(self._DATA_IDX)

    # ─────────────────────────────── left panel: data controls ────────────────

    def _create_data_controls(self) -> QGroupBox:
        panel = QGroupBox("⚙️ Data Controls")
        StyleUtils.style_groupbox(panel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(6, 6, 6, 6)

        # Table / column selectors
        tbl_group = QGroupBox("")
        StyleUtils.style_groupbox(tbl_group)
        tg = QVBoxLayout(tbl_group)

        tbl_lbl = QLabel("Select Table")
        StyleUtils.style_badge(tbl_lbl)
        self.table_combo = QComboBox()
        StyleUtils.style_dropdown(self.table_combo)

        col_lbl = QLabel("Select Column")
        StyleUtils.style_badge(col_lbl)
        self.column_combo = QComboBox()
        StyleUtils.style_dropdown(self.column_combo)

        tg.addWidget(tbl_lbl)
        tg.addWidget(self.table_combo)
        tg.addWidget(col_lbl)
        tg.addWidget(self.column_combo)
        layout.addWidget(tbl_group)

        # Statistical aggregation
        stat_group = QGroupBox("")
        sg = QVBoxLayout(stat_group)
        func_lbl = QLabel("Select Function")
        StyleUtils.style_badge(func_lbl)
        self.func_combo = QComboBox()
        StyleUtils.style_dropdown(self.func_combo)
        self.func_combo.addItems([
            "Count", "Min", "Max", "Mean",
            "Median", "Sum", "Unique Count"
        ])
        self.apply_func_btn = QPushButton("Apply")
        sg.addWidget(func_lbl)
        sg.addWidget(self.func_combo)
        sg.addWidget(self.apply_func_btn)
        layout.addWidget(stat_group)

        # Search
        srch_group = QGroupBox("")
        StyleUtils.style_groupbox(srch_group)
        sq = QVBoxLayout(srch_group)
        srch_lbl = QLabel("Search")
        StyleUtils.style_badge(srch_lbl)
        self.search_input = QLineEdit()
        StyleUtils.style_text_input(self.search_input)
        self.search_input.setPlaceholderText("Search across all columns…")
        sq.addWidget(srch_lbl)
        sq.addWidget(self.search_input)
        layout.addWidget(srch_group)

        # Export / Reset / Delete
        other_group = QGroupBox("")
        StyleUtils.style_groupbox(other_group)
        og = QVBoxLayout(other_group)

        btn_row = QHBoxLayout()
        self.export_btn = QPushButton("Export CSV")
        self.reset_btn = QPushButton("Reset View")
        btn_row.addWidget(self.export_btn)
        btn_row.addWidget(self.reset_btn)

        del_row = QHBoxLayout()
        self.del_db_btn = QPushButton("Delete Database")
        del_row.addWidget(self.del_db_btn)

        og.addLayout(btn_row)
        og.addLayout(del_row)
        layout.addWidget(other_group)

        layout.addStretch()
        return panel

    # ─────────────────────────────── left panel: graph controls ───────────────

    def _create_graph_controls(self) -> QGroupBox:
        panel = QGroupBox("📊 Graph Controls")
        StyleUtils.style_groupbox(panel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(6, 6, 6, 6)

        axis_group = QGroupBox("")
        StyleUtils.style_groupbox(axis_group)
        ag = QVBoxLayout(axis_group)

        # ── Table selector (independent from data panel) ──
        gtbl_lbl = QLabel("Select Table")
        StyleUtils.style_badge(gtbl_lbl)
        self.graph_table_combo = QComboBox()
        StyleUtils.style_dropdown(self.graph_table_combo)
        ag.addWidget(gtbl_lbl)
        ag.addWidget(self.graph_table_combo)

        # ── X / Y column pickers ──
        xy_row = QHBoxLayout()

        x_col = QVBoxLayout()
        x_lbl = QLabel("X Column")
        StyleUtils.style_badge(x_lbl)
        self.x_col_combo = QComboBox()
        StyleUtils.style_pill_dropdown(self.x_col_combo)
        x_col.addWidget(x_lbl)
        x_col.addWidget(self.x_col_combo)

        y_col_box = QVBoxLayout()
        y_lbl = QLabel("Y Column")
        StyleUtils.style_badge(y_lbl)
        self.y_col_combo = QComboBox()
        StyleUtils.style_pill_dropdown(self.y_col_combo)
        y_col_box.addWidget(y_lbl)
        y_col_box.addWidget(self.y_col_combo)

        xy_row.addLayout(x_col)
        xy_row.addLayout(y_col_box)
        ag.addLayout(xy_row)

        type_lbl = QLabel("Graph Type")
        StyleUtils.style_badge(type_lbl)
        self.graph_type_combo = QComboBox()
        StyleUtils.style_dropdown(self.graph_type_combo)
        self.graph_type_combo.addItems(["Line", "Spline", "Area", "Bar"])
        ag.addWidget(type_lbl)
        ag.addWidget(self.graph_type_combo)

        self.show_graph_btn = QPushButton("Render Graph")
        StyleUtils.style_primary_button(self.show_graph_btn)
        ag.addWidget(self.show_graph_btn)

        layout.addWidget(axis_group)
        layout.addStretch()
        return panel

    # ──────────────────────────────── right panels ─────────────────────────────

    def _create_data_panel(self) -> QGroupBox:
        panel = QGroupBox("📖 Data")
        StyleUtils.style_groupbox(panel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        self.tree_view = DataTreeView()
        layout.addWidget(self.tree_view)
        return panel

    def _create_graph_panel(self) -> QGroupBox:
        panel = QGroupBox("📊 Chart")
        StyleUtils.style_groupbox(panel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeLight)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)
        return panel

    # ─────────────────────────────── toggle logic ──────────────────────────────

    def _switch_to(self, idx: int):
        self.left_stack.setCurrentIndex(idx)
        self.right_stack.setCurrentIndex(idx)
        if idx == self._DATA_IDX:
            self.data_btn.setStyleSheet(_TOGGLE_ACTIVE)
            self.graph_btn.setStyleSheet(_TOGGLE_INACTIVE)
        else:
            self.data_btn.setStyleSheet(_TOGGLE_INACTIVE)
            self.graph_btn.setStyleSheet(_TOGGLE_ACTIVE)

    # ─────────────────────────────── connections ───────────────────────────────

    def _setup_connections(self) -> None:
        self.data_btn.clicked.connect(lambda: self._switch_to(self._DATA_IDX))
        self.graph_btn.clicked.connect(lambda: self._switch_to(self._GRAPH_IDX))

        self.table_combo.currentTextChanged.connect(self.load_data)
        self.graph_table_combo.currentTextChanged.connect(self._load_graph_data)
        self.apply_func_btn.clicked.connect(self.apply_aggregation)
        self.search_input.textChanged.connect(self.on_search)
        self.show_graph_btn.clicked.connect(self.render_chart)
        self.export_btn.clicked.connect(self.export_data)
        self.reset_btn.clicked.connect(self.reset_view)
        self.del_db_btn.clicked.connect(self.delete_database)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

    # ────────────────────────────── data loading ───────────────────────────────

    def _load_initial_data(self) -> None:
        try:
            tables = self.db_manager.get_tables()
            self.table_combo.addItems(tables)
            self.graph_table_combo.addItems(tables)
            if tables:
                default = tables[2] if len(tables) > 2 else tables[0]
                self.table_combo.setCurrentText(default)
                self.graph_table_combo.setCurrentText(default)
        except DatabaseError as e:
            self._show_error(f"Failed to load tables: {str(e)}")

    def load_data(self, table_name: str) -> None:
        if not table_name:
            return
        try:
            self.date_columns = self.db_manager.detect_date_columns(table_name)
            self.df = self.db_manager.get_table_data(table_name, self.date_columns)
            self.original_df = self.df.copy()
            self._update_data_column_menus()
            self.tree_view.display_dataframe(self.df)
            self._update_status(f"Loaded {len(self.df)} records")
        except DatabaseError as e:
            self._show_error(f"Failed to load data: {str(e)}")

    def _load_graph_data(self, table_name: str) -> None:
        """Load data for the graph panel (independent table selector)."""
        if not table_name:
            return
        try:
            date_cols = self.db_manager.detect_date_columns(table_name)
            self.graph_df = self.db_manager.get_table_data(table_name, date_cols)
            col_names = list(self.graph_df.columns)
            for combo in [self.x_col_combo, self.y_col_combo]:
                combo.clear()
                combo.addItems(col_names)
            self._update_status(f"Graph source: {table_name} ({len(self.graph_df)} records)")
        except DatabaseError as e:
            self._update_status(f"Graph table load failed: {e}")

    def _update_data_column_menus(self) -> None:
        column_names = list(self.df.columns)
        for combo in [self.column_combo]:
            combo.clear()
            combo.addItems(column_names)

    # ───────────────────────────── context menu ────────────────────────────────

    def show_context_menu(self, position) -> None:
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
        dialog = EditTaskDialog(task_data, self)
        dialog.task_updated.connect(self.reset_view)
        dialog.exec_()

    def _delete_task(self, task_id: str) -> None:
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

    # ─────────────────────────── data operations ───────────────────────────────

    def apply_aggregation(self) -> None:
        col = self.column_combo.currentText()
        agg_func = self.func_combo.currentText()
        self.reset_view()
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
            else:
                result = pd.Series(
                    [getattr(self.df[col], agg_func.lower())()], index=[agg_func]
                )
            self.df = result.reset_index()
            self.df.columns = ['Statistic', 'Value']
            self.tree_view.display_dataframe(self.df)
            self._update_status(f"Applied {agg_func} on {col}")
        except Exception as e:
            self._show_error(f"Error applying aggregation: {str(e)}")

    def on_search(self, text: str) -> None:
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
        try:
            filename, selected_filter = QFileDialog.getSaveFileName(
                self, "Export Data", "", "CSV Files (*.csv);;Excel Files (*.xlsx)"
            )
            if not filename:
                return
            export_df = self.df.copy()
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
        self.df = self.original_df.copy()
        self.search_input.clear()
        self.load_data(self.table_combo.currentText())
        self._update_status("Reset")

    # ─────────────────────────────── Qt charting ───────────────────────────────

    def render_chart(self) -> None:
        """Build and display a Qt chart based on current axis/type selections."""
        x_col = self.x_col_combo.currentText()
        y_col = self.y_col_combo.currentText()
        graph_type = self.graph_type_combo.currentText()

        if not x_col or not y_col:
            self._show_warning("Please select both X and Y columns")
            return

        # Use graph-specific df if available, else fall back to data df
        source_df = getattr(self, 'graph_df', self.original_df)
        if source_df is None or source_df.empty:
            self._show_warning("No data loaded. Select a table first.")
            return

        try:
            # Safe column extraction: avoid duplicate-col DataFrame when x==y
            if x_col == y_col:
                raw = source_df[[x_col]].dropna()
                x_data = raw[x_col].reset_index(drop=True)
                y_data = raw[x_col].reset_index(drop=True)
            else:
                raw = source_df[[x_col, y_col]].dropna()
                # iloc to guarantee Series even if col names collide
                cols = list(raw.columns)
                x_data = raw.iloc[:, cols.index(x_col)].reset_index(drop=True)
                y_data = raw.iloc[:, (len(cols) - 1 - cols[::-1].index(y_col))].reset_index(drop=True)

            if raw.empty:
                self._show_warning("No data available for the selected columns")
                return

            x_is_numeric = pd.api.types.is_numeric_dtype(x_data)
            y_is_numeric = pd.api.types.is_numeric_dtype(y_data)

            # Auto-downgrade to Bar when data is not numeric
            effective_type = graph_type
            if graph_type in ("Line", "Spline", "Area") and (not x_is_numeric or not y_is_numeric):
                effective_type = "Bar"
                self._update_status(
                    f"Non-numeric data detected — switched to Bar chart automatically"
                )

            self.chart.removeAllSeries()
            for ax in self.chart.axes():
                self.chart.removeAxis(ax)

            title = f"{y_col} vs {x_col}  [{effective_type}]"
            self.chart.setTitle(title)
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)
            self.chart.setTitleFont(font)

            if effective_type == "Bar" or not x_is_numeric:
                self._render_bar(x_data, y_data, x_col, y_col, y_is_numeric)
            elif effective_type == "Area":
                self._render_area(x_data, y_data, x_col, y_col)
            elif effective_type == "Spline":
                self._render_spline(x_data, y_data, x_col, y_col)
            else:
                self._render_line(x_data, y_data, x_col, y_col)

            self._switch_to(self._GRAPH_IDX)
            if effective_type == graph_type:
                self._update_status(f"Chart rendered: {graph_type} — {x_col} vs {y_col}")

        except Exception as e:
            logger.error(f"Chart render error: {e}", exc_info=True)
            self._show_chart_error(f"Failed to render chart: {str(e)}")

    def _make_numeric_axes(self, x_label: str, y_label: str):
        """Create and attach numeric axes, return (x_axis, y_axis)."""
        x_axis = QValueAxis()
        x_axis.setTitleText(x_label)
        x_axis.setLabelFormat("%.2f")
        y_axis = QValueAxis()
        y_axis.setTitleText(y_label)
        y_axis.setLabelFormat("%.2f")
        self.chart.addAxis(x_axis, Qt.AlignBottom)
        self.chart.addAxis(y_axis, Qt.AlignLeft)
        return x_axis, y_axis

    # All render helpers now take pre-extracted Series (x_data, y_data)
    def _render_line(self, x_data, y_data, x_col, y_col):
        series = QLineSeries()
        series.setName(y_col)
        for x, y in zip(x_data, y_data):
            series.append(QPointF(float(x), float(y)))
        self.chart.addSeries(series)
        ax, ay = self._make_numeric_axes(x_col, y_col)
        series.attachAxis(ax)
        series.attachAxis(ay)

    def _render_spline(self, x_data, y_data, x_col, y_col):
        series = QSplineSeries()
        series.setName(y_col)
        for x, y in zip(x_data, y_data):
            series.append(QPointF(float(x), float(y)))
        self.chart.addSeries(series)
        ax, ay = self._make_numeric_axes(x_col, y_col)
        series.attachAxis(ax)
        series.attachAxis(ay)

    def _render_area(self, x_data, y_data, x_col, y_col):
        upper = QLineSeries()
        for x, y in zip(x_data, y_data):
            upper.append(QPointF(float(x), float(y)))
        series = QAreaSeries(upper)
        series.setName(y_col)
        self.chart.addSeries(series)
        ax, ay = self._make_numeric_axes(x_col, y_col)
        series.attachAxis(ax)
        series.attachAxis(ay)

    def _render_bar(self, x_data, y_data, x_col, y_col, y_is_numeric):
        """Render a bar chart. x_data/y_data are pandas Series."""
        if y_is_numeric:
            bar_set = QBarSet(y_col)
            categories = [str(v) for v in x_data.tolist()]
            for v in y_data:
                bar_set.append(float(v))
        else:
            # Count value frequencies in x_data
            counts = x_data.value_counts()
            categories = [str(k) for k in counts.index.tolist()]
            bar_set = QBarSet(f"{x_col} (count)")
            for c in counts.values.tolist():
                bar_set.append(float(c))

        series = QBarSeries()
        series.append(bar_set)
        self.chart.addSeries(series)

        x_axis = QBarCategoryAxis()
        x_axis.append(categories)
        x_axis.setTitleText(x_col)
        self.chart.addAxis(x_axis, Qt.AlignBottom)
        series.attachAxis(x_axis)

        y_axis = QValueAxis()
        y_axis.setTitleText(y_col if y_is_numeric else "Count")
        y_axis.setLabelFormat("%.0f")
        self.chart.addAxis(y_axis, Qt.AlignLeft)
        series.attachAxis(y_axis)

    # ────────────────────────────── database ops ───────────────────────────────

    def delete_database(self) -> None:
        reply = QMessageBox.question(
            self, "Confirm Delete", "Delete the database?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(self.db_manager.db_path):
                    os.remove(self.db_manager.db_path)
                    Database()
                    self._update_status("Database deleted")
                    self.reset_view()
                else:
                    self._update_status("No database to delete")
            except Exception as e:
                self._show_error(f"Failed to delete database: {str(e)}")

    # ────────────────────────────── helpers ────────────────────────────────────

    def _update_status(self, message: str) -> None:
        self.status_bar.showMessage(message)

    def _show_warning(self, message: str) -> None:
        QMessageBox.warning(self, "Warning", message)

    def _show_error(self, message: str) -> None:
        """For data-layer errors — also resets the view."""
        QMessageBox.critical(self, "Error", message)
        logger.error(f"Error: {message}", exc_info=True)
        self.reset_view()

    def _show_chart_error(self, message: str) -> None:
        """For chart errors — does NOT reset the data view."""
        QMessageBox.critical(self, "Chart Error", message)
