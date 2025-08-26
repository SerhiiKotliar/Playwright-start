import sys
from PySide6.QtWidgets import QApplication, QDialog
from form import Ui_Dialog
from PySide6.QtCore import Qt


# клас що працює з формою налаштування тестів
class MyDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)   # створює інтерфейс
        # окно поверх всех
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        # модальный режим (блокирует остальные окна приложения)
        self.setModal(True)

        # кнопки
        self.btnOk.clicked.connect(self.on_ok)
        self.btnCnl.clicked.connect(self.close)

        # --- нове: вмикаємо/вимикаємо tbSpec по чекбоксу ---
        self.tbSpec.setEnabled(False)  # початково вимкнене
        self.chkbSpecS.toggled.connect(self.on_spec_toggled)

    def on_spec_toggled(self, checked: bool):
        """Увімкнення/вимкнення поля tbSpec"""
        self.tbSpec.setEnabled(checked)
        if self.tbSpec.isEnabled() == False:
            self.tbSpec.setText("")

    def on_ok(self):
        """Читаємо дані з форми"""
        # Комбобокс (розкладка)
        localiz = self.cmbLocaliz.currentText()

        # Радіокнопки (регістр)
        register = self.cmbLocaliz_2.currentText()

        # Чекбокси
        cyfry = self.chkbCyfry.isChecked()
        spec = self.chkbSpecS.isChecked()
        if spec:
            spec = self.tbSpec.text()
        probel = self.chkbProbel.isChecked()
        email_in = self.chkbEmail.isChecked()
        url_in = self.chkbURL.isChecked()

        # Спінбокси
        len_min = self.spinBoxLenMin.value()
        len_max = self.spinBoxLenMax.value()

        self.result = {
            "register": register,
            "localiz": localiz,
            "cyfry": cyfry,
            "spec": spec,
            "probel": probel,
            "len_min": len_min,
            "len_max": len_max,
            "email_in": email_in,
            "url_in": url_in,
        }
        # Закриваємо діалог
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = MyDialog()
    dlg.show()
    sys.exit(app.exec())
