from collections import OrderedDict
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from assistInterface import DisplayWindow, SearchWindow, PreviewWindow
from main import *


class MainWindow(QMainWindow):
    def __init__(self):
        # 窗口设置
        super().__init__(None)
        self.setGeometry(*self.init_size())
        self.setWindowTitle("信息编辑器")
        self.setWindowIcon(QIcon("cache/icon.png"))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.menuitems = OrderedDict()  # 菜单
        self.widgets = OrderedDict()  # 组件
        self.assist_window = DisplayWindow(self.x(), self.y(), self.height())  # 辅助窗口

        # 菜单栏容器
        self.__setup_menubar()
        my_menu = self.menuBar().addMenu("设置")
        for key in self.menuitems:
            my_menu.addAction(self.menuitems[key])

        # 主界面布局
        self.__setup_main()
        layout_rows = [QHBoxLayout() for _ in range(4)]  # 每行一个布局器
        for key in self.widgets:
            match key:
                case 'modelid' | 'name' | 'save':
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

    def __setup_menubar(self):
        self.menuitems['upload'] = QAction("同步到共享")
        self.menuitems['upload'].setIcon(QIcon("cache/upload.png"))
        # self.menuitems['upload'].triggered.connect(self.upload_share_database)

        self.menuitems['download'] = QAction("同步到本地")
        self.menuitems['download'].setIcon(QIcon("cache/download.png"))
        # self.menuitems['download'].triggered.connect(self.download_share_database)

        self.menuitems['clean_db'] = QAction("清理数据库")
        self.menuitems['clean_db'].setIcon(QIcon("cache/delete.png"))
        self.menuitems['clean_db'].triggered.connect(self.clean_unusable_of_attribution)

        self.menuitems['quit'] = QAction("退出")
        self.menuitems['quit'].setIcon(QIcon("cache/quit.png"))
        self.menuitems['quit'].triggered.connect(self.closeEvent)

    def __setup_main(self):
        # 模型id输入\显示
        self.widgets['modelid'] = QSpinBox(None)
        self.widgets['modelid'].setMinimumWidth(100)
        self.widgets['modelid'].setMinimum(100000)
        self.widgets['modelid'].setMaximum(2119999)

        # 显示模型名字
        self.widgets['name'] = QLineEdit("模型名字")
        self.widgets['name'].setReadOnly(True)
        self.widgets['name'].setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 保存当前数据
        self.widgets['save'] = QPushButton("保 存")
        self.widgets['save'].clicked.connect(self.save_info)
        self.widgets['save'].setMinimumWidth(100)

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
        font.setPointSize(12)
        for key in ('modelid', 'name', 'save'):
            self.widgets[key].setFont(font)

        font.setPointSize(10)
        for key in ('info', 'sentence'):
            self.widgets[key].setFont(font)

        # 批量设置焦点策略
        for key in self.widgets:
            self.widgets[key].setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def load_model(self):
        """
        载入模型数据
        """
        if self.assist_window.isVisible():
            self.assist_window.display_info(self.model)
        self.widgets['name'].setText(self.model.name)
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
            question = QMessageBox()
            question.setWindowTitle("添加其他信息")
            question.setText("选择信息来源。")
            question.addButton("新编辑的信息", QMessageBox().ButtonRole.ActionRole)
            question.addButton("CA上的信息", QMessageBox().ButtonRole.ActionRole)
            question.setStyleSheet("QPushButton {width: 100px; height: 20px}")
            match question.exec():
                case 0:
                    # 第0个按钮，从新数据表加载
                    sentences = produce_sentences_by_value(value)
                    self.model.add_into_paragraph(sentences)
                    self.widgets['info'].appendPlainText(self.model.paragraph)
                case 1:
                    # 第1个按钮，从老信息字段加载
                    paragraph = get_old_info(value)
                    self.widgets['info'].appendPlainText(paragraph)
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

            agree_preview = PreviewWindow(models, self)
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
        popup = SearchWindow(keywords, parent=self, multi_mode=multi)
        popup.exec()
        modelvals = popup.get_selected_models
        assert len(modelvals)
        return modelvals if multi else modelvals[0]

    def clean_unusable_of_attribution(self):
        """
        清理数据句子表
        """
        try:
            answer = QMessageBox().question(
                self, "再次确认", "此行为将会清理没有关联上任何模型的信息。\n\n确定要清理数据库？")
            assert answer == QMessageBox().StandardButton.Yes
            clean_table_of_attribution()
        except AssertionError:
            pass
        except Exception as e:
            QMessageBox().critical(self, "错误", f"清理失败！\n原因：{e}")
        else:
            QMessageBox().information(self, "Good", "清理成功！")

    def upload_share_database(self):
        """
        上传
        """
        try:
            answer = QMessageBox().question(
                self, "再次确认", "同步到共享是指将本地数据上传到\n共享数据库，不会删除本地文件。\n\n确定要同步到共享？")
            if answer == QMessageBox().StandardButton.Yes:
                num = sync_share_database(True)
            else:
                return
        except Exception as e:
            QMessageBox().critical(self, "错误", f"上传失败！\n原因：{e}")
        else:
            QMessageBox().information(self, "Good", "成功上传%d条数据！" % num)

    def download_share_database(self):
        """
        下载
        """
        try:
            answer = QMessageBox().question(
                self, "再次确认", "同步到本地是指将共享数据下载到\n本地数据库，不会删除本地文件。\n\n确定要同步到本地？")
            if answer == QMessageBox().StandardButton.Yes:
                num = sync_share_database(False)
            else:
                return
        except Exception as e:
            QMessageBox().critical(self, "错误", f"下载失败！\n原因：{e}")
        else:
            QMessageBox().information(self, "Good", "成功下载%d条数据！" % num)

    def show_oldinfo_context(self):
        """
        显示旧info数据
        """
        if self.assist_window.isVisible():
            self.assist_window.hide()
        else:
            self.assist_window.display_info(self.model)
            self.assist_window.show()

    def closeEvent(self, event: QCloseEvent):
        """
        重写窗口关闭事件
        """
        del self.assist_window
        write_cache_model(self.model.value)
        event.accept()

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

    @staticmethod
    def init_size() -> Iterable:
        """
        :return:返回符合Geometry函数格式的初始坐标，初始尺寸
        """
        desk = QApplication.primaryScreen().geometry()
        w = desk.width()
        h = desk.height()
        size = [w / 2 - 400, h / 2 - 300, w * 0.4, h * 0.55]
        return map(int, size)
