from PySide6.QtCore import QObject, Signal, Slot
from ultralytics import YOLO


class ImageAnalysisWorker(QObject):
    finished = Signal(object)

    def __init__(self, model_path, image_path):
        super().__init__()
        self.model_path = model_path
        self.image_path = image_path

    @Slot()
    def run(self):
        model = YOLO(self.model_path)
        results = model(self.image_path)
        self.finished.emit(results)
