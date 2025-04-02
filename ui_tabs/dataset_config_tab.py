from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGridLayout,
                               QFrame, QStackedLayout, QPushButton,
                               QMessageBox, QComboBox)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os
from helpers import file_helpers
from ui_tabs.create_dataset import CreateDataset
from ui_tabs.view_dataset import ViewDataset
from ui_tabs.view_image import ImageViewer


class DatasetConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        self.main_stacked_layout = QStackedLayout()
        self.view_config_stacked_layout = QStackedLayout()

        data_dir = os.path.abspath("stored_training_images")
        self.dataset_config_dir = os.path.join(data_dir, "datasets")
        self.image_dir = os.path.join(data_dir, "images", "raw")
        self.annotation_dir = os.path.join(data_dir, "labels", "raw")
        self.image_files = []
        self.column_count = 3

        # Buttons
        self.create_new_config_button = QPushButton("Create New Config")
        self.edit_config_button = QPushButton("Edit Config")
        self.delete_config_button = QPushButton("Delete Config")
        self.create_new_config_button.pressed.connect(self.create_config)
        self.edit_config_button.pressed.connect(self.edit_config)
        self.delete_config_button.pressed.connect(self.delete_config)

        # Select Image Config
        self.dataset_config_combobox = QComboBox()
        self.update_dataset_configs(self.dataset_config_dir)
        self.dataset_config_combobox.currentIndexChanged.connect(self.load_config)

        # Main Layout
        self.stacked_layout_widget_wrapper = QWidget()
        self.stacked_layout_widget_wrapper.setLayout(self.view_config_stacked_layout)

        self.dataset_config_grid_layout = QGridLayout()
        self.dataset_config_grid_layout.addWidget(self.dataset_config_combobox, 0, 0)
        self.dataset_config_grid_layout.addWidget(self.edit_config_button, 0, 1)
        self.dataset_config_grid_layout.addWidget(self.delete_config_button, 0, 2)
        self.dataset_config_grid_layout.addWidget(self.create_new_config_button, 0, 3)
        self.dataset_config_grid_layout.addWidget(self.stacked_layout_widget_wrapper, 1, 0, 1, 4)

        self.dataset_config_grid_layout_widget_container = QWidget()
        self.dataset_config_grid_layout_widget_container.setLayout(self.dataset_config_grid_layout)

        self.main_stacked_layout.addWidget(self.dataset_config_grid_layout_widget_container)

        self.setLayout(self.main_stacked_layout)

        self.load_images()

        self.load_config(0)

        self.view_config_stacked_layout.setCurrentIndex(0)
        self.main_stacked_layout.setCurrentIndex(0)

    def set_column_count(self, count):
        if count != self.column_count:
            self.column_count = max(1, count)
            if self.current_config:
                self.current_config.set_column_count(count)

    def update_dataset_configs(self, dataset_dir):
        """Retrieve list of .txt files in the directory"""
        if self.dataset_config_combobox.count() != 0:
            self.dataset_config_combobox.clear()

        datasets = [os.path.splitext(f)[0] for f in os.listdir(dataset_dir) if f.endswith(".txt")]
        self.combobox_items = ["All Images"]
        self.combobox_items.extend(datasets)
        self.dataset_config_combobox.addItems(self.combobox_items)
        self.dataset_config_combobox.setCurrentIndex(0)

    def load_images(self):
        """ Loads the images to be added to the list of item containers """
        self.image_files = [f for f in os.listdir(self.image_dir) if f.endswith(('.jpg', '.png'))]

        self.list_of_item_containers = []
        self.filtered_list = []

        for i, img_file in enumerate(self.image_files):
            self.append_images(img_file)

    def append_images(self, img_file):
        img_path = os.path.join(self.image_dir, img_file)

        # Create a container widget for image + label
        item_container = QWidget()
        item_layout = QVBoxLayout(item_container)
        item_layout.setAlignment(Qt.AlignCenter)

        # Thumbnail
        thumb_label = QLabel()
        thumb_label.setPixmap(QPixmap(img_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        thumb_label.setFixedSize(110, 110)  # Keeps all boxes the same size
        thumb_label.setAlignment(Qt.AlignCenter)
        thumb_label.setFrameStyle(QFrame.Box)  # Adds a border for consistency

        # Image name
        name_label = QLabel(img_file)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setFixedWidth(110)  # Keeps labels aligned

        # Add to layout
        item_layout.addWidget(thumb_label)
        item_layout.addWidget(name_label)
        item_container.setLayout(item_layout)

        thumb_label.mousePressEvent = lambda e, path=img_path, file_name=img_file: self.open_detail_view(path,
                                                                                                         file_name)

        self.list_of_item_containers.append(item_container)

    def open_detail_view(self, img_path, file_name):
        """ Open selected image in a detailed view """
        annotation_path = os.path.join(self.annotation_dir, os.path.splitext(os.path.basename(img_path))[0] + ".txt")

        self.view_image_layout = QGridLayout()
        backButton = QPushButton("Return To View Images")
        backButton.pressed.connect(self.reset_layout)
        self.view_image_layout.addWidget(backButton, 0, 0)
        self.img_viewer_widget = ImageViewer(img_path, annotation_path, file_name)
        self.img_viewer_widget.save_finished_signal.connect(self.reset_layout)
        self.img_viewer_widget.delete_image_signal.connect(self.delete_image)
        self.view_image_layout.addWidget(self.img_viewer_widget)

        self.view_image_layout_wrapper = QWidget()
        self.view_image_layout_wrapper.setLayout(self.view_image_layout)

        self.main_stacked_layout.addWidget(self.view_image_layout_wrapper)
        self.main_stacked_layout.setCurrentWidget(self.view_image_layout_wrapper)

    def reset_layout(self):
        if self.main_stacked_layout.count() > 1:
            if hasattr(self, "img_viewer_widget"):
                if self.img_viewer_widget.image_view.is_unsaved_changes():
                    reply = QMessageBox.question(self,
                                                 "Unsaved Changes",
                                                 "You have unsaved changes to the bounding boxes. "
                                                 "Do you want to exit without saving?",
                                                 QMessageBox.Yes | QMessageBox.No,
                                                 QMessageBox.No)
                    if reply == QMessageBox.No:
                        return

            self.main_stacked_layout.setCurrentWidget(self.dataset_config_grid_layout_widget_container)
            self.main_stacked_layout.removeWidget(
                self.main_stacked_layout.itemAt(
                    self.main_stacked_layout.count() - 1
                ).widget()
            )

    def delete_image(self, image_path, annotation_path, img_name):
        for img in self.list_of_item_containers:
            if self.compare_name_to_search(img.layout(), img_name):
                self.reset_layout()
                self.list_of_item_containers.remove(img)
                file_helpers.delete_file(image_path)
                file_helpers.delete_file(annotation_path)
                self.filter_images()
                break

        if self.current_config:
            self.current_config.update_images(self.list_of_item_containers)

    def create_config(self):
        self.create_config_page = CreateDataset(self.dataset_config_dir)
        self.create_config_page.dataset_created_signal.connect(self.config_created)
        self.create_config_page.cancel_creation_signal.connect(self.reset_layout)
        self.main_stacked_layout.addWidget(self.create_config_page)
        self.main_stacked_layout.setCurrentWidget(self.create_config_page)

    def config_created(self, new_file_name):
        self.update_dataset_configs(self.dataset_config_dir)
        index_of_new_config = self.combobox_items.index(new_file_name)
        self.dataset_config_combobox.setCurrentIndex(index_of_new_config)
        self.load_config(index_of_new_config)

    def load_config(self, index):
        if index >= 0:  # Ensure a valid selection
            if hasattr(self, "current_config"):
                self.view_config_stacked_layout.setCurrentIndex(0)
                self.view_config_stacked_layout.removeWidget(self.current_config)
                self.current_config = None

            if index == 0:
                self.edit_config_button.setHidden(True)
                self.delete_config_button.setHidden(True)
                self.current_config = ViewDataset(self.list_of_item_containers, self.annotation_dir)
            else:
                self.edit_config_button.setHidden(False)
                self.delete_config_button.setHidden(False)
                selected_file = self.combobox_items[index]
                config_path = os.path.join(self.dataset_config_dir, selected_file + ".txt")
                self.current_config = ViewDataset(self.list_of_item_containers, self.annotation_dir, config_path)

            self.current_config.set_column_count(self.column_count)
            self.view_config_stacked_layout.addWidget(self.current_config)
            self.view_config_stacked_layout.setCurrentWidget(self.current_config)

            self.current_config.add_image_signal.connect(self.add_image)

    def add_image(self, path_to_config=""):
        # Image prompt, user selects valid image
        result = file_helpers.browse_file(self, "", "Images (*.png *.jpg)")
        if result != "" and (result.endswith(".png") or result.endswith(".jpg")):
            self.selectedImage = result
        else:
            return

        new_img_folder = os.path.join("stored_training_images", "images", "raw")
        new_txt_folder = os.path.join("stored_training_images", "labels", "raw")
        safe_image_path, safe_image_file_name = file_helpers.create_valid_data_file_name(result,
                                                                                         new_img_folder,
                                                                                         new_txt_folder)

        file_helpers.move_file(result, safe_image_path)

        # Annotation file created
        file_name_without_ext = (os.path.splitext(safe_image_file_name)[0]) + ".txt"
        txt_destination_path = os.path.join(new_txt_folder, file_name_without_ext)

        file_helpers.create_file_empty_txt(txt_destination_path)

        if path_to_config != "":
            file_helpers.add_new_img(path_to_config, file_name_without_ext)

        self.append_images(safe_image_file_name)
        self.current_config.update_images(self.list_of_item_containers)
        self.open_detail_view(safe_image_path, safe_image_file_name)

    def edit_config(self):
        pass

    def delete_config(self):
        combo_box_current_index = self.dataset_config_combobox.currentIndex()
        if combo_box_current_index != 0:
            reply = QMessageBox.question(self,
                                         "Confirmation",
                                         "Are you sure you would like to delete this config? "
                                         "This operation cannot be undone!",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if reply == QMessageBox.No:
                return

            config_to_be_delete_name = self.combobox_items[combo_box_current_index]
            config_to_be_delete_path = os.path.join(self.dataset_config_dir, config_to_be_delete_name + ".txt")
            file_helpers.delete_file(config_to_be_delete_path)

            self.update_dataset_configs(self.dataset_config_dir)
