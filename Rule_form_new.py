
from PySide6.QtWidgets import (
    QApplication, QDialog, QMessageBox, QFileDialog, QWidget, QPushButton, QVBoxLayout)
from PySide6.QtCore import Qt
import allure
from Config_dialog import ConfigInputDialog
from form_filling_fields import DynamicDialog
from mycombo import WhichBinding
import sys
from datetime import datetime
import os
import pytest
import json



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


def make_defaul_data(file_name):
    # Словарь для хранения данных
    data = {
        "home_page": [],
        "count_fields": [],
        "titles_fields": [],
        "names_fields": [],
        "attr_err": [],
        "html_el_t": [],
        "txt_el_t": []
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




def get_user_input():
    global number_of_test
    app = QApplication.instance()
    created_app = False
    if app is None:
        app = QApplication(sys.argv)
        created_app = True
    # reply = QMessageBox.question(
    #     None,
    #     "КОНФІГУРАЦІЯ",
    #     "СТВОРИТИ?",
    #     QMessageBox.Yes | QMessageBox.No,
    #     defaultButton=QMessageBox.No
    # )
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("КОНФІГУРАЦІЯ")
    msg.setText("СТВОРИТИ?")
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)
    msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)  # 👈 делает окно поверх всех
    reply = msg.exec()
    if reply == QMessageBox.Yes:
        file_name, _ = QFileDialog.getOpenFileName(
            None,
            "Відкрити конфігурацію",
            os.getcwd(),  # текущая директория
            "JSON files (*.json);;All files (*)"
        )

        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                QMessageBox.information(None, "Успіх", f"Файл успішно завантажено:\n{file_name}")
                print(config_data)
            except Exception as e:
                QMessageBox.critical(None, "Помилка", f"Не вдалося відкрити файл:\n{e}")
        else:
            QMessageBox.information(None, "Скасовано", "Вибір файлу скасовано")
    # Проверяем, есть ли QApplication
    # app = QApplication.instance()
    # created_app = False
    # if app is None:
    #     app = QApplication(sys.argv)
    #     created_app = True
    input_dlg = ConfigInputDialog()

    # Заполняем отдельные поля
    # input_dlg.attr_input.setText('//*[@id="error_1_id_text_string"]')
    input_dlg.html_input.setText(config_data['HTML_element'])
    input_dlg.text_input.setText(config_data['HTML_text'])
    input_dlg.radio_button.setChecked(config_data['fix_button']) #фіксація ввеедення кнопкою
    input_dlg.radio_event.setChecked(config_data['fix_event']) #фіксація введення по події виходу з поля
    input_dlg.radio_enter.setChecked(config_data['fix_enter']) #фіксація введення клавішею Enter
    input_dlg.attr_input.setText(config_data['attribut_error'])
    input_dlg.spin.setValue(config_data['count_fields'])  # Устанавливаем начальное значение

    # Теперь можно заполнять каждое поле напрямую через виджеты
    # titles = ['URL of page', 'Користувач', 'Пароль']
    # names = ['url_of_page', 'Username', 'Password']
    titles = []
    names = []
    titles = config_data['titles']
    names = config_data['names']
    requireds = config_data['required']
    i = 0
    n = len(input_dlg.current_widgets)
    for title_edit, name_edit, checkbox in input_dlg.current_widgets:
        title_edit.setText(titles[i])
        name_edit.setText(names[i])
        checkbox.setChecked(requireds[i])
        i += 1

    # Запускаем диалог конфигурации
    if input_dlg.exec() != QDialog.Accepted:
        return None

    config = input_dlg.get_config()

    dlg = DynamicDialog(config, input_url=input_data['url'], input_login=input_data['login'],
                      input_login_l=input_data['login_l'], input_password=input_data['password'],
                      input_email=input_data['email'], name_of_test="")
    # запускаємо діалог введення даних у поля
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
