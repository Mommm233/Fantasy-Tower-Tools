# 识别类
import cv2
import numpy as np
from pyautogui import screenshot
from pygetwindow import pyrect

class Identify:
    def __init__(self, screen_img:np.ndarray) -> None:
        self.screen_img = screen_img
        self.height, self.width, _ = screen_img.shape

    # 判断part是否出现在img里
    def part_is_in_img(self, img:np.ndarray, part:np.ndarray, threshold=0.8) -> bool:
        if img is None or part is None:
            return False
        if img.size == 0 or part.size == 0:
            return False
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_part = cv2.cvtColor(part, cv2.COLOR_BGR2GRAY)
        # 使用模板匹配
        result = cv2.matchTemplate(gray_img, gray_part, cv2.TM_CCOEFF_NORMED)
        if cv2.minMaxLoc(result)[1] > threshold:
            return True
        else:
            return False

    def check(self, rect:list, sign:np.ndarray) -> bool:
        [x, y, w, h] = rect
        img = self.screen_img[y:y+h, x:x+w]
        # cv2.imwrite("img.png", img)
        # cv2.imwrite("sign.png", sign)
        return self.part_is_in_img(img, sign)

    def get_screen_img(self, rect:pyrect.Rect) -> np.ndarray:
        screen_img = screenshot(region=(rect.left, rect.top, rect.width, rect.height))
        screen_img = cv2.cvtColor(np.asarray(screen_img), cv2.COLOR_RGB2BGR)
        return screen_img
    
    # 更新屏幕图像
    def update(self, screen_img:np.ndarray) -> None:
        self.screen_img = screen_img
        self.height, self.width, _ = screen_img.shape


