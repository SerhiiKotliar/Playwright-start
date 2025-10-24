import allure
from datetime import datetime

def get_extension(filename: str) -> str:
    """
    Возвращает часть строки после последней точки.
    Если точки нет — возвращает пустую строку.
    """
    parts = filename[-9:].rsplit('.', 1)
    return parts[1] if len(parts) > 1 else ''


def debug(value, description="DEBUG", att=None):
    """
    Вывод сообщения для отладки с таймштампом:
    - печать в консоль
    - добавление в Allure-отчёт
    """
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Часы:Минуты:Секунды.мс
    message = f"[{timestamp}] [{description}] {value}"

    # Консоль
    print(message)
    # тип вложения
    type_txt = get_extension(message).upper()
    if type_txt != '':
        attach_txt =f"allure.attachment_type.{type_txt}"
        allure.attach(
            att,
            name=message,
            attachment_type=attach_txt
        )
    else:
        allure.attach(
            message,
            name=description
        )
    # # Allure
    # try:
    #     allure.attach(
    #         message,
    #         name=description,
    #         attachment_type=attach_txt
    #     )
    # except Exception:
    #     pass


# if __name__ == "__main__":
#     list_test = test_list("tests\test_main.py")
#     print(list_test)
