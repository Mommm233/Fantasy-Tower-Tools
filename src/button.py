import json
import shutil
import subprocess
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QDesktopWidget, QLineEdit, QComboBox, QDialog, QSizePolicy, QSpacerItem, QGridLayout, QScrollArea, QCheckBox, QFileDialog
from typing import Callable  


class Button:
    def __init__(self, text: str, set_size_policy_flag: bool = False, hor: QSizePolicy = QSizePolicy.Preferred, ver: QSizePolicy = QSizePolicy.Preferred, on_click: Callable[[], None] = None) -> None:
        self.button = QPushButton(text)
        if set_size_policy_flag:
            self.button.setSizePolicy(hor, ver)
        if on_click is not None:
            self.connect(on_click)

    def connect(self, on_click: Callable[[], None]) -> None:
        self.button.clicked.connect(on_click)

    def set_text(self, new_text: str) -> None:
        self.button.setText(new_text)

    def get_button(self) -> QPushButton:
        return self.button
    

class Mod:
    def __init__(self, mod_path: str, img_path: str, img_rects: list[int], hide: bool = False) -> None:
        self.hlayout = QHBoxLayout()
        vlayout = QVBoxLayout()

        self.mod_path = mod_path

        img_label = QLabel()  
        pixmap = QPixmap(img_path)  
        img_label.setPixmap(pixmap.scaled(img_rects[0], img_rects[1])) 
        img_label.setAlignment(Qt.AlignCenter)

        text_label = QLabel()
        text_label.setText(mod_path.split("\\")[-1] if not hide else "")
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignCenter)

        vlayout.addWidget(img_label)
        vlayout.addWidget(text_label)

        self.checkbox = QCheckBox("")  
        self.checkbox.setChecked(False)  # 初始状态为未选中  
        if hide:
            self.checkbox.hide()

        self.hlayout.addLayout(vlayout)
        self.hlayout.addWidget(self.checkbox, alignment=Qt.AlignRight)

    def get_layout(self) -> QHBoxLayout:
        return self.hlayout 
    
    def is_checked(self) -> bool:
        return self.checkbox.isChecked() if self.checkbox else False

import qdarkstyle
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from typing import Dict  
from PyQt5.QtWidgets import QLayout
import zipfile
import rarfile

class ModUI(QWidget):
    def __init__(self, rects: list[int], custom_stylesheet: str) -> None:
        super().__init__()
        with open("config.json", "r") as f:
            self.data = json.load(f)
        self.rects = rects
        self.resize(self.rects[0], self.rects[1])
        # 设置暗黑样式
        self.setStyleSheet(custom_stylesheet)
        self.mod_dict: Dict[str, Mod] = self.get_mod_dict()
        self.select_all_click_count = 0
        self.init_ui()

    def init_ui(self) -> None:
        self.main_layout = QHBoxLayout(self)
        self.button_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()

        select_all_button = Button("全选", set_size_policy_flag=True, on_click=self.select_all)
        add_mod_button1 = Button("添加mod文件夹", set_size_policy_flag=True, on_click=self.add_mod_folder)
        add_mod_button2 = Button("添加mod压缩文件", set_size_policy_flag=True, on_click=self.add_mod_compress_file)
        remove_mod_button = Button("移除mod", set_size_policy_flag=True, on_click=self.remove_mod)
        use_mod_button = Button("启用", set_size_policy_flag=True, on_click=self.use_mod)

        self.button_layout.addWidget(select_all_button.get_button())
        self.button_layout.addWidget(add_mod_button1.get_button())
        self.button_layout.addWidget(add_mod_button2.get_button())
        self.button_layout.addWidget(remove_mod_button.get_button())
        self.button_layout.addWidget(use_mod_button.get_button())

        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)  # 设置边距  
        self.grid_layout.setHorizontalSpacing(5)  # 设置水平间距  
        self.grid_layout.setVerticalSpacing(5)  # 设置垂直间距 
        self.layout_show_mod(self.grid_layout)

        img_box = QVBoxLayout()
        # 创建一个滚动区域  
        scroll_area = QScrollArea()  
        scroll_area.setWidgetResizable(True)  # 设置滚动区域可以随着内容大小调整
        widget = QWidget()
        img_box_scroll = QVBoxLayout(widget)  # 使用垂直布局来放置图片

        # 将网格布局设置为一个单独的QWidget的子布局  
        self.container = QWidget()  
        self.container.setLayout(self.grid_layout)  
        # 将包含网格布局的QWidget添加到滚动区域的垂直布局中  
        img_box_scroll.addWidget(self.container)  
        # 设置滚动区域的内容为包含垂直布局的QWidget  
        scroll_area.setWidget(widget)  
        # 将滚动区域添加到主布局的末尾  
        img_box.addWidget(scroll_area) 

        self.main_layout.addLayout(img_box)
        self.main_layout.addLayout(self.button_layout)
        self.setWindowTitle('Mod Manage')
 
    def get_mod_dict(self) -> Dict[str, Mod]:
        mod_dict: Dict[str, Mod] = {}
        mod_dir = "mod"
        if not os.path.exists(mod_dir) or not os.path.isdir(mod_dir):
            os.mkdir(mod_dir)
            return
        
        mod_path_list = [os.path.join(mod_dir, name) for name in os.listdir(mod_dir)]  
        default_img_path = r"img\fle1.jpg"
        img_path_list = []
        for mod_path in mod_path_list:
            if not os.path.isdir(mod_path):
                continue
            img_path = default_img_path
            mod_file_list = os.listdir(mod_path)
            for mod_file in mod_file_list:
                if ".png" in mod_file or ".jpg" in mod_file:
                    img_path = os.path.join(mod_path, mod_file)
                    break
            img_path_list.append(img_path)

            mod_dict[mod_path] = Mod(mod_path, img_path, [25 * self.rects[0] // 100, 25 * self.rects[1] // 100])
        return mod_dict

    def layout_show_mod(self, layout: QGridLayout) -> None:
        self.clear_item_of_layout(layout)

        row, col, max_col = 0, 0, 3
        if not self.mod_dict:
            for i in range(max_col):
                layout.addLayout(Mod(r"img", r"img\hide.png", [25 * self.rects[0] // 100, 25 * self.rects[1] // 100], hide=True).get_layout(), 0, i)
            return
        for mod in self.mod_dict.values():
            if mod.mod_path in self.data["Mod"]:
                mod.checkbox.setChecked(self.data["Mod"][mod.mod_path])
                
            layout.addLayout(mod.get_layout(), row, col)
            col = (col + 1) % max_col
            if col == 0:
                row += 1

    def clear_item_of_layout(self, layout: QLayout) -> None:
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)  
            if item:  
                widget = item.widget()  
                if widget:
                    widget.setParent(None)
                else:
                    self.clear_item_of_layout(item.layout())

    def select_all(self) -> None:
        self.select_all_click_count = (self.select_all_click_count + 1) % 2
        for mod in self.mod_dict.values():
            mod.checkbox.setChecked(self.select_all_click_count)

    def extract_file(self, file_path: str) -> None:
            name = file_path.split("/")[-1]
            output_dir = r"mod/{}".format(name.replace(".rar", "").replace(".zip", ""))
            if os.path.exists(output_dir):
                return
            
            os.makedirs(output_dir, exist_ok=True)
            if name.endswith(".rar"):
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    rar_ref.extractall(output_dir)
            else:   # .zip
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)

            # 移动解压后的文件到根目录下
            for foldername, subfolders, filenames in os.walk(output_dir):
                for filename in filenames:
                    source = os.path.join(foldername, filename)
                    destination = os.path.join(output_dir, filename)
                    os.rename(source, destination)

            # 处理完文件后，检查子目录是否为空  
            for foldername, subfolders, filenames in os.walk(output_dir):
                if not subfolders and not filenames:  
                    # 如果子目录为空，则删除它  
                    os.rmdir(foldername)

    def add_mod_compress_file(self) -> None:
        # 设置文件过滤器，只显示压缩文件  
        file_types = "All Files (*.*)"
        file_dialog = QFileDialog()  
        file_dialog.setFileMode(QFileDialog.AnyFile)  
        file_dialog.setNameFilter(file_types)  
        file_dialog.setViewMode(QFileDialog.Detail)
        if file_dialog.exec_():  
            file_name = file_dialog.selectedFiles()[0]  
            if not (file_name.endswith(".rar") or file_name.endswith(".zip")):
                return
            
            self.extract_file(file_name)
            self.mod_dict = self.get_mod_dict()
            self.layout_show_mod(self.grid_layout)

    def add_mod_folder(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")  
        if not folder_path or not os.path.exists(folder_path):
            return

        des_path = r"mod\{}".format(folder_path.split("/")[-1])
        if not os.path.exists(des_path):
            shutil.copytree(folder_path, des_path)
            self.mod_dict = self.get_mod_dict()
            self.layout_show_mod(self.grid_layout)

    def delete_dir(self, path) -> None:
        try:  
            shutil.rmtree(path) 
            print(f"文件夹 {path} 已被删除")  
        except OSError as e:  
            print(f"删除文件夹时出错: {e.strerror}")

    def remove_mod(self) -> None:
        remove_mod_dict = {}
        for mod_path, mod in self.mod_dict.items():
            if mod.is_checked():
                remove_mod_dict[mod_path] = mod
  
        self.mod_dict = self.get_mod_dict()
        self.mod_dict = {k: v for k, v in self.mod_dict.items() if k not in remove_mod_dict.keys()}
        
        for k in remove_mod_dict.keys():
            del self.data["Mod"][k]
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)  # indent 参数用于美化输出，可选)

        self.layout_show_mod(self.grid_layout)
        self.grid_layout.setParent(self.container)

        for path in remove_mod_dict.keys():  
            self.delete_dir(path)

    def mk_link(self) -> None:
        link_name = r"D:\Game\Hotta\Client\WindowsNoEditor\Hotta\Content\PatchPaks\mod"
        target = os.path.join(os.path.abspath('.'), "tempMod")
        cmd = ["cmd.exe", "/C", "mklink", "/D", link_name, target] 
        subprocess.call(cmd)

    def save_selected_to_config(self) -> None:
        temp_mod_dict: Dict[str, int] = {}
        for mod_path, mod in self.mod_dict.items():
            temp_mod_dict[mod_path] = 1 if mod.is_checked() else 0
        self.data["Mod"] = temp_mod_dict
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)  # indent 参数用于美化输出，可选)
    
    def use_mod(self) -> None:
        temp_mod_path = "tempMod"
        if os.path.exists(temp_mod_path):
            self.delete_dir(temp_mod_path)
        os.mkdir(temp_mod_path)

        for mod_path, mod in self.mod_dict.items():
            if mod.is_checked():
                name = mod_path.split("\\")[-1]
                des_path = os.path.join(temp_mod_path, name)
                if not os.path.exists(des_path):
                    shutil.copytree(mod_path, des_path)

        self.mk_link()
        self.save_selected_to_config()
        
    # def resizeEvent(self, event: QEvent) -> None:  
    #     size = self.size()  
    #     print(f'Window size: {size.width()}x{size.height()}')  
    #     super().resizeEvent(event)


import sys  
import os
  
if __name__ == '__main__':  
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    unrar_path = os.path.join(script_dir, 'unrar.exe')  
    # 设置环境变量 PATH，以便包含 unrar.exe 的路径  
    os.environ['PATH'] = os.pathsep.join([os.environ.get('PATH', ''), script_dir]) 

    # 加载 qdarkstyle 样式表
    dark_stylesheet = qdarkstyle.load_stylesheet(qt_api='pyqt5')
    # 在 qdarkstyle 的基础上自定义字体大小
    custom_stylesheet = dark_stylesheet + """
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

    app = QApplication([])  
    ui = ModUI([1600, 900], custom_stylesheet) 
    ui.show()
    sys.exit(app.exec_()) 


