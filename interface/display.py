from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from factory.bodyfactory import BodyFactory
from model.bodymodel import BodyModel
from configuration import (
    UI_FONTSIZE, UI_FONTFAMILY, WINDOW_ICON_PATH
)


class DisplayWindow(QWidget):
    __width = 300

    def __init__(self, main_window: QWidget):
        super().__init__(None)
        self.main_window = main_window
        self.setWindowTitle("原信息")
        self.setWindowIcon(QIcon(WINDOW_ICON_PATH))
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
        self.lab.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font.setPointSize(UI_FONTSIZE - 1)
        self.browser.setFont(font)
        self.browser.setFrameShape(QFrame(self.browser).frameShape().WinPanel)

    def display_info(self, factory: BodyFactory, body: BodyModel):
        self.resize(self.__width, self.main_window.height())
        self.move(self.main_window.x() - self.__width, self.main_window.y())
        self.browser.clear()
        self.lab.setText(body.name)
        try:
            context = factory.get_old_info(body.value)
        except AssertionError:
            self.browser.setText('')
        else:
            self.browser.setText(context)
