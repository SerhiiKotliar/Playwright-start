import pytest
# from selenium import webdriver
from main import get_user_input
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright


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

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Add Chromium flag for always on top
    return {
        **browser_type_launch_args,
        "args": ["--always-on-top"]
    }

@pytest.fixture(scope="function")
def page_open(page: Page, user_data):
    page.goto(user_data['url'])
    return page