from playwright.sync_api import expect
from conftest import page_open
from helper import debug
from typing import Callable, Pattern, Union, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import re


"""Специфчні функції для конкретних виипадків тестування"""

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
        page.wait_for_url(matcher, timeout=timeout, wait_until="domcontentloaded")
        return page.url != old, page.url
    except PlaywrightTimeoutError:
        return False, page.url



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


    ### http://127.0.0.1:5000/")
    expect(page_open.get_by_role("link", name="Register")).to_be_visible()
    debug("знайдено посилання Register", "Перевірка наявності посилання Regiser")
    link_input = page_open.get_by_role("link", name="Register")

    changed, new_url = click_and_wait_url_change(page_open, lambda: link_input.click())

    debug("здійснено клік на посиланні Register", "Перехід на сторінку реєстрації користувача")
    assert changed, "Не відкрилась сторінка реєстрації користувача"

    expect(page_open.get_by_role("heading", name="Register")).to_be_visible()
    debug("здійснено перехід на сторінку", "Перехід на сторінку реєстрації користувача")


    # expect(page_open.get_by_role("link", name="Login")).to_be_visible()
    # expect(page_open.get_by_role("heading", name="Register")).to_be_visible()
    # expect(page_open.get_by_role("button", name="Register")).to_be_visible()
    # expect(page_open.get_by_role("textbox", name="Username")).to_be_visible()
    # expect(page_open.get_by_role("textbox", name="Password")).to_be_visible()
    # expect(page_open.get_by_text("Invalid username or password")).to_be_visible()
    # expect(page_open.get_by_role("heading", name="Profile")).to_be_visible()
    # expect(page_open.get_by_role("link", name="Logout")).to_be_visible()
    # expect(page_open.get_by_role("heading", name="Register")).to_be_visible()
    # expect(page_open.get_by_text("Invalid username (4-12")).to_be_visible()
    # expect(page_open.get_by_text("Invalid password (min 8 chars")).to_be_visible()

    return page_open

def confirmation(page_open: Page, value, field):
    expect(page_open.get_by_text(f"Your input was: {value}")).to_be_visible()
    debug(f"Підтверджене валідне введення {value}", f"{field}")

def after_fill_fields(page_open: Page, el: str == '', txt: str == '') -> bool:
    if el != '':
        lo_reg = page_open.get_by_role(el, name=txt)
        changed, new_url = click_and_wait_url_change(page_open, lambda: lo_reg.click())
        debug(f"здійснено клік на кнопці {txt}", f"Перехід на сторінку після кліку на кнопці {txt}")
        return changed