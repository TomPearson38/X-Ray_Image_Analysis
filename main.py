import signal
import sys
import ctypes
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon

from ui_tabs.analyse_image_tab import AnalyseImageTab
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
        self.tabs = QTabWidget()
        self.tabs.addTab(self.analyse_image_tab, "Analyse Image")
        self.tabs.addTab(self.view_models_tab, "View Models")
        self.tabs.addTab(self.train_ai_tab, "Train AI")
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

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
                color: #05f3ff;
                font-size: 25px;
            }

            /* tab widget and tabs */
            QTabWidget::pane {
                border: 1px solid #333333;
                background: #252525;
            }
            QTabBar::tab {
                background: #333333;
                color: #05f3ff;
                padding: 8px;
                margin: 2px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #555555;
                color: #05f3ff;
            }
            QTabBar::tab:hover {
                background: #777777;
                color: #05f3ff;
            }

            /* Config List Widget */
            QListWidget {
                background-color: #252525;
                border: 1px solid #333333;
                color: #05f3ff;
                font-size: 14px;
                padding: 4px;
            }
            QListWidget::item {
                background-color: #333333;
                padding: 8px;
                margin: 2px;
                border-radius: 1px;
            }
            QListWidget::item:selected {
                background-color: #555555;
                color: #05f3ff;
                border: none;
                outline: none;
            }
            QListWidget::item:hover {
                background-color: #777777;
                color: #05f3ff;
            }
            QListWidget::item:focus {
                outline: none;
                border: none;
            }

            QLabel {
                color: #05f3ff;
            }

            QPushButton {
                background: #333333;
                color: #05f3ff;
                padding: 8px;
                margin: 2px;
                border-radius: 5px;
            }
            QPushButton::hover {
                background: #777777;
                color: #05f3ff;
            }

            QLineEdit {
                background-color: #252525;
                color: #05f3ff;
                border: 1px solid #05f3ff;
                padding: 6px;
                border-radius: 5px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 1px solid #05f3ff;
                outline: none;
            }

            QComboBox {
                background-color: #252525;
                color: #05f3ff;
                border: 1px solid #05f3ff;
                padding: 6px;
                border-radius: 5px;
                font-size: 14px;
            }

            QComboBox:focus {
                border: 1px solid #05f3ff;
                outline: none;
            }

            QComboBox::drop-down {
                background-color: #252525;
                border: 1px solid #05f3ff;
                width: 20px;
            }

            QComboBox::item {
                background-color: #252525;
                color: #05f3ff;
                padding: 6px;
            }

            QComboBox::item:selected {
                background-color: #05f3ff;
                color: #252525;
            }
        """)


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
