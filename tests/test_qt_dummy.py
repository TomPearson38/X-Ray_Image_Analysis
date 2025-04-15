# tests/test_qt_dummy.py
def test_dummy_qt(qtbot):
    from PySide6.QtWidgets import QLabel
    label = QLabel("hello")
    qtbot.addWidget(label)
    assert label.text() == "hello"
