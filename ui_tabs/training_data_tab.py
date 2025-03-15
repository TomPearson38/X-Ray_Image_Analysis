from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame, QScrollArea)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os
from ui_tabs.view_image import ImageViewer


class TrainingDataTab(QWidget):
    """ Tab to browse and edit YOLO dataset """
    def __init__(self):
        super().__init__()

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

        # Main Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.scroll_area, 0, 0)
        self.setLayout(self.layout)

        # Load images to display
        self.load_images()

    def load_images(self):
        """ Loads the images to be added to the list of item containers """
        self.image_files = [f for f in os.listdir(self.image_dir) if f.endswith(('.jpg', '.png'))]

        self.list_of_item_containers = []

        # Add thumbnails
        for i, img_file in enumerate(self.image_files):
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

            thumb_label.mousePressEvent = lambda e, path=img_path: self.open_detail_view(path)

            self.list_of_item_containers.append(item_container)

            self.update_grid()

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
        for index, widget in enumerate(self.list_of_item_containers):
            row = index // self.column_count
            col = index % self.column_count
            self.grid_layout.addWidget(widget, row, col)

    def open_detail_view(self, img_path):
        """ Open selected image in a detailed view """
        annotation_path = os.path.join(self.annotation_dir, os.path.splitext(os.path.basename(img_path))[0] + ".txt")
        self.detail_view = ImageViewer(img_path, annotation_path)
        self.detail_view.show()
