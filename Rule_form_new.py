from PySide6.QtCore import QLocale, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QDialog, QSpinBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QWidget, QGroupBox,
    QComboBox, QCheckBox, QMessageBox
)
import re
from pyside_dialog import MyDialog
from functools import partial

rule_invalid = {}
login_invalid = []
login_l_invalid = []
url_invalid = []
email_invalid = []
password_invalid = []
upregcyr = "А-Я"
lowregcyr = "а-я"
upreglat = "A-Z"
lowreglat = "a-z"
# ---- Форма ввода конфигурации ----
class ConfigInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Конфігурація полів")
        self.resize(400, 200)

        main_layout = QVBoxLayout(self)

        # количество групп
        cnt_layout = QHBoxLayout()
        cnt_layout.addWidget(QLabel("Кількість полів:"))
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

    # def update_entries(self):
    #     for i in reversed(range(self.entries_layout.count())):
    #         widget = self.entries_layout.itemAt(i).widget()
    #         if widget:
    #             widget.deleteLater()
    #
    #     self.line_edits = []
    #     for i in range(self.spin.value()):
    #         container = QWidget()
    #         h_layout = QHBoxLayout(container)
    #         h_layout.addWidget(QLabel(f'Поле {i + 1}        Title:'))
    #         title_edit = QLineEdit(f"Поле {i+1}")
    #         h_layout.addWidget(title_edit)
    #
    #         h_layout.addWidget(QLabel("Name:"))
    #         name_edit = QLineEdit(f"textbox{i+1}")
    #         h_layout.addWidget(name_edit)
    #
    #         self.entries_layout.addWidget(container)
    #         self.line_edits.append((title_edit, name_edit))
    #
    # def get_config(self):
    #     return [{"title": t.text(), "name": n.text()} for t, n in self.line_edits]
    def update_entries(self):
        # очистка старых виджетов
        for i in reversed(range(self.entries_layout.count())):
            widget = self.entries_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.line_edits = []
        for i in range(self.spin.value()):
            container = QWidget()
            h_layout = QHBoxLayout(container)

            h_layout.addWidget(QLabel(f'Поле {i + 1}  Title:'))
            title_edit = QLineEdit(f"Поле {i + 1}")
            h_layout.addWidget(title_edit)

            h_layout.addWidget(QLabel("Name:"))
            name_edit = QLineEdit(f"textbox{i + 1}")
            h_layout.addWidget(name_edit)

            # чекбокс "Обов'язкове"
            required_chk = QCheckBox("Обов'язкове")
            h_layout.addWidget(required_chk)

            self.entries_layout.addWidget(container)
            self.line_edits.append((title_edit, name_edit, required_chk))

    def get_config(self):
        return [
            {
                "title": t.text(),
                "name": n.text(),
                "required": c.isChecked()
            }
            for t, n, c in self.line_edits
        ]
##################################################################################################################

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
###############################################################################################################
def entries_rules(fame, **kwargs):
    global pattern, chars, len_min, len_max, latin, Cyrillic, spec_escaped, is_probel, email, url, both_reg, both_reg_log_l, patternlog, patternlog_l, patternpas, lenminpas, lenmaxpas, lenminlog, lenmaxlog, lenminlog_l, lenmaxlog_l, spec, digits_str, digits_str_log_l, patterne, patternu,\
    email_url, email_p, email_login, email_login_l, url_login, url_e, url_p, url_login_l, both_reg_log, both_reg_log_l, both_reg_p, digits_str_p, digits_str_log, digits_str_log_l, spec_escaped_log, spec_escaped_p, spec_escaped_log_l, local, local_p, local_log, local_log_l, no_absent

    entries = kwargs["entries"]
    # инициализация переменных
    local = ""
    latin = "A-Za-z"
    Cyrillic = "А-Яа-я"
    both_reg = False
    digits_str = ""
    spec_escaped = ""
    is_probel = False
    len_min = 0
    len_max = 0
    email = False
    url = False

    for key, value in entries.items():
        if key == 'register':
            if value == 'великий':
                latin = upreglat
                Cyrillic = upregcyr
            elif value == "малий":
                latin = lowreglat
                Cyrillic = lowregcyr
            elif value == "обидва":
                both_reg = True
        elif key == 'localiz':
            if value == 'латиниця':
                local = latin
            elif value == 'кирилиця':
                local = Cyrillic
        elif key == "cyfry" and value:
            digits_str = "0-9"
        elif key == "spec" and value:
            if isinstance(value, str):
                spec_escaped = "".join(re.escape(ch) for ch in value)
            else:
                spec = "!@#$%^&*()_=+[]{};:,.<>/?\\|-"
                spec_escaped = "".join(re.escape(ch) for ch in spec)
        elif key == "probel":
            is_probel = value
        elif key == "len_min":
            len_min = value
        elif key == "len_max":
            len_max = value
        elif key == "email_in":
            # email = r"(A-Za-z0-9@._-)"
            email = value
        elif key == "url_in":
            # url = r"(http?://[^\s/$.?#].[^\s])"
            url = value
        elif key == "no_absent":
            no_absent = value

    if email:
        chars = "a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-."
    elif url:
        chars = "http?://[^\s/$.?#].[^\s"
    elif no_absent:
        chars = "."
    else:
        # собираем разрешённые символы
        parts = []
        if local:
            parts.append(local)
        if digits_str:
            parts.append(digits_str)
        if not is_probel:
            parts.append('\s')
            # chars = "^["+f"{chars}"+"]+$*"
        if spec_escaped:
            parts.append(spec_escaped)
        chars = "".join(parts) or "." # если ничего не выбрано — разрешаем всё
    pattern = "^["+f"{chars}"+"]+$"
    if fame == "login":
        lenminlog = len_min
        lenmaxlog = len_max
        patternlog = pattern
        both_reg_log = both_reg
        digits_str_log = digits_str
        spec_escaped_log = spec_escaped
        email_login = email
        url_login = url
        local_log = local
    if fame == "login_l":
        lenminlog_l = len_min
        lenmaxlog_l = len_max
        patternlog_l = pattern
        both_reg_log_l = both_reg
        digits_str_log_l = digits_str
        spec_escaped_log_l = spec_escaped
        email_login_l = email
        url_login_l = url
        local_log_l = local
    if fame == "password":
        lenminpas = len_min
        lenmaxpas = len_max
        patternpas = pattern
        both_reg_p = both_reg
        digits_str_p = digits_str
        spec_escaped_p = spec_escaped
        email_p = email
        url_p = url
        local_p = local
    if fame == "email":
        patterne = pattern
        url_e = url
    if fame == "url":
        # patternu = f"{chars}"+"]+$"
        email_url = email
        patternu = pattern
    # messagebox.showerror("Шаблон", pattern, parent=_root)
    return pattern


def make_input_data(file_name):
    # Словарь для хранения данных
    data = {
        "url": [],
        "login": [],
        "login_l": [],
        "password": [],
        "email": []
    }

    current_section = None

    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()  # Убираем пробелы и переносы строк
            if not line:  # Пропускаем пустые строки
                continue
            if line.startswith("[") and line.endswith("]"):
                # Определяем текущую секцию
                section = line[1:-1].lower()
                if section in data:
                    current_section = section
                else:
                    current_section = None
            elif current_section:
                # Добавляем строки в соответствующий список
                data[current_section].append(line)
    return data

# файл у якому перелічені вхідні дані
input_data = make_input_data("file_input_data.txt")

def diff_char(bigger: str, smaller: str) -> str:
    # ищем первую позицию, где строки расходятся
    for i, (c1, c2) in enumerate(zip(bigger, smaller)):
        if c1 != c2:
            return c1  # символ из "большей" строки

    # если отличий не нашли, то "лишний" символ — в конце
    return bigger[len(smaller)]

# --- проверки при вводе ---
def allow_login_value(new_value: str) -> bool:
    global chars, patternlog
    if not new_value:
        return True
    # если chars == ".", разрешаем всё
    if chars == ".":
        return True
    if email_login:
        patternlog = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$"
    return bool(re.fullmatch(patternlog, new_value))

def allow_login_l_value(new_value: str) -> bool:
    global chars, patternlog_l
    if not new_value:
        return True
    # если chars == ".", разрешаем всё
    if chars == ".":
        return True
    return bool(re.fullmatch(patternlog_l, new_value))


def allow_password_value(new_value: str) -> bool:
    global chars, patternpas
    if not new_value:
        return True
    # если chars == ".", разрешаем всё
    if chars == ".":
        return True
    return bool(re.fullmatch(patternpas, new_value))


def allow_url_value(new_value: str) -> bool:
    global patternu
    if not new_value:
        return True
    if chars == ".":
        return True
    return bool(re.fullmatch(patternu, new_value))
# --- проверки Email при вводе ---
def allow_email_value(new_value: str) -> bool:
    global patterne
    if not new_value:
        return True
    if chars == ".":
        return True
    return bool(re.fullmatch(patterne, new_value))

FIELDS_CONFIG = [
        {"name": "url", "default": "", "allow_func": allow_url_value},
        {"name": "login", "default": "", "allow_func": allow_login_value},
        {"name": "login_l", "default": "", "allow_func": allow_login_l_value},
        {"name": "password", "default": "", "allow_func": allow_password_value},
        {"name": "email", "default": "", "allow_func": allow_email_value},
    ]

for el in FIELDS_CONFIG:
    if el["name"] == "url":
        url_inv = []
    elif el["name"] == "login":
        login_inv = []
    elif el["name"] == "login_l":
        login_l_inv = []
    elif el["name"] == "password":
        pw_inv = []
    elif el["name"] == "email":
        email_inv = []



# ---- Динамическая форма ----
class DynamicDialog(QDialog):
    def __init__(self, config, parent=None, input_url=None, input_login=None, input_login_l=None, input_password=None, input_email=None, name_of_test=""):
        super().__init__(parent)
        self.setWindowTitle("Введення даних у тест    "+name_of_test)
        self.resize(640, 140)

        main_layout = QVBoxLayout(self)

        # ---- Layout для GroupBox ----
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        main_layout.addWidget(self.scroll_content)  # напрямую, без QScrollArea

        # создаём GroupBox
        self.gb = {}
        for cfg in config:
            title = cfg.get("title", "")
            name = cfg.get("name", "")
            required = cfg.get("required")

            # gb_widget = QGroupBox(title, scroll_content)
            gb_widget = QGroupBox(title)
            gb_widget.setObjectName(name)
            gb_widget.setStyleSheet("background-color: rgb(85, 255, 127);")
            gb_widget.setLocale(QLocale(QLocale.Ukrainian, QLocale.Ukraine))
            gb_widget.setMinimumHeight(60)

            # элементы
            cmb = QComboBox(gb_widget)
            cmb.setEditable(False)
            chkb = QCheckBox("Обов'язкове", gb_widget)
            if name == 'url':
                cmb.addItems(input_url)
                cmb.setCurrentText(input_url[0])
            if name == 'login':
                cmb.addItems(input_login)
                cmb.setCurrentText(input_login[0])
            if name == 'login_l':
                cmb.addItems(input_login_l)
                cmb.setCurrentText(input_login_l[0])
            if name == 'password':
                cmb.addItems(input_password)
                cmb.setCurrentText(input_password[0])
            if name == 'email':
                cmb.addItems(input_email)
                cmb.setCurrentText(input_email[0])
            if required:
                chkb.setChecked(True)
            cmb.setStyleSheet("background-color: rgb(255, 255, 255);")

            btn = QPushButton("Правила", gb_widget)

            # стандартная геометрия
            cmb.setGeometry(10, 20, 400, 25)
            chkb.setGeometry(420, 20, 100, 25)
            btn.setGeometry(530, 15, 60, 30)
            gb_widget.setFixedHeight(60)
            self.scroll_layout.addWidget(gb_widget)
            self.gb[name] = GroupBoxWrapper(gb_widget, cmb, chkb, btn)
            # подключаем событие изменения чекбокса (с правильным захватом имени)
            chkb.toggled.connect(partial(self.on_required_toggled, name))
            # подключаем сигнал с передачей combo и имени
            btn.clicked.connect(lambda _, c=cmb, n=name: self.on_rules_clicked(c, n))
            # запоминаем старое значение
            self.previous_text = cmb.currentText()
            # событие изменения текста
            cmb.editTextChanged.connect(self.on_text_changed)

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

        # события кнопок
        self.btnOK.clicked.connect(self.on_ok_clicked)
        self.btnCnl.clicked.connect(self.reject)

        # ---- обработчики ----

    def on_text_changed(self, text: str) -> bool:
        combo = self.sender()  # тот QComboBox, который вызвал сигнал
        global chars, pattern
        if not text:
            return True
        # если chars == ".", разрешаем всё
        if chars == ".":
            return True
        # if email_login:
        #     patternlog = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$"
        if not bool(re.fullmatch(pattern, text)):
            diff_simv = diff_char(text, self.previous_text)
            QMessageBox.warning(self, "Помилка вводу", f"Неприпустимий символ: '{diff_simv}'")
            # откатываем на предыдущее значение
            combo.blockSignals(True)  # блокируем сигналы, чтобы не зациклиться
            combo.setCurrentText(self.previous_text)
            combo.blockSignals(False)  # разблокируем сигналы
            return False
        else:
            # сохраняем новое значение как предыдущее
            self.previous_text = text
            return  True
        # return bool(re.fullmatch(patternlog, new_value))




    def on_required_toggled(self, name, state):
        """Срабатывает при изменении чекбокса."""
        # пример: можно отключать ComboBox, если поле не обязательное
        # wrapper = self.gb.get(name)
        # if wrapper:
        #     wrapper.cmb.setEnabled(state)

    # def on_rules_clicked(self, field_name):
    def on_rules_clicked(self, combo, field_name):
        # combo.setEditable(True)
        for name, wrapper in self.gb.items():
            if wrapper.cmb is combo:
                wrapper.cmb.setEditable(True)  # текущий делаем редактируемым
                wrapper.gb.setStyleSheet("background-color: rgb(255, 255, 200);")  # подсветка
                # print(f"ComboBox в {field_name} теперь редактируемый")
            else:
                if wrapper.cmb.isEditable():
                    # сохранить введённый текст
                    current_text = wrapper.cmb.currentText().strip()
                    if current_text:
                        items = [wrapper.cmb.itemText(i) for i in range(wrapper.cmb.count())]
                        if current_text not in items:
                            wrapper.cmb.addItem(current_text)  # добавляем в список
                        # получаем индекс добавленного или существующего значения
                        idx = wrapper.cmb.findText(current_text)
                        if idx >= 0:
                            wrapper.cmb.setCurrentIndex(idx)
                    # теперь можно выключить редактирование
                wrapper.cmb.setEditable(False)
                wrapper.gb.setStyleSheet("background-color: rgb(85, 255, 127);")
        #########################################################################################################
        global check_login, check_login_l, check_p, check_url, check_email, condition_login, condition_login_l, condition_p, condition_url, condition_email
        if field_name == "login":
            condition_login = False
        if field_name == "login_l":
            condition_login = False
        if field_name == "password":
            condition_p = False
        if field_name == "url":
            condition_url = False
        if field_name == "email":
            condition_email = False
        if field_name == "login":
            check_login = False
            rule_invalid['login'] = []
            login_inv.clear()
            condition_login = True
        if field_name == "login_l":
            check_login_l = False
            rule_invalid['login_l'] = []
            login_l_inv.clear()
            condition_login = True
        if field_name == "password":
            check_p = False
            rule_invalid['password'] = []
            pw_inv.clear()
            condition_p = True
        if field_name == "url":
            check_url = False
            rule_invalid['url'] = []
            url_inv.clear()
            condition_url = True
        if field_name == "email":
            check_email = False
            rule_invalid['email'] = []
            email_inv.clear()
            condition_email = True

        app = QApplication.instance()
        if not app:
            app = QApplication([])
        dlg = MyDialog()

        dlg.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        dlg.setModal(True)
        if dlg.exec() == QDialog.Accepted:  # ← проверка, нажата ли OK
            cur_rules = dlg.result  # ← берём результат после закрытия
            entries_rules(field_name, entries=cur_rules)

    def on_ok_clicked(self):
        """Срабатывает при нажатии кнопки 'Введення' — собирает данные и закрывает диалог."""
        data = {}
        # for name, wrapper in self.gb.items():
        #     data[name] = {
        #         "value": wrapper.cmb.currentText(),
        #         "required": wrapper.chkb.isChecked(),
        #         "rules": self.rules.get(name, "")
        #     }
        # print("Введённые данные:", data)
        # # если нужно вернуть данные наружу, можно сохранить в self.result_data
        self.result_data = data
        self.accept()


# ---- Основной запуск ----
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    input_dlg = ConfigInputDialog()
    if input_dlg.exec() == QDialog.Accepted:
        config = input_dlg.get_config()
        dlg = DynamicDialog(config, input_url=input_data['url'], input_login=input_data['login'],
                          input_login_l=input_data['login_l'], input_password=input_data['password'],
                          input_email=input_data['email'], name_of_test="test_first_name_field_visible")
        dlg.show()

        # пример изменения размеров элементов
        # dlg.gb["group1"].set_geometry(cmb_geom=(10, 10, 250, 30),
        #                               chkb_geom=(270, 10, 150, 30),
        #                               btn_geom=(430, 10, 120, 30))

    sys.exit(app.exec())
