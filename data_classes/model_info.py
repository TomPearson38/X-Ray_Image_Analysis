import json
import os


class ModelInfo:
    """Class to represent a configuration object."""
    def __init__(self, name, model, date_time_trained, number_of_images, path="", epoch="",
                 box_loss="", cls_loss="", mAP_50="", mAP_50_95="", precision="", recall=""):
        self.name = name
        self.model = model
        self.date_time_trained = date_time_trained
        self.number_of_images = number_of_images
        self.path = path
        self.epoch = epoch
        self.box_loss = box_loss
        self.cls_loss = cls_loss
        self.mAP_50 = mAP_50
        self.mAP_50_95 = mAP_50_95
        self.precision = precision
        self.recall = recall

    @classmethod
    def fromPath(cls, file_path):
        """Alternative constructor: Load config from a JSON file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Info file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return cls(**data)  # Create a Config instance from JSON data

    def to_dict(self):
        return {
            "name": self.name,
            "model": self.model,
            "date_time_trained": self.date_time_trained,
            "number_of_images": self.number_of_images,
            "path": self.path,
            "epoch": self.epoch,
            "box_loss": self.box_loss,
            "cls_loss": self.cls_loss,
            "mAP_50": self.mAP_50,
            "mAP_50_95": self.mAP_50_95,
            "precision": self.precision,
            "recall": self.recall,
        }

    def save_to_json(self):
        """Saves the configuration to a JSON file at the given folder path."""
        os.makedirs(self.path, exist_ok=True)  # Ensure the folder exists
        file_path = os.path.join(self.path, "info.json")

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.to_dict(), file, indent=4)  # Save with indentation for readability

        print(f"Configuration saved to {file_path}")
