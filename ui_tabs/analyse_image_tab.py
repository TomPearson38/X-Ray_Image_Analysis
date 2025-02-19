import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QFileDialog, QMessageBox
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
import cv2
from ultralytics import YOLO

class AnalyseImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selectedImage = ""
        self.selectedAIModel = ""

        layout = QGridLayout()

        layout.addWidget(QLabel("Select Image of X-Ray"), 0, 0)
        self.selectedImageLabel = QLabel("")
        layout.addWidget(self.selectedImageLabel, 0, 1)
        selectedImageButton = QPushButton("Browse...")
        layout.addWidget(selectedImageButton, 0, 2)
        selectedImageButton.clicked.connect(self.update_selected_image)


        layout.addWidget(QLabel("Select AI Model"), 1, 0)
        selectAIModelButton = QPushButton("Select AI")
        self.selectedModelLabel = QLabel("")
        layout.addWidget(self.selectedModelLabel, 1, 1)
        layout.addWidget(selectAIModelButton, 1, 2)
        selectAIModelButton.clicked.connect(self.update_selected_model)

        analyseImageButton = QPushButton("Analyse")
        layout.addWidget(analyseImageButton, 2, 0, 1, 3)
        analyseImageButton.clicked.connect(self.start_image_analysis)

        self.setLayout(layout)

    def update_selected_model(self):
        result = self.browse_file(os.path.abspath("trained_models/"), "PyTorch File (*.pt)")
        if result != "":
            self.selectedAIModel = result
            self.selectedModelLabel.setText("..." + self.selectedAIModel[-20:])

    def update_selected_image(self):
        result = self.browse_file("", "Images (*.png *.jpg)")
        if result != "":
            self.selectedImage = result
            self.selectedImageLabel.setText("..." + self.selectedImage[-20:])

    def browse_file(self, opendir, fileConstraints):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File", opendir, fileConstraints)
        if file_path:
            return file_path
        else:
            return ""
        
    def start_image_analysis(self):
        if(self.selectedAIModel == "" or Path(self.selectedAIModel).suffix != ".pt"):
            errorMessage = QMessageBox()
            errorMessage.setIcon(QMessageBox.Critical)
            errorMessage.setWindowTitle("Error")
            errorMessage.setText("Please select a valid AI model.")
            errorMessage.exec()
            return

        elif(self.selectedImage == "" or Path(self.selectedImage).suffix not in {".png", ".jpg"}):
            errorMessage = QMessageBox()
            errorMessage.setIcon(QMessageBox.Critical)
            errorMessage.setWindowTitle("Error")
            errorMessage.setText("Please select a valid image to analyse.")
            errorMessage.exec()
            return
        
        model = YOLO(self.selectedAIModel)
        results = model(self.selectedImage)

        image = results[0].plot() 

        # Convert OpenCV image (BGR) to QImage (RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(q_img)
        self.selectedImageLabel.setPixmap(pixmap)
        self.selectedImageLabel.setScaledContents(True) 
