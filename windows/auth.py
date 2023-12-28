# Импортируем библиотеки
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QLineEdit

# Импортируем окна
from helpers.class_save_user import SaveUser
from windows.main_menu import MainMenu
from windows.reg import Reg


# Класс окна авторизации
class Auth(QMainWindow):
    # Функция иницилизации
    def __init__(self, helpers):
        super().__init__()
        self.main_menu = None
        self.reg = None
        self.helpers = helpers
        self.helpers['class_sound'].play_music("resources/music/menu.mp3")
        self.initUI()

    # Функция инилизации интерфейса
    def initUI(self):
        # Загрузка шаблона
        uic.loadUi('templates/auth.ui', self)

        # Загрузка иконки
        icon = QIcon('resources/images/icon.ico')
        self.setWindowIcon(icon)

        # Установка обработчиков события
        self.regPushButton.clicked.connect(self.open_reg)
        self.enterPushButton.clicked.connect(self.open_enter)
        self.settingsAction.triggered.connect(self.helpers['class_app'].open_settings)
        self.exitPushButton.clicked.connect(self.helpers['class_app'].close_app)
        self.exitAction.triggered.connect(self.helpers['class_app'].close_app)
        self.showPasswordCheckBox.stateChanged.connect(self.change_mode_show_password)
        self.aboutAppAction.triggered.connect(self.helpers['class_app'].open_about_app)

        self.emailLineEdit.textChanged.connect(self.email_validate)
        self.passwordLineEdit.textChanged.connect(self.password_validate)

        self.passwordLineEdit.setEchoMode(QLineEdit.Password)

        # Если тестовый мод
        print(self.helpers['class_app'].debug_mode)
        if self.helpers['class_app'].debug_mode:
            self.usersComboBox.show()
            self.debugEnterPushButton.show()
            self.debugEnterPushButton.clicked.connect(self.open_enter_debug)
            self.update_debug_users()
        else:
            self.usersComboBox.hide()
            self.debugEnterPushButton.hide()

    # Функция обновления пользователей в тестовом поле
    def update_debug_users(self):
        self.usersComboBox.clear()
        users = self.helpers['class_db'].select('users', return_value='all')
        for i in users:
            self.usersComboBox.addItem(i[1])
        print(users)

    # Функция проверки валидации поля email
    def email_validate(self):
        if not self.emailLineEdit.text():
            self.emailLineEdit.setStyleSheet("background-color: red; color: white;")
            return False
        else:
            self.emailLineEdit.setStyleSheet("background-color: white; color: black;")
            return True

    # Функция проверки валидации поля password
    def password_validate(self):
        if not self.passwordLineEdit.text():
            self.passwordLineEdit.setStyleSheet("background-color: red; color: white;")
            return False
        else:
            self.passwordLineEdit.setStyleSheet("background-color: white; color: black;")
            return True

    # Функция перевода режима показа пароля
    def change_mode_show_password(self, state):
        if state == 2:
            self.passwordLineEdit.setEchoMode(QLineEdit.Normal)
        else:
            self.passwordLineEdit.setEchoMode(QLineEdit.Password)

    # Функция открытия окна регистрации
    def open_reg(self):
        self.reg = Reg(self, self.helpers)
        self.reg.show()
        self.hide()

    # Функция открытия окна авторизованного пользователя
    def open_enter(self):
        email = self.emailLineEdit.text()
        password = self.passwordLineEdit.text()
        user = self.helpers['class_db'].select("users", column="email", value=f"'{email}'", return_value='one')
        if isinstance(user, tuple):
            self.emailLineEdit.setStyleSheet("background-color: white; color: black;")
            if user[2] == self.helpers['class_app'].get_sha1_hash(password):
                self.helpers['class_save_user'] = SaveUser(self.helpers, user[0])
                self.helpers['class_app'].show_message_box("Вы вошли в систему!")
                self.passwordLineEdit.setStyleSheet("background-color: white; color: black;")
                self.main_menu = MainMenu(self, self.helpers)
                self.main_menu.show()
                self.hide()
            else:
                self.passwordLineEdit.setStyleSheet("background-color: red; color: white;")
                self.helpers['class_app'].show_message_box("Неверный пароль!")
        else:
            self.emailLineEdit.setStyleSheet("background-color: red; color: white;")
            self.helpers['class_app'].show_message_box("Неверная почта!")

    # Функция открытия окна авторизованного пользователя
    def open_enter_debug(self):
        user = self.helpers['class_db'].select('users', column='email', value=f"'{self.usersComboBox.currentText()}'",
                                               return_value='one')

        if user:
            self.helpers['class_save_user'] = SaveUser(self.helpers, user[0])
            self.helpers['class_app'].show_message_box("Вы вошли в систему!")
            self.passwordLineEdit.setStyleSheet("background-color: white; color: black;")
            self.main_menu = MainMenu(self, self.helpers)
            self.main_menu.show()
            self.hide()
        else:
            self.helpers['class_app'].show_message_box(" Пользователь не найден!")
