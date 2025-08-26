import allure
from datetime import datetime
# from main_file import test_list
# def debug(value, description="DEBUG"):
#     """
#     Универсальный вывод для отладки:
#     - печатает в консоль
#     - прикрепляет в Allure-отчёт
#     """
#     # Вывод в консоль
#     print(f"[{description}] {value}")
#
#     # Вывод в Allure
#     try:
#         allure.attach(
#             str(value),
#             name=description,
#             attachment_type=allure.attachment_type.TEXT
#         )
#     except Exception:
#         # если Allure не подключён — просто пропускаем
#         pass

def debug(value, description="DEBUG"):
    """
    Вывод сообщения для отладки с таймштампом:
    - печать в консоль
    - добавление в Allure-отчёт
    """
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Часы:Минуты:Секунды.мс
    message = f"[{timestamp}] [{description}] {value}"

    # Консоль
    print(message)

    # Allure
    try:
        allure.attach(
            message,
            name=description,
            attachment_type=allure.attachment_type.TEXT
        )
    except Exception:
        pass


# if __name__ == "__main__":
#     list_test = test_list("test_main.py")
#     print(list_test)
