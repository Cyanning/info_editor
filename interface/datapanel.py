from PyQt6.QtWidgets import *
from model.bodyfactory import *


class DatePanel(QDialog):
    def __init__(self):
        super().__init__(None)
        self.setWindowTitle("管理数据")
        self.setMinimumWidth(400)

        self.system_list = QComboBox(self)
        self.system_list.addItems(SYSTEMS)
        self.system_list.currentIndexChanged.connect(self.show_progress)
        self.lab = QLabel("的当前完成度")

        self.progress_bar = QProgressBar()
        self.progress_bar.resize(300, 20)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)

        self.export_sys = QPushButton("导出当前系统数据")
        self.export_sys.clicked.connect(self.export_sys_database)
        self.export_all = QPushButton("导出所有系统数据")
        self.export_all.clicked.connect(self.export_all_database)

        layout0 = QHBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()

        layout0.addWidget(self.system_list)
        layout0.addWidget(self.lab)

        layout1.addWidget(self.progress_bar)

        layout2.addWidget(self.export_sys)
        layout2.addWidget(self.export_all)

        layout_ = QVBoxLayout()
        layout_.addLayout(layout0)
        layout_.addLayout(layout1)
        layout_.addLayout(layout2)
        self.setLayout(layout_)
        self._style()

    def _style(self):
        font = self.font()
        font.setFamily(UI_FONTFAMILY)
        font.setPointSize(UI_FONTSIZE)
        self.system_list.setMaximumWidth(150)
        self.system_list.setFont(font)
        self.lab.setFont(font)
        self.progress_bar.setFont(font)
        self.export_sys.setFont(font)
        self.export_all.setFont(font)

    def show_progress(self):
        pass

    def export_sys_database(self):
        pass

    def export_all_database(self):
        try:
            filepath = QFileDialog(self).getExistingDirectory(self, "选择存储路径")
            export_database_to_json(filepath)
        except Exception as e:
            QMessageBox().critical(self, "错误", f"导出数据发生错误。\n错误原因：\n{e}")
        else:
            QMessageBox().information(self, "Good", "导出成功！")
