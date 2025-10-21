import traceback

import allure
import pytest
from playwright.sync_api import expect
# from Rule_form_new import report_about, report_bug_and_stop
from conftest import page_open
from helper import debug
import re
from typing import Callable, Pattern, Union, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import invalid_datas as in_d
from datetime import datetime
from enter_to_homepage import enter_to_fieldspage
from utils import  checking_for_errors

# now = datetime.now()
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
        # pytest.fail(f"❌ З'явилось повідомлення типу '{type_}': {el.inner_text()}")
        debug(f"{el.inner_text()}", f"❌ З'явилось повідомлення типу '{type_}'")
        return type_, el.inner_text()
    except PlaywrightTimeoutError:
        # если не появилось — всё хорошо
        # pass
        return None

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
        if field != 'fix_enter' and field != "check_attr" and field != 'el_fix_after_fill' and field != 'txt_el_fix_after_fill':
            ar_inv = []
            # перебір по назвам полів для розбору типу невалідних даних зі списків
            for el in user_data[1][field]:
            # if field != 'fix_enter' and field != "check_attr" and field != 'el_fix_after_fill' and field != 'txt_el_fix_after_fill':
                if el[:3] == 'len':
                    lminmax = el[4:]
                    lmin = int(lminmax.split(" ", 1)[0])
                    lmax = int(lminmax.split(" ", 1)[1])
                    first = ((user_data[0][field] * 6)[:(lmin - 1)], "lenmin")
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

def test_collection_interactive_elements(page_open):
    import json
    def get_dom_structure(page):
        # Выполняем JavaScript, чтобы пройтись по всем элементам и собрать данные
        return page.evaluate("""
            () => {
                const selectors = [
                    'a[href]',
                    'button',
                    'input',
                    'select',
                    'textarea',
                    'option',
                    'label',
                    'summary',
                    'details',
                    '[tabindex]',
                    '[role="button"]',
                    '[role="link"]',
                    '[contenteditable]'
                ];

                const elements = Array.from(document.querySelectorAll(selectors.join(',')));

                return elements.map(el => ({
                    tag: el.tagName.toLowerCase(),
                    type: el.getAttribute('type'),
                    id: el.id,
                    name: el.getAttribute('name'),
                    classes: el.className,
                    role: el.getAttribute('role'),
                    text: el.innerText.trim(),
                    href: el.getAttribute('href'),
                    value: el.value,
                }));
            }
            """)
    # Получаем структуру DOM
    dom_tree = get_dom_structure(page_open)
    # Сохраняем в JSON-файл
    # with open("dom_structure.json", "w", encoding="utf-8") as f:
    #     json.dump(dom_tree, f, ensure_ascii=False, indent=2)
    # with open("dom_structure.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)
    print(f"🔹 Найдено интерактивных элементов: {len(dom_tree)}")
    print(json.dumps(dom_tree, ensure_ascii=False, indent=2))
    # print(json.dumps(data, ensure_ascii=False, indent=2))
    page_open.close()


# 🔹 Позитивный тест выполняется всегда первым
@pytest.mark.dependency(name="positive")
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
            ##########################################################################
            # функція переходу до сторінки з полями, що треба заповнити (page_open)
            page_open = enter_to_fieldspage(page_open)
            #############################################################################
            with allure.step("Заповнення форми валідними даними"):
                for field, value in user_data[0].items():
                    safe_field = re.sub(r'[\\/*?:"<>| ]', '_', field)
                    now = datetime.now()
                    if field != "url" and field != 'fix_enter' and field != "check_attr" and field != 'el_fix_after_fill' and field != 'txt_el_fix_after_fill':
                        expect(page_open.get_by_role("textbox", name=field)).to_be_visible()
                        debug(f"знайдено текстове поле {field}", f"Перевірка наявності текстового поля {field}")
                        tb = page_open.get_by_role("textbox", name=field, exact=True)
                        # value = "пр ско№"
                        tb.fill(value)
                        debug(f"Заповнено поле значенням {value}", f"Поле {field}")
                        allure.attach(f"Заповнено поле значенням {value}", name=f"Поле {field}")
                        #####################################################################
                        # умова, що вибирає чи треба якось фіксувати введення даних, чи це трапляється при події виходу з поля
                        if user_data[0]["fix_enter"] == 1:
                            tb.press("Enter")
                            debug("Зафіксоване введення даних клавішею Enter", f"Поле {field}")
                        ######################################################################
                        # функція перевірки появи повідомлень про помилку
                        # checking_for_errors(page_open, tag: str)
                        check_m = fail_on_alert(page_open, "error", 2000)
                        if check_m is None:
                        # перевірка на появу повідомлень про помилки після введення даних у поле
                        # locator = page_open.locator('//*[@id="error_1_id_text_string"]')
                            check_m = checking_for_errors(page_open, user_data[0]["check_attr"])
                        # else:
                        #     check_m = fail_on_alert(page_open, "error", 2000)
                        if check_m[0] is not None:
                            #########################################################################
                            # try:
                                # locator.wait_for(state="visible", timeout=2000)
                                # # Если элемент появился — тогда проверяем
                                # if locator.count() > 0 and locator.is_visible():
                                # if locator.count() > 0 and locator.is_visible:
                            text_err = check_m[1]
                            now = datetime.now()
                            page_open.screenshot(type='jpeg',
                                                 path=f'screenshots/negativ_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.jpeg")
                            debug(
                                f'Скриншот останньої сторінки після помилки negativ_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.jpeg",
                                "Скрін сторінки")
                            allure.attach(
                                page_open.screenshot(),
                                name=f"Скриншот останньої сторінки після помилки",
                                attachment_type=allure.attachment_type.PNG)
                            raise AssertionError(
                                f"З'явилось повідомлення {text_err} про невалідний формат для поля '{field}' при введенні невалідних даних: {value}")
                            # except PlaywrightTimeoutError:
                                # Элемент не появился — просто пропускаем
                                ##################################################################
                                # функція можливих дій після валідного заповненння поля
                                # confirmation(page_open, value, field)
                        expect(page_open.get_by_text(f"Your input was: {value}")).to_be_visible()
                        debug(f"Підтверджене валідне введення {value}", f"{field}")
                                ######################################################################

                # Скриншот страницы
                screenshot = page_open.screenshot()
                page_open.screenshot(type='jpeg', path=f'screenshots/positiv_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.jpeg")
                debug(f'Скриншот останньої сторінки після заповнення полів positiv_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.jpeg", "Скрін сторінки")
                allure.attach(
                    screenshot,
                    name=f"Скриншот останньої сторінки піля заповнення полів",
                    attachment_type=allure.attachment_type.PNG
                )
                ####################################################################################
                # функція виконання можливої дії після заповнення полів (наприклад, вхід або реєстрація)
                # after_fill_fields(page_open)
                ##################################################################################
                debug(f"Позитивний тест пройдено", "PASSED")

    except AssertionError as e:
        debug(f"Тест провалено: позитивний сценарій не пройдено \n{e}", "ASSERTIONERROR")
        debug(f"Current URL: {page_open.url}", "INFO")
        # Логування помилок форми
        errorsa = []
        if text_err is not None:
            errorsa.append(f"{field}': - '{text_err}")
        else:
            errorsa.append(f"{field}: {e}")
        alert = page_open.get_by_role("alert").locator("div").first
        if alert.is_visible():
            errorsa.append(f"{field}': - '{alert.inner_text()}")
        if len(errorsa) > 1:
            debug(f"Знайдено помилки при введенні даних:\n{errorsa}", "AssertionErrors list:")
        # Скриншот страницы
        screenshot = page_open.screenshot()
        allure.attach(
            screenshot,
            name=f"Скриншот падіння або помилки у полі {field}",
            attachment_type=allure.attachment_type.PNG
        )
        text_err = ""
    except Exception as e:
        fail_on_alert(page_open, "error", 2000)
        debug(f"Тест провалено: позитивний сценарій не пройдено з помилкою \"{e}\"", "ERROR")
        debug(f"Current URL: {page_open.url}", "INFO")
        # Логування помилок форми
        errors = []
        errors.append(f"{field}': - '{e}")
        alert = page_open.get_by_role("alert").locator("div").first
        if alert.is_visible():
            errors.append(alert.inner_text())
            debug(alert.inner_text(), "ERROR")
        if len(errors) > 1:
            debug(f"Знайдено помилки при введенні даних:\n{errors}", "Errors list:")
        # Скриншот страницы
        screenshot = page_open.screenshot()
        allure.attach(
            screenshot,
            name=f"Скриншот падіння або помилки у полі {field}",
            attachment_type=allure.attachment_type.PNG
        )

        # # debug текущего текста страницы для анализа
        # try:
        #     account_text = page_open.locator("#maincontent").inner_text(timeout=5000)
        #     debug(account_text, "Текст сторінки My Account (якщо є):")
        # except:
        #     debug("Не вдалося отримати текст сторінки My Account", "INFO")
        #
        # # Сбрасываем AssertionError, чтобы тест упал и pytest зарегистрировал ошибку
        # raise e

# 🔹 Негативные тесты зависят от позитивного
# @pytest.mark.parametrize("invalid_field, data", generate_negative_cases())
@pytest.mark.dependency(depends=["positive"])
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
    count_tests_for_field = {}
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
    with (allure.step('Перехід на головну сторінку сайту')):
        expect(page_open.get_by_role("link", name=" Homepage")).to_be_visible()
        debug("знайдено посилання Homepage", "Перевірка наявності посилання Homepage")
        expect(page_open.get_by_role("heading", name="Hello!")).to_be_visible()
        debug("знайдено заголовок Hello!", "Перевірка наявності заголовка Hello!")
        expect(page_open.get_by_role("link", name="Text input")).to_be_visible()
        debug("знайдено посилання Text input", "Перевірка наявності посилання Text input")
        link_input = page_open.get_by_role("link", name="Text input")
        changed, new_url = click_and_wait_url_change(page_open, lambda: link_input.click())
        debug("здійснено клік на посиланні Text input", "Перехід на сторінку елементів введення даних")
        assert changed, "Не відкрилась сторінка елементів введення даних"
        debug("відкрилась сторінка елементів введення даних", "Перехід на сторінку елементів введення даних")
        expect(page_open.get_by_role("heading", name="Input field")).to_be_visible()
        debug("знайдено заголовок Input field", "Перевірка наявності заголовка Input field")
        ###################################################################################################################
        expect(page_open.get_by_role("link", name="Text input")).to_be_visible()
        debug("знайдено посилання Text input", "Перевірка наявності посилання Text input")
        page_open.get_by_role("link", name="Text input").click()
        # changed, new_url = click_and_wait_url_change(page_open, lambda: link_input.click())
        debug("здійснено клік на посиланні Text input", "Перехід на вкладку для введення тексту")
        # assert changed, "Не відкрилась сторінка елементів введення даних"
        # expect(page_open.get_by_role("textbox", name="Text string*")).to_be_visible()
        # debug("знайдено текстове поле Text string*", "Перевірка наявності текстового поля Text string*")
        for field, list_dicts_inv_data in dict_for_negative_tests.items():
            # try:
            count_tests_for_field[field] = len(list_dicts_inv_data)
            allure.dynamic.title(f"Негативний тест: поле '{field}' отримує невалідні значення")
            print('\n')
            debug(f"Негативний тест: поле '{field}' отримує невалідні значення", "Негативні тести")
            print('\n')
            #     поточний словник з черговим негативом для поля
            for dict_cur_data in list_dicts_inv_data:
                try:
                    for field_key, el_list in dict_cur_data.items():
                        neg = False
                        value = ""
                        if isinstance(el_list, tuple):
                            el_list_n = el_list[0]
                            el_list_d = el_list[1]
                            neg = True
                        else:
                            el_list_d = el_list
                        with allure.step("Заповнення полів"):
                            # debug("заповнення полів форми", "Форма")
                            tb = page_open.get_by_role("textbox", name=field_key, exact=True)
                            if neg:
                                ##############################################################
                                # tb = page_open.get_by_role("textbox", name=field_key, exact=True)
                                debug(f"заповнення поля {field_key} невалідністю {el_list_n} по типу {el_list_d}",
                                      "Заповнення форми")
                                tb.fill(el_list_n)
                                value = el_list_n
                                ##############################################################
                                str_att = f"введені невалідні дані {el_list_n} у поле {field_key}:"
                                debug(str_att, f"{field_key}")
                                allure.attach(str_att + " " + "\"" + str(el_list_n) + "\"", name=f"Поле {field_key}")
                            else:
                                ##############################################################
                                # tb = page_open.get_by_role("textbox", name=field_key, exact=True)
                                debug(f"заповнення поля {field_key} валідними даними {el_list_d}",
                                      "Заповнення форми")
                                tb.fill(el_list_d)
                                value = el_list_d
                                ##############################################################
                                str_att = f"введені валідні дані {el_list_d} у поле {field_key}:"
                                debug(str_att, f"{field_key}")
                                allure.attach(str_att + " " + "\"" + str(el_list_d) + "\"", name=f"Поле {field_key}")
                            tb.press("Enter")
                            debug("зафіксоване введення клавішею Enter", f"{field_key}")

                            # перевірка на появу повідомлень про помилки
                            locator = page_open.locator('//*[@id="error_1_id_text_string"]')
                            text_err = locator.inner_text()
                            page_open.wait_for_selector('//*[@id="error_1_id_text_string"]', timeout=1000)
                            if locator.is_visible():
                                safe_field = re.sub(r'[\\/*?:"<>| ]', '_', field_key)
                                now = datetime.now()
                                page_open.screenshot(type='jpeg',
                                                     path=f'screenshots/negativ_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.jpeg")
                                debug(f'Скриншот останньої сторінки negativ_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.jpeg", "Скрін сторінки")
                                allure.attach(
                                    page_open.screenshot(),
                                    name=f"Скриншот останньої сторінки",
                                    attachment_type=allure.attachment_type.PNG)
                                print('\n')
                                raise AssertionError(f"З'явилось повідомлення {text_err} про невалідний формат для поля '{field_key}' при введенні невалідних даних: {el_list_n}")
                            expect(page_open.get_by_text(f"Your input was: {value}")).to_be_visible()
                            debug(f"підтверджене введення {value}", f"{field}")
                except AssertionError as e:
                    # debug(f"Негативний тест пройдено для поля {field} з невалідним значенням \"{el_list_n}\"", "TEST FAIL")
                    fail_on_alert(page_open, "error", 2000)
                    failed_cases.append((field, el_list_n, str(e)))
                    continue

                    # alert = page_open.get_by_role("alert").locator("div").first
                    # if alert.is_visible():
                    #     errors.append(alert.inner_text())
                    #     debug(alert.inner_text(), "ERROR")


                except Exception as e:
                    # логування інших помилок (поля, алерти тощо)
                    fail_on_alert(page_open, "error", 2000)
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
                    allure.attach(screenshot, name="Скриншот падіння або помилки",
                                  attachment_type=allure.attachment_type.PNG)
                    # page_open.screenshot(type='jpeg',
                    #                      path=f'screenshots/negativ{now.strftime("%d-%m-%Y %H-%M-%S")}.jpg')
                    # debug("Скриншот останньої сторінки negativerror.jpg", "Скрін сторінки")

                # finally:
                    # # після всіх ітерацій: якщо були фейли — завалюємо тест 1 раз
                    # if failed_cases:
                    #     msg = "\n".join([f"{fld}='{val}' → {err}" for fld, val, err in failed_cases])
                    #     debug(f"Помилки, знайдені негативним тестом:\n{msg}", "ERROR")
                    #     # raise AssertionError(f"Негативний тест знайшов помилки:\n{msg}")
        # після всіх ітерацій: якщо були фейли — завалюємо тест 1 раз
        if failed_cases:
            msg = "\n".join([f"{fld}='{val}' → {err}" for fld, val, err in failed_cases])
            print('\n')
            txt_neg_tests = ""
            for key, neg_test in count_tests_for_field.items():
                txt_neg_tests = txt_neg_tests + f"\n{neg_test} тестах(і) для поля '{key}'"
            # debug(f"{len(failed_cases)} Помилок, знайдених у {count_tests_for_field} негативним тестом:\n{msg}", "ERROR")
            debug(f"{len(failed_cases)} помилок(ки), знайдених у {txt_neg_tests}:\n{msg}",
                  "ERROR")
            # raise AssertionError(f"Негативний тест знайшов помилки:\n{msg}")
