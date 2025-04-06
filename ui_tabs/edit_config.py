from PySide6.QtWidgets import (QWidget, QGridLayout, QPushButton, QMessageBox)
from PySide6.QtCore import Signal
from data_classes.edit_config_item_container import EditConfigItemContainer
from data_classes.image_item_container import ImageItemContainer
from helpers import file_helpers

from ui_tabs.view_dataset import ViewDataset


class EditConfig(QWidget):
    return_signal = Signal()

    def __init__(self, path_to_config, list_of_image_containers: list[ImageItemContainer], column_count=1):
        super().__init__()
        self.path_to_config = path_to_config
        self.column_count = column_count
        self.delete = False
        self.list_of_image_containers = list_of_image_containers
        self.unsaved_changes = False

        self.selected_files = file_helpers.read_config_file(self.path_to_config)

        self.converted_image_containers = [
            EditConfigItemContainer(
                item, item.get_label_text() in self.selected_files
            )
            for item in self.list_of_image_containers
        ]

        self.image_in_set = [obj for obj in self.converted_image_containers if obj.is_in_current_config]

        self.other_images = [obj for obj in self.converted_image_containers if not obj.is_in_current_config]

        self.view_added_images = ViewDataset(self.image_in_set, False, column_count=column_count)

        self.view_other_images = ViewDataset(self.other_images, False, column_count=column_count)

        self.save_button = QPushButton("Save")
        self.save_button.pressed.connect(self.save_button_pressed)

        self.return_button = QPushButton("Return")
        self.return_button.pressed.connect(self.return_button_pressed)

        self.layout = QGridLayout()
        self.layout.addWidget(self.view_added_images, 0, 0)
        self.layout.addWidget(self.view_other_images, 0, 1)
        self.layout.addWidget(self.save_button, 1, 0)
        self.layout.addWidget(self.return_button, 1, 1)

        for config in self.converted_image_containers:
            config.item_added.connect(self.image_added)
            config.item_removed.connect(self.image_removed)

        self.setLayout(self.layout)

    def image_added(self, label, edit_config_item_container):
        self.unsaved_changes = True
        self.image_in_set.append(edit_config_item_container)
        self.other_images.remove(edit_config_item_container)
        self.update_view_dataset_vars()

    def image_removed(self, label, edit_config_item_container):
        self.unsaved_changes = True
        self.image_in_set.remove(edit_config_item_container)
        self.other_images.append(edit_config_item_container)
        self.update_view_dataset_vars()

    def update_view_dataset_vars(self):
        self.view_added_images.update_images(self.image_in_set)
        self.view_other_images.update_images(self.other_images)

    def save_button_pressed(self):
        self.delete = True

        file_string = ""

        for item in self.image_in_set:
            file_string += item.save_to_config()

        if file_string.endswith("\n"):
            file_string = file_string[:-1]

        file_helpers.update_config(self.path_to_config, file_string)

        self.return_signal.emit()

    def return_button_pressed(self):
        self.return_button.setDisabled(True)

        if self.unsaved_changes:
            reply = QMessageBox.question(self,
                                         "Unsaved Changes",
                                         "You have unsaved changes to the bounding boxes. "
                                         "Do you want to exit without saving?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if reply == QMessageBox.No:
                self.return_button.setDisabled(False)
                return

        self.delete = True
        self.return_signal.emit()

    def set_column_count(self, count):
        """Update column count and refresh the grid."""
        if count != self.column_count:
            self.column_count = max(1, count)
            self.view_added_images.set_column_count(count)
            self.view_other_images.set_column_count(count)
