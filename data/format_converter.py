import os
import numpy as np
from PIL import Image


def convert_gt_to_yolo(gt_file, images_dir, output_dir, class_id=0):
    """
    Converts a ground truth file to YOLOv5 format.

    Args:
        gt_file (str): Path to the `ground_truth.txt` file.
        images_dir (str): Directory containing the images.
        output_dir (str): Directory to save YOLOv5 annotations.
        class_id (int): YOLO class ID to assign to all annotations (default is 0).
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load ground truth data
    gt_data = np.loadtxt(gt_file)

    # Iterate over all images in the directory
    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    processed_images = set()

    for image_file in image_files:
        image_id = int(image_file.split('_')[1].split('.')[0])  # Extract image ID from the file name
        image_path = os.path.join(images_dir, image_file)

        # Get image dimensions
        with Image.open(image_path) as img:
            img_width, img_height = img.size

        # Find annotations for the current image
        if image_id in gt_data[:, 0]:
            image_annotations = gt_data[gt_data[:, 0] == image_id][:, 1:]
            yolo_lines = []

            # Convert annotations to YOLO format
            for bbox in image_annotations:
                x_min, x_max, y_min, y_max = bbox
                x_center = (x_min + x_max) / 2 / img_width
                y_center = (y_min + y_max) / 2 / img_height
                norm_width = (x_max - x_min) / img_width
                norm_height = (y_max - y_min) / img_height

                yolo_lines.append(f"{class_id} {x_center} {y_center} {norm_width} {norm_height}")

            # Save YOLO annotations
            yolo_file_name = os.path.splitext(image_file)[0] + '.txt'
            yolo_file_path = os.path.join(output_dir, yolo_file_name)
            with open(yolo_file_path, 'w') as yolo_file:
                yolo_file.write('\n'.join(yolo_lines))
            print(f"Saved YOLO annotations for {image_file}.")
        else:
            # Create an empty label file for defect-free images
            yolo_file_name = os.path.splitext(image_file)[0] + '.txt'
            yolo_file_path = os.path.join(output_dir, yolo_file_name)
            open(yolo_file_path, 'w').close()  # Create an empty file
            print(f"No bounding boxes found for {image_file}. Created an empty label file.")

        # Track processed images
        processed_images.add(image_id)

    # Check for unprocessed images (those without ground truth entries)
    unprocessed_images = [f for f in image_files if int(f.split('_')[1].split('.')[0]) not in processed_images]
    for image_file in unprocessed_images:
        # Create an empty label file for these images as well
        yolo_file_name = os.path.splitext(image_file)[0] + '.txt'
        yolo_file_path = os.path.join(output_dir, yolo_file_name)
        open(yolo_file_path, 'w').close()  # Create an empty file
        print(f"No ground truth entry found for {image_file}. Created an empty label file.")


# Example usage
if __name__ == "__main__":
    ground_truth_file = "C:/Users/tomap/Downloads/Castings/Castings/C0002/ground_truth.txt"
    images_directory = "C:/Users/tomap/Downloads/Castings/Castings/C0002/"
    output_directory = "D:/Other computers/My PC/UniYear3/Dissertation/Code/X-Ray_Image_Analysis/data/labels"

    # Assuming all defects belong to class ID 0 for YOLO
    convert_gt_to_yolo(ground_truth_file, images_directory, output_directory, class_id=0)
