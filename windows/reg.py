# Импортируем библиотеки
import re
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLineEdit


# Класс окна регистрации
class Reg(QMainWindow):
    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    PASSWORD_PATTERN = r"^[a-zA-Z0-9_@/%+-]+$"
    NICKNAME_PATTERN = r"^[a-zA-Z0-9_]+$"

    # Функция иницилизации
    def __init__(self, auth_window, helpers):
        super().__init__()
        self.auth_window = auth_window
        self.helpers = helpers
        self.initUI()

    # Функция инилизации интерфейса
    def initUI(self):
        uic.loadUi('templates/reg.ui', self)

        # Загрузка иконки
        icon = QIcon('resources/images/icon.ico')
        self.setWindowIcon(icon)

        self.regPushButton.clicked.connect(self.reg)
        self.authPushButton.clicked.connect(self.open_auth)
        self.settingsAction.triggered.connect(self.helpers['class_app'].open_settings)
        self.exitPushButton.clicked.connect(self.helpers['class_app'].close_app)
        self.exitAction.triggered.connect(self.helpers['class_app'].close_app)
        self.aboutAppAction.triggered.connect(self.helpers['class_app'].open_about_app)
        self.selectAvatarPushButton.clicked.connect(self.select_avatar)

        self.emailLineEdit.textChanged.connect(self.email_validate)
        self.passwordLineEdit.textChanged.connect(self.password_validate)
        self.nicknameLineEdit.textChanged.connect(self.nickname_validate)
        self.showPasswordCheckBox.stateChanged.connect(self.change_mode_show_password)
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)

        pixmap = QPixmap('resources/images/default_avatar.jpg')
        self.avatarImageLabel.setPixmap(pixmap)

    # Функция проверки валидации поля email
    def email_validate(self):
        if not re.match(Reg.EMAIL_PATTERN, self.emailLineEdit.text()):
            self.emailLineEdit.setStyleSheet("background-color: red; color: white;")
            self.emailStatusLabel.setText(f"Не подходит!")
            return False
        else:
            self.emailStatusLabel.setText(f"")
            self.emailLineEdit.setStyleSheet("background-color: white; color: black;")
            return True

    # Функция проверки валидации поля password
    def password_validate(self):
        password = self.passwordLineEdit.text()

        if ((not re.match(Reg.PASSWORD_PATTERN, password) or len(password) < 4 or len(password) > 20
             or not re.search(r'[A-Z]', password)) or not re.search(r'[a-z]', password)
                or not re.search(r'\d', password)):
            self.passwordLineEdit.setStyleSheet("background-color: red; color: white;")
            self.passwordStatusLabel.setText(f"Не подходит!")
            return False
        else:
            self.passwordStatusLabel.setText(f"")
            self.passwordLineEdit.setStyleSheet("background-color: white; color: black;")
            return True

    # Функция перевода режима показа пароля
    def change_mode_show_password(self, state):
        if state == 2:
            self.passwordLineEdit.setEchoMode(QLineEdit.Normal)
        else:
            self.passwordLineEdit.setEchoMode(QLineEdit.Password)

    # Функция проверки валидации поля password
    def nickname_validate(self):
        nickname = self.nicknameLineEdit.text()

        if not re.match(Reg.NICKNAME_PATTERN, nickname) or len(nickname) < 4 or len(nickname) > 20:
            self.nicknameLineEdit.setStyleSheet("background-color: red; color: white;")
            self.nicknameStatusLabel.setText(f"Не подходит!")
            return False
        else:
            self.nicknameStatusLabel.setText(f"")
            self.nicknameLineEdit.setStyleSheet("background-color: white; color: black;")
            return True

    # Функция выбора аватара
    def select_avatar(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                            'Картинка (*.jpg);;Картинка (*.png)')[0]
        if fname:
            self.avatarTextEdit.setText(fname)
            pixmap = QPixmap(fname)
            self.avatarImageLabel.setPixmap(pixmap)
        else:
            self.avatarTextEdit.setText('')
            self.avatarImageLabel.clear()
            pixmap = QPixmap('resources/images/default_avatar.jpg')
            self.avatarImageLabel.setPixmap(pixmap)

    # Открытие окна авторизации
    def reg(self):
        self.email_validate()
        self.password_validate()
        self.nickname_validate()
        if (self.email_validate() and self.password_validate() and self.nickname_validate()
                and self.helpers['class_db'].check_connection()):
            email = self.emailLineEdit.text()
            password = self.passwordLineEdit.text()
            nickname = self.nicknameLineEdit.text()
            avatar_path = self.avatarTextEdit.toPlainText()
            check = True

            if self.helpers['class_db'].select("users", column="email", value=f"'{email}'", return_value='one'):
                self.helpers['class_app'].show_message_box('Почта уже используется!')
                self.emailLineEdit.setStyleSheet("background-color: red; color: white;")
                check = False

            if check:
                if not self.helpers['class_file'].check_file('data/'):
                    self.helpers['class_file'].create_dir('data/')
                if not self.helpers['class_file'].check_file('data/users/'):
                    self.helpers['class_file'].create_dir('data/users/')

                self.helpers['class_file'].delete_dir(f'data/users/{email}')
                self.helpers['class_file'].create_dir(f'data/users/{email}')

            if self.helpers['class_db'].select("users", column="nickname", value=f"'{nickname}'", return_value='one'):
                self.helpers['class_app'].show_message_box('Никнейм уже используется!')
                self.nicknameLineEdit.setStyleSheet("background-color: red; color: white;")
                check = False

            if check and avatar_path and self.helpers['class_file'].check_file(avatar_path):
                if (not self.helpers['class_file'].copy_file(avatar_path,
                                                             f'data/users/{email}/{avatar_path.split("/")[-1]}')):
                    self.helpers['class_app'].show_message_box('Возникла ошибка при установке аватара!')
                    check = False
                avatar_path = f'data/users/{email}/{avatar_path.split("/")[-1]}'
            else:
                avatar_path = ''

            password = self.helpers['class_app'].get_sha1_hash(password)
            if check and self.helpers['class_db'].insert("users",
                                                         columns="email, password, nickname, avatar_path, post_id",
                                                         values=f"'{email}', '{password}', '{nickname}', "
                                                                f"'{avatar_path}', 2"):
                last_id = self.helpers['class_db'].select(table='users', column='email', value=f"'{email}'",
                                                          return_value='one')[0]

                if self.helpers['class_db'].insert('saves', 'level, budget, experience, units, team, technologies, '
                                                            'campaign, user_id', f"1, 0, 0, '', '', '', '', {last_id}"):
                    print("Пользователь создан")
                else:
                    self.helpers['class_db'].delete('users', 'id', str(last_id))
                    self.helpers['class_app'].show_message_box('Возникла ошибка регистрации пользователя!')

                self.open_auth()
            else:
                self.helpers['class_app'].show_message_box('Возникла ошибка регистрации пользователя!')

    # Открытие окна авторизации
    def open_auth(self):
        self.auth_window.show()
        self.auth_window.update_debug_users()
        self.close()
