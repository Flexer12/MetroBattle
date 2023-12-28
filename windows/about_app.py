# Импорт библиотек
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QDialogButtonBox


# Инициализация класса
class AboutApp(QDialog):
    # Функция инициализации
    def __init__(self, helpers):
        super().__init__()
        self.helpers = helpers
        self.initUI()

    # Функция инилизации интерфейса
    def initUI(self):
        # Загрузка шаблона
        uic.loadUi('templates/about_app.ui', self)

        # Загрузка иконки
        icon = QIcon('resources/images/icon.ico')
        self.setWindowIcon(icon)

        self.buttonBox.button(QDialogButtonBox.Ok).setText("Ок")

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.nameLabel.setText(self.helpers['class_app'].settings['name_app'])
        pixmap = QPixmap("resources/images/background.jpg")
        self.logoLabel.setPixmap(pixmap)

        self.infoTextEdit.setText(''.join(self.helpers['class_file'].read_file_txt('data/about_app.txt')))
