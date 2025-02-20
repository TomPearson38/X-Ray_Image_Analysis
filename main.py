import signal
import sys
import ctypes
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
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
        self.train_ai_tab =  TrainAiTab()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.analyse_image_tab, "Analyse Image")
        self.tabs.addTab(self.view_models_tab, "View Models")
        self.tabs.addTab(self.train_ai_tab, "Train AI")

        # central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # styling
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E3440; 
                color: #D8DEE9;
            }

            /* tab widget and tabs */
            QTabWidget::pane {
                border: 1px solid #4C566A;
                background: #3B4252;
            }
            QTabBar::tab {
                background: #4C566A;
                color: #ECEFF4;
                padding: 8px;
                margin: 2px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #5E81AC;
                color: #ECEFF4;
            }
            QTabBar::tab:hover {
                background: #81A1C1;
                color: #ECEFF4;
            }
                           
            QLabel {
                color: #D8DEE9;
            }
                           
            QPushButton {
                background: #4C566A;
                color: #ECEFF4;
                padding: 8px;
                margin: 2px;
                border-radius: 5px;
            }
            QPushButton::hover {
                background: #81A1C1;
                color: #ECEFF4;
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
    
    #Logo Setting
    app.setWindowIcon(QIcon("Logo.ico"))
    myappid = 'amrc.x-ray-image-analysis' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    window = MainWindow()
    window.showNormal()
    sys.exit(app.exec())
