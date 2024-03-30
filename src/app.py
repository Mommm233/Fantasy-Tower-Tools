# pyqt界面类
import json
import sys
import multiprocessing
import psutil
import qdarkstyle
import subprocess
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QDesktopWidget, QLineEdit, QComboBox, QDialog, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QIcon, QPalette, QPixmap, QBrush
from PyQt5.QtCore import QTimer
from changeconfig import ChangeConfig
from controlf import ControlF
from controlfish import ControlFish

class Ui_MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        with open("config.json", "r") as f:
            self.data = json.load(f)
        # 设置样式
        self.setStyleSheet("""
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
        """)
        self.set_background()
        self.init_ui()
        self.controlf_run = multiprocessing.Value('i', 1)
        self.controlfish_run = multiprocessing.Value('i', 0)

        self.controlf_process = multiprocessing.Process(target=ControlF().run, 
                                                    args=(self.controlf_run,)
                                                    )
        self.controlfish_process = multiprocessing.Process(target=ControlFish().run, 
                                                    args=(self.controlfish_run,)
                                                    )      
        # self.control_process.daemon = True  # 设置为守护进程
        self.controlf_process.start()

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
        # 设置窗口的标题和大小
        self.setWindowTitle('幻塔小工具')
        self.resize(1145, 716)

        # 创建按钮
        self.controlf_button = QPushButton('F键: 1', self)
        self.controlfish_button = QPushButton('钓鱼: 0', self)
        self.config_info_button = QPushButton('配置信息', self)
        self.enter_button = QPushButton('进入游戏', self)

        # 设置按钮的大小策略，使其可以水平和垂直方向上都自动调整大小
        self.controlf_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.controlfish_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.config_info_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.enter_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 按钮点击事件
        self.controlf_button.clicked.connect(self.controlf_button_click)
        self.controlfish_button.clicked.connect(self.controlfish_button_click)
        self.config_info_button.clicked.connect(self.config_info_button_click)
        self.enter_button.clicked.connect(self.enter_button_click)

        # 创建垂直布局
        main_layout = QVBoxLayout()
        # 创建水平布局
        layout = QHBoxLayout()

        # 左侧部件
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.controlf_button)
        left_widget.setLayout(left_layout)

        # 右侧部件
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.controlfish_button)
        right_widget.setLayout(right_layout)

        # 将左右部件添加到水平布局
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)

        # 将水平布局和下方按钮添加到垂直布局
        main_layout.addLayout(layout)
        main_layout.addWidget(self.config_info_button)
        main_layout.addWidget(self.enter_button)

        # 将垂直布局设置到主窗口
        self.setLayout(main_layout)

        # 获取屏幕尺寸
        screen = QDesktopWidget().screenGeometry()
        # 将窗口移动到屏幕中间
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    # 更新进程
    def update_process(self) -> None:
        if self.controlf_run.value:
            if not self.controlf_process.is_alive():
                self.controlf_process.start()
        else:
            if self.controlf_process.is_alive():
                self.controlf_process.join()
            self.controlf_process = multiprocessing.Process(target=ControlF().run, 
                                                        args=(self.controlf_run,)
                                                        )
        if self.controlfish_run.value:
            if not self.controlfish_process.is_alive():
                self.controlfish_process.start()
        else:
            if self.controlfish_process.is_alive():
                self.controlfish_process.join()
            self.controlfish_process = multiprocessing.Process(target=ControlFish().run, 
                                                        args=(self.controlfish_run,)
                                                        )
    
    def controlf_button_click(self) -> None:
        self.controlf_run.value = not self.controlf_run.value  
        if self.controlf_run.value:
            self.controlfish_run.value = 0
            self.controlfish_button.setText(f'钓鱼: {self.controlfish_run.value}')
        self.controlf_button.setText(f'F键: {self.controlf_run.value}')
        self.update_process()

    def controlfish_button_click(self) -> None:
        self.controlfish_run.value = not self.controlfish_run.value  
        if self.controlfish_run.value:
            self.controlf_run.value = 0
            self.controlf_button.setText(f'F键: {self.controlf_run.value}')
        self.controlfish_button.setText(f'钓鱼: {self.controlfish_run.value}')
        self.update_process()

    def config_info_button_click(self) -> None:
        ConfigWindow().exec_()

    def enter_button_click(self) -> None:
        self.game_process = subprocess.Popen([self.data["game_path"]])
        
        # 使用定时器定期检查EXE进程状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_game_status)
        self.timer.setSingleShot(True)  # 设置为仅触发一次
        self.timer.start(60000)  # 一分钟后触发一次
        
    # 检查游戏状态
    def check_game_status(self) -> None:
        for process in psutil.process_iter(['name']):
            if process.info["name"] == self.data["game_process_name"]:
                self.timer.start(1000)  # 一秒钟后触发一次
                return
        self.exit_qt()

    # 退出qt程序
    def exit_qt(self) -> None:
        self.controlf_run.value = 0
        self.controlfish_run.value = 0
        self.update_process()
        sys.exit()

    #  重写窗口的closeEvent方法来捕获关闭事件
    def closeEvent(self, event):
        self.exit_qt()


class ConfigWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()
        with open("config.json", "r") as f:
            self.data = json.load(f)
        # 加载 qdarkstyle 样式表
        dark_stylesheet = qdarkstyle.load_stylesheet(qt_api='pyqt5')
        # 在 qdarkstyle 的基础上自定义字体大小
        custom_stylesheet = dark_stylesheet + """
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
        # 设置暗黑样式
        self.setStyleSheet(custom_stylesheet)
        self.init_ui()

    def init_ui(self) -> None:
        # 设置窗口的标题和大小
        self.setWindowTitle('配置信息')  
        # 设置大小
        self.resize(801, 501)

        self.RTPC_Sound_Master_Volume_label = QLabel("主音量")
        self.RTPC_Sound_Music_Volume_label = QLabel("背景音乐")
        self.RTPC_Sound_SFX_Volume_label = QLabel("音效")
        self.FullscreenMode_label = QLabel("全屏显示")
        self.WindowsAAType_label = QLabel("抗锯齿")
        self.FrameRateLimit_label = QLabel("帧数")
        self.bEnableShadow_label = QLabel("阴影")
        self.RayTracingQuality_label = QLabel("光线追踪")
       
        # 创建文本框
        self.RTPC_Sound_Master_Volume_edit = QLineEdit()
        self.RTPC_Sound_Music_Volume_edit = QLineEdit()
        self.RTPC_Sound_SFX_Volume_edit = QLineEdit()
        self.FrameRateLimit_edit = QLineEdit()
        
        # 创建组合框
        self.FullscreenMode_combobox = QComboBox()
        self.WindowsAAType_combobox = QComboBox()
        self.bEnableShadow_combobox = QComboBox()
        self.RayTracingQuality_combobox = QComboBox()

        self.FullscreenMode_combobox.addItems(["0", "1"])
        self.WindowsAAType_combobox.addItems(["None", "TAA", "SMAA", "DLSS"])
        self.bEnableShadow_combobox.addItems(["False", "True"])
        self.RayTracingQuality_combobox.addItems(["Disable", "Low", "Medium", "VeryHigh"])
        
        # 创建按钮
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.ok_button_click)

        # 设置控件的默认值
        self.set_default_value()

        # 设置布局
        self.set_layout()

        # 获取屏幕尺寸
        screen = QDesktopWidget().screenGeometry()
        # 将窗口移动到屏幕中间
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def ok_button_click(self)-> None:
        # 更新文本框的值到数据字典
        self.data["game_change_content"]["RTPC_Sound_Master_Volume"] = self.RTPC_Sound_Master_Volume_edit.text()
        self.data["game_change_content"]["RTPC_Sound_Music_Volume"] = self.RTPC_Sound_Music_Volume_edit.text()
        self.data["game_change_content"]["RTPC_Sound_SFX_Volume"] = self.RTPC_Sound_SFX_Volume_edit.text()
        self.data["game_change_content"]["FrameRateLimit"] = self.FrameRateLimit_edit.text()
        
        # 更新组合框的当前选项到数据字典
        self.data["game_change_content"]["FullscreenMode"] = self.FullscreenMode_combobox.currentText()
        self.data["game_change_content"]["WindowsAAType"] = self.WindowsAAType_combobox.currentText()
        self.data["game_change_content"]["bEnableShadow"] = self.bEnableShadow_combobox.currentText()
        self.data["game_change_content"]["RayTracingQuality"] = self.RayTracingQuality_combobox.currentText()
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)  # indent 参数用于美化输出，可选)
        
        ChangeConfig(self.data).change()
        
        # 关闭 QDialog 界面
        self.close() 

    # 设置文本框、组合框默认值
    def set_default_value(self)-> None:
        self.RTPC_Sound_Master_Volume_edit.setText(self.data["game_change_content"]["RTPC_Sound_Master_Volume"])
        self.RTPC_Sound_Music_Volume_edit.setText(self.data["game_change_content"]["RTPC_Sound_Music_Volume"])
        self.RTPC_Sound_SFX_Volume_edit.setText(self.data["game_change_content"]["RTPC_Sound_SFX_Volume"])
        self.FrameRateLimit_edit.setText(self.data["game_change_content"]["FrameRateLimit"])
        self.FullscreenMode_combobox.setCurrentText(self.data["game_change_content"]["FullscreenMode"])
        self.WindowsAAType_combobox.setCurrentText(self.data["game_change_content"]["WindowsAAType"])
        self.bEnableShadow_combobox.setCurrentText(self.data["game_change_content"]["bEnableShadow"])
        self.RayTracingQuality_combobox.setCurrentText(self.data["game_change_content"]["RayTracingQuality"])

    # 辅助函数
    def hlayout_add_widget(self, lable, widget):
        hlayout = QHBoxLayout()
        hlayout.addWidget(lable)
        hlayout.addWidget(widget)
        return hlayout

    # 设置布局
    def set_layout(self) -> None:
        hlayouts = []
        hlayouts.append(self.hlayout_add_widget(self.RTPC_Sound_Master_Volume_label, self.RTPC_Sound_Master_Volume_edit))
        hlayouts.append(self.hlayout_add_widget(self.RTPC_Sound_Music_Volume_label, self.RTPC_Sound_Music_Volume_edit))
        hlayouts.append(self.hlayout_add_widget(self.RTPC_Sound_SFX_Volume_label, self.RTPC_Sound_SFX_Volume_edit))
        hlayouts.append(self.hlayout_add_widget(self.FrameRateLimit_label, self.FrameRateLimit_edit))
        hlayouts.append(self.hlayout_add_widget(self.FullscreenMode_label, self.FullscreenMode_combobox))
        hlayouts.append(self.hlayout_add_widget(self.WindowsAAType_label, self.WindowsAAType_combobox))
        hlayouts.append(self.hlayout_add_widget(self.bEnableShadow_label, self.bEnableShadow_combobox))
        hlayouts.append(self.hlayout_add_widget(self.RayTracingQuality_label, self.RayTracingQuality_combobox))
        layout = QVBoxLayout()
        for hlayout in hlayouts:
            layout.addLayout(hlayout)
        layout.addWidget(self.ok_button)
        # 添加一个垂直方向的伸展因子，使控件在垂直方向上居中
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        self.setLayout(layout)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("img\\fle.jpg"))  # 替换 'icon.png' 为您的图标文件路径
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())


# pyinstaller --uac-admin --icon=img\\fle.jpg --name=幻塔小工具 ./src/app.py ./src/changeconfig.py ./src/controlf.py ./src/controlfish.py ./src/identify.py --noconsole
    
