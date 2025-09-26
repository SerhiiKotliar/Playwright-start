# mycombo.py — универсальный QComboBox с сигналом focusOut
import sys

# Попытки импортировать одну из Qt-биндингов
_binding = None
try:
    # PyQt5
    from PyQt5.QtCore import pyqtSignal as _Signal
    from PyQt5.QtWidgets import QComboBox as _BaseQComboBox, QApplication
    _binding = "PyQt5"
except Exception:
    try:
        # PyQt6
        from PyQt6.QtCore import pyqtSignal as _Signal
        from PyQt6.QtWidgets import QComboBox as _BaseQComboBox, QApplication
        _binding = "PyQt6"
    except Exception:
        try:
            # PySide2
            from PySide2.QtCore import Signal as _Signal
            from PySide2.QtWidgets import QComboBox as _BaseQComboBox, QApplication
            _binding = "PySide2"
        except Exception:
            try:
                # PySide6
                from PySide6.QtCore import Signal as _Signal
                from PySide6.QtWidgets import QComboBox as _BaseQComboBox, QApplication
                _binding = "PySide6"
            except Exception as exc:
                raise ImportError(
                    "Не найдено ни PyQt5/PyQt6/PySide2/PySide6. Установите одну из этих библиотек."
                ) from exc


class MyComboBox(_BaseQComboBox):
    """
    QComboBox с дополнительным сигналом focusOut.
    Имя сигнала — focusOut (поведение как в примерах выше).
    """
    focusOut = _Signal()

    def focusOutEvent(self, event):
        # генерируем сигнал и вызываем родительскую обработку
        try:
            self.focusOut.emit()
        except Exception:
            # на всякий случай — некоторые биндинги могут вести себя по-разному
            pass
        super().focusOutEvent(event)


# Экспортируем удобные имена: можно импортировать MyComboBox или QComboBox (чтобы не менять код)
QComboBox = MyComboBox
WhichBinding = lambda: _binding
