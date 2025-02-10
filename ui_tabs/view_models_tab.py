import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

class ViewModelsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("View Models"))
        layout.addWidget(QLabel(""))
        self.setLayout(layout)
