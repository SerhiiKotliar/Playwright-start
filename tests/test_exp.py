import allure
import pytest
from playwright.sync_api import expect

# from conftest import user_data
from helper import debug

names_fields = ["First Name*", "Last Name*", "Email*", "Password*", "Confirm Password*"]
names_data_for_fields = {"First Name*": "login", "Last Name*": "login_l", "Email*": "email", "Password*": "password", "Confirm Password*": "password"}
@allure.title("Позитивні та негативні тести: поле 'First Name*' відображається")
@pytest.mark.parametrize("scenario, expected_result", [
    ("valid", "PASS"),
    ("no_valid", "FAIL"),
    #("hidden", "FAIL"),
])
def test_first_name_field(page_open, scenario, expected_result, user_data):
    if scenario == "valid":
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
                debug("Виявлено рекламу google_vignette. Повертаємось назад...", "WARNING")
                page_open.go_back()
                expect(link).to_be_visible(timeout=20000)
                link.click()
                debug("повторний клік після реклами", "INFO")
            # close_button = page_open.locator("text=Close").first
            close_button = page_open.get_by_role("button", name="Close").first
            if close_button.is_visible():
                close_button.click()
        with allure.step('перевірка заголовку, чи це сторінка створення екаунту'):
            # page_cr_ac = page_open.get_by_role("heading", name="Create New Customer Account")
            expect(page_open.get_by_role("heading")).to_contain_text("Create New Customer Account", timeout=40000)
            debug("здійснено перехід на сторінку створення екаунту", "Сторінка створення екаунту")
        for cur_name in names_fields:
            allure.dynamic.title(f"Позитивний тест: поле {cur_name} відображається → {expected_result}")
            with allure.step(f"пошук і перехід на поле {cur_name}"):
                tb = page_open.get_by_role("textbox", name=cur_name, exact=True)
                expect(tb).to_be_visible()
                tb.fill(user_data[0][names_data_for_fields[cur_name]])
                debug(f"знайдено та заповнено поле {cur_name}", f"{cur_name}")

    # elif scenario == "no_valid":
    #     allure.dynamic.title(f"Негативний тест: поле 'First Name*' відображається → {expected_result}")
    #     with allure.step("перевірка реакції елемента поля імені на введення невалідних даних"):
    #         # expect(page_open.get_by_role("textbox", name="First Name*")).to_have_count(0)
    #         # expect(page_open.get_by_role("textbox", name="First Name*")).to_have_count(0)
    #         # debug("поле імені відсутнє у DOM", "Поле імені")
    #         for us_dat_inv in user_data[1]['login']:
    #             if us_dat_inv == 'absent':
    #                 locator_login = page_open.get_by_role("textbox", name="First Name*")
    #                 validate_attr = locator_login.get_attribute("data-validate")
    #                 if validate_attr == "{required:true}":
    #                     debug("поле обов'язкове, але перевіряється після Submit у формі", "Поле імені")
    #                 else:
    #                     # Проверяем, есть ли сообщение об ошибке
    #                     error = page_open.locator("#firstname-error")
    #                     expect(error).to_be_visible()
    #                     debug("з'явилась помилка на введення пустоти", "Поле імені")





            # page_open.get_by_role("textbox", name="First Name*").fill(user_data[1]['login'])

    # elif scenario == "hidden":
    #     allure.dynamic.title(f"Негативний тест: поле 'First Name*' приховане → {expected_result}")
    #     with allure.step("перевірка що поле імені приховане"):
    #         expect(page_open.get_by_role("textbox", name="First Name*")).to_be_hidden()
    #         # expect(page_cr_ac.get_by_role("textbox", name="First Name*")).to_be_hidden()
    #         debug("поле імені є у DOM, але приховане", "Поле імені")

