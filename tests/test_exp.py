import allure
import pytest
from playwright.sync_api import expect

from conftest import page_open
from main_file import report_about, report_bug_and_stop
# from conftest import user_data
from helper import debug
import re
names_fields = ["First Name*", "Last Name*", "Email*", "Password*", "Confirm Password*"]
names_data_for_fields = {"First Name*": "login", "Last Name*": "login_l", "Email*": "email", "Password*": "password", "Confirm Password*": "password"}

def in_inv(cur_name: str, el: str, user_data):
    # for el_t in user_data[1][cur_name]:
    #     for el in el_t:
    if el == 'absent':
        # tb.fill('')
        return  "", el
    elif el == 'url':
        # tb.fill(user_data[0]['url'])
        return user_data[0]['url'], el
    elif el[:3] == 'len':
        lminmax = el[4:]
        lmin = int(lminmax.split(" ", 1)[0])
        lmax = int(lminmax.split(" ", 1)[1])
        # tb.fill(user_data[0][cur_name] * 6[:(lmin - 2)])
        # tb.fill(user_data[0][cur_name] * 6[:(lmax + 2)])
        return user_data[0][names_data_for_fields[cur_name]] * 6[:(lmin - 2)] +" "+ user_data[0][names_data_for_fields[cur_name]] * 6[:(lmax + 2)], el
    elif el == 'no_email':
        # tb.fill(user_data[0]['email'])
        return user_data[0]['email'], el
    elif el == 'no_lower':
        # tb.fill(user_data[0][cur_name].upper())
        return user_data[0][names_data_for_fields[cur_name]].upper(), el
    elif el == 'no_upper':
        # tb.fill(user_data[0][cur_name].lower())
        return user_data[0][names_data_for_fields[cur_name]].lower(), el
    elif el == 'no_digit':
        res = re.sub(r"\d", "", el)
        # tb.fill(res + 'ab')
        return res + 'ab', el
    elif el == 'no_spec':
        res = "".join(ch for ch in el if ch.isalnum() or ch.isspace())
        # tb.fill(res + '1f')
        return res + '1f', el
    elif el == 'probel':
        # tb.fill(user_data[0][cur_name][:2] + ' ' + user_data[0][cur_name][2:])
        return user_data[0][names_data_for_fields[cur_name]][:2] + ' ' + user_data[0][names_data_for_fields[cur_name]][2:], el
    elif el == 'Cyrillic':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = dict(zip(en, ru))
        result1 = []
        for ch in el:
            low = ch.lower()
            if low in mapping:
                new_ch = mapping[low]
                # восстанавливаем регистр
                result1.append(new_ch.upper() if ch.isupper() else new_ch)
            else:
                result1.append(ch)
        # tb.fill("".join(result1))
        return "".join(result1), el
    elif el == 'latin':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = dict(zip(ru, en))
        result2 = []
        for ch in el:
            low = ch.lower()
            if low in mapping:
                new_ch = mapping[low]
                # восстанавливаем регистр
                result2.append(new_ch.upper() if ch.isupper() else new_ch)
            else:
                result2.append(ch)
        return "".join(result2), el
        # tb.fill("".join(result2))
    elif el == 'lowreglat':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = str.maketrans(ru + ru.lower(), en + en.lower())
        converted = el.translate(mapping)
        # tb.fill(converted)
        return converted, el
    elif el == 'upreglat':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = str.maketrans(ru + ru.upper(), en + en.upper())
        converted = el.translate(mapping)
        # tb.fill(converted)
        return converted, el
    elif el == 'lowregcyr':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = str.maketrans(en + en.lower(), ru + ru.lower())
        converted = el.translate(mapping)
        # tb.fill(converted)
        return converted, el
    elif el == 'upregcyr':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = str.maketrans(en + en.upper(), ru + ru.upper())
        converted = el.translate(mapping)
        # tb.fill(converted)
        return converted, el
    elif el == 'one_reg_log':
        # tb.fill(user_data[0][cur_name].upper())
        return user_data[0][names_data_for_fields[cur_name]].upper(), el
    else:
        # tb.fill(el)
        return el, el


@allure.title("Позитивні та негативні тести: поля відображаються")
@pytest.mark.parametrize("scenario, expected_result", [
    ("valid", "PASS"),
    ("no_valid", "FAIL"),
    #("hidden", "FAIL"),
])
def test_first_name_field(page_open, scenario, expected_result, user_data):

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
                report_about("Тест пройдено: позитивний сценарій успішно виконано", page_open)
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
            report_bug_and_stop("Тест провалено: позитивний сценарій не пройдено", page_open)
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
            # page_open(user_data[0]['url']
    elif scenario == "no_valid":
        debug("Початок негативних тестів", "Негативні тести")
        page_open.goto(user_data[0]['url'])
        debug("здійснено перехід на головну сторінку сайту", "Сайт для тренування")
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
                ind = names_data_for_fields[cur_name]
                list_inv = []
                list_inv = user_data[1][ind]
                for el_l_inv in list_inv:
                    allure.dynamic.title(f"Негативний тест: поле {cur_name} відображається → {expected_result}")
                    with allure.step(f"Пошук і заповнення поля {cur_name}"):
                        tb = page_open.get_by_role("textbox", name=cur_name, exact=True)
                        expect(tb).to_be_visible()
                        if in_inv(cur_name, el_l_inv, user_data)[1] == 'len':
                            resultl = in_inv(cur_name, el_l_inv, user_data)[0].split(" ", 1)[0]
                            tb.fill(resultl)
                            debug(f"знайдено та заповнено поле {cur_name}", f"{cur_name}")
                            resultl = in_inv(cur_name, el_l_inv, user_data)[0].split(" ", 1)[1]
                            tb.fill(resultl)
                            debug(f"знайдено та заповнено поле {cur_name}", f"{cur_name}")
                        else:
                            tb.fill(in_inv(cur_name, el_l_inv, user_data)[0])
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
                report_about("Тест пройдено: негативний сценарій успішно виконано", page_open)
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
            debug("Тест провалено: негативний сценарій не пройдено", "ERROR")
            report_bug_and_stop("Тест провалено: негативний сценарій не пройдено", page_open)
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

