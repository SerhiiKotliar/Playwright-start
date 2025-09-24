from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QSpinBox,
    QLabel, QLineEdit, QPushButton, QWidget
)


class ConfigInputDialog(QDialog):
    """Форма для ввода конфигурации GroupBox-ов"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Конфігурація груп")
        self.resize(400, 200)

        self.main_layout = QVBoxLayout(self)

        # Количество групп
        cnt_layout = QHBoxLayout()
        cnt_layout.addWidget(QLabel("Кількість груп:"))
        self.spin = QSpinBox()
        self.spin.setMinimum(1)
        self.spin.setMaximum(20)
        cnt_layout.addWidget(self.spin)
        self.main_layout.addLayout(cnt_layout)

        # Контейнер для полей title/name
        self.entries_layout = QVBoxLayout()
        self.main_layout.addLayout(self.entries_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btnOK = QPushButton("OK")
        self.btnCnl = QPushButton("Скасувати")
        btn_layout.addWidget(self.btnOK)
        btn_layout.addWidget(self.btnCnl)
        self.main_layout.addLayout(btn_layout)

        # Связи
        self.spin.valueChanged.connect(self.update_entries)
        self.btnOK.clicked.connect(self.accept)
        self.btnCnl.clicked.connect(self.reject)

        self.update_entries()

    def update_entries(self):
        """Создаем/обновляем поля для ввода title и name"""
        # очистить старые
        for i in reversed(range(self.entries_layout.count())):
            widget = self.entries_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.line_edits = []
        for i in range(self.spin.value()):
            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.addWidget(QLabel(f"Group {i+1} Title:"))
            title_edit = QLineEdit(f"Група {i+1}")
            h_layout.addWidget(title_edit)

            h_layout.addWidget(QLabel("Name:"))
            name_edit = QLineEdit(f"group{i+1}")
            h_layout.addWidget(name_edit)

            self.entries_layout.addWidget(container)
            self.line_edits.append((title_edit, name_edit))

    def get_config(self):
        """Возвращает список конфигураций"""
        config = []
        for title_edit, name_edit in self.line_edits:
            config.append({"title": title_edit.text(), "name": name_edit.text()})
        return config


# ---------------- Динамическая форма из предыдущего примера ----------------

from PySide6.QtCore import QLocale
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QCheckBox, QPushButton


class GroupBoxWrapper:
    def __init__(self, gb, cmb, chkb, btn):
        self.gb = gb
        self.cmb = cmb
        self.chkb = chkb
        self.btn = btn


class DynamicDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Введення даних для тестів")
        self.resize(600, 120 + 70 * len(config))

        main_layout = QVBoxLayout(self)
        self.gb = {}

        for cfg in config:
            title = cfg.get("title", "")
            name = cfg.get("name", "")

            gb_widget = QGroupBox(title, self)
            gb_widget.setObjectName(name)
            gb_widget.setStyleSheet("background-color: rgb(85, 255, 127);")
            gb_widget.setLocale(QLocale(QLocale.Ukrainian, QLocale.Ukraine))

            layout = QHBoxLayout(gb_widget)

            cmb = QComboBox(gb_widget)
            cmb.setStyleSheet("background-color: white;")
            layout.addWidget(cmb)

            chkb = QCheckBox("Обов'язкове", gb_widget)
            layout.addWidget(chkb)

            btn = QPushButton("Правила", gb_widget)
            layout.addWidget(btn)

            main_layout.addWidget(gb_widget)

            self.gb[name] = GroupBoxWrapper(gb_widget, cmb, chkb, btn)

        # OK/Cancel
        btn_layout = QHBoxLayout()
        font = QFont()
        font.setBold(True)

        self.btnOK = QPushButton("Введення", self)
        self.btnOK.setFont(font)
        btn_layout.addWidget(self.btnOK)

        self.btnCnl = QPushButton("ВІДМІНА", self)
        self.btnCnl.setFont(font)
        btn_layout.addWidget(self.btnCnl)

        main_layout.addLayout(btn_layout)


# ---------------- Основной запуск ----------------

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    input_dlg = ConfigInputDialog()
    if input_dlg.exec() == QDialog.Accepted:
        config = input_dlg.get_config()
        dlg = DynamicDialog(config)
        dlg.show()

    sys.exit(app.exec())
#     gljhgkjhgkjhg
