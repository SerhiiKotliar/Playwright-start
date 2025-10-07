import traceback

import allure
import pytest
from playwright.sync_api import expect, Page
from Rule_form_new import report_about, report_bug_and_stop
from helper import debug
import re
from typing import Callable, Pattern, Union, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import invalid_datas as in_d
from datetime import datetime

now = datetime.now()
fields = []
valid_values = []
invalid_values = {}

URLMatcher = Union[str, Pattern[str], Callable[[str], bool]]

def click_and_wait_url_change(
    page: Page,
    do_click: Callable[[], None],
    url: Optional[URLMatcher] = None,          # шаблон/regex/предикат или None = "любой новый URL"
    *,
    timeout: float = 5000,
    wait_until: str = "commit"                 # "commit" надёжно ловит смену URL без полной загрузки
) -> tuple[bool, str]:
    old = page.url
    # Если шаблон не задан — ждём любой URL, отличный от старого
    matcher: URLMatcher = (lambda u: u != old) if url is None else url

    do_click()
    try:
        page.wait_for_url(matcher, timeout=timeout, wait_until=wait_until)
        return (page.url != old, page.url)
    except PlaywrightTimeoutError:
        return (False, page.url)


def fail_on_alert(
    page: Page,
    type_: str = "error",
    timeout: int = 2000
) -> None:
    """
    Проверяет наличие алерта указанного типа и падает тестом, если он найден.

    :param page: объект Playwright Page
    :param type_: тип сообщения (error, success, warning, info)
    :param timeout: сколько ждать появления (мс)
    """
    # Словарь возможных селекторов (дополняй под свой проект)
    selectors = {
        "error": ".alert-danger, .notification.error, .toast-error",
        "success": ".alert-success, .notification.success, .toast-success",
        "warning": ".alert-warning, .notification.warning, .toast-warning",
        "info": ".alert-info, .notification.info, .toast-info",
    }

    selector = selectors.get(type_)
    if not selector:
        debug(f"{type_}", f"Невідомий тип алерта")
        raise ValueError(f"Невідомий тип алерта: {type_}")


    try:
        # ждём появления элемента
        el = page.wait_for_selector(selector, timeout=timeout)
        pytest.fail(f"❌ З'явилось повідомлення типу '{type_}': {el.inner_text()}")
        debug(f"{el.inner_text()}", f"❌ З'явилось повідомлення типу '{type_}'")
    except TimeoutError:
        # если не появилось — всё хорошо
        pass

# список валидных данных
def valid_val(user_data):
    global fields
    fields = user_data[0].keys()
    val_el = []
    # збір значень полів по іменам полів
    for val in user_data[0].values():
        val_el.append(val)
    return val_el
# список невалидных данных по полям
def invalid_val(user_data):
    global fields
    inval_el = {}
    # перебір по назвам полів
    for field in fields:
        ar_inv = []
        # перебір по назвам полів для розбору типу невалідних даних зі списків
        for el in user_data[1][field]:
            if el[:3] == 'len':
                lminmax = el[4:]
                lmin = int(lminmax.split(" ", 1)[0])
                lmax = int(lminmax.split(" ", 1)[1])
                first = ((user_data[0][field] * 6)[:(lmin - 2)], "lenmin")
                second = ((user_data[0][field] * 6)[:(lmax + 2)], "lenmax")
                ar_inv.append(first)
                ar_inv.append(second)
            elif el == "absent":
                ar_inv.append(("", "absent"))
            elif el == "no_url":
                for el_no_url in in_d.invalid_urls:
                    ar_inv.append((el_no_url, "no_url"))
            elif el == "no_email":
                for el_no_email in in_d.invalid_emails:
                    ar_inv.append((el_no_email, "no_email"))
            elif el == "no_lower":
                ar_inv.append((user_data[0][field].upper(), "no_lower"))
            elif el == "no_upper":
                ar_inv.append((user_data[0][field].lower(), "no_upper"))
            elif el == "no_digit":
                res = re.sub(r"\d", "", user_data[0][field])
                ar_inv.append((res + 'ab', "no_digit"))
            elif el == "no_spec":
                res = "".join(ch for ch in user_data[0][field] if ch.isalnum() or ch.isspace())
                ar_inv.append((res + '1f', "no_spec"))
            elif el == "probel":
                ar_inv.append((user_data[0][field][:2] + ' ' + user_data[0][field][2:], "probel"))
            elif el == "no_probel":
                ar_inv.append((user_data[0][field].replace(" ", ""), "no_probel"))
            elif el == "Cyrillic":
                ar_inv.append(("АЯаяЁёЇїІіЄєҐґ", "Cyrillic"))
            elif el == "latin":
                ar_inv.append(("AaZzEeYyUuIiOoPpFfDdGgHhJjKkLlQqWwRrTtSsCcVvBbNnMmXx", "latin"))
            elif el == "lowreglat":
                ar_inv.append(("qwertyuiop", "lowreglat"))
            elif el == "upreglat":
                ar_inv.append(("QWERTYUIOP", "upreglat"))
            elif el == "lowregcyr":
                ar_inv.append(("йцукенгшщзхъїієёґ", "lowregcyr"))
            elif el == "upregcyr":
                ar_inv.append(("ЙЦУКЕНГШЩЗХЪЁЇІЄҐ", "upregcyr"))
            elif el == "one_reg_log":
                ar_inv.append((user_data[0][field].upper(), "one_reg_log_upper"))
                ar_inv.append((user_data[0][field].lower(), "one_reg_log_lower"))
            else:
                ar_inv.append(("no_absent", "no_absent"))
        inval_el[field] =ar_inv
    return inval_el

#
# @allure.title("Позитивні та негативні тести: поля відображаються")
# @pytest.mark.parametrize("scenario, expected_result", [
#     ("valid", "PASS"),
#     ("no_valid", "FAIL"),
#     #("hidden", "FAIL"),
# ])
# список кортежей из полей и списков словарей с невалидными и валидными данными
def generate_negative_cases():
    """Собираем все наборы: одно поле невалидное, остальные валидные"""
    test_cases = []
    for i, field in enumerate(fields):
        for inv in invalid_values[field]:
            case = valid_values.copy()
            case[i] = inv
            test_cases.append((field, dict(zip(fields, case))))
    return test_cases

# 🔹 Позитивный тест выполняется всегда первым
# @pytest.mark.dependency(name="positive")
def test_positive_form(page_open, user_data):
    global valid_values, invalid_values, fields
    fields = user_data[0].keys()
    valid_values = valid_val(user_data)
    invalid_values = invalid_val(user_data)
    allure.dynamic.title("Позитивний тест: усі поля валідні")
    print('\n')
    debug("Позитивний тест: усі поля валідні", "Початок позитивного тесту")
    ##########################################################################
    try:
        with allure.step('Перехід на головну сторінку сайту'):
            expect(page_open.get_by_role("link", name=" Homepage")).to_be_visible()
            debug("знайдено посилання Homepage", "Перевірка наявності посилання Homepage")
            expect(page_open.get_by_role("heading", name="Hello!")).to_be_visible()
            debug("знайдено заголовок Hello!", "Перевірка наявності заголовка Hello!")
            expect(page_open.get_by_role("link", name="Text input")).to_be_visible()
            debug("знайдено посилання Text input", "Перевірка наявності посилання Text input")
            debug("здійснено клік на заголовку Elements", "Перехід на сторінку едементів HTML")
            link_input = page_open.get_by_role("link", name="Text input")
            changed, new_url = click_and_wait_url_change(page_open, lambda: link_input.click())
            # page.get_by_role("link", name="Text input").click()
            debug("здійснено клік на посиланні Text input", "Перехід на сторінку елементів введення даних")
            assert changed, "Не відкрилась сторінка елементів введення даних"
            debug("відкрилась сторінка елементів введення даних", "Перехід на сторінку елементів введення даних")
            expect(page_open.get_by_role("heading", name="Input field")).to_be_visible()
            debug("знайдено заголовок Input field", "Перевірка наявності заголовка Input field")
            expect(page_open.get_by_role("link", name="Text input")).to_be_visible()
            debug("знайдено посилання Text input", "Перевірка наявності посилання Text input")
            # expect(page_open.get_by_role("textbox", name="Text string*")).to_be_visible()
            # debug("знайдено текстове поле text_string", "Перевірка наявності текстового поля text_string")
            with allure.step("Заповнення форми валідними даними"):
                for field, value in user_data[0].items():
                    if field != "url":
                        expect(page_open.get_by_role("textbox", name=field)).to_be_visible()
                        debug(f"знайдено текстове поле {field}", f"Перевірка наявності текстового поля {field}")
                        tb = page_open.get_by_role("textbox", name=field, exact=True)
                        tb.fill(value)
                        debug("заповнено поле", f"{field}")
                        allure.attach(str(value), name=f"Поле {field}")
                        tb.press("Enter")
                        debug("зафіксоване введення клавішею Enter", f"{field}")
                        expect(page_open.get_by_text(f"Your input was: {value}")).to_be_visible()
                        debug(f"підтверджене введення {value}", f"{field}")
            # page_open.get_by_role("textbox", name="Text string*").fill("Test QA")
            # debug(f"заповнено текстове поле {field}", f"Заповнення текстового поля {field}")


            # expect(page_open.get_by_role("heading", name="Elements")).to_be_visible()
            page_open.get_by_role("heading", name="Elements").click()
            debug("здійснено клік на заголовку Elements", "Перехід на сторінку едементів HTML")
            expect(page_open.get_by_text("Book Store Application")).to_be_visible()
            page_open.get_by_text("Book Store Application").click()
            debug("здійснено клік на елементі Book Store Application", "Перехід на сторінку Застосунок книжкового магазину")
            expect(page_open.get_by_text("Login")).to_be_visible()
            page_open.get_by_text("Login").click()
            debug("здійснено клік на елементі Login списку Book Store Application",
                  "Перехід на сторінку реєстрації у Застосунку книжкового магазину")
            expect(page_open.get_by_role("heading", name="Login", exact=True)).to_be_visible()
            debug("перейшли на сторінку входу у застосунок Book Store Application",
                  "Перехід на сторінку реєстрації у Застосунку книжкового магазину")
            expect(page_open.get_by_role("button", name="New User")).to_be_visible()
            debug("знайдено кнопку переходу на сторінку реєстрації у застосунку Book Store Application",
                  "Перехід на сторінку реєстрації у Застосунку книжкового магазину")
            but_reestr = page_open.get_by_role("button", name="New User")

            changed, new_url = click_and_wait_url_change(page_open, lambda: but_reestr.click())
            debug("зроблено клік на кнопці переходу на сторінку реєстрації у застосунку Book Store Application",
                  "Перехід на сторінку реєстрації у Застосунку книжкового магазину")
            assert changed, "Не відкрилась сторінка реєстрації у Застосунку книжкового магазину"

            # --- обхід реклами ---
            if "google_vignette" in page_open.url or "ad.doubleclick" in page_open.url:
                debug("Виявлено рекламу google_vignette. Повертаємось назад...", "WARNING")
                page_open.go_back()
                expect(but_reestr).to_be_visible(timeout=10000)
                but_reestr.click()
                debug("повторний клік після реклами", "INFO")

            close_button = page_open.get_by_role("button", name="Close").first
            if close_button.is_visible():
                close_button.click()
                debug("Виявлено рекламу з кнопкою Close. Натиснуто на Close", "WARNING")
        # with allure.step('Перевірка заголовку, чи це сторінка реєстрації у застосунку Book Store Application'):
        #     expect(page_open.get_by_role("heading", name="Register", exact=True)).to_be_visible()
        #     debug("перейшли на сторінку реєстрації у застосунку Book Store Application",
        #           "Перехід на сторінку реєстрації у Застосунку книжкового магазину")
        ##########################################################################
        with allure.step("Заповнення форми валідними даними"):
            for field, value in user_data[0].items():
                if field != "url":
                    tb = page_open.get_by_role("textbox", name=field, exact=True)
                    tb.fill(value)
                    debug("заповнено поле", f"{field}")
                    allure.attach(str(value), name=f"Поле {field}")
            # Перехватываем запрос к серверу reCAPTCHA и возвращаем успешный ответ
            page_open.route("https://www.google.com/recaptcha/api2/**", lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body='{"success": true}'
            ))
        print('\n')
        with allure.step('Перехід на кнопку реєстрації екаунту та клік на ній'):
            expect(page_open.get_by_role("button", name="Register")).to_be_visible()
            debug("знайдено кнопку реєстрації у застосунку Book Store Application",
                  "Перехід на сторінку реєстрації у Застосунку книжкового магазину")
            page_open.get_by_role("button", name="Register").click()
            debug("здійснено клік на кнопку реєстрації у застосунку Book Store Application", "Реєстрація у Застосунку книжкового магазину")

            close_button = page_open.get_by_role("button", name="OK").first
            if close_button.is_visible():
                close_button.click()
                debug("Виявлено рекламу з кнопкою OK. Натиснуто на OK", "WARNING")

        # Скриншот страницы
        screenshot = page_open.screenshot()
        page_open.screenshot(type='jpeg', path='screenshots/positiv.jpg')
        debug("Скриншот останньої сторінки positiv.jpg", "Скрін сторінки")
        allure.attach(
            screenshot,
            name=f"Скриншот останньої сторінки",
            attachment_type=allure.attachment_type.PNG
        )

    except AssertionError as e:
        debug(f"Тест провалено: позитивний сценарій не пройдено {e}", "ERROR")
        report_bug_and_stop(f"Тест провалено: позитивний сценарій не пройдено {e}", page_open)
        debug(f"Current URL: {page_open.url}", "INFO")

        # Логування помилок форми
        errors = []
        for selector in [
            "#firstname-error",
            "#lastname-error",
            "#email_address-error",
            "#password-error",
            "#password-confirmation-error",
        ]:
            if page_open.locator(selector).is_visible():
                errors.append(page_open.locator(selector).inner_text())

        alert = page_open.get_by_role("alert").locator("div").first
        if alert.is_visible():
            errors.append(alert.inner_text())
            debug(alert.inner_text(), "Errors list:")

        if errors:
            debug("Знайдено помилки при введенні даних:", "ERROR")
            debug(errors, "Errors list:")
        # Скриншот страницы
        screenshot = page_open.screenshot()
        allure.attach(
            screenshot,
            name=f"Скриншот падіння або помилки",
            attachment_type=allure.attachment_type.PNG
        )

    except Exception as e:
        debug(f"Тест провалено: позитивний сценарій не пройдено з помилкою \"{e}\"", "ERROR")
        report_bug_and_stop(f"Тест провалено: позитивний сценарій не пройдено з помилкою {e}", page_open)
        debug(f"Current URL: {page_open.url}", "INFO")

        # Логування помилок форми
        errors = []
        for selector in [
            "#firstname-error",
            "#lastname-error",
            "#email_address-error",
            "#password-error",
            "#password-confirmation-error",
        ]:
            if page_open.locator(selector).is_visible():
                errors.append(page_open.locator(selector).inner_text())
                debug(page_open.locator(selector).inner_text(), "ERROR")

        alert = page_open.get_by_role("alert").locator("div").first
        if alert.is_visible():
            errors.append(alert.inner_text())
            debug(alert.inner_text(), "ERROR")

        if errors:
            debug("Знайдено помилки при введенні даних:", "ERROR")
            debug(errors, "Errors list:")
        # Скриншот страницы
        screenshot = page_open.screenshot()
        allure.attach(
            screenshot,
            name=f"Скриншот падіння або помилки",
            attachment_type=allure.attachment_type.PNG
        )

        # debug текущего текста страницы для анализа
        try:
            account_text = page_open.locator("#maincontent").inner_text(timeout=5000)
            debug(account_text, "Текст сторінки My Account (якщо є):")
        except:
            debug("Не вдалося отримати текст сторінки My Account", "INFO")

        # Сбрасываем AssertionError, чтобы тест упал и pytest зарегистрировал ошибку
        raise e
