import pytest
from playwright.sync_api import Page, expect
# import os
# from datetime import datetime
#
# from twisted.internet.defer import timeout

from conftest import user_data
from helper import debug
import allure
from main_file import report_about, report_bug_and_stop



@pytest.mark.timeout(10000)
@allure.story("створення екаунту на сайті https://magento.softwaretestingboard.com/")
def test_creat_account(page_open, user_data):
    # page.goto('https://magento.softwaretestingboard.com/')
    with allure.step('перехід на посилання створення екаунту та клік на ньому'):
        # page.goto("https://magento.softwaretestingboard.com/")
        # Перевірка наявності по тексту
        # expect(page_open.get_by_text("Create an Account")).to_be_visible(timeout=30000)
        expect(page_open.get_by_role("link", name="Create an Account")).to_be_visible(timeout=40000)
        debug("перехід на посилання створення екаунту", "Посилання створення екаунту")
        # page_open.get_by_text("Create an Account").click()
        page_open.get_by_role("link", name="Create an Account").click()
        # page_open.get_by_text("Create New Customer Account").click()
        debug("клік на посиланні створення екаунту", "Посилання створення екаунту")
    with allure.step('перевірка заголовку, чи це сторінка створення екаунту'):
        expect(page_open.get_by_role("heading")).to_contain_text("Create New Customer Account", timeout=40000)
        debug("здійснено перехід на сторінку створення екаунту", "Сторінка створення екаунту")
    with allure.step('пошук і перехід на поле імені та введення його'):
        expect(page_open.get_by_role("textbox", name="First Name*")).to_be_visible()
        debug("знайдено поле імені", "Поле імені")
        page_open.get_by_role("textbox", name="First Name*").fill(user_data['login'])
        # page_open.get_by_role("textbox", name="First Name*").fill('Serhii1')
        debug("введені дані в поле імені", "Поле імені")
    with allure.step('пошук і перехід на поле прізвища та введення його'):
        expect(page_open.get_by_role("textbox", name="Last Name*")).to_be_visible()
        debug("знайдено поле прізвища", "Поле прізвища")
        page_open.get_by_role("textbox", name="Last Name*").fill(user_data['login_l'])
        # page_open.get_by_role("textbox", name="Last Name*").fill('Kotliar1')
        debug("введені дані в поле прізвища", "Поле прізвища")
    with allure.step('пошук і перехід на поле email та введення його'):
        expect(page_open.get_by_role("textbox", name="Email*")).to_be_visible()
        debug("знайдене поле email", "Поле email")
        page_open.get_by_role("textbox", name="Email*").fill(user_data['email'])
        # page_open.get_by_role("textbox", name="Email*").fill('arecserg1@gmail.com')
        debug("введені дані в поле email", "Поле email")
    with allure.step('пошук і перехід на поле паролю та введення його'):
        expect(page_open.get_by_role("textbox", name="Password*", exact=True)).to_be_visible()
        debug("знайдене поле паролю", "Поле паролю")
        page_open.get_by_role("textbox", name="Password*", exact=True).fill(user_data['password'])
        # page_open.get_by_role("textbox", name="Password*", exact=True).fill('1980Pfgflyfz#1')
        debug("введені дані в поле паролю", "Поле паролю")
    with allure.step('пошук і перехід на поле підтвердження паролю та введення його'):
        expect(page_open.get_by_role("textbox", name="Confirm Password*")).to_be_visible()
        debug("знайдене поле підтвердження паролю", "Підтвердження паролю")
        page_open.get_by_role("textbox", name="Confirm Password*").fill(user_data['password'])
        # page_open.get_by_role("textbox", name="Confirm Password*").fill('1980Pfgflyfz#1')
        debug("введені дані в поле підтвердження паролю", "Підтвердження паролю")
    with allure.step('перевірка наявності кнопки підтвердження відкриття екаунту та клік на ній'):
        expect(page_open.get_by_role("button", name="Create an Account")).to_be_visible()
        debug("знайдена кнопка підтвердження створення екаунту", "Підтвердження створення екаунту")
        page_open.get_by_role("button", name="Create an Account").click()
        debug("зроблено клік на кнопці підтвердження створення екаунту", "Підтвердження створення екаунту")
    with allure.step('перевірка переходу на сторінку створенного екаунту'):
        # if page_open.get_by_role("heading", name="My Account").is_visible(timeout=30000):
        expect(page_open.get_by_role("heading", name="My Account")).to_be_visible(timeout=40000)
        debug("здійснено перехід на сторінку створеного екаунту", "Сторінка створеного екаунту")
        # else:
        #     debug("не здійснено перехід на сторінку створеного екаунту. такі дані екаунту вже є в базі", "Сторінка створеного екаунту")
        #     report_bug_and_stop("Екаунт з такими даними вже існує", page_open)
    with allure.step('перевірка співпадіння даних екаунту на сайті з введеними даними'):
        expect(page_open.get_by_text(f"{user_data['login']} {user_data['login_l']} {user_data['email']}")).to_be_visible()
        # expect(page_open.get_by_text("Serhii1 Kotliar1 arecserg1@gmail.com")).to_be_visible()
        debug("знайдено введені при створенні дані екаунту", "Дані екаунту")
        # expect(page_open.locator("#maincontent")).to_contain_text("Serhii1 Kotliar1 arecserg1@gmail.com")
        expect(page_open.locator("#maincontent")).to_contain_text(
            f"{user_data['login']} {user_data['login_l']} {user_data['email']}")
        # page_open.screenshot(type='jpeg', path='screenshots/Account.jpg')
        debug("дані екаунту співпадають з введеннми при створенні екаунту", "Дані екаунту")
        report_about("Створено екаунт за введеними даними, скріншот збережено", page_open)
        # debug("екаунт вже створено раніше з такими даними", "Дані екаунту")
