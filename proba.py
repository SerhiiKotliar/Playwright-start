from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QRadioButton, QHBoxLayout, QVBoxLayout, QPushButton, QButtonGroup
)
import sys


class InputFixationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фіксація вводу")

        main_layout = QVBoxLayout()

        # === Фіксація вводу у поле ===
        label_fix = QLabel("Фіксація вводу у поле")
        main_layout.addWidget(label_fix)

        # === Радиокнопки ===
        radio_layout = QHBoxLayout()
        self.radio_event = QRadioButton("Подія")
        self.radio_enter = QRadioButton("Enter")
        self.radio_button = QRadioButton("Кнопка")

        # Группируем радиокнопки, чтобы только одна могла быть выбрана
        radio_group = QButtonGroup(self)
        radio_group.addButton(self.radio_event)
        radio_group.addButton(self.radio_enter)
        radio_group.addButton(self.radio_button)

        # По умолчанию выбрана первая
        self.radio_event.setChecked(True)

        radio_layout.addWidget(self.radio_event)
        radio_layout.addWidget(self.radio_enter)
        radio_layout.addWidget(self.radio_button)
        main_layout.addLayout(radio_layout)

        # === Перевірка помилки ===
        label_check_error = QLabel("Перевірка помилки")
        main_layout.addWidget(label_check_error)

        # === Атрибут ===
        label_attr = QLabel("Атрибут")
        main_layout.addWidget(label_attr)

        # === Поле вводу для атрибута ===
        self.attr_input = QLineEdit()
        main_layout.addWidget(self.attr_input)

        # === Остаточна фіксація ===
        label_final_fix = QLabel("Остаточна фіксація")
        main_layout.addWidget(label_final_fix)

        # === Елемент HTML + Текст ===
        html_text_layout = QHBoxLayout()

        # Левая часть (Елемент HTML)
        html_layout = QVBoxLayout()
        label_html = QLabel("Елемент HTML")
        self.html_input = QLineEdit()
        html_layout.addWidget(label_html)
        html_layout.addWidget(self.html_input)

        # Правая часть (Текст)
        text_layout = QVBoxLayout()
        label_text = QLabel("Текст")
        self.text_input = QLineEdit()
        text_layout.addWidget(label_text)
        text_layout.addWidget(self.text_input)

        html_text_layout.addLayout(html_layout)
        html_text_layout.addLayout(text_layout)
        main_layout.addLayout(html_text_layout)

        # === Кнопки OK и Скасувати ===
        btn_layout = QHBoxLayout()
        self.btnOK = QPushButton("OK")
        self.btnCnl = QPushButton("Скасувати")
        btn_layout.addWidget(self.btnOK)
        btn_layout.addWidget(self.btnCnl)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InputFixationWindow()
    window.show()
    sys.exit(app.exec_())
