from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
import model.bodyfactory as factory


class DisplayWindow(QWidget):
    def __init__(self, default_hight: int):
        super().__init__(None)
        self.setWindowTitle("原信息")
        self.setWindowIcon(QIcon("./cache/icon.png"))
        self.resize(300, default_hight)
        self.lab = QLabel()
        self.browser = QTextBrowser(self)
        layout = QVBoxLayout()
        layout.addWidget(self.lab)
        layout.addWidget(self.browser)
        self.setLayout(layout)
        self._style()

    def _style(self):
        font = self.font()
        font.setPointSize(12)
        self.lab.setFont(font)

        font.setPointSize(10)
        self.browser.setFont(font)

    def display_info(self, model: factory.BodyModel, x: int, y: int):
        self.move(x - 300, y)
        self.browser.clear()
        self.lab.setText(model.name)
        try:
            context = factory.get_old_info(model.value)
        except AssertionError:
            self.browser.setText('')
        else:
            self.browser.setText(context)
