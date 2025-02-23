import os
from prefect import task, flow
from PySide6.QtCore import Signal, QThread
import sys
from helpers.console_output import CaptureConsoleOutputThread
import stages.model_training


class MainTrainPipeline(QThread):
    """
    Creates the training pipeline thread.
    It augments the data, trains a model and evaluates/tests the produced model.
    """
    pipeline_started = Signal(bool)
    pipeline_finished = Signal()
    data_augmentation_text = Signal(str)
    data_augmentation_progress_bar = Signal(int)
    model_training_text = Signal(str)
    model_training_progress_bar = Signal(int)
    model_testing_text = Signal(str)
    model_testing_progress_bar = Signal(int)

    def __init__(self, parent):
        QThread.__init__(self, parent)
        self._is_running = True

    def run(self):
        self.pipeline_flow()

    def stop(self):
        self._is_running = False

    @flow(name="PyQt Integrated Pipeline")
    def pipeline_flow(self):
        """
        Defines the pipeline using flow. Each stage is executed sequentially.
        Using results from previous stages.
        """

        self.pipeline_started.emit(True)
        if self._is_running:
            data = self.prepare_data()

        if data and self._is_running:
            result = self.train_model(data)

        if result and self._is_running:
            self.test_model(result)
        self.pipeline_finished.emit()

    @task
    def prepare_data(self):
        """Augments the data to improve the performance of the model training."""

        self.data_augmentation_progress_bar.emit(100)
        self.data_augmentation_text.emit("Finished")
        return [1, 2, 3, 4, 5]  # TODO: Implement correct data augmentation.

    @task
    def train_model(self, data):
        """
        Uses the augmented data to create a trained model based on the parameters.
        """
        # TODO: Create a config file to store this information

        data_dir = os.path.abspath("data")  # Path to the dataset directory
        class_names = ["0"]  # List of class names, only 1 flaw, so only one class
        output_yaml = os.path.abspath("data/dataset_yaml/dataset.yaml")  # Path to save the YAML file
        weights = "yolov5s.pt"  # Pretrained weights to use
        img_size = 640  # Image size for training
        batch_size = 16  # Batch size for training
        epochs = 1  # Number of epochs for training

        # Create YAML file for YOLO to use
        stages.model_training.create_yaml(data_dir, output_yaml, class_names)

        # Create an instance of the CaptureConsoleOutputThread to capture the YOLO output to print to the GUI.
        # TODO: Link this to a log file to store the information being created.
        self.console_thread = CaptureConsoleOutputThread()
        self.console_thread.output_written.connect(self.model_training_text)
        sys.stdout = self.console_thread  # Redirect stdout
        sys.stderr = self.console_thread  # Redirect stderr
        self.console_thread.start()

        # Train the model
        stages.model_training.train_yolo(
            data_yaml=output_yaml,
            output_root=os.path.abspath("trained_models"),
            weights=weights,
            img_size=img_size,
            batch_size=batch_size,
            epochs=epochs
        )

        if self.console_thread:
            self.console_thread.stop()
            self.console_thread.quit()
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    @task
    def test_model(self, model_dir):
        """Tests the trained model against previous iterations, to produce a performance score."""
        # TODO: Implement model testing.
        pass
