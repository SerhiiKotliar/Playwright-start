from PySide6.QtCore import QLocale
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QDialog, QSpinBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QWidget, QGroupBox,
    QComboBox, QCheckBox, QScrollArea
)

# ---- Форма ввода конфигурации ----
class ConfigInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Конфігурація груп")
        self.resize(400, 200)

        main_layout = QVBoxLayout(self)

        # количество групп
        cnt_layout = QHBoxLayout()
        cnt_layout.addWidget(QLabel("Кількість груп:"))
        self.spin = QSpinBox()
        self.spin.setMinimum(1)
        self.spin.setMaximum(20)
        cnt_layout.addWidget(self.spin)
        main_layout.addLayout(cnt_layout)

        # контейнер для полей title/name
        self.entries_layout = QVBoxLayout()
        main_layout.addLayout(self.entries_layout)

        # кнопки
        btn_layout = QHBoxLayout()
        self.btnOK = QPushButton("OK")
        self.btnCnl = QPushButton("Скасувати")
        btn_layout.addWidget(self.btnOK)
        btn_layout.addWidget(self.btnCnl)
        main_layout.addLayout(btn_layout)

        self.spin.valueChanged.connect(self.update_entries)
        self.btnOK.clicked.connect(self.accept)
        self.btnCnl.clicked.connect(self.reject)

        self.update_entries()

    def update_entries(self):
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
        return [{"title": t.text(), "name": n.text()} for t, n in self.line_edits]


# ---- Wrapper для удобного обращения ----
class GroupBoxWrapper:
    def __init__(self, gb, cmb, chkb, btn):
        self.gb = gb
        self.cmb = cmb
        self.chkb = chkb
        self.btn = btn

    def set_geometry(self, cmb_geom=None, chkb_geom=None, btn_geom=None):
        if cmb_geom:
            self.cmb.setGeometry(*cmb_geom)
        if chkb_geom:
            self.chkb.setGeometry(*chkb_geom)
        if btn_geom:
            self.btn.setGeometry(*btn_geom)


# ---- Динамическая форма ----
class DynamicDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Введення даних для тестів")
        self.resize(650, 500)

        main_layout = QVBoxLayout(self)

        # ---- Scroll area для GroupBox ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        scroll_content = QWidget()
        scroll.setWidget(scroll_content)

        self.scroll_layout = QVBoxLayout(scroll_content)

        # создаём GroupBox
        self.gb = {}
        for cfg in config:
            title = cfg.get("title", "")
            name = cfg.get("name", "")

            gb_widget = QGroupBox(title, scroll_content)
            gb_widget.setObjectName(name)
            gb_widget.setStyleSheet("background-color: rgb(85, 255, 127);")
            gb_widget.setLocale(QLocale(QLocale.Ukrainian, QLocale.Ukraine))
            gb_widget.setMinimumHeight(60)

            # элементы
            cmb = QComboBox(gb_widget)
            chkb = QCheckBox("Обов'язкове", gb_widget)
            btn = QPushButton("Правила", gb_widget)

            # стандартная геометрия
            cmb.setGeometry(10, 20, 200, 25)
            chkb.setGeometry(220, 20, 120, 25)
            btn.setGeometry(350, 15, 100, 30)

            self.scroll_layout.addWidget(gb_widget)

            self.gb[name] = GroupBoxWrapper(gb_widget, cmb, chkb, btn)

        # ---- Кнопки OK/Відміна внизу ----
        btn_layout = QHBoxLayout()
        font = QFont()
        font.setBold(True)

        self.btnOK = QPushButton("Введення")
        self.btnOK.setFont(font)
        self.btnCnl = QPushButton("Відміна")
        self.btnCnl.setFont(font)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btnOK)
        btn_layout.addWidget(self.btnCnl)
        main_layout.addLayout(btn_layout)


# ---- Основной запуск ----
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    input_dlg = ConfigInputDialog()
    if input_dlg.exec() == QDialog.Accepted:
        config = input_dlg.get_config()
        dlg = DynamicDialog(config)
        dlg.show()

        # пример изменения размеров элементов
        dlg.gb["group1"].set_geometry(cmb_geom=(10, 10, 250, 30),
                                      chkb_geom=(270, 10, 150, 30),
                                      btn_geom=(430, 10, 120, 30))

    sys.exit(app.exec())
