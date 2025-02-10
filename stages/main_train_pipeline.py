from prefect import task, flow
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QObject, Signal, Slot, QThread
import sys
import stages.model_training

class Communicate(QObject):
    signal_str = Signal(str)
    signal_int = Signal(int)

class MainTrainPipeline(QThread):
    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.signals = Communicate()
        # Connect the signals to the main thread slots
        self.signals.signal_str.connect(parent.update_a_str_field)
        self.signals.signal_int.connect(parent.update_a_int_field)

    
    def run(self):
        self.signals.signal_int.emit(1)
        self.signals.signal_str.emit("Hello World.")
        self.pipeline_flow()

    # Define the flow using @flow decorator
    @flow(name="PyQt Integrated Pipeline")
    def pipeline_flow(self):
        data = self.prepare_data()
        result = self.train_model(data)
        self.save_model(result)

    # Prefect tasks
    @task
    def prepare_data(self):
        # monitor.progress_signal.emit("Preparing data...") 
        return [1, 2, 3, 4, 5]

    @task
    def train_model(self, data):
        data_dir = "D:/Other computers/My PC/UniYear3/Dissertation/Code/X-Ray_Image_Analysis/data"  # Path to the dataset directory
        class_names = ["0"]  # List of class names, only 1 flaw
        output_yaml = "D:/Other computers/My PC/UniYear3/Dissertation/Code/X-Ray_Image_Analysis/data/models/1/dataset.yaml"  # Path to save the YAML file
        weights = "yolov5s.pt"  # Pretrained weights to use
        img_size = 640  # Image size for training
        batch_size = 16  # Batch size for training
        epochs = 50  # Number of epochs for training

        # Create YAML file for the dataset
        stages.model_training.create_yaml(data_dir, output_yaml, class_names)

        # Train the model
        stages.model_training.train_yolo(
            data_yaml=output_yaml,
            weights=weights,
            img_size=img_size,
            batch_size=batch_size,
            epochs=epochs
        )

        # monitor.progress_signal.emit(f"Model trained with result: {result}")
        # return result

    @task
    def save_model(self, result):
        monitor.progress_signal.emit("Saving model...")  # Emit progress update
        with open("model.txt", "w") as f:
            f.write(str(result))
        monitor.progress_signal.emit("Model saved to 'model.txt'.")