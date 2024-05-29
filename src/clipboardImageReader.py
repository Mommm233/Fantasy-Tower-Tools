import os
from PIL import Image, ImageGrab
from typing import List, Union, Optional



class ClipboardImageReader:
    def __init__(self) -> None:
        pass

    def get_image(self) -> Union[List[str], Image.Image, None]:
        # 尝试从剪贴板获取图像  
        return ImageGrab.grabclipboard()  
        
    def remove_image(self, path: str) -> None:
        file_name_list = os.listdir(path)
        for name in file_name_list:
            if name.endswith(".png") or name.endswith(".jpg"):
                os.remove(os.path.join(path, name))
  
    def save_image(self, path: str) -> None:
        img = self.get_image()
        if img:
            self.remove_image(path)
            img.save(os.path.join(path, "1.png"))
