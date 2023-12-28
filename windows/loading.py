# Импортируем библиотеки
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow


# Окно загрузки
class Loading(QMainWindow):
    # Функция иницилизации
    def __init__(self, window_open, helpers):
        super().__init__()
        self.i_loading = None
        self.timer_load = None
        self.k_time = None
        self.time = None
        self.i_progress_bar = 0
        self.timer = None
        self.helpers = helpers
        self.window_open = window_open
        self.initUI()

    # Функция инилизации интерфейса
    def initUI(self):
        uic.loadUi('templates/loading.ui', self)

        # Загрузка иконки
        icon = QIcon('resources/images/icon.ico')
        self.setWindowIcon(icon)

        pixmap = QPixmap("resources/images/background.jpg")
        self.imageLabel.setPixmap(pixmap)

        self.showMaximized()

        # Таймер на 2,5 секунды
        self.time = 2500
        self.i_loading = 0
        self.timer_load = QTimer()
        self.timer_load.timeout.connect(self.update_progress)
        self.timer_load.start(1)

        if self.helpers['class_app'].debug_mode:
            self.time = 200

    # Функция обновления progressBar
    def update_progress(self):
        self.i_loading += 1

        if self.i_loading % (self.time / 100) == 0:
            self.i_progress_bar += 1
            self.loadingProgressBar.setValue(int(self.i_progress_bar))

            if self.windowTitle() == 'Загрузка':
                self.setWindowTitle('Загрузка.')
            elif self.windowTitle() == 'Загрузка.':
                self.setWindowTitle('Загрузка..')
            elif self.windowTitle() == 'Загрузка..':
                self.setWindowTitle('Загрузка...')
            elif self.windowTitle() == 'Загрузка...':
                self.setWindowTitle('Загрузка')

        if int(self.i_progress_bar) == 100:
            self.open_auth()

    # Открытие окна авторизации
    def open_auth(self):
        self.window_open.show()
        self.close()

    # Переопределение метода closeEvent для остановки таймера
    def closeEvent(self, event):
        # Останавливаем таймер
        self.timer_load.stop()
        super().closeEvent(event)
