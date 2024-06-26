# 控制钓鱼类
import datetime
import cv2
import numpy as np
import multiprocessing
from pyautogui import press, keyDown, keyUp, click
from pygetwindow import getActiveWindow
from time import sleep, time
from identify import Identify



# 控制白条的左右移动
def control_white_bar(run: multiprocessing.Value, queue: multiprocessing.Queue) -> None:
    direction = None
    while run.value:
        if queue.empty():
            continue
        next_direction = queue.get()
        if direction == next_direction:
            continue
        if direction and direction != next_direction:
            keyUp(direction)
            direction = next_direction
            keyDown(direction)
        else:
            direction = next_direction
            keyDown(direction)

class ControlFish:
    def __init__(self, data: dict) -> None:
        self.window_title = data["Game_Info"]["title"]
        resolving_power = f"{data['Game_Info']['change_content']['ResolutionSizeX']}X{data['Game_Info']['change_content']['ResolutionSizeY']}"
        self.rects = data["Image_Related"][resolving_power]["ControlFish"]["rects"]
        self.signs = {}
        for key, value in data["Image_Related"]["img_names"]["fish_imgs"].items():
            self.signs[key] = cv2.imread(f"img\\{resolving_power}\\{value}")

        self.fidentify = FIdentify(np.zeros((100, 100, 3), dtype=np.uint8), self.rects, self.signs)
        
        self.fish = Fish(self.fidentify, data["Image_Related"][resolving_power]["ControlFish"]["v_values"])
        self.queue = multiprocessing.Queue()
        self.prepare_fish_flag = False
        self.have_fish_tolerance_flag = False
        self.start_fish_time = 0

    # 清空multiprocessing.Queue
    def clear_queue(self, q: multiprocessing.Queue) -> None:
        while not q.empty():
            _ = q.get()

    def init(self) -> None:
        self.fish.init()
        self.clear_queue(self.queue)
        self.prepare_fish_flag = False
        self.have_fish_tolerance_flag = False
        self.start_fish_time = time()

    def run(self,
            run: multiprocessing.Value
            ) -> None:
        
        self.journal = open(r"log\{}_journal.log".format(datetime.datetime.now().strftime("%Y-%m-%d")), "a", encoding="utf-8")
        s1 = time()

        control_white_bar_process = multiprocessing.Process(target=control_white_bar, 
                                                    args=(run, self.queue))
        while run.value:
            active_window = getActiveWindow()
            if not active_window or active_window.title.strip() != self.window_title:
                continue
            # 判断multiprocessing.Process是否已经调用了start()方法
            if not control_white_bar_process.is_alive():
                self.init()
                control_white_bar_process = multiprocessing.Process(target=control_white_bar, 
                                            args=(run, self.queue))
                control_white_bar_process.start()

            screen_img = self.fidentify.get_screen_img(active_window._rect)
            success, defeat, is_except, move_direction = self.fish.get_states(screen_img, time() - self.start_fish_time)

            if time() - s1 > 0.5:
                #journal_text = "----------------------------------------------------\n"
                journal_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
                journal_text += f"持续时间{int(time() - self.start_fish_time)}\n"
                journal_text += f"success: {success}, defeat: {defeat}, is_except: {is_except}, move_direction: {move_direction}\n"
                journal_text += f"准备钓鱼: {self.fish.prepare_fish}\n"
                journal_text += f"有鱼耐力: {self.fish.have_fish_tolerance}\n"
                journal_text += "----------------------------------------------------\n"
                self.journal.write(journal_text)
                s1 = time()

            if is_except:
                run.value = 0
                print("异常...")
            else:
                if self.fish.prepare_fish and not self.prepare_fish_flag:
                    self.prepare_fish_flag = True
                    press('1')
                elif self.fish.have_fish_tolerance and not self.have_fish_tolerance_flag:
                    self.have_fish_tolerance_flag = True
                    sleep(1)
                elif success:
                    keyUp('a')
                    keyUp('d')
                    sleep(1)
                    press('1')
                    sleep(2.5)
                    click()
                    sleep(2.5)
                    self.init()
                elif defeat:
                    self.init()
                    self.fish.prepare_fish = True
                elif move_direction:
                    self.queue.put(move_direction)
                # print(f"success: {success}", f"defeat: {defeat}", f"Time: {time() - self.start_fish_time}")

        self.journal.close()

        if control_white_bar_process.is_alive():
            control_white_bar_process.join()

class FIdentify(Identify):
    def __init__(self, screen_img: np.ndarray, rects: dict, signs: dict) -> None:
        super().__init__(screen_img)
        self.rects = rects
        self.signs = signs

    # 获得左右坐标 left right
    def get_position(self, gray_img: np.ndarray, vmin: int, vmax: int, length: int) -> tuple:
        one_dim = np.mean(np.array(gray_img), axis=0).astype(np.uint8)
        # print(one_dim)
        left, right = -1, -1
        i, j = 0, one_dim.shape[0] - 1
        for i in range(one_dim.shape[0]):
            if vmin <= one_dim[i] <= vmax:
                if length * vmin <= one_dim[i:i+length].sum() <= length * vmax:
                    left = i + length // 2
                    break
        for j in range(one_dim.shape[0] - 1, -1, -1):
            if vmin <= one_dim[j] <= vmax:
                if length * vmin <= one_dim[j-length+1:j+1].sum() <= length * vmax:
                    right = j - length // 2
                    break
        return (left, right)

    # 获得钓鱼条信息
    def get_fish_bar_info(self, vmin1: int, vmax1: int, len1: int,
                          vmin2: int, vmax2: int, len2: int) -> tuple:
        [x, y, w, h] = self.rects["fish_bar"]
        img = self.screen_img[y:y+h, x:x+w]
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # cv2.imwrite("gray_fish_bar_img.png", gray_img)
        slider_left, slider_right = self.get_position(gray_img, vmin1, vmax1, len1)
        white_bar_pos, _ = self.get_position(gray_img, vmin2, vmax2, len2)
        # print(slider_left, slider_right, white_bar_pos)
        return (slider_left, slider_right, white_bar_pos)

    # 判断是否进入钓鱼界面
    def is_fish_sign(self) -> bool:
        return self.check(self.rects["fish_sign"], self.signs["fish_sign"])

    # 判断是否准备钓鱼
    def is_prepare_fish(self) -> bool:
        return self.check(self.rects["prepare_fish"], self.signs["prepare_fish"], threshold=0.6)
    
    # 判断是否有鱼耐力
    def is_have_fish_tolerance(self) -> bool:
        # [x, y, w, h] = self.rects["fish_tolerance"]
        # have_fish_tolerance_img = self.screen_img[y:y+h, x:x+w]
        # cv2.imwrite("have_fish_tolerance_img.png", have_fish_tolerance_img)
        # cv2.imwrite("have_fish_tolerance_sign.png", self.signs["fish_tolerance"])
        return self.check(self.rects["fish_tolerance"], self.signs["fish_tolerance"])

    # 判断是否成功
    def is_success(self) -> bool:
        [x, y, w, h] = self.rects["success"]
        img = self.screen_img[y:y+h, x:x+w]
        # cv2.imwrite("success_img.png", img)
        binary_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) // 218
        # cv2.imwrite("binary_success_img.png", binary_img)
        return np.sum(binary_img) == 0

    # 判断是否异常
    def is_except(self) -> bool:
        return self.check(self.rects["except"], self.signs["except"])

class Fish:
    def __init__(self, fidentify: FIdentify, v_values: list[int]) -> None:
        self.fidentify = fidentify
        self.v_values = v_values
        self.fish_sign = False
        self.prepare_fish = False
        self.have_fish_tolerance = False    # 耐力

    def init(self) -> None:
        self.fish_sign = False
        self.prepare_fish = False
        self.have_fish_tolerance = False

    # 返回成功、失败、异常, 移动方向
    def get_states(self, screen_img: np.ndarray, Time: int) -> tuple:
        move_direction = None 
        self.fidentify.update(screen_img)
        if not self.fish_sign:
            self.fish_sign = self.fidentify.is_fish_sign()
            return 0, 0, 0, move_direction
        elif self.fidentify.is_except():
            return 0, 0, 1, move_direction
        elif not self.prepare_fish:
            self.prepare_fish = self.fidentify.is_prepare_fish()
            return 0, 0, 0, move_direction
        elif not self.have_fish_tolerance:
            self.have_fish_tolerance = self.fidentify.is_have_fish_tolerance()
            return 0, 0, 0, move_direction
        
        [vmin1, vmax1, vmin2, vmax2] = self.v_values
        slider_left, slider_right, white_bar_pos = self.fidentify.get_fish_bar_info(vmin1, vmax1, 20, vmin2, vmax2, 1)
        slider_mid = (slider_left + slider_right) // 2
        
        if self.fidentify.is_success():
            return 1, 0, 0, move_direction 
        elif Time >= 120:
            return 0, 1, 0, move_direction
        elif slider_left == -1 or white_bar_pos == -1:
            return 0, 0, 0, move_direction

        if white_bar_pos < slider_mid:
            move_direction = 'd'
        else:
            move_direction = 'a'
        return 0, 0, 0, move_direction


