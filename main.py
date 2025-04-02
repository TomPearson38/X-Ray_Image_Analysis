import os
import signal
import sys
import ctypes
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon

from ui_tabs.analyse_image_tab import AnalyseImageTab
from ui_tabs.dataset_config_tab import DatasetConfigTab
from ui_tabs.train_ai_tab import TrainAiTab
from ui_tabs.view_models_tab import ViewModelsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("X-Ray Image Analysis")
        self.setGeometry(200, 200, 600, 400)

        self.analyse_image_tab = AnalyseImageTab()
        self.view_models_tab = ViewModelsTab()
        self.train_ai_tab = TrainAiTab()
        self.training_data_tab = DatasetConfigTab()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.analyse_image_tab, "Analyse Image")
        self.tabs.addTab(self.view_models_tab, "View Models")
        self.tabs.addTab(self.train_ai_tab, "Train AI")
        self.tabs.addTab(self.training_data_tab, "Training Data")
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # styling
        self.apply_styles()

    def on_tab_changed(self, index):
        if index == 1:
            self.view_models_tab.update_models()

    def resizeEvent(self, event):
        """Adjust the column count dynamically when the window resizes."""
        new_columns = max(1, self.width() // 200)  # Adjust column width threshold (200px per column)
        self.training_data_tab.set_column_count(new_columns)
        return super().resizeEvent(event)

    def apply_styles(self):
        """Load QSS stylesheet and apply it to the app."""
        style_path = os.path.join("helpers", "style.qss")
        with open(style_path, "r") as file:
            self.setStyleSheet(file.read())


# TODO: Need to fix functionality for closing window. Ensure all threads terminate correctly.
def handle_sigint(signal_received, frame):
    """ Handle Ctrl+C """
    print("Ctrl+C detected, exiting...")
    app.quit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)  # CTRL C exit condition
    app = QApplication(sys.argv)

    # Logo Setting
    app.setWindowIcon(QIcon("Logo.ico"))
    myappid = 'amrc.x-ray-image-analysis'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    window = MainWindow()
    window.showNormal()
    sys.exit(app.exec())
