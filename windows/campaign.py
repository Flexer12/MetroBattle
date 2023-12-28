# Импорт библиотек
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem

from windows.camaign_map import CampaignMap
# Импорт окон
from windows.characters_shop import CharactersShop
from windows.components.list_elem_custom import QCustomQWidget
from windows.technologies_shop import TechnologiesShop


# Класс окна кампании
class Campaign(QMainWindow):
    # Функция инициализации
    def __init__(self, main_window, helpers):
        super().__init__()
        self.map_window = None
        self.shop = None
        self.main_window = main_window
        self.helpers = helpers
        self.initUI()

    # Функция инициализации интерфейса
    def initUI(self):
        uic.loadUi('templates/campaign.ui', self)

        # Загрузка иконки
        icon = QIcon('resources/images/icon.ico')
        self.setWindowIcon(icon)

        self.exitAction.triggered.connect(self.helpers['class_app'].close_app)
        self.aboutAppAction.triggered.connect(self.helpers['class_app'].open_about_app)
        self.settingsAppAction.triggered.connect(self.helpers['class_app'].open_settings)
        self.backAction.triggered.connect(self.back)
        self.backPushButton.clicked.connect(self.back)
        self.aboutAccountAction.triggered.connect(self.helpers['class_app'].show_info_account)
        self.passPushButton.clicked.connect(self.open_map)

        self.characterPushButton.clicked.connect(self.open_characters_shop)
        self.technologiesPushButton.clicked.connect(self.open_technologies_shop)

        self.refresh_maps()

    # Функция обновления карт
    def refresh_maps(self):
        maps = self.helpers['class_registry'].maps

        self.mapsListWidget.clear()
        for name, map_v in maps.items():
            index_map = int(name.split('.')[0])
            check = False
            if not self.helpers['class_save_user'].campaign:
                if index_map == 1:
                    check = True
            elif int(self.helpers['class_save_user'].campaign[-1]) + 1 >= index_map:
                check = True

            if check:
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

    # Функция открытия окна карты кампании
    def open_map(self):
        map_index = self.mapsListWidget.currentRow()
        if map_index >= 0:
            self.map_window = CampaignMap(self, self.helpers, map_index + 1)
            self.map_window.show()
            self.close()
        else:
            self.helpers['class_app'].show_message_box('Выберите карту для прохождения!')

    # Функция открытия окна магазина персонажей
    def open_characters_shop(self):
        self.shop = CharactersShop(self, self.helpers)
        self.shop.show()
        self.close()

    # Функция открытия окна магазина технологий
    def open_technologies_shop(self):
        self.shop = TechnologiesShop(self, self.helpers)
        self.shop.show()
        self.close()

    # Функция выхода в главное меню
    def back(self):
        self.main_window.show()
        self.main_window.update_fields()
        self.close()
