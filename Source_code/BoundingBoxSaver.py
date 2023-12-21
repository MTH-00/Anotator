# BoundingBoxSaver.py

import os

class BoundingBoxSaver:
    def __init__(self, txt_folder="annotations_txt"):
        self.txt_folder = txt_folder

    def save_bounding_boxes(self, image_path, annotations):
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        txt_file_path = os.path.join(self.txt_folder, f"{image_name}_annotations.txt")

        # Ensure the directory exists
        os.makedirs(self.txt_folder, exist_ok=True)

        with open(txt_file_path, "a") as txt_file:
            txt_file.write(f"Version {len(annotations)}:\n")
            for i, (box, label) in enumerate(annotations):
                txt_file.write(f"Box {i + 1}: {box[0]} {box[1]} {box[2]} {box[3]} - Class: {label}\n")

        print(f"Bounding box history saved for {image_path} in {txt_file_path}.")
