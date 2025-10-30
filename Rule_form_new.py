# from PyQt6.sip import wrapper
# from PyQt6.sip import wrapper
from PySide6.QtCore import QLocale, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QDialog, QSpinBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QWidget, QGroupBox,
    QComboBox, QCheckBox, QMessageBox, QRadioButton, QButtonGroup
)
# import re
import allure

# from main_file import both_reg
from pyside_dialog import MyDialog
# from functools import partial
from mycombo import QComboBox, WhichBinding
from mygroupbox_dynamic import MyGroupBox
import sys
import re, unicodedata
from typing import Tuple, Set, Optional
from datetime import datetime
import os
import pytest
from itertools import zip_longest
import sre_parse
# import invalid_datas

rule_invalid = {}
# login_invalid = []
# login_l_invalid = []
# url_invalid = []
# email_invalid = []
# password_invalid = []
Cyrillic = "[А-Яа-яЁёЇїІіЄєҐґ]"
Cyrillic_1 = "(?=.*[А-ЯЁЇІЄҐа-яїієёґ])[А-Яа-яЁёЇїІіЄєҐґ]"
Cyrillic_1_1 = "(?=.*[А-ЯЁЇІЄҐ])(?=.*[а-яїієёґ])[А-Яа-яЁёЇїІіЄєҐґ]"
latin = "[A-Za-z]"
latin_1 = "(?=.*[A-Za-z])[A-Za-z]"
latin_1_1 = "(?=.*[A-Z])(?=.*[a-z])[A-Za-z]"
lat_Cyr = f"[{latin}{Cyrillic}]"
lat_Cyr_1 = "(?=.*[A-ZА-ЯЁЇІЄҐa-zа-яїієёґ])[A-Za-zА-Яа-яЁёЇїІіЄєҐґ]"
lat_Cyr_1_1 = "(?=.*[A-ZА-ЯЁЇІЄҐ])(?=.*[a-zа-яїієёґ])[A-Za-zА-Яа-яЁёЇїІіЄєҐґ]"
upregcyr = "[А-ЯЁЇІЄҐ]"
upregcyr_1 = f"(?=.*{upregcyr})[{upregcyr}]"
lowregcyr = "[а-яїієёґ]"
lowregcyr_1 = f"(?=.*{lowregcyr})[{lowregcyr}]"
upreglat = "[A-Z]"
upreglat_1 = "(?=.*[A-Z])[A-Z]"
lowreglat = "[a-z]"
lowreglat_1 = "(?=.*[a-z])[a-z]"
lat_Cyr_up = f"[{upreglat}{upregcyr}]"
lat_Cyr_up_1 = f"(?=.*[A-ZА-ЯЁЇІЄҐ])[{upreglat}{upregcyr}]"
lat_Cyr_low = f"[{lowreglat}{lowregcyr}]"
lat_Cyr_low_1 = f"(?=.*[a-zа-яёїієґ])[{lowreglat}{lowregcyr}]"
chars: str = "."
pattern = rf"^[{chars}]+$"
len_min = 0
len_max = 0
spec_escaped = ""
spec_escaped_1 = False
no_absent = False
spec = "!@#$%^&*()_=+[]{};:,.<>/?\\|-"
# spec = "@#_=!$%^&§~`№<>;:'\",./?|-"
digits_str = ""
digits_str_1 = False
# check_on = False


# ---- Форма ввода конфигурации ----
class ConfigInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Конфігурація перевірки полів")
        self.resize(400, 200)

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
        self.attr_input.setText('//*[@id="error_1_id_text_string"]')
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
        self.btnCnl = QPushButton("Скасувати")
        btn_layout.addWidget(self.btnOK)
        btn_layout.addWidget(self.btnCnl)
        main_layout.addLayout(btn_layout)

        # кнопки
        # btn_layout = QHBoxLayout()
        # self.btnOK = QPushButton("OK")
        # self.btnCnl = QPushButton("Скасувати")
        # btn_layout.addWidget(self.btnOK)
        # btn_layout.addWidget(self.btnCnl)
        # main_layout.addLayout(btn_layout)

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
        for i in range(self.spin.value()+1):
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

            # чекбокс "Обов'язкове"
            required_chk = QCheckBox("Обов'язкове")
            if i == 0:
                required_chk.setChecked(True)
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


def has_text_special_chars(pattern: str) -> bool:
    """
    Возвращает True, если паттерн разрешает спецсимволы (не буквы и цифры).
    """

    # Сначала проверяем lookahead/lookbehind на наличие \W или специальных символов
    lookahead_matches = re.finditer(r"\(\?[=!<](.*?)\)", pattern)
    for match in lookahead_matches:
        lookahead_content = match.group(1)
        # Проверяем на \W в lookahead
        if "\\W" in lookahead_content:
            return True
        # Проверяем на специальные символы в классах внутри lookahead
        lookahead_class_matches = re.finditer(r"\[(.*?)\]", lookahead_content)
        for class_match in lookahead_class_matches:
            inside = class_match.group(1)
            if contains_special_char_in_class(inside):
                return True

    # Удаляем lookahead/lookbehind утверждения для дальнейшего анализа
    pattern_clean = re.sub(r"\(\?[=!<].*?\)", "", pattern)

    # Проверка на \W или . вне классов
    in_class = False
    escaped = False
    i = 0
    while i < len(pattern_clean):
        ch = pattern_clean[i]

        if not escaped:
            if ch == "\\":
                escaped = True
                # Проверяем \W (но не \w, \d, \s и т.д.)
                if i + 1 < len(pattern_clean) and pattern_clean[i + 1] == "W":
                    return True
            elif ch == "[":
                in_class = True
            elif ch == "]":
                in_class = False
            elif ch == "." and not in_class:
                return True
        else:
            escaped = False

        i += 1

    # Проверка классов символов [ ... ]
    for m in re.finditer(r"\[(.*?)\]", pattern_clean):
        inside = m.group(1)

        # Обрабатываем escape-последовательности внутри класса
        inside_clean = ""
        j = 0
        while j < len(inside):
            c = inside[j]
            if c == "\\":
                if j + 1 < len(inside):
                    next_char = inside[j + 1]
                    # Если это \W - точно разрешает спецсимволы
                    if next_char == "W":
                        return True
                    # Если это \w, \d, \s - пропускаем (это буквы/цифры/пробелы)
                    elif next_char in "wds":
                        inside_clean += next_char
                        j += 1
                    else:
                        # Другие escape-последовательности могут быть спецсимволами
                        return True
                j += 1
            else:
                inside_clean += c
                j += 1

        # отрицательный класс [^...]
        if inside_clean.startswith("^"):
            excluded = inside_clean[1:]
            # Если исключаются ТОЛЬКО буквы и цифры (и возможно диапазоны между ними),
            # то разрешаются спецсимволы
            if all_characters_are_alnum(excluded):
                return True
        # положительный класс [ ... ]
        else:
            # Если есть хотя бы один явный не-буквенно-цифровой символ
            if contains_special_char_in_class(inside_clean):
                return True

    return False


def all_characters_are_alnum(chars: str) -> bool:
    """Проверяет, содержат ли символы только буквы, цифры и их диапазоны."""
    i = 0
    while i < len(chars):
        if chars[i] == '-':
            if i > 0 and i < len(chars) - 1:
                # Проверяем диапазон
                start = chars[i - 1]
                end = chars[i + 1]
                if not (start.isalnum() and end.isalnum() and ord(start) < ord(end)):
                    return False
                i += 2
            else:
                return False
        elif not chars[i].isalnum():
            return False
        else:
            i += 1
    return True


def contains_special_char_in_class(chars: str) -> bool:
    """Проверяет, содержит ли строка специальные символы в классе символов."""
    i = 0
    while i < len(chars):
        if chars[i] == '-':
            if i > 0 and i < len(chars) - 1:
                # Это диапазон, пропускаем
                i += 2
            else:
                # Одиночный '-' - это специальный символ
                return True
        elif not chars[i].isalnum() and chars[i] not in '^':
            # Найден специальный символ (кроме ^ в начале)
            return True
        else:
            i += 1
    return False

def report_bug_and_stop(message: str, page_open=None, name="screenshot_of_skip"):
    # додаємо повідомлення у Allure
    allure.attach(message, name="Причина зупинки", attachment_type=allure.attachment_type.TEXT)
    filename = ""
    # унікальне ім’я файлу
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshots/{name}_{timestamp}.png"
    if page_open:
        try:
            # створюємо папку screenshots (якщо немає)
            os.makedirs("screenshots", exist_ok=True)

            # # унікальне ім’я файлу
            # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # filename = f"screenshots/{name}_{timestamp}.png"

            # робимо скріншот у файл
            page_open.screenshot(path=filename, timeout=40000)

            # прикріплюємо цей файл у Allure
            allure.attach.file(
                filename,
                name=name,
                attachment_type=allure.attachment_type.PNG
            )

        except Exception as e:
            # якщо файл не вдалось зберегти — все одно прикріплюємо байти у Allure
            allure.attach(
                page_open.screenshot(),
                name=f"{name}_{timestamp}",
                attachment_type=allure.attachment_type.PNG
            )
            print(f"[WARNING] Не вдалось записати файл {filename}: {e}")

    # зупиняємо тест
    pytest.fail(message, pytrace=False)

def report_about(message: str, page_open=None, name="screenshot_of_final"):
    # додаємо повідомлення у Allure
    allure.attach(message, name="Тест пройдено", attachment_type=allure.attachment_type.TEXT)
    filename = ""
    # унікальне ім’я файлу
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshots/{name}_{timestamp}.png"
    if page_open:
        try:
            # створюємо папку screenshots (якщо немає)
            os.makedirs("screenshots", exist_ok=True)

            # # унікальне ім’я файлу
            # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # filename = f"screenshots/{name}_{timestamp}.png"

            # робимо скріншот у файл
            page_open.screenshot(path=filename, timeout=40000)

            # прикріплюємо цей файл у Allure
            allure.attach.file(
                filename,
                name=name,
                attachment_type=allure.attachment_type.PNG
            )

        except Exception as e:
            # якщо файл не вдалось зберегти — все одно прикріплюємо байти у Allure
            allure.attach(
                page_open.screenshot(),
                name=f"{name}_{timestamp}",
                attachment_type=allure.attachment_type.PNG
            )
            print(f"[WARNING] Не вдалось записати файл {filename}: {e}")

    # зупиняємо тест
    # pytest.fail(message, pytrace=False)


def detect_script(text1: str) -> str:
    """Визначення локалізації тільки по буквам"""
    text = re.sub(r"[^A-Za-zА-Яа-яЁёЇїІіЄєҐґ]", "", text1)
    if re.fullmatch(r"[А-Яа-яЁёЇїІіЄєҐґ]+", text):
        return "Cyrillic"
    elif re.fullmatch(r"[A-Za-z]+", text):
        return "latin"
    elif re.fullmatch(r"[a-z]+", text):
        return "lowreglat"
    elif re.fullmatch(r"(?=.*{lowreglat})[{lowreglat}]+", text):
        return "lowreglat_1"
    elif re.fullmatch(r"[A-Z]+", text):
        return "upreglat"
    elif re.fullmatch(r"(?=.*{upreglat})[{upreglat}]+", text):
        return "upreglat_1"
    elif re.fullmatch(r"[а-яїієёґ]+", text):
        return "lowregcyr"
    elif re.fullmatch(r"(?=.*{lowregcyr})[{lowregcyr}]+", text):
        return "lowregcyr_1"
    elif re.fullmatch(r"[А-ЯЁЇІЄҐ]+", text):
        return "upregcyr"
    elif re.fullmatch(r"(?=.*{upregcyr})[{upregcyr}]+", text):
        return "upregcyr_1"
    ############################################
    elif re.fullmatch(r"[A-Za-zА-Яа-яЁёЇїІіЄєҐґ]+", text):
        return "lat_Cyr"
    elif re.fullmatch(r"(?=.*[A-ZА-ЯЁЇІЄҐa-zа-яїієёґ])[A-Za-zА-Яа-яЁёЇїІіЄєҐґ]+", text):
        return "lat_Cyr_1"
    elif re.fullmatch(r"(?=.*[A-ZА-ЯЁЇІЄҐ])(?=.*[a-zа-яїієёґ])[A-Za-zА-Яа-яЁёЇїІіЄєҐґ]+", text):
        return "lat_Cyr_1_1"
    elif re.fullmatch(r"(?=.*[А-ЯЁЇІЄҐа-яїієёґ])[А-Яа-яЁёЇїІіЄєҐґ]+", text):
        return "Cyrillic_1"
    elif re.fullmatch(r"(?=.*[А-ЯЁЇІЄҐ])(?=.*[а-яїієёґ])[А-Яа-яЁёЇїІіЄєҐґ]+", text):
        return "Cyrillic_1_1"
    elif re.fullmatch(r"(?=.*[A-Za-z])[A-Za-z]+", text):
        return "latin_1"
    elif re.fullmatch(r"(?=.*[A-Z])(?=.*[a-z])[A-Za-z]+", text):
        return "latin_1_1"
    elif re.fullmatch(r"[A-ZА-ЯЁЇІЄҐ]+", text):
        return "lat_Cyr_up"
    elif re.fullmatch(r"[a-zа-яёїієґ]+", text):
        return "lat_Cyr_low"
    elif re.fullmatch(r"(?=.*[A-ZА-ЯЁЇІЄҐ])[A-ZА-ЯЁЇІЄҐ]+", text):
        return "lat_Cyr_up_1"
    elif re.fullmatch(r"(?=.*[a-zа-яёїієґ])[a-zа-яёїієґ]+", text):
        return "lat_Cyr_low_1"
    # elif re.fullmatch(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]", text):
    #     return "latin"
    # elif re.fullmatch(r"(http://|https://)([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(:\d+)?(/[^\s?#]*)?(\?[^\s#]*)?(#[^\s]*)?", text):
    #     return "latin"
    return "Unknown"

def entries_rules(log, required, fame, **kwargs):
    global pattern, chars, len_min, len_max, latin, Cyrillic, spec_escaped, rule_invalid, no_absent, upregcyr, upreglat, lowregcyr, lowreglat, lat_Cyr_1, latin_1, Cyrillic_1, lat_Cyr_up, lat_Cyr_low, lat_Cyr_1, lat_Cyr, spec, digits_str_1, digits_str, spec_escaped, spec_escaped_1

    entries = kwargs["entries"]
    # инициализация переменных
    local = ""
    latin = "[A-Za-z]"
    Cyrillic = "[А-Яа-яЁёЇїІіЄєҐґ]"
    upregcyr = "[А-ЯЁЇІЄҐ]"
    lowregcyr = "[а-яїієёґ]"
    upreglat = "[A-Z]"
    lowreglat = "[a-z]"
    both_reg = False
    digits_str = ""
    spec_escaped = ""
    is_probel = False
    no_absent = False
    len_min = 0
    len_max = 0
    email = False
    url = False
    up = False
    low = False
    register_at_least_one = entries['register_at_least_one']
    spec_at_least_one = entries['spec_at_least_one']
    localiz_at_least_one = entries['localiz_at_least_one']
    cyfry_at_least_one = entries['cyfry_at_least_one']

    for key, value in entries.items():
        if key == 'register':
            if value == 'великий':
                up = True
            elif value == "малий":
                low = True
            elif value == "будь який":
                any_reg = True
            elif value == "обидва":
                both_reg = True
        # elif key == "register_at_least_one":
        #     register_at_least_one = value
        # elif key == "localiz_at_least_one":
        #     localiz_at_least_one = value
        elif key == 'localiz' and value:
            if value == 'латиниця':
                if up:
                    local = upreglat
                    if localiz_at_least_one:
                        local = upreglat_1
                elif low:
                    local = lowreglat
                    if localiz_at_least_one:
                        local = lowreglat_1
                elif both_reg:
                    if register_at_least_one:
                        local = latin_1_1
                    else:
                        local = latin
                else:
                    local = latin
                    if localiz_at_least_one:
                        local = latin_1
            elif value == 'кирилиця':
                if up:
                    local = upregcyr
                    if localiz_at_least_one:
                        local = upregcyr_1
                elif low:
                    local = lowregcyr
                    if localiz_at_least_one:
                        local = lowregcyr_1
                elif both_reg:
                    if register_at_least_one:
                        local = Cyrillic_1_1
                    else:
                        local = Cyrillic
                else:
                    local = Cyrillic
                    if localiz_at_least_one:
                        local = Cyrillic_1
            elif value == "латиниця і кирилиця":
                if up:
                    local = lat_Cyr_up
                    if localiz_at_least_one:
                        local = lat_Cyr_up_1
                elif low:
                    local = lat_Cyr_low
                    if localiz_at_least_one:
                        local = lat_Cyr_low_1
                elif both_reg:
                    if register_at_least_one:
                        local = lat_Cyr_1_1
                    else:
                        local = lat_Cyr
                else:
                    local = lat_Cyr
                    if localiz_at_least_one:
                        local = lat_Cyr_1
        # elif key == "localiz_at_least_one" and value:
        #     if up:
        #         local = lat_Cyr_up_1
        #     elif low:
        #         local = lat_Cyr_low_1
        #     elif both_reg:
        #         if register_at_least_one:
        #             local = lat_Cyr_1
        #         else:
        #             local = lat_Cyr
        #     else:
        #         local = lat_Cyr_1
        elif key == "cyfry" and value:
            digits_str = "[0-9]"
            if cyfry_at_least_one:
                digits_str = f"(?=.*\d){digits_str}"
                digits_str_1 = True
        # elif key == "cyfry_at_least_one" and value:
        #     digits_str = f"(?=.*\d){digits_str}"
        #     digits_str_1 = True
        elif key == "spec" and value:
            if isinstance(value, str):
                spec_escaped = "".join(re.escape(ch) for ch in value)
            else:
                spec_escaped = "".join(re.escape(ch) for ch in spec)
        # elif key == "spec_at_least_one":
        #     spec_at_least_one = value
        elif key == "len_min":
            len_min = value
        elif key == "len_max":
            if value and value != 0:
                len_max = value
            else:
                len_max = None
        elif key == "email_in":
            email = value
        elif key == "url_in":
            url = value
        elif key == "no_absent":
            no_absent = value
        elif key == "probel":
            is_probel = value
    if email:
        # chars = "a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-."
        chars = "[a-zA-Z0-9_.+-@]"
    elif url:
        # chars = "http?://[^\s/$.?#].[^\s"
        # chars = "a-zA-Z0-9\-_.~:/?#\[\]@!$&'()*+,;=%"
        chars = "[a-zA-Z0-9_.~:/?#@!$&'()*+,;=%-]"
    elif no_absent:
        chars = "."
    else:
        # собираем разрешённые символы
        parts = []
        if local:
            parts.append(local)
        if digits_str:
            parts.append(digits_str)
        # if not is_probel and not no_absent:
        #     parts.append(' ')
        if spec_escaped:
            if spec_at_least_one:
                spec_escaped = f"(?=.*[{spec_escaped}])[{spec_escaped}]"
                spec_escaped_1 = True
            else:
                spec_escaped = f"[{spec_escaped}]"
            parts.append(spec_escaped)
        chars = "".join(parts) or "." # если ничего не выбрано — разрешаем всё
    # є пробіли
    if not is_probel:
        # pattern = "^(?=.*\s)["+f"{chars}"+"]+$"
        # pattern = "^(?=.*\s)["+f"{chars}]\{{len_min, len_max}\}$"
        # pattern = rf"^(?=.*\s)[{chars}]{{{len_min},{len_max}}}$"
        # не пустое с пробелами
        if no_absent:
            # хоч один пробіл без меж довжини строки
            pattern = rf"^(?=.*\s)[{chars}]+$"
        else:
            # хоч один пробіл в межах довжини строки
            if len_max is not None:
                pattern = rf"^(?=.*\s)[{chars}]{{{len_min},{len_max}}}$"
            else:
                pattern = rf"^(?=.*\s)[{chars}]{{{len_min}}}$"
    # немає пробілів
    else:
        # pattern = "^["+f"{chars}"+"]+$"
        # pattern = "^["+f"{chars}]\{{len_min}, {len_max}\}$"
        # pattern = rf"^[{chars}]{{{len_min},{len_max}}}$"
        # не пустое без пробелов без ограничения длины строки
        if no_absent:
            if "(?=." in chars:
                pattern = rf"^{chars}+$"
            else:
                pattern = rf"^{chars}+$"
        else:
            if len_max is not None:
                if "(?=." in chars:
                    pattern = rf"^{chars}{{{len_min},{len_max}}}$"
                else:
                    # набір символів в межах довжини строки без пробілів
                    pattern = rf"^{chars}{{{len_min},{len_max}}}$"
            else:
                if "(?=." in chars:
                    pattern = rf"^{chars}{{{len_min}}}$"
                else:
                    pattern = rf"^{chars}{{{len_min}}}$"
                # # набір символів в межах довжини строки без пробілів
                # pattern = rf"^[{chars}]{{{len_min}}}$"


    if email:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    elif url:
        # pattern = r"^(http://|https://)[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+$"
        # pattern = r"^(http://|https://)[^\s/$.?#].[^\s]+$"
        # pattern = r"^(http://|https://)[^\s]+$"
        # pattern = r"^(http://|https://)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/[^\s]*)?$"
        pattern = r"^(http://|https://)([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(:\d+)?(/[^\s?#]*)?(\?[^\s#]*)?(#[^\s]*)?$"
    # QMessageBox.information(None, "Символи", chars)
    # QMessageBox.information(None, "Шаблон", pattern)
    rule_invalid[fame] = []
    if url:
        rule_invalid[fame].append("no_url")
        rule_invalid[fame].append("localiz latin")
    if (not email) and (not url) and (not no_absent):
        if len_max is not None:
            rule_invalid[fame].append(f"len {len_min} {len_max}")
        else:
            rule_invalid[fame].append(f"len {len_min}")
    if email:
        rule_invalid[fame].append("no_email")
        rule_invalid[fame].append("localiz latin")
    if both_reg:
        rule_invalid[fame].append("no_lower")
        rule_invalid[fame].append("no_upper")
    if digits_str and digits_str_1:
        rule_invalid[fame].append("no_digit")
    if spec_escaped and spec_escaped_1:
        rule_invalid[fame].append("no_spec")
    if has_text_special_chars(pattern):
        rule_invalid[fame].append("add_spec")
    if digits_str == "":
        rule_invalid[fame].append("add_digit")
    # немає пробілів
    if is_probel and not no_absent:
        rule_invalid[fame].append("probel")
    # є пробіли
    else:
        if not no_absent:
            rule_invalid[fame].append("no_probel")
    if local == latin:
        rule_invalid[fame].append("Cyrillic")
        rule_invalid[fame].append("localiz latin")
    elif local == upreglat:
        rule_invalid[fame].append("lowregcyr")
        rule_invalid[fame].append("localiz upreglat")
    elif local == lowreglat:
        rule_invalid[fame].append("upregcyr")
        rule_invalid[fame].append("localiz lowreglat")
    elif local == Cyrillic:
        rule_invalid[fame].append("latin")
        rule_invalid[fame].append("localiz Cyrillic")
    elif local == upregcyr:
        rule_invalid[fame].append("lowreglat")
        rule_invalid[fame].append("localiz upregcyr")
    elif local == lowregcyr:
        rule_invalid[fame].append("upreglat")
        rule_invalid[fame].append("localiz lowregcyr")
    elif local == Cyrillic_1:
        rule_invalid[fame].append("latin")
        rule_invalid[fame].append("localiz Cyrillic_1")
    elif local == latin_1:
        rule_invalid[fame].append("Cyrillic")
        rule_invalid[fame].append("localiz latin_1")
    elif local == lat_Cyr_1:
        rule_invalid[fame].append("Cyrillic")
        rule_invalid[fame].append("localiz lat_Cyr_1")
    elif local == lat_Cyr:
        rule_invalid[fame].apped("latin")
        rule_invalid[fame].append("localiz lat_Cyr")
    elif local == lat_Cyr_up:
        rule_invalid[fame].append("lowregcyr")
        rule_invalid[fame].append("localiz lat_Cyr_up")
    elif local == lat_Cyr_low:
        rule_invalid[fame].append("upregcyr")
        rule_invalid[fame].append("localiz lat_Cyr_low")
    elif local == lat_Cyr_up_1:
        rule_invalid[fame].append("lat_Cyr_low")
        rule_invalid[fame].append("localiz lat_Cyr_up_1")
    elif local == lat_Cyr_low_1:
        rule_invalid[fame].append("lat_Cyr_up")
        rule_invalid[fame].append("localiz lat_Cyr_low_1")
    elif local == upregcyr_1:
        rule_invalid[fame].append("lowreglat")
        rule_invalid[fame].append("localiz upregcyr_1")
    elif local == lowregcyr_1:
        rule_invalid[fame].append("upreglat")
        rule_invalid[fame].append("localiz lowregcyr_1")
    elif local == upreglat_1:
        rule_invalid[fame].append("lowregcyr")
        rule_invalid[fame].append("localiz upreglat_1")
    elif local == lowreglat_1:
        rule_invalid[fame].append("upregcyr")
        rule_invalid[fame].append("localiz lowreglat_1")
    elif local == Cyrillic_1_1:
        rule_invalid[fame].append("latin")
        rule_invalid[fame].append("localiz Cyrillic_1_1")
    elif local == latin_1_1:
        rule_invalid[fame].append("Cyrillic")
        rule_invalid[fame].append("localiz latin_1_1")
    elif local == lat_Cyr_1_1:
        rule_invalid[fame].append("latin")
        rule_invalid[fame].append("localiz lat_Cyr_1_1")
    # if both_reg:
    #     rule_invalid[fame].append("one_reg_log")
    if no_absent and not "absent" in rule_invalid[fame]:
        rule_invalid[fame].append("absent")
    # print(pattern)
    return pattern

EXTRA_CYRILLIC = {
    "А-Я": "ЁЇІҐ",
    "а-я": "ёїіґ",
}

# дефисы/тире, которые иногда попадают из копипаста — нормализуем в ASCII '-'
HYPHENS = {"\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2212"}

def normalize_allowed_string(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    return "".join("-" if ch in HYPHENS else ch for ch in s)

def _escape_for_charclass(ch: str) -> str:
    if ch in r"\^-]":
        return "\\" + ch
    return ch

def _parse_allowed_string(allowed: str) -> Tuple[str, Set[str]]:
    allowed = normalize_allowed_string(allowed)
    ranges = []
    singles = []
    s = allowed
    i = 0
    while i < len(s):
        if (
            i + 2 < len(s)
            and s[i+1] == '-'
            and (s[i].isalpha() or s[i].isdigit())
            and (s[i+2].isalpha() or s[i+2].isdigit())
        ):
            a, b = s[i], s[i+2]
            if ord(a) > ord(b):
                raise ValueError(f"Invalid range {a}-{b}: start > end")
            ranges.append((a, b))
            i += 3
        else:
            singles.append(s[i])
            i += 1

    parts = []
    allowed_set = set()

    for a, b in ranges:
        parts.append(f"{a}-{b}")
        for code in range(ord(a), ord(b) + 1):
            allowed_set.add(chr(code))
        if a == "А" and b == "Я":
            allowed_set.update(EXTRA_CYRILLIC["А-Я"])
            parts.append(EXTRA_CYRILLIC["А-Я"])
        elif a == "а" and b == "я":
            allowed_set.update(EXTRA_CYRILLIC["а-я"])
            parts.append(EXTRA_CYRILLIC["а-я"])

    for ch in singles:
        parts.append(_escape_for_charclass(ch))
        allowed_set.add(ch)

    charclass = "".join(parts)
    return charclass, allowed_set

def validate_chars_mode(text: str, allowed: str) -> Tuple[bool, Optional[str]]:
    if text == "":
        return True, None
    try:
        charclass, allowed_set = _parse_allowed_string(allowed)
    except ValueError as e:
        return False, f"INVALID_ALLOWED_SPEC: {e}"
    regex = fr'^[{charclass}]*$'
    if re.fullmatch(regex, text):
        return True, None
    for ch in text:
        if ch not in allowed_set:
            return False, ch
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

# ---- Динамическая форма ----
class DynamicDialog(QDialog):
    def __init__(self, config, parent=None, input_url=None, input_login=None, input_login_l=None, input_password=None, input_email=None, name_of_test=""):
        super().__init__(parent)
        self.setWindowTitle("Введення даних у тест    "+name_of_test)
        self.resize(640, 140)
        self.result = {}
        self.result_invalid = {}
        self.result_title_fields = {}
        self.result_fields = {}
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
            gb_widget.setObjectName(name)
            gb_widget.setStyleSheet("background-color: rgb(85, 255, 127);")
            gb_widget.setLocale(QLocale(QLocale.Ukrainian, QLocale.Ukraine))
            gb_widget.setMinimumHeight(60)
            self.result_title_fields[title] = name
            # элементы
            cmb = QComboBox(gb_widget)
            cmb.setEditable(False)
            chkb = QCheckBox("Обов'язкове", gb_widget)
            # привязываем чекбокс к комбобоксу
            # cmb.checkbox = chkb
            if name == 'url_of_page':
                cmb.addItems(input_url)
                cmb.setCurrentText(input_url[0])
            if name == 'url':
                cmb.addItems(input_url)
                cmb.setCurrentText(input_url[0])
            if name in ('login', 'Login', 'First name', 'first name', 'First_name', 'first_name'):
                cmb.addItems(input_login)
                cmb.setCurrentText(input_login[0])
            if name in ('login_l', 'Last name', 'last name', 'Last_name', 'last_name'):
                cmb.addItems(input_login_l)
                cmb.setCurrentText(input_login_l[0])
            if name in ('password', 'Password'):
                cmb.addItems(input_password)
                cmb.setCurrentText(input_password[0])
            if name in ('email', 'Email'):
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
            # chkb.toggled.connect(partial(self.on_required_toggled, name))
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
            # подія отримання фокусу групбоксом
            gb_widget.focusEntered.connect(self.on_gb_focus_entered)

        # ---- Кнопки OK/Відміна внизу ----
        btn_layout = QHBoxLayout()
        font = QFont()
        font.setBold(True)

        self.btnOK = QPushButton("Введення")
        # Устанавливаем кнопку по умолчанию
        self.btnOK.setDefault(True)
        self.btnOK.setFont(font)
        self.btnCnl = QPushButton("Відміна")
        self.btnCnl.setFont(font)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btnOK)
        btn_layout.addWidget(self.btnCnl)
        main_layout.addLayout(btn_layout)

        # события кнопок
        self.btnOK.clicked.connect(self.on_ok_clicked)
        self.btnCnl.clicked.connect(self.on_cnl_clicked)

    cur_rules ={}
        # ---- обработчики ----

    def on_text_changed(self, text: str) -> bool:
        combo = self.sender()  # тот QComboBox, который вызвал сигнал
        global chars, pattern
        if not text:
            return True
        pred_txt = self.previous_text
        # если chars == ".", разрешаем всё
        if chars == ".":
            return True
        if len(pred_txt) < len(text):
            # текст доодається
            ok, bad = validate_chars_mode(text, chars)
        else:
            # текст видаляється
            ok = True
        if not ok:
            QMessageBox.warning(self, "Помилка вводу", f"Недопустимий символ: '{bad}'")
            combo.blockSignals(True)
            combo.setCurrentText(pred_txt)
            combo.blockSignals(False)
            combo.setFocus()
            return False
        else:
            # всё ок — обновляем previous_text
            self.previous_text = text
            return True

    def on_gb_focus_entered(self):
        gb = self.sender()
        self.previous_text = gb.cmb.currentText()


    # втрата фокусу групбоксом
    def on_gb_focus_left(self):
        gb = self.sender()
        global chars, pattern, len_min, len_max, rule_invalid, spec
        gr_t_title = gb.title()
        gr_t = gb.objectName()
        # cur_txt = gb.cmb.currentText()
        # Якщо chars == ".", дозволяємо все
        if chars == ".":
            pattern = rf"^[{chars}]+$"
            self.previous_text = gb.cmb.currentText()
            # self.previous_text = ''
            return True

        # Перевірка на відповідність pattern
        txt_err = ""
        # if not bool(re.fullmatch(pattern, gb.cmb.currentText())):
        #     if "no_lower" in rule_invalid[gr_t] and not any(c.islower() for c in gb.cmb.currentText()):
        #         txt_err += "має містити принаймні одну маленьку літеру\n"
        #     if "no_upper" in rule_invalid[gr_t] and not any(c.isupper() for c in gb.cmb.currentText()):
        #         txt_err += "має містити принаймні одну велику літеру\n"
        #     if "no_digit" in rule_invalid[gr_t] and not any(c.isdigit() for c in gb.cmb.currentText()):
        #         txt_err += "має містити принаймні одну цифру\n"
        #     if "no_spec" in rule_invalid[gr_t] and not any(c in spec_escaped for c in gb.cmb.currentText()):
        #         txt_err += f"має містити принаймні один спеціальний символ з {spec_escaped}\n"
        #     if "no_email" in rule_invalid[gr_t]:
        #         txt_err += "має бути формату email\n"
        #     if "no_url" in rule_invalid[gr_t]:
        #         txt_err += "має бути формату URL\n"
        #     if f"len {len_min} {len_max}" in rule_invalid[gr_t] and (len_max < len(gb.cmb.currentText()) or len(gb.cmb.currentText()) < len_min):
        #         txt_err += f"має мати від {len_min} до {len_max} символів включно\n"
        #     if "probel" in rule_invalid[gr_t] and gb.cmb.currentText().find(' ') > -1:
        #         txt_err += "не має бути з пробілами\n"
        #     if "no_probel" in rule_invalid[gr_t] and gb.cmb.currentText().find(' ') == -1:
        #         txt_err += "має бути з пробілами\n"
            # if "one_reg_log" in rule_invalid[gr_t]:
            #     txt_err += "має бути з текстом у двох регістрах\n"
        for el_t in rule_invalid[gr_t]:
            sp_simv = has_text_special_chars(pattern)
            sp_sim1 = any(c in spec for c in gb.cmb.currentText())
            if el_t[:7] == "localiz":
                # локализация установленная, полная, с учётом всех символов и регистра
                localiz = el_t[8:]
                # сновная, определённая по символам, локализация (без цифр, спецсимволов и т.д.)
                loc_text = detect_script(gb.cmb.currentText())
                # if loc_text == "lat_Cyr":
                result = "".join((c1 + c2) if c1 != c2 else "" for c1, c2 in zip_longest(localiz, loc_text, fillvalue=""))
                if result[:1] == "_":
                    loc_text = localiz
                if localiz != loc_text:
                    if localiz == "latin":
                        txt_err += "може бути з латиницею\n"
                    if localiz == "Cyrillic":
                        txt_err += "може бути з кирилицею\n"
                    if localiz == "lowreglat":
                        txt_err += "може бути з малою латиницею\n"
                    if localiz == "upreglat":
                        txt_err += "може бути з великою латиницею\n"
                    if localiz == "loeregcyr":
                        txt_err += "може бути з малою кирилицею\n"
                    if localiz == "upregcyr":
                        txt_err += "може бути з великою кирилицею\n"
                    if localiz == "lowreglat_1":
                        txt_err += "має бути з малою латиницею\n"
                    if localiz == "upreglat_1":
                        txt_err += "має бути з великою латиницею\n"
                    if localiz == "loeregcyr_1":
                        txt_err += "має бути з малою кирилицею\n"
                    if localiz == "upregcyr_1":
                        txt_err += "має бути з великою кирилицею\n"
                    if localiz == "latin_1":
                        txt_err += "має бути хоча б з 1 символом латиниці\n"
                    if localiz == "Cyrillic_1":
                        txt_err += "має бути хоча б з 1 символом кирилиці\n"
                    if localiz == "latin_1_1":
                        txt_err += "має бути хоча б з 1 символом латиниці в великому та малому регістрах\n"
                    if localiz == "Cyrillic_1_1":
                        txt_err += "має бути хоча б з 1 символом кирилиці в великому та малому регістрах\n"
                    if localiz == "lat_Cyr":
                        txt_err += "може бути з латиницею і кирилицею\n"
                    if localiz == 'lat_Cyr_1_1':
                        txt_err += "має бути хоча б з 1 символом латиниці або кирилиці в великому і малому регістрі\n"
                    if localiz == "lat_Cyr_1":
                        txt_err += "має бути хоча б з 1 символом латиниці або кирилиці\n"
                    if localiz == 'lat_Cyr_up':
                        txt_err += "може бути з великими символами латиниці і кирилиці\n"
                    if localiz == "lat_Cyr_low":
                        txt_err += "може бути з малими символами латиниці і кирилиці\n"
                    if localiz == "lat_Cyr_up_1":
                        txt_err += "має бути хоча б з 1 великим символом латиниці і 1 великим символом кирилиці\n"
                    if localiz == "lat_Cyr_low_1":
                        txt_err += "має бути хоча б з 1 малим символом латиниці і 1 малим символом кирилиці\n"
            else:
                if "no_lower" in rule_invalid[gr_t] and not any(c.islower() for c in gb.cmb.currentText()):
                    txt_err += "має містити принаймні одну маленьку літеру\n"
                if "no_upper" in rule_invalid[gr_t] and not any(c.isupper() for c in gb.cmb.currentText()):
                    txt_err += "має містити принаймні одну велику літеру\n"
                if "no_digit" in rule_invalid[gr_t] and not any(c.isdigit() for c in gb.cmb.currentText()):
                    txt_err += "має містити принаймні одну цифру\n"
                if "no_spec" in rule_invalid[gr_t] and not any(c in spec_escaped for c in gb.cmb.currentText()):
                    txt_err += f"має містити принаймні один спеціальний символ з {spec_escaped}\n"
                if "no_email" in rule_invalid[gr_t] and not bool(re.fullmatch(pattern, gb.cmb.currentText())):
                    txt_err += "має бути формату email\n"
                if "no_url" in rule_invalid[gr_t] and not bool(re.fullmatch(pattern, gb.cmb.currentText())):
                    txt_err += "має бути формату URL\n"
                if f"len {len_min} {len_max}" in rule_invalid[gr_t] and (
                        len_max < len(gb.cmb.currentText()) or len(gb.cmb.currentText()) < len_min):
                    txt_err += f"має мати від {len_min} до {len_max} символів включно\n"
                if "probel" in rule_invalid[gr_t] and gb.cmb.currentText().find(' ') > -1:
                    txt_err += "не має бути з пробілами\n"
                if "no_probel" in rule_invalid[gr_t] and gb.cmb.currentText().find(' ') == -1:
                    txt_err += "має бути з пробілами\n"
                # if not re.search(r"[^A-Za-zА-Яа-яЁёЇїІіЄєҐґ0-9\s]", pattern) and any(c in spec for c in gb.cmb.currentText()):
                #     txt_err += "не має бути зі спецсимволами"
                if not has_text_special_chars(pattern) and any(c in spec for c in gb.cmb.currentText()):
                    txt_err += "не має бути зі спецсимволами"
                if not re.search(r"\d", pattern) and any(c.isdigit() for c in gb.cmb.currentText()):
                    txt_err = "не мє бути з цифрами"
                        # break
            if txt_err != "":
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title}\n"+txt_err)
                # gb.cmb.setFocus()
                return False
        # Якщо все добре, зберігаємо нове значення
        self.previous_text = gb.cmb.currentText()
        chars == "."
        pattern = rf"^[{chars}]+$"
        return True

    # нажатие на кнопку Правила
    def on_rules_clicked(self, combo, field_name):
        global rule_invalid
        for name, wrapper in self.gb.items():
            # wrapper = GroupBoxWrapper()
            chck_stat = wrapper.chkb.isChecked()
            if wrapper.cmb is combo:
                wrapper.cmb.setEditable(True)  # текущий делаем редактируемым
                # combo.setEditable(True)
                wrapper.gb.setStyleSheet("background-color: rgb(255, 255, 200);")  # подсветка
            else:
            # #для случая когда поле, а не комбобокс
            #     if wrapper.cmb.isEditable():
            #         # сохранить введённый текст
            #         current_text = wrapper.cmb.currentText().strip()
            #         if current_text:
            #             items = [wrapper.cmb.itemText(i) for i in range(wrapper.cmb.count())]
            #             if current_text not in items:
            #                 wrapper.cmb.addItem(current_text)  # добавляем в список
            #             # получаем индекс добавленного или существующего значения
            #             idx = wrapper.cmb.findText(current_text)
            #             if idx >= 0:
            #                 wrapper.cmb.setCurrentIndex(idx)
            #         # теперь можно выключить редактирование
            #     wrapper.cmb.setEditable(False)
                wrapper.gb.setStyleSheet("background-color: rgb(85, 255, 127);")
        rule_invalid[field_name] = []
        dlg = MyDialog()

        dlg.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        dlg.setModal(True)
        if dlg.exec() == QDialog.Accepted:  # ← проверка, нажата ли OK
            cur_rules = dlg.result  # ← берём результат после закрытия
            # if not entries_rules(wrapper.cmb.currentText(), chck_stat, field_name, entries=cur_rules):
            if not entries_rules(combo.currentText(), chck_stat, field_name, entries=cur_rules):
                self.reject()
        # wrapper.cmb.setFocus()
        combo.setFocus()

    def on_ok_clicked(self):
        """Срабатывает при нажатии кнопки 'Введення' — собирает данные и закрывает диалог."""
        global rule_invalid
        titles = []
        for name, wrapper in self.gb.items():
            if not name in rule_invalid:
                rule_invalid[name] = []
            if len(rule_invalid[name]) == 0:
                msg = QMessageBox(self)
                msg.setWindowTitle("Підтвердження")
                msg.setText(f"Натискаючи Продовжити ви залишаєте правила створення строки в полі {wrapper.gb.title()} по замовчуванню \"НЕ ПУСТЕ\"\nПРОДОВЖИТИ?")
                msg.setIcon(QMessageBox.Question)
                yes_btn = msg.addButton("Продовжити", QMessageBox.YesRole)
                no_btn = msg.addButton("Скасувати", QMessageBox.NoRole)
                msg.exec()
                if msg.clickedButton() == no_btn:
                    return False

                rule_invalid[name].append("absent")
            if wrapper.chkb.isChecked():
                if wrapper.cmb.currentText() != "":
                    self.result[name] = wrapper.cmb.currentText()
                    if name != 'url_of_page':
                        self.result_fields[name] = wrapper.cmb.currentText()
                else:
                    titles.append(wrapper.gb.title())
        # self.result['fix_enter'] = self.
        if len(titles) > 0:
            QMessageBox.warning(self, f"Поля {titles}", "Обов'язкові дані не введені.")
            return False
        for key, value in rule_invalid.items():
            val_new = []
            for el in value:
                if el[:7] != "localiz":
                    val_new.append(el)
            self.result_invalid[key] = val_new
        # self.result_invalid = rule_invalid
        self.accept()

    def on_cnl_clicked(self):
        # gb = self.sender()
        # if wrapper.cmb.hasFocus():
        #     self.btnCnl.setFocus()
        self.reject()

def get_user_input():
    global number_of_test
    # Проверяем, есть ли QApplication
    app = QApplication.instance()
    created_app = False
    if app is None:
        app = QApplication(sys.argv)
        created_app = True
    input_dlg = ConfigInputDialog()
    if input_dlg.exec() != QDialog.Accepted:
        return None  # пользователь отменил ввод

    config = input_dlg.get_config()
    dlg = DynamicDialog(config, input_url=input_data['url'], input_login=input_data['login'],
                      input_login_l=input_data['login_l'], input_password=input_data['password'],
                      input_email=input_data['email'], name_of_test="")
    if dlg.exec() == QDialog.Accepted:
        if created_app:
            app.quit()
        if input_dlg.radio_event.isChecked():
            dlg.result["fix_enter"] = 0
        if input_dlg.radio_enter.isChecked():
            dlg.result["fix_enter"] = 1
        if input_dlg.radio_button.isChecked():
            dlg.result["fix_enter"] = 2
        dlg.result['check_attr'] = input_dlg.attr_input.text()
        dlg.result['el_fix_after_fill'] = input_dlg.html_input.text()
        dlg.result['txt_el_fix_after_fill'] = input_dlg.text_input.text()
        result_f = dlg.result, dlg.result_invalid, dlg.result_title_fields, dlg.result_fields
        return result_f
    return None
# # ---- Основной запуск ----
# if __name__ == "__main__":
#     get1_2 = get_user_input()
#     if get1_2 is not None:
#         print(str(get1_2[0])+"\n"+str(get1_2[1])+"\n"+str(get1_2[2])+"\n"+str(get1_2[3]))
