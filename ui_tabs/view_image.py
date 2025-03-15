from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem)
from PySide6.QtGui import QPixmap, QPen
from PySide6.QtCore import Qt, QRectF
import os
import cv2


class BoundingBoxItem(QGraphicsRectItem):
    """ Custom class to handle bounding box selection/editing """
    def __init__(self, rect):
        super().__init__(rect)
        self.setPen(QPen(Qt.red, 2))
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)


class ImageViewer(QGraphicsView):
    """ Custom QGraphicsView to handle bounding box drawing """
    def __init__(self, image_path, annotation_path):
        super().__init__()
        self.image_path = image_path
        self.annotation_path = annotation_path
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Load image
        pixmap = QPixmap(self.image_path)
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)

        # Load annotations
        self.bounding_boxes = []
        self.load_annotations()

        # Mouse tracking
        self.drawing = False
        self.start_pos = None

    def load_annotations(self):
        """ Load YOLO bounding boxes and convert to pixel coordinates """
        img = cv2.imread(self.image_path)
        h, w, _ = img.shape

        if os.path.exists(self.annotation_path):
            with open(self.annotation_path, "r") as f:
                for line in f.readlines():
                    class_id, x_center, y_center, box_w, box_h = map(float, line.strip().split())
                    x1 = (x_center - box_w / 2) * w
                    y1 = (y_center - box_h / 2) * h
                    box = BoundingBoxItem(QRectF(x1, y1, box_w * w, box_h * h))
                    self.scene.addItem(box)
                    self.bounding_boxes.append(box)
