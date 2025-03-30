from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGridLayout,
                               QFrame, QScrollArea, QStackedLayout, QPushButton, QMessageBox, QLineEdit, QFileDialog)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os
import shutil
from ui_tabs.view_image import ImageViewer


class TrainingDataTab(QWidget):
    """ Tab to browse and edit YOLO dataset """
    def __init__(self):
        super().__init__()
        self.stacked_layout = QStackedLayout()

        data_dir = os.path.abspath("stored_training_images")
        self.image_dir = os.path.join(data_dir, "images", "raw")
        self.annotation_dir = os.path.join(data_dir, "labels", "raw")
        self.image_files = []
        self.column_count = 3

        # Scrollable Thumbnail Grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Ensures the content resizes properly
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.scroll_area.setWidget(self.grid_container)

        # Search Function
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_images)

        # Buttons
        self.add_image_button = QPushButton("Add Image")
        self.add_image_button.clicked.connect(self.add_image)

        # Main Layout
        self.images_grid_layout = QGridLayout()
        self.images_grid_layout.addWidget(self.search_bar, 0, 0)
        self.images_grid_layout.addWidget(self.add_image_button, 0, 1)
        self.images_grid_layout.addWidget(self.scroll_area, 1, 0, 1, 2)
        self.images_grid_layout_wrapper = QWidget()
        self.images_grid_layout_wrapper.setLayout(self.images_grid_layout)

        self.stacked_layout.addWidget(self.images_grid_layout_wrapper)
        self.stacked_layout.setCurrentIndex(0)

        self.setLayout(self.stacked_layout)

        # Load images to display
        self.load_images()

    def load_images(self):
        """ Loads the images to be added to the list of item containers """
        self.image_files = [f for f in os.listdir(self.image_dir) if f.endswith(('.jpg', '.png'))]

        self.list_of_item_containers = []
        self.filtered_list = []

        for i, img_file in enumerate(self.image_files):
            self.append_images(img_file)

        self.filter_images()

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

    def filter_images(self):
        """Filters the images based on the contents of the search box"""
        self.filtered_list = []

        self.filtered_list = [img for img in self.list_of_item_containers
                              if self.compare_name_to_search(img.layout(), self.search_bar.text())]
        self.update_grid()

    def get_last_item(self, layout):
        """Get the last widget in the given layout."""
        count = layout.count()
        if count > 0:
            return layout.itemAt(count - 1)
        return None

    def compare_name_to_search(self, layout, search_string):
        """Check if the last item is a QLabel and contains the provided string."""
        last_item = self.get_last_item(layout)

        if last_item:
            widget = last_item.widget()
            if isinstance(widget, QLabel):  # Check if QLabel
                return search_string.lower() in widget.text().lower()  # Check contains the search string
        return False

    def set_column_count(self, count):
        """Update column count and refresh the grid."""
        if count != self.column_count:
            self.column_count = max(1, count)
            self.update_grid()

    def update_grid(self):
        """Clear and repopulate the grid with images based on current column count."""
        # Clear previous items
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        # Re-add images based on new column count
        for index, widget in enumerate(self.filtered_list):
            row = index // self.column_count
            col = index % self.column_count
            self.grid_layout.addWidget(widget, row, col)

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

        self.stacked_layout.addWidget(self.view_image_layout_wrapper)
        self.stacked_layout.setCurrentWidget(self.view_image_layout_wrapper)

    def reset_layout(self):
        if self.img_viewer_widget.image_view.is_unsaved_changes():
            reply = QMessageBox.question(self,
                                         "Unsaved Changes",
                                         "You have unsaved changes to the bounding boxes. "
                                         "Do you want to exit without saving?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if reply == QMessageBox.No:
                return

        self.stacked_layout.setCurrentWidget(self.images_grid_layout_wrapper)
        self.stacked_layout.removeWidget(self.view_image_layout_wrapper)

    # TODO add check for duplicate image name
    def add_image(self):
        # Image prompt, user selects valid image
        result = self.browse_file("", "Images (*.png *.jpg)")
        if result != "" and (result.endswith(".png") or result.endswith(".jpg")):
            self.selectedImage = result
        else:
            return

        # Correct image name extracted for destination path
        img_file_name = os.path.basename(self.selectedImage)
        img_destination_path = os.path.join("stored_training_images", "images", "raw", img_file_name)

        # Image moved
        shutil.copy(self.selectedImage, img_destination_path)

        # Annotation file created
        file_name_without_ext = (os.path.splitext(img_file_name)[0]) + ".txt"
        txt_destination_path = os.path.join("stored_training_images", "labels", "raw", file_name_without_ext)

        with open(txt_destination_path, 'w') as file:
            file.write("")

        self.append_images(img_file_name)  # Image added to current view
        self.filter_images()  # Images updated
        self.open_detail_view(img_destination_path, img_file_name)  # Detailed view opened for new img

    # TODO: Remove this function and add to shared DIR
    def browse_file(self, opendir, fileConstraints):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File", opendir, fileConstraints)
        if file_path:
            return file_path
        else:
            return ""

    def delete_image(self, image_path, annotation_path, img_name):
        for img in self.list_of_item_containers:
            if self.compare_name_to_search(img.layout(), img_name):
                self.reset_layout()
                self.list_of_item_containers.remove(img)
                self.delete_file(image_path)
                self.delete_file(annotation_path)
                self.filter_images()
                return

    def delete_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            print("File deleted")
        else:
            print("The file does not exist")
