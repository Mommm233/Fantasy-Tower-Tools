# pyqt界面类
import os, sys, subprocess
import multiprocessing
import psutil
import json
import qdarkstyle
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon, QPalette, QPixmap, QBrush
from button import Button
from controlF import ControlF
from controlFish import ControlFish
from secondWindow import ModUI, ConfigInfoUI



class Ui_MainWindow(QWidget):
    def __init__(self, custom_stylesheet: str) -> None:
        super().__init__()
        with open("config.json", "r") as f:
            self.data = json.load(f)
        self.rects = [self.data["UI_Rects"]["MainWindow"]["w"], self.data["UI_Rects"]["MainWindow"]["h"]]

        # 多进程通信信号
        self.controlf_run = multiprocessing.Value('i', 1)
        self.controlfish_run = multiprocessing.Value('i', 0)
        self.controlf_process = multiprocessing.Process(target=ControlF(self.data).run, 
                                                    args=(self.controlf_run,)
                                                    )  
        self.controlf_process.start()

        self.resize(self.rects[0], self.rects[1])
        # 设置样式
        self.setStyleSheet(custom_stylesheet)
        self.init_ui()

    # 设置窗口背景图片
    def set_background(self) -> None:
        # 设置窗口的调色板
        palette = QPalette()
        # 创建一个QBrush对象，使用QPixmap加载图片
        brush = QBrush(QPixmap("img\\fle1.jpg"))
        # 设置调色板的背景角色为我们创建的QBrush对象
        palette.setBrush(QPalette.Background, brush)
        # 应用调色板
        self.setPalette(palette)

    # 初始化ui部件
    def init_ui(self) -> None:
        self.set_background()
        main_layout = QVBoxLayout(self)
        layout = QHBoxLayout()

        # 创建按钮
        self.f_button = Button('F key: 1', set_size_policy_flag=True, on_click=self.f_button_click)
        self.fish_button = Button('Fish: 0', set_size_policy_flag=True, on_click=self.fish_button_click)
        self.mod_manage_button = Button('Mod Manage', set_size_policy_flag=True, on_click=self.mod_manage_button_click)
        self.config_info_button = Button('Config Information', set_size_policy_flag=True, on_click=self.config_info_button_click)
        self.enter_button = Button('进入游戏', set_size_policy_flag=True, on_click=self.enter_button_click)

        # 左侧部件
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.f_button.get_button())
        left_widget.setLayout(left_layout)

        # 右侧部件
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.fish_button.get_button())
        right_widget.setLayout(right_layout)

        # 将左右部件添加到水平布局
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)

        # 将水平布局和下方按钮添加到垂直布局
        main_layout.addLayout(layout)
        main_layout.addWidget(self.mod_manage_button.get_button())
        main_layout.addWidget(self.config_info_button.get_button())
        main_layout.addWidget(self.enter_button.get_button())

        self.setWindowTitle('幻塔小工具')

    # 更新进程
    def update_process(self) -> None:
        if self.controlf_run.value:
            if not self.controlf_process.is_alive():
                self.controlf_process.start()
        else:
            if self.controlf_process.is_alive():
                self.controlf_process.join()
            self.controlf_process = multiprocessing.Process(target=ControlF(self.data).run, 
                                                        args=(self.controlf_run,)
                                                        )
        if self.controlfish_run.value:
            self.controlfish_process = multiprocessing.Process(target=ControlFish(self.data).run, 
                                                    args=(self.controlfish_run,)
                                                    )  
            self.controlfish_process.start()
    
    # 更新按钮文本
    def update_button_text(self) -> None:
        self.f_button.set_text(f'F Key: {self.controlf_run.value}')
        self.fish_button.set_text(f'Fish: {self.controlfish_run.value}')

    def update_widget_and_process(self) -> None:
        self.update_button_text()
        self.update_process()

    def f_button_click(self) -> None:
        self.controlf_run.value = not self.controlf_run.value  
        if self.controlf_run.value:
            self.controlfish_run.value = 0
        self.update_widget_and_process()

    def fish_button_click(self) -> None:
        self.controlfish_run.value = not self.controlfish_run.value  
        if self.controlfish_run.value:
            self.controlf_run.value = 0
        self.update_widget_and_process()

    def mod_manage_button_click(self) -> None:
        ModUI(custom_stylesheet2).exec_()

    def config_info_button_click(self) -> None:
        ConfigInfoUI(custom_stylesheet3).exec_()

    def enter_button_click(self) -> None:
        self.game_process = subprocess.Popen([self.data["Game_Info"]["launcher_path"]])
        # 使用定时器定期检查EXE进程状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_game_status)
        self.timer.setSingleShot(True)  # 设置为仅触发一次
        self.timer.start(60000)  # 一分钟后触发一次
        
    # 检查游戏状态
    def check_game_status(self) -> None:
        for process in psutil.process_iter(['name']):
            if process.info["name"] == self.data["Game_Info"]["process_name"]:
                self.timer.start(1000)  # 一秒钟后触发一次
                return
        self.exit_qt()

    # 退出qt程序
    def exit_qt(self) -> None:
        self.controlf_run.value = 0
        self.controlfish_run.value = 0
        self.update_widget_and_process()
        sys.exit()

    #  重写窗口的closeEvent方法来捕获关闭事件
    def closeEvent(self, event):
        self.exit_qt()





if __name__ == '__main__':
    multiprocessing.freeze_support()

    script_dir = os.path.dirname(os.path.abspath(__file__))  
    unrar_path = os.path.join(script_dir, 'unrar.exe')  
    # 设置环境变量 PATH，以便包含 unrar.exe 的路径  
    os.environ['PATH'] = os.pathsep.join([os.environ.get('PATH', ''), script_dir]) 

    # 加载 qdarkstyle 样式表
    dark_stylesheet = qdarkstyle.load_stylesheet(qt_api='pyqt5')
    custom_stylesheet1 = """
            QPushButton {
                background-color: rgba(0, 0, 255, 100); /* 设置背景颜色为半透明的蓝色 */
                color: white;
                border: 1px solid #666;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 30px;
            }

            QPushButton:hover {
                background-color: #555;
            }
        """
    custom_stylesheet2 = dark_stylesheet + """
        QLabel {
            font-size: 25px; /* 设置 QLabel 的字体大小为 20px */
        }
        
        QCheckBox {  
                color: black; /* 设置文字颜色 */  
                background-color: white; /* 设置背景颜色 */  
            }  
        
        QCheckBox::indicator {  
            width: 20px;  
            height: 20px;  
        }  

        QCheckBox::indicator:unchecked {  
            image: none; /* 移除默认的未选中图片 */  
            background-color: lightgray; /* 设置未选中时的背景颜色 */  
        }  

        QCheckBox::indicator:checked {  
            image: none; /* 移除默认的选中图片 */  
            background-color: green; /* 设置选中时的背景颜色 */  
        }  

        QCheckBox::indicator:disabled {  
            background-color: lightgray; /* 设置禁用时的背景颜色 */  
        }  

        QPushButton {
            font-size: 25px;
        }
        /* 您可以根据需要为其他控件添加或修改样式 */
    """
    custom_stylesheet3 = dark_stylesheet + """
            QLabel {
                font-size: 30px; /* 设置 QLabel 的字体大小为 30px */
            }
            QLineEdit {
                font-size: 30px;
            }
            QComboBox {
                font-size: 30px;
            }
            QPushButton {
                font-size: 30px;
            }
            /* 您可以根据需要为其他控件添加或修改样式 */
        """

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("img\\fle.jpg"))  # 替换 'icon.png' 为您的图标文件路径
    window = Ui_MainWindow(custom_stylesheet1)
    window.show()
    sys.exit(app.exec_())
'''
pyinstaller --uac-admin --icon=img\\fle.jpg --name=幻塔小工具 ./src/app.py ./src/button.py ./src/controlF.py ./src/controlFish.py ./src/identify.py ./src/secondWindow.py ./src/updateGameConfig.py ./src/clipboardImageReader.py --noconsole

D:\\Game\\Hotta\\Script\\_internal\\PyQt5\\Qt5\\plugins\\platforms -> D:\\Game\\Hotta\\Script\\platforms

D:\\Game\\Hotta\\Script\\
                     |\\_internal
                     |\\img
                     |\\mod
                     |\\platforms
                     |\\tempMod
                     |\\config.json
                     |\\UnRAR.exe
                     |\\幻塔小工具.exe

'''
