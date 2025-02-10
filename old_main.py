from prefect import task, flow
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QObject, Signal
import sys
import stages.model_training

# Signal Monitor class to monitor progress to GUI
class PrefectMonitor(QObject):
    progress_signal = Signal(str)  # Signal to send task updates to the GUI

monitor = PrefectMonitor()  # Instantiate the monitor

# Prefect tasks
@task
def prepare_data():
    monitor.progress_signal.emit("Preparing data...") 
    return [1, 2, 3, 4, 5]

@task
def train_model(data):
    data_dir = "D:/Other computers/My PC/UniYear3/Dissertation/Code/X-Ray_Image_Analysis/data"  # Path to the dataset directory
    class_names = ["0"]  # List of class names, only 1 flaw
    output_yaml = "dataset.yaml"  # Path to save the YAML file
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

    monitor.progress_signal.emit(f"Model trained with result: {result}")
    return result

@task
def save_model(result):
    monitor.progress_signal.emit("Saving model...")  # Emit progress update
    with open("model.txt", "w") as f:
        f.write(str(result))
    monitor.progress_signal.emit("Model saved to 'model.txt'.")

# Define the flow using @flow decorator
@flow(name="PyQt Integrated Pipeline")
def pipeline_flow():
    data = prepare_data()
    result = train_model(data)
    save_model(result)

# Define PyQt GUI
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pipeline Monitor")
        self.setGeometry(100, 100, 600, 400)

        # aMin layout
        layout = QVBoxLayout()

        # Log area for showing progress
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # Start button to run the pipeline
        self.start_button = QPushButton("Start Pipeline")
        self.start_button.clicked.connect(self.run_pipeline)
        layout.addWidget(self.start_button)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_log(self, message):
        """Append log messages to the text area."""
        self.log_area.append(message)

    def run_pipeline(self):
        """Run the Prefect pipeline and update the GUI."""
        monitor.progress_signal.connect(self.update_log)  # Connect the signal to the log update method
        pipeline_flow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
