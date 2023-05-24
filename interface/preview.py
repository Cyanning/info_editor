from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from main import *


class PreviewWindow(QDialog):
    def __init__(self, models: list[BodyModel], parent=None):
        super().__init__(parent)
        self.setWindowTitle("预览并确认是否关联")

        scroll = QScrollArea(self)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumWidth(1050 if len(models) > 4 else len(models) * 250 + 50)
        widget = QWidget(scroll)
        gbox = QGridLayout(widget)

        for i in range(0, len(models)):
            textarea = QLabel()
            textarea.setWordWrap(True)
            textarea.setText(f"{models[i].value} {models[i].name}\n\n{models[i].paragraph}")
            textarea.setMinimumWidth(250)
            textarea.setFrameShape(QFrame(textarea).frameShape().WinPanel)
            gbox.addWidget(textarea, i // 4, i % 4)

        widget.setLayout(gbox)
        scroll.setWidget(widget)

        btns = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        btnbox = QDialogButtonBox(btns)
        btnbox.accepted.connect(self.accept)
        btnbox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(scroll)
        layout.addWidget(btnbox)
        self.setLayout(layout)
