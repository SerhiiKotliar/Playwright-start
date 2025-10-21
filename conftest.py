import pytest
import shutil
import  os
# from main_file import get_user_input
from Rule_form_new import get_user_input
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

@pytest.fixture(scope='session')
def user_data():
    # debug("Фикстура user_data запускается", "FIXTURE")

    # debug("Форма откроется сейчас", "FIXTURE")
    result, result_inv, result_tit_f = get_user_input()  # открытие формы

    debug(f"Дані для тестів отримані: {result}\n{result_inv}\n{result_tit_f}", "FIXTURE")
    return result, result_inv, result_tit_f  # возвращаем введённые данные

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
    page.goto(user_data[0]['url'], timeout=6000, wait_until="domcontentloaded")
    return page
#, wait_until="commit"

@pytest.fixture(scope="session", autouse=True)
def clear_allure_results():
    allure_dir = "result"
    if os.path.exists(allure_dir):
        shutil.rmtree(allure_dir)
    os.makedirs(allure_dir)
    print(f"\n✅ Очищена директорія: {allure_dir}")
    allure_dir = "screenshots"
    if os.path.exists(allure_dir):
        shutil.rmtree(allure_dir)
    os.makedirs(allure_dir)
    print(f"\n✅ Очищена директорія: {allure_dir}")
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