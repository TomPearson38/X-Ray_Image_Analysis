from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ViewModelsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("View Models"))
        layout.addWidget(QLabel(""))
        self.setLayout(layout)
