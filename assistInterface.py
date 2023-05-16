from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from main import *


class SearchWindow(QDialog):
    def __init__(self, init_keyword: str, multi_mode=False, parent=None):
        super().__init__(parent)
        self.resize(500, 700)
        self.setWindowTitle("搜索模型")
        # 搜索内容输入
        self.search_text = QLineEdit()
        # 搜索按钮
        self.search_push = QPushButton("搜索", self)
        self.search_push.clicked.connect(self.search_model)
        # 系统筛选
        self.system_list = QComboBox(self)
        self.system_list.addItems(SYSTEMS)
        self.system_list.currentIndexChanged.connect(self.search_model)
        # 结果列表
        self.result = []
        self.result_list = QListWidget(self)
        if multi_mode:
            # 多选模式
            self.result_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        else:
            # 单选模式
            self.result_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        # 选择确认
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
        self.set_style()
        self.search_text.setText(init_keyword)
        self.search_model()

    def set_style(self):
        font = self.font()
        font.setPointSize(10)
        self.search_text.setFont(font)
        self.system_list.setFont(font)
        self.result_list.setFont(font)
        self.system_list.setFont(font)

    def search_model(self):
        keystring = self.search_text.text()
        keystring = keystring.strip()
        if not len(keystring):
            QMessageBox().warning(self, "警告", "请输入有效内容")
            return
        # 系统序号
        keysysid = self.system_list.currentIndex()
        keysysid = keysysid - 1 if keysysid else None
        # 搜索并展示
        self.result.clear()
        self.result_list.clear()
        self.result = [*produce_by_search(keystring, keysysid)]
        self.result_list.addItems(("{:<8d}{}".format(x.value, x.name) for x in self.result))

    @property
    def get_selected_models(self):
        idxes = [idx.row() for idx in self.result_list.selectedIndexes()]
        values = [self.result[i].value for i in idxes]
        return values


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


class DisplayWindow(QWidget):
    def __init__(self, x, y, h):
        super().__init__(None)
        self.setWindowTitle("原信息")
        self.setWindowIcon(QIcon("cache/icon.png"))
        self.setGeometry(x - 300, y, 300, h)
        self.lab = QLabel()
        self.browser = QTextBrowser(self)
        layout = QVBoxLayout()
        layout.addWidget(self.lab)
        layout.addWidget(self.browser)
        self.setLayout(layout)
        self.__set_style()

    def __set_style(self):
        font = self.font()
        font.setPointSize(12)
        self.lab.setFont(font)

        font.setPointSize(10)
        self.browser.setFont(font)

    def display_info(self, model: BodyModel):
        self.browser.clear()
        self.lab.setText(model.name)
        try:
            context = get_old_info(model.value)
        except AssertionError:
            self.browser.setText('')
        else:
            self.browser.setText(context)
