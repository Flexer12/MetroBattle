# Импорт библиотек
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem

from windows.components.list_elem_custom import QCustomQWidget


# Класс окна кампании
class TechnologiesShop(QMainWindow):
    # Функция инициализации
    def __init__(self, window, helpers):
        super().__init__()
        self.window = window
        self.helpers = helpers
        self.initUI()

    # Функция инициализации интерфейса
    def initUI(self):
        uic.loadUi('templates/technologies_shop.ui', self)

        # Загрузка иконки
        icon = QIcon('resources/images/icon.ico')
        self.setWindowIcon(icon)

        self.exitAction.triggered.connect(self.helpers['class_app'].close_app)
        self.aboutAppAction.triggered.connect(self.helpers['class_app'].open_about_app)
        self.settingsAppAction.triggered.connect(self.helpers['class_app'].open_settings)
        self.backAction.triggered.connect(self.back)
        self.backPushButton.clicked.connect(self.back)
        self.buyPushButton.clicked.connect(self.buy_technology)

        self.aboutAccountAction.triggered.connect(self.helpers['class_app'].show_info_account)
        self.refresh_technologies()

    # Функция обновления технологий
    def refresh_technologies(self):
        technologies = self.helpers['class_registry'].technologies
        self.shopListWidget.clear()
        self.availabilityListWidget.clear()
        for name, technology in technologies.items():
            myQCustomQWidget = QCustomQWidget()
            myQCustomQWidget.set_text_up(technology['name'] + f' ({technology["cost"]})')
            myQCustomQWidget.set_text_down(technology['description'])
            myQCustomQWidget.set_icon(technology['image'])
            myQListWidgetItem = QListWidgetItem(self.shopListWidget)
            myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
            self.shopListWidget.addItem(myQListWidgetItem)
            self.shopListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)

            if name in self.helpers['class_save_user'].technologies:
                myQCustomQWidget = QCustomQWidget()
                myQCustomQWidget.set_text_up(technology['name'] + f' ({technology["cost"]})')
                myQCustomQWidget.set_text_down(technology['description'])
                myQCustomQWidget.set_icon(technology['image'])
                myQListWidgetItem = QListWidgetItem(self.availabilityListWidget)
                myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
                self.availabilityListWidget.addItem(myQListWidgetItem)
                self.availabilityListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)

        self.levelLabel.setText(f'Уровень: {self.helpers["class_save_user"].level} '
                                f'({self.helpers["class_save_user"].experience})')
        self.budgetLabel.setText(f'Бюджет: {self.helpers["class_save_user"].budget}')

    # Функция покупки технологии
    def buy_technology(self):
        technology = self.shopListWidget.currentRow()
        if technology >= 0:
            technologies = self.helpers['class_registry'].technologies
            i = 0
            for key, value in technologies.items():
                if i == technology:
                    if key not in self.helpers['class_save_user'].technologies:
                        if self.helpers['class_save_user'].budget < value['cost']:
                            self.helpers['class_app'].show_message_box('Недостаточно средств!')
                        else:
                            self.helpers['class_save_user'].budget -= value['cost']
                            self.helpers['class_save_user'].technologies.append(key)
                            self.helpers['class_save_user'].save_data()
                            self.helpers['class_app'].show_message_box('Технология куплена!')
                            self.refresh_technologies()
                    else:
                        self.helpers['class_app'].show_message_box('Технология уже куплена!')
                    break
                i += 1

        else:
            self.helpers['class_app'].show_message_box('Выберите технологию!')

    # Функция выхода в главное меню
    def back(self):
        self.window.show()
        self.close()
