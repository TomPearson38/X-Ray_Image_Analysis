from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, Signal
import cv2


class ViewResultsPage(QWidget):
    switch_view = Signal()

    def __init__(self, original_image, ai_result):
        super().__init__()

        self.original_image = original_image
        self.ai_result = ai_result
        layout = QGridLayout()

        result_label = QLabel("")
        if len(self.ai_result[0].boxes.cls) > 0:
            confidence_scores = self.ai_result[0].boxes.conf
            result_label.setText("Result: Fault Detected")

            count = 1
            for conf in confidence_scores:
                result_label.setText(result_label.text() + f"\n{count}: Confidence {conf:.2f}")
                count += 1
        else:
            result_label.setText("No Fault Detected")

        layout.addWidget(result_label, 0, 0, Qt.AlignmentFlag.AlignCenter)

        image = self.convert_image(self.ai_result[0].plot())

        analysed_image_label = QLabel()
        image.scaledToHeight(100)
        analysed_image_label.setPixmap(image)
        layout.addWidget(analysed_image_label, 1, 0, Qt.AlignmentFlag.AlignCenter)

        return_button = QPushButton("Return")
        return_button.pressed.connect(self.close_view)
        layout.addWidget(return_button, 2, 0, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def convert_image(self, image) -> QPixmap:
        # Convert OpenCV image (BGR) to QImage (RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        return QPixmap.fromImage(q_img)

    def close_view(self):
        self.switch_view.emit()
