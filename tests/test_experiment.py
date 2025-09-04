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
    page_open.locator("div").filter(has_text=re.compile(r"^Elements$")).first.click()
    page_open.get_by_text("Book Store Application").click()
    page_open.get_by_role("listitem").filter(has_text="Login").click()
    page_open.get_by_role("button", name="New User").click()
    page_open.get_by_role("textbox", name="First Name").click()
    page_open.get_by_role("textbox", name="Last Name").click()
    page_open.get_by_role("textbox", name="UserName").click()
    page_open.get_by_role("textbox", name="Password").click()
    page_open.locator("iframe[name=\"a-yvxz48f9weee\"]").content_frame.get_by_role("checkbox",
                                                                              name="I'm not a robot").click()

    page_open.get_by_role("button", name="Register").click()

