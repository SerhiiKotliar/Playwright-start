
# from PySide6.QtCore import QLocale, Qt
# from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QDialog, QSpinBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QWidget, QGroupBox,
    QComboBox, QCheckBox, QMessageBox, QRadioButton, QButtonGroup
)
import allure
from pyside_dialog import MyDialog
from Config_dialog import ConfigInputDialog
from form_filling_fields import DynamikDialog
from mycombo import QComboBox, WhichBinding
from mygroupbox_dynamic import MyGroupBox
import sys
import re, unicodedata
from typing import Tuple, Set, Optional
from datetime import datetime
import os
import pytest
from itertools import zip_longest


rule_invalid = {}
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
digits_str = ""
digits_str_1 = False






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
    # унікальне ім’я файлу
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshots/{name}_{timestamp}.png"
    if page_open:
        try:
            # створюємо папку screenshots (якщо немає)
            os.makedirs("screenshots", exist_ok=True)

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
    # унікальне ім’я файлу
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshots/{name}_{timestamp}.png"
    if page_open:
        try:
            # створюємо папку screenshots (якщо немає)
            os.makedirs("screenshots", exist_ok=True)

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
    return "Unknown"

def entries_rules(log, required, fame, **kwargs):
    global pattern, chars, len_min, len_max, latin, Cyrillic, spec_escaped, rule_invalid, no_absent, upregcyr, upreglat, lowregcyr, lowreglat, lat_Cyr_1, latin_1, Cyrillic_1, lat_Cyr_up, lat_Cyr_low, lat_Cyr_1, lat_Cyr, spec, digits_str_1, digits_str, spec_escaped, spec_escaped_1

    entries = kwargs["entries"]
    # инициализация переменных
    local = ""
    # latin = "[A-Za-z]"
    # Cyrillic = "[А-Яа-яЁёЇїІіЄєҐґ]"
    # upregcyr = "[А-ЯЁЇІЄҐ]"
    # lowregcyr = "[а-яїієёґ]"
    # upreglat = "[A-Z]"
    # lowreglat = "[a-z]"
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
        elif key == "cyfry" and value:
            digits_str = "[0-9]"
            if cyfry_at_least_one:
                digits_str = f"(?=.*\d){digits_str}"
                digits_str_1 = True
        elif key == "spec" and value:
            if isinstance(value, str):
                spec_escaped = "".join(re.escape(ch) for ch in value)
            else:
                spec_escaped = "".join(re.escape(ch) for ch in spec)
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
        chars = "[a-zA-Z0-9_.+-@]"
    elif url:
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
        # не пустое без пробелов без ограничения длины строки
        if no_absent:
            # if "(?=." in chars:
            #     pattern = rf"^{chars}+$"
            # else:
            pattern = rf"^{chars}+$"
        else:
            if len_max is not None:
                # if "(?=." in chars:
                #     pattern = rf"^{chars}{{{len_min},{len_max}}}$"
                # else:
                    # набір символів в межах довжини строки без пробілів
                pattern = rf"^{chars}{{{len_min},{len_max}}}$"
            else:
                # if "(?=." in chars:
                #     pattern = rf"^{chars}{{{len_min}}}$"
                # else:
                pattern = rf"^{chars}{{{len_min}}}$"
                # # набір символів в межах довжини строки без пробілів
                # pattern = rf"^[{chars}]{{{len_min}}}$"


    if email:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    elif url:
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


def get_user_input():
    global number_of_test
    # Проверяем, есть ли QApplication
    app = QApplication.instance()
    created_app = False
    if app is None:
        app = QApplication(sys.argv)
        created_app = True
    input_dlg = ConfigInputDialog()

    # Заполняем отдельные поля
    # input_dlg.attr_input.setText('//*[@id="error_1_id_text_string"]')
    input_dlg.html_input.setText('button')
    input_dlg.text_input.setText('Register')
    input_dlg.radio_button.setChecked(False) #фіксація ввеедення кнопкою
    input_dlg.radio_event.setChecked(True) #фіксація введення по події виходу з поля
    input_dlg.radio_enter.setChecked(False) #фіксація введення клавішею Enter
    # Задаём количество полей (вызовет update_entries и создаст line_edits)
    input_dlg.spin.setValue(2)

    # Теперь можно заполнять каждое поле напрямую через виджеты
    titles = ['URL of page', 'Користувач', 'Пароль']
    names = ['url_of_page', 'Username', 'Password']

    for i, (title, name) in enumerate(zip(titles, names)):
        t_edit, n_edit, chk = input_dlg.line_edits[i]
        t_edit.setText(title)
        n_edit.setText(name)
        chk.setChecked(True)

    # Запускаем диалог
    if input_dlg.exec() != QDialog.Accepted:
        return None
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
