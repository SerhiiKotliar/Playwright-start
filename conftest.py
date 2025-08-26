import pytest

from main import get_user_input
from playwright.sync_api import Page
from helper import debug

# @pytest.fixture(scope='function')
# def user_data():
#         """Фікстура, яка перед запуском тестів показує форму і повертає введені дані"""
#         return get_user_input()

# @pytest.fixture(scope="function")
# def user_data():
#     data, root = get_user_input()
#     # Сохраняем root в data, чтобы можно было использовать при необходимости
#     data["_root"] = root
#     return data

@pytest.fixture(scope='function')
def user_data():
    # debug("Фикстура user_data запускается", "FIXTURE")

    # debug("Форма откроется сейчас", "FIXTURE")
    result = get_user_input()  # открытие формы

    debug(f"Дані для введення отримані: {result}", "FIXTURE")
    return result

# @pytest.fixture(scope="session")
# def browser():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         yield browser
#         browser.close()

# @pytest.fixture(scope="session")
# def browser_type_launch_args(browser_type_launch_args):
#     # Add Chromium flag for always on top
#     return {
#         **browser_type_launch_args,
#         "args": ["--always-on-top"]
#     }

# @pytest.fixture(scope="function", autouse=True)
# def page_open(page: Page, user_data, browser):
#     page = browser.new_page()
#     page.goto(user_data['url'])
#     # page.goto(get_user_input['url'])
#     return page


# @pytest.fixture(autouse=True, scope="function")
# def page_open(browser: Browser, user_data) -> Page:
#     # создаём новую вкладку (а не берём общую fixture page)
#     page = browser.new_page()
#     page.goto(user_data["url"])
#     yield page
#     page.close()


# @pytest.fixture(autouse=True, scope="function")
# def page(page: Page, user_data) -> Page:
#     # каждый тест начнёт с этого URL
#     page.goto(user_data["url"])
#     yield page
#     # можно очистить, если нужно
#     page.goto("about:blank")

@pytest.fixture(autouse=True, scope="function")
def page_open(page: Page, user_data):
    page.goto(user_data['url'])
    return page

# @pytest.fixture(autouse=True, scope="function")
# def page_open(page: Page, user_data):
#     page.goto(user_data["url"])
#     yield page   # важно: именно yield, а не return
#     # сюда можно добавить очистку после теста, если нужно
#     page.goto("about:blank")  # сбрасываем страницу
# фикстура, которая открывает браузер и страницу
# @pytest.fixture(scope="function")
# def page_open(user_data):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)  # headless=True, если нужно без UI
#         page = browser.new_page()
#         page.goto(user_data["url"])
#         yield page   # отдаем страницу в тест
#         browser.close()

# @pytest.fixture(scope="function")
# def page_open(user_data):
#      with async_playwright() as p:
#         browser = p.chromium.launch(headless=False)  # headless=True если без UI
#         page =  browser.new_page()
#          page.goto(user_data["url"])
#         yield page
#          browser.close()