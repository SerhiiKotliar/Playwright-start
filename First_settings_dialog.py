from PySide6.QtWidgets import (
    QApplication, QDialog, QSpinBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QWidget, QFileDialog,
    QCheckBox, QMessageBox, QRadioButton, QButtonGroup
)
import json
import sys
import os
# ---- Форма ввода конфигурации ----
class SettingInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.current_widgets = None
        self.setWindowTitle("Первинне налаштування конфігурації")
        self.resize(400, 200)

        self.txt_spin_previous = 0
        self.first_config = {}
        self.config_data = []
        self.current_widgets = []
        self.start = True
        self.file_config = None

        main_layout = QVBoxLayout(self)

        # === Головна сторінка ===
        label_attr = QLabel("Назва фалу налаштувань конфігурації для серії тестів")
        main_layout.addWidget(label_attr)

        # === Поле назви файлу ===
        self.name_file_input = QLineEdit()
        # self.name_file_input.setText('http://127.0.0.1:5000/')
        self.name_file_input.setPlaceholderText('наприклад: Example_reestr_login_logout')
        main_layout.addWidget(self.name_file_input)


        # === Головна сторінка ===
        label_attr = QLabel("URL цільової (головної) сторінки")
        main_layout.addWidget(label_attr)

        # === Поле вводу URL для головної сторінки ===
        self.url_page_input = QLineEdit()
        self.url_page_input.setText('http://127.0.0.1:5000/')
        main_layout.addWidget(self.url_page_input)

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
        self.btnOK = QPushButton("Створити файл")

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
        # self.config_data = []
        # if hasattr(self, 'current_widgets'):
        #     for title_edit, name_edit, checkbox in self.current_widgets:
        #         self.config_data.append({
        #             "title": title_edit.text(),
        #             "name": name_edit.text(),
        #             "required": checkbox.isChecked()
        #         })
        self.first_config['file_name'] = self.name_file_input.text()
        self.first_config['home_page'] = self.url_page_input.text()
        self.first_config['count_fields'] = self.spin.value()
        titles = []
        names = []
        requireds = []
        for title_edit, name_edit, checkbox in self.current_widgets:
            titles.append(title_edit.text())
            names.append(name_edit.text())
            requireds.append(checkbox.isChecked())
        self.first_config['titles'] = titles
        self.first_config['names'] = names
        self.first_config['required'] = requireds
        self.first_config['fix_button'] = self.radio_button.isChecked()
        self.first_config['fix_event'] = self.radio_event.isChecked()
        self.first_config['fix_enter'] = self.radio_enter.isChecked()
        self.first_config['HTML_element'] = self.html_input.text()
        self.first_config['HTML_text'] = self.text_input.text()
        self.first_config['attribut_error'] = self.attr_input.text()
        self.save_dict_to_file()

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
        if self.spin.value() == self.txt_spin_previous and self.start == False:
            self.start = False
            return
        # очистка старых виджетов
        for i in reversed(range(self.entries_layout.count())):
            widget = self.entries_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Создаем новый список для виджетов текущей сессии
        self.current_widgets = []

        for i in range(self.spin.value()):
            container = QWidget()
            h_layout = QHBoxLayout(container)

            h_layout.addWidget(QLabel(f'Title {i+1}:'))
            title_edit = QLineEdit(f"Поле {i+1}")
            h_layout.addWidget(title_edit)

            h_layout.addWidget(QLabel(f"Name {i+1}:"))
            name_edit = QLineEdit(f"textbox{i+1}")
            h_layout.addWidget(name_edit)

            required_chk = QCheckBox("Обов'язкове")
            h_layout.addWidget(required_chk)

            self.entries_layout.addWidget(container)
            self.current_widgets.append((title_edit, name_edit, required_chk))
            self.txt_spin_previous = self.spin.value()

    def get_config(self):
        """Возвращает сохраненную конфигурацию"""
        return self.config_data

    def save_dict_to_file(self):
        # Получаем текущую директорию
        current_dir = os.getcwd()

        # Имя файла по умолчанию
        default_path = os.path.join(current_dir, self.name_file_input.text())

        # Диалог сохранения файла
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Зберегти конфігурацію",
            default_path,
            "JSON files (*.json);;All files (*)"
        )
        if not file_name:
            return  # пользователь нажал "Отмена"

        try:
            # Сохраняем словарь в JSON-файл
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(self.first_config, f, ensure_ascii=False, indent=4)
            self.file_config = file_name
            QMessageBox.information(self, "Успіх", f"Дані конфігурації збережено у {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти файл:\n{e}")


##################################################################################################################
if __name__ == "__main__":
    # app = QApplication(sys.argv)
    app = QApplication.instance()
    created_app = False
    if app is None:
        app = QApplication(sys.argv)
        created_app = True
    dlg_config = SettingInputDialog()
    dlg_config.show()
    if created_app:
        app.quit()
    sys.exit(app.exec())