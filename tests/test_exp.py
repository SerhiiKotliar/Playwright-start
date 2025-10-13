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
        with allure.step('Перехід на сторінку створення екаунту'):
            expect(page_open.get_by_role("heading", name="Elements")).to_be_visible()
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
        with allure.step('Перевірка заголовку, чи це сторінка реєстрації у застосунку Book Store Application'):
            expect(page_open.get_by_role("heading", name="Register", exact=True)).to_be_visible()
            debug("перейшли на сторінку реєстрації у застосунку Book Store Application",
                  "Перехід на сторінку реєстрації у Застосунку книжкового магазину")
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

# 🔹 Негативные тесты зависят от позитивного
# @pytest.mark.parametrize("invalid_field, data", generate_negative_cases())
# @pytest.mark.dependency(depends=["positive"])
# def test_negative_form(page_open, invalid_field, data):
def test_negative_form(page_open, user_data):
    global valid_values, invalid_values, fields
    fields = user_data[0].keys()
    valid_values = valid_val(user_data)
    invalid_values = invalid_val(user_data)
    # список кортежей из полей со списками словарей с валидными и невалидными данными
    list_tuppels_negative_tests = generate_negative_cases()
    # збір імен полів для невалідних тестів
    fields_for_negative_tests = [t[0] for t in list_tuppels_negative_tests if t[0] != "url"]
    dict_for_negative_tests = {}
    for ff in fields_for_negative_tests:
        dict_for_negative_tests[ff] = []
    # перебіг по кортежам зі списками невалідних даних
    for t in list_tuppels_negative_tests:
        if t[0] in dict_for_negative_tests.keys():
            dict_negative = {}
            for key, value in t[1].items():
                if key != "url":
                    dict_negative[key] = value
            # створення словника зі списками невалідних даних по полях
            # ключ це ім'я поля а значення список словників з полями і даними'
            dict_for_negative_tests[t[0]].append(dict_negative)
    failed_cases = []  # тут збираємо всі провали
    allure.dynamic.title("Негативний тест: одне поле невалідне, інші поля валідні")
    print('\n')
    debug("Негативний тест: одне поле невалідне, інші поля валідні", "Початок негативного тесту")
    print('\n')

    # try:
    with allure.step('Перехід на сторінку створення екаунту'):
        expect(page_open.get_by_role("heading", name="Elements")).to_be_visible()
        page_open.get_by_role("heading", name="Elements").click()
        debug("здійснено клік на заголовку Elements", "Перехід на сторінку едементів HTML")
        expect(page_open.get_by_text("Book Store Application")).to_be_visible()
        page_open.get_by_text("Book Store Application").click()
        debug("здійснено клік на елементі Book Store Application",
              "Перехід на сторінку Застосунок книжкового магазину")
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
        # page_open.get_by_role("button", name="New User").click()
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
    with allure.step('Перевірка заголовку, чи це сторінка реєстрації у застосунку Book Store Application'):
        expect(page_open.get_by_role("heading", name="Register", exact=True)).to_be_visible()
        debug("перейшли на сторінку реєстрації у застосунку Book Store Application",
              "Перехід на сторінку реєстрації у Застосунку книжкового магазину")
    for field, list_dicts_inv_data in dict_for_negative_tests.items():
        # try:
        allure.dynamic.title(f"Негативний тест: поле '{field}' отримує невалідні значення")
        print('\n')
        debug(f"Негативний тест: поле '{field}' отримує невалідні значення", "Негативні тести")
        print('\n')
    #     поточний словник з черговим негативом для поля
        for dict_cur_data in list_dicts_inv_data:
            try:
                for field_key, el_list in dict_cur_data.items():
                    neg = False
                    if isinstance(el_list, tuple):
                        el_list_n = el_list[0]
                        el_list_d = el_list[1]
                        neg = True
                    else:
                        el_list_d = el_list
                    with allure.step("Заповнення форми"):
                        # debug("заповнення полів форми", "Форма")
                        if neg:
                            ##############################################################
                            tb = page_open.get_by_role("textbox", name=field_key, exact=True)
                            debug(f"заповнення поля {field_key} невалідністю {el_list_n} по типу {el_list_d}", "Заповнення форми")
                            tb.fill(el_list_n)
                            ##############################################################
                            str_att = f"введені невалідні дані {el_list_n} у поле {field_key}:"
                            debug(str_att, f"{field_key}")
                            allure.attach(str_att+" "+ "\""+str(el_list_n)+"\"", name=f"Поле {field_key}")
                        else:
                            ##############################################################
                            tb = page_open.get_by_role("textbox", name=field_key, exact=True)
                            debug(f"заповнення поля {field_key} валідними даними {el_list_d}",
                                  "Заповнення форми")
                            tb.fill(el_list_d)
                            ##############################################################
                            str_att = f"введені валідні дані {el_list_d} у поле {field_key}:"
                            debug(str_att, f"{field_key}")
                            allure.attach(str_att + " " + "\"" + str(el_list_d) + "\"", name=f"Поле {field_key}")
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
                          "Перехід на кнопку реєстрації у Застосунку книжкового магазину")
                    # page_open.get_by_role("button", name="Register").click()
                    # debug("здійснено клік на кнопку реєстрації у застосунку Book Store Application",
                    #       "Реєстрація у Застосунку книжкового магазину")
                    but_registr = page_open.get_by_role("button", name="Register")
                    changed, new_url = click_and_wait_url_change(page_open, lambda: but_registr.click())
                    debug("зроблено клік на кнопці реєстрації у застосунку Book Store Application",
                          "Перехід на сторінку реєстрації у Застосунку книжкового магазину")
                    # assert changed, f"Не відкрилась сторінка реєстрації у Застосунку книжкового магазину при невалідному {field}"
                    if not changed:
                        failed_cases.append((field, el_list_n, str(e)))

                    close_button = page_open.get_by_role("button", name="OK").first
                    if close_button.is_visible():
                        close_button.click()
                        debug("Виявлено рекламу з кнопкою OK. Натиснуто на OK", "WARNING")
                    # assert page_open.get_by_role("strong").filter(has_text="Account Information").is_visible(), \
                    #     "BUG: Відсутня інформація про екаунт"
                # Скриншот страницы
                screenshot = page_open.screenshot()
                page_open.screenshot(type='jpeg', path=f'screenshots/negativ{now.strftime("%d-%m-%Y %H-%M-%S")}.jpg')
                debug("Скриншот останньої сторінки negativ.jpg", "Скрін сторінки")
                print('\n')
                allure.attach(
                    screenshot,
                    name=f"Скриншот останньої сторінки",
                    attachment_type=allure.attachment_type.PNG
                )

            except AssertionError as e:
                # debug(f"Негативний тест пройдено для поля {field} з невалідним значенням \"{el_list_n}\"", "TEST FAIL")
                failed_cases.append((field, el_list_n, str(e)))
                continue

                # alert = page_open.get_by_role("alert").locator("div").first
                # if alert.is_visible():
                #     errors.append(alert.inner_text())
                #     debug(alert.inner_text(), "ERROR")


            except Exception as e:
                # логування інших помилок (поля, алерти тощо)
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
                    failed_cases.append((field, el_list_n, "; ".join(errors)))
                    debug(errors, "ERROR")

                screenshot = page_open.screenshot()
                allure.attach(screenshot, name="Скриншот падіння або помилки", attachment_type=allure.attachment_type.PNG)

            finally:
                # після всіх ітерацій: якщо були фейли — завалюємо тест 1 раз
                if failed_cases:
                    msg = "\n".join([f"{fld}='{val}' → {err}" for fld, val, err in failed_cases])
                    debug(f"Помилки, знайдені негативним тестом:\n{msg}", "ERROR")
                    # raise AssertionError(f"Негативний тест знайшов помилки:\n{msg}")


def test_generate(page_open, user_data):
    global valid_values, invalid_values, fields
    fields = user_data[0].keys()
    valid_values = valid_val(user_data)
    invalid_values = invalid_val(user_data)
    print(generate_negative_cases())

if __name__ == "__main__":
    test_generate()