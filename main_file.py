import tkinter as tk
from tkinter import messagebox
import re
import string
# from urllib.parse import urlparse
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt
from pyside_dialog import MyDialog  # твоя PySide форма
import os
# from tkinter import simpledialog
# from helper import debug
# _root = None  # глобальная ссылка на root


email = False
url = False
len_min = 4
len_max = 16
lenminlog = 4
lenmaxlog = 16
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
pattern = ""
patterne = ""
patternu = ""
patternlog: str = ""
patternpas: str = ""
chars = ""
both_reg_log = False
digits_str_log = ""
spec_escaped_log = ""
both_reg_p = False
digits_str_p = ""
spec_escaped_p = ""


def entries_rules(fame, **kwargs):
    global pattern, chars, len_min, len_max, latin, Cyrillic, spec_escaped, is_probel, email, url, both_reg, patternlog, patternpas, lenminpas, lenmaxpas, lenminlog, lenmaxlog, spec, digits_str, patterne, patternu

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
                spec = "-!@#$%^&*()_=+[]{};:,.<>/?\\|"
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

    # собираем разрешённые символы
    parts = []
    if local:
        parts.append(local)
    if spec_escaped:
        parts.append(spec_escaped)
    if digits_str:
        parts.append(digits_str)
    if is_probel:
        parts.append(r'^\s')
    # if email:
    #     parts.append(email)
    # if url:
    #     parts.append(url)

    chars = "".join(parts) or "."  # если ничего не выбрано — разрешаем всё
    if email:
        # parts.append(email)
        # chars = r"A-Za-z0-9@._-"
        chars = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if url:
        # parts.append(url)
        chars = r"(http?://[^\s/$.?#].[^\s])"
        # chars = re.compile(
        #     r'^[A-Za-z][A-Za-z0-9+.-]*://'  # схема (http, https, ftp…)
        #     r'([A-Za-z0-9._~%!$&\'()*+,;=-]+@)?'  # user:pass@
        #     r'([A-Za-z0-9._~%+-]+|\[[0-9a-fA-F:.]+\])'  # хост або IPv6
        #     r'(:[0-9]+)?'  # порт
        #     r'(/[A-Za-z0-9._~%!$&\'()*+,;=:@-]*)*'  # шлях
        #     r'(\?[A-Za-z0-9._~%!$&\'()*+,;=:@/?-]*)?'  # query
        #     r'(#[A-Za-z0-9._~%!$&\'()*+,;=:@/?-]*)?$'  # fragment
        # )
    # финальный паттерн с учётом длины
    pattern = r"[{chars}]*"
    # print("✅ Готовый паттерн:", pattern)
    if fame == "login":
        # if not email:
        #     patternlog = pattern
        # else:
        lenminlog = len_min
        lenmaxlog = len_max
        patternlog = pattern
        both_reg_log = both_reg
        digits_str_log = digits_str
        spec_escaped_log = spec_escaped
    if fame == "password":
        lenminpas = len_min
        lenmaxpas = len_max
        patternpas = pattern
        both_reg_p = both_reg
        digits_str_p = digits_str
        spec_escaped_p = spec_escaped
    if fame == "email":
        patterne = pattern
    if fame == "url":
        patternu = pattern
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
        patternlog = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$)"
    return bool(re.fullmatch(patternlog, new_value))


def allow_password_value(new_value: str) -> bool:
    global pattern, chars, patternpas
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
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$)"
    return bool(re.fullmatch(pattern, new_value))


def validate_email_rules(email_t: str):
    if url:
        return "Помилка, Email не може форматуватись як URL адреса."
    if not email_t:
        return "Email не може бути порожнім."
    # RFC 5322 упрощённая проверка
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$)"
    if not re.fullmatch(pattern, email_t):
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

def test_list(file_test):
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
# --- конфиг полей ---
FIELDS_CONFIG = [
    {"label": "Адреса (URL):", "name": "url", "default": "",
         "allow_func": allow_url_value},
    {"label": "Логін:", "name": "login", "default": "", "allow_func": allow_login_value},
    {"label": "Пароль:", "name": "password", "default": "", "allow_func": allow_password_value},
    {"label": "Email:", "name": "email", "default": "", "allow_func": allow_email_value},
]


class InputDialog(tk.Toplevel):
    def __init__(self, parent, init_url=None):
        super().__init__(parent)
        self.title("Введення тестових даних")
        self.attributes("-topmost", True)

        self.entries = {}
        self.required_vars = {}
        self.labels = {}

        for row, field in enumerate(FIELDS_CONFIG):
            label_text = field["label"]
            name = field["name"]
            default = field["default"]
            allow_func = field["allow_func"]

            tk.Label(self, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            self.labels[name] = label_text

            entry = tk.Entry(self)
            # if name == 'url':
            #     entry.insert(0, init_url)
            # else:
            entry.insert(0, default)
            entry.config(highlightthickness=1, highlightbackground="gray", highlightcolor="gray", state=tk.DISABLED)

            if allow_func:
                vcmd = self._vcmd_factory(entry, allow_func)
                entry.config(validate="key", validatecommand=vcmd)

            entry.grid(row=row, column=1, sticky="we", padx=5, pady=5)
            self.entries[name] = entry
            setattr(self, name, entry)

            var = tk.BooleanVar(master=self, value=(name in ("login", "password")))
            self.required_vars[name] = var
            chk = tk.Checkbutton(self, text="Обов'язкове", variable=var,
                                 command=lambda name=name: self.on_toggle(name))
            chk.grid(row=row, column=2, sticky="w", padx=5, pady=5)
            # кнопка для виклику toggle_rule
            btn = tk.Button(self, text="Правила",
                            command=lambda n=name: self.toggle_rule(n))
            btn.grid(row=row, column=3, sticky="w", padx=5, pady=5)

        self.submit_button = tk.Button(self, text="OK", command=self.on_ok)
        self.submit_button.grid(row=len(FIELDS_CONFIG), column=0, padx=5, pady=10, sticky="we")

        self.cancel_button = tk.Button(self, text="Cancel", command=self.on_cancel)
        self.cancel_button.grid(row=len(FIELDS_CONFIG), column=1, padx=5, pady=10, sticky="we")

        self.columnconfigure(1, weight=1)
        self.result = None

        self.update_idletasks()
        self.center_window(600, self.winfo_reqheight() + 20)

        first_field = FIELDS_CONFIG[0]["name"]
        self.entries[first_field].focus_set()


    def set_url(self, url_value):
        self.entries["url"].delete(0, tk.END)
        self.entries["url"].insert(0, url_value)

    def on_toggle(self, name):
        val = self.required_vars[name].get()

    # --- validatecommand factory ---
    def _vcmd_factory(self, entry, allow_func):
        def _vcmd(new_value):
            if allow_func(new_value):
                entry.config(highlightthickness=1, highlightbackground="gray", highlightcolor="gray")
            else:
                entry.config(highlightthickness=2, highlightbackground="red", highlightcolor="red")
            return True

        return (self.register(_vcmd), "%P")

    def _set_err(self, entry):
        entry.config(highlightthickness=2, highlightbackground="red", highlightcolor="red")

    def _set_ok(self, entry):
        entry.config(highlightthickness=1, highlightbackground="gray", highlightcolor="gray")

    def center_window(self, width, height):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    # відкриття форми з налаштуваннями тестів
    def toggle_rule(self, field_name):
        global patternl, patternpas, pattern
        for en in self.entries.values():
            if en['state'] == tk.NORMAL:
                en.config(state=tk.DISABLED)
        entry = self.entries[field_name]
        entry.config(state=tk.NORMAL)
        entry.focus_set()
        global len_max, len_min, lenminlog, lenmaxlog, lenminpas, lenmaxpas
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
        empty_fields = [name for name, entry in self.entries.items() if not entry.get().strip()]
        # if not "email" in empty_fields:
        #     empty_email = False
        missing = [name for name, var in self.required_vars.items() if var.get() and self.entries[name].get() == ""]
        for name in missing:
            if not self.entries[name].get():
                self._set_err(self.entries[name])
        if missing:
            messagebox.showerror("Помилка", "Будь ласка, заповніть обов'язкові поля:\n" +
                                 "\n".join(self.labels[n] for n in missing), parent=self)
            return

        login_val = self.login.get()
        if "login" in self.required_vars and login_val != "":
            if email and self.entries["email"].get() == "":
                # if "email" in self.required_vars and login_val != "":
                errlog = validate_email_rules(login_val)
            else:
                errlog = validate_login_rules(login_val)
            if not allow_login_value(login_val) or errlog:
                self._set_err(self.login)
                messagebox.showerror("Помилка", errlog or "Логін містить недопустимі символи.", parent=self)
                self.login.focus_set()
                return
            self._set_ok(self.login)

        pw = self.password.get()
        if "password" in self.required_vars and pw != "":
            errp = validate_password_rules(pw)
            if not allow_password_value(pw) or errp:
                self._set_err(self.password)
                messagebox.showerror("Помилка", errp or "Пароль містить недопустимі символи.", parent=self)
                self.password.focus_set()
                return
            self._set_ok(self.password)

        url_val = self.url.get()
        if "url" in self.required_vars and url_val != "":
            erru = validate_url_value(url_val)
            if erru:
                self._set_err(self.url)
                messagebox.showerror("Помилка", erru, parent=self)
                self.url.focus_set()
                return
            self._set_ok(self.url)

        # проверка Email
        email_val = self.email.get()
        if "email" in self.required_vars and email_val != "":
            erre = validate_email_rules(email_val)
            if not allow_email_value(email_val) or erre:
                self._set_err(self.email)
                messagebox.showerror("Помилка", erre or "Email містить недопустимі символи.", parent=self)
                self.email.focus_set()
                return
            self._set_ok(self.email)

        self.result = {"login": login_val, "password": pw, "url": url_val, "email": email_val}
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
    root = tk.Tk()
    root.withdraw()
    # Пример простой формы через askstring
    # url = simpledialog.askstring("Ввод URL", "Введите URL:", parent=root)
    # debug("Открываем форму InputDialog", "INFO")
    dlg = InputDialog(root, url)
    dlg.grab_set()
    root.wait_window(dlg)
    # debug(f"Форма закрыта, результат: {dlg.result}", "INFO")
    return dlg.result

