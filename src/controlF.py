# 控制F键类
import cv2
import multiprocessing
import json
import numpy as np
from pyautogui import press
from pygetwindow import getActiveWindow
from time import sleep
from identify import Identify



class ControlF:
    def __init__(self) -> None:
        with open("config.json", "r") as f:
            data = json.load(f)
        self.window_title = data["title"]
        self.rect = data["ControlF"]["rect"]

        self.sign = cv2.imread(data["ControlF"]["path"])
        self.identify = Identify(np.zeros((100, 100, 3), dtype=np.uint8))

    def run(self,
            run: multiprocessing.Value) -> None:
        while run.value:
            active_window = getActiveWindow()
            if not active_window or active_window.title.strip() != self.window_title:
                sleep(1)
                continue
            
            screen_img = self.identify.get_screen_img(active_window._rect)
            self.identify.update(screen_img)
            if self.identify.check(self.rect, self.sign):
                #print("f")
                press('f')
            sleep(0.2)