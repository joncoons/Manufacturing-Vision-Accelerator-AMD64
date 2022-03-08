import io
import cv2
from datetime import datetime

class FrameSave():
    
    def __init__(self, img_path, img_data):
        self.img_path = img_path
        self.img_data = img_data
        self.frame_write(self.img_path, self.img_data)

    def frame_write(self, module_path, image_data):
        cv2.imwrite(module_path, image_data,[int(cv2.IMWRITE_JPEG_QUALITY), 100]) 
        return f"Successfully wrote file: {module_path}"

