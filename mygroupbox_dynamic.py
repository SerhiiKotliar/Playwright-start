# mygroupbox_dynamic.py
# Работает с PyQt5 / PyQt6 / PySide2 / PySide6
from typing import Optional

_binding = None
try:
    # PyQt5
    from PyQt5.QtCore import pyqtSignal as Signal, QEvent, Qt
    from PyQt5.QtWidgets import (
        QGroupBox as _BaseGroupBox,
        QWidget,
    )
    _binding = "PyQt5"
except Exception:
    try:
        # PyQt6
        from PyQt6.QtCore import pyqtSignal as Signal, QEvent, Qt
        from PyQt6.QtWidgets import (
            QGroupBox as _BaseGroupBox,
            QWidget,
        )
        _binding = "PyQt6"
    except Exception:
        try:
            # PySide2
            from PySide2.QtCore import Signal, QEvent, Qt
            from PySide2.QtWidgets import (
                QGroupBox as _BaseGroupBox,
                QWidget,
            )
            _binding = "PySide2"
        except Exception:
            # PySide6
            from PySide6.QtCore import Signal, QEvent, Qt
            from PySide6.QtWidgets import (
                QGroupBox as _BaseGroupBox,
                QWidget,
            )
            _binding = "PySide6"


class MyGroupBox(_BaseGroupBox):
    """
    QGroupBox с сигналом focusLeft.
    Сигнал испускается, когда фокус уходит за пределы ВСЕХ дочерних виджетов группы.
    """
    focusLeft = Signal()  # важно: именно Signal()
    # focusEntered = Signal()

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(title, parent)
        # Чтобы не регистрировать виджеты дважды
        self._watched = set()
        # зарегистрируем уже существующие дочерние виджеты (если они уже добавлены)
        self._install_filters_for_children()

    # публичный метод: регистрирует конкретный виджет для отслеживания фокуса
    def watch_widget(self, widget: QWidget) -> None:
        if widget is None:
            return
        # используем id(widget) как ключ, чтобы избежать повторной регистрации
        key = id(widget)
        if key in self._watched:
            return
        try:
            widget.setFocusPolicy(Qt.StrongFocus)
        except Exception:
            # не все объекты поддерживают смену политики или это не важно
            pass
        try:
            widget.installEventFilter(self)
        except Exception:
            pass
        self._watched.add(key)

    def _install_filters_for_children(self) -> None:
        # находим дочерние виджеты и регистрируем их
        for w in self.findChildren(QWidget):
            self.watch_widget(w)

    # Автоматически ловим динамически добавляемые дочерние объекты
    def childEvent(self, event):
        # QEvent.ChildAdded появляется, когда добавлен дочерний QObject (в т.ч. QWidget)
        if event.type() == QEvent.ChildAdded:
            obj = event.child()
            # иногда child() возвращает не QWidget — проверяем
            if isinstance(obj, QWidget):
                self.watch_widget(obj)
        return super().childEvent(event)

    # главный фильтр — ловим FocusOut у дочерних виджетов
    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusOut:
            # новое виджет с фокусом в окне
            try:
                new_focus = self.window().focusWidget()
            except Exception:
                new_focus = None
            # если новый фокус либо отсутствует, либо НЕ внутри этого GroupBox -> emit
            if new_focus is None or not self.isAncestorOf(new_focus):
                # emit у экземпляра сигнала
                try:
                    self.focusLeft.emit()
                except Exception:
                    # на всякий случай — если биндинг как-то необычно себя ведет
                    pass
        return super().eventFilter(obj, event)
    # def eventFilter(self, obj, event):
    #     if event.type() == QEvent.FocusIn:
    #         try:
    #             new_focus = self.window().focusWidget()
    #         except Exception:
    #             new_focus = None
    #
    #         if new_focus is not None and self.isAncestorOf(new_focus):
    #             try:
    #                 self.focusEntered.emit()
    #             except Exception:
    #                 pass
    #
    #     elif event.type() == QEvent.FocusOut:
    #         try:
    #             new_focus = self.window().focusWidget()
    #         except Exception:
    #             new_focus = None
    #
    #         if new_focus is None or not self.isAncestorOf(new_focus):
    #             try:
    #                 self.focusLeft.emit()
    #             except Exception:
    #                 pass
    #
    #     return super().eventFilter(obj, event)


# Удобный экспорт
WhichBinding = lambda: _binding
QGroupBox = MyGroupBox  # чтобы можно было просто заменить импорт QGroupBox
