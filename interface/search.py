from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
from model.bodyfactory import BodyFactory
from configuration import (
    GENDERS, UI_FONTSIZE, UI_FONTFAMILY, SYSTEMS
)


class SearchWindow(QDialog):
    def __init__(self, parent: QWidget, factory: BodyFactory, multi_mode=False):
        super().__init__(parent)
        self.factory = factory
        self.resize(500, 700)
        self.setWindowTitle("搜索模型")
        # Search input
        self.search_text = QLineEdit()
        # Search button
        self.search_push = QPushButton("搜索", self)
        self.search_push.clicked.connect(self.search_model)
        # System filter
        self.system_list = QComboBox(self)
        self.system_list.addItems(SYSTEMS)
        self.system_list.currentIndexChanged.connect(self.search_model)
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

        top = QHBoxLayout()
        top.addWidget(self.search_text)
        top.addWidget(self.search_push)

        bottom = QVBoxLayout()
        bottom.addWidget(self.system_list)
        bottom.addWidget(self.result_list)
        bottom.addWidget(self.sure_push)

        layout = QVBoxLayout()
        layout.addLayout(top)
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
        self.sure_push.setFont(font)

        font.setFamily("黑体")
        self.result_list.setFont(font)

    def search_model(self):
        keystring = self.search_text.text()
        keystring = keystring.strip()
        if not len(keystring):
            QMessageBox().warning(self, "警告", "请输入有效内容")
            return
        # System serial number
        keysysid = self.system_list.currentIndex()
        keysysid = keysysid - 1 if keysysid else None
        # Search and display
        self.result.clear()
        self.result_list.clear()
        self.result = [*self.factory.produce_by_search(keystring, keysysid)]
        for _model in self.result:
            _listitem = QListWidgetItem()
            _listitem.setIcon(QIcon(GENDERS[_model.gender()]))
            _listitem.setText(f"{_model.value_} {_model.name}")
            self.result_list.addItem(_listitem)

    @property
    def get_selected_models(self):
        idxes = [idx.row() for idx in self.result_list.selectedIndexes()]
        values = [self.result[i].value for i in idxes]
        return values
