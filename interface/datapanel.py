from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import model.bodyfactory as factory
from configuration import (
    UI_FONTFAMILY, UI_FONTSIZE, SYSTEMS
)


class DatePanel(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle("管理数据")
        self.setMinimumWidth(int(parent.width() / 2))

        self.system_list = QComboBox(self)
        self.gender_boxes = [QCheckBox(), QCheckBox()]

        self.lab = QLabel("当前完成度：")
        self.progress_bar = QProgressBar(self)

        self.export_data = QPushButton("导出数据")
        self.import_data = QPushButton("导入数据")
        self.export_lost = QPushButton("导出未录数据")

        layout0 = QHBoxLayout()
        layout0.addWidget(self.system_list)
        for v in self.gender_boxes:
            layout0.addWidget(v)
        layout0.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout1 = QVBoxLayout()
        layout1.addWidget(self.lab)
        layout1.addWidget(self.progress_bar)
        layout1.setContentsMargins(0, 10, 0, 0)

        layout2 = QHBoxLayout()
        layout2.addWidget(self.export_data)
        layout2.addWidget(self.import_data)
        layout2.addWidget(self.export_lost)
        layout2.setContentsMargins(0, 10, 0, 0)

        layout_ = QVBoxLayout()
        layout_.addLayout(layout0)
        layout_.addLayout(layout1)
        layout_.addLayout(layout2)
        layout_.setContentsMargins(20, 10, 20, 20)

        self.setLayout(layout_)
        self._style()
        self.gender_boxes[0].setChecked(True)
        self.show_progress()

    def _style(self):
        font = self.font()
        font.setFamily(UI_FONTFAMILY)
        font.setPointSize(UI_FONTSIZE)

        self.system_list.addItems(SYSTEMS)
        self.system_list.currentIndexChanged.connect(self.show_progress)
        self.system_list.setFont(font)
        self.system_list.setFixedWidth(150)

        for i, checkbox in enumerate(self.gender_boxes):
            checkbox.setIcon(QIcon(GENDERS[i]))
            checkbox.setFont(font)
            checkbox.setFixedWidth(50)
            checkbox.clicked.connect(self.show_progress)

        self.lab.setFont(font)

        self.progress_bar.setFont(font)
        self.progress_bar.resize(300, 20)
        self.progress_bar.setRange(0, 100)

        self.export_data.setFont(font)
        self.export_data.clicked.connect(self.export_database)

        self.import_data.setFont(font)
        self.import_data.clicked.connect(self.import_database)

        self.export_lost.setFont(font)

    def show_progress(self):
        sysid = self.system_list.currentIndex() - 1
        male = self.gender_boxes[0].checkState() == Qt.CheckState.Checked
        if male ^ (self.gender_boxes[1].checkState() == Qt.CheckState.Checked):
            gender = 0 if male else 1
        else:
            gender = None
        self.progress_bar.setValue(factory.percentage_of_progress_completed(gender, sysid))

    def export_database(self):
        try:
            filepath = QFileDialog(self).getExistingDirectory(self, "选择存储路径")
            if len(filepath):
                factory.export_database_json(filepath)
                QMessageBox().information(self, "Good", "导出成功！")
        except Exception as e:
            QMessageBox().critical(self, "Error", f"导出数据发生错误。\n错误原因：\n{e}")

    def import_database(self):
        try:
            filepath = QFileDialog(self).getExistingDirectory(self, "选择存储路径")
            if len(filepath):
                statistics = factory.import_database_from_json(filepath)
                contents = (f"{item} 表成功导入 {statistics[item]} 条数据" for item in statistics)
                QMessageBox().information(self, "Good", "；\n".join(contents) + '。')
        except Exception as e:
            QMessageBox().critical(self, "Error", f"导入数据发生错误。\n错误原因：\n{e}")
