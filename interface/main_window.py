from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from interface.preview import PreviewWindow
from interface.search import SearchWindow
from interface.display import DisplayWindow
from interface.datapanel import DatePanel
from factory.bodyfactory import BodyFactory, write_cache_model, load_cache_model
from configuration import (
    WINDOW_ICON_PATH, UI_FONTFAMILY, UI_FONTSIZE, GENDERS
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(None)
        # Window settings
        desk = QApplication.primaryScreen().geometry()
        w, h = desk.width(), desk.height()
        sizes = map(int, (w / 4, h / 2 - w / 6, w / 2, w / 3))
        self.setGeometry(*sizes)
        self.setWindowTitle("信息编辑器")
        self.setWindowIcon(QIcon(WINDOW_ICON_PATH))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Auxiliary window
        self.assist_window = DisplayWindow(self)

        # UI widgets
        self.widgets = {}
        self.widget_keys = [
            ['modelid', 'name', 'export', 'save'],
            ['jump', 'pervious', 'next', 'search'],
            ['info', 'sentence'],
            ['addoldinfo', 'addinfo', 'split', 'assignment']
        ]
        self.__add_widgets()

        # Set fonts,focus policy
        font = QFont(UI_FONTFAMILY, UI_FONTSIZE)
        for key, widget in self.widgets.items():
            widget.setFont(font)
            if key != "gender_icon":
                widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        # Layout
        main_layout = QVBoxLayout()
        for row in self.widget_keys:
            row_layout = QHBoxLayout()
            for kw in row:
                row_layout.addWidget(self.widgets[kw])
            main_layout.addLayout(row_layout)
        main_widget = QWidget(None)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Initialize model
        value = load_cache_model()
        if value is None:
            value = 100000
        self.factory = BodyFactory()
        self.body = self.factory.create_by_value(value)
        self.load_model()

    def __add_widgets(self):
        # Model's ID input/display
        self.widgets['modelid'] = QSpinBox(None)
        self.widgets['modelid'].setMinimum(100000)
        self.widgets['modelid'].setMaximum(2119999)
        self.widgets['modelid'].setFixedWidth(100)
        self.widgets['modelid'].setAlignment(Qt.AlignmentFlag.AlignRight)

        # Display model name
        self.widgets['name'] = QLineEdit()
        self.widgets['name'].setReadOnly(True)
        self.widgets['name'].setFrame(False)
        self.widgets['name'].setFixedWidth(self.width() // 2)

        # Gender icon
        self.widgets['gender_icon'] = QAction()  # Gender icon on name
        self.widgets['gender_icon'].triggered.connect(self.change_gender)
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

    def load_model(self):
        """
        Load model data.
        """
        self.widgets['gender_icon'].setIcon(QIcon(GENDERS[self.body.gender()]))
        self.widgets['name'].setText(self.body.name)
        self.widgets['modelid'].setValue(self.body.value)
        self.widgets['info'].setPlainText(self.body.paragraph)
        self.display_sentences_list()

    def display_sentences_list(self):
        """
        Show sentence list.
        """
        self.widgets['sentence'].clear()
        for i, item in enumerate(self.body, start=1):
            self.widgets['sentence'].addItem(f"{i}. {item.value}")

    def previous_model(self):
        self.body = self.factory.setup_model(self.body.value, direction=-1)
        self.load_model()

    def next_model(self):
        self.body = self.factory.setup_model(self.body.value, direction=1)
        self.load_model()

    def jump_model(self):
        try:
            value = self.widgets['modelid'].value()
            self.body = self.factory.setup_model(value=value)
            self.load_model()
        except ValueError:
            QMessageBox().warning(self, "警告", "Id 格式错误。")

    def specify_model_from_search(self):
        """
        Search model and jump.
        """
        try:
            modelvals = self.search_model_single()
            self.body = self.factory.setup_model(value=modelvals)
            self.load_model()
        except AssertionError:
            pass

    def save_info(self):
        """
        Save information（Sentence shall prevail.
        """
        if self.warning("确定以当前所填内容保存吗？"):
            try:
                self.body.paragraph = self.widgets['info'].toPlainText()
                if len(self.body.paragraph) == 0:
                    self.body.clean_sentences()
                else:
                    self.body.convert_into_sentences()
            except Exception as e:
                QMessageBox().critical(self, "错误", f"保存信息发生错误。\n错误原因：\n{e}")
            else:
                QMessageBox().information(self, "Good", "保存成功！")
                write_cache_model(self.body.value)
            finally:
                self.body = self.factory.setup_model(value=self.body.value)
                self.load_model()

    def add_sentences_from_search(self):
        """
        Add sentences, information from database.
        """
        try:
            value = self.search_model_single()
            sentences = self.factory.produce_sentences_by_value(value)
            self.body.add_into_paragraph(sentences)
            self.widgets['info'].appendPlainText(self.body.paragraph)
        except AssertionError:
            QMessageBox().warning(self, "警告", "没有信息可以被添加。")
        except Exception as e:
            QMessageBox().critical(self, "错误", f"错误原因：\n{e}")

    def load_sentences_list(self):
        """
        Split sentences.
        """
        try:
            self.body.paragraph = self.widgets['info'].toPlainText()
            self.body.convert_into_sentences()
            self.display_sentences_list()
        except AssertionError:
            QMessageBox().critical(self, "错误", f"内容为空白。")

    def sentence_put_others(self):
        """
        Add sentences for other models.
        """
        try:
            # 获取句子对象
            sentences = [self.body[i.row()] for i in self.widgets['sentence'].selectedIndexes()]
            assert len(sentences) > 0
            # 将句子关联到选中的模型中
            modelvals = self.search_model_multi()
            models = []
            for item in modelvals:
                model_item = self.factory.create_by_value(item)
                model_item.add_into_sentences(sentences)
                model_item.convert_for_paragraph()
                models.append(model_item)
            # 生成所有模型信息的预览， 等待确认
            agree_preview = PreviewWindow(self, models)
            if agree_preview.exec():
                for model_item in models:
                    self.factory.saving_model(model_item)
                QMessageBox().information(self, "Good", "关联成功！")
        except AssertionError:
            QMessageBox().critical(self, "错误", f"请做出完整的选择。")
        except Exception as e:
            QMessageBox().critical(self, "错误", f"添加句子发生错误。\n错误原因：\n{e}")

    def search_model_single(self):
        """
        Common callback method of search window with single select.
        """
        popup = SearchWindow(self, self.factory, multi_mode=False)
        popup.exec()
        modelvals = popup.get_selected_models()
        assert len(modelvals)
        return modelvals[0]

    def search_model_multi(self):
        """
        Common callback method of search window with multi select.
        """
        popup = SearchWindow(self, self.factory, multi_mode=True)
        popup.exec()
        modelvals = popup.get_selected_models()
        assert len(modelvals)
        return modelvals

    def show_oldinfo_context(self):
        """
        Show old info data.
        """
        if self.assist_window.isVisible():
            self.assist_window.hide()
        else:
            self.assist_window.display_info(self.factory, self.body)
            self.assist_window.show()

    def management_database(self):
        """
        Popup of manage data.
        """
        manager = DatePanel(self, self.factory)
        manager.exec()

    def change_gender(self):
        """
        Change opposite gender with same name.
        """
        for model_res in self.factory.produce_by_search(self.body.name, None, 0):
            if model_res.name == self.body.name and model_res.gender() != self.body.gender():
                self.body = self.factory.create_by_value(model_res.value)
                self.load_model()
                break

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
            write_cache_model(self.body.value)
            self.factory.close()
            del self.assist_window
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
