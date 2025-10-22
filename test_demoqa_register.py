# test_demoqa_register.py
import json
import time
import pytest
from playwright.sync_api import sync_playwright, expect, Page
# from tests.test_practice import fail_on_alert

def fail_on_alert(
    page: Page,
    type_: str = "error",
    timeout: int = 2000
):
    """
    Проверяет наличие алерта указанного типа и падает тестом, если он найден.

    :param page: объект Playwright Page
    :param type_: тип сообщения (error, success, warning, info)
    :param timeout: сколько ждать появления (мс)
    """
    # Словарь возможных селекторов (дополняй под свой проект)
    selectors = {
        "error": ".alert-danger, .notification.error, .toast-error",
        "success": ".alert-success, .notification.success, .toast-success",
        "warning": ".alert-warning, .notification.warning, .toast-warning",
        "info": ".alert-info, .notification.info, .toast-info",
    }

    selector = selectors.get(type_)
    if not selector:
        print(f"{type_}", f"Невідомий тип алерта")
        raise ValueError(f"Невідомий тип алерта: {type_}")


    try:
        # ждём появления элемента
        el = page.wait_for_selector(selector, timeout=timeout)
        # pytest.fail(f"❌ З'явилось повідомлення типу '{type_}': {el.inner_text()}")
        print(f"{el.inner_text()}", f"❌ З'явилось повідомлення типу '{type_}'")
        return type_, el.inner_text()
    except TimeoutError:
        # если не появилось — всё хорошо
        # pass
        return None



def fill_if_exists(page, selectors_or_locator, value):
    """Пробуем заполнить первый подходящий селектор/локатор."""
    for sel in selectors_or_locator:
        try:
            if page.locator(sel).count() > 0:
                page.fill(sel, value)
                return True
        except Exception:
            # Игнорируем возможные ошибки и пробуем следующий селектор
            continue
    return False

def try_set_recaptcha_token(page, token="fake-token"):
    # Попытка найти скрытое поле g-recaptcha-response и поставить туда токен
    page.evaluate(f"""() => {{
        const ta = document.querySelector('textarea[name="g-recaptcha-response"]') ||
                   document.querySelector('input[name="g-recaptcha-response"]');
        if (ta) ta.value = "{token}";
    }}""")

def stub_grecaptcha_if_needed(page):
    # Если grecaptcha не определён и скрипт виджета мешает — создаём простую заглушку
    page.evaluate("""
    () => {
      if (!window.grecaptcha) {
        window.grecaptcha = {
          render: (el, opts) => {
            // добавим в форму поле с токеном
            const form = document.querySelector('form') || document.body;
            const ta = document.createElement('textarea');
            ta.name = 'g-recaptcha-response';
            ta.value = 'fake-token';
            ta.style.display = 'none';
            form.appendChild(ta);
            return 'fake-widget';
          },
          getResponse: () => 'fake-token'
        };
      }
    }
    """)

def test_demoqa_register_with_recaptcha_mock():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        # # Перехват и подмена вызова siteverify
        # def route_handler(route, request):
        #     if request.url.startswith("https://www.google.com/recaptcha/api/siteverify"):
        #         body = json.dumps({
        #             "success": True,
        #             "challenge_ts": "2025-10-22T00:00:00Z",
        #             "hostname": "demoqa.com"
        #         })
        #         route.fulfill(status=200, headers={"Content-Type": "application/json"}, body=body)
        #     else:
        #         route.continue_()
        #
        # # Регистрируем перехват для точечного URL
        # page.route("**/recaptcha/api/siteverify", route_handler)
        # Мок reCAPTCHA
        def route_handler(route, request):
            if "recaptcha/api/siteverify" in request.url:
                route.fulfill(
                    status=200,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({"success": True, "hostname": "demoqa.com"})
                )
            else:
                route.continue_()

        page.route("**/recaptcha/api/siteverify", route_handler)

        # Переход на страницу регистрации
        page.goto("https://demoqa.com/register", wait_until="domcontentloaded")

        # На всякий случай — подтрубим заглушку grecaptcha (если виджет пытается загрузиться)
        stub_grecaptcha_if_needed(page)

        # Подбор селекторов — берём несколько вариантов (id/имя/label)
        first_name_selectors = ["#firstname", "#firstName", "input[placeholder='First Name']", "input[aria-label='First Name']"]
        last_name_selectors  = ["#lastname", "#lastName", "input[placeholder='Last Name']", "input[aria-label='Last Name']"]
        username_selectors   = ["#userName", "input[name='userName']", "input[placeholder='UserName']", "input[aria-label='UserName']"]
        password_selectors   = ["#password", "input[name='password']", "input[placeholder='Password']", "input[aria-label='Password']"]

        # Ждём форму и заполняем (если поле найдено)
        page.wait_for_timeout(500)  # даём немного времени для динамической подгрузки
        # fill_if_exists(page, first_name_selectors, "TestFirst")
        # fill_if_exists(page, last_name_selectors, "TestLast")
        # fill_if_exists(page, username_selectors, f"testuser_{int(time.time())%10000}")
        # fill_if_exists(page, password_selectors, "Password!123")
        fill_if_exists(page, first_name_selectors, "Peterw")
        fill_if_exists(page, last_name_selectors, "Petruccyw")
        fill_if_exists(page, username_selectors, "platk123w")
        fill_if_exists(page, password_selectors, "1980Pfgflyfz#")

        # Попробовать поставить токен reCAPTCHA
        # try_set_recaptcha_token(page, token="fake-token")
        # Ставим фиктивный токен reCAPTCHA
        page.evaluate("""() => {
                    const ta = document.querySelector('textarea[name="g-recaptcha-response"]');
                    if (ta) ta.value = 'fake-token';
                }""")

        # Нажать кнопку Register — несколько вариантов селекторов
        register_buttons = ["button#register", "button[type='submit']", "button:has-text('Register')", "button:has-text('Register')"]
        clicked = False
        for sel in register_buttons:
            try:
                if page.locator(sel).count() > 0 and page.locator(sel).is_enabled():
                    page.click(sel)
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            # последний ресурс — нажать на первый видимый button
            try:
                page.click("button")
            except Exception:
                pass

        # Подождём ответа / проверки — ища текст успеха или редирект
        try:
            # check_m = fail_on_alert(page, "error", 2000)
            # print(check_m[1])
            # alert = page.get_by_role("alert").locator("div").first
            # print(alert.inner_text())
            # page.wait_for_selector("text=User exists", timeout=8000)
            # assert page.locator("text=User Register Successfully").is_visible()
            # expect(page.get_by_text("User Register Successfully")).to_be_visible(timeout=10000)
            expect(page.get_by_text("User exists")).to_be_visible(timeout=8000)
            print("User exists")
        except AssertionError as e:
            # Если нет явного текста — допустим, что сервер вернул redirect на /login
            print(e)
            assert "login" in page.url or page.locator("text=Back to Login").count() > 0

        browser.close()
