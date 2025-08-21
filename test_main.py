import re
import pytest
from playwright.sync_api import Page, expect


def test_first(page: Page):
    page.goto('https://www.google.com/')
    expect(page).to_have_title('Google')
    mail_link = page.get_by_role('link', name='mail')
    expect(mail_link).to_have_attribute('href', 'https://mail.google.com/mail/&ogbl')
    input_field = page.locator('css=[name="q"]')
    input_field.fill('cat')
    search_button = page.locator('xpath=(//*[@name="btnK"])[2]')
    search_button.click()
    expect(page).to_have_title(re.compile('cat'))


@pytest.mark.skip('Site doesn\'t work')
def test_dynamic_props(page: Page):
    page.goto('https://demoqa.com/dynamic-properties')
    button = page.locator('#visibleAfter')
    button.click()
    page.screenshot(type='jpeg', path='/Users/eokulik/projects/playwright-start/shot.jpg')


def test_iframe(page: Page):
    page.goto('https://www.qa-practice.com/elements/iframe/iframe_page')
    toggler = page.frames[1].locator('css=.navbar-toggler-icon')
    toggler.click()
    page.screenshot(type='jpeg', path='/Users/eokulik/projects/playwright-start/toggler.jpg')


def test_drag(page: Page):
    page.goto('https://www.qa-practice.com/elements/dragndrop/boxes')
    page.drag_and_drop('#rect-draggable', '#rect-droppable')
    page.screenshot(type='jpeg', path='/Users/eokulik/projects/playwright-start/drag.jpg')


def test_select(page: Page):
    page.goto('https://www.qa-practice.com/elements/button/disabled')
    page.locator('#id_select_state').select_option('enabled')
    page.screenshot(type='jpeg', path='/Users/eokulik/projects/playwright-start/select.jpg')


def test_hover(page: Page):
    page.goto('https://magento.softwaretestingboard.com/')
    page.locator('#ui-id-4').hover()
    page.locator('#ui-id-9').hover()
    page.screenshot(type='jpeg', path='/Users/eokulik/projects/playwright-start/hover.jpg')
