import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class AnalyseImageTab(QWidget):    
    def __init__(self):
        super().__init__()
        layout = QGridLayout()

        layout.addWidget(QLabel("Select Image of X-Ray"), 0, 0)
        selectedImageButton = QPushButton("Analyse")
        layout.addWidget(selectedImageButton, 0, 1)


        layout.addWidget(QLabel("Select AI Model"), 1, 0)
        selectAIModelButton = QPushButton("Select AI")
        layout.addWidget(selectAIModelButton, 1, 1)


        analyseImageButton = QPushButton("Analyse")
        layout.addWidget(analyseImageButton, 2, 0, 1, 2)

        self.setLayout(layout)
