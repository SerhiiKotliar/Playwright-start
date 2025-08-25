import re
import pytest
from playwright.sync_api import Page, expect

# pytestmark = pytest.mark.usefixtures("page_open")

# from conftest import page_open


# def test_first(page: Page, page_open):
    # page.goto('https://www.google.com/')
    # logo = page_open.locator("img.logo_image")  # знаходимо <img> з класом
    # expect(logo).to_be_visible()  # перевіряємо, що зображення видно
    # entrance = page_open.locator('xpath=(//*[@id="content"]/div/ol/li[5]/a)')
    # entrance.click()
    # choose = page_open.locator('xpath=(//*[@id="id_choose_language"]')




    # choose.click()
    # choose_lang = page_open.locator('xpath=(//*[@id="id_choose_language"]/option[2]')
    # expect(choose_lang).to_have_text('Python')
    # choose_lang.click()
    # submit = page_open.locator('xpath=(//*[@id="submit-id-submit"]')
    # submit.click()
    # expect(page_open).to_have_text('You selected Python')

    # expect(page_open.locator("site_header")).to_be_visible()
    # expect(page_open).to_have_title('Google')
    # mail_link = page.get_by_role('link', name='mail')
    # expect(mail_link).to_have_attribute('href', 'https://mail.google.com/mail/&ogbl')
    # input_field = page.locator('css=[name="q"]')
    # input_field.fill('cat')
    # search_button = page.locator('xpath=(//*[@name="btnK"])[2]')
    # search_button.click()
    # expect(page).to_have_title(re.compile('cat'))

def test_example(page: Page, page_open) -> None:
    logo = page_open.locator("img.logo_image")  # знаходимо <img> з класом
    expect(logo).to_be_visible()  # перевіряємо, що зображення видно
    expect(page_open.get_by_role("link", name="Select input")).to_be_visible()
    page_open.get_by_role("link", name="Select input").click()
    expect(page_open.get_by_label("Choose language*")).to_be_visible()
    page_open.get_by_label("Choose language*").select_option(label="Python")
    page_open.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("You selected Python")).to_be_visible()
    page.get_by_text("You selected Python").screenshot(path="screenshots/Python.png")



@pytest.mark.skip('Site doesn\'t work')
def test_dynamic_props(page: Page, page_open) -> None:
    # page.goto('https://demoqa.com/dynamic-properties')
    button = page_open.locator('#visibleAfter')
    button.click()
    page_open.screenshot(type='jpeg', path='screenshots/shot.jpg')


def test_iframe(page: Page, page_open):
    # page.goto('https://www.qa-practice.com/elements/iframe/iframe_page')
    toggler = page_open.frames[1].locator('css=.navbar-toggler-icon')
    toggler.click()
    page_open.screenshot(type='jpeg', path='screenshots/toggler.jpg')


def test_drag(page: Page, page_open):
    # page.goto('https://www.qa-practice.com/elements/dragndrop/boxes')
    page_open.drag_and_drop('#rect-draggable', '#rect-droppable')
    page_open.screenshot(type='jpeg', path='screenshots/drag.jpg')


def test_select(page: Page, page_open):
    # page.goto('https://www.qa-practice.com/elements/button/disabled')
    page_open.locator('#id_select_state').select_option('enabled')
    page_open.screenshot(type='jpeg', path='screenshots/select.jpg')


def test_hover(page: Page, page_open):
    # page.goto('https://magento.softwaretestingboard.com/')
    page_open.locator('#ui-id-4').hover()
    page_open.locator('#ui-id-9').hover()
    page.screenshot(type='jpeg', path='screenshots/hover.jpg')
