from playwright.async_api import expect
from playwright.async_api import async_playwright
import re
import pytest


# @pytest.fixture(scope="session")
# def event_loop():
#     policy = asyncio.get_event_loop_policy()
#     loop = policy.new_event_loop()
#     yield loop
#     loop.close()

@pytest.mark.asyncio
async def test_first():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://www.google.com/')
        await expect(page).to_have_title('Google')
        mail_link = page.get_by_role('link', name='mail')
        await expect(mail_link).to_have_attribute('href', 'https://mail.google.com/mail/&ogbl')
        input_field = page.locator('css=[name="q"]')
        await input_field.fill('cat')
        search_button = page.locator('xpath=(//*[@name="btnK"])[2]')
        await search_button.click()
        await expect(page).to_have_title(re.compile('cat'))


@pytest.mark.asyncio
@pytest.mark.skip('Site doesn\'t work')
async def test_dynamic_props():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://demoqa.com/dynamic-properties')
        button = page.locator('#visibleAfter')
        await button.click()
        await page.screenshot(type='jpeg', path='/Users/eokulik/projects/playwright-start/shot.jpg')


@pytest.mark.asyncio
async def test_iframe():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://www.qa-practice.com/elements/iframe/iframe_page')
        toggler = page.frames[1].locator('css=.navbar-toggler-icon')
        await toggler.click()
        await page.screenshot(type='jpeg', path='/Users/eokulik/projects/playwright-start/toggler.jpg')


@pytest.mark.asyncio
async def test_drag():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://www.qa-practice.com/elements/dragndrop/boxes')
        await page.drag_and_drop('#rect-draggable', '#rect-droppable')
        await page.screenshot(type='jpeg', path='/Users/eokulik/projects/playwright-start/drag.jpg')


@pytest.mark.asyncio
async def test_select():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://www.qa-practice.com/elements/button/disabled')
        await page.locator('#id_select_state').select_option('enabled')
        await page.screenshot(type='jpeg', path='/Users/eokulik/projects/playwright-start/select.jpg')


@pytest.mark.asyncio
# async def test_hover():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch()
#         page = await browser.new_page()
#         await page.goto('https://magento.softwaretestingboard.com/')
#         await page.locator('#ui-id-4').hover()
#         await page.locator('#ui-id-9').hover()
#         await page.screenshot(type='jpeg', path='/Users/eokulik/projects/playwright-start/hover.jpg')
async def test_hover():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://magento.softwaretestingboard.com/')

        locator = page.locator('#ui-id-4')
        try:
            await locator.wait_for(state='visible', timeout=10000)  # ждём элемент до 10 секунд
            await locator.scroll_into_view_if_needed()
            await locator.hover()
        except TimeoutError:
            print("Элемент не найден или не видим")