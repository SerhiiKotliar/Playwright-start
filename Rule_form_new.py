
from PySide6.QtWidgets import (
    QApplication, QDialog)
import allure
from Config_dialog import ConfigInputDialog
from form_filling_fields import DynamicDialog
from mycombo import WhichBinding
import sys
from datetime import datetime
import os
import pytest



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

# def diff_char(bigger: str, smaller: str) -> str:
#     # ищем первую позицию, где строки расходятся
#     for i, (c1, c2) in enumerate(zip(bigger, smaller)):
#         if c1 != c2:
#             return c1  # символ из "большей" строки
#     # если отличий не нашли, то "лишний" символ — в конце
#     return bigger[len(smaller)]


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
