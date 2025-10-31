from playwright.sync_api import expect
from conftest import page_open
from helper import debug
from typing import Callable, Pattern, Union, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import re
from datetime import datetime


"""Специфчні функції для конкретних виипадків тестування"""

URLMatcher = Union[str, Pattern[str], Callable[[str], bool]]

# функція очикування переходу на іншу сторінку
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
        page.wait_for_url(matcher, timeout=timeout, wait_until="domcontentloaded")
        return page.url != old, page.url
    except PlaywrightTimeoutError:
        return False, page.url


# функція переходу з головної сторінки на цільову для реєстрації
def enter_to_fieldspage(page_open: Page) -> Page:
    # ## https: // www.qa - practice.com /
    # ## перехід на сторінку, де заповнюються поля
    # expect(page_open.get_by_role("link", name="Text input")).to_be_visible()
    # debug("знайдено посилання Text input", "Перевірка наявності посилання Text input")
    # link_input = page_open.get_by_role("link", name="Text input")
    #
    # changed, new_url = click_and_wait_url_change(page_open, lambda: link_input.click())
    #
    # debug("здійснено клік на посиланні Text input", "Перехід на сторінку елементів введення даних")
    # assert changed, "Не відкрилась сторінка елементів введення даних"
    # debug("відкрилась сторінка елементів введення даних", "Перехід на сторінку елементів введення даних")
    # expect(page_open.get_by_role("heading", name="Input field")).to_be_visible()
    # debug("знайдено заголовок Input field", "Перевірка наявності заголовка Input field")
    # expect(page_open.get_by_role("link", name="Text input")).to_be_visible()
    # debug("знайдено посилання Text input", "Перевірка наявності посилання Text input")

    #
    ### http://127.0.0.1:5000/")
    expect(page_open.get_by_role("link", name="Register")).to_be_visible()
    debug("знайдено посилання Register", "Перевірка наявності посилання Regiser")
    link_input = page_open.get_by_role("link", name="Register")

    changed, new_url = click_and_wait_url_change(page_open, lambda: link_input.click())

    debug("здійснено клік на посиланні Register", "Перехід на сторінку реєстрації користувача")
    assert changed, "Не відкрилась сторінка реєстрації користувача"

    expect(page_open.get_by_role("heading", name="Register")).to_be_visible()
    debug("здійснено перехід на сторінку", "Перехід на сторінку реєстрації користувача")

    return page_open
# функція переходу з головної сторінки на цільову для входу
def enter_to_fieldspage_login(page_open: Page) -> Page:
    ### http://127.0.0.1:5000/")

    ### http://127.0.0.1:5000/")
    expect(page_open.get_by_role("link", name="Login")).to_be_visible()
    debug("знайдено посилання Login", "Перевірка наявності посилання Login")
    link_input = page_open.get_by_role("link", name="Login")

    changed, new_url = click_and_wait_url_change(page_open, lambda: link_input.click())

    debug("здійснено клік на посиланні Login", "Перехід на сторінку входу користувача на сайт")
    assert changed, "Не відкрилась сторінка входу користувача на сайт"

    expect(page_open.get_by_role("heading", name="Login")).to_be_visible()
    debug("здійснено перехід на сторінку", "Перехід на сторінку входу користувача на сайт")

    return page_open

# фнкція підтвердження введених даних в усі поля без впливу якогось елементу HTML
def confirmation(page_open: Page, value, field):
    expect(page_open.get_by_text(f"Your input was: {value}")).to_be_visible()
    debug(f"Підтверджене введення {value}", f"{field}")


# функція дій після введення даних в усі поля
def after_fill_fields(page_open: Page, el: str == '', txt: str == '', last_field) -> bool:
    safe_field = re.sub(r'[\\/*?:"<>| ]', "", last_field)
    # є елемент HTML для впливу піля ввдення даних
    if el != '':
        lo_reg = page_open.get_by_role(el, name=txt)
        changed, new_url = click_and_wait_url_change(page_open, lambda: lo_reg.click())
        debug(f"здійснено клік на кнопці {txt}", f"Перехід на сторінку після кліку на кнопці {txt}")
    if not changed:
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
    else:
        loc_txt_reg = page_open.get_by_text(re.compile(r"^(Welcome, .*|Congradulation.*)"))
        if loc_txt_reg.count() > 0:
            expect(loc_txt_reg).to_be_visible()
            debug("Підтверджено привітання користувача", "Вхід у профіль")
            # Скриншот страницы
            now = datetime.now()
            screenshot = page_open.screenshot()
            page_open.screenshot(type='png',
                                 path=f'screenshots/positiv_reestr_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png")
            debug(
                f'Скриншот сторінки привітання після заповнення полів positiv_reestr_{safe_field}_{now.strftime("%d-%m-%Y %H-%M-%S")}' + f"-{now.microsecond}.png",
                "Скрін сторінки", screenshot)
        else:
            debug(f"Вхід у профіль відхилено з невідомих причин", "Вхід у профіль")
            raise AssertionError(
                f"{loc_txt_reg.inner_text()}\nЗ невідомих причин не відкрилась сторінка входу у профіль користувача")


# функція переходу на головну сторінку (виходу)
def out_from_register(page_open: Page) -> bool:
    ### http://127.0.0.1:5000/")

    expect(page_open.get_by_role("link", name="Logout")).to_be_visible()
    debug("знайдено посилання Logout", "Перевірка наявності посилання Logout")
    link_output = page_open.get_by_role("link", name="Logout")

    changed, new_url = click_and_wait_url_change(page_open, lambda: link_output.click())

    debug("здійснено клік на посиланні Logout", "Перехід на головну сторінку сайту")
    assert changed, "Не відкрилась головна сторінка сайту"
    expect(page_open.get_by_role("link", name="Register")).to_be_visible()
    debug("Головна сторінка. Знайдено посилання Register", "Перевірка повертання на головну сторінку")

    return  changed
