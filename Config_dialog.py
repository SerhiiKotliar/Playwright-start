from PySide6.QtWidgets import (
    QApplication, QDialog, QSpinBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QWidget, QGroupBox,
    QComboBox, QCheckBox, QMessageBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt

# ---- Форма ввода конфигурации ----
class ConfigInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.current_widgets = None
        self.setWindowTitle("Конфігурація перевірки полів")
        self.resize(400, 200)

        self.txt_spin_previous = 0
        self.config_data = []

        main_layout = QVBoxLayout(self)

        # количество групп
        cnt_layout = QHBoxLayout()
        cnt_layout.addWidget(QLabel("Кількість полів:"))
        self.spin = QSpinBox()
        self.spin.setMinimum(0)
        self.spin.setMaximum(20)
        cnt_layout.addWidget(self.spin)
        main_layout.addLayout(cnt_layout)

        # контейнер для полей title/name
        self.entries_layout = QVBoxLayout()
        main_layout.addLayout(self.entries_layout)

        # === Фіксація вводу у поле ===
        label_fix = QLabel("Фіксація введених даних у кожне поле")
        main_layout.addWidget(label_fix)

        # === Радиокнопки ===
        radio_layout = QHBoxLayout()
        self.radio_event = QRadioButton("Подія")
        self.radio_enter = QRadioButton("\"Enter\"")
        self.radio_button = QRadioButton("Кнопка")

        # Группируем радиокнопки, чтобы только одна могла быть выбрана
        radio_group = QButtonGroup(self)
        radio_group.addButton(self.radio_event)
        radio_group.addButton(self.radio_enter)
        radio_group.addButton(self.radio_button)

        # По умолчанию выбрана первая
        self.radio_event.setChecked(True)

        radio_layout.addWidget(self.radio_event)
        radio_layout.addWidget(self.radio_enter)
        radio_layout.addWidget(self.radio_button)
        main_layout.addLayout(radio_layout)

        # === Перевірка помилки ===
        label_check_error = QLabel("Перевірка помилки у введених у поле даних")
        main_layout.addWidget(label_check_error)

        # === Атрибут ===
        label_attr = QLabel("Атрибут сповіщувача про помилку")
        main_layout.addWidget(label_attr)

        # === Поле вводу для атрибута ===
        self.attr_input = QLineEdit()
        # self.attr_input.setText('//*[@id="error_1_id_text_string"]')
        main_layout.addWidget(self.attr_input)

        # === Остаточна фіксація ===
        label_final_fix = QLabel("Остаточна фіксація введених даних елементом HTML")
        main_layout.addWidget(label_final_fix)

        # === Елемент HTML + Текст ===
        html_text_layout = QHBoxLayout()

        # Левая часть (Елемент HTML)
        html_layout = QVBoxLayout()
        label_html = QLabel("Елемент HTML")
        self.html_input = QLineEdit()
        html_layout.addWidget(label_html)
        html_layout.addWidget(self.html_input)

        # Правая часть (Текст)
        text_layout = QVBoxLayout()
        label_text = QLabel("Текст елемента")
        self.text_input = QLineEdit()
        text_layout.addWidget(label_text)
        text_layout.addWidget(self.text_input)

        html_text_layout.addLayout(html_layout)
        html_text_layout.addLayout(text_layout)
        main_layout.addLayout(html_text_layout)

        # === Кнопки OK и Скасувати ===
        btn_layout = QHBoxLayout()
        self.btnOK = QPushButton("OK")

        # Устанавливаем кнопку по умолчанию
        self.btnOK.setDefault(True)
        self.btnOK.setAutoDefault(True)
        self.btnCnl = QPushButton("Скасувати")
        btn_layout.addWidget(self.btnOK)
        btn_layout.addWidget(self.btnCnl)
        main_layout.addLayout(btn_layout)

        self.spin.valueChanged.connect(self.update_entries)
        self.btnOK.clicked.connect(self.on_ok_clicked)
        self.btnCnl.clicked.connect(self.reject)

        # self.update_entries()

    def on_ok_clicked(self):
        # """Обработчик нажатия кнопки OK"""
        self.config_data = []
        if hasattr(self, 'current_widgets'):
            for title_edit, name_edit, checkbox in self.current_widgets:
                self.config_data.append({
                    "title": title_edit.text(),
                    "name": name_edit.text(),
                    "required": checkbox.isChecked()
                })

        print(f"Собрано данных: {len(self.config_data)}")
        self.accept()

    def update_entries(self):
        # print("=== UPDATE_ENTRIES ВЫЗВАН ===")
        #
        # # Показываем КОРОТКИЙ стек вызовов
        # import traceback
        # stack = traceback.extract_stack()
        # # Берем только последние 3 вызова (самые важные)
        # for frame in stack[-4:-1]:
        #     print(f"  {frame.name}():{frame.lineno} - {frame.line}")
        #
        # print("=== КОНЕЦ ===")
        if self.spin.value() == self.txt_spin_previous:
            return
        # очистка старых виджетов
        for i in reversed(range(self.entries_layout.count())):
            widget = self.entries_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Создаем новый список для виджетов текущей сессии
        self.current_widgets = []

        for i in range(self.spin.value() + 1):
            container = QWidget()
            h_layout = QHBoxLayout(container)

            if i == 0:
                h_layout.addWidget(QLabel('Title:'))
                title_edit = QLineEdit("URL of page")
            else:
                h_layout.addWidget(QLabel(f'Title {i}:'))
                title_edit = QLineEdit(f"Поле {i}")
            h_layout.addWidget(title_edit)

            if i == 0:
                h_layout.addWidget(QLabel("Name:"))
                name_edit = QLineEdit("url_of_page")
            else:
                h_layout.addWidget(QLabel(f"Name {i}:"))
                name_edit = QLineEdit(f"textbox{i}")
            h_layout.addWidget(name_edit)

            required_chk = QCheckBox("Обов'язкове")
            if i == 0:
                required_chk.setChecked(True)
            h_layout.addWidget(required_chk)

            self.entries_layout.addWidget(container)
            self.current_widgets.append((title_edit, name_edit, required_chk))
            self.txt_spin_previous = self.spin.value()

    def get_config(self):
        """Возвращает сохраненную конфигурацию"""
        return self.config_data

##################################################################################################################
