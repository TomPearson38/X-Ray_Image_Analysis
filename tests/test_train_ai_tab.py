# TODO - This test passes locally and on github, but the cleanup causes it to fail the test overall on github,
# giving an incorrect conclusion about the test failing. Therefore it needs to be refactored to be re-implemented.

# import pytest
# import sys
# import os
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from main import MainWindow


# @pytest.fixture
# def app(qtbot):
#     test_app = MainWindow()
#     qtbot.addWidget(test_app)
#     return test_app


# def test_pipeline_creation(app: MainWindow, qtbot):
#     os.makedirs("data/dataset_yaml/", exist_ok=True)
#     app.tabs.setCurrentIndex(2)
#     app.train_ai_tab.AINameInput.setText("Example Name")
#     app.train_ai_tab.start_ai_train()
#     qtbot.wait(500)
#     assert app.train_ai_tab.trainInProgress is True
#     app.train_ai_tab.pipeline.exit_early()
#     app.train_ai_tab.pipeline.quit()
