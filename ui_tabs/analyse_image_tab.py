from pathlib import Path
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QFileDialog, QMessageBox, QStackedLayout
from ultralytics import YOLO

from ui_tabs.select_ai_page import SelectAiPage
from ui_tabs.view_results_page import ViewResultsPage


class AnalyseImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selectedImage = ""
        self.selectedAIModelPath = ""
        self.selectAIModelName = ""

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

        self.stacked_layout = QStackedLayout()
        widget_layout = QWidget()
        widget_layout.setLayout(layout)
        self.stacked_layout.addWidget(widget_layout)

        self.setLayout(self.stacked_layout)
        self.stacked_layout.setCurrentIndex(0)

    def update_selected_model(self):
        # result = self.browse_file(os.path.abspath("trained_models/"), "PyTorch File (*.pt)")
        # if result != "" and result.endswith(".pt"):
        #     self.selectedAIModel = result
        #     self.selectedModelLabel.setText("..." + self.selectedAIModel[-20:])

        self.select_ai_widget = SelectAiPage()
        self.select_ai_widget.model_selected.connect(self.model_selected)
        self.select_ai_widget.switch_view.connect(self.reset_view)
        self.stacked_layout.addWidget(self.select_ai_widget)
        self.stacked_layout.setCurrentWidget(self.select_ai_widget)

    def model_selected(self, name, path):
        self.selectedAIModelPath = path
        self.selectedModelLabel.setText(name)
        self.reset_view()

    def update_selected_image(self):
        result = self.browse_file("", "Images (*.png *.jpg)")
        if result != "" and (result.endswith(".png") or result.endswith(".jpg")):
            self.selectedImage = result
            self.selectedImageLabel.setText("..." + self.selectedImage[-20:])

    def browse_file(self, opendir, fileConstraints):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File", opendir, fileConstraints)
        if file_path:
            return file_path
        else:
            return ""

    def start_image_analysis(self):
        if (self.selectedAIModelPath == "" or Path(self.selectedAIModelPath).suffix != ".pt"):
            errorMessage = QMessageBox()
            errorMessage.setIcon(QMessageBox.Critical)
            errorMessage.setWindowTitle("Error")
            errorMessage.setText("Please select a valid AI model.")
            errorMessage.exec()
            return

        elif (self.selectedImage == "" or Path(self.selectedImage).suffix not in {".png", ".jpg"}):
            errorMessage = QMessageBox()
            errorMessage.setIcon(QMessageBox.Critical)
            errorMessage.setWindowTitle("Error")
            errorMessage.setText("Please select a valid image to analyse.")
            errorMessage.exec()
            return

        model = YOLO(self.selectedAIModelPath)
        results = model(self.selectedImage)

        self.results_widget = ViewResultsPage(self.selectedImage, results)
        self.results_widget.switch_view.connect(self.reset_view)
        self.stacked_layout.addWidget(self.results_widget)
        self.stacked_layout.setCurrentWidget(self.results_widget)

    def reset_view(self):
        self.stacked_layout.setCurrentIndex(0)

        if hasattr(self, 'results_widget'):
            self.stacked_layout.removeWidget(self.results_widget)
            # self.results_widget.deleteLater()

        elif hasattr(self, 'select_ai_widget'):
            self.stacked_layout.removeWidget(self.select_ai_widget)
            # self.select_ai_widget.deleteLater()
