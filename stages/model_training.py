import os
import pandas as pd
import torch
import yaml
import datetime
import shutil
from ultralytics import YOLO


def create_yaml(data_dir, output_path, class_names):
    """
    Create a dataset YAML file for YOLOv5 training.

    Args:
        data_dir (str): Path to the dataset directory containing 'images' and 'labels' subdirectories.
        output_path (str): Path to save the YAML file.
        class_names (list): List of class names.
    """
    yaml_data = {
        "train": os.path.join(data_dir, "images/train"),
        "val": os.path.join(data_dir, "images/val"),
        "nc": len(class_names),
        "names": class_names
    }

    with open(output_path, 'w') as file:
        yaml.dump(yaml_data, file)

    print(f"YAML file saved at: {output_path}")


def train_yolo(data_yaml, output_root, model_info, weights="yolov5s.pt", img_size=640, batch_size=16, epochs=50):
    """
    Train a YOLOv5 model with the specified parameters.

    Args:
        data_yaml (str): Path to the dataset YAML file.
        weights (str): Pretrained weights to use (e.g., 'yolov5s.pt').
        img_size (int): Image size for training (e.g., 640).
        batch_size (int): Batch size for training.
        epochs (int): Number of epochs to train.
        output_root (str): Root directory where trained models should be saved

    :return: Path to created model
    :rtype: str
    """
    training_start = datetime.datetime.now()
    timestamp = training_start.strftime("%Y%m%d_%H%M%S")
    model_dir = os.path.join(output_root, f"model_{timestamp}")
    os.makedirs(model_dir, exist_ok=True)

    print(f"Saving model artifacts in: {model_dir}")

    # Check if CUDA (GPU) is available and set the device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Training on {device.upper()}...")

    model = YOLO(weights)

    # Train the model
    model.train(
        data=data_yaml,
        imgsz=img_size,
        batch=batch_size,
        epochs=epochs,
        cache=True,
        device=device
    )

    runs_dir = "runs/detect"  # Location YOLO saves trained models
    latest_run = sorted(os.listdir(runs_dir))[-1]  # Get the latest training run
    best_model_path = os.path.join(runs_dir, latest_run)

    # Move contents to new location
    for item in os.listdir(best_model_path):
        shutil.move(os.path.join(best_model_path, item), model_dir)

    # Remove old file
    shutil.rmtree(best_model_path)
    results_df = (pd.read_csv(os.path.join(model_dir, "results.csv"))).iloc[-1].to_dict()

    model_info.path = model_dir
    model_info.date_time_trained = training_start.strftime("%Y-%m-%d__%H:%M:%S")
    model_info.recall = results_df["metrics/recall(B)"]
    model_info.precision = results_df["metrics/precision(B)"]
    model_info.epoch = results_df["epoch"]
    model_info.box_loss = results_df["train/box_loss"]
    model_info.cls_loss = results_df["train/cls_loss"]
    model_info.mAP_50 = results_df["metrics/mAP50(B)"]
    model_info.mAP_50_95 = results_df["metrics/mAP50-95(B)"]

    model_info.save_to_json()

    print(f"Model saved at: {model_dir}")

    return model_dir  # Return the directory where the model was saved
