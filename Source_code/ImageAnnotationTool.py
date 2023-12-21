from PIL import Image, ImageDraw, ImageTk, ImageColor, ImageFilter
import tkinter as tk
from tkinter import ttk, filedialog
import os
from BoundingBoxSaver import BoundingBoxSaver
from Buttons import Buttons
from ClassSelector import ClassSelector
from Image_navigator import ImageNavigator
from AnnotationHandler import AnnotationHandler
from AnnotationEditor import AnnotationEditor


class ImageAnnotationTool:
    def __init__(self, master):

        self.master = master
        self.master.title("Anotator")
        self.master.attributes('-topmost', False)
        self.master.state('zoomed')

        self.image_path = None         
        self.image_directory = None
        self.annotated_images_directory = "annotated_images"

        self.edit_mode = False  # Flag to track editing mode
        self.selected_box = None  # Index of the selected bounding box
        self.resizing_handle = None  # Handle for resizing (if any)
        self.BUTTON_WIDTH = 20

        # Initialize variables for bounding box creation
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.box_counter = 1  # Counter for box numbers

        # Create an instance classes:
        self.bounding_box_saver = BoundingBoxSaver()
        self.annotation_handler = AnnotationHandler(self)
        self.image_navigator    = ImageNavigator(self)
        self.ClassSelector      = ClassSelector(self)
        self.AnnotationEditor   = AnnotationEditor(self) 
       
        self.create_widgets()

        # Bind mouse events for bounding box creation
        self.canvas.bind("<ButtonPress-1>", self.on_click_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)


    def create_widgets(self):

        self.annotations_history = self.annotation_handler.annotations_history

        # Create a paned window for dividing the main window into two panes
        self.paned_window = tk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.paned_window.pack(expand=True, fill=tk.BOTH)

        # Create the left pane for chat history (image list)
        self.left_pane = tk.Frame(self.paned_window)
        self.paned_window.add(self.left_pane)

        # Create another paned window within the left pane
        self.left_paned_window = tk.PanedWindow(self.left_pane, orient=tk.VERTICAL)
        self.left_paned_window.pack(expand=True, fill=tk.BOTH)

        # Create the right pane for displaying images and annotations
        self.right_pane = tk.Frame(self.paned_window)
        self.paned_window.add(self.right_pane)

        # Create a Tkinter canvas for displaying the image
        self.canvas = tk.Canvas(self.right_pane)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        # Create the upper part of the left pane (you can customize this part)
        upper_left_frame = tk.Frame(self.left_paned_window)
        self.left_paned_window.add(upper_left_frame)

        # Create the middle part of the left pane
        middle_left_frame = tk.Frame(self.left_paned_window)
        self.left_paned_window.add(middle_left_frame)

        # Create the lower part of the left pane (you can customize this part)
        lower_left_frame = tk.Frame(self.left_paned_window)
        self.left_paned_window.add(lower_left_frame)

        Buttons.open_folder(self, lower_left_frame)
        Buttons.open_image(self, lower_left_frame)
        Buttons.Next_image(self,lower_left_frame)
        Buttons.save_annotated_image(self, lower_left_frame)
        Buttons.add_class(self, lower_left_frame)


        self.ClassSelector.menu(lower_left_frame)
        self.AnnotationEditor.Annotation_list(middle_left_frame)


        # Create a listbox for displaying image files in the selected directory
        self.listbox_images = tk.Listbox(upper_left_frame, height=13)
        self.listbox_images.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox_images.bind("<ButtonRelease-1>", self.load_selected_image)

        # Add a scrollbar to the listbox
        scrollbar = tk.Scrollbar(upper_left_frame, command=self.listbox_images.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_images.config(yscrollcommand=scrollbar.set)

        # Check and create the annotated images directory if it doesn't exist
        if not os.path.exists(self.annotated_images_directory):
            os.makedirs(self.annotated_images_directory)

    
    
    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_directory = folder_path
            self.listbox_images.delete(0, tk.END)
            image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            self.listbox_images.insert(tk.END, *image_files)

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.webp")])
        if file_path:
            self.image_path = file_path
            self.load_image()

    def load_image(self):
        try:
            if self.image_path:
                self.annotation_handler.annotations_history = []  # Reset annotation history when loading a new image
                self.box_counter = 1  # Reset box counter

                pil_image = Image.open(self.image_path)

                # Calculate scaling factors for width and height
                width_factor = self.canvas.winfo_width() / pil_image.width
                height_factor = self.canvas.winfo_height() / pil_image.height

                # Choose the minimum scaling factor to fit the image in the canvas
                scale_factor = min(width_factor, height_factor)

                # Resize the image
                resized_image = pil_image.resize(
                (int(pil_image.width * scale_factor), int(pil_image.height * scale_factor)),
                )


                self.image = ImageTk.PhotoImage(resized_image)
                self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

                self.resize_window(resized_image.width , resized_image.height)

        except Exception as e:
            print(f"Error opening image '{self.image_path}': {e}")
        

    def resize_window(self, width, height):
        geometry_string = f"{width}x{height}"
        self.master.geometry(geometry_string)
        

    def save_annotated_image(self):
        self.annotations_history = self.annotation_handler.annotations_history 

        if self.image_path and self.annotations_history:
            annotated_image = Image.open(self.image_path).convert("RGBA")

            # Calculate scaling factors for width and height
            width_factor = self.canvas.winfo_width() / annotated_image.width
            height_factor = self.canvas.winfo_height() / annotated_image.height

            # Choose the minimum scaling factor to fit the image in the canvas
            scale_factor = min(width_factor, height_factor)

            # Resize the image
            annotated_image = annotated_image.resize(
            (int(annotated_image.width * scale_factor), int(annotated_image.height * scale_factor)),
            )

            draw = ImageDraw.Draw(annotated_image)

            for i, (box, label) in enumerate(self.annotations_history):
                if len(box) == 4 and box[0] < box[2] and box[1] < box[3]:
                    bounding_box_color = self.ClassSelector.class_colors.get(label, "pink")
                    draw.rectangle(box, outline=bounding_box_color)

                    # Automatically select text color for readability
                    text_color = "black" if sum(ImageColor.getcolor(bounding_box_color, "RGBA")[:3]) > 384 else "white"

                    # Display class label and box number on the colored rectangle
                    text = f"{label} - {i + 1}"
                    text_width, text_height = draw.textbbox((0, 0), text)[2] - draw.textbbox((0, 0), text)[0], \
                                             draw.textbbox((0, 0), text)[3] - draw.textbbox((0, 0), text)[1]
                    draw.rectangle([box[0], box[1], box[0] + text_width + 10, box[1] + text_height + 10], fill=bounding_box_color)
                    draw.text((box[0] + 5, box[1] + 5), text, fill=text_color)

            annotated_image = annotated_image.convert("RGB")

            annotated_image_name = os.path.basename(self.image_path)
            annotated_image_path = os.path.join(self.annotated_images_directory, annotated_image_name.replace('.', '_annotated.'))
            annotated_image.save(annotated_image_path)

            print(f"Annotated image saved: {annotated_image_path}")


    def load_selected_image(self, event):
        selected_index = self.listbox_images.curselection()
        if selected_index:
            selected_image = self.listbox_images.get(selected_index)
            self.image_path = os.path.join(self.image_directory, selected_image)
            self.load_image()


    def on_click_press(self, event):

        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        selected_class = self.ClassSelector.combobox_class.get()
        bounding_box_color = self.ClassSelector.class_colors.get(selected_class, "pink")

        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline=bounding_box_color
        )

        # Add colored rectangle on the left top corner during annotation
        rect_width = 50
        rect_height = 20
        self.rect_color_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x + rect_width, self.start_y + rect_height,
            fill=bounding_box_color
        )

        # Automatically select text color for readability
        text_color = "black" if sum(ImageColor.getcolor(bounding_box_color, "RGBA")[:3]) > 384 else "white"

        # Display class label and box number on the colored rectangle during annotation
        text = f"{selected_class} - {self.box_counter}"
        text_width, text_height = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), text)[2] - \
                                ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), text)[0], \
                                ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), text)[3] - \
                                ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), text)[1]
        self.text_id = self.canvas.create_text(
            self.start_x + 5, self.start_y + 5, text=text, fill=text_color, anchor=tk.NW, width=(text_width + 100 )
        )

        self.box_counter += 1


    def on_drag(self, event):

        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)

        # Update position of colored rectangle and text during dragging
        self.canvas.coords(self.rect_color_id, self.start_x, self.start_y, self.start_x + 50, self.start_y + 20)
        self.canvas.coords(self.text_id, self.start_x + 5, self.start_y + 5)
        

    def on_button_release(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        print("Left mouse button released")
        print(f"Rectangle Coordinates: ({self.start_x}, {self.start_y}, {cur_x}, {cur_y})")
        self.annotation_handler.save_annotations()
        