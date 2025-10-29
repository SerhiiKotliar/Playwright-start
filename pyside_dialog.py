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
        self.btnCnl.clicked.connect(self.reject)

        # --- нове: вмикаємо/вимикаємо tbSpec по чекбоксу ---
        self.tbSpec.setEnabled(False)  # початково вимкнене
        self.chkbSpecS.toggled.connect(self.on_spec_toggled)
        self.chkbEmail.toggled.connect(self.on_CHKE_toggled)
        self.chkbURL.toggled.connect(self.on_CHKU_toggled)
        self.chkbNo_absent.setChecked(True)
        self.chkbNo_absent.toggled.connect(self.on_CHKN_toggled)
        self.chkbCyfry.toggled.connect(self.on_CHKC_toggled)
        self.chkbProbel.toggled.connect(self.on_CHKP_toggled)
        self.cmbLocaliz.activated.connect(self.on_item_activated_localiz)
        self.cmbLocaliz.currentIndexChanged.connect(self.on_index_changed)
        self.cmbLocaliz_2.activated.connect(self.on_item_activated_localiz_2)
        self.cmbLocaliz_2.currentIndexChanged.connect(self.on_index_changed2)
        self.spinBoxLenMin.editingFinished.connect(self.on_editing_finished_min)
        self.spinBoxLenMax.editingFinished.connect(self.on_editing_finished_max)

    def on_index_changed(self, index):
        """Вызывается при изменении индекса"""
        text = self.cmbLocaliz.itemText(index)
        # if text == "латиниця і кирилиця":
        #     self.chkbLocaliz_at_least_one.setEnabled(True)
        # else:
        #     self.chkbLocaliz_at_least_one.setEnabled(False)

    def on_index_changed2(self, index):
        """Вызывается при изменении индекса"""
        text = self.cmbLocaliz_2.itemText(index)
        if text == "обидва":
            self.chkbRegistr_at_least_one.setEnabled(True)
        else:
            self.chkbRegistr_at_least_one.setEnabled(False)


    def on_spec_toggled(self, checked: bool):
        """Увімкнення/вимкнення поля tbSpec"""
        self.chkbNo_absent.setChecked(False)
        self.chkbURL.setChecked(False)
        self.chkbEmail.setChecked(False)
        if self.chkbSpecS.isChecked():
            self.chkbSpecS_at_least_one.setChecked(True)
        self.chkbSpecS_at_least_one.setEnabled(checked)
        self.tbSpec.setEnabled(checked)
        if self.tbSpec.isEnabled() == False:
            self.tbSpec.setText("")

    def on_CHKE_toggled(self, checked: bool):
        if self.chkbEmail.isChecked():
            self.chkbURL.setChecked(False)
            self.chkbNo_absent.setChecked(False)
        # else:
        #     self.chkbURL.setChecked(True)

    def on_CHKU_toggled(self, checked: bool):
        if self.chkbURL.isChecked():
            self.chkbEmail.setChecked(False)
            self.chkbNo_absent.setChecked(False)
        # else:
        #     self.chkbEmail.setChecked(True)

    def on_CHKN_toggled(self, checked: bool):
        if self.chkbNo_absent.isChecked():
            self.chkbEmail.setChecked(False)
            self.chkbURL.setChecked(False)

    def on_CHKC_toggled(self, checked: bool):
        self.chkbNo_absent.setChecked(False)
        self.chkbURL.setChecked(False)
        self.chkbEmail.setChecked(False)
        if self.chkbCyfry.isChecked():
            self.chkbCyfry_at_least_one.setEnabled(True)
            self.chkbCyfry_at_least_one.setChecked(True)
        else:
            self.chkbCyfry_at_least_one.setEnabled(False)

    def on_CHKP_toggled(self, checked: bool):
        self.chkbNo_absent.setChecked(False)
        self.chkbURL.setChecked(False)
        self.chkbEmail.setChecked(False)

    def on_item_activated_localiz(self, index):
        self.chkbNo_absent.setChecked(False)
        self.chkbURL.setChecked(False)
        self.chkbEmail.setChecked(False)

    def on_item_activated_localiz_2(self, index):
        self.chkbNo_absent.setChecked(False)
        self.chkbURL.setChecked(False)
        self.chkbEmail.setChecked(False)

    def on_editing_finished_min(self):
        self.chkbNo_absent.setChecked(False)
        self.chkbURL.setChecked(False)
        self.chkbEmail.setChecked(False)

    def on_editing_finished_max(self):
        self.chkbNo_absent.setChecked(False)
        self.chkbURL.setChecked(False)
        self.chkbEmail.setChecked(False)


    def on_ok(self):
        """Читаємо дані з форми"""
        # Комбобокс (розкладка)
        localiz = self.cmbLocaliz.currentText()

        # Радіокнопки (регістр)
        register = self.cmbLocaliz_2.currentText()

        # Чекбокси
        cyfry = self.chkbCyfry.isChecked()
        spec = self.chkbSpecS.isChecked()
        if spec and self.tbSpec.text() != "":
            spec = self.tbSpec.text()
        probel = self.chkbProbel.isChecked()
        email_in = self.chkbEmail.isChecked()
        url_in = self.chkbURL.isChecked()
        absent_in = self.chkbNo_absent.isChecked()
        register_one = self.chkbRegistr_at_least_one.isChecked() and self.chkbRegistr_at_least_one.isEnabled()
        localiz_one = self.chkbLocaliz_at_least_one.isChecked() and self.chkbLocaliz_at_least_one.isEnabled()
        cyfry_one = self.chkbCyfry_at_least_one.isChecked() and self.chkbCyfry_at_least_one.isEnabled()
        spec_one = self.chkbSpecS_at_least_one.isChecked() and self.chkbSpecS_at_least_one.isEnabled()

        # Спінбокси
        len_min = self.spinBoxLenMin.value()
        len_max = self.spinBoxLenMax.value()

        self.result = {
            "no_absent": absent_in,
            "register": register,
            "register_at_least_one": register_one,
            "localiz": localiz,
            "localiz_at_least_one": localiz_one,
            "cyfry": cyfry,
            "cyfry_at_least_one": cyfry_one,
            "spec": spec,
            "spec_at_least_one": spec_one,
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
