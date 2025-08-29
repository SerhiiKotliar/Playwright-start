import pytest
from playwright.sync_api import Page, expect
import os
from datetime import datetime

from twisted.internet.defer import timeout

from conftest import user_data
from helper import debug
import allure

def report_bug_and_stop(message: str, page_open=None, name="screenshot_of_skip"):
    # додаємо повідомлення у Allure
    allure.attach(message, name="Причина зупинки", attachment_type=allure.attachment_type.TEXT)
    filename = ""
    if page_open:
        try:
            # створюємо папку screenshots (якщо немає)
            os.makedirs("screenshots", exist_ok=True)

            # унікальне ім’я файлу
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/{name}_{timestamp}.png"

            # робимо скріншот у файл
            page_open.screenshot(path=filename)

            # прикріплюємо цей файл у Allure
            allure.attach.file(
                filename,
                name=name,
                attachment_type=allure.attachment_type.PNG
            )

        except Exception as e:
            # якщо файл не вдалось зберегти — все одно прикріплюємо байти у Allure
            allure.attach(
                page_open.screenshot(),
                name=f"{name}_fallback",
                attachment_type=allure.attachment_type.PNG
            )
            print(f"[WARNING] Не вдалось записати файл {filename}: {e}")

    # зупиняємо тест
    pytest.fail(message, pytrace=False)

@pytest.mark.timeout(5000)
@allure.feature("тестування декількох сайтів")
@allure.story("перебіг функціональних елементів на сторінках сайту https://www.qa-practice.com/")
def test_example(page: Page, page_open) -> None:
    # 'https://www.qa-practice.com/'
    # debug(user_data['url'], "URL")  # сразу в консоль и в Allure
    with  allure.step("перехід на малюнок img.logo_image"):
        logo = page_open.locator("img.logo_image")  # знаходимо <img> з класом
        expect(logo).to_be_visible()  # перевіряємо, що зображення видно
        print('\n')
        debug("Видне шукане зображення", "Пошук зображення")
    with  allure.step("Перевірка видимісті посилання на вибір мов"):
        expect(page_open.get_by_role("link", name="Select input")).to_be_visible()
        debug("Видне шукане посилання", "Пошук посилання")
    with  allure.step("перехід до вибору мови і клік по ній та перевірка видимісті її"):
        page_open.get_by_role("link", name="Select input").click()
        expect(page.get_by_label("Choose language*")).to_be_visible()
        debug("Після кліку відкрився вибір", "Вибір мови")
    with  allure.step("вибір мови та натискання на кнопу, що підтверджує вибір"):
        page.get_by_label("Choose language*").select_option(label="Python")
        debug("Перехід на мітку Python для подальшого натискання на неї", "Вибір мови")
        page.get_by_role("button", name="Submit").click()
    with  allure.step("перевірка видимісті тексту вибраної мови, зберігання скріну малюнку, що підтверджує вибрану мову"):
        expect(page.get_by_text("You selected Python")).to_be_visible()
        debug("Після вибору мови та кліку видна вибрана мова", "Вибір мови")
        page.get_by_text("You selected Python").screenshot(path="../screenshots/Python.png")
        debug("Збережений скрін Python.png з вибраною мовою", "Скрін сторінки")

@pytest.mark.timeout(5000)
@pytest.mark.skip(reason="Поки не потрібен")
@allure.story("натискання кнопки на сайті https://demoqa.com/dynamic-properties")
def test_dynamic_props(page_open) -> None:
    # page.goto('https://demoqa.com/dynamic-properties')
    with  allure.step("перехід на кнопку"):
        button = page_open().locator('#visibleAfter')
        debug("Здійснено перехід на кнопку", "Клік на кнопці")
        button.click()
        debug("Клік на кнопці", "Клік на кнопці")
    with  allure.step("перевірка видимісті тексту вибраної мови, зберігання скріну малюнку, що підтверджує вибрану мову"):
        page_open.screenshot(type='jpeg', path='screenshots/shot.jpg')
        debug("Збережений скрін shot.jpg", "Скрін сторінки")
@pytest.mark.timeout(5000)
@allure.story("перехід і натискання рамки на сайті https://www.qa-practice.com/elements/iframe/iframe_page")
def test_iframe(page_open):
    # page.goto('https://www.qa-practice.com/elements/iframe/iframe_page')
    with  allure.step("перехід на рамку"):
        toggler = page_open.frames[1].locator('css=.navbar-toggler-icon')
        debug("Здійснено перехід на рамку", "Клік на рамці")
        toggler.click()
        debug("Здійснено клік на рамку", "Клік на рамці")
    with  allure.step("зберігання скріну малюнку toggler.jpg"):
        page_open.screenshot(type='jpeg', path='../screenshots/toggler.jpg')
        debug("Збережений скрін toggler.jpg", "Скрін сторінки")
@pytest.mark.timeout(5000)
@allure.story("перевірка перетаскування елементів на сайті https://www.qa-practice.com/elements/dragndrop/boxes")
def test_drag( page_open):
    # page.goto('https://www.qa-practice.com/elements/dragndrop/boxes')
    with  allure.step("перетаскування"):
        page_open.drag_and_drop('#rect-draggable', '#rect-droppable')
        debug("елемент перетягнуто", "Клік на рамці")
        page_open.screenshot(type='jpeg', path='../screenshots/drag.jpg')
        debug("Збережений скрін drag.jpg", "Скрін сторінки")

@pytest.mark.timeout(5000)
@allure.story("переведення елементу в інший стан вибором зі списку сайті https://www.qa-practice.com/elements/button/disabled")
def test_select(page_open):
    # page.goto('https://www.qa-practice.com/elements/button/disabled')
    with  allure.step("переведення вибором стану зі списку"):
        page_open.locator('#id_select_state').select_option('enabled')
        debug("вибран стан зі списку", "Зміна стану")
        page_open.screenshot(type='jpeg', path='../screenshots/select.jpg')
        debug("Збережений скрін select.jpg", "Скрін сторінки")
@pytest.mark.timeout(5000)
@pytest.mark.skip(reason="Поки не потрібен")
@allure.story("переведення миші по елементам спеціального сайту для автоматизації тестування сайті https://magento.softwaretestingboard.com/")
def test_hover(page_open):
    # page.goto('https://magento.softwaretestingboard.com/')
    with  allure.step("переведення миші по елементам"):
        page_open.locator('#ui-id-4').hover()
        debug("переведена на елемент ui-id-4", "Переведення миші")
        page_open.locator('#ui-id-9').hover()
        debug("переведена на елемент ui-id-9", "Переведення миші")
        page_open.screenshot(type='jpeg', path='../screenshots/hover.jpg')
        debug("Збережений скрін hover.jpg", "Скрін сторінки")

@pytest.mark.timeout(10000)
@allure.story("створення екаунту на сайті https://magento.softwaretestingboard.com/")
def test_creat_account(page_open, user_data):
    # page.goto('https://magento.softwaretestingboard.com/')
    with allure.step('перехід на посилання створення екаунту та клік на ньому'):
        # page.goto("https://magento.softwaretestingboard.com/")
        expect(page_open.get_by_role("link", name="Create an Account")).to_be_visible(timeout=10000)
        debug("перехід на посилання створення екаунту", "Посилання створення екаунту")
        page_open.get_by_role("link", name="Create an Account").click()
        # page_open.get_by_text("Create New Customer Account").click()
        debug("клік на посиланні створення екаунту", "Посилання створення екаунту")
    with allure.step('перевірка заголовку, чи це сторінка створення екаунту'):
        expect(page_open.get_by_role("heading")).to_contain_text("Create New Customer Account", timeout=10000)
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
        if page_open.get_by_role("heading", name="My Account").is_visible():
            debug("здійснено перехід на сторінку створеного екаунту", "Сторінка створеного екаунту")
        else:
            debug("не здійснено перехід на сторінку створеного екаунту. такі дані екаунту вже є в базі", "Сторінка створеного екаунту")
            report_bug_and_stop("Екаунт з такими даними вже існує", page_open)
    with allure.step('перевірка співпадіння даних екаунту на сайті з введеними даними'):
        expect(page_open.get_by_text(f"{user_data['login']} {user_data['login_l']} {user_data['email']}")).to_be_visible()
        # expect(page_open.get_by_text("Serhii1 Kotliar1 arecserg1@gmail.com")).to_be_visible()
        debug("знайдено введені при створенні дані екаунту", "Дані екаунту")
        # expect(page_open.locator("#maincontent")).to_contain_text("Serhii1 Kotliar1 arecserg1@gmail.com")
        expect(page_open.locator("#maincontent")).to_contain_text(
            f"{user_data['login']} {user_data['login_l']} {user_data['email']}")
        debug("дані екаунту співпадають з введеннми при створенні екаунту", "Дані екаунту")
        # debug("екаунт вже створено раніше з такими даними", "Дані екаунту")


