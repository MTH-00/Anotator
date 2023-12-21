class AnnotationHandler:
    def __init__(self, image_annotation_tool):
        self.image_annotation_tool = image_annotation_tool
        self.annotations_history = []  # List to store annotation history for each version
        self.box_counter = 1  # Counter for box numbers

    def add_annotation(self, box, label):
        # Save the annotation in the history
        self.annotations_history.append((box, label))
        self.box_counter += 1

    def save_annotations(self):
        if self.image_annotation_tool.rect_id:
            x1, y1, x2, y2 = self.image_annotation_tool.canvas.coords(self.image_annotation_tool.rect_id)
            image_coords = (x1, y1, x2, y2)
            selected_class = self.image_annotation_tool.ClassSelector.combobox_class.get()

            # Save the annotation in the history
            self.annotations_history.append((image_coords, selected_class))

            # Save bounding box information for the current image
            if self.image_annotation_tool.image_path:
                self.image_annotation_tool.bounding_box_saver.save_bounding_boxes(
                    self.image_annotation_tool.image_path, self.annotations_history
                )
            self.image_annotation_tool.AnnotationEditor.update_list()
            print(f"Annotations saved for class '{selected_class}'.")

    def clear_annotations(self):
        # Clear existing annotations
        self.annotations_history = []
        self.box_counter = 1