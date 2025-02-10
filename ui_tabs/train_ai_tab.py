import sys
from PySide6.QtWidgets import (QApplication, QTabWidget, QWidget, QVBoxLayout, 
                               QLabel, QGridLayout, QPushButton, QLineEdit, QComboBox, 
                               QStackedLayout, QFrame, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, Signal, Slot, QThread

from stages.main_train_pipeline import MainTrainPipeline

class TrainAiTab(QWidget):
    def __init__(self):
        super().__init__()
        self.mainLayout = QGridLayout()
        
        #Adds button to be able to switch to previous view when training is in progress
        
        switch_view_layout = QGridLayout()
        
        self.controlViewPushButton = QPushButton()
        self.controlViewPushButton.setText("Switch View")
        self.controlViewPushButton.pressed.connect(self.switch_views)

        self.trainInProgress = False
        switch_view_layout.addWidget(QLabel("Start Train Ai View"), 0, 0)
        switch_view_layout.addWidget(self.controlViewPushButton, 0, 1)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        switch_view_layout.addWidget(separator, 1, 0, 1, 2)  # Span across both columns
        
        self.switch_view_widget = QWidget()
        self.switch_view_widget.setLayout(switch_view_layout)
        
        self.mainLayout.addWidget(self.switch_view_widget, 0, 0, 2, 2)
        self.switch_view_widget.setHidden(True)
        ##
        
        self.stacked_layout = QStackedLayout()
        self.mainLayout.addLayout(self.stacked_layout, 2, 0, 1, 2)

        #default values
        self.dataCount = "TODO"
        self.dateSinceLastTrain = "20/01/2025"

        self.stacked_layout.addWidget(self.create_start_train_ai_gui())
        self.stacked_layout.addWidget(self.create_ai_train_gui())

        self.setLayout(self.mainLayout)
        self.stacked_layout.setCurrentIndex(0)

    def create_start_train_ai_gui(self) -> QWidget:
        self.modelSelected = QComboBox()
        self.modelSelected.addItems(["YOLOv5"])
        self.modelSelected.setCurrentIndex(0)
        self.AINameInput = QLineEdit()
        self.AINameInput.setText("New AI")

        newAIModelLayout = QGridLayout()
        startTrainAiLayout = QGridLayout()

        newAIModelLayout.addWidget(QLabel("Name:"), 0, 0)
        newAIModelLayout.addWidget(self.AINameInput, 0, 1)

        newAIModelLayout.addWidget(QLabel("Image Count:"), 1, 0)
        newAIModelLayout.addWidget(QLabel(self.dataCount), 1, 1)
        
        newAIModelLayout.addWidget(QLabel("Model Architecture Selected:"), 2, 0)
        newAIModelLayout.addWidget(self.modelSelected, 2, 1) 
        
        newAIModelLayout.addWidget(QLabel("Previous Model Training Date:"), 3, 0)
        newAIModelLayout.addWidget(QLabel(self.dateSinceLastTrain), 3, 1)

        #Init main layout
        startTrainAiLayout.addWidget(QLabel("Train New AI"), 0, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)

        startTrainAiLayout.addLayout(newAIModelLayout, 1, 0, newAIModelLayout.rowCount(), 2)

        startTrainingButtonsLayout = QGridLayout()
        
        trainFromScratchButton = QPushButton("Train from scratch")
        trainFromScratchButton.pressed.connect(self.start_ai_train)
        startTrainingButtonsLayout.addWidget(trainFromScratchButton, 0, 0)

        trainModelFromLastModel = QPushButton("Train from last model")
        startTrainingButtonsLayout.addWidget(trainModelFromLastModel, 0, 1)

        self.startTrainingButtonsWidget = QWidget()
        self.startTrainingButtonsWidget.setLayout(startTrainingButtonsLayout)
        startTrainAiLayout.addWidget(self.startTrainingButtonsWidget, newAIModelLayout.rowCount()+1, 0, 1, 2)

        self.cancelButton = QPushButton("Cancel Training")
        self.cancelButton.pressed.connect(self.confirm_cancel_training)
        self.cancelButton.setHidden(True)
        startTrainAiLayout.addWidget(self.cancelButton, newAIModelLayout.rowCount()+1, 0, 1, 2)
        
        startTrainAiWidget = QWidget()
        startTrainAiWidget.setLayout(startTrainAiLayout)
        return startTrainAiWidget

    def create_ai_train_gui(self):
        dataAugmentationLayout = QGridLayout()
        modelTrainingLayout = QGridLayout()
        modelTestingLayout = QGridLayout()
        aiTrainingInProgressLayout = QGridLayout()
        #AI In Training Layout

        self.AINameInputInProgress = QLabel(self.AINameInput.text())
        aiTrainingInProgressLayout.addWidget(self.AINameInputInProgress, 0, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        aiTrainingInProgressLayout.setSpacing(20)

        #Data Augmentation Layout
        dataAugmentationColumn = QFrame()
        dataAugmentationColumn.setFrameShape(QFrame.Box)
        dataAugmentationColumn.setLineWidth(1)
        dataAugmentationColumn.setMinimumWidth(200)

        layout = QVBoxLayout()
        label = QLabel("Data Augmentation Stage")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        self.modelTrainingTextBox = QLabel("No Update")
        layout.addWidget(self.modelTrainingTextBox,  Qt.AlignmentFlag.AlignCenter)
        
        self.dataAugmentationProgressBar = QProgressBar()
        self.dataAugmentationProgressBar.setValue(100)
        layout.addWidget(self.dataAugmentationProgressBar, Qt.AlignmentFlag.AlignBottom)
        
        dataAugmentationColumn.setLayout(layout)
        aiTrainingInProgressLayout.addWidget(dataAugmentationColumn, 1, 0)

        #Training Layout
        trainingStageColumn = QFrame()
        trainingStageColumn.setFrameShape(QFrame.Box)
        trainingStageColumn.setLineWidth(1)
        trainingStageColumn.setMinimumWidth(200)

        layout = QVBoxLayout()
        label = QLabel("Training Stage")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        self.modelTrainingTextBox = QLabel("No Update")
        layout.addWidget(self.modelTrainingTextBox,  Qt.AlignmentFlag.AlignCenter)
        
        self.trainingProgressBar = QProgressBar()
        self.trainingProgressBar.setValue(50)
        layout.addWidget(self.trainingProgressBar, Qt.AlignmentFlag.AlignBottom)
        
        trainingStageColumn.setLayout(layout)
        aiTrainingInProgressLayout.addWidget(trainingStageColumn, 1, 1)


        #Testing Layout
        testingStageColumn = QFrame()
        testingStageColumn.setFrameShape(QFrame.Box)
        testingStageColumn.setLineWidth(1)
        testingStageColumn.setMinimumWidth(200)

        layout = QVBoxLayout()
        label = QLabel("Testing Stage")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        self.testingStageTextBox = QLabel("No Update")
        layout.addWidget(self.testingStageTextBox,  Qt.AlignmentFlag.AlignCenter)
        
        self.testingProgressBar = QProgressBar()
        self.testingProgressBar.setValue(0)
        layout.addWidget(self.testingProgressBar, Qt.AlignmentFlag.AlignBottom)
        
        testingStageColumn.setLayout(layout)
        aiTrainingInProgressLayout.addWidget(testingStageColumn, 1, 2)

        aiTrainingInProgressLayout.setColumnStretch(1, 1)
        aiTrainingInProgressLayout.setColumnStretch(2, 1)
        aiTrainingInProgressLayout.setColumnStretch(3, 1)
        aiTrainingInProgressWidget = QWidget()
        aiTrainingInProgressWidget.setLayout(aiTrainingInProgressLayout)

        return aiTrainingInProgressWidget

    def switch_views(self):
        if(self.trainInProgress):
            if(self.stacked_layout.currentIndex() == 0):
                self.stacked_layout.setCurrentIndex(1)
            else:
                self.stacked_layout.setCurrentIndex(0)
                

    def start_ai_train(self):
        self.AINameInputInProgress.setText(self.AINameInput.text())
        self.trainInProgress = True
        self.stacked_layout.setCurrentIndex(1)
        self.switch_view_widget.setHidden(False)
        self.startTrainingButtonsWidget.setHidden(True)
        self.cancelButton.setHidden(False)
        #self.pipeline = MainTrainPipeline(self)
        #self.pipeline.run()

    def confirm_cancel_training(self):
        confirmMessageBox = QMessageBox()
        confirmMessageBox.setIcon(QMessageBox.Warning)
        confirmMessageBox.setWindowTitle("Cancel Confirmation")
        confirmMessageBox.setText("Are you sure you want to cancel?")
        confirmMessageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = confirmMessageBox.exec()
        
        if(result == QMessageBox.Yes):
            self.cancel_training()
            
    def cancel_training(self):
        print("TODO: Cancel Logic")
        
        self.trainInProgress = False
        self.cancelButton.setVisible(False)
        self.switch_view_widget.setVisible(False)
        self.stacked_layout.setCurrentIndex(0)
        self.startTrainingButtonsWidget.setVisible(True)

    @Slot(str)
    def update_a_str_field(self, message):
        print("here")
        self.modelTrainingTextBox.setText(message)

    @Slot(int)
    def update_a_int_field(self, value):
        print(value)
        
