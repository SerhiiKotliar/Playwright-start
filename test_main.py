import pytest
from playwright.sync_api import Page, expect
# from conftest import user_data
from helper import debug
import allure
# def _show_message(title, text):
#     root = tk.Tk()
#     root.withdraw()
#     root.attributes("-topmost", True)
#     messagebox.showinfo(title, text)
#     root.destroy()
#
# def show_message_async(title, text):
#     """Показывает окно в отдельном процессе, не блокируя тест"""
#     p = multiprocessing.Process(target=_show_message, args=(title, text))
#     p.start()
# def _show(title, text):
#     root = tk.Tk()
#     root.withdraw()
#     root.attributes("-topmost", True)   # окно поверх всех
#     messagebox.showinfo(title, text)
#     root.destroy()
# def show_message(parent, title="Сообщение", text="Текст"):
#     parent.attributes("-topmost", True)  # делаем поверх всех
#     messagebox.showinfo(title, text, parent=parent)
# def show_message(title: str = "Сообщение", text: str = "Текст", kind: str = "info") -> bool | None:
#     """Универсальная функция для вывода messagebox поверх всех окон.
#        kind = info | warning | error | askyesno | askokcancel | askretrycancel
#     """
#     """Показать окно поверх всех, даже внутри pytest+playwright"""
#     p = multiprocessing.Process(target=_show, args=(title, text))
#     p.start()
#     p.join()  # ждём, пока пользователь закроет окно
#     # root = tk.Tk()
#     # root.withdraw()  # Скрываем главное окно
#     # # root.attributes("-topmost", True)
#     # root.attributes("-topmost", 1)  # держать поверх всех
#     #
#     # # чтобы окно гарантированно появилось
#     # root.update()
#     # # создаём скрытое окно, которое будет всегда сверху
#     # top = tk.Toplevel(root)
#     # top.withdraw()
#     # top.attributes("-topmost", True)
#
#     # # выбираем тип окна
#     # if kind == "info":
#     #     messagebox.showinfo(title, text)
#     # elif kind == "warning":
#     #     messagebox.showwarning(title, text)
#     # elif kind == "error":
#     #     messagebox.showerror(title, text)
#     # elif kind == "askyesno":
#     #     return messagebox.askyesno(title, text)
#     # elif kind == "askokcancel":
#     #     return messagebox.askokcancel(title, text)
#     # elif kind == "askretrycancel":
#     #     return messagebox.askretrycancel(title, text)
#
#     # root.destroy()  # корректно закрываем скрытый root
@allure.feature("тестування декількох сайтів")
@allure.story("перебіг функціональних елементів на сторінках сайту https://www.qa-practice.com/")
def test_example(page: Page, page_open) -> None:
    # 'https://www.qa-practice.com/'
    # debug(user_data['url'], "URL")  # сразу в консоль и в Allure
    with  allure.step("перехід на малюнок img.logo_image"):
        logo = page_open.locator("img.logo_image")  # знаходимо <img> з класом
        expect(logo).to_be_visible()  # перевіряємо, що зображення видно
        print('\n')
        debug("Видне шукане зображення", "Пошук зображення")
    with  allure.step("Перевірка видимісті посилання на вибір мов"):
        expect(page_open.get_by_role("link", name="Select input")).to_be_visible()
        debug("Видне шукане посилання", "Пошук посилання")
    with  allure.step("перехід до вибору мови і клік по ній та перевірка видимісті її"):
        page_open.get_by_role("link", name="Select input").click()
        expect(page.get_by_label("Choose language*")).to_be_visible()
        debug("Після кліку відкрився вибір", "Вибір мови")
    with  allure.step("вибір мови та натискання на кнопу, що підтверджує вибір"):
        page.get_by_label("Choose language*").select_option(label="Python")
        debug("Перехід на мітку Python для подальшого натискання на неї", "Вибір мови")
        page.get_by_role("button", name="Submit").click()
    with  allure.step("перевірка видимісті тексту вибраної мови, зберігання скріну малюнку, що підтверджує вибрану мову"):
        expect(page.get_by_text("You selected Python")).to_be_visible()
        debug("Після вибору мови та кліку видна вибрана мова", "Вибір мови")
        page.get_by_text("You selected Python").screenshot(path="screenshots/Python.png")
        debug("Збережений скрін Python.png з вибраною мовою", "Скрін сторінки")


@pytest.mark.skip('Сайт не працює')
@allure.story("натискання кнопки на сайті https://demoqa.com/dynamic-properties")
def test_dynamic_props(page_open) -> None:
    # page.goto('https://demoqa.com/dynamic-properties')
    with  allure.step("перехід на кнопку"):
        button = page_open().locator('#visibleAfter')
        debug("Здійснено перехід на кнопку", "Клік на кнопці")
        button.click()
        debug("Клік на кнопці", "Клік на кнопці")
    with  allure.step("перевірка видимісті тексту вибраної мови, зберігання скріну малюнку, що підтверджує вибрану мову"):
        page_open.screenshot(type='jpeg', path='screenshots/shot.jpg')
        debug("Збережений скрін shot.jpg", "Скрін сторінки")

@allure.story("перехід і натискання рамки на сайті https://www.qa-practice.com/elements/iframe/iframe_page")
def test_iframe(page_open):
    # page.goto('https://www.qa-practice.com/elements/iframe/iframe_page')
    with  allure.step("перехід на рамку"):
        toggler = page_open.frames[1].locator('css=.navbar-toggler-icon')
        debug("Здійснено перехід на рамку", "Клік на рамці")
        toggler.click()
        debug("Здійснено клік на рамку", "Клік на рамці")
    with  allure.step("зберігання скріну малюнку toggler.jpg"):
        page_open.screenshot(type='jpeg', path='screenshots/toggler.jpg')
        debug("Збережений скрін toggler.jpg", "Скрін сторінки")

@allure.story("перевірка перетаскування елементів на сайті https://www.qa-practice.com/elements/dragndrop/boxes")
def test_drag( page_open):
    # page.goto('https://www.qa-practice.com/elements/dragndrop/boxes')
    with  allure.step("перетаскування"):
        page_open.drag_and_drop('#rect-draggable', '#rect-droppable')
        debug("елемент перетягнуто", "Клік на рамці")
        page_open.screenshot(type='jpeg', path='screenshots/drag.jpg')
        debug("Збережений скрін drag.jpg", "Скрін сторінки")

@allure.story("переведення елементу в інший стан вибором зі списку сайті https://www.qa-practice.com/elements/button/disabled")
def test_select(page_open):
    # page.goto('https://www.qa-practice.com/elements/button/disabled')
    with  allure.step("переведення вибором стану зі списку"):
        page_open.locator('#id_select_state').select_option('enabled')
        debug("вибран стан зі списку", "Зміна стану")
        page_open.screenshot(type='jpeg', path='screenshots/select.jpg')
        debug("Збережений скрін select.jpg", "Скрін сторінки")

@allure.story("переведення миші по елементам спеціального сайту для автоматизації тестування сайті https://magento.softwaretestingboard.com/")
def test_hover(page_open):
    # page.goto('https://magento.softwaretestingboard.com/')
    with  allure.step("переведення миші по елементам"):
        page_open.locator('#ui-id-4').hover()
        debug("переведена на елемент ui-id-4", "Переведення миші")
        page_open.locator('#ui-id-9').hover()
        debug("переведена на елемент ui-id-9", "Переведення миші")
        page_open.screenshot(type='jpeg', path='screenshots/hover.jpg')
        debug("Збережений скрін hover.jpg", "Скрін сторінки")
