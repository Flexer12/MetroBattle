# Импорт библиотек
import hashlib

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog

# Импорт классов
from helpers.class_file import ClassFile

# Импорт окон
from windows.settings import Settings
from windows.about_app import AboutApp
from windows.power_characters import PowerCharactersDialog


# Класс настроек и вспомогательных функций для приложения
class ClassApp:
    # Функция инициализации
    def __init__(self, helpers):
        self.helpers = helpers
        if not self.helpers['class_file'].check_file('data/'):
            self.helpers['class_file'].create_dir('data/')

        if not self.helpers['class_file'].check_file('data/about_app.txt'):
            value = """Данное приложение распространяется на бесплатной основе и не несёт коммерческий характер. Приложение в первую очередь рассчитано на удовлетворение досуга и привлечения интереса к играм подобного рода.

Автор проекта: X разработчик
"""
            self.helpers['class_file'].write_file_txt('data/about_app.txt', value)

        if not self.helpers['class_file'].check_file('data/users'):
            self.helpers['class_file'].create_dir('data/users')

        self.settings = {
            'volume_sounds': 0,
            'volume_music': 0,
            'name_app': 'PyBattle'
        }
        debug = ClassFile().read_file_txt("data/debug.txt")
        if not debug:
            ClassFile().write_file_txt("data/debug.txt", "0")
            debug = ClassFile().read_file_txt("data/debug.txt")
        self.debug_mode = bool(int(debug[0]))

    # Функция принятия настроек
    def apply_setting(self, settings):
        print(settings)
        for key, value in settings.items():
            self.settings[key] = value
        print(self.settings)
        reboot = False

        for key, value in settings.items():
            if key == 'debug_mode':
                if ClassFile().read_file_txt("data/debug.txt")[0] != str(value):
                    ClassFile().write_file_txt("data/debug.txt", str(value))
                    reboot = True
            elif isinstance(self.helpers['class_db'].select('settings', column=f"parameter", value=f"'{key}'",
                                                            return_value='one'), tuple):
                self.helpers['class_db'].update('settings', 'value', f"'{value}'", 'parameter', f"'{key}'")
            else:
                type_data = 'str'

                if isinstance(value, int):
                    type_data = 'int'
                self.helpers['class_db'].insert('settings', 'parameter, value, type_data',
                                                f"'{key}', '{value}', '{type_data}'")
        self.load_settings()

        if reboot:
            self.close_app()

    # Функция открытия окна настроек
    def open_settings(self):
        result = Settings(self.helpers).exec_()
        if result == QDialog.Accepted:
            return True
        else:
            return False

    # Функция вызова справки о приложении
    def open_about_app(self):
        result = AboutApp(self.helpers).exec_()
        if result == QDialog.Accepted:
            return True
        else:
            return False

    # Функция вызова окна силы
    def open_power_team(self, characters):
        result = PowerCharactersDialog(characters).exec_()
        if result == QDialog.Accepted:
            return True
        else:
            return False

    # Функция вызова диалогового окна
    def show_message_box(self, text, yes_no=False):
        message_box = QMessageBox()
        message_box.setText(text)
        message_box.setWindowTitle(self.settings['name_app'])
        icon = QIcon('resources/images/icon.ico')
        message_box.setWindowIcon(icon)
        message_box.setIcon(QMessageBox.Information)
        if not yes_no:
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.button(QMessageBox.Ok).setText("Ок")
        else:
            message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            message_box.button(QMessageBox.Ok).setText("Ок")
            message_box.button(QMessageBox.Cancel).setText("Отмена")

        result = message_box.exec_()
        if result == QMessageBox.Ok:
            return True
        else:
            return False

    # Функция генерации хэш строки
    def get_sha1_hash(self, string):
        return hashlib.sha1(string.encode()).hexdigest()

    # Функция показа окна с данными об аккаунте
    def show_info_account(self):
        info = 'У данного аккаунте следующие данные:\n'
        info += 'Почта: ' + self.helpers['class_save_user'].email + '\n'
        info += 'Никнейм: ' + self.helpers['class_save_user'].nickname + '\n'
        info += 'Уровень: ' + str(self.helpers['class_save_user'].level) + '\n'
        info += 'Опыт: ' + str(self.helpers['class_save_user'].experience) + '\n'
        info += 'Бюджет: ' + str(self.helpers['class_save_user'].budget) + '\n'
        self.show_message_box(info)

    # Функция загрузки настроек
    def load_settings(self):
        settings = self.helpers['class_db'].select("settings", return_value='all')
        print(settings)
        for i in settings:
            if i[3] == 'int':
                self.settings[i[1]] = int(i[2])
            elif i[3] == 'str':
                self.settings[i[1]] = i[2]
        self.helpers['class_sound'].set_media_player_volume(self.settings['volume_music'])
        self.helpers['class_sound'].set_sounds_volume(self.settings['volume_sounds'])
        self.debug_mode = bool(int(ClassFile().read_file_txt("data/debug.txt")[0]))

        # Удаляем лишние папки от удаленных пользователей
        users = [i[1] for i in self.helpers['class_db'].select('users', return_value='all')]
        dirs = self.helpers['class_file'].get_dirs('data/users/')
        for i in dirs:
            if i not in users:
                self.helpers['class_file'].delete_dir(f'data/users/{i}')

    # Функция установки стандартных настроек
    def default_settings(self):
        if self.show_message_box('Подтвердите действие!', True):
            print("Очищаем")
            self.helpers['class_file'].delete_dir('data/users/')
            self.helpers['class_file'].delete_file('data/debug.txt')
            self.helpers['class_file'].delete_file('data/data.db')
            self.close_app()

    # Функция стандартных параметров (применяется в том случае, если нет начальных настроек)
    # Проверяется только при запуске приложения
    def default_data(self, password='d033e22ae348aeb5660fc2140aec35850c4da997'):
        # Создаем табличку ролей
        query = """
                CREATE TABLE IF NOT EXISTS posts(
                    id  INTEGER NOT NULL
                        PRIMARY KEY AUTOINCREMENT
                        UNIQUE,
                    name TEXT
                )
                """
        if not self.helpers['class_db'].query_execute(query):
            print("Таблица ролей не создана!")
            return False

        # Очищаем если не очищено
        if not self.helpers['class_db'].delete('posts'):
            print("Таблица должностей не очищена!")
            return False

        # Проверяем есть ли админ, если нет создаем
        res = self.helpers['class_db'].select('posts', column='name', value=f"'Администратор'", return_value='one')
        if not isinstance(res, tuple):
            if not self.helpers['class_db'].insert('posts', 'id, name', "1, 'Администратор'"):
                print("Роль админа не добавлена!")
                return False
        else:
            print("Роль админа присутствует!")
            return False

        # Проверяем есть ли игрок, если нет создаем
        res = self.helpers['class_db'].select('posts', column='name', value=f"'Игрок'", return_value='one')
        if not isinstance(res, tuple):
            if not self.helpers['class_db'].insert('posts', 'id, name', "2, 'Игрок'"):
                print("Роль игрока не добавлена!")
                return False
        else:
            print("Роль игрок присутствует!")
            return False

        # Создаем табличку пользователей
        query = """
                    CREATE TABLE IF NOT EXISTS users(
                        id       INTEGER PRIMARY KEY AUTOINCREMENT
                                         UNIQUE
                                         NOT NULL,
                        email    TEXT    UNIQUE
                                         NOT NULL,
                        password TEXT    NOT NULL,
                        nickname TEXT    NOT NULL
                                         UNIQUE,
                        avatar_path TEXT,
                        post_id  INTEGER REFERENCES posts (id) 
                                         NOT NULL
                    );
                   """
        if not self.helpers['class_db'].query_execute(query):
            print("Таблица пользователей не создана!")
            return False

        # Проверяем есть ли админ, если нет создаем
        res = self.helpers['class_db'].select('users', column='post_id', value=f"1", return_value='one')
        if not isinstance(res, tuple):
            if not self.helpers['class_db'].insert('users', 'email, password, nickname, avatar_path, post_id',
                                                   f"'admin@mail.ru', '{password}', 'admin', '', 1"):
                print("Администратор не создан!")
                return False
        else:
            print("Администратор присутствует!")

        # Создаем табличку сохранений
        query = """
                    CREATE TABLE IF NOT EXISTS saves(
                        id       INTEGER PRIMARY KEY AUTOINCREMENT
                                         UNIQUE
                                         NOT NULL,
                        level      INTEGER  NOT NULL,
                        budget     INTEGER  NOT NULL,
                        experience INTEGER  NOT NULL,
                        units      TEXT, 
                        team       TEXT, 
                        technologies TEXT, 
                        campaign   TEXT,
                        user_id    INTEGER REFERENCES users (id) NOT NULL UNIQUE
                    );
                   """
        if not self.helpers['class_db'].query_execute(query):
            print("Таблица сохранений не создана!")
            return False

        # Проверяем есть ли админ, если нет создаем
        res = self.helpers['class_db'].select('saves', column='user_id', value=f"1", return_value='one')
        if not isinstance(res, tuple):
            last_id = self.helpers['class_db'].select(table='users', column='email', value=f"'admin@mail.ru'",
                                                      return_value='one')[0]
            if not self.helpers['class_db'].insert('saves',
                                                   'level, budget, experience, units, team, technologies, campaign, '
                                                   'user_id', f"1, 0, 0, '', '', '', '', {last_id}"):
                print("Сохранение на создано!")
                return False
        else:
            print("Администратор присутствует!")

        # Создаем табличку настроек
        query = """
                    CREATE TABLE IF NOT EXISTS settings(
                        id       INTEGER PRIMARY KEY AUTOINCREMENT
                                         UNIQUE
                                         NOT NULL,
                        parameter    TEXT NOT NULL,
                        value        TEXT NOT NULL,
                        type_data    TEXT NOT NULL
                    );
                   """
        if not self.helpers['class_db'].query_execute(query):
            print("Таблица настроек не создана!")
            return False
        else:
            res = self.helpers['class_db'].select('settings', column='parameter', value=f"'volume_music'",
                                                  return_value='one')
            if isinstance(res, tuple):
                print('Параметр громкости музыки есть!')
            else:
                if not self.helpers['class_db'].insert('settings', 'parameter, value, type_data',
                                                       "'volume_music', '30', 'int'"):
                    print('Параметр громкости музыки не создан')
                    return False
                else:
                    print('Параметр громкости музыки создан!')

            res = self.helpers['class_db'].select('settings', column='parameter', value=f"'volume_sounds'",
                                                  return_value='one')
            if isinstance(res, tuple):
                print('Параметр громкости звуков есть!')
            else:
                if not self.helpers['class_db'].insert('settings', 'parameter, value, type_data',
                                                       "'volume_sounds', '30', 'int'"):
                    print('Параметр громкости звуков не создан')
                    return False
                else:
                    print('Параметр громкости звуков создан!')

            res = self.helpers['class_db'].select('settings', column='parameter', value=f"'name_app'",
                                                  return_value='one')
            if isinstance(res, tuple):
                print('Параметр названия приложения есть!')
            else:
                if not self.helpers['class_db'].insert('settings', 'parameter, value, type_data',
                                                       "'name_app', 'PyBattle', 'str'"):
                    print('Параметр названия приложения не создан')
                    return False
                else:
                    print('Параметр названия приложения создан!')

        return True

    # Функция закрытия приложения
    def close_app(self):
        QApplication.instance().quit()

    # Функция возвращающая показатели персонажа в виде текста для вывода
    def get_text_character(self, character, technologies):
        text_down = f'Опыт {character["experience"]} + \n'
        text_down += f'Жизнь {character["health"]} + \n'
        technology_text = technologies.get(character['technology'], character['technology'])
        if isinstance(technology_text, dict):
            technology_text = technology_text['name']
        text_down += ('Требуется технология ' +
                      technology_text +
                      '\n')
        text_down += 'Звук выбора: '
        text_down += "Да" if character['sound'] else "Нет"
        text_down += '\n'

        if 'actions' in character.keys():
            for action_name, action in character['actions'].items():
                text_down += '\n'
                text_down += 'Способность: '
                text_down += f'{action["name"]}\n'

                for parameter in action:
                    if 'distance' == parameter:
                        text_down += f'Дальность: {action["distance"]}\n'

                    if 'number' == parameter:
                        text_down += f'Количество выполнений: {action["number"]}\n'

                    if 'accuracy' == parameter:
                        text_down += f'Точность: {action["accuracy"] * 100}%\n'

                    if 'damage' == parameter:
                        text_down += f'Урон: {action["damage"]}\n'

                    if 'value' == parameter:
                        text_down += f'Значение: {action["value"]}\n'

                    if 'mass_action' == parameter:
                        text_down += f'Массовое действие: {"Да" if action["mass_action"] else "Нет"}\n'

                if action['sound']:
                    text_down += f'Звук способности: Да\n'
                else:
                    text_down += f'Звук способности: Нет\n'
        return text_down
