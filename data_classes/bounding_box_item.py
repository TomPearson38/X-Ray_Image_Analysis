from PySide6.QtWidgets import (QGraphicsRectItem, QListWidgetItem)
from PySide6.QtGui import QPen
from PySide6.QtCore import Qt, QRectF


class BoundingBoxItem(QGraphicsRectItem):
    """ Custom class to handle bounding box selection/editing """
    def __init__(self, class_id, x_center, y_center, box_w, box_h, img_w,
                 img_h, list_widget):

        self.class_id = int(class_id)
        self.x_center = x_center
        self.y_center = y_center
        self.box_w = box_w
        self.box_h = box_h
        self.img_w = img_w
        self.img_h = img_h
        self.list_widget = list_widget

        x1 = (self.x_center - self.box_w / 2) * self.img_w
        y1 = (self.y_center - self.box_h / 2) * self.img_h
        rect = QRectF(x1, y1, self.box_w * self.img_w, self.box_h * self.img_h)
        super().__init__(rect)

        self.setPen(QPen(Qt.red, 2))
        self.setFlag(QGraphicsRectItem.ItemIsMovable, False)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, False)

        annotation_text = f"Class {self.class_id}: ({x1:.1f}, {y1:.1f})"
        list_item = QListWidgetItem(annotation_text)
        self.list_widget.addItem(list_item)

        self.annotation_text = annotation_text
        self.list_item = list_item

    @classmethod
    def from_rect(cls, class_id, rect: QRectF, img_w, img_h, list_widget):
        rect_vals = rect.getRect()

        box_w = rect_vals[2] / img_w
        box_h = rect_vals[3] / img_h

        x_center = (rect_vals[0] / img_w) + (box_w / 2)
        y_center = (rect_vals[1] / img_h) + (box_h / 2)

        return cls(class_id, x_center, y_center, box_w, box_h, img_w,
                   img_h, list_widget)

    def convert_to_string(self, img_w, img_h) -> str:
        return_statement = f"{self.class_id} {self.x_center} {self.y_center} {self.box_w} {self.box_h}"
        return return_statement
