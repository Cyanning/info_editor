from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from factory.bodyfactory import BodyModel
from configuration import (
    UI_FONTFAMILY, UI_FONTSIZE
)


class PreviewWindow(QDialog):
    def __init__(self, parent: QWidget, models: list[BodyModel]):
        super().__init__(parent)
        self.setWindowTitle("预览并确认是否关联")
        # Scrolling area - Used to fill many text boxes
        scroll = QScrollArea(self)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumWidth(1050 if len(models) > 4 else len(models) * 250 + 50)

        # Widget directly hosted by the scroll area and Table layout for textbox
        widget = QWidget(scroll)
        gbox = QGridLayout(widget)
        font = QFont(UI_FONTFAMILY, UI_FONTSIZE)
        # Put four text boxes per row
        for i in range(0, len(models)):
            textarea = QLabel()
            textarea.setFont(font)
            textarea.setWordWrap(True)
            textarea.setMinimumWidth(250)
            textarea.setFrameShape(QFrame(textarea).frameShape().WinPanel)
            textarea.setText(f"{models[i].value} {models[i].name}\n\n{models[i].paragraph}")
            gbox.addWidget(textarea, i // 4, i % 4)
        widget.setLayout(gbox)
        scroll.setWidget(widget)

        # Twice confirmation button
        btns = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        btnbox = QDialogButtonBox(btns)
        btnbox.accepted.connect(self.accept)
        btnbox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(scroll)
        layout.addWidget(btnbox)
        self.setLayout(layout)
