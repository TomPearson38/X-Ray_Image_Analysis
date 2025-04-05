import gc
import os
from PySide6.QtCore import Signal, QThread
import sys
import torch
from helpers import file_helpers
from helpers.console_output import CaptureConsoleOutputThread
import stages.model_training
from data_classes.model_info import ModelInfo


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

    def __init__(self, parent, model_info: ModelInfo):
        QThread.__init__(self, parent)
        self._is_running = True
        self.model_info = model_info
        self.data_dir = os.path.abspath("data")  # Path to the dataset directory
        self.train_data_dir = os.path.join(self.data_dir, "images")
        self.train_labels_dir = os.path.join(self.data_dir, "labels")

        data_dir = os.path.abspath("stored_training_images")
        self.dataset_config_dir = os.path.join(data_dir, "datasets")
        self.image_dir = os.path.join(data_dir, "images", "raw")
        self.annotation_dir = os.path.join(data_dir, "labels", "raw")

    def run(self):
        self.pipeline_flow()

    def stop(self):
        self._is_running = False

    def pipeline_flow(self):
        """
        Defines the pipeline using flow. Each stage is executed sequentially.
        Using results from previous stages.
        """

        self.pipeline_started.emit(True)
        if self._is_running:
            self.prepare_data()
            result = self.train_model()

        if result and self._is_running:
            self.test_model(result)
        self.pipeline_finished.emit()

    def prepare_data(self):
        """Augments the data to improve the performance of the model training."""
        self.data_augmentation_text.emit("Resetting Data...")
        file_helpers.reset_training_data(self.train_data_dir, self.train_labels_dir)
        self.data_augmentation_progress_bar.emit(10)

        self.data_augmentation_text.emit("Loading Data...")
        all_img_path = [f for f in os.listdir(self.image_dir) if f.endswith(('.jpg', '.png'))]
        self.data_augmentation_progress_bar.emit(20)

        if (self.model_info.dataset_config != "All Images"):
            self.data_augmentation_text.emit("Config Found, Loading...")
            config_path = os.path.join(self.dataset_config_dir, self.model_info.dataset_config + ".txt")
            selected_files = file_helpers.read_config_file(config_path)
            filtered_img_list = [
                img for img in all_img_path
                if any(img.lower() in filename.lower()
                       for filename in selected_files)
            ]
            all_img_path = filtered_img_list

        self.data_augmentation_progress_bar.emit(80)
        self.data_augmentation_text.emit("Initialising Training Values...")
        file_helpers.load_training_images(all_img_path, self.image_dir, self.annotation_dir, self.data_dir)

        self.data_augmentation_progress_bar.emit(100)
        self.data_augmentation_text.emit("Data Loaded!")

    def train_model(self):
        """
        Uses the augmented data to create a trained model based on the parameters.
        """
        # TODO: Create a config file to store this information

        class_names = ["0"]  # List of class names, only 1 flaw, so only one class
        output_yaml = os.path.abspath("data/dataset_yaml/dataset.yaml")  # Path to save the YAML file

        if self.model_info.starting_model == "":
            weights = "yolov5s.pt"  # Pretrained weights to use
        else:
            weights = self.model_info.starting_model

        img_size = 640  # Image size for training
        batch_size = 16  # Batch size for training
        epochs = int(self.model_info.epoch)  # Number of epochs for training

        # Create YAML file for YOLO to use
        stages.model_training.create_yaml(self.data_dir, output_yaml, class_names)

        # Create an instance of the CaptureConsoleOutputThread to capture the YOLO output to print to the GUI.
        # TODO: Link this to a log file to store the information being created.
        self.console_thread = CaptureConsoleOutputThread()
        self.console_thread.output_written.connect(self.model_training_text)
        sys.stdout = self.console_thread  # Redirect stdout
        sys.stderr = self.console_thread  # Redirect stderr
        self.console_thread.start()

        # self.trainYoloThread = YoloThread(output_yaml, weights, img_size, batch_size, epochs, self.cleanup)

        stages.model_training.train_yolo(
            data_yaml=output_yaml,
            output_root=os.path.abspath("trained_models"),
            weights=weights,
            img_size=img_size,
            batch_size=batch_size,
            epochs=epochs,
            model_info=self.model_info
        )
        torch.cuda.empty_cache()
        torch._C._cuda_clearCublasWorkspaces()
        gc.collect()
        self.cleanup()

    def test_model(self, model_dir):
        """Tests the trained model against previous iterations, to produce a performance score."""
        # TODO: Implement model testing.
        pass

    def cleanup(self):
        if hasattr(self, 'console_thread'):
            self.console_thread.stop()
            self.console_thread.quit()
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    def exit_early(self):
        self.cleanup()
        if hasattr(self, 'trainYoloThread') and self.trainYoloThread._running:
            self.trainYoloThread.stop()
