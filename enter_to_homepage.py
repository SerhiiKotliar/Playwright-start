from playwright.sync_api import expect
from conftest import page_open
from helper import debug
from typing import Callable, Pattern, Union, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


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



def enter_to_fieldspage(page_open: Page) -> Page:
    # перехід на сторінку, де заповнюються поля
    expect(page_open.get_by_role("link", name="Text input")).to_be_visible()
    debug("знайдено посилання Text input", "Перевірка наявності посилання Text input")
    link_input = page_open.get_by_role("link", name="Text input")

    changed, new_url = click_and_wait_url_change(page_open, lambda: link_input.click())

    debug("здійснено клік на посиланні Text input", "Перехід на сторінку елементів введення даних")
    assert changed, "Не відкрилась сторінка елементів введення даних"
    debug("відкрилась сторінка елементів введення даних", "Перехід на сторінку елементів введення даних")
    expect(page_open.get_by_role("heading", name="Input field")).to_be_visible()
    debug("знайдено заголовок Input field", "Перевірка наявності заголовка Input field")
    expect(page_open.get_by_role("link", name="Text input")).to_be_visible()
    debug("знайдено посилання Text input", "Перевірка наявності посилання Text input")
    return page_open

def confirmation(page_open: Page, value, field):
    expect(page_open.get_by_text(f"Your input was: {value}")).to_be_visible()
    debug(f"Підтверджене валідне введення {value}", f"{field}")

def after_fill_fields(page_open: Page):
    return  True