import allure
import pytest
from playwright.sync_api import expect

from conftest import page_open
from main_file import report_about, report_bug_and_stop
# from conftest import user_data
from helper import debug
import re
fields = ["First Name*", "Last Name*", "Email*", "Password*", "Confirm Password*"]
names_data_for_fields = {"First Name*": "login", "Last Name*": "login_l", "Email*": "email", "Password*": "password", "Confirm Password*": "password"}
valid_values = []
invalid_values = {}
def valid_val(user_data):
    val_el = []
    for field in fields:
        val_el.append(user_data[0][names_data_for_fields[field]])
    return val_el

def invalid_val(user_data):
    inval_el = {}
    for field in fields:
        ar_inv = []
        for el in user_data[1][names_data_for_fields[field]]:
            value, mode = in_inv(field, el, user_data)
            if mode == "len":
                first, second = value.split(" ", 1)
                # tb.fill(first)
                ar_inv.append(first)
                # debug(f"заповнено перше значення {first}", f"{cur_name}")
                # tb.fill(second)
                ar_inv.append(second)
                # debug(f"заповнено друге значення {second}", f"{cur_name}")
            else:
                # tb.fill(value)
                # debug(f"заповнено {value}", f"{cur_name}")
                ar_inv.append(value)
            # ar_inv.append(in_inv(field, el, user_data))
        inval_el[field] =ar_inv
    return inval_el

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
        return (user_data[0][names_data_for_fields[cur_name]] * 6)[:(lmin - 2)] +" "+ (user_data[0][names_data_for_fields[cur_name]] * 6)[:(lmax + 2)], el
    elif el == 'no_email':
        # tb.fill(user_data[0]['email'])
        return user_data[0]['url'], el
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
        mapping = dict(zip(ru, en))
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
        mapping = dict(zip(en, ru))
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
        mapping = str.maketrans(en + en.lower(), ru + ru.lower())
        converted = el.translate(mapping)
        # tb.fill(converted)
        return converted, el
    elif el == 'upreglat':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = str.maketrans(en + en.upper(), ru + ru.upper())
        converted = el.translate(mapping)
        # tb.fill(converted)
        return converted, el
    elif el == 'lowregcyr':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = str.maketrans(ru + ru.lower(), en + en.lower())
        converted = el.translate(mapping)
        # tb.fill(converted)
        return converted, el
    elif el == 'upregcyr':
        ru = "йцукенгшщзхъфывапролджэячсмитьбю"
        en = "qwertyuiopdfasdfghjkldfzxcvbnmdf"
        mapping = str.maketrans(ru + ru.upper(), en + en.upper())
        converted = el.translate(mapping)
        # tb.fill(converted)
        return converted, el
    elif el == 'one_reg_log':
        # tb.fill(user_data[0][cur_name].upper())
        return user_data[0][names_data_for_fields[cur_name]].upper(), el
    else:
        # tb.fill(el)
        return el, el


# @allure.title("Позитивні та негативні тести: поля відображаються")
# @pytest.mark.parametrize("scenario, expected_result", [
#     ("valid", "PASS"),
#     ("no_valid", "FAIL"),
#     #("hidden", "FAIL"),
# ])
# def test_first_name_field(page_open, scenario, expected_result, user_data):
#     valid_values = valid_val(user_data)
#     invalid_values = invalid_val(user_data)


def generate_negative_cases():
    """Собираем все наборы: одно поле невалидное, остальные валидные"""
    test_cases = []
    for i, field in enumerate(fields):
        for inv in invalid_values[field]:
            case = valid_values.copy()
            case[i] = inv
            test_cases.append((field, dict(zip(fields, case))))
    return test_cases

# 🔹 Позитивный тест выполняется всегда первым
# @pytest.mark.dependency(name="positive")
def test_positive_form(page_open, user_data):
    global valid_values, invalid_values
    valid_values = valid_val(user_data)
    invalid_values = invalid_val(user_data)
    allure.dynamic.title("Позитивний тест: усі поля валідні")
    print('\n')
    debug("Позитивний тест: усі поля валідні", "Початок позитивного тесту")
    ##########################################################################
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
                debug("Виявлено рекламу з кнопкою Close. Натиснуто на Close", "WARNING")

        with allure.step('Перевірка заголовку, чи це сторінка створення екаунту'):
            expect(page_open.get_by_text("Create New Customer Account")).to_be_visible(timeout=40000)

            # expect(page_open.get_by_role("heading")).to_contain_text(
            #     "Create New Customer Account", timeout=40000
            # )
            debug("здійснено перехід на сторінку створення екаунту", "Сторінка створення екаунту")
        ##########################################################################
        with allure.step("Заповнення форми валідними даними"):
            for field, value in zip(fields, valid_values):
                tb = page_open.get_by_role("textbox", name=field, exact=True)
                tb.fill(value)
                debug("заповнено поле", f"{field}")
                allure.attach(str(value), name=f"Поле {field}")

        # with allure.step("Перевірка успішної відправки форми"):
        #     # пример проверки (должно пройти!)
        #     # expect(page_open.get_by_text("Account created")).to_be_visible()
        #     pass
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
            name=f"Скриншот останньої сторінки",
            attachment_type=allure.attachment_type.PNG
        )

    except AssertionError as e:
        debug(f"Тест провалено: позитивний сценарій не пройдено {e}", "ERROR")
        report_bug_and_stop(f"Тест провалено: позитивний сценарій не пройдено {e}", page_open)
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
            name=f"Скриншот падіння або помилки",
            attachment_type=allure.attachment_type.PNG
        )

    except Exception as e:
        debug(f"Тест провалено: позитивний сценарій не пройдено {e}", "ERROR")
        report_bug_and_stop(f"Тест провалено: позитивний сценарій не пройдено {e}", page_open)
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
            name=f"Скриншот падіння або помилки",
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

############################################################################################################
# def generate_negative_cases():
#     """Собираем все наборы: одно поле невалидное, остальные валидные"""
#     test_cases = []
#     for i, field in enumerate(fields):
#         for inv in invalid_values[field]:
#             case = valid_values.copy()
#             case[i] = inv
#             test_cases.append((field, dict(zip(fields, case))))
#     return test_cases
##########################################################################
# 🔹 Негативные тесты зависят от позитивного
# @pytest.mark.parametrize("invalid_field, data", generate_negative_cases())
# @pytest.mark.dependency(depends=["positive"])
# def test_negative_form(page_open, invalid_field, data):
def test_negative_form(page_open, user_data):
    global valid_values, invalid_values
    valid_values = valid_val(user_data)
    invalid_values = invalid_val(user_data)

   #  try:
   #      with allure.step('Перехід на посилання створення екаунту та клік на ньому'):
   #          link = page_open.get_by_role("link", name="Create an Account")
   #          expect(link).to_be_visible(timeout=40000)
   #          print('\n')
   #          debug("здійснено перехід на посилання створення екаунту", "Посилання створення екаунту")
   #          link.click()
   #          debug("здійснено клік на посиланні створення екаунту", "Посилання створення екаунту")
   #
   #          # --- обхід реклами ---
   #          if "google_vignette" in page_open.url or "ad.doubleclick" in page_open.url:
   #              debug("Виявлено рекламу google_vignette. Повертаємось назад...", "WARNING")
   #              page_open.go_back()
   #              expect(link).to_be_visible(timeout=20000)
   #              link.click()
   #              debug("повторний клік після реклами", "INFO")
   #
   #          close_button = page_open.get_by_role("button", name="Close").first
   #          if close_button.is_visible():
   #              close_button.click()
   #              debug("Виявлено рекламу з кнопкою Close. Натиснуто на Close", "WARNING")
   #
   #      with allure.step('Перевірка заголовку, чи це сторінка створення екаунту'):
   #          expect(page_open.get_by_text("Create New Customer Account")).to_be_visible(timeout=40000)
   #          # expect(page_open.get_by_role("heading")).to_contain_text(
   #          #     "Create New Customer Account", timeout=40000
   #          # )
   #          debug("здійснено перехід на сторінку створення екаунту", "Сторінка створення екаунту")
   #      list_inv_fields = generate_negative_cases()
   #      invalid_field = ''
   #      for el_list in list_inv_fields:
   #          invalid_field, data = el_list
   #          inv_value = ''
   #          allure.dynamic.title(f"Негативний тест: поле '{invalid_field}' отримує невалідні значення")
   #          print('\n')
   #          debug(f"Негативний тест: поле '{invalid_field}' отримує невалідні значення", "Негативні тести")
   #          with allure.step("Заповнення форми"):
   #              debug("заповнення полів форми", "Форма")
   #              for field, value in data.items():
   #                  if invalid_field == field:
   #                      inv_value = value
   #                  tb = page_open.get_by_role("textbox", name=field, exact=True)
   #                  tb.fill(value)
   #                  allure.attach(str(value), name=f"Поле {field}")
   #                  debug("введені невалідні дані у поле", f"{field}")
   #          with allure.step('Перехід на кнопку створення екаунту та клік на ній'):
   #              btnS = page_open.get_by_role("button", name="Create an Account")
   #              expect(btnS).to_be_visible(timeout=10000)
   #              debug("здійснено перехід на кнопку створення екаунту", "Кнопка створення екаунту")
   #              btnS.click()
   #              debug("здійснено клік на кнопку створення екаунту", "Кнопка створення екаунту")
   #              # expect(page_open.get_by_role("alert").locator("div").first).to_be_visible(timeout=10000)
   #              expect(page_open.get_by_role("alert")).to_contain_text("Thank you for registering with Main Website Store.")
   #              assert page_open.get_by_role("strong").filter(has_text="Account Information").is_visible(),\
   #                                   "BUG: Відсутня інформація про екаунт"
   #              # assert page_open.locator("h1").           page_open.locator("h1").to_contain_text("My Account", timeout=40000), \
   #              #     "BUG: Немає переходу на сторінку екаунту"
   #          with allure.step('Перевірка переходу на сторінку My Account'):
   #              expect(page_open.locator("h1")).to_be_visible(timeout=20000)
   #              debug("здійснено перехід на сторінку зареєстрованого екаунту", "Сторінка екаунту")
   #
   #              # Перевіряємо наявність інформації про акаунт
   #              assert page_open.get_by_role("strong").filter(has_text="Account Information").is_visible(), \
   #                  "BUG: Відсутня інформація про екаунт"
   #
   #  except AssertionError as e:
   #      debug(f"Негативний тест пройдено для поля {invalid_field} зі значенням \"{inv_value}\"", "TEST FAIL")
   #      raise e
   #      report_bug_and_stop(f"Негативний тест пройдено для поля {invalid_field} зі значенням \"{inv_value}\"", page_open)
   #      debug(f"Current URL: {page_open.url}", "INFO")
   #  except Exception as e:
   #      # Логування помилок форми
   #      errors = []
   #      for selector in [
   #          "#firstname-error",
   #          "#lastname-error",
   #          "#email_address-error",
   #          "#password-error",
   #          "#password-confirmation-error",
   #      ]:
   #          if page_open.locator(selector).is_visible():
   #              errors.append(page_open.locator(selector).inner_text())
   #              debug(page_open.locator(selector).inner_text(), "ERROR")
   #
   #      alert = page_open.get_by_role("alert").locator("div").first
   #      if alert.is_visible():
   #          errors.append(alert.inner_text())
   #          debug(alert.inner_text(), "ERROR")
   #          debug(e, "Errors list:")
   #
   #      if errors:
   #          debug("Знайдено помилки при введенні даних:", "ERROR")
   #          debug(errors, "Errors list:")
   #          debug(e, "Errors list:")
   #      # Скриншот страницы
   #      screenshot = page_open.screenshot()
   #      allure.attach(
   #          screenshot,
   #          name=f"Скриншот падіння або помилки",
   #          attachment_type=allure.attachment_type.PNG
   #      )
   #
   #      # debug текущего текста страницы для анализа
   #      try:
   #          account_text = page_open.locator("#maincontent").inner_text(timeout=5000)
   #          debug(account_text, "Текст сторінки My Account (якщо є):")
   #      except:
   #          debug("Не вдалося отримати текст сторінки My Account", "INFO")
   #
   #      # Сбрасываем AssertionError, чтобы тест упал и pytest зарегистрировал ошибку
   #      raise e
   #      # page_open(user_data[0]['url']
   #
    failed_cases = []  # тут збираємо всі провали

    try:
        with allure.step('Перехід на посилання створення екаунту та клік на ньому'):
            link = page_open.get_by_role("link", name="Create an Account")
            expect(link).to_be_visible(timeout=40000)
            print('\n')
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
                debug("Виявлено рекламу з кнопкою Close. Натиснуто на Close", "WARNING")

        with allure.step('Перевірка заголовку, чи це сторінка створення екаунту'):
            expect(page_open.get_by_text("Create New Customer Account")).to_be_visible(timeout=40000)
            debug("здійснено перехід на сторінку створення екаунту", "Сторінка створення екаунту")

        list_inv_fields = generate_negative_cases()

        for el_list in list_inv_fields:
            invalid_field, data = el_list
            inv_value = ''
            allure.dynamic.title(f"Негативний тест: поле '{invalid_field}' отримує невалідні значення")
            print('\n')
            debug(f"Негативний тест: поле '{invalid_field}' отримує невалідні значення", "Негативні тести")

            try:
                with allure.step("Заповнення форми"):
                    debug("заповнення полів форми", "Форма")
                    for field, value in data.items():
                        if invalid_field == field:
                            inv_value = value
                        tb = page_open.get_by_role("textbox", name=field, exact=True)
                        tb.fill(value)
                        str_att = ''
                        if inv_value == value:
                            str_att = "введені невалідні дані у поле"
                            debug(str_att, f"{field}")
                        else:
                            str_att = "введені валідні дані у поле"
                            debug(str_att, f"{field}")
                        allure.attach(str_att+" "+ "\""+str(value)+"\"", name=f"Поле {field}")


                with allure.step('Клік на кнопці створення екаунту'):
                    btnS = page_open.get_by_role("button", name="Create an Account")
                    expect(btnS).to_be_visible(timeout=10000)
                    btnS.click()

                    # тут навмисно ставимо "невірне" очікування,
                    # щоб тест зловив помилку, якщо акаунт створився
                    # expect(page_open.get_by_role("alert")).to_contain_text(
                    #     "Thank you for registering with Main Website Store."
                    # )
                    assert page_open.get_by_role("strong").filter(has_text="Account Information").is_visible(), \
                        "BUG: Відсутня інформація про екаунт"

                # with allure.step('Перевірка переходу на сторінку My Account'):
                #     expect(page_open.locator("h1")).to_be_visible(timeout=20000)
                #     debug("здійснено перехід на сторінку зареєстрованого екаунту", "Сторінка екаунту")
                #     assert page_open.get_by_role("strong").filter(has_text="Account Information").is_visible(), \
                #         "BUG: Відсутня інформація про екаунт"

            except AssertionError as e:
                debug(f"Негативний тест пройдено для поля {invalid_field} зі значенням \"{inv_value}\"", "TEST FAIL")
                failed_cases.append((invalid_field, inv_value, str(e)))

                alert = page_open.get_by_role("alert").locator("div").first
                if alert.is_visible():
                    errors.append(alert.inner_text())
                    debug(alert.inner_text(), "ERROR")


            except Exception as e:
                # логування інших помилок (поля, алерти тощо)
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
                        debug(page_open.locator(selector).inner_text(), "ERROR")

                alert = page_open.get_by_role("alert").locator("div").first
                if alert.is_visible():
                    errors.append(alert.inner_text())
                    debug(alert.inner_text(), "ERROR")

                if errors:
                    failed_cases.append((invalid_field, inv_value, "; ".join(errors)))

                screenshot = page_open.screenshot()
                allure.attach(screenshot, name="Скриншот падіння або помилки", attachment_type=allure.attachment_type.PNG)

    finally:
        # після всіх ітерацій: якщо були фейли — завалюємо тест 1 раз
        if failed_cases:
            msg = "\n".join([f"{fld}='{val}' → {err}" for fld, val, err in failed_cases])
            raise AssertionError(f"Негативний тест знайшов помилки:\n{msg}")