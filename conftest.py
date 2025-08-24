import pytest
# from selenium import webdriver
from main import get_user_input
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
# from playwright.async_api import async_playwright

@pytest.fixture(scope="session")
def user_data():
        """Фікстура, яка перед запуском тестів показує форму і повертає введені дані"""
        return get_user_input()

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

# @pytest.fixture(scope="function")
# def page_open(user_data, browser):
#     page = browser.new_page()
#     page.goto(user_data['url'])
#     # page.goto(get_user_input['url'])
#     return page


@pytest.fixture()
def page_open(page: Page, user_data):
    page.goto(user_data['url'])
    return page

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