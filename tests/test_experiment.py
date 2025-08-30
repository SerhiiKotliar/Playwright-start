import allure
import pytest
from playwright.sync_api import expect

from conftest import user_data
from helper import debug

@allure.title("Позитивний тест: поле 'First Name*' відображається")
@pytest.mark.parametrize("scenario", ["visible", "absent", "hidden"])
def test_first_name_field_visible(page_open, scenario, user_data):
    if scenario == "visible":
        # user_data = request.getfixturevalue("user_data")
        # используешь user_data только тут
        with allure.step('перехід на посилання створення екаунту та клік на ньому'):
            # Перевірка наявності по тексту
            # expect(page_open.get_by_text("Create an Account")).to_be_visible(timeout=30000)
            link = page_open.get_by_role("link", name="Create an Account")
            # expect(page_open.get_by_role("link", name="Create an Account")).to_be_visible(timeout=40000)
            expect(link).to_be_visible(timeout=40000)
            debug("перехід на посилання створення екаунту", "Посилання створення екаунту")
            # page_open.get_by_text("Create an Account").click()
            # page_open.get_by_role("link", name="Create an Account").click()
            link.click()
            # page_open.get_by_text("Create New Customer Account").click()
            debug("клік на посиланні створення екаунту", "Посилання створення екаунту")

            # --- обхід реклами ---
            # Проверяем и закрываем рекламу

            # Если попали на рекламу — возвращаемся назад
            if "google_vignette" in page_open.url or "ad.doubleclick" in page_open.url:
                page_open.go_back()
                expect(link).to_be_visible(timeout=20000)
                link.click()
            close_button = page_open.locator("text=Close").first
            if close_button.is_visible():
                close_button.click()
            # if page_open.locator("text=Close").is_visible():
            #     page_open.locator("text=Close").click()
            if "google_vignette" in page_open.url:
                debug("Виявлено рекламу google_vignette. Повертаємось назад...", "WARNING")
                page_open.go_back()
                expect(link).to_be_visible(timeout=20000)
                link.click()
                debug("повторний клік після реклами", "INFO")

        with allure.step('перевірка заголовку, чи це сторінка створення екаунту'):
            # page_cr_ac = page_open.get_by_role("heading", name="Create New Customer Account")
            expect(page_open.get_by_role("heading")).to_contain_text("Create New Customer Account", timeout=40000)
            debug("здійснено перехід на сторінку створення екаунту", "Сторінка створення екаунту")
    if scenario == "visible":
        allure.dynamic.title("Позитивний тест: поле 'First Name*' відображається")
        with allure.step("пошук і перехід на поле імені та введення його"):
            expect(page_open.get_by_role("textbox", name="First Name*")).to_be_visible()
            page_open.get_by_role("textbox", name="First Name*").fill(user_data['login'])
            debug("знайдено та заповнено поле імені", "Поле імені")

    elif scenario == "absent":
        allure.dynamic.title("Негативний тест: поле 'First Name*' відсутнє у DOM")
        with allure.step("перевірка відсутності елемента поля імені"):
            # expect(page_open.get_by_role("textbox", name="First Name*")).to_have_count(0)
            expect(page_open.get_by_role("textbox", name="First Name*")).to_have_count(0)
            debug("поле імені відсутнє у DOM", "Поле імені")

    elif scenario == "hidden":
        allure.dynamic.title("Негативний тест: поле 'First Name*' приховане")
        with allure.step("перевірка що поле імені приховане"):
            expect(page_open.get_by_role("textbox", name="First Name*")).to_be_hidden()
            # expect(page_cr_ac.get_by_role("textbox", name="First Name*")).to_be_hidden()
            debug("поле імені є у DOM, але приховане", "Поле імені")

