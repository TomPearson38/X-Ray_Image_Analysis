import os
import random
from PySide6.QtCore import Signal, QThread
import cv2
import numpy as np
from ultralytics import YOLO
from helpers import file_helpers
from data_classes.model_info import ModelInfo


class TestModelStage(QThread):
    model_testing_text_signal = Signal(str)
    model_testing_progress_bar_signal = Signal(int)

    def __init__(self, model_info: ModelInfo, path_to_images, path_to_labels, path_to_all_images, path_to_models):
        """Tests the model and creates statistics for comparison."""
        super().__init__()
        self.model_info = model_info
        self.path_to_images = path_to_images
        self.path_to_labels = path_to_labels
        self.path_to_models = path_to_models

        self.path_to_train_images = os.path.join(path_to_images, "train")
        self.path_to_val_images = os.path.join(path_to_images, "val")

        self.train_image_count = file_helpers.count_image_files_in_directory(self.path_to_train_images)
        self.val_image_count = file_helpers.count_image_files_in_directory(self.path_to_val_images)

        self.selected_training_images = self.select_random_images(self.path_to_train_images, 20)
        self.selected_val_images = self.select_random_images(self.path_to_val_images, 20)
        self.selected_all_images = self.select_random_images(path_to_all_images, 5)

        self.selected_test_images = []
        self.selected_test_images.extend(self.selected_training_images)
        self.selected_test_images.extend(self.selected_val_images)
        self.selected_test_images.extend(self.selected_all_images)

        self.selected_test_annotation = []
        for img in self.selected_test_images:
            self.selected_test_annotation.append(file_helpers.get_annotation_for_image(img, self.path_to_labels))

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
            matched, total = self.compare_annotations(rotated_original_boxes, rotated_boxes, 0.3)
            total_match += matched
            total_number += total

            self.model_testing_text_signal.emit(f"Metamorphic Test (Iteration "
                                                f"{iteration_num}/{len(self.selected_test_images)}) - Matched "
                                                f"{matched}/{total}.")
            iteration_num += 1
            self.model_testing_progress_bar_signal.emit(int(iteration_num / len(self.selected_test_images) * 33))

        if total_number == 0:
            final_result = "0% Matched. No bounding boxes were found in test data."
        else:
            final_result = f"{(total_match / total_number) * 100}% Matched out of {total_number} Total"

        self.model_info.metamorphic_test_result = final_result

        self.model_testing_text_signal.emit(f"Metamorphic Test Finished, FINAL RESULT - {final_result} ")

    def differential_tests(self):
        """ Compares current model's mean precision to previous models. """
        previous_model_path = self.model_info.starting_model
        if previous_model_path == "":
            previous_model_path = file_helpers.get_model_for_comparison(self.path_to_models)

        # No previous models
        if previous_model_path == "":
            # Emit a status update
            result_string = "No previous model found. Passing Test."
            self.model_info.differential_test_result = result_string
            self.model_testing_text_signal.emit(f"Differential Testing - {result_string} ")
            self.model_testing_progress_bar_signal.emit(66)
            return

        current_model = YOLO(self.model_info.get_best_pt_path())
        previous_model = YOLO(previous_model_path)

        total_correct_bounding_boxes = 0
        current_model_performance = 0
        previous_model_performance = 0

        length_of_selected_images = len(self.selected_test_images)

        # Compare performance for each model, to the correct bounding boxes for the image.
        for index in range(0, length_of_selected_images):
            current_image = self.selected_test_images[index]
            current_annotation = self.selected_test_annotation[index]

            # Loads correct bounding boxes
            correct_bounding_boxes = []
            with open(current_annotation, "r") as f:
                for line in f.readlines():
                    stripped_line = line.strip()
                    class_id, x_center, y_center, box_w, box_h = map(float, stripped_line.split())
                    correct_bounding_boxes.append([class_id, x_center, y_center, box_w, box_h])
            total_correct_bounding_boxes += len(correct_bounding_boxes)

            # Calculates new model's bounding boxes
            current_model_results = current_model(current_image)
            current_model_bounding_boxes = []
            for box in current_model_results[0].boxes:
                x_center, y_center, w, h = box.xywhn[0].tolist()
                current_model_bounding_boxes.append([0, x_center, y_center, w, h])

            # Calculates previous model's bounding boxes
            previous_model_results = previous_model(current_image)
            previous_model_bounding_boxes = []
            for box in previous_model_results[0].boxes:
                x_center, y_center, w, h = box.xywhn[0].tolist()
                previous_model_bounding_boxes.append([0, x_center, y_center, w, h])

            # Adds the matching bounding boxes between the true value and the model's predicted values
            current_model_performance += self.compare_annotations(current_model_bounding_boxes,
                                                                  correct_bounding_boxes, 0.5)[0]

            previous_model_performance += self.compare_annotations(previous_model_bounding_boxes,
                                                                   correct_bounding_boxes, 0.5)[0]

            # Emit a status update
            self.model_testing_text_signal.emit("Differential Testing - Calculated "
                                                f"{index + 1}/{length_of_selected_images}")
            self.model_testing_progress_bar_signal.emit(int(index / length_of_selected_images * 33) + 33)

        if total_correct_bounding_boxes == 0:
            percentage_current_correct = 0
            percentage_previous_correct = 0
        else:
            percentage_current_correct = current_model_performance / total_correct_bounding_boxes
            percentage_previous_correct = previous_model_performance / total_correct_bounding_boxes

        # Difference can be positive (improved) or negative (degraded)
        difference = (percentage_current_correct - percentage_previous_correct) * 100

        result_string = (f"Change in precision of {difference}%"
                         f" since previous model, based on {length_of_selected_images}"
                         " images.")

        self.model_info.differential_test_result = result_string

        self.model_testing_text_signal.emit(f"Differential Testing Finished, FINAL RESULT - {result_string}")
        self.model_testing_progress_bar_signal.emit(66)

    def fuzzing_tests(self):
        """ Generates random and unexpected inputs for the system. The primary goal is to identify issues
            such as program crashes, memory corruption and other vulnerabilities. """

        model = YOLO(self.model_info.get_best_pt_path())
        num_passes = 0
        num_fails = 0
        total_num = len(self.selected_test_images)

        for index in range(0, total_num):
            try:
                test_img_path = self.selected_test_images[index]
                test_img = cv2.imread(test_img_path)

                # Swap the colour channels
                channels = list(cv2.split(test_img))
                random.shuffle(channels)
                test_img = cv2.merge(channels)

                # Add gaussian noise
                random_gaussian_noise = np.random.normal(0, 25, test_img.shape).astype(np.uint8)
                test_img = cv2.add(test_img, random_gaussian_noise)

                # Add occlusion
                h, w = test_img.shape[:2]
                x1 = random.randint(0, w // 2)
                y1 = random.randint(0, h // 2)
                x2 = x1 + random.randint(10, w // 2)
                y2 = y1 + random.randint(10, h // 2)
                cv2.rectangle(test_img, (x1, y1), (x2, y2), (0, 0, 0), -1)

                # Test the corrupted image with the model.
                model(test_img)

                # If an exception was not thrown, it has passed.
                num_passes += 1
                self.model_testing_text_signal.emit(f"Fuzzing Testing - Test {index + 1}/{total_num} Passed.")
            except Exception:
                # Exception has been thrown so the test must have failed.
                num_fails += 1
                self.model_testing_text_signal.emit(f"Fuzzing Testing - Test {index}/{total_num} Failed.")

            self.model_testing_progress_bar_signal.emit(int(int(index / total_num * 33) + 66))

        percentage_passed = (num_passes / total_num) * 100
        result_string = f"{percentage_passed}% Passed out of {total_num} Images."

        self.model_testing_text_signal.emit(f"Fuzzing Testing Finished, FINAL RESULT - {result_string}")
        self.model_testing_progress_bar_signal.emit(100)

        self.model_info.fuzzing_test_result = result_string

    def select_random_images(self, image_dir, percentage=5):
        """ Selects a provided percentage of images from the provided DIR. """
        all_files = [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
            if f != '.gitignore'
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

    def compare_annotations(self, boxes1, boxes2, intersection_over_union_percentage=0.5):
        """ Compares to see if any annotations match. """
        matched = 0
        for original_box in boxes1:
            for rotated_box in boxes2:
                # If the IoU is over the threshold of 0.1
                if self.intersection_over_union(original_box, rotated_box) >= intersection_over_union_percentage:
                    matched += 1
                    break

        return matched, len(boxes1)
