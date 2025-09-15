import allure
import pytest
from playwright.sync_api import expect
from helper import debug
import re
from playwright.sync_api import Page, expect

# @allure.title("Позитивний тест: поле 'First Name*' відображається")
# @pytest.mark.parametrize("scenario, expected_result", [
#     ("visible", "PASS"),
#     ("absent", "FAIL"),
#     ("hidden", "FAIL"),
# ])
# def test_first_name_field(page_open, scenario, expected_result, user_data):
#     page_open.goto("https://demoqa.com/")
#     import re
#     from playwright.sync_api import Page, expect

def test_example(page_open: Page, user_data) -> None:
    # page_open.locator("div").filter(has_text=re.compile(r"^Elements$")).first.click()
    # page_open.get_by_text("Book Store Application").click()
    # page_open.get_by_role("listitem").filter(has_text="Login").click()


    expect(page_open.get_by_role("heading", name="Elements")).to_be_visible()
    page_open.get_by_role("heading", name="Elements").click()
    expect(page_open.get_by_text("Book Store Application")).to_be_visible()
    page_open.get_by_text("Book Store Application").click()
    expect(page_open.get_by_text("Login")).to_be_visible()
    page_open.get_by_text("Login").click()
    expect(page_open.get_by_role("heading", name="Login", exact=True)).to_be_visible()
    expect(page_open.get_by_role("button", name="New User")).to_be_visible()
    page_open.get_by_role("button", name="New User").click()
    expect(page_open.get_by_role("heading", name="Register", exact=True)).to_be_visible()

    # page_open.get_by_role("button", name="New User").click()
    page_open.get_by_role("textbox", name="First Name").fill(user_data[0]['login'])
    page_open.get_by_role("textbox", name="Last Name").fill(user_data[0]['login_l'])
    page_open.get_by_role("textbox", name="UserName").fill(user_data[0]['email'])
    page_open.get_by_role("textbox", name="Password").fill(user_data[0]['password'])
    # Перехватываем запрос к серверу reCAPTCHA и возвращаем успешный ответ
    page_open.route("https://www.google.com/recaptcha/api2/**", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"success": true}'
    ))
    # expect(page_open.locator("iframe[name=\"a-58bd9sn74qxo\"]").content_frame.locator(".rc-anchor-center-item").first).to_be_visible()
    # page_open.locator("iframe[name=\"a-58bd9sn74qxo\"]").content_frame.locator(".rc-anchor-center-item").first.click()
    expect(page_open.get_by_role("button", name="Register")).to_be_visible()
    page_open.get_by_role("button", name="Register").click()
    close_button = page_open.get_by_role("button", name="OK").first
    if close_button.is_visible():
        close_button.click()
        debug("Виявлено рекламу з кнопкою OK. Натиснуто на OK", "WARNING")




