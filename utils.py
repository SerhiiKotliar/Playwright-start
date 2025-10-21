from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

def checking_for_errors(page_open: Page, tag: str):
    # locator = page_open.locator('//*[@id="error_1_id_text_string"]')
    locator = page_open.locator(tag)
    try:
        locator.wait_for(state="visible", timeout=2000)
        # Если элемент появился — тогда проверяем
        if locator.count() > 0 and locator.is_visible():
            text_err = locator.inner_text()
            return locator, text_err
    except PlaywrightTimeoutError:
            # Элемент не появился — просто пропускаем
        return None