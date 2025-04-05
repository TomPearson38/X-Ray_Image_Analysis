import shutil
from PySide6.QtWidgets import QFileDialog
import os


def browse_file(self, opendir, fileConstraints):
    file_path, _ = QFileDialog.getOpenFileName(self, "Select a File", opendir, fileConstraints)
    if file_path:
        return file_path
    else:
        return ""


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted")
    else:
        print("The file does not exist")


def create_valid_data_file_name(source, img_folder, txt_folder):
    if not os.path.exists(source):
        print("Source file does not exist.")
        return

    filename = os.path.basename(source)
    name, ext = os.path.splitext(filename)
    dest_path = os.path.join(img_folder, filename)

    new_filename = name
    new_filename_including_ext = f"{name}{ext}"
    counter = 1
    while (os.path.exists(dest_path) or os.path.exists(os.path.join(txt_folder, new_filename + ".txt"))):
        new_filename = f"{name}({counter})"
        new_filename_including_ext = new_filename + ext
        dest_path = os.path.join(img_folder, new_filename_including_ext)
        counter += 1

    return dest_path, new_filename_including_ext


def move_file(source_path, destination_path):
    if os.path.exists(destination_path):
        print("File exists already!")
        return

    shutil.copy(source_path, destination_path)


def read_config_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            paths = [line.strip() for line in file if line.strip()]  # Remove empty lines
        return paths
    return []


def add_new_img(file_path, new_img):
    try:
        with open(file_path, "r+", encoding="utf-8") as file:
            lines = file.readlines()

            for i, line in enumerate(lines):
                if line.strip() == "":  # Found a blank line
                    lines[i] = new_img + "\n"
                    break
            else:
                # No blank line found, append at the end
                lines.append(new_img + "\n")

            # Move cursor to the beginning and write updated content
            file.seek(0)
            file.writelines(lines)
            file.truncate()  # Ensure no extra old content remains
    except Exception as e:
        print(f"Error: {e}")


def create_file_empty_txt(file_path):
    if os.path.exists(file_path):
        return False

    with open(file_path, 'w') as file:
        file.write("")

    return True


def update_config(file_path, new_config):
    if os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(new_config)
    else:
        return False
