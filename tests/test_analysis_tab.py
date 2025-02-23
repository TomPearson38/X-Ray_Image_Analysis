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

def test_select_ai_model(app: MainWindow):
    """Test select model QDialogue to ensure it selects a valid file."""
    
    mock_file_path = "C:/Users/Test/sample.pt"
    with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(mock_file_path, "PyTorch File (*.pt)")):
        
        app.analyse_image_tab.update_selected_model()
        result = app.analyse_image_tab.selectedModelLabel.text()

        assert result == ("..." + mock_file_path[-20:])

        assert app.analyse_image_tab.selectedAIModel == mock_file_path


def test_incorrect_select_ai_model(app: MainWindow):
    """Test that an invalid file extension is rejected."""
    invalid_file = "C:/Users/Test/image.png"

    with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(invalid_file, "All Files (*)")):
        app.analyse_image_tab.update_selected_model()
        result = app.analyse_image_tab.selectedModelLabel.text()

        assert result is ""

        assert app.analyse_image_tab.selectedAIModel is ""

def test_select_image(app: MainWindow):
    """Test select model QDialogue to ensure it selects a valid file."""
    
    mock_file_path = "C:/Users/Test/sample.png"
    with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(mock_file_path, "Images (*.png *.jpg)")):
        
        app.analyse_image_tab.update_selected_image()
        result = app.analyse_image_tab.selectedImageLabel.text()

        assert result == ("..." + mock_file_path[-20:])

        assert app.analyse_image_tab.selectedImage == mock_file_path


def test_incorrect_select_image(app: MainWindow):
    """Test that an invalid file extension is rejected."""
    invalid_file = "C:/Users/Test/image.pt"

    with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(invalid_file, "All Files (*)")):
        app.analyse_image_tab.update_selected_image()
        result = app.analyse_image_tab.selectedImageLabel.text()

        assert result is ""

        assert app.analyse_image_tab.selectedImage is ""
