# Импортируем библиотеки
import random
import re
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLineEdit, QTableWidgetItem, QListWidgetItem

# Импортирование окон
from windows.campaign import Campaign
from windows.components.list_elem_custom import QCustomQWidget
from windows.battle_bots_map import BattleBotsMap


# Окно авторизованного пользователя
class MainMenu(QMainWindow):
    PASSWORD_PATTERN = r"^[a-zA-Z0-9_@/%+-]+$"
    NICKNAME_PATTERN = r"^[a-zA-Z0-9_]+$"

    # Функция иницилизации
    def __init__(self, auth_window, helpers):
        super().__init__()
        self.battle_bot_map = None
        self.campaign = None
        self.auth_window = auth_window
        self.helpers = helpers
        self.initUI()

    # Функция инилизации интерфейса
    def initUI(self):
        posts_id = self.helpers['class_save_user'].post_id

        # Импортируем шаблоны в зависимости от роли пользователя
        if posts_id == 1:
            uic.loadUi('templates/main_menu_admin.ui', self)
        elif posts_id == 2:
            uic.loadUi('templates/main_menu.ui', self)

        # Загрузка иконки
        icon = QIcon('resources/images/icon.ico')
        self.setWindowIcon(icon)

        self.exitPushButton.clicked.connect(self.helpers['class_app'].close_app)
        self.exitAction.triggered.connect(self.helpers['class_app'].close_app)

        # Обработчики открытия окон
        self.logoutAction.triggered.connect(self.open_auth)
        self.aboutAppAction.triggered.connect(self.helpers['class_app'].open_about_app)
        self.settingsAction.triggered.connect(self.helpers['class_app'].open_settings)

        self.authPushButton.clicked.connect(self.open_auth)
        self.campaignPushButton.clicked.connect(self.open_campaign_window)
        self.battleBotsPushButton.clicked.connect(self.open_battle_bots_window)

        # Обработчики профиля
        self.selectAvatarPushButton.clicked.connect(self.select_avatar)
        self.deleteAccountPushButton.clicked.connect(self.delete_account)
        self.applyDataUserPushButton.clicked.connect(self.update_data_account)
        self.updateDataPushButton.clicked.connect(self.update_fields)

        self.showPasswordCheckBox.stateChanged.connect(self.change_mode_show_password)
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        self.showOldPasswordCheckBox.stateChanged.connect(self.change_mode_show_old_password)
        self.oldPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.passwordLineEdit.textChanged.connect(self.password_validate)
        self.nicknameLineEdit.textChanged.connect(self.nickname_validate)

        self.newGameAction.triggered.connect(self.new_game)

        self.get_save_user()

        # Функционал окна администратора
        if posts_id == 1:
            self.tabWidget.setCurrentIndex(0)

            self.defaultAction.triggered.connect(self.helpers['class_app'].default_settings)

            # Обработчики профиля
            self.addBudgetPushButton.clicked.connect(self.add_budget)
            self.reduceBudgetPushButton.clicked.connect(self.reduce_budget)
            self.addExperiencePushButton.clicked.connect(self.add_experience)
            self.reduceExperiencePushButton.clicked.connect(self.reduce_experience)

            # Обработчики вкладки учета пользователей
            self.refreshUserPushButton.clicked.connect(self.refresh_users_table)
            self.deleteUserPushButton.clicked.connect(self.delete_user)
            self.tabWidget.currentChanged.connect(self.refresh_users_table)
            # Обработчики вкладки технологий
            self.tabWidget.currentChanged.connect(self.refresh_technologies)
            self.refreshTechnologiesPushButton.clicked.connect(self.refresh_technologies)
            # Обработчики вкладки персонажей
            self.tabWidget.currentChanged.connect(self.refresh_characters)
            self.refreshCharactersPushButton.clicked.connect(self.refresh_characters)
            # Обработчики вкладки карт
            self.tabWidget.currentChanged.connect(self.refresh_maps)
            self.refreshMapsPushButton.clicked.connect(self.refresh_maps)
            # Обработчики вкладки блоков
            self.tabWidget.currentChanged.connect(self.refresh_blocks)
            self.refreshBlocksPushButton.clicked.connect(self.refresh_blocks)

        self.update_fields()

    ### Функции профиля
    # Получение данных о пользователе
    def get_save_user(self):
        return self.helpers['class_db'].select("saves", column="user_id", value=self.helpers['class_save_user'].id,
                                               return_value='one')

    # Функция обнуления игровых данных пользователя
    def new_game(self):
        self.helpers['class_save_user'].level = 1
        self.helpers['class_save_user'].budget = 0
        self.helpers['class_save_user'].experience = 0
        self.helpers['class_save_user'].units = ''
        self.helpers['class_save_user'].team = ''
        self.helpers['class_save_user'].campaign = ''
        self.helpers['class_save_user'].technologies = ''
        self.helpers['class_save_user'].save_data()
        self.update_fields()

    # Функция обновления полей
    def update_fields(self):
        self.helpers['class_save_user'].select_user(self.helpers['class_save_user'].id)
        self.mainMenuGroupBox.setTitle(self.helpers['class_app'].settings['name_app'])
        self.profileGroupBox.setTitle(f"{self.helpers['class_save_user'].nickname} "
                                      f"({self.helpers['class_save_user'].level} уровень)")
        self.budgetLabel.setText(f"Бюджет: {self.helpers['class_save_user'].budget}")
        self.experienceLabel.setText(f"Опыт: {self.helpers['class_save_user'].experience}/"
                                     f"{self.helpers['class_save_user'].experience_up}")
        self.emailLabel.setText(f"Почта: {self.helpers['class_save_user'].email}")

        self.passwordLineEdit.clear()
        self.oldPasswordLineEdit.clear()
        self.passwordLineEdit.setStyleSheet("background-color: white; color: black;")
        self.oldPasswordLineEdit.setStyleSheet("background-color: white; color: black;")
        font = QFont("MS Shell Dlg 2", 11)
        font.setBold(True)
        self.passwordLineEdit.setFont(font)
        self.oldPasswordLineEdit.setFont(font)

        if self.helpers['class_save_user'].avatar_path:
            pixmap = QPixmap(self.helpers['class_save_user'].avatar_path)
            self.avatarLabel.setPixmap(pixmap)
        else:
            pixmap = QPixmap('resources/images/default_avatar.jpg')
            self.avatarLabel.setPixmap(pixmap)

        self.avatarLineEdit.setText(self.helpers['class_save_user'].avatar_path)
        self.nicknameLineEdit.setText(self.helpers['class_save_user'].nickname)
        self.nicknameLineEdit.setStyleSheet("background-color: white; color: black; font")
        self.nicknameLineEdit.setFont(font)

    # Функция выбора аватара
    def select_avatar(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                            'Картинка (*.jpg);;Картинка (*.png)')[0]
        if fname:
            self.avatarLineEdit.setText(fname)
            pixmap = QPixmap(fname)
            self.avatarLabel.setPixmap(pixmap)
        else:
            self.avatarLineEdit.setText('')
            self.avatarLabel.clear()
            pixmap = QPixmap('resources/images/default_avatar.jpg')
            self.avatarLabel.setPixmap(pixmap)

    # Функция удаления аккаунта
    def delete_account(self):
        if self.helpers['class_app'].show_message_box('Подтвердите действие!', True):
            self.helpers['class_db'].delete('saves', column='user_id', value=self.helpers['class_save_user'].id)
            self.helpers['class_db'].delete('users', column='id', value=self.helpers['class_save_user'].id)
            self.helpers['class_file'].delete_dir(f'data/users/{self.helpers["class_save_user"].email}')
            self.auth_window.show()
            self.helpers['class_db'].default_data()
            self.auth_window.update_debug_users()

    # Функция принятия новых данных пользователя
    def update_data_account(self):
        # Обработка нового аватара
        if self.avatarLineEdit.text() != self.helpers['class_save_user'].avatar_path:
            if not self.helpers['class_file'].check_file('data/'):
                self.helpers['class_file'].create_dir('data/')
            if not self.helpers['class_file'].check_file('data/users/'):
                self.helpers['class_file'].create_dir('data/users/')
            if not self.helpers['class_file'].check_file(f'data/users/{self.helpers["class_save_user"].email}'):
                self.helpers['class_file'].create_dir(f'data/users/{self.helpers["class_save_user"].email}')

            if self.helpers['class_file'].check_file(self.avatarLineEdit.text()):
                if (not self.helpers['class_file'].copy_file(self.avatarLineEdit.text(),
                                                             f'data/users/{self.helpers["class_save_user"].email}/' +
                                                             f'{self.avatarLineEdit.text().split("/")[-1]}')):
                    self.helpers['class_app'].show_message_box('Возникла ошибка при установке аватара!')
                else:
                    self.helpers['class_save_user'].avatar_path = (
                            f'data/users/{self.helpers["class_save_user"].email}/' +
                            f'{self.avatarLineEdit.text().split("/")[-1]}')
                    self.helpers['class_save_user'].save_data()
                    self.helpers['class_app'].show_message_box('Аватар изменён!')
            elif self.avatarLineEdit.text() == '':
                self.helpers['class_save_user'].avatar_path = ''
                self.helpers['class_save_user'].save_data()

        # Обработка нового пароля
        old_password = self.oldPasswordLineEdit.text()
        if old_password:
            if self.helpers['class_app'].get_sha1_hash(old_password) == self.helpers['class_save_user'].password:
                if self.password_validate():
                    self.helpers['class_save_user'].password = (
                        self.helpers['class_app'].get_sha1_hash(self.passwordLineEdit.text()))
                    self.helpers['class_save_user'].save_data()
                    self.helpers['class_app'].show_message_box('Пароль обновлён!')
            else:
                self.helpers['class_app'].show_message_box('Введен не правильный текущий пароль!')
        else:
            self.passwordLineEdit.clear()

        # Обработка нового никнейма
        if self.nicknameLineEdit.text() != self.helpers['class_save_user'].nickname:
            if self.nickname_validate():
                self.helpers['class_save_user'].nickname = self.nicknameLineEdit.text()
                self.helpers['class_save_user'].save_data()
                self.helpers['class_app'].show_message_box('Никнейм изменён!')
            else:
                self.helpers['class_app'].show_message_box('Не корректный никнейм!')

        self.update_fields()

    # Функция добавления денег пользователю
    def add_budget(self):
        self.helpers["class_save_user"].budget += 1000
        self.helpers["class_save_user"].save_data()
        self.update_fields()

    # Функция убавления денег пользователя
    def reduce_budget(self):
        self.helpers["class_save_user"].budget -= 1000
        self.helpers["class_save_user"].save_data()
        self.update_fields()

    # Функция добавления опыта пользователю
    def add_experience(self):
        self.helpers["class_save_user"].experience += 500
        self.helpers["class_save_user"].save_data()
        self.update_fields()

    # Функция убавления опыта пользователя
    def reduce_experience(self):
        self.helpers["class_save_user"].experience -= 500
        self.helpers["class_save_user"].save_data()
        self.update_fields()

    # Функция проверки валидации поля password
    def password_validate(self):
        password = self.passwordLineEdit.text()

        if ((not re.match(MainMenu.PASSWORD_PATTERN, password) or len(password) < 4 or len(password) > 20
             or not re.search(r'[A-Z]', password)) or not re.search(r'[a-z]', password)
                or not re.search(r'\d', password)):
            self.passwordLineEdit.setStyleSheet("background-color: red; color: white;")
            font = QFont("MS Shell Dlg 2", 11)
            font.setBold(True)
            self.passwordLineEdit.setFont(font)
            return False
        else:
            self.passwordLineEdit.setStyleSheet("background-color: white; color: black;")
            font = QFont("MS Shell Dlg 2", 11)
            font.setBold(True)
            self.passwordLineEdit.setFont(font)
            return True

    # Функция проверки валидации поля password
    def nickname_validate(self):
        nickname = self.nicknameLineEdit.text()

        if not re.match(MainMenu.NICKNAME_PATTERN, nickname) or len(nickname) < 4 or len(nickname) > 20:
            self.nicknameLineEdit.setStyleSheet("background-color: red; color: white;")
            font = QFont("MS Shell Dlg 2", 11)
            font.setBold(True)
            self.nicknameLineEdit.setFont(font)
            return False
        else:
            self.nicknameLineEdit.setStyleSheet("background-color: white; color: black;")
            font = QFont("MS Shell Dlg 2", 11)
            font.setBold(True)
            self.nicknameLineEdit.setFont(font)
            return True

    # Функция показа старого пароля
    def change_mode_show_old_password(self, state):
        if state == 2:
            self.oldPasswordLineEdit.setEchoMode(QLineEdit.Normal)
        else:
            self.oldPasswordLineEdit.setEchoMode(QLineEdit.Password)

    # Функция показа пароля
    def change_mode_show_password(self, state):
        if state == 2:
            self.passwordLineEdit.setEchoMode(QLineEdit.Normal)
        else:
            self.passwordLineEdit.setEchoMode(QLineEdit.Password)

    ### Функции открытия окон
    # Открытие окна авторизации
    def open_auth(self):
        self.auth_window.show()
        self.helpers['class_save_user'] = None
        self.close()

    # Открытие окна кампании
    def open_campaign_window(self):
        self.campaign = Campaign(self, self.helpers)
        self.campaign.show()
        self.close()

    # Открытие окна моделирования битвы ботов
    def open_battle_bots_window(self):
        len_bot_maps = len(self.helpers['class_registry'].bots_maps)
        if len_bot_maps > 0:
            self.battle_bot_map = BattleBotsMap(self, self.helpers, random.randint(1, len_bot_maps))
            self.battle_bot_map.show()
            self.close()

    ### Функции вкладки менеджера пользователей
    # Фиксация вкладки, которая была открыта
    def tab_changed(self, index):
        if index == 1:
            self.refresh_users_table()

    # Функция обновления таблицы пользователей
    def refresh_users_table(self):
        query = """
        SELECT users.id, users.email, users.nickname, users.avatar_path, posts.name as post_name, saves.level, 
        saves.budget, saves.experience, saves.units, saves.team, saves.technologies, saves.campaign
FROM users
JOIN posts ON users.post_id = posts.id
JOIN saves ON users.id = saves.user_id"""
        users = self.helpers['class_db'].query_execute(query, return_value='all')

        self.usersTableWidget.setColumnCount(0)
        self.usersTableWidget.setRowCount(0)
        if users:
            # Заполним размеры таблицы
            self.usersTableWidget.setColumnCount(len(users[0]))
            self.usersTableWidget.setHorizontalHeaderLabels(["Идентификатор", "Почта", "Никнейм", "Аватар", "Роль",
                                                             "Уровень", "Бюджет", "Опыт", "Юниты", "Команда",
                                                             "Технологии", "Кампания"])
            # Заполняем таблицу элементами
            for i, row in enumerate(users):
                self.usersTableWidget.setRowCount(self.usersTableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.usersTableWidget.setItem(i, j, QTableWidgetItem(str(elem)))

    # Функция вызова окна для удаления пользователя
    def delete_user(self):
        if self.usersTableWidget.selectedItems():
            id = self.usersTableWidget.item(self.usersTableWidget.selectedItems()[0].row(), 0).text()
            email = self.usersTableWidget.item(self.usersTableWidget.selectedItems()[0].row(), 0).text()

            if int(id) == self.helpers['class_save_user'].id:
                self.helpers['class_app'].show_message_box('Удаление текущего аккаунта, происходит в главной вкладке!')
            elif self.helpers['class_app'].show_message_box('Подтвердите действие!', True):
                self.helpers['class_db'].delete('saves', column='user_id', value=id)
                self.helpers['class_db'].delete('users', column='id', value=id)
                self.helpers['class_file'].delete_dir(f'data/users/{email}')
                self.auth_window.update_debug_users()
                self.refresh_users_table()

    ### Функции вкладки технологий
    # Функция обновления технологий
    def refresh_technologies(self):
        technologies = self.helpers['class_registry'].technologies
        self.technologiesListWidget.clear()
        for name, technology in technologies.items():
            myQCustomQWidget = QCustomQWidget()
            myQCustomQWidget.set_text_up(technology['name'] + f' ({technology["cost"]})')
            myQCustomQWidget.set_text_down(technology['description'])
            myQCustomQWidget.set_icon(technology['image'])
            myQListWidgetItem = QListWidgetItem(self.technologiesListWidget)
            myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
            self.technologiesListWidget.addItem(myQListWidgetItem)
            self.technologiesListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)

    ### Функции вкладки персонажей
    # Функция обновления персонажей
    def refresh_characters(self):
        technologies = self.helpers['class_registry'].technologies
        characters = self.helpers['class_registry'].characters

        self.charactersListWidget.clear()
        for name, character in characters.items():
            myQCustomQWidget = QCustomQWidget()
            myQCustomQWidget.set_text_up(character['name'] + f' ({character["cost"]})')

            text_down = self.helpers['class_app'].get_text_character(character, technologies)

            myQCustomQWidget.set_text_down(text_down)
            myQCustomQWidget.set_icon(character['image'])
            myQListWidgetItem = QListWidgetItem(self.charactersListWidget)
            myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
            self.charactersListWidget.addItem(myQListWidgetItem)
            self.charactersListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)

    ### Функции вкладки карт
    # Функция обновления карт
    def refresh_maps(self):
        maps = self.helpers['class_registry'].maps

        self.mapsListWidget.clear()
        for name, map_v in maps.items():
            myQCustomQWidget = QCustomQWidget()
            myQCustomQWidget.set_text_up(map_v['name'])
            text_down = f'Опыт {map_v["experience"]} \n'
            text_down += f'Награда {map_v["prize"]} \n'
            text_down += 'Описания: ' + map_v['description'] + '\n'

            myQCustomQWidget.set_text_down(text_down)
            myQCustomQWidget.set_icon(map_v['image'])
            myQListWidgetItem = QListWidgetItem(self.mapsListWidget)
            myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
            self.mapsListWidget.addItem(myQListWidgetItem)
            self.mapsListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)

    ### Функции вкладки блоков
    # Функция обновления блоков
    def refresh_blocks(self):
        blocks = self.helpers['class_registry'].blocks

        self.blocksListWidget.clear()
        for name, block in blocks.items():
            myQCustomQWidget = QCustomQWidget()
            myQCustomQWidget.set_text_up(block['name'])
            text_down = f'Проходимость {"Да" if block["passability"] else "Нет"} \n'
            text_down += f'Видимость через блок {"Да" if block["transparency"] else "Нет"} \n'
            myQCustomQWidget.set_text_down(text_down)
            myQCustomQWidget.set_icon(block['image'])
            myQListWidgetItem = QListWidgetItem(self.blocksListWidget)
            myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
            self.blocksListWidget.addItem(myQListWidgetItem)
            self.blocksListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)
