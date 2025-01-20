import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QLineEdit, QComboBox, QStackedLayout
from PyQt6.QtCore import Qt, pyqtSignal

class TrainAiTab(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_layout = QStackedLayout()

        startTrainAiLayout = QGridLayout()
        newAIModelLayout = QGridLayout()
        aiTrainingInProgressLayout = QGridLayout()
        self.dataAugmentationLayout = QGridLayout()
        self.modelTrainingLayout = QGridLayout()
        self.modelTestingLayout = QGridLayout()


        self.AINameInput = QLineEdit()
        self.AINameInput.setText("New AI")

        self.dataCount = "TODO"

        self.modelSelected = QComboBox()
        self.modelSelected.addItems(["YOLOv5"])
        self.modelSelected.setCurrentIndex(0)

        self.dateSinceLastTrain = "20/01/2025"


        newAIModelLayout.addWidget(QLabel("Name:"), 0, 0)
        newAIModelLayout.addWidget(self.AINameInput, 0, 1)

        newAIModelLayout.addWidget(QLabel("Image Count:"), 1, 0)
        newAIModelLayout.addWidget(QLabel(self.dataCount), 1, 1)

        newAIModelLayout.addWidget(QLabel("Model Selected:"), 2, 0)
        newAIModelLayout.addWidget(self.modelSelected, 2, 1) 
        
        newAIModelLayout.addWidget(QLabel("Model Selected:"), 2, 0)
        newAIModelLayout.addWidget(self.modelSelected, 2, 1) 
        
        newAIModelLayout.addWidget(QLabel("Previous Model Training Date:"), 3, 0)
        newAIModelLayout.addWidget(QLabel(self.dateSinceLastTrain), 3, 1)

        #Init main layout
        startTrainAiLayout.addWidget(QLabel("Train New AI"), 0, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)

        startTrainAiLayout.addLayout(newAIModelLayout, 1, 0, newAIModelLayout.rowCount(), 2)

        trainFromScratchButton = QPushButton("Train from scratch")
        trainFromScratchButton.pressed.connect(self.startAiTrain)
        startTrainAiLayout.addWidget(trainFromScratchButton, newAIModelLayout.rowCount()+1, 0)

        trainModelFromLastModel = QPushButton("Train from last model")
        startTrainAiLayout.addWidget(trainModelFromLastModel, newAIModelLayout.rowCount()+1, 1)

        startTrainAiWidget = QWidget()
        startTrainAiWidget.setLayout(startTrainAiLayout)
        self.stacked_layout.addWidget(startTrainAiWidget)

        #AI In Training Layout

        aiTrainingInProgressLayout.addWidget(QLabel(self.AINameInput.text()), 0, 1, 1, 3, Qt.AlignmentFlag.AlignCenter)
        aiTrainingInProgressLayout.setSpacing(20)

        #Data Augmentation Layout
        self.dataAugmentationLayout.addWidget(QLabel("Data Augmentation Stage"), 0, 0,  Qt.AlignmentFlag.AlignCenter)
        temp1 = QWidget()
        temp1.setLayout(self.dataAugmentationLayout)
        temp1.setStyleSheet(
                """
                border: 2px solid #555;
                border-radius: 5px;
                """
            )
        
        aiTrainingInProgressLayout.addWidget(temp1, 1, 0)

        #Training Layout
        self.modelTrainingLayout.addWidget(QLabel("Training Stage"), 0, 0,  Qt.AlignmentFlag.AlignCenter)
        temp2 = QWidget()
        temp2.setLayout(self.modelTrainingLayout)
        temp2.setStyleSheet(
                """
                border: 2px solid #555;
                border-radius: 5px;
                """
            )
        aiTrainingInProgressLayout.addWidget(temp2, 1, 1)

        #Testing Layout
        self.modelTestingLayout.addWidget(QLabel("Testing Stage"), 0, 0,  Qt.AlignmentFlag.AlignCenter)
        temp3 = QWidget()
        temp3.setLayout(self.modelTestingLayout)
        temp3.setStyleSheet(
                """
                border: 2px solid #555;
                border-radius: 5px;
                """
            )

        aiTrainingInProgressLayout.addWidget(temp3, 1, 2)

        aiTrainingInProgressLayout.setColumnStretch(1, 1)
        aiTrainingInProgressLayout.setColumnStretch(2, 1)
        aiTrainingInProgressLayout.setColumnStretch(3, 1)

        aiTrainingInProgressWidget = QWidget()
        aiTrainingInProgressWidget.setLayout(aiTrainingInProgressLayout)



        self.stacked_layout.addWidget(aiTrainingInProgressWidget)

        self.setLayout(self.stacked_layout)
        self.stacked_layout.setCurrentIndex(0)

    def startAiTrain(self):
        self.stacked_layout.setCurrentIndex(1)
