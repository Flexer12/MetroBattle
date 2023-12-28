# Импорт библиотек
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem

from windows.components.list_elem_custom import QCustomQWidget


# Класс окна кампании
class CharactersShop(QMainWindow):
    # Функция инициализации
    def __init__(self, window, helpers):
        super().__init__()
        self.window = window
        self.helpers = helpers
        self.initUI()

    # Функция инициализации интерфейса
    def initUI(self):
        uic.loadUi('templates/characters_shop.ui', self)

        # Загрузка иконки
        icon = QIcon('resources/images/icon.ico')
        self.setWindowIcon(icon)

        self.exitAction.triggered.connect(self.helpers['class_app'].close_app)
        self.aboutAppAction.triggered.connect(self.helpers['class_app'].open_about_app)
        self.settingsAppAction.triggered.connect(self.helpers['class_app'].open_settings)
        self.backAction.triggered.connect(self.back)
        self.backPushButton.clicked.connect(self.back)
        self.buyPushButton.clicked.connect(self.buy_character)
        self.activatePushButton.clicked.connect(self.activate_character)
        self.deactivatePushButton.clicked.connect(self.deactivate_character)

        self.aboutAccountAction.triggered.connect(self.helpers['class_app'].show_info_account)
        self.refresh_characters()

    # Функция обновления персонажей
    def refresh_characters(self):
        technologies = self.helpers['class_registry'].technologies
        characters = self.helpers['class_registry'].characters

        self.shopListWidget.clear()
        self.availabilityListWidget.clear()
        self.teamListWidget.clear()
        for name, character in characters.items():
            if character['technology'] in self.helpers['class_save_user'].technologies or character[
                'technology'] == '-':
                myQCustomQWidget = QCustomQWidget()
                myQCustomQWidget.set_text_up(character['name'] + f' ({character["cost"]})')

                text_down = self.helpers['class_app'].get_text_character(character, technologies)

                myQCustomQWidget.set_text_down(text_down)
                myQCustomQWidget.set_icon(character['image'])
                myQListWidgetItem = QListWidgetItem(self.shopListWidget)
                myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
                self.shopListWidget.addItem(myQListWidgetItem)
                self.shopListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)

        if self.helpers['class_save_user'].units:
            pos = 1
            for u_character in self.helpers['class_save_user'].units:
                for name, character in characters.items():
                    if u_character == name:
                        myQCustomQWidget = QCustomQWidget()
                        myQCustomQWidget.set_text_up(f'{pos}) ' + character['name'] + f' ({character["cost"]})')

                        text_down = self.helpers['class_app'].get_text_character(character, technologies)

                        myQCustomQWidget.set_text_down(text_down)
                        myQCustomQWidget.set_icon(character['image'])
                        myQListWidgetItem = QListWidgetItem(self.availabilityListWidget)
                        myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
                        self.availabilityListWidget.addItem(myQListWidgetItem)
                        self.availabilityListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)
                        pos += 1

        if self.helpers['class_save_user'].team:
            pos = 1
            for t_character in self.helpers['class_save_user'].team:
                for name, character in characters.items():
                    if t_character == name:
                        myQCustomQWidget = QCustomQWidget()
                        myQCustomQWidget.set_text_up(f'{pos}) ' + character['name'] + f' ({character["cost"]})')

                        text_down = self.helpers['class_app'].get_text_character(character, technologies)

                        myQCustomQWidget.set_text_down(text_down)
                        myQCustomQWidget.set_icon(character['image'])
                        myQListWidgetItem = QListWidgetItem(self.teamListWidget)
                        myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
                        self.teamListWidget.addItem(myQListWidgetItem)
                        self.teamListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)
                        pos += 1

        self.levelLabel.setText(f'Уровень: {self.helpers["class_save_user"].level} '
                                f'({self.helpers["class_save_user"].experience})')
        self.budgetLabel.setText(f'Бюджет: {self.helpers["class_save_user"].budget}')

    # Функция покупки персонажей
    def buy_character(self):
        character = self.shopListWidget.currentRow()
        if character >= 0:
            characters = self.helpers['class_registry'].characters
            i = 0
            for key, value in characters.items():
                if value['technology'] in self.helpers['class_save_user'].technologies or value['technology'] == '-':
                    if character == i:
                        if self.helpers['class_save_user'].budget < value['cost']:
                            self.helpers['class_app'].show_message_box('Недостаточно средств!')
                        else:
                            self.helpers['class_save_user'].budget -= value['cost']
                            self.helpers['class_save_user'].units.append(key)
                            self.helpers['class_save_user'].save_data()
                            self.helpers['class_app'].show_message_box('Персонаж куплен!')
                            self.refresh_characters()
                        break
                    i += 1
        else:
            self.helpers['class_app'].show_message_box('Выберите персонажа!')

    # Функция активации персонажей
    def activate_character(self):
        character = self.availabilityListWidget.currentRow()
        if character >= 0:
            characters = self.helpers['class_registry'].characters
            for key, value in characters.items():
                if self.helpers['class_save_user'].units[character] == key:
                    if len(self.helpers['class_save_user'].team) >= 6:
                        self.helpers['class_app'].show_message_box('Максимум 6 юнитов в команде!')
                    else:
                        self.helpers['class_save_user'].team.append(key)
                        self.helpers['class_save_user'].units.pop(character)
                        self.helpers['class_save_user'].save_data()
                        self.helpers['class_app'].show_message_box('Персонаж активирован!')
                        self.refresh_characters()
                    break

        else:
            self.helpers['class_app'].show_message_box('Выберите персонажа!')

    # Функция деактивации персонажей
    def deactivate_character(self):
        character = self.teamListWidget.currentRow()
        if character >= 0:
            characters = self.helpers['class_registry'].characters
            for key, value in characters.items():
                if self.helpers['class_save_user'].team[character] == key:
                    self.helpers['class_save_user'].units.append(key)
                    self.helpers['class_save_user'].team.pop(character)
                    self.helpers['class_save_user'].save_data()
                    self.helpers['class_app'].show_message_box('Персонаж деактивирован!')
                    self.refresh_characters()
                    break

        else:
            self.helpers['class_app'].show_message_box('Выберите персонажа!')

    # Функция выхода в главное меню
    def back(self):
        self.window.show()
        self.close()
