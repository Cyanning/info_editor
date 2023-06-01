from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
import model.bodyfactory as factory
from configuration import *


class DisplayWindow(QWidget):
    __width = 300

    def __init__(self, main_window: QWidget):
        super().__init__(None)
        self.main_window = main_window
        self.setWindowTitle("原信息")
        self.setWindowIcon(QIcon("./cache/icon.png"))
        self.lab = QLabel()
        self.browser = QTextBrowser(self)
        layout = QVBoxLayout()
        layout.addWidget(self.lab)
        layout.addWidget(self.browser)
        self.setLayout(layout)
        self._style()

    def _style(self):
        font = self.font()
        font.setFamily(UI_FONTFAMILY)
        font.setPointSize(UI_FONTSIZE)
        self.lab.setFont(font)

        font.setPointSize(UI_FONTSIZE - 1)
        self.browser.setFont(font)

    def display_info(self, model: factory.BodyModel):
        self.resize(self.__width, self.main_window.height())
        self.move(self.main_window.x() - self.__width, self.main_window.y())
        self.browser.clear()
        self.lab.setText(model.name)
        try:
            context = factory.get_old_info(model.value)
        except AssertionError:
            self.browser.setText('')
        else:
            self.browser.setText(context)
