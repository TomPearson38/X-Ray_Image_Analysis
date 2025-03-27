from PySide6.QtWidgets import (QWidget, QGridLayout,
                               QPushButton, QListWidget, QLabel)
from PySide6.QtCore import Signal
from data_classes.ScrollableQGraphicsView import ScrollableQGraphicsView


class ImageViewer(QWidget):
    save_finished = Signal()

    """ Custom QGraphicsView to handle bounding box drawing """
    def __init__(self, image_path, annotation_path, file_name):
        super().__init__()
        self.image_path = image_path
        self.annotation_path = annotation_path
        self.file_name = file_name

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        ####
        # Name Label
        self.name_label = QLabel(file_name)

        # Annotation List
        self.annotation_list = QListWidget()

        # Load Image and Annotations
        self.image_view = ScrollableQGraphicsView(self.image_path, self.annotation_path, self.annotation_list)
        self.annotation_list.itemClicked.connect(self.image_view.on_annotation_selected)

        # Buttons
        self.add_annotations_button = QPushButton("Add Annotation")
        self.cancel_add_annotations_button = QPushButton("Cancel Add Annotation")
        delete_annotation_button = QPushButton("Delete Annotation")
        zoom_in_button = QPushButton("Zoom In")
        zoom_out_button = QPushButton("Zoom Out")
        save_button = QPushButton("Save Changes!")
        save_button.clicked.connect(self.save_changes)
        zoom_in_button.clicked.connect(self.image_view.zoom_in)
        zoom_out_button.clicked.connect(self.image_view.zoom_out)
        self.add_annotations_button.clicked.connect(self.add_annotation)
        delete_annotation_button.clicked.connect(self.image_view.delete_selected_annotation)
        self.cancel_add_annotations_button.clicked.connect(self.finish_annotation)
        self.image_view.annotation_added.connect(self.finish_annotation)

        ####
        # Layout setup
        self.layout.addWidget(self.name_label, 0, 0, 1, 2)
        self.layout.addWidget(self.image_view, 1, 0)
        self.layout.addWidget(self.annotation_list, 1, 1)
        self.layout.addWidget(zoom_in_button, 2, 0)
        self.layout.addWidget(self.add_annotations_button, 2, 1)
        self.layout.addWidget(self.cancel_add_annotations_button, 2, 1)
        self.layout.addWidget(zoom_out_button, 3, 0)
        self.layout.addWidget(delete_annotation_button, 3, 1)
        self.layout.addWidget(save_button, 4, 0, 1, 2)

        self.cancel_add_annotations_button.setHidden(True)

    def add_annotation(self):
        self.cancel_add_annotations_button.setVisible(True)
        self.add_annotations_button.setVisible(False)
        self.image_view.add_annotation()

    def finish_annotation(self):
        self.cancel_add_annotations_button.setVisible(False)
        self.add_annotations_button.setVisible(True)
        self.image_view.cancel_add_annotation()

    def save_changes(self):
        new_txt = self.image_view.save_annotations()
        with open(self.annotation_path, 'w') as file:
            file.write(new_txt)

        self.save_finished.emit()
