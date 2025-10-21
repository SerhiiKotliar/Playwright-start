from Rule_form_new import get_user_input as gui
# from conftest import user_data
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

# def get_user_data():
#     result, result_inv, result_tit_f = gui()
#     # debug(f"Дані для тестів отримані: {result}\n{result_inv}\n{result_tit_f}", "FIXTURE")
#     return result, result_inv, result_tit_f
#
# def fixing_fills():
#     res, res1, res2 = get_user_data()
#     return res['fix_enter']

def checking_for_errors(page_open: Page, tag: str):
    # locator = page_open.locator('//*[@id="error_1_id_text_string"]')
    locator = page_open.locator(tag)
    try:
        locator.wait_for(state="visible", timeout=2000)
        # Если элемент появился — тогда проверяем
        if locator.count() > 0 and locator.is_visible():
            # if locator.count() > 0 and locator.is_visible:
            text_err = locator.inner_text()
            return locator, text_err
    except PlaywrightTimeoutError:
            # Элемент не появился — просто пропускаем
        return None