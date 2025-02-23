import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from PySide6.QtWidgets import QApplication, QLabel
from unittest.mock import patch
from PySide6.QtCore import Qt
from main import MainWindow

@pytest.fixture
def app(qtbot):
    test_app = MainWindow()
    qtbot.addWidget(test_app)
    return test_app

def test_pipeline_creation(app:MainWindow, qtbot):
    app.tabs.setCurrentIndex(2)
    app.train_ai_tab.AINameInput.setText("Example Name")
    app.train_ai_tab.start_ai_train()
    qtbot.wait(500)
    assert app.train_ai_tab.pipeline is not None