import allure
import pytest
from playwright.sync_api import expect
from helper import debug

# Данные для теста
valid_inputs = ["Alice", "Bob", "JohnDoe"]
invalid_inputs = ["Invalid@Name", "123#Name", ""]

# Параметризация: (scenario, input_value, expected_result, expect_successful_input)
test_cases = []

# Позитивные данные для видимого поля
for val in valid_inputs:
    test_cases.append(("visible", val, "PASS", True))

# Негативные данные для видимого поля
for val in invalid_inputs:
    test_cases.append(("visible", val, "FAIL", False))

# Негативные сценарии: поле отсутствует или скрыто
for val in valid_inputs + invalid_inputs:
    test_cases.append(("absent", val, "FAIL", False))
    test_cases.append(("hidden", val, "FAIL", False))

@pytest.mark.parametrize("scenario, input_value, expected_result, expect_successful_input", test_cases)
def test_first_name_field(page_open, scenario, input_value, expected_result, expect_successful_input):
    locator = page_open.get_by_role("textbox", name="First Name*")

    try:
        if scenario == "visible":
            with allure.step('перехід на посилання створення екаунту та клік на ньому'):
                # page.goto("https://magento.softwaretestingboard.com/")
                # Перевірка наявності по тексту
                # expect(page_open.get_by_text("Create an Account")).to_be_visible(timeout=30000)
                expect(page_open.get_by_role("link", name="Create an Account")).to_be_visible(timeout=40000)
                debug("перехід на посилання створення екаунту", "Посилання створення екаунту")
                # page_open.get_by_text("Create an Account").click()
                page_open.get_by_role("link", name="Create an Account").click()
                # page_open.get_by_text("Create New Customer Account").click()
                debug("клік на посиланні створення екаунту", "Посилання створення екаунту")
            with allure.step('перевірка заголовку, чи це сторінка створення екаунту'):
                expect(page_open.get_by_role("heading")).to_contain_text("Create New Customer Account", timeout=40000)
                debug("здійснено перехід на сторінку створення екаунту", "Сторінка створення екаунту")
            allure.dynamic.title(f"Тест: поле 'First Name*' видно, ввод: '{input_value}'")
            with allure.step(f"Ввод данных '{input_value}' в поле"):
                expect(locator).to_be_visible()
                locator.fill(input_value)
                if expect_successful_input:
                    expect(locator).to_have_value(input_value)
                else:
                    expect(locator).not_to_have_value(input_value)

        elif scenario == "absent":
            allure.dynamic.title(f"Тест: поле 'First Name*' отсутствует, ввод: '{input_value}'")
            with allure.step("Проверка отсутствия поля в DOM"):
                expect(locator).to_have_count(0)
                assert locator.count() == 0, "Поле не должно существовать"

        elif scenario == "hidden":
            allure.dynamic.title(f"Тест: поле 'First Name*' скрыто, ввод: '{input_value}'")
            with allure.step("Проверка, что поле скрыто"):
                expect(locator).to_be_hidden()
                locator.fill(input_value)
                expect(locator).not_to_have_value(input_value)

        actual_result = "PASS"

    except Exception as e:
        actual_result = "FAIL"
        debug(f"Ошибка в сценарии '{scenario}' с данными '{input_value}': {e}", "ERROR")

        # Скриншот страницы
        screenshot = page_open.screenshot()
        allure.attach(
            screenshot,
            name=f"Скриншот при ошибке ({scenario})",
            attachment_type=allure.attachment_type.PNG
        )

        # HTML страницы
        html_content = page_open.content()
        allure.attach(
            html_content,
            name=f"HTML при ошибке ({scenario})",
            attachment_type=allure.attachment_type.HTML
        )

        raise

    finally:
        # Лог в Allure
        allure.attach(str(expected_result), "Ожидаемый результат")
        allure.attach(str(actual_result), "Фактический результат")
        allure.attach(str(expect_successful_input), "Ожидаемое поведение поля")

        # Проверка соответствия
        assert actual_result == expected_result, (
            f"Сценарий '{scenario}' с данными '{input_value}': ожидался результат {expected_result}, "
            f"но получили {actual_result}"
        )

# ####################################################################################################################
# Отличный вопрос! Давай разберём, как работают эти переменные и какие значения они могут принимать в нашем тесте:
#
# ---
#
# ### 1️⃣ `expected_result`
#
# * Это **ожидаемый результат выполнения теста** с точки зрения pytest.
# * Присваивается **в параметризации** при создании тест-кейсов.
# * Возможные значения:
#
#   * `"PASS"` → мы ожидаем, что тест пройдет успешно (например, корректное поле и корректные данные).
#   * `"FAIL"` → мы ожидаем, что тест упадет (например, поле отсутствует, скрыто или данные некорректные).
#
# **Пример:**
#
# ```python
# test_cases = [
#     ("visible", "Alice", "PASS", True),      # поле видно, данные корректные → тест должен пройти
#     ("visible", "Invalid@Name", "FAIL", False),  # поле видно, данные некорректные → тест должен упасть
#     ("absent", "AnyName", "FAIL", False),    # поле отсутствует → тест должен упасть
# ]
# ```
#
# ---
#
# ### 2️⃣ `expect_successful_input`
#
# * Это **логическое значение**, отражающее, ожидаем ли мы, что данные **будут введены успешно** в поле.
# * Присваивается также при параметризации вместе с `expected_result`.
# * Типичные значения:
#
#   * `True` → данные должны быть успешно введены в поле (позитивный кейс).
#   * `False` → данные **не должны быть введены** (негативный кейс: поле скрыто, отсутствует или данные некорректные).
#
# **Пример:**
#
# ```python
# ("visible", "Alice", "PASS", True)       # данные должны пройти
# ("visible", "Invalid@Name", "FAIL", False)  # данные не должны пройти
# ("hidden", "John", "FAIL", False)        # поле скрыто → данные не проходят
# ```
#
# ---
#
# ### 3️⃣ `actual_result`
#
# * Это **фактический результат выполнения теста**.
# * Присваивается внутри `try/except`:
#
#   * Если тест прошёл без ошибок → `"PASS"`.
#   * Если тест упал, поймана ошибка → `"FAIL"`.
# * Сравнивается с `expected_result` в `assert` в блоке `finally`.
#
# **Пример присвоения:**
#
# ```python
# try:
#     # действия с полем
#     actual_result = "PASS"  # если все проверки прошли
# except Exception:
#     actual_result = "FAIL"  # если что-то пошло не так
# ```
#
# ---
#
# ### 🔹 Таблица для примера
#
# | scenario | input\_value    | expected\_result | expect\_successful\_input | actual\_result |
# | -------- | --------------- | ---------------- | ------------------------- | -------------- |
# | visible  | "Alice"         | PASS             | True                      | PASS           |
# | visible  | "Invalid\@Name" | FAIL             | False                     | FAIL           |
# | absent   | "AnyName"       | FAIL             | False                     | FAIL           |
# | hidden   | "John"          | FAIL             | False                     | FAIL           |
#
# ---
# сделай ещё расширение, где при негативных данных тест будет проверять сообщение об ошибке формы (например, валидатор не пропускает некорректные символы) и это тоже будет в Allure.
#
