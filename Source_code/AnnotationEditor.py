import tkinter as tk
import os

class AnnotationEditor:
    def __init__(self, image_annotation_tool):
        self.image_annotation_tool = image_annotation_tool
        self.annotation_handler = image_annotation_tool.annotation_handler

    def Annotation_list(self, frame):
        # Create a Listbox to display annotations
        self.listbox_annotations = tk.Listbox(frame, height=13)
        self.listbox_annotations.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox_annotations.bind("<ButtonRelease-1>", self.select_annotation)


        # Add a scrollbar to the Listbox
        scrollbar = tk.Scrollbar(frame, command=self.listbox_annotations.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_annotations.config(yscrollcommand=scrollbar.set)



    def update_list(self):
        # Clear existing items in the listbox
        self.listbox_annotations.delete(0, tk.END)

        # Get the image name without extension
        image_name = os.path.splitext(os.path.basename(self.image_annotation_tool.image_path))[0]

        # Construct the path to the annotations file
        txt_file_path = os.path.join("annotations_txt", f"{image_name}_annotations.txt")

        # Check if the file exists
        if os.path.exists(txt_file_path):
            # Read all lines from the annotations file
            with open(txt_file_path, "r") as txt_file:
                lines = txt_file.readlines()

            version_lines = [line for line in lines if line.startswith("Version")]

            # Find the last version line
            last_version_line = version_lines[-1] if version_lines else None

            if last_version_line:
                # Find the index of the last version line
                last_version_index = lines.index(last_version_line)

                # Extract the lines corresponding to the last version
                last_version_lines = lines[last_version_index+1:]

                # Iterate over the lines and add label + box number to the listbox
                for line in last_version_lines:
                    # Extract number after "Box" and text after "Class:"
                    box_parts = line.split("Box")
                    class_parts = line.split("- Class:")

                    if len(box_parts) == 2 and len(class_parts) == 2:
                        box_number = box_parts[1].split(":")[0].strip()
                        label = class_parts[1].strip()

                        # Combine label and box number and insert into the listbox
                        label_and_box = f"{label} {box_number}"
                        self.listbox_annotations.insert(tk.END, label_and_box)
                    else:
                        print(f"Invalid line format: {line.strip()}")

                print(f"Listbox updated with annotations from {txt_file_path}")
            else:
                print("No 'Version' line found in the annotations file.")
        else:
            print(f"Annotations file not found: {txt_file_path}")


    def select_annotation(self, event):
        selected_index = self.listbox_annotations.curselection()
        if selected_index:
            print(f"Selected annotation: {self.listbox_annotations.get(selected_index)}")

    def extract_num(self, text):
        # Find the index of "x"
        x_index = text.find("x")

        # Check if "x" is found in the text
        if x_index != -1:
            # Find the index of ":"
            colon_index = text.find(":", x_index)

            # Check if ":" is found after "x"
            if colon_index != -1:
                # Extract the number between 'x' and ':'
                number_between_x_and_colon = text[x_index + 1:colon_index].strip()
                print(number_between_x_and_colon)
            else:
                print("Colon ':' not found after 'x'")
        else:
            print("Letter 'x' not found in the text.")

    