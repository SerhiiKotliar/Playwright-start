import allure
import pytest
from playwright.sync_api import expect

# from conftest import user_data
from helper import debug

names_fields = ["First Name*", "Last Name*", "Email*", "Password*", "Confirm Password*"]
names_data_for_fields = {"First Name*": "login", "Last Name*": "login_l", "Email*": "email", "Password*": "password", "Confirm Password*": "password"}
@allure.title("Позитивні та негативні тести: поля відображаються")
@pytest.mark.parametrize("scenario, expected_result", [
    ("valid", "PASS"),
    ("no_valid", "FAIL"),
    #("hidden", "FAIL"),
])
def test_first_name_field(page_open, scenario, expected_result, user_data):
    #
    # if scenario == "valid":
    #     with allure.step('перехід на посилання створення екаунту та клік на ньому'):
    #         link = page_open.get_by_role("link", name="Create an Account")
    #         expect(link).to_be_visible(timeout=40000)
    #         debug("\n", "")
    #         debug("здійснено перехід на посилання створення екаунту", "Посилання створення екаунту")
    #         link.click()
    #         debug("здійснено клік на посиланні створення екаунту", "Посилання створення екаунту")
    #         # --- обхід реклами ---
    #         # Проверяем и закрываем рекламу
    #         # Если попали на рекламу — возвращаемся назад
    #         if "google_vignette" in page_open.url or "ad.doubleclick" in page_open.url:
    #             debug("Виявлено рекламу google_vignette. Повертаємось назад...", "WARNING")
    #             page_open.go_back()
    #             expect(link).to_be_visible(timeout=20000)
    #             link.click()
    #             debug("повторний клік після реклами", "INFO")
    #         # якщо реклама з кнопкою Close (найчастіше це перша кнопка з декількох таких)
    #         close_button = page_open.get_by_role("button", name="Close").first
    #         if close_button.is_visible():
    #             close_button.click()
    #     with allure.step('перевірка заголовку, чи це сторінка створення екаунту'):
    #         expect(page_open.get_by_role("heading")).to_contain_text("Create New Customer Account", timeout=40000)
    #         debug("здійснено перехід на сторінку створення екаунту", "Сторінка створення екаунту")
    #     for cur_name in names_fields:
    #         allure.dynamic.title(f"Позитивний тест: поле {cur_name} відображається → {expected_result}")
    #         with allure.step(f"пошук і перехід на поле {cur_name}"):
    #             tb = page_open.get_by_role("textbox", name=cur_name, exact=True)
    #             expect(tb).to_be_visible()
    #             tb.fill(user_data[0][names_data_for_fields[cur_name]])
    #             debug(f"знайдено та заповнено поле {cur_name}", f"{cur_name}")
    #     with allure.step('перехід на кнопку створення екаунту та клік на ній'):
    #         btnS = page_open.get_by_role("button", name="Create an Account")
    #         expect(btnS).to_be_visible(timeout=10000)
    #         debug("здійснено перехід на кнопку створення екаунту", "Кнопка створення екаунту")
    #         btnS.click()
    #         debug("здійснено клік на кнопку створення екаунту", "Кнопка створення екаунту")
    #
    #         try:
    #             # Проверяем переход на страницу My Account
    #             expect(page_open.locator("h1")).to_contain_text("My Account", timeout=40000)
    #             debug("здійснено перехід на сторінку зареєстрованого екаунту", "Сторінка екаунту")
    #
    #             # Проверяем, что есть блок с інформацією про акаунт
    #             if page_open.get_by_role("strong").filter(has_text="Account Information").is_visible():
    #                 debug("знайдено інформацію про екаунт", "Сторінка екаунту")
    #
    #                 account_text = page_open.locator("#maincontent").inner_text(timeout=5000)
    #                 expected_text = f"{user_data[0]['login']} {user_data[0]['login_l']}\n{user_data[0]['email']}"
    #
    #                 if expected_text in account_text:
    #                     debug("інформація про екаунт відповідає введеним даним", "Сторінка екаунту")
    #                 else:
    #                     debug("інформація про екаунт не відповідає введеним даним, потрібна повторна перевірка вводу",
    #                           "Сторінка екаунту")
    #                 debug(account_text, "Отриманий текст:")
    #                 debug(expected_text, "Очікуваний текст:")
    #             else:
    #                 debug("відсутня інформація про екаунт BUG", "Сторінка екаунту BUG")
    #
    #
    #         except AssertionError:
    #             # Если не удалось знайти "My Account"
    #             debug("екаунт не зареєстрований, переходу на сторінку екаунту не здійснено", "Реєстрація екаунту")
    #             debug(page_open.url, "Current URL:")
    #
    #             # Логируем ошибки формы
    #             errors = []
    #             for selector in [
    #                 "#firstname-error",
    #                 "#lastname-error",
    #                 "#email_address-error",
    #                 "#password-error",
    #                 "#password-confirmation-error",
    #             ]:
    #                 if page_open.locator(selector).is_visible():
    #                     errors.append(page_open.locator(selector).inner_text())
    #
    #             if page_open.get_by_role("alert").locator("div").first.is_visible():
    #                 errors.append(page_open.get_by_role("alert").locator("div").first.inner_text())
    #
    #             if errors:
    #                 debug("знайдено помилки при введенні даних", "Реєстрація екаунту")
    #                 debug(errors, "Errors found:")
    #             else:
    #                 debug("помилок не знайдено, але сторінка My Account не відкрита", "Реєстрація екаунту")
    #
    if scenario == "valid":
        try:
            with allure.step('Перехід на посилання створення екаунту та клік на ньому'):
                link = page_open.get_by_role("link", name="Create an Account")
                expect(link).to_be_visible(timeout=40000)
                debug("здійснено перехід на посилання створення екаунту", "Посилання створення екаунту")
                link.click()
                debug("здійснено клік на посиланні створення екаунту", "Посилання створення екаунту")

                # --- обхід реклами ---
                if "google_vignette" in page_open.url or "ad.doubleclick" in page_open.url:
                    debug("Виявлено рекламу google_vignette. Повертаємось назад...", "WARNING")
                    page_open.go_back()
                    expect(link).to_be_visible(timeout=20000)
                    link.click()
                    debug("повторний клік після реклами", "INFO")

                close_button = page_open.get_by_role("button", name="Close").first
                if close_button.is_visible():
                    close_button.click()

            with allure.step('Перевірка заголовку, чи це сторінка створення екаунту'):
                expect(page_open.get_by_role("heading")).to_contain_text(
                    "Create New Customer Account", timeout=40000
                )
                debug("здійснено перехід на сторінку створення екаунту", "Сторінка створення екаунту")

            for cur_name in names_fields:
                allure.dynamic.title(f"Позитивний тест: поле {cur_name} відображається → {expected_result}")
                with allure.step(f"Пошук і заповнення поля {cur_name}"):
                    tb = page_open.get_by_role("textbox", name=cur_name, exact=True)
                    expect(tb).to_be_visible()
                    tb.fill(user_data[0][names_data_for_fields[cur_name]])
                    debug(f"знайдено та заповнено поле {cur_name}", f"{cur_name}")

            with allure.step('Перехід на кнопку створення екаунту та клік на ній'):
                btnS = page_open.get_by_role("button", name="Create an Account")
                expect(btnS).to_be_visible(timeout=10000)
                debug("здійснено перехід на кнопку створення екаунту", "Кнопка створення екаунту")
                btnS.click()
                debug("здійснено клік на кнопку створення екаунту", "Кнопка створення екаунту")

            with allure.step('Перевірка переходу на сторінку My Account'):
                expect(page_open.locator("h1")).to_contain_text("My Account", timeout=40000)
                debug("здійснено перехід на сторінку зареєстрованого екаунту", "Сторінка екаунту")

                # Перевіряємо наявність інформації про акаунт
                assert page_open.get_by_role("strong").filter(has_text="Account Information").is_visible(), \
                    "BUG: Відсутня інформація про екаунт"

                account_text = page_open.locator("#maincontent").inner_text(timeout=5000)
                expected_text = f"{user_data[0]['login']} {user_data[0]['login_l']}\n{user_data[0]['email']}"

                assert expected_text in account_text, \
                    f"BUG: Інформація про екаунт не відповідає введеним даним"

                # --- debug для позитивного сценарію ---
                debug("інформація про екаунт відповідає введеним даним", "Сторінка екаунту")
                debug(account_text, "Отриманий текст:")
                debug(expected_text, "Очікуваний текст:")
            # Скриншот страницы
            screenshot = page_open.screenshot()
            allure.attach(
                screenshot,
                name=f"Скриншот останньої сторінки ({scenario})",
                attachment_type=allure.attachment_type.PNG
            )

        except AssertionError as e:
            debug("Тест провалено: позитивний сценарій не пройдено", "ERROR")
            debug(f"Current URL: {page_open.url}", "INFO")

            # Логування помилок форми
            errors = []
            for selector in [
                "#firstname-error",
                "#lastname-error",
                "#email_address-error",
                "#password-error",
                "#password-confirmation-error",
            ]:
                if page_open.locator(selector).is_visible():
                    errors.append(page_open.locator(selector).inner_text())

            alert = page_open.get_by_role("alert").locator("div").first
            if alert.is_visible():
                errors.append(alert.inner_text())

            if errors:
                debug("Знайдено помилки при введенні даних:", "ERROR")
                debug(errors, "Errors list:")
            # Скриншот страницы
            screenshot = page_open.screenshot()
            allure.attach(
                screenshot,
                name=f"Скриншот падіння або помилки ({scenario})",
                attachment_type=allure.attachment_type.PNG
            )

            # debug текущего текста страницы для анализа
            try:
                account_text = page_open.locator("#maincontent").inner_text(timeout=5000)
                debug(account_text, "Текст сторінки My Account (якщо є):")
            except:
                debug("Не вдалося отримати текст сторінки My Account", "INFO")

            # Сбрасываем AssertionError, чтобы тест упал и pytest зарегистрировал ошибку
            raise e

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

