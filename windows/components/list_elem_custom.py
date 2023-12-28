# Импорт библиотек
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout


# Класс своего элемента для листа
class QCustomQWidget(QWidget):
    # Функция инициализации
    def __init__(self, parent=None):
        super(QCustomQWidget, self).__init__(parent)
        self.textQVBoxLayout = QVBoxLayout()
        self.textUpQLabel = QLabel()
        self.textDownQLabel = QLabel()
        self.textUpQLabel.setWordWrap(True)  # Добавляем перенос на новые строчки
        self.textDownQLabel.setWordWrap(True)  # Добавляем перенос на новые строчки
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.textQVBoxLayout.addWidget(self.textDownQLabel)
        self.allQHBoxLayout = QHBoxLayout()
        self.iconQLabel = QLabel()
        self.iconQLabel.setMaximumSize(80, 110)
        self.iconQLabel.setScaledContents(True)
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)

        # Установка стиля текста
        self.textUpQLabel.setStyleSheet('''
            color: rgb(0, 0, 255);
        ''')
        self.textDownQLabel.setStyleSheet('''
            color: rgb(255, 0, 0);
        ''')

    # Функция установки верхнего текста
    def set_text_up(self, text):
        self.textUpQLabel.setText(text)

    # Функция установки нижнего текста
    def set_text_down(self, text):
        self.textDownQLabel.setText(text)

    # Функция установки картинки
    def set_icon(self, imagePath):
        self.iconQLabel.setPixmap(QPixmap(imagePath))
