# Импорт библиотек
import sys
from PyQt5.QtWidgets import QApplication

# Импорт классов
from helpers.class_app import ClassApp
from helpers.class_db import ClassDB
from helpers.class_file import ClassFile
from helpers.class_sound import ClassSound
from helpers.class_registry import ClassRegistry

# Импорт окон
from windows.loading import Loading
from windows.auth import Auth


# Функция фиксации ошибок
def excepthook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# Старт программы
if __name__ == '__main__':
    sys.excepthook = excepthook
    app = QApplication(sys.argv)

    # Иницилизируем классы помощники и отдаем их окну авторизации
    helpers = dict()
    helpers['class_file'] = ClassFile()
    helpers['class_app'] = ClassApp(helpers)
    helpers['class_db'] = ClassDB('data/data.db')
    helpers['class_registry'] = ClassRegistry(helpers)
    helpers['class_sound'] = ClassSound()
    # Проверяем целостность данных
    if helpers['class_db'].check_connection():
        helpers['class_app'].default_data()
    helpers['class_app'].load_settings()
    # Выводим первое окно, с передачей словаря помощников
    ex = Loading(Auth(helpers), helpers)
    ex.show()

    sys.exit(app.exec_())
