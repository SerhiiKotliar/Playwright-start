import allure

def debug(value, description="DEBUG"):
    """
    Универсальный вывод для отладки:
    - печатает в консоль
    - прикрепляет в Allure-отчёт
    """
    # Вывод в консоль
    print(f"[{description}] {value}")

    # Вывод в Allure
    try:
        allure.attach(
            str(value),
            name=description,
            attachment_type=allure.attachment_type.TEXT
        )
    except Exception:
        # если Allure не подключён — просто пропускаем
        pass
