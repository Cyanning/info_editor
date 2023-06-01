from collections import OrderedDict
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import model.bodyfactory as factory
from configuration import *
from interface import preview, search, display, datapanel


class MainWindow(QMainWindow):
    def __init__(self):
        # Window settings
        super().__init__(None)
        self.__init_size()
        self.setWindowTitle("信息编辑器")
        self.setWindowIcon(QIcon(RTPATH + "cache/icon.png"))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.widgets = OrderedDict()  # Widgets dict with ordered
        self.assist_window = display.DisplayWindow(self)  # Auxiliary window
        self.__setup_interface()

        # Main interface layout
        layout_rows = [QHBoxLayout() for _ in range(4)]  # One layout per line
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

        # Overall layout and widget
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        widget = QWidget(self)
        for row in layout_rows:
            layout.addLayout(row)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Initialize loading model
        self.model = factory.load_cache_model()
        self.load_model()

    def __setup_interface(self):
        # Model's ID input/display
        self.widgets['modelid'] = QSpinBox(None)
        self.widgets['modelid'].setMinimum(100000)
        self.widgets['modelid'].setMaximum(2119999)
        self.widgets['modelid'].setFixedWidth(100)
        self.widgets['modelid'].setAlignment(Qt.AlignmentFlag.AlignRight)

        # Display model name
        self.widgets['name'] = QLineEdit("模型名字")
        self.widgets['name'].setReadOnly(True)
        self.widgets['name'].setFrame(False)
        self.widgets['name'].setFixedWidth(self.width() // 2)
        # Gender icon in name
        self.widgets['gender_icon'] = QAction()
        self.widgets['name'].addAction(self.widgets['gender_icon'], QLineEdit.ActionPosition.LeadingPosition)

        # Export current data
        self.widgets['export'] = QPushButton("管理数据")
        self.widgets['export'].clicked.connect(self.management_database)

        # Save current data
        self.widgets['save'] = QPushButton("保  存")
        self.widgets['save'].clicked.connect(self.save_info)

        # Jump to the model with the specified id
        self.widgets['jump'] = QPushButton("跳转")
        self.widgets['jump'].clicked.connect(self.jump_model)

        # Switch to previous
        self.widgets['pervious'] = QPushButton("上一条")
        self.widgets['pervious'].clicked.connect(self.previous_model)

        # Switch to next
        self.widgets['next'] = QPushButton("下一条")
        self.widgets['next'].clicked.connect(self.next_model)

        # Search for models to edit
        self.widgets['search'] = QPushButton("搜索")
        self.widgets['search'].clicked.connect(self.specify_model_from_search)

        # Information edit box
        self.widgets['info'] = QPlainTextEdit()
        self.widgets['info'].setFrameShape(QFrame(self.widgets['info']).frameShape().WinPanel)

        # Sentence display box
        self.widgets['sentence'] = QListWidget(self)
        self.widgets['sentence'].setWordWrap(True)
        self.widgets['sentence'].setFrameShape(QFrame(self.widgets['sentence']).frameShape().WinPanel)
        self.widgets['sentence'].setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        # Load original information
        self.widgets['addoldinfo'] = QPushButton("显示原始数据", self)
        self.widgets['addoldinfo'].clicked.connect(self.show_oldinfo_context)

        # Load from searched model information
        self.widgets['addinfo'] = QPushButton("添加其他信息", self)
        self.widgets['addinfo'].clicked.connect(self.add_sentences_from_search)

        # Split the current message by sentence
        self.widgets['split'] = QPushButton("拆分信息")
        self.widgets['split'].clicked.connect(self.load_sentences_list)

        # Associate the current sentence with other models
        self.widgets['assignment'] = QPushButton("关联其他模型")
        self.widgets['assignment'].clicked.connect(self.sentence_put_others)

        # Set fonts in batches
        font = self.font()
        font.setFamily(UI_FONTFAMILY)
        font.setPointSize(UI_FONTSIZE)
        for key in self.widgets:
            self.widgets[key].setFont(font)
            # Set focus policy
            if key not in ('gender_icon',):
                self.widgets[key].setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def __init_size(self):
        """
        Initial coordinates, initial size.
        """
        desk = QApplication.primaryScreen().geometry()
        w, h = desk.width(), desk.height()
        sizes = map(int, (w / 4, h / 2 - w / 6, w / 2, w / 3))
        self.setGeometry(*sizes)

    def load_model(self):
        """
        Load model data.
        """
        self.widgets['gender_icon'].setIcon(QIcon(GENDERS[self.model.gender]))
        self.widgets['name'].setText(self.model.name)
        self.widgets['modelid'].setValue(self.model.value)
        self.widgets['info'].setPlainText(self.model.paragraph)
        self.display_sentences_list()

    def display_sentences_list(self):
        """
        Show sentence list.
        """
        self.widgets['sentence'].clear()
        for i, item in enumerate(self.model, start=1):
            self.widgets['sentence'].addItem(f"{i}. {item.value}")

    def previous_model(self):
        value = self.model.value
        self.changed_model(value, -1)

    def next_model(self):
        value = self.model.value
        self.changed_model(value, 1)

    def jump_model(self):
        value = self.widgets['modelid'].value()
        self.changed_model(value, 0)

    def changed_model(self, value, direction):
        """
        Switch the front and back models, or jump to the specified model.
        """
        try:
            self.model = factory.create_next_value(value, direction)
            self.load_model()
        except AssertionError:
            QMessageBox().warning(self, "警告", "Id 格式错误。")

    def specify_model_from_search(self):
        """
        Search model and jump.
        """
        try:
            modelvals = self.search_model(False)
            self.model = factory.create_by_value(modelvals)
            self.load_model()
        except AssertionError:
            return

    def save_info(self):
        """
        Save information（Sentence shall prevail.
        """
        if not self.warning("确定以当前所填内容保存吗？"):
            return
        try:
            self.model.paragraph = self.widgets['info'].toPlainText()
            factory.saving_model_basedon_paragraph(self.model)
        except Exception as e:
            QMessageBox().critical(self, "错误", f"保存信息发生错误。\n错误原因：\n{e}")
        else:
            QMessageBox().information(self, "Good", "保存成功！")
        finally:
            self.model = factory.create_by_value(self.model.value)
            self.load_model()

    def add_sentences_from_search(self):
        """
        Add sentences, information from database.
        """
        try:
            value = self.search_model(False)
            sentences = factory.produce_sentences_by_value(value)
            self.model.add_into_paragraph(sentences)
            self.widgets['info'].appendPlainText(self.model.paragraph)
        except AssertionError:
            QMessageBox().warning(self, "警告", "没有信息可以被添加。")
        except Exception as e:
            QMessageBox().critical(self, "错误", f"错误原因：\n{e}")

    def load_sentences_list(self):
        """
        Split sentences.
        """
        try:
            self.model.paragraph = self.widgets['info'].toPlainText()
            self.model.convert_into_sentences()
            self.display_sentences_list()
        except AssertionError:
            QMessageBox().critical(self, "错误", f"内容为空白。")

    def sentence_put_others(self):
        """
        Add sentences for other models.
        """
        try:
            # 获取句子对象
            sentences = [self.model[i.row()] for i in self.widgets['sentence'].selectedIndexes()]
            assert len(sentences) > 0
            # 将句子关联到选中的模型中
            modelvals = self.search_model(True)
            models = []
            for item in modelvals:
                model_item = factory.create_by_value(item)
                model_item.add_into_sentences(sentences)
                model_item.convert_for_paragraph()
                models.append(model_item)
            # 生成所有模型信息的预览， 等待确认
            agree_preview = preview.PreviewWindow(self, models)
            if agree_preview.exec():
                for model_item in models:
                    factory.saving_model(model_item)
                QMessageBox().information(self, "Good", "关联成功！")
        except AssertionError:
            QMessageBox().critical(self, "错误", f"请做出完整的选择。")
        except Exception as e:
            QMessageBox().critical(self, "错误", f"添加句子发生错误。\n错误原因：\n{e}")

    def search_model(self, open_multi: bool):
        """
        Common callback method of search window.
        :param open_multi: False is radio；True is multiple choice
        """
        keywords = self.model.name
        if keywords[-1] == '）':
            keywords = keywords[:keywords.index('（')]
        popup = search.SearchWindow(self, keywords, multi_mode=open_multi)
        popup.exec()
        modelvals = popup.get_selected_models
        assert len(modelvals)
        return modelvals if open_multi else modelvals[0]

    def show_oldinfo_context(self):
        """
        Show old info data.
        """
        if self.assist_window.isVisible():
            self.assist_window.hide()
        else:
            self.assist_window.display_info(self.model)
            self.assist_window.show()

    def management_database(self):
        """
        Popup of manage data.
        """
        manager = datapanel.DatePanel(self)
        manager.exec()

    def warning(self, context: str) -> bool:
        """
        Generic confirmation popup.
        """
        font = self.font()
        font.setPointSize(UI_FONTSIZE)
        font.setFamily(UI_FONTFAMILY)

        sure = QMessageBox(self)
        sure.setFont(font)
        sure.setIcon(QMessageBox.Icon.Warning)
        sure.setWindowTitle("Confirmation")
        sure.setText(context)
        sure.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        sure.setDefaultButton(QMessageBox.StandardButton.Cancel)

        flag = sure.exec() == QMessageBox.StandardButton.Ok
        return flag

    def closeEvent(self, event: QCloseEvent):
        """
        Rewrite the window close event.
        """
        if self.warning("退出前确认是否保存。\n确认退出？\n"):
            del self.assist_window
            factory.write_cache_model(self.model.value)
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        """
        Rewrite the key response event.
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
        """
        Rewind window size change event.
        """
        self.widgets['name'].setFixedWidth(self.width() // 2)
        super().resizeEvent(event)
