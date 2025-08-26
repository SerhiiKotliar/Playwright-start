import re
import pytest
from playwright.sync_api import Page, expect
import tkinter as tk
from tkinter import messagebox
import multiprocessing
# from main import get_root
from helper import debug

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

def test_example(page: Page, page_open) -> None:
    # show_message('URL', 'https://www.qa-practice.com/')
    # Всплывающее окно для отладки
    # show_message_async("URL", 'https://www.qa-practice.com/')
    debug('https://www.qa-practice.com/', "URL")  # сразу в консоль и в Allure
    logo = page_open.locator("img.logo_image")  # знаходимо <img> з класом
    expect(logo).to_be_visible()  # перевіряємо, що зображення видно
    expect(page_open.get_by_role("link", name="Select input")).to_be_visible()
    page_open.get_by_role("link", name="Select input").click()
    expect(page.get_by_label("Choose language*")).to_be_visible()
    page.get_by_label("Choose language*").select_option(label="Python")
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("You selected Python")).to_be_visible()
    page.get_by_text("You selected Python").screenshot(path="screenshots/Python.png")



# @pytest.mark.skip('Site doesn\'t work')
def test_dynamic_props(page_open) -> None:
    # page.goto('https://demoqa.com/dynamic-properties')
    button = page_open().locator('#visibleAfter')
    button.click()
    page_open.screenshot(type='jpeg', path='screenshots/shot.jpg')


def test_iframe(page_open):
    # page.goto('https://www.qa-practice.com/elements/iframe/iframe_page')
    toggler = page_open.frames[1].locator('css=.navbar-toggler-icon')
    toggler.click()
    page_open.screenshot(type='jpeg', path='screenshots/toggler.jpg')


def test_drag( page_open):
    # page.goto('https://www.qa-practice.com/elements/dragndrop/boxes')
    page_open.drag_and_drop('#rect-draggable', '#rect-droppable')
    page_open.screenshot(type='jpeg', path='screenshots/drag.jpg')


def test_select(page_open):
    # page.goto('https://www.qa-practice.com/elements/button/disabled')
    page_open.locator('#id_select_state').select_option('enabled')
    page_open.screenshot(type='jpeg', path='screenshots/select.jpg')


def test_hover(page_open):
    # page.goto('https://magento.softwaretestingboard.com/')
    page_open.locator('#ui-id-4').hover()
    page_open.locator('#ui-id-9').hover()
    page_open.screenshot(type='jpeg', path='screenshots/hover.jpg')
