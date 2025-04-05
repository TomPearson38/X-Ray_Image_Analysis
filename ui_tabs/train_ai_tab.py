import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout,
                               QLabel, QGridLayout, QPushButton, QLineEdit, QComboBox,
                               QStackedLayout, QFrame, QMessageBox, QProgressBar, QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from data_classes.model_info import ModelInfo
from stages.main_train_pipeline import MainTrainPipeline
from helpers import file_helpers
import os

from ui_tabs.select_ai_page import SelectAiPage


class TrainAiTab(QWidget):
    def __init__(self):
        super().__init__()
        self.mainLayout = QGridLayout()

        # Adds button to be able to switch to previous view when training is in progress
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

        self.stacked_layout = QStackedLayout()
        self.mainLayout.addLayout(self.stacked_layout, 2, 0, 1, 2)

        # default values
        data_dir = os.path.abspath("stored_training_images")
        self.dataset_config_dir = os.path.join(data_dir, "datasets")
        self.image_dir = os.path.join(data_dir, "images", "raw")
        self.image_count = "0"
        self.selected_starting_model = ""

        self.stacked_layout.addWidget(self.create_start_train_ai_gui())
        self.stacked_layout.addWidget(self.create_ai_train_gui())
        self.stacked_layout.addWidget(self.create_select_model())

        self.setLayout(self.mainLayout)
        self.stacked_layout.setCurrentIndex(0)

    def create_start_train_ai_gui(self) -> QWidget:
        # Labels
        self.image_count_label = QLabel(self.image_count)

        # Comboboxes
        self.modelSelected = QComboBox()
        self.modelSelected.addItems(["YOLOv5"])
        self.modelSelected.setCurrentIndex(0)

        self.config_selector_combobox = QComboBox()
        self.load_dataset_configs()
        self.config_selector_combobox.currentIndexChanged.connect(self.combobox_index_changed)

        self.selectedModelLabel = QLabel("None")
        self.select_model_button = QPushButton("Select Model")
        self.reset_model_selected_button = QPushButton("Reset Model")
        self.reset_model_selected_button.setHidden(True)
        self.select_model_button.pressed.connect(self.select_model)
        self.reset_model_selected_button.pressed.connect(self.reset_model_selection)

        self.AINameInput = QLineEdit()
        self.AINameInput.setText("New AI")

        self.epoch_num_input = QLineEdit()
        self.epoch_num_input.setPlaceholderText("Enter Number of Epoch")
        self.epoch_num_input.setValidator(QIntValidator())  # Only allows integers
        self.epoch_num_input.setText("50")

        newAIModelLayout = QGridLayout()
        startTrainAiLayout = QGridLayout()

        selected_model_layout = QGridLayout()
        selected_model_layout.addWidget(self.selectedModelLabel, 0, 0)
        selected_model_layout.addWidget(self.select_model_button, 0, 1)
        selected_model_layout.addWidget(self.reset_model_selected_button, 0, 1)
        selected_model_layout_wrapper_widget = QWidget()
        selected_model_layout_wrapper_widget.setLayout(selected_model_layout)

        newAIModelLayout.addWidget(QLabel("Name:"), 0, 0)
        newAIModelLayout.addWidget(self.AINameInput, 0, 1)

        newAIModelLayout.addWidget(QLabel("Selected Dataset"), 1, 0)
        newAIModelLayout.addWidget(self.config_selector_combobox, 1, 1)

        newAIModelLayout.addWidget(QLabel("Image Count:"), 2, 0)
        newAIModelLayout.addWidget(self.image_count_label, 2, 1)

        newAIModelLayout.addWidget(QLabel("Model Architecture Selected:"), 3, 0)
        newAIModelLayout.addWidget(self.modelSelected, 3, 1)

        newAIModelLayout.addWidget(QLabel("Continue Training From:"), 4, 0)
        newAIModelLayout.addWidget(selected_model_layout_wrapper_widget, 4, 1)

        newAIModelLayout.addWidget(QLabel("Epoch:"), 5, 0)
        newAIModelLayout.addWidget(self.epoch_num_input, 5, 1)

        # Init main layout
        startTrainAiLayout.addWidget(QLabel("Train New AI"), 0, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)

        startTrainAiLayout.addLayout(newAIModelLayout, 1, 0, newAIModelLayout.rowCount(), 2)

        self.trainFromScratchButton = QPushButton("Train from scratch")
        self.trainFromScratchButton.pressed.connect(self.start_ai_train)

        startTrainAiLayout.addWidget(self.trainFromScratchButton, newAIModelLayout.rowCount() + 1, 0, 1, 2)

        self.cancelButton = QPushButton("Cancel Training")
        self.cancelButton.pressed.connect(self.confirm_cancel_training)
        self.cancelButton.setHidden(True)
        startTrainAiLayout.addWidget(self.cancelButton, newAIModelLayout.rowCount() + 1, 0, 1, 2)

        startTrainAiWidget = QWidget()
        startTrainAiWidget.setLayout(startTrainAiLayout)
        return startTrainAiWidget

    def create_ai_train_gui(self):
        aiTrainingInProgressLayout = QGridLayout()
        # AI In Training Layout

        self.AINameInputInProgress = QLabel(self.AINameInput.text())
        aiTrainingInProgressLayout.addWidget(self.AINameInputInProgress, 0, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        aiTrainingInProgressLayout.setSpacing(20)

        # Data Augmentation Layout
        dataAugmentationColumn = QFrame()
        dataAugmentationColumn.setFrameShape(QFrame.Box)
        dataAugmentationColumn.setLineWidth(1)
        dataAugmentationColumn.setMinimumWidth(200)

        layout = QVBoxLayout()
        label = QLabel("Data Augmentation Stage")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        self.dataAugmentationTextBox = QLabel("")
        layout.addWidget(self.dataAugmentationTextBox, Qt.AlignmentFlag.AlignCenter)

        self.dataAugmentationProgressBar = QProgressBar()
        self.dataAugmentationProgressBar.setValue(0)
        layout.addWidget(self.dataAugmentationProgressBar, Qt.AlignmentFlag.AlignBottom)

        dataAugmentationColumn.setLayout(layout)
        aiTrainingInProgressLayout.addWidget(dataAugmentationColumn, 1, 0)

        # Training Layout
        trainingStageColumn = QFrame()
        trainingStageColumn.setFrameShape(QFrame.Box)
        trainingStageColumn.setLineWidth(1)
        trainingStageColumn.setMinimumWidth(200)

        layout = QVBoxLayout()
        label = QLabel("Training Stage")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        self.modelTrainingTextBox = QTextEdit()
        self.modelTrainingTextBox.setReadOnly(True)
        layout.addWidget(self.modelTrainingTextBox, Qt.AlignmentFlag.AlignCenter)

        self.trainingProgressBar = QProgressBar()
        self.trainingProgressBar.setValue(0)
        layout.addWidget(self.trainingProgressBar, Qt.AlignmentFlag.AlignBottom)

        trainingStageColumn.setLayout(layout)
        aiTrainingInProgressLayout.addWidget(trainingStageColumn, 1, 1)

        # Testing Layout
        testingStageColumn = QFrame()
        testingStageColumn.setFrameShape(QFrame.Box)
        testingStageColumn.setLineWidth(1)
        testingStageColumn.setMinimumWidth(200)

        layout = QVBoxLayout()
        label = QLabel("Testing Stage")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        self.testingStageTextBox = QLabel("")
        layout.addWidget(self.testingStageTextBox, Qt.AlignmentFlag.AlignCenter)

        self.testingProgressBar = QProgressBar()
        self.testingProgressBar.setValue(0)
        layout.addWidget(self.testingProgressBar, Qt.AlignmentFlag.AlignBottom)

        testingStageColumn.setLayout(layout)
        aiTrainingInProgressLayout.addWidget(testingStageColumn, 1, 2)

        aiTrainingInProgressLayout.setColumnStretch(0, 1)
        aiTrainingInProgressLayout.setColumnStretch(1, 1)
        aiTrainingInProgressLayout.setColumnStretch(2, 1)
        aiTrainingInProgressWidget = QWidget()
        aiTrainingInProgressWidget.setLayout(aiTrainingInProgressLayout)

        return aiTrainingInProgressWidget

    def select_model(self):
        self.stacked_layout.setCurrentIndex(2)

    def reset_model_selection(self):
        self.selected_starting_model = ""
        self.selectedModelLabel.setText("None")
        self.select_model_button.setHidden(False)
        self.reset_model_selected_button.setHidden(True)

    def create_select_model(self):
        self.select_ai_widget = SelectAiPage()
        self.select_ai_widget.model_selected.connect(self.model_selected)
        self.select_ai_widget.switch_view.connect(self.switch_views)
        return self.select_ai_widget

    def model_selected(self, name, path):
        self.selected_starting_model = path
        self.selectedModelLabel.setText(name)
        self.select_model_button.setHidden(True)
        self.reset_model_selected_button.setHidden(False)
        self.switch_views()

    def load_dataset_configs(self):
        """Retrieve list of .txt files in the directory"""
        if self.config_selector_combobox.count() != 0:
            self.config_selector_combobox.clear()

        datasets = [os.path.splitext(f)[0] for f in os.listdir(self.dataset_config_dir) if f.endswith(".txt")]
        self.config_combobox_items = ["All Images"]
        self.config_combobox_items.extend(datasets)
        self.config_selector_combobox.addItems(self.config_combobox_items)
        self.config_selector_combobox.setCurrentIndex(0)
        self.combobox_index_changed(0)

    def combobox_index_changed(self, index):
        if index == 0:
            self.image_count = str(file_helpers.count_files_in_directory(self.image_dir))
            self.image_count_label.setText(self.image_count)
        else:
            current_config = self.config_combobox_items[index]
            config_path = os.path.join(self.dataset_config_dir, current_config + ".txt")
            self.image_count = str(file_helpers.count_lines_in_file(config_path))
            self.image_count_label.setText(self.image_count)

    def switch_views(self):
        if (self.trainInProgress):
            if (self.stacked_layout.currentIndex() == 0):
                self.stacked_layout.setCurrentIndex(1)
            else:
                self.stacked_layout.setCurrentIndex(0)
        else:
            if (self.stacked_layout.currentIndex() == 0):
                self.stacked_layout.setCurrentIndex(2)
            else:
                self.stacked_layout.setCurrentIndex(0)

    def start_ai_train(self):
        if (self.AINameInput.text() == "" or not
                self.epoch_num_input.text().isdigit() or int(self.epoch_num_input.text()) <= 0):

            errorMessage = QMessageBox()
            errorMessage.setIcon(QMessageBox.Critical)
            errorMessage.setWindowTitle("Error")
            errorMessage.setText("One or more parameters is incorrect.\nPlease check your inputs.")
            errorMessage.exec()
            return

        self.AINameInputInProgress.setText(self.AINameInput.text())
        self.trainInProgress = True
        self.trainFromScratchButton.setVisible(False)
        self.cancelButton.setHidden(False)
        self.cancelButton.setText("Creating Pipeline...")
        self.cancelButton.setDisabled(True)
        self.model_info = ModelInfo(self.AINameInput.text(),
                                    self.modelSelected.currentText(),
                                    "",
                                    self.image_count,
                                    epoch=self.epoch_num_input.text(),
                                    dataset_config=self.config_combobox_items[
                                        self.config_selector_combobox.currentIndex()],
                                    starting_model=self.selected_starting_model)

        self.pipeline = MainTrainPipeline(self, self.model_info)

        self.pipeline.pipeline_started.connect(self.pipeline_created)
        self.pipeline.data_augmentation_text.connect(self.update_data_augmentation_text)
        self.pipeline.data_augmentation_progress_bar.connect(self.update_data_augmentation_progress_bar)
        self.pipeline.model_training_text.connect(self.update_model_training_text)
        self.pipeline.model_training_progress_bar.connect(self.update_model_training_progress_bar)
        self.pipeline.model_testing_text.connect(self.update_testing_text)
        self.pipeline.model_testing_progress_bar.connect(self.update_data_augmentation_progress_bar)
        self.pipeline.pipeline_finished.connect(self.stop_training)

        self.pipeline.start()

    def pipeline_created(self, val):
        self.switch_view_widget.setHidden(False)
        self.stacked_layout.setCurrentIndex(1)
        self.cancelButton.setText("Cancel Training")
        self.cancelButton.setDisabled(False)

    def confirm_cancel_training(self):
        confirmMessageBox = QMessageBox()
        confirmMessageBox.setIcon(QMessageBox.Warning)
        confirmMessageBox.setWindowTitle("Cancel Confirmation")
        confirmMessageBox.setText("Are you sure you want to cancel?")
        confirmMessageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = confirmMessageBox.exec()

        if (result == QMessageBox.Yes):
            self.cancel_training()

    def cancel_training(self):
        print("TODO: Cancel Logic")

        self.trainInProgress = False
        self.cancelButton.setVisible(False)
        self.switch_view_widget.setVisible(False)
        self.stacked_layout.setCurrentIndex(0)
        self.trainFromScratchButton.setVisible(True)

    def stop_training(self):
        if (self.pipeline and self.pipeline._is_running):
            self.pipeline.stop()
            self.pipeline.wait()
        self.cancel_training()

    def update_data_augmentation_progress_bar(self, progress):
        self.dataAugmentationProgressBar.setValue(progress)

    def update_data_augmentation_text(self, update):
        self.dataAugmentationTextBox.setText(self.dataAugmentationTextBox.text() + " " + update)

    def update_model_training_progress_bar(self, progress):
        self.trainingProgressBar.setValue(progress)

    def parse_update_for_progress(self, text):
        # Regex to extract (epoch/total_epochs) and (percentage completed)
        pattern = r"(\d+)\/(\d+).*?(\d+)%\|"
        match = re.search(pattern, text)

        if match:
            epoch = int(match.group(1))         # Current epoch
            total_epochs = int(match.group(2))  # Total epochs
            stage_progress = int(match.group(3))  # % progress in the current stage

            # Overall progress
            self.trainingProgressBar.setValue(
                ((epoch - 1) / total_epochs + (stage_progress / 100) / total_epochs) * 100
            )

    def update_model_training_text(self, update):
        self.modelTrainingTextBox.append(update)
        self.parse_update_for_progress(update)

    def update_testing_progress_bar(self, progress):
        self.testingProgressBar.setValue(progress)

    def update_testing_text(self, update):
        self.testingStageTextBox.setText(self.testingStageTextBox.text() + " " + update)

    def closeEvent(self, event):
        """ Handle window close event """
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()  # Ensure thread exits before closing

        event.accept()  # Proceed with closing
