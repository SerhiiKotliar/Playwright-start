from PySide6.QtWidgets import QApplication, QMessageBox, QWidget, QPushButton, QVBoxLayout
import sys

app = QApplication.instance()
created_app = False
if app is None:
    app = QApplication(sys.argv)
    created_app = True
# class Example(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Вікно з двома кнопками")
#
#         btn = QPushButton("Показати повідомлення")
#         btn.clicked.connect(self.ask_user)
#
#         layout = QVBoxLayout(self)
#         layout.addWidget(btn)
#
#     def ask_user(self):
msg = QMessageBox()
msg.setWindowTitle("Конфігурація тестів")
msg.setText("Створити конфігурацію чи використати існуючу?")
msg.setIcon(QMessageBox.Question)
# Добавляем две кнопки
yes_btn = msg.addButton("СТВОРИТИ", QMessageBox.YesRole)
no_btn = msg.addButton("ВИКОРИСТАТИ ІСНУЮЧУ", QMessageBox.NoRole)
msg.setDefaultButton(no_btn)
msg.exec()

if msg.clickedButton() == yes_btn:
    print("Користувач вибрав: Так")
elif msg.clickedButton() == no_btn:
    print("Користувач вибрав: Ні")
if created_app:
    app.quit()

if __name__ == "__main__":
    app = QApplication.instance()
    created_app = False
    if app is None:
        app = QApplication(sys.argv)
        created_app = True
    # app = QApplication(sys.argv)
    # w = Example()
    # w.show()
    sys.exit(app.exec())
