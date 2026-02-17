
from PySide6.QtWidgets import (QPushButton, QLabel, QLineEdit, QTextEdit, 
                              QComboBox, QCheckBox, QRadioButton, QSlider,
                              QProgressBar, QListWidget, QGroupBox , QAbstractItemView , QDateEdit)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon ,  QColor, QFont
from controller.path_manager import path_manager

class StyleUtils:

    # Color palette constants
    PRIMARY_COLOR = "#4CAF50"  # Green
    SECONDARY_COLOR = "#2196F3"  # Blue
    DANGER_COLOR = "#F44336"  # Red
    WARNING_COLOR = "#FF9800"  # Orange
    DARK_COLOR = "#333333"
    LIGHT_COLOR = "#F5F5F5"
    TEXT_COLOR = "#212121"
    DISABLED_COLOR = "#9E9E9E"

    @staticmethod
    def style_groupbox(groupbox: QGroupBox) -> None:
        groupbox.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding: 3px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0px 3px;
            }
        """)

    @staticmethod
    def style_list_widget(listwidget: QListWidget) -> None:
        listwidget.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;
                font-size: 16px;
                border: none;
            }
            QListWidget::item {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #ffffff;
                padding: 5px;
                color: #333333;
                font-family: Arial, sans-serif;
                font-weight: bold;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
            }
            QListWidget::item:nth-child(even) {
                background-color: #f8f8f8;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #f0f0f0;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
            }
        """)
        listwidget.setItemAlignment(Qt.AlignCenter)
        # listwidget.setFixedSize(300, 200)
        listwidget.setSpacing(3)
        listwidget.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        # listwidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    @staticmethod
    def style_secondary_button(button: QPushButton) -> None:
        button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                color: #333333;
                padding: 8px 16px;
                text-align: center;
                font-size: 14px;
                border-radius: 4px;
                margin: 4px 2px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #aaaaaa;
            }
        """)

    @staticmethod
    def style_danger_button(button: QPushButton) -> None:
        button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;  /* Red */
                border: none;
                color: white;
                padding: 10px 24px;
                text-align: center;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 4px 2px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #ffcdd2;
                color: #666666;
            }
        """)

    @staticmethod
    def style_icon_button(button: QPushButton ,icon : QIcon, icon_size=14) -> None:
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.2);
            }
        """)
        button.setIcon(icon)
        button.setIconSize(QSize(icon_size, icon_size))

    @staticmethod
    def style_primary_button(button: QPushButton, icon: QIcon = None , icon_size = 16) -> None:
        """
        Styles a primary action button (green theme)
        
        Args:
            button: QPushButton instance to style
            icon: Optional icon to add (default: None)
        """
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleUtils.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 4px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #43A047;
            }}
            QPushButton:pressed {{
                background-color: #2E7D32;
            }}
            QPushButton:disabled {{
                background-color: #C8E6C9;
                color: {StyleUtils.DISABLED_COLOR};
            }}
        """)
        if icon:
            button.setIcon(icon)
            button.setIconSize(QSize(icon_size, icon_size))

    @staticmethod
    def style_text_input(input_field: QLineEdit) -> None:
        """
        Styles a text input field with modern appearance
        
        Args:
            input_field: QLineEdit or QTextEdit instance
        """
        input_field.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                background: white;
                selection-background-color: {StyleUtils.SECONDARY_COLOR};
                color: crimson;
                font-weight: bold;
            }}
            QLineEdit:focus {{
                border: 2px solid {StyleUtils.SECONDARY_COLOR};
            }}
            QLineEdit:disabled {{
                background: #EEEEEE;
                color: {StyleUtils.DISABLED_COLOR};
            }}
        """)

    @staticmethod
    def style_dark_card(container: QGroupBox) -> None:
        """
        Styles a container with dark theme (for cards/sections)
        
        Args:
            container: QGroupBox or QFrame instance
        """
        container.setStyleSheet(f"""
            QGroupBox {{
                background-color: {StyleUtils.DARK_COLOR};
                border-radius: 8px;
                padding: 16px;
                color: white;
                font-size: 16px;
                border: none;
            }}
            QGroupBox::title {{
                color: white;
                subcontrol-origin: margin;
                left: 8px;
            }}
        """)

    @staticmethod
    def style_modern_slider(slider: QSlider) -> None:
        """
        Styles a QSlider with modern touch-friendly appearance
        
        Args:
            slider: QSlider instance (works for both horizontal/vertical)
        """
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 6px;
                background: #E0E0E0;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                width: 16px;
                height: 16px;
                margin: -6px 0;
                background: {StyleUtils.PRIMARY_COLOR};
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {StyleUtils.PRIMARY_COLOR};
                border-radius: 3px;
            }}
        """)

    @staticmethod
    def style_toggle_switch(toggle: QCheckBox) -> None:
        """
        Styles a checkbox as a modern toggle switch
        
        Args:
            toggle: QCheckBox instance to style as toggle
        """
        toggle.setStyleSheet(f"""
            QCheckBox {{
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 48px;
                height: 24px;
                border-radius: 12px;
                border: 1px solid #BDBDBD;
            }}
            QCheckBox::indicator:unchecked {{
                background: #E0E0E0;
            }}
            QCheckBox::indicator:checked {{
                background: {StyleUtils.PRIMARY_COLOR};
                border: 1px solid {StyleUtils.PRIMARY_COLOR};
            }}
            QCheckBox::indicator:unchecked:hover {{
                background: #D5D5D5;
            }}
            QCheckBox::indicator:checked:hover {{
                background: #43A047;
            }}
        """)

    @staticmethod
    def style_progress_bar(progress_bar: QProgressBar) -> None:
        """
        Styles a progress bar with modern gradient appearance
        
        Args:
            progress_bar: QProgressBar instance
        """
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                text-align: center;
                background: #F5F5F5;
                height: 16px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {StyleUtils.PRIMARY_COLOR}, 
                    stop:1 {StyleUtils.SECONDARY_COLOR}
                );
                border-radius: 3px;
            }}
        """)

    @staticmethod
    def style_lable(label: QLabel) -> None:
        """
        Styles a label with subtle shadow
        
        Args:
            label: QLabel instance to style 
        """
        label.setStyleSheet("""
            QLabel {
                background-color: cyan;
                color: crimson;
                border: 1px solid #BDBDBD;
                border-radius: 15px;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
                font-size: 16px;
            }
        """)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setMargin(4)

    @staticmethod
    def style_badge(label: QLabel, color: str = PRIMARY_COLOR) -> None:
        """
        Styles a label as a circular/rounded badge
        
        Args:
            label: QLabel instance
            color: Background color (default: primary color)
        """
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border: 1px solid #BDBDBD;
                border-radius: 10px;
                margin: 2px;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
                min-width: 20px;
                qproperty-alignment: AlignCenter;
            }}
        """)

    @staticmethod
    def style_rich_text_editor(text_edit: QTextEdit) -> None:
        """
        Styles a QTextEdit as a modern rich text editor with:
        - Custom scrollbars
        - Focus highlighting
        - Placeholder text styling
        - Code block friendly font
        
        Args:
            text_edit: QTextEdit instance to style
        """
        text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: white;
                border: 1px solid #BDBDBD;
                border-radius: 6px;
                padding: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: {StyleUtils.TEXT_COLOR};
                selection-background-color: {StyleUtils.SECONDARY_COLOR};
                selection-color: white;
            }}
            QTextEdit:focus {{
                border: 2px solid {StyleUtils.SECONDARY_COLOR};
                padding: 11px; /* Adjust for thicker border */
            }}
            QTextEdit:disabled {{
                background-color: #FAFAFA;
                color: #9E9E9E;
            }}
            
            /* Scrollbar styling */
            QScrollBar:vertical {{
                width: 10px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: #C0C0C0;
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
        # Set placeholder text color (requires Qt 5.15+)
        text_edit.setProperty("placeholderTextColor", "#9E9E9E")
        
        # Set tab stop width (4 spaces equivalent)
        text_edit.setTabStopDistance(32) 

    @staticmethod
    def style_dropdown(combo: QComboBox, editable: bool = False) -> None:
        """
        Styles a QComboBox with modern dropdown appearance
        
        Args:
            combo: QComboBox instance to style
            editable: Whether the combo box is editable (default: False)
        """
        base_style = f"""
            QComboBox {{
                background-color: black;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 8px;
                padding-right: 24px; /* Space for arrow */
                font-size: 14px;
                min-width: 120px;
            }}
            QComboBox:hover {{
                border-color: #9E9E9E;
            }}
            QComboBox:focus {{
                border: 2px solid {StyleUtils.SECONDARY_COLOR};
                padding: 7px 23px 7px 7px; /* Adjust for thicker border */
            }}
            QComboBox:disabled {{
                background-color: #EEEEEE;
                color: {StyleUtils.DISABLED_COLOR};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #E0E0E0;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }}
            QComboBox::down-arrow {{
                image: url({path_manager.get_icon_path('down1.png')});
                width: 24px;
                height: 24px;
            }}
        """
        
        if editable:
            editable_style = """
                QComboBox QAbstractItemView {
                    border: 1px solid #BDBDBD;
                    background: white;
                    selection-background-color: %s;
                    selection-color: white;
                    color: black;
                }
                QComboBox::editable {
                    background: white;
                    color: black;
                }
            """ % StyleUtils.SECONDARY_COLOR
            combo.setStyleSheet(base_style + editable_style)
        else:
            combo.setStyleSheet(base_style)
        
        # Additional non-CSS settings
        combo.setMinimumHeight(36)
        combo.view().setMinimumWidth(combo.minimumSizeHint().width())
        
        # For editable comboboxes
        if editable:
            combo.setEditable(True)
            line_edit = combo.lineEdit()
            line_edit.setStyleSheet("""
                QLineEdit {
                    padding: 0;
                    border: none;
                    background: transparent;
                }
            """)

    @staticmethod
    def style_pill_dropdown(combo: QComboBox) -> None:
        """
        Styles a QComboBox as a modern "pill" shaped dropdown
        (Rounded ends, compact appearance)
        
        Args:
            combo: QComboBox instance to style
        """
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {StyleUtils.LIGHT_COLOR};
                border: none;
                border-radius: 16px;
                padding: 6px 16px;
                padding-right: 32px;
                font-size: 13px;
                min-width: 80px;
                color:black;
            }}
            QComboBox:hover {{
                background-color: #E0E0E0;
            }}
            QComboBox::drop-down {{
                width: 24px;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                border: none;
                border-radius: 8px;
                padding: 4px;
                background: white;
                color: black;
            }}
            QComboBox QAbstractItemView::item {{
                height: 28px;
                padding: 0 8px;
                border-radius: 4px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: black;
                color: white;
            }}
        """)
        combo.setMinimumHeight(32)

    
    @staticmethod
    def get_theme_color(theme, element):
        """
        Get color for a specific UI element based on theme
        
        Args:
            theme: Theme name
            element: UI element ('background', 'text', 'selection', etc.)
        
        Returns:
            Hex color code as string
        """
        themes = {
            "default": {
                "background": "#ffffff",
                "alternate": "#f5f5f5",
                "text": "#333333",
                "text_selected": "#ffffff",
                "selection": "#3daee9",
                "hover": "#e0e0e0",
                "grid": "#e0e0e0",
                "border": "#cccccc",
                "header": "#f8f8f8",
                "header_border": "#e0e0e0"
            },
            "dark": {
                "background": "#2d2d2d",
                "alternate": "#353535",
                "text": "#e0e0e0",
                "text_selected": "#ffffff",
                "selection": "#3daee9",
                "hover": "#454545",
                "grid": "#404040",
                "border": "#252525",
                "header": "#353535",
                "header_border": "#404040"
            },
            "light": {
                "background": "#f9f9f9",
                "alternate": "#f0f0f0",
                "text": "#333333",
                "text_selected": "#ffffff",
                "selection": "#4a90e2",
                "hover": "#e8e8e8",
                "grid": "#e0e0e0",
                "border": "#d0d0d0",
                "header": "#f0f0f0",
                "header_border": "#d0d0d0"
            },
            "modern": {
                "background": "#ffffff",
                "alternate": "#f8fafc",
                "text": "#334155",
                "text_selected": "#ffffff",
                "selection": "#6366f1",  # Indigo
                "hover": "#f1f5f9",
                "grid": "#e2e8f0",
                "border": "#e2e8f0",
                "header": "#f8fafc",
                "header_border": "#e2e8f0"
            },
            "hover_text": {
                "background": "#ffffff",
                'color': "#000000"
            },
        }
        
        return themes.get(theme, themes["default"]).get(element, "#ffffff")

    @staticmethod
    def set_column_colors(tree_view, column_colors):
        """
        Set specific background colors for columns
        
        Args:
            tree_view: QTreeView widget
            column_colors: Dictionary of {column_index: color}
        """
        style = tree_view.styleSheet()
        
        for col, color in column_colors.items():
            style += f"""
            QTreeView::item:nth-child({col}) {{
                background-color: {color};
            }}
            """
        
        tree_view.setStyleSheet(style)

    @staticmethod
    def highlight_priority_items(tree_view, priority_column=2):
        """
        Apply color coding based on priority values
        
        Args:
            tree_view: QTreeView widget
            priority_column: Column index containing priority values
        """
        style = tree_view.styleSheet()
        
        style += f"""
        QTreeView::item[priority="High"] {{
            color: #e53e3e;
            font-weight: bold;
        }}
        QTreeView::item[priority="Medium"] {{
            color: #dd6b20;
        }}
        QTreeView::item[priority="Low"] {{
            color: #38a169;
        }}
        """
        
        tree_view.setStyleSheet(style)

    @staticmethod
    def apply_tree_style(tree_view, theme="default"):
        """
        Apply a complete style to a QTreeView
        
        Args:
            tree_view: The QTreeView widget to style
            theme: Style theme ('default', 'dark', 'light', 'modern')
        """
        # Base style that applies to all themes
        base_style = f"""
        QTreeView {{
            background-color: {StyleUtils.get_theme_color(theme, 'background')};
            alternate-background-color: {StyleUtils.get_theme_color(theme, 'alternate')};
            border: 1px solid {StyleUtils.get_theme_color(theme, 'border')};
            border-radius: 4px;
            outline: 0;  /* Remove focus border */
        }}
        
        QTreeView::item {{
            padding: 6px 1px;
            border-bottom: 1px solid {StyleUtils.get_theme_color(theme, 'grid')};
        }}
        

        
        QTreeView::item:selected {{
            background-color: {StyleUtils.get_theme_color(theme, 'selection')};
            color: {StyleUtils.get_theme_color(theme, 'text_selected')};
        }}
        
        QHeaderView::section {{
            background-color: {StyleUtils.get_theme_color(theme, 'header')};
            padding: 6px;
            border: none;
            border-bottom: 2px solid {StyleUtils.get_theme_color(theme, 'header_border')};
        }}
        """
        
        # Additional theme-specific tweaks
        if theme == "dark":
            base_style += """
            QTreeView::branch {
                background: palette(dark);
            }
            """
        elif theme == "modern":
            base_style += """
            QHeaderView::section {
                font-weight: bold;
                font-size: 12px;
            }
            """
        
        tree_view.setStyleSheet(base_style)
        
        # Apply font settings
        font = QFont()
        font.setFamily("Segoe UI" if theme == "modern" else "Arial")
        font.setPointSize(10 if theme == "compact" else 11)
        tree_view.setFont(font)
        
        # Configure visual behavior
        tree_view.setAlternatingRowColors(True)
        tree_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        tree_view.setSelectionMode(QAbstractItemView.SingleSelection)
        tree_view.setFocusPolicy(Qt.NoFocus)
        
        # Header styling
        header = tree_view.header()
        header.setDefaultAlignment(Qt.AlignLeft)
        header.setStretchLastSection(False)
        
        if theme == "modern":
            header.setStyleSheet("""
            QHeaderView::section {
                padding-left: 15px;
            }
            """)

    def style_date_edit(date_edit: QDateEdit) -> None:
        date_edit.setStyleSheet("""
            QDateEdit {
                border: 2px solid crimson;
                border-radius: 10px;
                padding: 4px 6px;
                background-color: white;
                color : black;
                selection-background-color: #0078d7;
                selection-color: blue;
            }
            QDateEdit::drop-down {
                color: black;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #ccc;
            }
            QDateEdit::down-arrow {{
                image: url({path_manager.get_icon_path('calendar.png')});
                color: black;
                width: 24px;
                height: 24px;
            }}
            QDateEdit:disabled {
                background-color: black;
                color: white;
                                }
        """)

