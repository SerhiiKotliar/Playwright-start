import allure
import pytest

from conftest import page_open
from helper import debug
import re
from playwright.sync_api import Page, expect, Dialog
from typing import Callable, Pattern, Union, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from main_file import report_about, report_bug_and_stop

fields = ["First Name*", "Last Name*", "Email*", "Password*", "Confirm Password*"]
names_data_for_fields = {"First Name*": "login", "Last Name*": "login_l", "Email*": "email", "Password*": "password", "Confirm Password*": "password"}
valid_values = []
invalid_values = {}

# @allure.title("Позитивний тест: поле 'First Name*' відображається")
# @pytest.mark.parametrize("scenario, expected_result", [
#     ("visible", "PASS"),
#     ("absent", "FAIL"),
#     ("hidden", "FAIL"),
# ])
# def test_first_name_field(page_open, scenario, expected_result, user_data):
#     page_open.goto("https://demoqa.com/")
#     import re
#     from playwright.sync_api import Page, expect
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


def catch_dialog(page: Page) -> str:
    """Перехватывает диалоговое окно с одной кнопкой и возвращает его текст"""
    dialog_text = ""

    def handle_dialog(dialog: Dialog):
        nonlocal dialog_text
        dialog_text = dialog.message
        print("Перехвачено окно:", dialog_text)
        dialog.accept()  # нажимаем ОК (можно заменить на dialog.dismiss())

    # ловим одно окно
    page.once("dialog", handle_dialog)

    return dialog_text



def handle_dialog(page: Page, action, expected_text: str = None, accept: bool = True) -> str:
    """
    Выполняет действие, которое вызывает диалоговое окно (alert/confirm/prompt),
    перехватывает окно и возвращает его текст.

    :param page: объект Playwright Page
    :param action: функция/лямбда с действием, которое вызывает окно
    :param expected_text: ожидаемый текст окна (опционально)
    :param accept: True - нажать ОК, False - нажать Cancel
    :return: текст окна
    """
    # ждём событие dialog
    with page.expect_event("dialog") as dialog_info:
        action()  # выполняем действие, которое вызовет alert/confirm

    dialog = dialog_info.value
    text = dialog.message
    print("Диалоговое окно:", text)

    # проверка текста
    if expected_text:
        assert expected_text in text, (
            f"Ожидали текст '{expected_text}', но получили '{text}'"
        )

    # действие: ОК или Cancel
    if accept:
        dialog.accept()
    else:
        dialog.dismiss()

    return text

from playwright.sync_api import Page, expect

def handle_html_modal(page: Page, modal_selector: str, ok_button_selector: str, expected_text: str = None) -> str:
    """
    Ждёт появления HTML-модалки, проверяет текст и нажимает ОК.

    :param page: объект Playwright Page
    :param modal_selector: селектор модалки
    :param ok_button_selector: селектор кнопки ОК внутри модалки
    :param expected_text: ожидаемый текст модалки (опционально)
    :return: текст модалки
    """
    # находим модалку
    modal = page.locator(modal_selector)
    expect(modal).to_be_visible(timeout=10000)  # ждём до 10 секунд

    text = modal.inner_text()
    print("Текст модалки:", text)

    if expected_text:
        assert expected_text in text, f"Ожидали текст '{expected_text}', но получили '{text}'"

    # нажимаем кнопку ОК
    modal.locator(ok_button_selector).click()

    # ждём, пока модалка исчезнет
    expect(modal).not_to_be_visible(timeout=5000)

    return text



def test_example(page_open: Page, user_data) -> None:
    try:
        page_open.locator("div").filter(has_text=re.compile(r"^Elements$")).first.click()
        page_open.get_by_text("Book Store Application").click()
        page_open.get_by_role("listitem").filter(has_text="Login").click()
        page_open.get_by_role("button", name="New User").click()
        page_open.get_by_role("textbox", name="First Name").fill(user_data[0]['login'])
        page_open.get_by_role("textbox", name="Last Name").fill(user_data[0]['login_l'])
        page_open.get_by_role("textbox", name="UserName").fill(user_data[0]['email'])
        page_open.get_by_role("textbox", name="Password").fill(user_data[0]['password'])
        # Перехватываем запрос к серверу reCAPTCHA и возвращаем успешный ответ
        page_open.route("https://www.google.com/recaptcha/api2/**", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"success": true}'
        ))
        expect(page_open.get_by_role("button", name="Register")).to_be_visible()

        # # Вызываем handle_dialog с действием, которое вызывает alert
        # text = handle_dialog(
        #     page_open,
        #     action=lambda: page_open.get_by_role("button", name="Register").click(),
        #     expected_text="User register successfully",
        #     accept=True
        # )
        #
        # # дополнительная проверка
        # assert "User register successfully" in text

        # Кликаем кнопку Register
        page_open.get_by_role("button", name="Register").click()

        # Обрабатываем HTML-модалку
        text = handle_html_modal(
            page_open,
            modal_selector=".modal-content",  # пример селектора модалки
            ok_button_selector="button:has-text('OK')",  # кнопка ОК внутри модалки
            expected_text="User register successfully"
        )

        # Дополнительная проверка
        assert "User register successfully" in text

        # Перехватываем системное alert (JavaScript) с одной кнопкой
        # Вызов функции для перехвата и возврата текста до нажатия кнопки регистрации
        # dialog_text = catch_dialog(page_open)
        # Подключаем обработчик диалога
        # вызывать handle_dialog с действием, которое триггерит окно
        # text = handle_dialog(
        #     page_open,
        #     action=lambda: page_open.get_by_role("button", name="Register").click(),
        #     expected_text="User register successfully",
        #     accept=True
        # )

        # дополнительная проверка (если нужно)
        # assert "User register successfully" in text

        # with page_open.expect_dialog() as dialog_info:
        #     # используйте корректный селектор здесь
        #     page_open.get_by_role("button", name="Register").click()
        #
        # dialog = dialog_info.value
        # print("Текст диалога:", dialog.message)
        # assert "User register successfully" in dialog.message
        # dialog.accept()

        # dialog_text = handle_dialog(page_open, accept=True)
        # debug(text, "Повідомлення про успішну реєстрацію")
        # if text != "":
        #     debug(dialog_text, "Повідомлення про успішну реєстрацію")
        # else:
        #     exist = page_open.get_by_text("User exists!")
        #     expect(exist).to_be_visible(timeout=1000)

        # page_open.get_by_role("button", name="Register").click()
        # assert "User register successfully" in dialog_text.get("text", "")
        # exist = page_open.get_by_text("User exists!")
        # fail_on_alert(page_open)
        # if page_open.get_by_role("alert").locator("div").first.is_visible(timeout=2000):
        #     debug("Помилка створення екаунту", "ПОМИЛКА")

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





