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
# from PyQt6.QtCore import pyqtSignal
from mycombo import QComboBox, WhichBinding
from mygroupbox_dynamic import MyGroupBox
import sys

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
chars: str = "."
pattern = "^["+f"{chars}"+"]+$"
len_min = 0
len_max = 0
spec_escaped = ""
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

def detect_script(text: str) -> str:
    if re.search(r"[А-Яа-яЁёЇїІіЄєҐґ]", text):
        return "Cyrillic"
    elif re.search(r"[A-Za-z]", text):
        return "Latin"
    elif re.search(r"[a-z]", text):
        return "lowreglat"
    elif re.search(r"[A-Z]", text):
        return "upreglat"
    elif re.search(r"[а-яїієёґ]", text):
        return "lowregcyr"
    elif re.search(r"[А-ЯЁЇІЄҐ]", text):
        return "upregcyr"
    return "Unknown"

def entries_rules(log, required, fame, **kwargs):
    global pattern, chars, len_min, len_max, latin, Cyrillic, spec_escaped, is_probel, email, url, both_reg, both_reg_log_l, patternlog, patternlog_l, patternpas, lenminpas, lenmaxpas, lenminlog, lenmaxlog, lenminlog_l, lenmaxlog_l, spec, digits_str, digits_str_log_l, patterne, patternu,\
    email_url, email_p, email_login, email_login_l, url_login, url_e, url_p, url_login_l, both_reg_log, both_reg_log_l, both_reg_p, digits_str_p, digits_str_log, digits_str_log_l, spec_escaped_log, spec_escaped_p, spec_escaped_log_l, local, local_p, local_log, local_log_l, no_absent

    entries = kwargs["entries"]
    # инициализация переменных
    local = ""
    latin = "A-Za-z"
    Cyrillic = "А-Яа-я"
    upregcyr = "А-Я"
    lowregcyr = "а-я"
    upreglat = "A-Z"
    lowreglat = "a-z"
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
            email = value
        elif key == "url_in":
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
            parts.append(' ')
        if spec_escaped:
            parts.append(spec_escaped)
        chars = "".join(parts) or "." # если ничего не выбрано — разрешаем всё
    if not is_probel:
        # pattern = "^(?=.*\s)["+f"{chars}"+"]+$"
        # pattern = "^(?=.*\s)["+f"{chars}]\{{len_min, len_max}\}$"
        pattern = rf"^(?=.*\s)[{chars}]{{{len_min},{len_max}}}$"
    else:
        # pattern = "^["+f"{chars}"+"]+$"
        # pattern = "^["+f"{chars}]\{{len_min}, {len_max}\}$"
        pattern = rf"^[{chars}]{{{len_min},{len_max}}}$"
    # QMessageBox.information(None, "Символи", chars)
    # QMessageBox.information(None, "Шаблон", pattern)
    rule_invalid[fame] = []
    if not log and required:
        rule_invalid[fame].append("absent")
        # return f"Помилка, Поле {fame} не може бути пустим."
    if url:
        rule_invalid[fame].append("no_url")
        # return "Помилка, Логін не може форматуватись як URL адреса."
    if len(log) < len_min or len(log) > len_max:
        rule_invalid[fame].append(f"len {len_min} {len_max}")
        # return f"Логін має бути від {lenminlog} до {lenmaxlog} символів включно"
    if email:
        rule_invalid[fame].append("no_email")
        # return None
    if both_reg:
        rule_invalid[fame].append("no_lower")
        rule_invalid[fame].append("no_upper")
        # if not any(c.islower() for c in log):
        #     # return "Логін має містити принаймні одну маленьку літеру."
        # if not any(c.isupper() for c in log):
            # return "Логін має містити принаймні одну велику літеру."
    if digits_str:
        rule_invalid[fame].append("no_digit")
        # if not any(c.isdigit() for c in log):
            # return "Логін має містити принаймні одну цифру."
    if spec_escaped:
        rule_invalid[fame].append("no_spec")
        # if not any(c in spec_escaped_log for c in log):
            # return "Логін має містити принаймні один спеціальний символ."
    # немає пробілів
    if is_probel:
        rule_invalid[fame].append("probel")
    # є пробіли
    else:
        rule_invalid[fame].append("no_probel")
    if local == latin:
        rule_invalid[fame].append("Cyrillic")
    elif local == upreglat:
        rule_invalid[fame].append("lowreglat")
    elif local == lowreglat:
        rule_invalid[fame].append("upreglat")
    elif local == Cyrillic:
        rule_invalid[fame].append("latin")
    elif local == upregcyr:
        rule_invalid[fame].append("lowregcyr")
    elif local == lowregcyr:
        rule_invalid[fame].append("upregcyr")
    if both_reg:
        rule_invalid[fame].append("one_reg_log")
    if no_absent:
        rule_invalid[fame].append("absent")
    # rule_invalid['login'] = login_invalid

    return pattern

from typing import Tuple, Set, Optional

def _parse_allowed_string(allowed: str) -> Tuple[str, Set[str]]:
    """
    Разбирает строку allowed, извлекая диапазоны вида a-z и одиночные символы.
    Возвращает (charclass_string_for_regex, set_of_allowed_chars).
    Пример allowed: "a-zA-Z0-9_.@+-"
    """
    ranges = []
    singles = []
    s = allowed
    i = 0
    while i < len(s):
        # детектим простой диапазон вида X-Y где X и Y — цифра/буква
        if i + 2 < len(s) and s[i+1] == '-' and re.match(r'[A-Za-z0-9]', s[i]) and re.match(r'[A-Za-z0-9]', s[i+2]):
            ranges.append((s[i], s[i+2]))
            i += 3
        else:
            # одиночный символ (может быть спецсимвол)
            singles.append(s[i])
            i += 1

    # Собираем класс символов и множество разрешённых символов
    parts = []
    allowed_set = set()

    for a, b in ranges:
        # диапазон в виде a-b оставляем как есть в классе
        parts.append(f"{a}-{b}")
        for code in range(ord(a), ord(b) + 1):
            allowed_set.add(chr(code))

    for ch in singles:
        parts.append(re.escape(ch))
        allowed_set.add(ch)

    charclass = "".join(parts)
    return charclass, allowed_set


def validate_chars_mode(text: str, allowed: str) -> Tuple[bool, Optional[str]]:
    """
    Проверка текста в режиме 'chars'.
    :param text: входная строка
    :param allowed: строка описания допустимых символов, например "a-zA-Z0-9_.@+-"
    :return: (True, None) если OK, иначе (False, first_invalid_char)
    """
    if text == "":
        return True, None

    charclass, allowed_set = _parse_allowed_string(allowed)
    regex = fr'^[{charclass}]*$'   # разрешаем пустую строку; можно заменить * на + если нельзя пустую
    if re.fullmatch(regex, text):
        return True, None

    # обнаружим первый недопустимый символ (быстро через множество)
    for ch in text:
        if ch not in allowed_set:
            return False, ch

    # запасной вариант (маловероятно)
    return False, text[0]


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

FIELDS_CONFIG = [
        {"name": "url", "default": "", "allow_func": None},
        {"name": "login", "default": "", "allow_func": None},
        {"name": "login_l", "default": "", "allow_func": None},
        {"name": "password", "default": "", "allow_func": None},
        {"name": "email", "default": "", "allow_func": None},
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
        self.result = {}
        self.result_invalid = {}
        main_layout = QVBoxLayout(self)
        # ---- предупреждающий текст ----
        self.warning_label = QLabel("⚠ По замовчуванню для кожного поля тільки одне правило: БУТИ НЕ ПУСТИМ!")
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        self.warning_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.warning_label)
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

            gb_widget = MyGroupBox(title)
            # gb_widget = QGroupBox(title)
            gb_widget.setObjectName(name)
            gb_widget.setStyleSheet("background-color: rgb(85, 255, 127);")
            gb_widget.setLocale(QLocale(QLocale.Ukrainian, QLocale.Ukraine))
            gb_widget.setMinimumHeight(60)

            # элементы
            cmb = QComboBox(gb_widget)
            cmb.setEditable(False)
            chkb = QCheckBox("Обов'язкове", gb_widget)
            # привязываем чекбокс к комбобоксу
            # cmb.checkbox = chkb
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

            # прикрепляем ссылки внутрь gb_widget
            gb_widget.cmb = cmb
            gb_widget.chkb = chkb
            gb_widget.btn = btn
            # Обязательно зарегистрировать виджеты в MyGroupBox,
            # чтобы он отслеживал их FocusOut:
            gb_widget.watch_widget(cmb)
            gb_widget.watch_widget(chkb)
            gb_widget.watch_widget(btn)

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
            # событие потери фокуса комбобоксом
            # cmb.focusOut.connect(self.on_focusOut)
            # событие потери фокуса групбоксом
            gb_widget.focusLeft.connect(self.on_gb_focus_left)

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
        ok, bad = validate_chars_mode(text, chars)
        if not ok:
            QMessageBox.warning(self, "Помилка вводу", f"Недопустимий символ: '{bad}'")
            combo.blockSignals(True)
            combo.setCurrentText(self.previous_text)
            combo.blockSignals(False)
            return False
        else:
            # всё ок — обновляем previous_text
            self.previous_text = text
            return True

    def on_gb_focus_left(self):
        gb = self.sender()
        global chars, pattern, len_min, len_max
        gr_t_title = gb.title()
        # QMessageBox.warning(self, f"Поле {gr_t_title}", f"MIN {len_min} MAX {len_max} LEN TXT {len(gb.cmb.currentText())}")
        gr_t = gb.objectName()
        if gb.chkb.isChecked() and gb.cmb.currentText() == "":
            QMessageBox.warning(self, "Обов'язкове поле", f"Введіть дані у обов'язкове поле: '{gr_t}'")
            gb.cmb.setFocus(True)
            return False
        # Якщо chars == ".", дозволяємо все
        if chars == ".":
            self.previous_text = gb.cmb.currentText()
            return True
        # Перевірка на відповідність pattern
        if not bool(re.fullmatch(pattern, gb.cmb.currentText())) and gb.cmb.currentText() != "":
            QMessageBox.warning(self, f"Поле {gr_t_title}", "Видаліть неприпустимі символи або додайте необхідні")
            # return False
        ###############################################################
            if "no_lower" in rule_invalid[gr_t] and not any(c.islower() for c in gb.cmb.currentText()):
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має містити принаймні одну маленьку літеру.")
            if "no_upper" in rule_invalid[gr_t] and not any(c.isupper() for c in gb.cmb.currentText()):
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має містити принаймні одну велику літеру.")
            if "no_digit" in rule_invalid[gr_t] and not any(c.isdigit() for c in gb.cmb.currentText()):
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має містити принаймні одну цифру.")
            if "no_spec" in rule_invalid[gr_t] and not any(c in spec_escaped for c in gb.cmb.currentText()):
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має містити принаймні один спеціальний символ.")
            if "no_email" in rule_invalid[gr_t]:
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має бути формату email.")
            if "no_url" in rule_invalid[gr_t]:
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має бути формату URL.")
            if f"len {len_min} {len_max}" in rule_invalid[gr_t] and (len_max < len(gb.cmb.currentText()) or len(gb.cmb.currentText()) < len_min):
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має мати від {len_min} до {len_max} символів включно.")
            if "probel" in rule_invalid[gr_t] and gb.cmb.currentText().find(' ') > -1:
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} не має бути пробілів.")
            if "no_probel" in rule_invalid[gr_t] and gb.cmb.currentText().find(' ') == -1:
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має бути з пробілами.")
            if "one_reg_log" in rule_invalid[gr_t]:
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має бути з текстом у двох регістрах.")
            loc_text = detect_script(gb.cmb.currentText())
            if "Latin" in rule_invalid[gr_t] and loc_text == "Latin":
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має бути з кирилицею.")
            if "Cyrillic" in rule_invalid[gr_t] and loc_text == "Cyrillic":
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має бути з латиницею.")
            if "upreglat" in rule_invalid[gr_t] and loc_text != "loureglat":
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має бути з малими латинськими літерами.")
            if "lowreglat" in rule_invalid[gr_t] and loc_text != "upreglat":
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має бути з великими латинськими літерами.")
            if "upregcyr" in rule_invalid[gr_t] and loc_text != "lowregcyr":
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має бути з малими кириличними літерами.")
            if "lowregcyr" in rule_invalid[gr_t] and loc_text != "upregcyr":
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title} має бути з великими кириличними літерами.")
            gb.cmb.setFocus(True)
            return False
        ###############################################################
        # Якщо все добре, зберігаємо нове значення
        self.previous_text = gb.cmb.currentText()
        return True


    def on_required_toggled(self, name, state):
        """Срабатывает при изменении чекбокса."""
        # пример: можно отключать ComboBox, если поле не обязательное
        # wrapper = self.gb.get(name)
        # if wrapper:
        #     wrapper.cmb.setEnabled(state)

    # нажатие на кнопку Правила
    def on_rules_clicked(self, combo, field_name):
        for name, wrapper in self.gb.items():
            chck_stat = wrapper.chkb.isChecked()
            if wrapper.cmb is combo:
                wrapper.cmb.setEditable(True)  # текущий делаем редактируемым
                wrapper.gb.setStyleSheet("background-color: rgb(255, 255, 200);")  # подсветка
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
        rule_invalid[field_name] = []
        #########################################################################################################
        # global check_login, check_login_l, check_p, check_url, check_email, condition_login, condition_login_l, condition_p, condition_url, condition_email
        # if field_name == "login":
        #     condition_login = False
        # if field_name == "login_l":
        #     condition_login = False
        # if field_name == "password":
        #     condition_p = False
        # if field_name == "url":
        #     condition_url = False
        # if field_name == "email":
        #     condition_email = False
        # if field_name == "login":
        #     check_login = False
        #     rule_invalid['login'] = []
        #     login_inv.clear()
        #     condition_login = True
        # if field_name == "login_l":
        #     check_login_l = False
        #     rule_invalid['login_l'] = []
        #     login_l_inv.clear()
        #     condition_login = True
        # if field_name == "password":
        #     check_p = False
        #     rule_invalid['password'] = []
        #     pw_inv.clear()
        #     condition_p = True
        # if field_name == "url":
        #     check_url = False
        #     rule_invalid['url'] = []
        #     url_inv.clear()
        #     condition_url = True
        # if field_name == "email":
        #     check_email = False
        #     rule_invalid['email'] = []
        #     email_inv.clear()
        #     condition_email = True

        # app = QApplication.instance()
        # if not app:
        #     app = QApplication([])
        dlg = MyDialog()

        dlg.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        dlg.setModal(True)
        if dlg.exec() == QDialog.Accepted:  # ← проверка, нажата ли OK
            cur_rules = dlg.result  # ← берём результат после закрытия
            if not entries_rules(wrapper.cmb.currentText(), chck_stat, field_name, entries=cur_rules):
                self.reject()

    def on_ok_clicked(self):
        """Срабатывает при нажатии кнопки 'Введення' — собирает данные и закрывает диалог."""
        txt_data = ""
        for name, wrapper in self.gb.items():
            # if wrapper.cmb is combo:
            if wrapper.chkb.isChecked():
                txt_data += wrapper.cmb.currentText().strip()
                if wrapper.cmb.currentText() != "":
                    self.result[name] = wrapper.cmb.currentText()
        if txt_data == "":
            QMessageBox.warning(self, "Обов'язкові дані", "Обов'язкові дані не введені.")
            self.reject()
        self.result
        self.result_invalid = rule_invalid
        self.accept()

def get_user_input():
    global number_of_test
    app = QApplication(sys.argv)
    input_dlg = ConfigInputDialog()
    if input_dlg.exec() == QDialog.Accepted:
        config = input_dlg.get_config()
        dlg = DynamicDialog(config, input_url=input_data['url'], input_login=input_data['login'],
                          input_login_l=input_data['login_l'], input_password=input_data['password'],
                          input_email=input_data['email'], name_of_test="")
    if dlg.exec() == QDialog.Accepted:
        return dlg.result, dlg.result_invalid
    else:
        return None

# ---- Основной запуск ----
if __name__ == "__main__":
    get1_2 = get_user_input()
    print(str(get1_2[0])+"\n"+str(get1_2[1]))
