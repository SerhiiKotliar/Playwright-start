from PySide6.QtWidgets import (
    QApplication, QFileDialog, QMessageBox, QPushButton, QVBoxLayout, QWidget
)
import json
import sys


class SaveDictExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сохранение словаря в файл")

        # Пример словаря
        self.data = {
            "name": "Test",
            "fields": [
                {"title": "Поле 1", "name": "field_1", "required": True},
                {"title": "Поле 2", "name": "field_2", "required": False}
            ]
        }

        # Кнопка "Сохранить"
        self.btn_save = QPushButton("Сохранить словарь")
        self.btn_save.clicked.connect(self.save_dict_to_file)

        layout = QVBoxLayout(self)
        layout.addWidget(self.btn_save)

    def save_dict_to_file(self):
        # Окно выбора файла
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Зберегти конфігурацію",
            "",
            "JSON files (*.json);;All files (*)"
        )

        if not file_name:
            return  # пользователь нажал "Отмена"

        try:
            # Сохраняем словарь в JSON-файл
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)

            QMessageBox.information(self, "Успіх", f"Дані збережено у {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти файл:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SaveDictExample()
    win.show()
    sys.exit(app.exec())
