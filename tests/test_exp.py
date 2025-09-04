import traceback

import allure
import pytest
from playwright.sync_api import expect, Page
# from conftest import page_open
from main_file import report_about, report_bug_and_stop
from helper import debug
import re
from typing import Callable, Pattern, Union, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

fields = ["First Name*", "Last Name*", "Email*", "Password*", "Confirm Password*"]
names_data_for_fields = {"First Name*": "login", "Last Name*": "login_l", "Email*": "email", "Password*": "password", "Confirm Password*": "password"}
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
    val_el = []
    for field in fields:
        val_el.append(user_data[0][names_data_for_fields[field]])
    return val_el
# список невалидных данных по полям
def invalid_val(user_data):
    inval_el = {}
    for field in fields:
        ar_inv = []
        for el in user_data[1][names_data_for_fields[field]]:
            value, mode = in_inv(field, el, user_data)
            if mode == "len":
                first, second = value.split(" ", 1)
                ar_inv.append(first)
                ar_inv.append(second)
            else:
                ar_inv.append(value)
        inval_el[field] =ar_inv
    return inval_el
#генерация невалидных данных по ключам
def in_inv(cur_name: str, el: str, user_data):
    if el == 'absent':
        return  "", el
    elif el == 'url':
        return user_data[0]['url'], el
    elif el[:3] == 'len':
        lminmax = el[4:]
        lmin = int(lminmax.split(" ", 1)[0])
        lmax = int(lminmax.split(" ", 1)[1])
        return (user_data[0][names_data_for_fields[cur_name]] * 6)[:(lmin - 2)] +" "+ (user_data[0][names_data_for_fields[cur_name]] * 6)[:(lmax + 2)], el
    elif el == 'no_email':
        return user_data[0]['url'], el
    elif el == 'no_lower':
        return user_data[0][names_data_for_fields[cur_name]].upper(), el
    elif el == 'no_upper':
        return user_data[0][names_data_for_fields[cur_name]].lower(), el
    elif el == 'no_digit':
        res = re.sub(r"\d", "", el)
        return res + 'ab', el
    elif el == 'no_spec':
        res = "".join(ch for ch in el if ch.isalnum() or ch.isspace())
        return res + '1f', el
    elif el == 'probel':
        return user_data[0][names_data_for_fields[cur_name]][:2] + ' ' + user_data[0][names_data_for_fields[cur_name]][2:], el
    elif el == 'Cyrillic':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = dict(zip(ru, en))
        result1 = []
        for ch in el:
            low = ch.lower()
            if low in mapping:
                new_ch = mapping[low]
                # восстанавливаем регистр
                result1.append(new_ch.upper() if ch.isupper() else new_ch)
            else:
                result1.append(ch)
        return "".join(result1), el
    elif el == 'latin':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = dict(zip(en, ru))
        result2 = []
        for ch in el:
            low = ch.lower()
            if low in mapping:
                new_ch = mapping[low]
                # восстанавливаем регистр
                result2.append(new_ch.upper() if ch.isupper() else new_ch)
            else:
                result2.append(ch)
        return "".join(result2), el
    elif el == 'lowreglat':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = str.maketrans(en + en.lower(), ru + ru.lower())
        converted = el.translate(mapping)
        return converted, el
    elif el == 'upreglat':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = str.maketrans(en + en.upper(), ru + ru.upper())
        converted = el.translate(mapping)
        return converted, el
    elif el == 'lowregcyr':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = str.maketrans(ru + ru.lower(), en + en.lower())
        converted = el.translate(mapping)
        return converted, el
    elif el == 'upregcyr':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = str.maketrans(ru + ru.upper(), en + en.upper())
        converted = el.translate(mapping)
        return converted, el
    elif el == 'one_reg_log':
        return user_data[0][names_data_for_fields[cur_name]].upper(), el
    else:
        return el, el

# @allure.title("Позитивні та негативні тести: поля відображаються")
# @pytest.mark.parametrize("scenario, expected_result", [
#     ("valid", "PASS"),
#     ("no_valid", "FAIL"),
#     #("hidden", "FAIL"),
# ])
# список кортежей из полей со списками невалидных данных
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
@pytest.mark.dependency(name="positive")
def test_positive_form(page_open, user_data):
    global valid_values, invalid_values
    valid_values = valid_val(user_data)
    invalid_values = invalid_val(user_data)
    allure.dynamic.title("Позитивний тест: усі поля валідні")
    print('\n')
    debug("Позитивний тест: усі поля валідні", "Початок позитивного тесту")
    ##########################################################################
    try:
        with allure.step('Перехід на посилання створення екаунту та клік на ньому'):
            link = page_open.get_by_role("link", name="Create an Account")
            expect(link).to_be_visible(timeout=10000)
            debug("здійснено перехід на посилання створення екаунту", "Посилання створення екаунту")
            # link.click()
            debug("здійснено клік на посиланні створення екаунту", "Посилання створення екаунту")
            changed, new_url = click_and_wait_url_change(page_open, lambda: link.click())
            assert changed, "Не відкрилась сторінка створення екаунту"

            # --- обхід реклами ---
            if "google_vignette" in page_open.url or "ad.doubleclick" in page_open.url:
                debug("Виявлено рекламу google_vignette. Повертаємось назад...", "WARNING")
                page_open.go_back()
                expect(link).to_be_visible(timeout=10000)
                link.click()
                debug("повторний клік після реклами", "INFO")

            close_button = page_open.get_by_role("button", name="Close").first
            if close_button.is_visible():
                close_button.click()
                debug("Виявлено рекламу з кнопкою Close. Натиснуто на Close", "WARNING")

        with allure.step('Перевірка заголовку, чи це сторінка створення екаунту'):
            expect(page_open.get_by_text("Create New Customer Account")).to_be_visible(timeout=10000)
            debug("здійснено перехід на сторінку створення екаунту", "Сторінка створення екаунту")
        ##########################################################################
        with allure.step("Заповнення форми валідними даними"):
            for field, value in zip(fields, valid_values):
                tb = page_open.get_by_role("textbox", name=field, exact=True)
                tb.fill(value)
                fail_on_alert(page_open)
                debug("заповнено поле", f"{field}")
                allure.attach(str(value), name=f"Поле {field}")
        with allure.step('Перехід на кнопку створення екаунту та клік на ній'):
            btnS = page_open.get_by_role("button", name="Create an Account")
            expect(btnS).to_be_visible(timeout=10000)
            debug("здійснено перехід на кнопку створення екаунту", "Кнопка створення екаунту")
            # btnS.click()
            debug("здійснено клік на кнопку створення екаунту", "Кнопка створення екаунту")
            changed, new_url = click_and_wait_url_change(page_open, lambda: btnS.click())
            assert changed, "Не відкрилась сторінка створеного екаунту"
            # expect(page_open.get_by_role("alert").locator("div").first).to_be_visible()
            fail_on_alert(page_open)
            if page_open.get_by_role("alert").locator("div").first.is_visible(timeout=10000):
                debug("Помилка створення екаунту", "ПОМИЛКА")
            expect(page_open.get_by_role("alert").locator("div").first).not_to_be_visible(timeout=10000)
        with allure.step('Перевірка переходу на сторінку My Account'):
            expect(page_open.locator("h1")).to_contain_text("My Account", timeout=10000)
            debug("здійснено перехід на сторінку зареєстрованого екаунту", "Сторінка екаунту")

            # # Перевіряємо наявність інформації про акаунт
            # assert page_open.get_by_role("strong").filter(has_text="Account Information").is_visible(), \
            #     "BUG: Відсутня інформація про екаунт"

            account_text = page_open.locator("#maincontent").inner_text(timeout=5000)
            expected_text = f"{user_data[0]['login']} {user_data[0]['login_l']}\n{user_data[0]['email']}"

            assert expected_text in account_text, \
                f"BUG: Інформація про екаунт не відповідає введеним даним"

            # --- debug для позитивного сценарію ---
            debug("інформація про екаунт відповідає введеним даним", "Сторінка екаунту")
            report_about("Тест пройдено: позитивний сценарій успішно виконано", page_open)
            debug(account_text, "Отриманий текст:")
            debug(expected_text, "Очікуваний текст:")
        # Скриншот страницы
        screenshot = page_open.screenshot()
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
@pytest.mark.dependency(depends=["positive"])
# def test_negative_form(page_open, invalid_field, data):
def test_negative_form(page_open, user_data):
    global valid_values, invalid_values
    valid_values = valid_val(user_data)
    invalid_values = invalid_val(user_data)
    failed_cases = []  # тут збираємо всі провали

    try:
        with allure.step('Перехід на посилання створення екаунту та клік на ньому'):
            link = page_open.get_by_role("link", name="Create an Account")
            expect(link).to_be_visible(timeout=10000)
            print('\n')
            debug("здійснено перехід на посилання створення екаунту", "Посилання створення екаунту")
            # link.click()
            debug("здійснено клік на посиланні створення екаунту", "Посилання створення екаунту")
            changed, new_url = click_and_wait_url_change(page_open, lambda: link.click())
            assert changed, "Не відкрилась сторінка створеня екаунту"
            fail_on_alert(page_open)
            if page_open.get_by_role("alert").locator("div").first.is_visible(timeout=10000):
                debug("Помилка створення екаунту", "ПОМИЛКА")
            expect(page_open.get_by_role("alert").locator("div").first).not_to_be_visible(timeout=10000)

            # --- обхід реклами ---
            if "google_vignette" in page_open.url or "ad.doubleclick" in page_open.url:
                debug("Виявлено рекламу google_vignette. Повертаємось назад...", "WARNING")
                page_open.go_back()
                expect(link).to_be_visible(timeout=10000)
                link.click()
                debug("повторний клік після реклами", "INFO")

            close_button = page_open.get_by_role("button", name="Close").first
            if close_button.is_visible():
                close_button.click()
                debug("Виявлено рекламу з кнопкою Close. Натиснуто на Close", "WARNING")

        with allure.step('Перевірка заголовку, чи це сторінка створення екаунту'):
            expect(page_open.get_by_text("Create New Customer Account")).to_be_visible(timeout=10000)
            debug("здійснено перехід на сторінку створення екаунту", "Сторінка створення екаунту")

        list_inv_fields = generate_negative_cases()

        for el_list in list_inv_fields:
            invalid_field, data = el_list
            inv_value = ''
            allure.dynamic.title(f"Негативний тест: поле '{invalid_field}' отримує невалідні значення")
            print('\n')
            debug(f"Негативний тест: поле '{invalid_field}' отримує невалідні значення", "Негативні тести")

            try:
                with allure.step("Заповнення форми"):
                    debug("заповнення полів форми", "Форма")
                    for field, value in data.items():
                        if invalid_field == field:
                            inv_value = value
                        tb = page_open.get_by_role("textbox", name=field, exact=True)
                        tb.fill(value)
                        if inv_value == value:
                            str_att = "введені невалідні дані у поле"
                            debug(str_att, f"{field}")
                        else:
                            str_att = "введені валідні дані у поле"
                            debug(str_att, f"{field}")
                        allure.attach(str_att+" "+ "\""+str(value)+"\"", name=f"Поле {field}")


                with allure.step('Клік на кнопці створення екаунту'):
                    btnS = page_open.get_by_role("button", name="Create an Account")
                    expect(btnS).to_be_visible(timeout=10000)
                    btnS.click()

                    changed, new_url = click_and_wait_url_change(page_open, lambda: btnS.click())
                    assert changed, "Не відкрилась сторінка створеного екаунту"
                    fail_on_alert(page_open)
                    if page_open.get_by_role("alert").locator("div").first.is_visible(timeout=10000):
                        debug("Помилка створення екаунту", "ПОМИЛКА")
                    expect(page_open.get_by_role("alert").locator("div").first).not_to_be_visible(timeout=10000)

                    # тут навмисно ставимо "невірне" очікування,
                    # щоб тест зловив помилку, якщо акаунт створився
                    # expect(page_open.get_by_role("alert")).to_contain_text(
                    #     "Thank you for registering with Main Website Store."
                    # )
                    assert page_open.get_by_role("strong").filter(has_text="Account Information").is_visible(), \
                        "BUG: Відсутня інформація про екаунт"

                # with allure.step('Перевірка переходу на сторінку My Account'):
                #     expect(page_open.locator("h1")).to_be_visible(timeout=20000)
                #     debug("здійснено перехід на сторінку зареєстрованого екаунту", "Сторінка екаунту")
                #     assert page_open.get_by_role("strong").filter(has_text="Account Information").is_visible(), \
                #         "BUG: Відсутня інформація про екаунт"

            except AssertionError as e:
                debug(f"Негативний тест пройдено для поля {invalid_field} зі значенням \"{inv_value}\"", "TEST FAIL")
                failed_cases.append((invalid_field, inv_value, str(e)))

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
                    failed_cases.append((invalid_field, inv_value, "; ".join(errors)))
                    debug(errors, "ERROR")

                screenshot = page_open.screenshot()
                allure.attach(screenshot, name="Скриншот падіння або помилки", attachment_type=allure.attachment_type.PNG)

    finally:
        # після всіх ітерацій: якщо були фейли — завалюємо тест 1 раз
        if failed_cases:
            msg = "\n".join([f"{fld}='{val}' → {err}" for fld, val, err in failed_cases])
            debug(f"Помилки, знайдені негативним тестом:\n{msg}", "ERROR")
            raise AssertionError(f"Негативний тест знайшов помилки:\n{msg}")
