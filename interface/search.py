from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
from factory.bodyfactory import BodyFactory
from configuration import (
    GENDERS, UI_FONTSIZE, UI_FONTFAMILY, SYSTEMS
)


class SearchWindow(QDialog):
    def __init__(self, parent: QWidget, factory: BodyFactory, multi_mode: bool):
        super().__init__(parent)
        self.factory = factory
        self.resize(500, 700)
        self.setWindowTitle("搜索模型")
        # Search input
        self.search_text = QLineEdit()
        # Search button
        self.search_push = QPushButton("搜索", self)
        self.search_push.clicked.connect(self.search_model)
        # Filter by system
        self.system_list = QComboBox(self)
        self.system_list.addItems(SYSTEMS)
        # Filter which had be edited
        self.mode_list = QComboBox(self)
        self.mode_list.addItems(["全部", "无信息的", "有信息的"])
        # Modle list of result and list widget of result
        self.result = []
        self.result_list = QListWidget(self)
        if multi_mode:
            # Multiple choice mode
            self.result_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        else:
            # Single choice mode
            self.result_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        self.sure_push = QPushButton("选好了", self)
        self.sure_push.clicked.connect(self.accept)

        row1 = QHBoxLayout()
        row1.addWidget(self.system_list)
        row1.addWidget(self.mode_list)

        row2 = QHBoxLayout()
        row2.addWidget(self.search_text)
        row2.addWidget(self.search_push)

        bottom = QVBoxLayout()
        bottom.addWidget(self.result_list)
        bottom.addWidget(self.sure_push)

        layout = QVBoxLayout()
        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addLayout(bottom)

        self.setLayout(layout)
        self._style()

    def _style(self):
        font = self.font()
        font.setPointSize(UI_FONTSIZE)
        font.setFamily(UI_FONTFAMILY)

        self.search_text.setFont(font)
        self.search_push.setFont(font)
        self.system_list.setFont(font)
        self.mode_list.setFont(font)
        self.sure_push.setFont(font)

        font.setFamily("黑体")
        self.result_list.setFont(font)

    def search_model(self):
        # Keywords
        keystring = self.search_text.text()
        keystring = keystring.strip()

        # System serial number
        keysysid = self.system_list.currentIndex()
        keysysid = keysysid - 1 if keysysid else None

        # Filter mode number
        keyfiltermode = self.mode_list.currentIndex()

        # Search and display
        self.result.clear()
        self.result_list.clear()
        self.result = [*self.factory.produce_by_search(keystring, keysysid, keyfiltermode)]
        for _model in self.result:
            _listitem = QListWidgetItem()
            _listitem.setIcon(QIcon(GENDERS[_model.gender()]))
            _listitem.setText(f"{_model.value_()} {_model.name}")
            self.result_list.addItem(_listitem)

    def get_selected_models(self):
        idxes = [idx.row() for idx in self.result_list.selectedIndexes()]
        values = [self.result[i].value for i in idxes]
        return values
