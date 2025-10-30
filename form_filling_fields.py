from PySide6.QtWidgets import (
    QApplication, QDialog, QSpinBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QWidget, QGroupBox,
    QComboBox, QCheckBox, QMessageBox, QRadioButton, QButtonGroup
)

# ---- Wrapper для удобного обращения ----
class GroupBoxWrapper:
    def __init__(self, gb, cmb, chkb, btn):
        self.gb = gb
        self.cmb = cmb
        self.chkb = chkb
        self.btn = btn

    def set_geometry(self, cmb_geom=None, chkb_geom=None, btn_geom=None):
        if cmb_geom:
            self.cmb.setGeometry(*cmb_geom)
        if chkb_geom:
            self.chkb.setGeometry(*chkb_geom)
        if btn_geom:
            self.btn.setGeometry(*btn_geom)
###############################################################################################################

# ---- Динамическая форма заполнения полей----
class DynamicDialog(QDialog):
    def __init__(self, config, parent=None, input_url=None, input_login=None, input_login_l=None, input_password=None, input_email=None, name_of_test=""):
        super().__init__(parent)
        self.gb_focus_left_triggered = False  # флаг, вызывалось ли on_gb_focus_left
        self._focus_processing = False  # <— добавляем внутренний флаг
        self.current_groupbox = None
        self.setWindowTitle("Введення даних у тест    "+name_of_test)
        self.resize(640, 140)
        self.result = {}
        self.result_invalid = {}
        self.result_title_fields = {}
        self.result_fields = {}
        main_layout = QVBoxLayout(self)
        # ---- предупреждающий текст ----
        self.warning_label = QLabel("⚠ По замовчуванню для кожного поля тільки одне правило: БУТИ НЕ ПУСТИМ!")
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        self.warning_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.warning_label)
        # ---- Layout для GroupBox ----
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        main_layout.addWidget(self.scroll_content)  # напрямую, без QScrollArea

        # создаём GroupBox
        self.gb = {}
        for cfg in config:
            title = cfg.get("title", "")
            name = cfg.get("name", "")
            required = cfg.get("required")
            gb_widget = MyGroupBox(title)
            gb_widget.setObjectName(name)
            gb_widget.setStyleSheet("background-color: rgb(85, 255, 127);")
            gb_widget.setLocale(QLocale(QLocale.Ukrainian, QLocale.Ukraine))
            gb_widget.setMinimumHeight(60)
            self.result_title_fields[title] = name
            # элементы
            cmb = QComboBox(gb_widget)
            cmb.setEditable(False)
            chkb = QCheckBox("Обов'язкове", gb_widget)
            # привязываем чекбокс к комбобоксу
            # cmb.checkbox = chkb
            if name == 'url_of_page':
                cmb.addItems(input_url)
                cmb.setCurrentText(input_url[0])
            if name == 'url':
                cmb.addItems(input_url)
                cmb.setCurrentText(input_url[0])
            if name in ('login', 'Login', 'First name', 'first name', 'First_name', 'first_name'):
                cmb.addItems(input_login)
                cmb.setCurrentText(input_login[0])
            if name in ('login_l', 'Last name', 'last name', 'Last_name', 'last_name'):
                cmb.addItems(input_login_l)
                cmb.setCurrentText(input_login_l[0])
            if name in ('password', 'Password'):
                cmb.addItems(input_password)
                cmb.setCurrentText(input_password[0])
            if name in ('email', 'Email'):
                cmb.addItems(input_email)
                cmb.setCurrentText(input_email[0])
            if required:
                chkb.setChecked(True)
            cmb.setStyleSheet("background-color: rgb(255, 255, 255);")

            btn = QPushButton("Правила", gb_widget)

            # прикрепляем ссылки внутрь gb_widget
            gb_widget.cmb = cmb
            gb_widget.chkb = chkb
            gb_widget.btn = btn
            # Обязательно зарегистрировать виджеты в MyGroupBox,
            # чтобы он отслеживал их FocusOut:
            gb_widget.watch_widget(cmb)
            gb_widget.watch_widget(chkb)
            gb_widget.watch_widget(btn)

            # стандартная геометрия
            cmb.setGeometry(10, 20, 400, 25)
            chkb.setGeometry(420, 20, 100, 25)
            btn.setGeometry(530, 15, 60, 30)
            gb_widget.setFixedHeight(60)
            self.scroll_layout.addWidget(gb_widget)
            self.gb[name] = GroupBoxWrapper(gb_widget, cmb, chkb, btn)
            # подключаем событие изменения чекбокса (с правильным захватом имени)
            # chkb.toggled.connect(partial(self.on_required_toggled, name))
            # подключаем сигнал с передачей combo и имени
            btn.clicked.connect(lambda _, c=cmb, n=name: self.on_rules_clicked(c, n))
            # запоминаем старое значение
            self.previous_text = cmb.currentText()
            # событие изменения текста
            cmb.editTextChanged.connect(self.on_text_changed)
            # событие потери фокуса групбоксом
            gb_widget.focusLeft.connect(self.on_gb_focus_left)
            # подія отримання фокусу групбоксом
            gb_widget.focusEntered.connect(lambda: self.on_gb_focus_entered(gb_widget))

        # ---- Кнопки OK/Відміна внизу ----
        btn_layout = QHBoxLayout()
        font = QFont()
        font.setBold(True)

        self.btnOK = QPushButton("Введення")
        # Устанавливаем кнопку по умолчанию
        self.btnOK.setDefault(True)
        self.btnOK.setAutoDefault(True)
        self.btnOK.setFont(font)
        self.btnCnl = QPushButton("Відміна")
        self.btnCnl.setFont(font)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btnOK)
        btn_layout.addWidget(self.btnCnl)
        main_layout.addLayout(btn_layout)

        # события кнопок
        self.btnOK.clicked.connect(self.on_ok_clicked)
        self.btnCnl.clicked.connect(self.on_cnl_clicked)

    cur_rules ={}
        # ---- обработчики ----

    def on_text_changed(self, text: str) -> bool:
        combo = self.sender()  # тот QComboBox, который вызвал сигнал
        global chars, pattern
        if not text:
            return True
        pred_txt = self.previous_text
        # если chars == ".", разрешаем всё
        if chars == ".":
            return True
        if len(pred_txt) < len(text):
            # текст доодається
            ok, bad = validate_chars_mode(text, chars)
        else:
            # текст видаляється
            ok = True
        if not ok:
            QMessageBox.warning(self, "Помилка вводу", f"Недопустимий символ: '{bad}'")
            combo.blockSignals(True)
            combo.setCurrentText(pred_txt)
            combo.blockSignals(False)
            combo.setFocus()
            return False
        else:
            # всё ок — обновляем previous_text
            self.previous_text = text
            return True

    def on_gb_focus_entered(self, gb):
        if gb is None:
            gb = self.sender()  # если не передали явно, берём источник сигнала
        if gb is None:
            return
        self.current_groupbox = gb
        # gb = self.sender()
        self.active_groupbox = gb
        self.previous_text = gb.cmb.currentText()
        self.gb_focus_left_triggered = False


    # втрата фокусу групбоксом
    def on_gb_focus_left(self, gb=None):
        if self._focus_processing:
            return False  # предотвращаем повторный вызов
        self._focus_processing = True
        if gb is None:
            gb = self.sender()  # если вызвано сигналом — возьмём sender
        # gb = self.sender()
        global chars, pattern, len_min, len_max, rule_invalid, spec
        gr_t_title = gb.title()
        gr_t = gb.objectName()
        # Якщо chars == ".", дозволяємо все
        if chars == ".":
            pattern = rf"^[{chars}]+$"
            self.previous_text = gb.cmb.currentText()
            self.gb_focus_left_triggered = True
            self._focus_processing = False  # обязательно снять блокировку даже при ошибке
            if self.current_groupbox == gb:
                self.current_groupbox = None
            return True

        # Перевірка на відповідність pattern
        txt_err = ""
        self.gb_focus_left_triggered = True
        for el_t in rule_invalid[gr_t]:
            # sp_simv = has_text_special_chars(pattern)
            # sp_sim1 = any(c in spec for c in gb.cmb.currentText())
            if el_t[:7] == "localiz":
                # локализация установленная, полная, с учётом всех символов и регистра
                localiz = el_t[8:]
                # сновная, определённая по символам, локализация (без цифр, спецсимволов и т.д.)
                loc_text = detect_script(gb.cmb.currentText())
                result = "".join((c1 + c2) if c1 != c2 else "" for c1, c2 in zip_longest(localiz, loc_text, fillvalue=""))
                if result[:1] == "_":
                    loc_text = localiz
                if localiz != loc_text:
                    if localiz == "latin":
                        txt_err += "може бути з латиницею\n"
                    if localiz == "Cyrillic":
                        txt_err += "може бути з кирилицею\n"
                    if localiz == "lowreglat":
                        txt_err += "може бути з малою латиницею\n"
                    if localiz == "upreglat":
                        txt_err += "може бути з великою латиницею\n"
                    if localiz == "loeregcyr":
                        txt_err += "може бути з малою кирилицею\n"
                    if localiz == "upregcyr":
                        txt_err += "може бути з великою кирилицею\n"
                    if localiz == "lowreglat_1":
                        txt_err += "має бути з малою латиницею\n"
                    if localiz == "upreglat_1":
                        txt_err += "має бути з великою латиницею\n"
                    if localiz == "loeregcyr_1":
                        txt_err += "має бути з малою кирилицею\n"
                    if localiz == "upregcyr_1":
                        txt_err += "має бути з великою кирилицею\n"
                    if localiz == "latin_1":
                        txt_err += "має бути хоча б з 1 символом латиниці\n"
                    if localiz == "Cyrillic_1":
                        txt_err += "має бути хоча б з 1 символом кирилиці\n"
                    if localiz == "latin_1_1":
                        txt_err += "має бути хоча б з 1 символом латиниці в великому та малому регістрах\n"
                    if localiz == "Cyrillic_1_1":
                        txt_err += "має бути хоча б з 1 символом кирилиці в великому та малому регістрах\n"
                    if localiz == "lat_Cyr":
                        txt_err += "може бути з латиницею і кирилицею\n"
                    if localiz == 'lat_Cyr_1_1':
                        txt_err += "має бути хоча б з 1 символом латиниці або кирилиці в великому і малому регістрі\n"
                    if localiz == "lat_Cyr_1":
                        txt_err += "має бути хоча б з 1 символом латиниці або кирилиці\n"
                    if localiz == 'lat_Cyr_up':
                        txt_err += "може бути з великими символами латиниці і кирилиці\n"
                    if localiz == "lat_Cyr_low":
                        txt_err += "може бути з малими символами латиниці і кирилиці\n"
                    if localiz == "lat_Cyr_up_1":
                        txt_err += "має бути хоча б з 1 великим символом латиниці і 1 великим символом кирилиці\n"
                    if localiz == "lat_Cyr_low_1":
                        txt_err += "має бути хоча б з 1 малим символом латиниці і 1 малим символом кирилиці\n"
            else:
                if "no_lower" in rule_invalid[gr_t] and not any(c.islower() for c in gb.cmb.currentText()):
                    txt_err += "має містити принаймні одну маленьку літеру\n"
                if "no_upper" in rule_invalid[gr_t] and not any(c.isupper() for c in gb.cmb.currentText()):
                    txt_err += "має містити принаймні одну велику літеру\n"
                if "no_digit" in rule_invalid[gr_t] and not any(c.isdigit() for c in gb.cmb.currentText()):
                    txt_err += "має містити принаймні одну цифру\n"
                if "no_spec" in rule_invalid[gr_t] and not any(c in spec_escaped for c in gb.cmb.currentText()):
                    txt_err += f"має містити принаймні один спеціальний символ з {spec_escaped}\n"
                if "no_email" in rule_invalid[gr_t] and not bool(re.fullmatch(pattern, gb.cmb.currentText())):
                    txt_err += "має бути формату email\n"
                if "no_url" in rule_invalid[gr_t] and not bool(re.fullmatch(pattern, gb.cmb.currentText())):
                    txt_err += "має бути формату URL\n"
                if f"len {len_min} {len_max}" in rule_invalid[gr_t] and (
                        len_max < len(gb.cmb.currentText()) or len(gb.cmb.currentText()) < len_min):
                    txt_err += f"має мати від {len_min} до {len_max} символів включно\n"
                if "probel" in rule_invalid[gr_t] and gb.cmb.currentText().find(' ') > -1:
                    txt_err += "не має бути з пробілами\n"
                if "no_probel" in rule_invalid[gr_t] and gb.cmb.currentText().find(' ') == -1:
                    txt_err += "має бути з пробілами\n"
                if not has_text_special_chars(pattern) and any(c in spec for c in gb.cmb.currentText()):
                    txt_err += "не має бути зі спецсимволами"
                if not re.search(r"\d", pattern) and any(c.isdigit() for c in gb.cmb.currentText()):
                    txt_err = "не має бути з цифрами"
            if txt_err != "":
                QMessageBox.warning(self, "Помилка вводу", f"Поле {gr_t_title}\n"+txt_err)
                self._focus_processing = False  # обязательно снять блокировку даже при ошибке
                return False
        # Якщо все добре, зберігаємо нове значення
        self.previous_text = gb.cmb.currentText()
        chars == "."
        pattern = rf"^[{chars}]+$"
        self._focus_processing = False  # обязательно снять блокировку даже при ошибке
        if self.current_groupbox == gb:
            self.current_groupbox = None
        return True

    # нажатие на кнопку Правила
    def on_rules_clicked(self, combo, field_name):
        global rule_invalid
        for name, wrapper in self.gb.items():
            # wrapper = GroupBoxWrapper()
            chck_stat = wrapper.chkb.isChecked()
            if wrapper.cmb is combo:
                wrapper.cmb.setEditable(True)  # текущий делаем редактируемым
                # combo.setEditable(True)
                wrapper.gb.setStyleSheet("background-color: rgb(255, 255, 200);")  # подсветка
            else:
            # #для случая когда поле, а не комбобокс
            #     if wrapper.cmb.isEditable():
            #         # сохранить введённый текст
            #         current_text = wrapper.cmb.currentText().strip()
            #         if current_text:
            #             items = [wrapper.cmb.itemText(i) for i in range(wrapper.cmb.count())]
            #             if current_text not in items:
            #                 wrapper.cmb.addItem(current_text)  # добавляем в список
            #             # получаем индекс добавленного или существующего значения
            #             idx = wrapper.cmb.findText(current_text)
            #             if idx >= 0:
            #                 wrapper.cmb.setCurrentIndex(idx)
            #         # теперь можно выключить редактирование
            #     wrapper.cmb.setEditable(False)
                wrapper.gb.setStyleSheet("background-color: rgb(85, 255, 127);")
        rule_invalid[field_name] = []
        dlg = MyDialog()

        dlg.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        dlg.setModal(True)
        if dlg.exec() == QDialog.Accepted:  # ← проверка, нажата ли OK
            cur_rules = dlg.result  # ← берём результат после закрытия
            # if not entries_rules(wrapper.cmb.currentText(), chck_stat, field_name, entries=cur_rules):
            if not entries_rules(combo.currentText(), chck_stat, field_name, entries=cur_rules):
                self.reject()
        # wrapper.cmb.setFocus()
        combo.setFocus()

    def on_ok_clicked(self):
        """Срабатывает при нажатии кнопки 'Введення' — собирает данные и закрывает диалог."""
        if not self.gb_focus_left_triggered:
            # if not self.on_gb_focus_left():
            if not self.on_gb_focus_left(self.current_groupbox):
                return False
        global rule_invalid
        titles = []
        for name, wrapper in self.gb.items():
            if not name in rule_invalid:
                rule_invalid[name] = []
            if len(rule_invalid[name]) == 0:
                msg = QMessageBox(self)
                msg.setWindowTitle("Підтвердження")
                msg.setText(f"Натискаючи Продовжити ви залишаєте правила створення строки в полі {wrapper.gb.title()} по замовчуванню \"НЕ ПУСТЕ\"\nПРОДОВЖИТИ?")
                msg.setIcon(QMessageBox.Question)
                yes_btn = msg.addButton("Продовжити", QMessageBox.YesRole)
                no_btn = msg.addButton("Скасувати", QMessageBox.NoRole)
                msg.exec()
                if msg.clickedButton() == no_btn:
                    return False

                rule_invalid[name].append("absent")
            if wrapper.chkb.isChecked():
                if wrapper.cmb.currentText() != "":
                    self.result[name] = wrapper.cmb.currentText()
                    if name != 'url_of_page':
                        self.result_fields[name] = wrapper.cmb.currentText()
                else:
                    titles.append(wrapper.gb.title())
        # self.result['fix_enter'] = self.
        if len(titles) > 0:
            QMessageBox.warning(self, f"Поля {titles}", "Обов'язкові дані не введені.")
            return False
        for key, value in rule_invalid.items():
            val_new = []
            for el in value:
                if el[:7] != "localiz":
                    val_new.append(el)
            self.result_invalid[key] = val_new
        # self.result_invalid = rule_invalid
        self.accept()

    def on_cnl_clicked(self):
        # gb = self.sender()
        # if wrapper.cmb.hasFocus():
        #     self.btnCnl.setFocus()
        self.reject()
