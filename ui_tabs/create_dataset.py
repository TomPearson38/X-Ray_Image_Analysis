import os
from PySide6.QtWidgets import (QWidget, QLabel, QGridLayout,
                               QPushButton, QLineEdit, QCheckBox, QMessageBox)
from PySide6.QtCore import Signal, Qt
from helpers import file_helpers


class CreateDataset(QWidget):
    dataset_created_signal = Signal(str)
    cancel_creation_signal = Signal()

    def __init__(self, path_to_dataset_folder):
        super().__init__()
        self.main_layout = QGridLayout()
        self.path_to_dataset_folder = path_to_dataset_folder

        # Labels
        self.page_label = QLabel("Create New Dataset Config")
        self.name_label = QLabel("Name: ")
        self.import_all_images_label = QLabel("Import All Images? ")

        # Text Input
        self.name_text_input = QLineEdit()

        # Check box
        self.import_all_images_checkbox = QCheckBox()

        # Buttons
        self.create_dataset_button = QPushButton("Create")
        self.cancel_create_dataset_button = QPushButton("Cancel")
        self.create_dataset_button.pressed.connect(self.create_dataset)
        self.cancel_create_dataset_button.pressed.connect(self.cancel_create_dataset)

        # Buttons Layout
        self.stacked_buttons_layout = QGridLayout()
        self.stacked_buttons_layout.addWidget(self.create_dataset_button, 0, 0)
        self.stacked_buttons_layout.addWidget(self.cancel_create_dataset_button, 0, 1)
        self.stacked_buttons_layout_wrapper_widget = QWidget()
        self.stacked_buttons_layout_wrapper_widget.setLayout(self.stacked_buttons_layout)

        self.main_layout.addWidget(self.page_label, 0, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self.name_label, 1, 0)
        self.main_layout.addWidget(self.name_text_input, 1, 1)
        self.main_layout.addWidget(self.import_all_images_label, 2, 0)
        self.main_layout.addWidget(self.import_all_images_checkbox, 2, 1)
        self.main_layout.addWidget(self.stacked_buttons_layout_wrapper_widget, 3, 0, 1, 2)

        self.setLayout(self.main_layout)

    def create_dataset(self):
        new_name = self.name_text_input.text()
        if new_name == "":
            QMessageBox.information(self,
                                    "Invalid Name",
                                    "The name you have entered is not valid. "
                                    "Please enter a new name")
            return

        new_file_name = new_name + ".txt"
        new_file_path = os.path.join(self.path_to_dataset_folder, new_file_name)
        is_created = file_helpers.create_file_empty_txt(new_file_path)

        if not is_created:
            QMessageBox.information(self,
                                    "Name Taken",
                                    "The name you have entered is already taken. "
                                    "Please enter a new name")
        else:
            self.dataset_created_signal.emit(new_name)

    def cancel_create_dataset(self):
        self.cancel_creation_signal.emit()
