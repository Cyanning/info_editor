from collections import OrderedDict
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from interface import preview, search, display, datapanel
from model.bodyfactory import *


class MainWindow(QMainWindow):
    def __init__(self):
        # 窗口设置
        super().__init__(None)
        self.__init_size()
        self.setWindowTitle("信息编辑器")
        self.setWindowIcon(QIcon(RTPATH + "cache/icon.png"))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.menuitems = OrderedDict()  # 菜单
        self.widgets = OrderedDict()  # 组件
        self.assist_window = display.DisplayWindow(self.height())  # 辅助窗口

        # 主界面布局
        self.__setup_interface()
        layout_rows = [QHBoxLayout() for _ in range(4)]  # 每行一个布局器
        for key in self.widgets:
            match key:
                case 'modelid' | 'name' | 'export' | 'save':
                    layout_rows[0].addWidget(self.widgets[key])

                case 'jump' | 'pervious' | 'next' | 'search':
                    layout_rows[1].addWidget(self.widgets[key])

                case 'info' | 'sentence':
                    layout_rows[2].addWidget(self.widgets[key])

                case 'addoldinfo' | 'addinfo' | 'split' | 'assignment':
                    layout_rows[3].addWidget(self.widgets[key])

        layout = QVBoxLayout()  # 总布局器
        for row in layout_rows:
            layout.addLayout(row)

        widget = QWidget(self)  # 中央控件
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # 初始化加载模型
        self.model = load_cache_model()
        self.load_model()

    def __setup_interface(self):
        # 模型id输入\显示
        self.widgets['modelid'] = QSpinBox(None)
        self.widgets['modelid'].setMinimum(100000)
        self.widgets['modelid'].setMaximum(2119999)
        self.widgets['modelid'].setAlignment(Qt.AlignmentFlag.AlignRight)
        self.widgets['modelid'].setFixedWidth(100)

        # 显示模型名字
        self.widgets['name'] = QLineEdit("模型名字")
        self.widgets['name'].setReadOnly(True)
        self.widgets['name'].setFixedWidth(self.width() // 2)
        self.widgets['name'].setStyleSheet("border: none;")
        self.widgets['name'].setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # 导出当前数据
        self.widgets['export'] = QPushButton("管理数据")
        self.widgets['export'].clicked.connect(self.management_database)

        # 保存当前数据
        self.widgets['save'] = QPushButton("保  存")
        self.widgets['save'].clicked.connect(self.save_info)

        # 跳转指定id的模型
        self.widgets['jump'] = QPushButton("跳转")
        self.widgets['jump'].clicked.connect(self.jump_model)

        # 切换上一条
        self.widgets['pervious'] = QPushButton("上一条")
        self.widgets['pervious'].clicked.connect(self.previous_model)

        # 切换下一条
        self.widgets['next'] = QPushButton("下一条")
        self.widgets['next'].clicked.connect(self.next_model)

        # 搜索模型来编辑
        self.widgets['search'] = QPushButton("搜索")
        self.widgets['search'].clicked.connect(self.specify_model_from_search)

        # 信息编辑框
        self.widgets['info'] = QPlainTextEdit()

        # 按句子显示框
        self.widgets['sentence'] = QListWidget(self)
        self.widgets['sentence'].setWordWrap(True)
        self.widgets['sentence'].setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        # 加载原始信息
        self.widgets['addoldinfo'] = QPushButton("显示原始数据", self)
        self.widgets['addoldinfo'].clicked.connect(self.show_oldinfo_context)

        # 从搜索的模型信息加载
        self.widgets['addinfo'] = QPushButton("添加其他信息", self)
        self.widgets['addinfo'].clicked.connect(self.add_sentences_from_search)

        # 按句拆分当前信息
        self.widgets['split'] = QPushButton("拆分信息")
        self.widgets['split'].clicked.connect(self.load_sentences_list)

        # 将当前句子关联其他模型
        self.widgets['assignment'] = QPushButton("关联其他模型")
        self.widgets['assignment'].clicked.connect(self.sentence_put_others)

        # 批量设置字体
        font = self.font()
        font.setFamily(UI_FONTFAMILY)
        font.setPointSize(UI_FONTSIZE)
        for key in self.widgets:
            match key:
                case 'name' | 'save':
                    font.setBold(True)
                    self.widgets[key].setFont(font)
                    font.setBold(False)
                case _:
                    self.widgets[key].setFont(font)
            # 设置焦点策略
            self.widgets[key].setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def __init_size(self):
        """
        初始坐标，初始尺寸
        """
        desk = QApplication.primaryScreen().geometry()
        w, h = desk.width(), desk.height()
        size = map(int, [w / 4, h / 2 - w / 6, w / 2, w / 3])
        self.setGeometry(*size)

    def load_model(self):
        """
        载入模型数据
        """
        self.widgets['name'].setText(genders[self.model.gender] + self.model.name)
        self.widgets['modelid'].setValue(self.model.value)
        self.widgets['info'].setPlainText(self.model.paragraph)
        self.display_sentences_list()

    def display_sentences_list(self):
        """
        显示句子列表
        """
        self.widgets['sentence'].clear()
        for i, item in enumerate(self.model, start=1):
            self.widgets['sentence'].addItem(f"{i}. {item.value}")

    def previous_model(self):
        """
        上一条
        """
        value = self.model.value
        self.changed_model(value, -1)

    def next_model(self):
        """
        下一条
        """
        value = self.model.value
        self.changed_model(value, 1)

    def jump_model(self):
        """
        跳转指定id，或附近
        """
        value = self.widgets['modelid'].value()
        self.changed_model(value, 0)

    def changed_model(self, value, direction):
        """
        切换前后模型，或者跳转到指定模型
        """
        try:
            self.model = create_next_value(value, direction)
            self.load_model()
        except AssertionError:
            QMessageBox().warning(self, "警告", "Id 格式错误。")

    def specify_model_from_search(self):
        """
        搜索模型
        """
        try:
            modelvals = self.search_model(False)
            self.model = create_by_value(modelvals)
            self.load_model()
        except AssertionError:
            return

    def save_info(self):
        """
        保存信息（以句子为准）
        """
        if not self.warning("Confirm save?", "确定以当前所填内容保存吗？"):
            return
        try:
            self.model.paragraph = self.widgets['info'].toPlainText()
            saving_model_basedon_paragraph(self.model)
        except Exception as e:
            QMessageBox().critical(self, "错误", f"保存信息发生错误。\n错误原因：\n{e}")
        else:
            QMessageBox().information(self, "Good", "保存成功！")
        finally:
            self.model = create_by_value(self.model.value)
            self.load_model()

    def add_sentences_from_search(self):
        """
        从数据库添加句子、信息
        """
        try:
            value = self.search_model(False)
            sentences = produce_sentences_by_value(value)
            self.model.add_into_paragraph(sentences)
            self.widgets['info'].appendPlainText(self.model.paragraph)
        except AssertionError:
            QMessageBox().warning(self, "警告", "没有信息可以被添加。")
        except Exception as e:
            QMessageBox().critical(self, "错误", f"错误原因：\n{e}")

    def load_sentences_list(self):
        """拆分句子"""
        try:
            self.model.paragraph = self.widgets['info'].toPlainText()
            self.model.convert_into_sentences()
            self.display_sentences_list()
        except AssertionError:
            QMessageBox().critical(self, "错误", f"内容为空白。")

    def sentence_put_others(self):
        """
        为其他模型添加句子
        """
        try:
            sentences = [self.model[i.row()] for i in self.widgets['sentence'].selectedIndexes()]
            assert len(sentences) > 0
            modelvals = self.search_model(True)
            models = []
            for item in modelvals:
                model_item = create_by_value(item)
                model_item.add_into_sentences(sentences)
                model_item.convert_for_paragraph()
                models.append(model_item)

            agree_preview = preview.PreviewWindow(models, self)
            if agree_preview.exec():
                for model_item in models:
                    saving_model(model_item)
                QMessageBox().information(self, "Good", "关联成功！")
        except AssertionError:
            QMessageBox().critical(self, "错误", f"请做出完整的选择。")
        except Exception as e:
            QMessageBox().critical(self, "错误", f"添加句子发生错误。\n错误原因：\n{e}")

    def search_model(self, multi: bool):
        """
        通用搜索窗口回调方法
        :param multi: False 为单选；True 为多选
        """
        keywords = self.model.name
        if keywords[-1] == '）':
            keywords = keywords[:keywords.index('（')]
        popup = search.SearchWindow(keywords, parent=self, multi_mode=multi)
        popup.exec()
        modelvals = popup.get_selected_models
        assert len(modelvals)
        return modelvals if multi else modelvals[0]

    def show_oldinfo_context(self):
        """
        显示旧info数据
        """
        if self.assist_window.isVisible():
            self.assist_window.hide()
        else:
            self.assist_window.display_info(self.model, self.x(), self.y())
            self.assist_window.show()

    def management_database(self):
        manager = datapanel.DatePanel()
        manager.exec()

    def warning(self, tittle: str, context: str) -> bool:
        font = self.font()
        font.setPointSize(UI_FONTSIZE)
        font.setFamily(UI_FONTFAMILY)

        sure = QMessageBox(self)
        sure.setFont(font)
        sure.setIcon(QMessageBox.Icon.Warning)
        sure.setWindowTitle(tittle)
        sure.setText(context)
        sure.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        sure.setDefaultButton(QMessageBox.StandardButton.Cancel)
        flag = sure.exec() == QMessageBox.StandardButton.Ok
        return flag

    def closeEvent(self, event: QCloseEvent):
        """
        重写窗口关闭事件
        """
        if self.warning("Confirm quit?", "退出前确认是否保存。\n确认退出？\n"):
            # del self.assist_window
            write_cache_model(self.model.value)
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        """
        重写按键事件
        """
        match event.key():
            case Qt.Key.Key_Return | Qt.Key.Key_Enter:
                if self.widgets['modelid'].hasFocus():
                    self.jump_model()

            case Qt.Key.Key_Left:
                self.previous_model()

            case Qt.Key.Key_Right:
                self.next_model()

    def resizeEvent(self, event: QResizeEvent):
        self.widgets['name'].setFixedWidth(self.width() // 2)
        super().resizeEvent(event)
