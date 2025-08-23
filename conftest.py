import pytest
# from selenium import webdriver
from main import get_user_input
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def user_data():
    """Фікстура, яка перед запуском тестів показує форму і повертає введені дані"""
    return get_user_input()

@pytest.fixture(scope="function")
def page_open(page: Page, user_data):
    page.goto(user_data['url'])
    return page