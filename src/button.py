from PyQt5.QtWidgets import QPushButton, QSizePolicy
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
    



