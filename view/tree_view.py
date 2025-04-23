from PySide6.QtWidgets import QTreeView, QAbstractItemView, QHeaderView , QLabel ,QGroupBox , QVBoxLayout
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import Qt

def create_task_tree():
    """Create a configured task tree view"""
    
    tree = QTreeView()

    tree.setModel(QStandardItemModel(0, 7, tree))
    tree.model().setHorizontalHeaderLabels(['Title', 'Category', 'Priority', 'Status','','' ,''])

    # Tree configuration
    tree.setSelectionBehavior(QAbstractItemView.SelectRows)
    tree.setSelectionMode(QAbstractItemView.SingleSelection)
    tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tree.setAlternatingRowColors(True)
    tree.setSortingEnabled(True)
    tree.setAnimated(True)
    tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    tree.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    # Header configuration
    header = tree.header()
    header.setSectionResizeMode(0, QHeaderView.Stretch)  # Title column stretches
    header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
    header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
    header.setSectionsClickable(True) 
    return tree
