import tkinter as tk
from tkinter import messagebox
import re
import string
import os
from datetime import datetime

import pytest
import allure
# from urllib.parse import urlparse
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt
from pyside_dialog import MyDialog  # твоя PySide форма
import os
from tkinter import ttk
# from tkinter import simpledialog
from helper import debug
# _root = None  # глобальная ссылка на root


email = False
url = False
len_min = 4
len_max = 16
lenminlog = 4
lenmaxlog = 16
lenminlog_l = 1
lenmaxlog_l = 30
lenminpas = 8
lenmaxpas = 20
local = ""
latin = "A-Za-z"
Cyrillic = "А-Яа-я"
# spec = "!@#$%^&*()-_=+[]{};:,.<>/?\\|"
spec = ""
upregcyr = "А-Я"
lowregcyr = "а-я"
upreglat = "A-Z"
lowreglat = "a-z"
both_reg = False
digits_str = ""
spec_escaped = ""
is_probel = False
pattern: str = ""
patterne: str = ""
patternu: str = ""
patternlog: str = ""
patternlog_l: str = ""
patternpas: str = ""
chars: str = ""
both_reg_log = False
both_reg_log_l = False
digits_str_log = ""
digits_str_log_l = ""
spec_escaped_log = ""
spec_escaped_log_l = ""
both_reg_p = False
digits_str_p = ""
spec_escaped_p = ""
number_of_test = 0
create_acc = False


def report_bug_and_stop(message: str, page_open=None, name="screenshot_of_skip"):
    # додаємо повідомлення у Allure
    allure.attach(message, name="Причина зупинки", attachment_type=allure.attachment_type.TEXT)
    filename = ""
    if page_open:
        try:
            # створюємо папку screenshots (якщо немає)
            os.makedirs("screenshots", exist_ok=True)

            # унікальне ім’я файлу
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/{name}_{timestamp}.png"

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
                name=f"{name}_fallback",
                attachment_type=allure.attachment_type.PNG
            )
            print(f"[WARNING] Не вдалось записати файл {filename}: {e}")

    # зупиняємо тест
    pytest.fail(message, pytrace=False)

def report_about(message: str, page_open=None, name="screenshot_of_final"):
    # додаємо повідомлення у Allure
    allure.attach(message, name="Тест пройдено", attachment_type=allure.attachment_type.TEXT)
    filename = ""
    if page_open:
        try:
            # створюємо папку screenshots (якщо немає)
            os.makedirs("screenshots", exist_ok=True)

            # унікальне ім’я файлу
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/{name}_{timestamp}.png"

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
                name=f"{name}_fallback",
                attachment_type=allure.attachment_type.PNG
            )
            print(f"[WARNING] Не вдалось записати файл {filename}: {e}")

    # зупиняємо тест
    # pytest.fail(message, pytrace=False)



def entries_rules(fame, **kwargs):
    global pattern, chars, len_min, len_max, latin, Cyrillic, spec_escaped, is_probel, email, url, both_reg, both_reg_log_l, patternlog, patternlog_l, patternpas, lenminpas, lenmaxpas, lenminlog, lenmaxlog, lenminlog_l, lenmaxlog_l, spec, digits_str, digits_str_log_l, patterne, patternu

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
        if key == 'localiz':
            if value == 'латиниця':
                local = latin
            elif value == 'кирилиця':
                local = Cyrillic

        elif key == 'register':
            if value == 'великий':
                latin = upreglat
                Cyrillic = upregcyr
            elif value == "малий":
                latin = lowreglat
                Cyrillic = lowregcyr
            elif value == "обидва":
                both_reg = True

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
        #     url = re.compile(
        #     r'^[A-Za-z][A-Za-z0-9+.-]*://'  # схема (http, https, ftp…)
        #     r'([A-Za-z0-9._~%!$&\'()*+,;=-]+@)?'  # user:pass@
        #     r'([A-Za-z0-9._~%+-]+|\[[0-9a-fA-F:.]+\])'  # хост або IPv6
        #     r'(:[0-9]+)?'  # порт
        #     r'(/[A-Za-z0-9._~%!$&\'()*+,;=:@-]*)*'  # шлях
        #     r'(\?[A-Za-z0-9._~%!$&\'()*+,;=:@/?-]*)?'  # query
        #     r'(#[A-Za-z0-9._~%!$&\'()*+,;=:@/?-]*)?$'  # fragment
        # )

    # # собираем разрешённые символы
    # parts = []
    # if local:
    #     parts.append(local)
    # if spec_escaped:
    #     parts.append(spec_escaped)
    # if digits_str:
    #     parts.append(digits_str)
    # if is_probel:
    #     parts.append(r'^\s')
    # if email:
    #     parts.append(email)
    # if url:
    #     parts.append(url)

    # chars = "".join(parts) or "."  # если ничего не выбрано — разрешаем всё
    if email:
        # parts.append(email)
        # chars = r"A-Za-z0-9@._-"
        # chars = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        chars = "a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-."
    elif url:
        # parts.append(url)
        chars = "http?://[^\s/$.?#].[^\s"
        # chars = re.compile(
        #     r'^[A-Za-z][A-Za-z0-9+.-]*://'  # схема (http, https, ftp…)
        #     r'([A-Za-z0-9._~%!$&\'()*+,;=-]+@)?'  # user:pass@
        #     r'([A-Za-z0-9._~%+-]+|\[[0-9a-fA-F:.]+\])'  # хост або IPv6
        #     r'(:[0-9]+)?'  # порт
        #     r'(/[A-Za-z0-9._~%!$&\'()*+,;=:@-]*)*'  # шлях
        #     r'(\?[A-Za-z0-9._~%!$&\'()*+,;=:@/?-]*)?'  # query
        #     r'(#[A-Za-z0-9._~%!$&\'()*+,;=:@/?-]*)?$'  # fragment
        # )
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

    # финальный паттерн с учётом длины
    # pattern = f"{chars}*"
    pattern = "^["+f"{chars}"+"]+$"
    # print("✅ Готовый паттерн:", pattern)
    if fame == "login":
        lenminlog = len_min
        lenmaxlog = len_max
        patternlog = pattern
        both_reg_log = both_reg
        digits_str_log = digits_str
        spec_escaped_log = spec_escaped
    if fame == "login_l":
        lenminlog_l = len_min
        lenmaxlog_l = len_max
        patternlog_l = pattern
        both_reg_log_l = both_reg
        digits_str_log_l = digits_str
        spec_escaped_log_l = spec_escaped
    if fame == "password":
        lenminpas = len_min
        lenmaxpas = len_max
        patternpas = pattern
        both_reg_p = both_reg
        digits_str_p = digits_str
        spec_escaped_p = spec_escaped
    if fame == "email":
        # patterne = f"^["+f"{chars}"+"]+$"
        patterne = pattern
    if fame == "url":
        patternu = f"{chars}"+"]+$"
        # patternu = pattern
    return pattern


# глобальный root (невидимый, topmost)
_root = tk.Tk()
_root.withdraw()
_root.attributes("-topmost", True)


def show_error(parent, text: str):
    """Универсальная функция для вывода ошибки поверх всех окон"""
    messagebox.showerror("Помилка", text, parent=parent)


# --- проверки при вводе ---
def allow_login_value(new_value: str) -> bool:
    global chars, patternlog
    if not new_value:
        return True
    # если chars == ".", разрешаем всё
    if chars == ".":
        return True
    if email:
        patternlog = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$"
    # messagebox.showerror("Паттерн", str(bool(re.fullmatch(patternlog, new_value))), parent=_root)
    return bool(re.fullmatch(patternlog, new_value))

def allow_login_l_value(new_value: str) -> bool:
    global chars, patternlog_l
    if not new_value:
        return True
    # если chars == ".", разрешаем всё
    if chars == ".":
        return True
    # if email:
    #     patternlog = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$"
    # messagebox.showerror("Паттерн", str(bool(re.fullmatch(patternlog, new_value))), parent=_root)
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
    # return bool(re.fullmatch(r"(http?://[^\s/$.?#].[^\s]*)", new_value))
    return bool(re.fullmatch(patternu, new_value))


# --- проверки Email при вводе ---
def allow_email_value(new_value: str) -> bool:
    global patterne
    if not new_value:
        return True
    if chars == ".":
        return True
    # простой паттерн для "live" проверки: разрешаем буквы, цифры, @, ., -, _
    # pattern = r"[A-Za-z0-9@._\-]*"
    # pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$"
    return bool(re.fullmatch(patterne, new_value))


def validate_email_rules(email_t: str):
    if url:
        return "Помилка, Email не може форматуватись як URL адреса."
    if not email_t:
        return "Email не може бути порожнім."
    # RFC 5322 упрощённая проверка
    # pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$"
    if not re.fullmatch(patterne, email_t):
        return "Неправильний формат Email."
    return None


# --- проверки при OK ---
def validate_login_rules(log: str):
    global both_reg_log, digits_str_log, spec_escaped_log, lenminlog, lenmaxlog
    if not log:
        return "Логін не може бути порожнім."
    if len(log) < lenminlog or len(log) > lenmaxlog:
        return f"Логін має бути від {lenminlog} до {lenmaxlog} символів включно"
    if email:
        return None
    if both_reg_log:
        if not any(c.islower() for c in log):
            return "Логін має містити принаймні одну маленьку літеру."
        if not any(c.isupper() for c in log):
            return "Логін має містити принаймні одну велику літеру."
    if digits_str_log:
        if not any(c.isdigit() for c in log):
            return "Логін має містити принаймні одну цифру."
    if spec_escaped_log:
        if not any(c in string.punctuation for c in log):
            return "Логін має містити принаймні один спеціальний символ."
    return None

def validate_login_l_rules(log: str):
    global both_reg_log_l, digits_str_log_l, spec_escaped_log_l, lenminlog_l, lenmaxlog_l
    if not log:
        return "Прізвище не може бути порожнім."
    if len(log) < lenminlog_l or len(log) > lenmaxlog_l:
        return f"Прізвище має бути від {lenminlog_l} до {lenmaxlog_l} символів включно"
    if email or url:
        return "Помилка, Прізвище не може форматуватись як Email або URL адреса."
    if both_reg_log_l:
        if not any(c.islower() for c in log):
            return "Прізвище має містити принаймні одну маленьку літеру."
        if not any(c.isupper() for c in log):
            return "Прізвище має містити принаймні одну велику літеру."
    if digits_str_log_l:
        if not any(c.isdigit() for c in log):
            return "Прізвище має містити принаймні одну цифру."
    if spec_escaped_log_l:
        if not any(c in string.punctuation for c in log):
            return "Прізвище має містити принаймні один спеціальний символ."
    return None


def validate_password_rules(pw: str):
    global both_reg_p, digits_str_p, spec_escaped_p
    if email:
        # show_error(_root, "Помилка, Пароль не може форматуватись як Email адреса.")
        return "Помилка, Пароль не може форматуватись як Email адреса."
    if url:
        # show_error(_root, "Помилка, Пароль не може форматуватись як Email адреса.")
        return "Помилка, Пароль не може форматуватись як URL адреса."
    if not pw:
        return "Пароль не може бути порожнім."
    if len(pw) < lenminpas or len(pw) > lenmaxpas:
        return f"Пароль має бути від {lenminpas} до {lenmaxpas} символів включно"
    if both_reg_p:
        if not any(c.islower() for c in pw):
            return "Пароль має містити принаймні одну маленьку літеру."
        if not any(c.isupper() for c in pw):
            return "Пароль має містити принаймні одну велику літеру."
    if digits_str_p:
        if not any(c.isdigit() for c in pw):
            return "Пароль має містити принаймні одну цифру."
    if spec_escaped_p:
        if not any(c in string.punctuation for c in pw):
            return "Пароль має містити принаймні один спеціальний символ."
    return None


def validate_url_value(url: str):
    if not url:
        return "URL не може бути порожнім."
    if email:
        # show_error(_root, "Помилка, URL не може форматуватись як Email адреса.")
        return "Помилка, URL не може форматуватись як Email адреса."
    # allowed_pattern = re.compile(
    #     r'^[A-Za-z][A-Za-z0-9+.-]*://'
    #     r'([A-Za-z0-9\-._~%!$&\'()*+,;=]+@)?'
    #     r'([A-Za-z0-9\-._~%]+|\[[0-9a-fA-F:.]+\])'
    #     r'(:[0-9]+)?'
    #     r'(/[A-Za-z0-9\-._~%!$&\'()*+,;=:@]*)*'
    #     r'(\?[A-Za-z0-9\-._~%!$&\'()*+,;=:@/?]*)?'
    #     r'(#[A-Za-z0-9\-._~%!$&\'()*+,;=:@/?]*)?$'
    # )
    allowed_pattern = re.compile(
        r'^[A-Za-z][A-Za-z0-9+.-]*://'  # схема (http, https, ftp…)
        r'([A-Za-z0-9._~%!$&\'()*+,;=-]+@)?'  # user:pass@
        r'([A-Za-z0-9._~%+-]+|\[[0-9a-fA-F:.]+\])'  # хост або IPv6
        r'(:[0-9]+)?'  # порт
        r'(/[A-Za-z0-9._~%!$&\'()*+,;=:@-]*)*'  # шлях
        r'(\?[A-Za-z0-9._~%!$&\'()*+,;=:@/?-]*)?'  # query
        r'(#[A-Za-z0-9._~%!$&\'()*+,;=:@/?-]*)?$'  # fragment
    )
    # if not allowed_pattern.fullmatch(url):
    #     return "URL містить недопустимі символи або неправильний формат."
    # try:
    #     u = urlparse(url)
    #     if u.scheme not in ("http", "https") or not u.netloc:
    #         return "URL повинен починатися з http:// або https:// і містити домен."
    # except Exception:
    #     return "Неправильний формат URL."
    # pattern = r"(http?://[^\s/$.?#].[^\s]*)"
    if not re.fullmatch(allowed_pattern, url):
        return "Неправильний формат URL."
    return None

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

def fortest_list(file_test):
    test_names = []
    with open(file_test, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("def test_") and line.endswith(":"):
                # Витягаємо назву тесту без "def" та дужок
                name = line.split("(")[0].replace("def ", "").strip()
                test_names.append(name)
    return test_names

# https://www.qa-practice.com/
# https://en.wikipedia.org/wiki/Main_Page
# root = Tk()
_root.withdraw()  # ховаємо головне вікно

result = messagebox.askyesno("Вибір типу тестів", "Ви тестуватимете реєстрацію екаунту?")
# if result:
#     print("Обрано: Так")
# else:
#     print("Обрано: Ні")
# --- конфиг полей ---
if result:
    create_acc = True
    FIELDS_CONFIG = [
        {"label": "Адреса (URL):", "name": "url", "default": "", "allow_func": allow_url_value},
        {"label": "Ім'я:", "name": "login", "default": "", "allow_func": allow_login_l_value},
        {"label": "Прізвище:", "name": "login_l", "default": "", "allow_func": allow_login_l_value},
        {"label": "Пароль:", "name": "password", "default": "", "allow_func": allow_password_value},
        {"label": "Email:", "name": "email", "default": "", "allow_func": allow_email_value},
    ]
else:
    FIELDS_CONFIG = [
        {"label": "Адреса (URL):", "name": "url", "default": "", "allow_func": allow_url_value},
        {"label": "Логін:", "name": "login", "default": "", "allow_func": allow_login_value},
        {"label": "Пароль:", "name": "password", "default": "", "allow_func": allow_password_value},
        {"label": "Email:", "name": "email", "default": "", "allow_func": allow_email_value},
    ]

input_data = make_input_data("file_input_data.txt")
# list_of_tests = test_list("tests/test_main.py")
list_of_tests = fortest_list("tests/test_experiment.py")

class InputDialog(tk.Toplevel):
    def __init__(self, parent, input_url=None, input_login=None, input_login_l=None, input_password=None, input_email=None, name_of_test=""):
        super().__init__(parent)
        # self.login = None
        self.title("Введення даних у тест    "+name_of_test)
        self.attributes("-topmost", True)
        style = ttk.Style()
        style.configure("Error.TCombobox", fieldbackground="misty rose")
        style.configure("Ok.TCombobox", fieldbackground="white")
        self.cur_name = ""
        self.entries = {}
        self.required_vars = {}
        self.labels = {}

        # for row, field in enumerate(FIELDS_CONFIG):
        #     label_text = field["label"]
        #     name = field["name"]
        #     default = field["default"]
        #     allow_func = field["allow_func"]
        #
        #     tk.Label(self, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        #     self.labels[name] = label_text
        #
        #     entry = tk.Entry(self)
        #     entry.insert(0, default)
        #     entry.config(highlightthickness=1, highlightbackground="gray", highlightcolor="gray", state=tk.DISABLED)
        #
        #     if allow_func:
        #         vcmd = self._vcmd_factory(entry, allow_func)
        #         entry.config(validate="key", validatecommand=vcmd)
        #
        #     entry.grid(row=row, column=1, sticky="we", padx=5, pady=5)
        #     self.entries[name] = entry
        #     setattr(self, name, entry)
        for row, field in enumerate(FIELDS_CONFIG):
            label_text = field["label"]
            name = field["name"]
            default = field["default"]
            allow_func = field.get("allow_func")
            values = field.get("values", [])

            tk.Label(self, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            self.labels[name] = label_text

            # создаём комбинированный список
            combobox = ttk.Combobox(self, values=values)
            combobox.set(default)  # значение по умолчанию
            combobox.config(state="disabled")
            # combobox.config()

            if allow_func:
                # для Combobox валидация работает иначе, можно использовать bind("<<ComboboxSelected>>", ...)
                combobox.bind("<<ComboboxSelected>>", lambda e, func=allow_func: func(e.widget.get()))

            combobox.grid(row=row, column=1, sticky="we", padx=5, pady=5)
            self.entries[name] = combobox
            setattr(self, name, combobox)

            # биндим проверку на САМ combobox, а не на self.combobox
            combobox.bind("<<ComboboxSelected>>", lambda e, func=allow_func, w=combobox: self._validate_combo(w, func))
            combobox.bind("<FocusOut>", lambda e, func=allow_func, w=combobox: self._validate_combo(w, func))

            if name == 'url':
                # обновляем список вариантов
                self.entries['url'].config(values=input_url)
                # при желании можно установить значение по умолчанию
                if len(input_url) > 0:
                    self.entries['url'].set(input_url[0])
                # self.entries['url'].setFocus(False)
            if name == 'login':
                self.entries['login'].config(values=input_login)
                if len(input_login) > 0:
                    self.entries['login'].set(input_login[0])
            if name == 'login_l':
                self.entries['login_l'].config(values=input_login_l)
                if len(input_login_l) > 0:
                    self.entries['login_l'].set(input_login_l[0])
                # self.entries['login'].setFocus(False)
            if name == 'password':
                self.entries['password'].config(values=input_password)
                if len(input_password) > 0:
                    self.entries['password'].set(input_password[0])
                # self.entries['password'].setFocus(False)
            if name == 'email':
                self.entries['email'].config(values=input_email)
                if len(input_email) > 0:
                    self.entries['email'].set(input_email[0])
                # self.entries['email'].setFocus(False)

            # var = tk.BooleanVar(master=self, value=(name in ("login", "password")))
            var = tk.BooleanVar(master=self)
            self.required_vars[name] = var
            chk = tk.Checkbutton(self, text="Обов'язкове", variable=var,
                                 command=lambda name=name: self.on_toggle(name, var))
            chk.grid(row=row, column=2, sticky="w", padx=5, pady=5)
            # кнопка для виклику toggle_rule
            btn = tk.Button(self, text="Правила",
                            command=lambda n=name: self.toggle_rule(n))
            btn.grid(row=row, column=3, sticky="w", padx=5, pady=5)

        self.submit_button = tk.Button(self, text="OK", command=self.on_ok)
        # self.submit_button = tk.Button(self, text="OK", command=lambda n=self.cur_name: self.on_ok())
        self.submit_button.grid(row=len(FIELDS_CONFIG), column=0, padx=5, pady=10, sticky="we")

        self.cancel_button = tk.Button(self, text="Cancel", command=self.on_cancel)
        self.cancel_button.grid(row=len(FIELDS_CONFIG), column=1, padx=5, pady=10, sticky="we")

        self.columnconfigure(1, weight=1)
        self.result = None

        self.update_idletasks()
        self.center_window(600, self.winfo_reqheight() + 20)

        first_field = FIELDS_CONFIG[0]["name"]
        self.entries[first_field].focus_set()
        # # --- ВАЖНО: здесь добавляем логику "снять фокус" ---
        # for cb in self.entries.values():
        #     if isinstance(cb, ttk.Combobox):
        #         cb.configure(takefocus=0)  # запрещаем автофокус
        #
        # # сброс фокуса после отрисовки окна
        # self.after(100, lambda: self.focus_set())


    # def set_url(self, url_value):
    #     self.entries["url"].delete(0, tk.END)
    #     self.entries["url"].insert(0, url_value)

    def on_toggle(self, name, var):
        self.required_vars[name].get()


    def _set_err(self, widget):
        if isinstance(widget, ttk.Combobox):  # сначала проверяем Combobox
            style = ttk.Style()
            style.configure("Error.TCombobox", fieldbackground="misty rose")
            widget.configure(style="Error.TCombobox")
        elif isinstance(widget, tk.Entry):  # потом Entry
            widget.config(highlightthickness=2,
                          highlightbackground="red",
                          highlightcolor="red")

    def _set_ok(self, widget):
        if isinstance(widget, ttk.Combobox):
            style = ttk.Style()
            style.configure("Ok.TCombobox", fieldbackground="white")
            widget.configure(style="Ok.TCombobox")
        elif isinstance(widget, tk.Entry):
            widget.config(highlightthickness=1,
                          highlightbackground="gray",
                          highlightcolor="gray")


    def _validate_combo(self, widget, allow_func):
        value = widget.get().strip()

        if isinstance(widget, ttk.Combobox):  # это combobox
            if allow_func and allow_func(value):
                self._set_ok(widget)
            else:
                self._set_err(widget)

        elif isinstance(widget, tk.Entry):  # это entry
            if allow_func and allow_func(value):
                self._set_ok(widget)
            else:
                self._set_err(widget)

    def center_window(self, width, height):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    # відкриття форми з налаштуваннями тестів
    def toggle_rule(self, field_name):
        # messagebox.showerror("Имя элементу після вводу", f"Ім'я елементу  {field_name}", parent=self)
        self.cur_name = field_name
        # global patternl, patternpas, pattern, len_max, len_min, lenminlog, lenmaxlog, lenminpas, lenmaxpas
        # for en in self.entries.values():
        #     if en['state'] == tk.NORMAL:
        #         en.config(state=tk.DISABLED)
        # entry = self.entries[field_name]
        # entry.config(state=tk.NORMAL)
        # entry.focus_set()
        for widget in self.entries.values():
            if isinstance(widget, ttk.Combobox):
                widget.config(state="disabled")
            elif isinstance(widget, tk.Entry):
                widget.config(state=tk.DISABLED)

        entry = self.entries[field_name]
        if isinstance(entry, ttk.Combobox):
            entry.config(state="normal")  # включено
        elif isinstance(entry, tk.Entry):
            entry.config(state=tk.NORMAL)  # включено
        entry.focus_set()

        app = QApplication.instance()
        if not app:
            app = QApplication([])
        dlg = MyDialog()

        dlg.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        dlg.setModal(True)
        if dlg.exec() == QDialog.Accepted:  # ← проверка, нажата ли OK
            cur_rules = dlg.result  # ← берём результат после закрытия
            entries_rules(field_name, entries=cur_rules)

    def on_ok(self):
        # messagebox.showerror("Имя элементу при закритті форми", f"Ім'я елементу  {self.cur_name}", parent=self)
        empty_fields = []
        missing = []

        for name_m, widget in self.entries.items():
            value = widget.get().strip()

            if self.required_vars[name_m].get():
                if value == "":
                    missing.append(name_m)
                    self._set_err(widget)  # подсветим красным
                else:
                    self._set_ok(widget)  # подсветим серым (валидное поле)
            else:
                # необязательное поле: если есть значение → серое, иначе оставляем как есть
                if value != "":
                    self._set_ok(widget)

            if value == "":
                empty_fields.append(name_m)

        if missing:
            messagebox.showerror(
                "Помилка",
                "Будь ласка, заповніть обов'язкові поля:\n" +
                "\n".join(self.labels[n] for n in missing),
                parent=self
            )
            return
        # messagebox.showerror("Шаблон", f"Склад шаблонуу  {pattern}", parent=self)
        login_val = self.login.get()
        # задані вимоги для поля, поле обов'язкове або не пусте
        if self.cur_name == "login" and self.required_vars[self.cur_name].get() and login_val != "":
            if email: #and self.entries["email"].get() == "":
                errlog = validate_email_rules(login_val)
            else:
                errlog = validate_login_rules(login_val)
            if not allow_login_value(login_val) or errlog:
                self._set_err(self.login)
                messagebox.showerror("Помилка", errlog or "Логін містить недопустимі символи.", parent=self)
                self.entries['login'].set('')
                self.login.focus_set()
                return
            self._set_ok(self.login)

        if create_acc:
            login_l_val = self.login_l.get()
        # задані вимоги для поля, поле обов'язкове або не пусте
        if self.cur_name == "login_l" and self.required_vars[self.cur_name].get() and login_l_val != "":
            errlog_l = validate_login_l_rules(login_l_val)
            if not allow_login_l_value(login_l_val) or errlog_l:
                self._set_err(self.login_l)
                messagebox.showerror("Помилка", errlog_l or "Прізвище містить недопустимі символи.", parent=self)
                self.entries['login_l'].set('')
                self.login_l.focus_set()
                return
            self._set_ok(self.login_l)

        pw = self.password.get()
        if self.cur_name == "password" and self.required_vars[self.cur_name].get() and pw != "":
            errp = validate_password_rules(pw)
            if not allow_password_value(pw) or errp:
                self._set_err(self.password)
                messagebox.showerror("Помилка", errp or "Пароль містить недопустимі символи.", parent=self)
                # self.entries['password'].delete(0, tk.END)
                self.entries['password'].set('')
                self.password.focus_set()
                return
            self._set_ok(self.password)

        url_val = self.url.get()
        # задані вимоги для поля, поле обов'язкове або не пусте
        if self.cur_name == "url" and self.required_vars[self.cur_name].get() and url_val != "":
            erru = validate_url_value(url_val)
            if erru:
                self._set_err(self.url)
                messagebox.showerror("Помилка", erru, parent=self)
                self.entries['url'].set('')
                self.url.focus_set()
                return
            self._set_ok(self.url)

        # проверка Email
        email_val = self.email.get()
        if self.cur_name == "email" and self.required_vars[self.cur_name].get() and email_val != "":
            erre = validate_email_rules(email_val)
            if not allow_email_value(email_val) or erre:
                self._set_err(self.email)
                messagebox.showerror("Помилка", erre or "Email містить недопустимі символи.", parent=self)
                self.entries['email'].set('')
                self.email.focus_set()
                return
            self._set_ok(self.email)
        if not create_acc:
            login_l_val = ""
        self.result = {"login": login_val, "login_l": login_l_val, "password": pw, "url": url_val, "email": email_val}
        self.destroy()

    def on_cancel(self):
        self.result = None
        try:
            self.destroy()
        finally:
            os._exit(0)  # немедленно завершает процесс


# --- вызов диалога ---
def get_user_input():
    # debug("Создаём форму Tkinter...", "INFO")
    global number_of_test
    # root = tk.Tk()
    # root.withdraw()
    # Пример простой формы через askstring
    # url = simpledialog.askstring("Ввод URL", "Введите URL:", parent=root)
    # debug("Открываем форму InputDialog", "INFO")
    if create_acc:
        # dlg = InputDialog(_root, input_url=input_data['url'], input_login=input_data['login'], input_login_l=input_data['login_l'], input_password=input_data['password'], input_email=input_data['email'], name_of_test=list_of_tests[number_of_test])
        dlg = InputDialog(_root, input_url=input_data['url'], input_login=input_data['login'],
                          input_login_l=input_data['login_l'], input_password=input_data['password'],
                          input_email=input_data['email'], name_of_test="test_first_name_field_visible")
    else:
        dlg = InputDialog(_root, input_url=input_data['url'], input_login=input_data['login'], input_password=input_data['password'], input_email=input_data['email'], name_of_test=list_of_tests[number_of_test])
    dlg.grab_set()
    _root.wait_window(dlg)

    # debug(f"Початок тесту {list_of_tests[number_of_test]} зі сторінки з адресою : {input_data['url'][number_of_test]}", "INFO")
    debug(f"Початок тесту test_first_name_field_visible зі сторінки з адресою : {dlg.result['url']}", "INFO")
    number_of_test += 1
    return dlg.result
