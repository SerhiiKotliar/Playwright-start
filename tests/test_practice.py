import allure
import pytest
from playwright.sync_api import expect

# from Rule_form_new import lat_Cyr_up
# from Rule_form_new import lat_Cyr_up, lat_Cyr_low
# from Rule_form_new import report_about, report_bug_and_stop
from conftest import page_open
from helper import debug
import re
from typing import Callable, Pattern, Union, Optional
from playwright.sync_api import Page, sync_playwright, TimeoutError as PlaywrightTimeoutError, Locator
import invalid_datas as in_d
from datetime import datetime
from enter_to_homepage import enter_to_fieldspage, confirmation, after_fill_fields
from utils import  checking_for_errors

# now = datetime.now()
fields = []
valid_values = []
invalid_values = {}
Cyrillic = "АаБбВвГгДдЕеЄєЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯаяЁёЇїІіЄєҐґ"
latin = "AaZzEeYyUuIiOoPpFfDdGgHhJjKkLlQqWwRrTtSsCcVvBbNnMmXx"
lowregcyr = "абвгдеёжзийлмнопрстуфхцчшщъыьэюяїієґ"
upregcyr = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯЇІЄҐ"
lowreglat = "azeyuiopfdghjklqwrtscvbnmx"
upreglat = "AZEYUIOPFDGHJKLQWRTSCVBNMX"
lat_Cyr_up = "QWERTYUIOPЙЦУКЕНГШЩЗХЪЁЇІЄҐ"
lat_Cyr_low = "qwertyuiopйцукенгшщзхъїієёґ"
def fill_field_js(page, field_name, value):
    page.evaluate(
        """([field, val]) => {
            const el = document.querySelector(`input[name="${field}"], textarea[name="${field}"]`);
            if (el) {
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }""",
        [field_name, value]
    )

def press_enter_js(page, field_name):
    page.evaluate(
        """(field) => {
            const el = document.querySelector(`input[name="${field}"], textarea[name="${field}"]`);
            if (el) {
                const eventInit = { key: 'Enter', code: 'Enter', bubbles: true };
                el.dispatchEvent(new KeyboardEvent('keydown', eventInit));
                el.dispatchEvent(new KeyboardEvent('keyup', eventInit));
            }
        }""",
        field_name
    )



def get_text_field(page: Page, field: str):
    """
    Универсальный локатор для текстового поля или textarea.
    Сначала пробует get_by_role, если не найдёт — fallback на CSS.
    """
    try:
        # Сначала пытаемся по роли (работает, если есть label)
        return page.get_by_role("textbox", name=field, exact=True)
    except Exception:
        # fallback: любой input или textarea с нужным name
        return page.locator(f"input[name='{field}'], textarea[name='{field}']")



def fill_if_exists(page: Page, field: str, value: str, timeout: int = 5000):
    """
    Надёжное заполнение текстового поля.
    Использует get_text_field(), ждёт видимости и делает fill() или type().
    """
    tb = get_text_field(page, field)

    try:
        tb.fill(value)
        # fill_field_js(page, field, value)
    except Exception as e:
        print(f"⚠️ fill() не сработал для {field}: {e}. Используем type()")
        fill_field_js(page, field, value)
    return tb


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
):
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
    val_el = []
    for field in fields:
        val_el.append(user_data[3][field])
    return val_el
# список невалидных данных по полям
def invalid_val(user_data):
    global fields
    inval_el = {}
    # перебір по назвам полів
    for field in fields:
        ar_inv = []
        add_str = ""
        lmin = None
        lmax = None
        # перебір по назвам полів для розбору типу невалідних даних зі списків
        for el in user_data[1][field]:
        # if field != 'fix_enter' and field != "check_attr" and field != 'el_fix_after_fill' and field != 'txt_el_fix_after_fill':
            if el[:3] == 'len':
                lminmax = el[4:]
                if el.count(" ") > 1:
                    lmin = int(lminmax.split(" ", 1)[0])
                    lmax = int(lminmax.split(" ", 1)[1])
                    second = ((user_data[0][field] * 6)[:(lmax + 2)], "lenmax")
                    ar_inv.append(second)
                else:
                    lmin = int(lminmax.split(" ", 1)[0])
                    # second = 0
                first = ((user_data[0][field] * 6)[:(lmin - 1)], "lenmin")
                ar_inv.append(first)
                # ar_inv.append(second)
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
                if lmax is not None:
                    add_str = Cyrillic[:lmax]
                else:
                    add_str = Cyrillic
                ar_inv.append((add_str, "Cyrillic"))
            elif el == "latin":
                if lmax is not None:
                    add_str = latin[:lmax]
                else:
                    add_str = latin
                ar_inv.append((add_str, "latin"))
                # ar_inv.append(("AaZzEeYyUuIiOoPpFfDdGgHhJjKkLlQqWwRrTtSsCcVvBbNnMmXx", "latin"))
            elif el == "lowreglat":
                if lmax is not None:
                    add_str = lowreglat[:lmax]
                else:
                    add_str = lowreglat
                ar_inv.append((add_str, "lowreglat"))
                # ar_inv.append(("qwertyuiop", "lowreglat"))
            elif el == "upreglat":
                if lmax is not None:
                    add_str = upreglat[:lmax]
                else:
                    add_str = upreglat
                ar_inv.append((add_str, "upreglat"))
                # ar_inv.append(("QWERTYUIOP", "upreglat"))
            elif el == "lowregcyr":
                if lmax is not None:
                    add_str = lowregcyr[:lmax]
                else:
                    add_str = lowregcyr
                ar_inv.append((add_str, "lowregcyr"))
                # ar_inv.append(("йцукенгшщзхъїієёґ", "lowregcyr"))
            elif el == "upregcyr":
                if lmax is not None:
                    add_str = upregcyr[:lmax]
                else:
                    add_str = upregcyr
                ar_inv.append((add_str, "upregcyr"))
                # ar_inv.append(("ЙЦУКЕНГШЩЗХЪЁЇІЄҐ", "upregcyr"))
            # elif el == "lat_Cyr":
            #     ar_inv.append(("ЙЦУКЕНГШЩЗХЪЁЇІЄҐ", "upregcyr"))
            # elif el == "lat_Cyr_1":
            #     ar_inv.append(("ЙЦУКЕНГШЩЗХЪЁЇІЄҐ", "upregcyr"))
            elif el == "lat_Cyr_up":
                if lmax is not None:
                    add_str = lat_Cyr_up[:lmax]
                else:
                    add_str = lat_Cyr_up
                ar_inv.append((add_str, "lat_Cyr_up"))
                # ar_inv.append(("QWERTYUIOPЙЦУКЕНГШЩЗХЪЁЇІЄҐ", "lat_Cyr_up"))
            elif el == "lat_Cyr_low":
                if lmax is not None:
                    add_str = lat_Cyr_low[:lmax]
                else:
                    add_str = lat_Cyr_low
                ar_inv.append((add_str, "lat_Cyr_low"))
                # ar_inv.append(("qwertyuiopйцукенгшщзхъїієёґ", "lat_Cyr_low"))
            # elif el == "lat_Cyr_up_1":
            #     ar_inv.append(("ЙЦУКЕНГШЩЗХЪЁЇІЄҐ", "upregcyr"))
            # elif el == "lat_Cyr_low_1":
            #     ar_inv.append(("ЙЦУКЕНГШЩЗХЪЁЇІЄҐ", "upregcyr"))
            # elif el == "Cyrillic_1":
            #     ar_inv.append(("ЙЦУКЕНГШЩЗХЪЁЇІЄҐ", "upregcyr"))
            # elif el == "latin_1":
            #     ar_inv.append(("ЙЦУКЕНГШЩЗХЪЁЇІЄҐ", "upregcyr"))
            # elif el == "one_reg_log":
            #     ar_inv.append((user_data[0][field].upper(), "one_reg_log_upper"))
            #     ar_inv.append((user_data[0][field].lower(), "one_reg_log_lower"))
            elif el == "add_spec":
                if lmax is not None:
                    add_str = user_data[0][field][:lmax-1]
                else:
                    add_str = user_data[0][field][:-1]
                ar_inv.append((add_str + "#", "add_spec"))
            elif el == "add_digit":
                if lmax is not None:
                    add_str = user_data[0][field][:lmax-1]
                else:
                    add_str = user_data[0][field][:-1]
                ar_inv.append((add_str + "5", "add_digit"))
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
# # список кортежей из полей и списков словарей с невалидными и валидными данными
# def generate_negative_cases():
#     """Собираем все наборы: одно поле невалидное, остальные валидные"""
#     global fields
#     test_cases = []
#     for i, field in enumerate(fields):
#         # if field != 'fix_enter' and field != "check_attr" and field != 'el_fix_after_fill' and field != 'txt_el_fix_after_fill':
#         for inv in invalid_values[field]:
#             case = valid_values.copy()
#             case[i] = inv
#             test_cases.append((field, dict(zip(fields, case))))
#     return test_cases


@pytest.mark.skip(reason="Тест вимкнено")
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
@allure.epic("Реєстрація. Валідні дані")
# @allure.feature("Валідні дані")
# @allure.story("Успішний вхід з валідними даними")
# @allure.severity(allure.severity_level.CRITICAL)
# @allure.title("Успішний логін користувача")
@pytest.mark.dependency(name="positive")
def test_positive_form(page_open, user_data):
    global valid_values, invalid_values, fields
    if len(fields) < 1:
        for field in user_data[3].keys():
            fields.append(field)
    # список валідних даних
    valid_values = valid_val(user_data)
    # список зі словників (ключ поле а значення список кортежів (невалід, тип неваліду)
    # invalid_values = invalid_val(user_data)
    print('\n')
    print("\nПозитивний тест: усі поля валідні", "Початок позитивного тесту\n")
    ##########################################################################
    try:
        with allure.step('Перехід на головну сторінку сайту'):
            text_err = ""
            ##########################################################################
            # функція переходу до сторінки з полями, що треба заповнити (page_open)
            page_open = enter_to_fieldspage(page_open)
            ############################################################################
        with allure.step("Заповнення полів валідними даними"):
            el_t = user_data[0]['el_fix_after_fill']
            txt = user_data[0]['txt_el_fix_after_fill']
            for field in fields:
                allure.dynamic.title(f"Позитивний тест: поле '{field}' отримує валідні дані")
                value = user_data[0][field]
                safe_field = re.sub(r'[\\/*?:"<>| ]', "", field)
                tb = page_open.get_by_role("textbox", name=field, exact=True)
                tb.fill(value)
                val = tb.input_value()
                debug(f"Заповнено поле значенням {value}", f"{field}")
                #####################################################################
                # умова, що вибирає чи треба якось фіксувати введення даних у поле, чи це трапляється при події виходу з поля
                # 0 - це фіксація о події виходу, 1 - натисканням Enter, 2 - натисканням кнопки
                if user_data[0]["fix_enter"] == 1:
                    tb.press("Enter")
                    debug(f"Зафіксоване введення даних {val} клавішею Enter", f"{field}")
                ######################################################################
                # функція перевірки появи alert про помилку
                check_m = fail_on_alert(page_open, "error", 2000)
                if check_m is None:
                # перевірка на появу повідомлень про помилки після введення даних у поле
                # тобто коли відомі атрибути аварійного повідомлення (id, чи інші селектори)
                # locator = page_open.locator('//*[@id="error_1_id_text_string"]')
                    if user_data[0]["check_attr"] != '':
                        # відомі атрибути повідомлення про помилку
                        check_m = checking_for_errors(page_open, user_data[0]["check_attr"])
                    else:
                        # невідомі атрибути, але відома частина тексту повідомлення
                        loc_er = page_open.get_by_text(re.compile(r"^(Invalid .*|User .*)"))
                        if loc_er.count() > 0:
                            expect(loc_er).to_be_visible(timeout=1000)
                            check_m = "Повідомлення про помилку", loc_er.inner_text()

                if check_m is not None:
                    text_err = check_m[1]
                    now = datetime.now()
                    screenshot = page_open.screenshot(type='png',
                                         path=f'screenshots/negativ_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png")
                    debug(f'Скриншот останньої сторінки після помилки negativ_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png",
                        "Скрін сторінки", screenshot )
                    raise AssertionError(
                        f"З'явилось повідомлення {text_err} про невалідний формат для поля '{field}' при введенні невалідних даних: {value}")
                        # Элемент не появился — просто пропускаем
            ###################################################################################
            # функція можливих дій після валідного заповнення усих полів
            # у разі відсутності елемента фіксації валідного введення
            if el_t == '':
                confirmation(page_open, value, field)
            ####################################################################################
        with allure.step("Дії після заповнення полів валідними  даними"):
            # функція виконання можливої дії після заповнення полів (наприклад, вхід або реєстрація)
            el_t = user_data[0]['el_fix_after_fill']
            if el_t != '':
                if not after_fill_fields(page_open, el_t, user_data[0]['txt_el_fix_after_fill']):
                    loc_er = page_open.get_by_text(re.compile(r"^(Invalid .*|User .*)"))
                    if loc_er.count() > 0:
                        expect(loc_er).to_be_visible(timeout=1000)
                        debug(f"{loc_er.inner_text()}", "Повідомлення про помилку")
                        raise AssertionError(
                            f"{loc_er.inner_text()}\nНе відкрилась сторінка після кліку на кнопці {txt}")
                    else:
                        debug(f"Вхід у профіль відхилено з невідомих причин", "Вхід у профіль")
                        now = datetime.now()
                        screenshot = page_open.screenshot(type='png',
                                                          path=f'screenshots/question_positiv_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png")
                        debug(
                            f'Скриншот останньої сторінки після проходження негативного тесту з невідомих причин question_positive_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png",
                            "Скрін сторінки", screenshot)
                        print('\n')
                        raise Exception(
                            "З невідомих причин не відкрилась сторінка входу у профіль користувача")
                    # else:
                    #     raise AssertionError(
                    #         f"З невідомих причин не відкрилась сторінка після кліку на кнопці {txt}")
                else:
                    loc_txt_reg = page_open.get_by_text(re.compile(r"^(Welcome, .*|Congradulation.*)"))
                if loc_txt_reg.count() > 0:
                    expect(loc_txt_reg).to_be_visible()
                    debug("Підтверджено привітання користувача", "Вхід у профіль")
                else:
                    debug(f"Вхід у профіль відхилено з невідомих причин", "Вхід у профіль")
                    raise AssertionError(
                        f"{loc_txt_reg.inner_text()}\nЗ невідомих причин не відкрилась сторінка входу у профіль користувача")
        ##################################################################################
        print('\n')
        debug("Позитивні тести пройдено успішно", "PASSED")
        # Скриншот страницы
        now = datetime.now()
        screenshot = page_open.screenshot()
        page_open.screenshot(type='png', path=f'screenshots/positiv_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png")
        debug(f'Скриншот останньої сторінки після заповнення полів positiv_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png", "Скрін сторінки", screenshot)
    except AssertionError as e:
        debug(f"Тест провалено: позитивний сценарій не пройдено \n{e}", "ASSERTIONERROR")

        debug(f"Current URL: {page_open.url}", "INFO")
        # Логування помилок форми
        errorsa = []
        if text_err != "":
            errorsa.append(f"{field}': - '{text_err}\n")
        else:
            errorsa.append(f"{field}': - '{e}\n")
        alert = page_open.get_by_role("alert").locator("div").first
        if alert.is_visible():
            errorsa.append(f"{field}': - '{alert.inner_text()}\n")
        if len(errorsa) > 0:
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
        errors = []
        check_n = fail_on_alert(page_open, "error", 2000)
        if check_n is not None:
            errors.append(f"{field}': - '{check_n[1]}\n")
        debug(f"Тест провалено: позитивний сценарій не пройдено \n{e}", "ERROR")
        debug(f"Current URL: {page_open.url}", "INFO")
        # Логування помилок форми
        errors.append(f"{field}': - '{e}\n")
        alert = page_open.get_by_role("alert").locator("div").first
        if alert.is_visible():
            errors.append(alert.inner_text()+"\n")
            debug(alert.inner_text(), "ERROR")
        if len(errors) > 0:
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
@allure.epic("Реєстрація. Невалідні дані")
# @pytest.mark.dependency(depends=["positive"])
def test_negative_form(page_open: Page, user_data):
    global valid_values, invalid_values, fields
    if len(fields) < 1:
        for field in user_data[3].keys():
            fields.append(field)
    # список валідних даних
    valid_values = valid_val(user_data)
    # список зі словників (ключ поле а значення список невалідів)
    invalid_values = invalid_val(user_data)
    el_t = user_data[0]['el_fix_after_fill']
    txt = user_data[0]['txt_el_fix_after_fill']
    count_tests_for_field = {}
    for field_in, list_inv in invalid_values.items():
        count_tests_for_field[field_in] = len(list_inv)
    failed_cases = []  # тут збираємо всі провали
    print('\n')
    print("\nНегативний тест: по черзі поля невалідні", "Початок негативного тесту\n")
    with (allure.step('\nПерехід на головну сторінку сайту')):
        print('\n')
        ####################################################################################
        page_open = enter_to_fieldspage(page_open)
        #####################################################################################
    with allure.step("Заповнення полів невалідами"):
        print('\n')
        for field, list_tup_invalid in invalid_values.items():
            try:
                safe_field = re.sub(r'[\\/*?:"<>| ]', "", field)
                # кількість прогонів циклу дорівнює кількості невалідів у списку
                for el_invalid in list_tup_invalid:
                    # value_n = ""
                    field_n = ""
                    el_invalid_data = el_invalid[0]
                    el_invalid_t = el_invalid[1]
                    tb_f_neg = page_open.get_by_role("textbox", name=field, exact=True)
                    debug(f"заповнення поля невалідністю {el_invalid_data} по типу {el_invalid_t}",f"{field}")
                    tb_f_neg.fill(el_invalid_data)
                    field_n = field
                    #####################################################################
                    # умова, що вибирає чи треба якось фіксувати введення даних у поле, чи це трапляється при події виходу з поля
                    # 0 - це фіксація о події виходу, 1 - натисканням Enter, 2 - натисканням кнопки
                    if user_data[0]["fix_enter"] == 1:
                        tb_f_neg.press("Enter")
                        debug(f"Зафіксоване введення невалідних даних {el_invalid_data} клавішею Enter", f"{field}")
                    ######################################################################
                    # функція перевірки появи alert про помилку
                    check_m = fail_on_alert(page_open, "error", 2000)
                    if check_m is None:
                        # перевірка на появу повідомлень про помилки після введення даних у поле
                        # тобто коли відомі атрибути аварійного повідомлення (id, чи інші селектори)
                        # locator = page_open.locator('//*[@id="error_1_id_text_string"]')
                        if user_data[0]["check_attr"] != '':
                            # відомі атрибути повідомлення про помилку
                            check_m = checking_for_errors(page_open, user_data[0]["check_attr"])
                        else:
                            # невідомі атрибути, але відома частина тексту повідомлення
                            loc_er = page_open.get_by_text(re.compile(r"^(Invalid .*|User .*)"))
                            if loc_er.count() > 0:
                                expect(loc_er).to_be_visible(timeout=1000)
                                check_m = "Повідомлення про помилку", loc_er.inner_text()

                    if check_m is not None:
                        text_err = check_m[1]
                        now = datetime.now()
                        screenshot = page_open.screenshot(type='png',
                                                          path=f'screenshots/negativ_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png")
                        debug(
                            f'Скриншот останньої сторінки після введення неваліду negativ_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png",
                            "Скрін сторінки", screenshot)
                        print('\n')
                        # raise AssertionError(
                        #     f"З'явилось повідомлення {text_err} про невалідний формат для поля '{field}' при введенні невалідних даних: {el_invalid_data}")
                        failed_cases.append((field_n, el_invalid_data, f"З'явилось повідомлення {text_err} про невалідний формат для поля '{field}' при введенні невалідних даних: {el_invalid_data}"))
                        # continue
                        # Элемент не появился — просто пропускаем
                    else:
                        # в деяких випадках підтвердження введених валідних даних
                        if el_t == '':
                            confirmation(page_open, el_invalid_data, field)
                    #######################################################################
                    for field_v, val_valid in user_data[3].items():
                        if field_v != field:
                            value = ""
                            field_n = ""
                            safe_field1 = re.sub(r'[\\/*?:"<>| ]', "", field_v)
                            tb_f_v = page_open.get_by_role("textbox", name=field_v, exact=True)
                            debug(f"заповнення поля валідними даними {val_valid}",
                                  f"{field_v}")
                            tb_f_v.fill(val_valid)
                            value = val_valid
                            field_n = field_v
                            #####################################################################
                            # умова, що вибирає чи треба якось фіксувати введення даних у поле, чи це трапляється при події виходу з поля
                            # 0 - це фіксація о події виходу, 1 - натисканням Enter, 2 - натисканням кнопки
                            if user_data[0]["fix_enter"] == 1:
                                tb_f_v.press("Enter")
                                debug(f"Зафіксоване введення валідних даних {val_valid} клавішею Enter", f"{field_v}")
                            ######################################################################
                            # функція перевірки появи alert про помилку
                            check_m = fail_on_alert(page_open, "error", 2000)
                            if check_m is None:
                                # перевірка на появу повідомлень про помилки після введення даних у поле
                                # тобто коли відомі атрибути аварійного повідомлення (id, чи інші селектори)
                                # locator = page_open.locator('//*[@id="error_1_id_text_string"]')
                                if user_data[0]["check_attr"] != '':
                                    # відомі атрибути повідомлення про помилку
                                    check_m = checking_for_errors(page_open, user_data[0]["check_attr"])
                                else:
                                    # невідомі атрибути, але відома частина тексту повідомлення
                                    loc_er = page_open.get_by_text(re.compile(r"^(Invalid .*|User .*)"))
                                    if loc_er.count() > 0:
                                        expect(loc_er).to_be_visible(timeout=1000)
                                        check_m = "Повідомлення про помилку", loc_er.inner_text()

                            if check_m is not None:
                                text_err = check_m[1]
                                now = datetime.now()
                                screenshot = page_open.screenshot(type='png',
                                                                  path=f'screenshots/negativ_question_{safe_field1}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png")
                                debug(
                                    f'Скриншот останньої сторінки після помилки при введенні валідних даних negativ_question_{safe_field1}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png",
                                    "Скрін сторінки", screenshot)
                                print('\n')
                                failed_cases.append((field_n, value, f"З'явилось повідомлення {text_err} про невалідний формат для поля '{field_v}' при введенні валідних даних: {val_valid}"))
                            else:
                                # Элемент не появился — просто пропускаем
                                # в деяких випадках підтвердження введених валідних даних
                                if el_t == '':
                                    confirmation(page_open, val_valid, field_v)
                        #############################################################################
                    with allure.step("Дії після заповнення полів невалідними  даними"):
                        # функція виконання можливої дії після заповнення полів (наприклад, вхід або реєстрація)
                        if el_t != '':
                            if not after_fill_fields(page_open, el_t, txt):
                                loc_er = page_open.get_by_text(re.compile(r"^(Invalid .*|User .*)"))
                                if loc_er.count() > 0:
                                    expect(loc_er).to_be_visible(timeout=1000)
                                    debug(f"{loc_er.inner_text()}", f"Не відкрилась сторінка після кліку на кнопці {txt}")
                                    failed_cases.append((field, el_invalid_data, f"{loc_er.inner_text()}\nНе відкрилась сторінка після кліку на кнопці {txt}"))
                                    now = datetime.now()
                                    screenshot = page_open.screenshot(type='png',
                                                                      path=f'screenshots/negativ_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png")
                                    debug(
                                        f'Скриншот останньої сторінки після планової помилки negativ_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png",
                                        "Скрін сторінки", screenshot)
                                    print('\n')
                                    er_txt = loc_er.inner_text()
                                    # Перезагрузка страницы
                                    page_open.reload()
                                    page_open.wait_for_load_state("domcontentloaded")
                                    # Новый локатор после reload
                                    loc_er1 = page_open.get_by_text(er_txt)
                                    # # Проверка, что сообщение исчезло
                                    expect(loc_er1).not_to_be_visible()
                                    # expect(page_open.get_by_text(er_txt)).to_have_count(0)
                                    debug(f"Скинута помилка {er_txt}","Скидання помилки")
                                    print('\n')

                            else:
                                loc_txt_reg = page_open.get_by_text(re.compile(r"^(Welcome, .*|Congradulation.*)"))
                                if loc_txt_reg.count() > 0:
                                    expect(loc_txt_reg).to_be_visible()
                                    debug("Підтверджено привітання користувача", "Вхід у профіль")
                                    screenshot = page_open.screenshot(type='png',
                                                                      path=f'screenshots/questions_positiv_{safe_field1}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png")
                                    debug(
                                        f'Скриншот останньої сторінки після проходження позитивного тесту з невідомих причин question_positiv_{safe_field1}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png",
                                        "Скрін сторінки", screenshot)
                                    print('\n')
                                else:
                                    debug(f"Вхід у профіль відхилено з невідомих причин", "Вхід у профіль")
                                    now = datetime.now()
                                    screenshot = page_open.screenshot(type='png',
                                                                      path=f'screenshots/question_negativ_{safe_field1}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png")
                                    debug(
                                        f'Скриншот останньої сторінки після проходження негативного тесту з невідомих причин question_negative_{safe_field1}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png",
                                        "Скрін сторінки", screenshot)
                                    print('\n')
                                    raise Exception(
                                        "З невідомих причин не відкрилась сторінка входу у профіль користувача")
                    # ###################################################################################
            except Exception as e:
                # логування інших помилок (поля, алерти тощо)
                check_n = fail_on_alert(page_open, "error", 2000)
                errors = []

                if check_n is not None:
                    errors.append(f"{field_n}': - '{check_n[1]}\n")
                errors.append(f"{field_n}': - '{e}\n")

                alert = page_open.get_by_role("alert").locator("div").first
                if alert.is_visible():
                    errors.append(alert.inner_text()+"\n")
                    debug(alert.inner_text(), "ERROR")
                if len(errors) > 0:
                    debug(f"Знайдено помилки при введенні даних:\n{errors}", "Errors list:")

                screenshot = page_open.screenshot()
                now = datetime.now()
                debug(
                    f'Скриншот падіння або помилки у полі {field_n}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png",
                    "Скрін сторінки", screenshot)
                allure.attach(screenshot, name=f"Скриншот падіння або помилки у полі {field_n}",
                              attachment_type=allure.attachment_type.PNG)
        if failed_cases:
            msg = "\n".join([f"{fld}='{val}' → {err}" for fld, val, err in failed_cases])
            txt_neg_tests = ""
            txt_neg_int = 0
            for key, neg_test in count_tests_for_field.items():
                txt_neg_tests = txt_neg_tests + f"{neg_test} тестах(і) для поля '{key}'\n"
                txt_neg_int += int(neg_test)
            print('\n')
            debug(f"{len(failed_cases)} помилок(ки), знайдено у {txt_neg_tests}:{msg}",
                  "ERRORS")
            print('\n')
            if txt_neg_int == len(failed_cases):
                debug("Всі негативні тести пройдено успішно(впали)", "Результат негативних тестів")
            else:
                debug("Частково негативні тести пройдено успішно(впали)", "Результат негативних тестів")
