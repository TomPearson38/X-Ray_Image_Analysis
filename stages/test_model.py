import os
import random
from PySide6.QtCore import Signal, QThread
import cv2
from ultralytics import YOLO
from helpers import file_helpers
from data_classes.model_info import ModelInfo


class TestModelStage(QThread):
    model_testing_text_signal = Signal(str)
    model_testing_progress_bar_signal = Signal(int)

    def __init__(self, model_info: ModelInfo, path_to_images, path_to_labels, path_to_all_images):
        """Tests the model and creates statistics for comparison."""
        super().__init__()
        self.model_info = model_info
        self.path_to_images = path_to_images
        self.path_to_labels = path_to_labels

        self.path_to_train_images = os.path.join(path_to_images, "train")
        self.path_to_val_images = os.path.join(path_to_images, "val")

        self.path_to_train_labels = os.path.join(path_to_labels, "train")
        self.path_to_val_labels = os.path.join(path_to_labels, "val")

        self.train_image_count = file_helpers.count_image_files_in_directory(self.path_to_train_images)
        self.val_image_count = file_helpers.count_image_files_in_directory(self.path_to_val_images)

        self.selected_training_images = self.select_random_images(self.path_to_train_images, 5)
        self.selected_val_images = self.select_random_images(self.path_to_val_images, 5)
        self.selected_all_images = self.select_random_images(path_to_all_images, 1)

        self.selected_test_images = []
        self.selected_test_images.extend(self.selected_training_images)
        self.selected_test_images.extend(self.selected_val_images)
        self.selected_test_images.extend(self.selected_all_images)

    def run(self):
        self.metamorphic_tests()
        self.differential_tests()
        self.fuzzing_tests()

        self.model_info.save_to_json()

    def metamorphic_tests(self):
        """ Tests a model's ability to handle different variations of input data with
            the same metamorphic properties.
            This function tests if the model identifies the same bounding boxes for images before
            and after they are rotated. """
        # Setup worker and thread
        model = YOLO(self.model_info.get_best_pt_path())

        # Init values
        total_match = 0
        total_number = 0
        iteration_num = 1

        # Iterate through all test images
        for file in self.selected_test_images:
            image = cv2.imread(file)
            rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

            # Compute bounding boxes for the original image
            original_results = model(file)
            original_boxes = []

            for box in original_results[0].boxes:
                x_center, y_center, w, h = box.xywhn[0].tolist()
                original_boxes.append([0, x_center, y_center, w, h])

            # Rotate the bounding boxes for comparison to the rotated image's bounding boxes
            rotated_original_boxes = self.rotate_annotations_by_90(original_boxes)

            # Compute bounding boxes for rotated images
            rotated_results = model(rotated_image)
            rotated_boxes = []

            for box in rotated_results[0].boxes:
                x_center, y_center, w, h = box.xywhn[0].tolist()
                rotated_boxes.append([0, x_center, y_center, w, h])

            # Compare bounding boxes
            matched, total = self.compare_annotations(rotated_original_boxes, rotated_boxes)
            total_match += matched
            total_number += total

            self.model_testing_text_signal.emit(f"Metamorphic Test (Iteration "
                                                f"{iteration_num}/{len(self.selected_test_images)}) - Matched "
                                                f"{matched}/{total}.")
            iteration_num += 1
            self.model_testing_progress_bar_signal.emit(int(iteration_num / len(self.selected_test_images) * 33))

        final_result = f"{(total_match / total_number) * 100}% Matched out of {total_number} Total"

        self.model_info.metamorphic_test_result = final_result

        self.model_testing_text_signal.emit(f"Metamorphic Test Finished, FINAL RESULT - {final_result} ")

    def differential_tests(self):
        pass

    def fuzzing_tests(self):
        pass

    def select_random_images(self, image_dir, percentage=5):
        """ Selects a provided percentage of images from the provided DIR. """
        all_files = [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
        ]

        total = len(all_files)
        count = max(1, int(total * (percentage / 100)))  # at least 1 image
        selected = random.sample(all_files, count)
        return selected

    def rotate_annotations_by_90(self, boxes):
        """ Rotates the annotations by 90 degrees clockwise """
        rotated = []

        for box in boxes:
            class_id, x, y, bw, bh = box
            new_x = 1 - y
            new_y = x
            new_bw = bh
            new_bh = bw

            rotated.append([class_id, new_x, new_y, new_bw, new_bh])

        return rotated

    def intersection_over_union(self, box1, box2):
        """ Calculates if the predicted bounding boxes overlap. """
        # Turning the yolo coordinates into normal box coordinates with
        # each var being a corner of the box

        x1_min = box1[1] - box1[3] / 2
        y1_min = box1[2] - box1[4] / 2
        x1_max = box1[1] + box1[3] / 2
        y1_max = box1[2] + box1[4] / 2

        x2_min = box2[1] - box2[3] / 2
        y2_min = box2[2] - box2[4] / 2
        x2_max = box2[1] + box2[3] / 2
        y2_max = box2[2] + box2[4] / 2

        # Find the intersection points between the boxes
        inter_x1 = max(x1_min, x2_min)  # Left edge
        inter_y1 = max(y1_min, y2_min)  # Top edge
        inter_x2 = min(x1_max, x2_max)  # Right edge
        inter_y2 = min(y1_max, y2_max)  # Bottom edge

        # Calculate the width and height of the overlap.
        # If the length is negative, it is discarded.
        inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

        # Compute the area of each box
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)

        # Compute IoU
        union = box1_area + box2_area - inter_area

        return inter_area / union if union else 0

    def compare_annotations(self, original_boxes, rotated_boxes):
        """ Compares to see if any annotations match. """
        matched = 0
        for original_box in original_boxes:
            for rotated_box in rotated_boxes:
                # If the IoU is over the threshold of 0.1
                if self.intersection_over_union(original_box, rotated_box) >= 0.3:
                    matched += 1
                    break

        return matched, len(original_boxes)
