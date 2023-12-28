# Импорт библиотек
import random

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont
from PyQt5.QtWidgets import QMainWindow, QLabel


# Класс Label принимающего событие нажатия
class ClickedLabel(QLabel):
    clicked = pyqtSignal()

    # Функция фиксирующая события мышки
    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.clicked.emit()


# Класс окна карты кампании
class CampaignMap(QMainWindow):
    # Функции инициализации
    def __init__(self, window, helpers, map_id):
        super().__init__()
        self.next = False
        self.start = False
        self.queue = 0
        self.labels = []
        self.size_m = None
        self.size_n = None
        self.window = window
        self.helpers = helpers
        self.map_id = map_id
        self.active_character = None
        self.active_action = None
        self.last_point = (-1, -1)

        self.groups = ['player', 'enemy_1', 'enemy_2']
        self.groups_dict = {
            'player': 'Игрок',
            'enemy_1': 'Противник 1',
            'enemy_2': 'Противник 2'
        }
        self.map_matrix = None
        self.map_data = None

        self.characters = {}
        self.cell_size_height = 120
        self.cell_size_width = 75
        self.font_size = 50
        self.time_speed = 200

        self.initUI()
        self.load_map()

        # Создаем и настраиваем таймер
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start()

    # Функция инициализации интерфейса
    def initUI(self):
        uic.loadUi('templates/campaign_map.ui', self)

        # Загрузка иконки
        icon = QIcon('resources/images/icon.ico')
        self.setWindowIcon(icon)

        self.exitAction.triggered.connect(self.helpers['class_app'].close_app)
        self.aboutAppAction.triggered.connect(self.helpers['class_app'].open_about_app)
        self.settingsAppAction.triggered.connect(self.helpers['class_app'].open_settings)
        self.showPowerTeamAction.triggered.connect(self.show_team_power)
        self.showPowerEnemyAction.triggered.connect(self.show_enemy_power)
        self.backAction.triggered.connect(self.back)

        self.setSizeGridPushButton.clicked.connect(self.set_size_cells)
        self.actionsComboBox.setEnabled(False)
        self.activeActionPushButton.hide()
        self.passPushButton.hide()
        self.activeActionPushButton.clicked.connect(self.click_action)

        self.startPushButton.clicked.connect(self.start_game)
        self.backPushButton.clicked.connect(self.back)
        self.passPushButton.clicked.connect(self.pass_queue)

    # Функция загрузки карты
    def load_map(self):
        for group in self.groups:
            self.characters[group] = []
        for m in self.helpers['class_registry'].maps:
            if str(self.map_id) == m.split('.')[0]:
                self.map_matrix = self.helpers['class_file'].read_file_txt(f'resources/game/maps/{m}/map.csv')
                self.map_matrix = [i.replace('\n', '') for i in self.map_matrix]
                self.map_matrix = [i for i in self.map_matrix if i]
                self.map_matrix = [i.split(';') for i in self.map_matrix]

                self.map_data = self.helpers['class_file'].get_file_dict(f'resources/game/maps/{m}/characteristic.txt')
                if self.helpers['class_file'].check_file(f'resources/game/maps/{m}/music.mp3'):
                    self.helpers['class_sound'].play_music(f'resources/game/maps/{m}/music.mp3')
                else:
                    print('музыки нет')
                self.size_n = len(self.map_matrix)
                if self.size_n:
                    self.size_m = len(self.map_matrix[0])
                else:
                    self.size_m = 0
                self.map_matrix = [[i.split(',') for i in m] for m in self.map_matrix]

                for i in range(self.size_n):
                    for j in range(self.size_m):
                        for block in self.helpers['class_registry'].blocks:
                            if block in self.map_matrix[i][j]:
                                index = self.map_matrix[i][j].index(block)
                                self.map_matrix[i][j][index] = self.helpers['class_registry'].blocks[block].copy()
                                self.map_matrix[i][j][index]['type_object'] = 'block'

                        for character in self.helpers['class_registry'].characters:
                            for group in self.groups:
                                # Подставляем команду
                                for i_cell, cell in enumerate(self.map_matrix[i][j]):
                                    for index in range(1, 7):
                                        if cell == f'player_{index}':
                                            if len(self.helpers["class_save_user"].team) > index - 1:
                                                self.map_matrix[i][j][
                                                    i_cell] = f'player_{self.helpers["class_save_user"].team[index - 1]}'
                                            continue
                                        elif isinstance(cell, str) and 'player' in cell:
                                            pass

                                # Добавляем персонажей
                                group_character = f'{group}_{character}'
                                if group_character in self.map_matrix[i][j]:
                                    index = self.map_matrix[i][j].index(group_character)

                                    if isinstance(self.map_matrix[i][j][index], str):
                                        self.map_matrix[i][j][index] = self.helpers['class_registry'].characters[
                                            character].copy()
                                        self.map_matrix[i][j][index]['character'] = character
                                        self.map_matrix[i][j][index]['type_object'] = group
                                        self.characters[group].append(self.map_matrix[i][j][index])
                                        self.characters[group][-1]['i'] = i
                                        self.characters[group][-1]['j'] = j

                self.labels = [[] for i in range(self.size_n)]
                self.render_map()

    # Установка способности
    def set_combobox(self, action=None, index=None):
        if index:
            self.actionsComboBox.setCurrentIndex(index)
        elif action and self.active_character:
            i = 0
            for key, value in self.active_character['actions'].items():
                if value == action:
                    self.actionsComboBox.setCurrentIndex(i)
                    break
                i += 1

    # Функция отрисовки карты
    def render_map(self):
        new = False
        if self.labels == [[] for i in range(self.size_n)]:
            new = True
        # Установка настроек на панели
        self.fontSpinBox.setValue(self.font_size)
        self.heightSpinBox.setValue(self.cell_size_height)
        self.widthSpinBox.setValue(self.cell_size_width)
        self.speedTimeSpinBox.setValue(self.time_speed)

        # Позиция персонажей всегда обновляется при рендере
        for group in self.groups:
            self.characters[group] = []

        self.scrollAreaWidgetContents.resize(self.cell_size_width * self.size_m, self.cell_size_height * self.size_n)
        for i in range(self.size_n):
            for j in range(self.size_m):
                if new:
                    self.labels[i].append(ClickedLabel(self.scrollAreaWidgetContents))
                self.labels[i][j].setFixedSize(self.cell_size_width, self.cell_size_height)
                self.labels[i][j].move(self.cell_size_width * j, self.cell_size_height * i)
                self.labels[i][j].setAlignment(Qt.AlignCenter)
                self.labels[i][j].setScaledContents(True)
                self.labels[i][j].setText(f"{i}, {j}")
                # Рисуем текстуры если они есть
                for element in self.map_matrix[i][j]:
                    if isinstance(element, dict) and 'type_object' in element.keys():
                        if element['type_object'] == 'block':
                            pixmap = QPixmap(element['image'])
                            if 'select_blue' in self.map_matrix[i][j]:
                                # Получение ширины и высоты изначальной картинки
                                width = pixmap.width()
                                height = pixmap.height()

                                # Расчет размеров и координат красного квадратика
                                square_width = int(width * 0.2)
                                square_height = int(height * 0.2)

                                # Создание новой картинки с добавленным красным квадратиком
                                new_pixmap = QPixmap(width, height)
                                new_pixmap.fill(Qt.transparent)

                                # Копирование исходной картинки на новую картинку
                                painter = QPainter(new_pixmap)
                                painter.drawPixmap(0, 0, pixmap)

                                painter.setPen(Qt.blue)
                                painter.setBrush(Qt.blue)

                                if self.groups[self.queue] == 'player':
                                    painter.setPen(Qt.green)
                                    painter.setBrush(Qt.green)
                                elif self.groups[self.queue] == 'enemy_1':
                                    painter.setPen(Qt.red)
                                    painter.setBrush(Qt.red)
                                elif self.groups[self.queue] == 'enemy_2':
                                    painter.setPen(Qt.yellow)
                                    painter.setBrush(Qt.yellow)
                                else:
                                    painter.setPen(Qt.white)
                                    painter.setBrush(Qt.white)

                                painter.drawRect(0, 0, square_width, square_height)
                                painter.end()
                                pixmap = new_pixmap

                            self.labels[i][j].setPixmap(pixmap)

                        if element['type_object'] in self.groups:
                            if element['health'] > 0:
                                self.characters[element['type_object']].append(element.copy())
                                self.characters[element['type_object']][-1]['i'] = i
                                self.characters[element['type_object']][-1]['j'] = j

                                pixmap = QPixmap(element['image'])

                                # Получение ширины и высоты изначальной картинки
                                width = pixmap.width()
                                height = pixmap.height()

                                if 'select_blue' in self.map_matrix[i][j]:
                                    # Расчет размеров и координат красного квадратика
                                    square_width = int(width * 0.2)
                                    square_height = int(height * 0.2)

                                    # Создание новой картинки с добавленным красным квадратиком
                                    new_pixmap = QPixmap(width, height)
                                    new_pixmap.fill(Qt.transparent)

                                    # Копирование исходной картинки на новую картинку
                                    painter = QPainter(new_pixmap)
                                    painter.drawPixmap(0, 0, pixmap)

                                    painter.setPen(Qt.blue)
                                    painter.setBrush(Qt.blue)

                                    if self.groups[self.queue] == 'player':
                                        painter.setPen(Qt.green)
                                        painter.setBrush(Qt.green)
                                    elif self.groups[self.queue] == 'enemy_1':
                                        painter.setPen(Qt.red)
                                        painter.setBrush(Qt.red)
                                    elif self.groups[self.queue] == 'enemy_2':
                                        painter.setPen(Qt.yellow)
                                        painter.setBrush(Qt.yellow)
                                    else:
                                        painter.setPen(Qt.white)
                                        painter.setBrush(Qt.white)

                                    painter.drawRect(0, 0, square_width, square_height)
                                    painter.end()
                                    pixmap = new_pixmap

                                # Расчет размеров и координат красного квадратика
                                square_width = int(width * 0.4)
                                square_height = int(height * 0.15)
                                square_x = width - square_width
                                square_y = height - square_height

                                # Создание новой картинки с добавленным красным квадратиком
                                new_pixmap = QPixmap(width, height)
                                new_pixmap.fill(Qt.transparent)

                                # Копирование исходной картинки на новую картинку
                                painter = QPainter(new_pixmap)
                                painter.drawPixmap(0, 0, pixmap)

                                # Рисование красного квадратика
                                # Маркеры распознавания персонажей
                                if element['type_object'] == 'player':
                                    painter.setPen(Qt.green)
                                    painter.setBrush(Qt.green)
                                elif element['type_object'] == 'enemy_1':
                                    painter.setPen(Qt.red)
                                    painter.setBrush(Qt.red)
                                elif element['type_object'] == 'enemy_2':
                                    painter.setPen(Qt.yellow)
                                    painter.setBrush(Qt.yellow)
                                else:
                                    painter.setPen(Qt.white)
                                    painter.setBrush(Qt.white)

                                painter.drawRect(square_x, square_y, square_width, square_height)
                                health = element['health']
                                painter.setPen(Qt.black)
                                font = QFont()
                                font.setPointSize(self.font_size)
                                painter.setFont(font)
                                painter.drawText(square_x, square_y, square_width, square_height, Qt.AlignCenter,
                                                 str(health))

                                painter.end()

                                self.labels[i][j].setPixmap(new_pixmap)
                            else:
                                if element['type_object'] != 'player':
                                    self.helpers['class_save_user'].budget += element['cost'] // random.randint(2, 3)
                                    self.helpers['class_save_user'].experience += element['experience']
                                    self.helpers['class_save_user'].save_data()
                                else:
                                    index_rem = self.helpers['class_save_user'].team.index(element['character'])
                                    if index_rem >= 0:
                                        self.helpers['class_save_user'].team.pop(index_rem)
                                        self.helpers['class_save_user'].save_data()
                                self.map_matrix[i][j].remove(element)
                                self.helpers['class_sound'].play_sound('resources/music/dead.mp3')
                    elif self.active_action is None and 'select' in element:
                        self.map_matrix[i][j].remove(element)
                self.labels[i][j].x = i
                self.labels[i][j].y = j
                self.labels[i][j].clicked.connect(self.click)

    # Функция вызываемая при нажатии на клетку
    def click(self):
        x = self.sender().y
        y = self.sender().x
        if not self.start or self.last_point == (x, y) or self.queue != 0:
            return
        self.last_point = (x, y)

        print(self.sender().x, self.sender().y)
        self.select_cell(x, y)

    # Функция нанесения урона целой группе
    def all_group_damage(self, group, action):
        for character in self.characters[group]:
            i = character['i']
            j = character['j']
            for index, cell in enumerate(self.map_matrix[i][j]):
                if isinstance(cell, dict) and cell['type_object'] == group and action['type'] == 'damage':
                    for i_action in range(self.active_action['number']):
                        if random.random() <= self.active_action['accuracy']:
                            self.map_matrix[i][j][index]['health'] -= random.choice(self.active_action['damage'])

    # Функция лечения целой группы
    def all_group_treatment(self, group, action):
        for character in self.characters[group]:
            i = character['i']
            j = character['j']
            for index, cell in enumerate(self.map_matrix[i][j]):
                if isinstance(cell, dict) and cell['type_object'] == group and action['type'] == 'regeneration':
                    for i_action in range(self.active_action['number']):
                        if random.random() <= self.active_action['accuracy']:
                            self.map_matrix[i][j][index]['health'] += random.choice(self.active_action['value'])
                    if self.map_matrix[i][j][index]['health'] > self.map_matrix[i][j][index]['max_health']:
                        self.map_matrix[i][j][index]['health'] = self.map_matrix[i][j][index]['max_health']

    # Функция выбора клетки
    def select_cell(self, x, y):
        if self.active_character and self.active_action:
            if self.active_action['type'] == 'moving':
                if 'select_blue' in self.map_matrix[y][x]:
                    self.map_matrix[y][x].remove('select_blue')
                    character = self.active_character.copy()
                    character['i'] = y
                    character['j'] = x
                    self.map_matrix[y][x].append(character)
                    self.map_matrix[self.active_character['i']][self.active_character['j']].remove(
                        self.active_character)
                    if self.active_action["sound"]:
                        self.helpers['class_sound'].play_sound(self.active_action["sound"])
                    self.next = True
            if self.active_action['type'] == 'damage':
                if 'select_blue' in self.map_matrix[y][x]:
                    for index, character in enumerate(self.map_matrix[y][x]):
                        if (isinstance(character, dict) and character['type_object'] in self.groups and
                                character['type_object'] != self.active_character['type_object']):
                            if self.active_action['mass_action']:
                                self.all_group_damage(character['type_object'], self.active_action)
                                continue

                            for i_action in range(self.active_action['number']):
                                if random.random() <= self.active_action['accuracy']:
                                    self.map_matrix[y][x][index]['health'] -= random.choice(self.active_action['damage'])
                    self.map_matrix[y][x].remove('select_blue')
                    if self.active_action["sound"]:
                        self.helpers['class_sound'].play_sound(self.active_action["sound"])
                    self.next = True
            if self.active_action['type'] == 'regeneration':
                if 'select_blue' in self.map_matrix[y][x]:
                    for index, character in enumerate(self.map_matrix[y][x]):
                        if (isinstance(character, dict) and character['type_object'] in self.groups and
                                character['type_object'] == self.active_character['type_object']):
                            if self.active_action['mass_action']:
                                self.all_group_treatment(character['type_object'], self.active_action)
                                continue

                            for i_action in range(self.active_action['number']):
                                if random.random() <= self.active_action['accuracy']:
                                    self.map_matrix[y][x][index]['health'] += random.choice(self.active_action['value'])
                            if self.map_matrix[y][x][index]['health'] > self.map_matrix[y][x][index]['max_health']:
                                self.map_matrix[y][x][index]['health'] = self.map_matrix[y][x][index]['max_health']
                    self.map_matrix[y][x].remove('select_blue')
                    if self.active_action["sound"]:
                        self.helpers['class_sound'].play_sound(self.active_action["sound"])
                    self.next = True

        self.clear_select_cell()

        for value in self.map_matrix[y][x]:
            if not self.next and isinstance(value, dict) and value['type_object'] in self.groups:
                if self.active_character or self.active_action:
                    self.active_character = None
                    self.active_action = None
                    self.render_map()
                self.active_character = value
                self.active_character['i'] = y
                self.active_character['j'] = x
                self.posLabel.setText(f'Позиция x={x}-y={y}')
                pixmap = QPixmap(value['image'])
                self.imageLabel.setPixmap(pixmap)
                self.nameLabel.setText(f'{value["name"]}')
                self.groupLabel.setText(self.groups_dict.get(value['type_object'], value['type_object']))
                self.healthLabel.setText(f'Жизнь: {value["health"]}')

                if 'actions' in value.keys():
                    for key, action in value['actions'].items():
                        image = QIcon(action['image'])
                        self.actionsComboBox.addItem(image, action['name'])

                if self.start and value['type_object'] == 'player':
                    self.actionsComboBox.show()
                    self.activeActionPushButton.show()

                if value["sound"]:
                    self.helpers['class_sound'].play_sound(value["sound"])
        self.render_map()

    def clear_select_cell(self):
        self.imageLabel.clear()
        self.nameLabel.clear()
        self.groupLabel.clear()
        self.posLabel.clear()
        self.healthLabel.clear()
        self.actionsComboBox.clear()
        self.actionsComboBox.setEnabled(False)
        self.activeActionPushButton.hide()
        self.passPushButton.hide()
        self.active_character = None
        self.active_action = None

    # Функция получения пути по волновому алгоритму
    def has_path(self, x1, y1, x2, y2, ignore_groups=False):
        prev = {(x1, y1): None}
        d = {(x1, y1): 0}
        v = [(x1, y1)]
        while len(v) > 0:
            x, y = v.pop(0)
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    # if dx * dy != 0:
                    #     continue

                    if x + dx < 0 or x + dx >= self.size_m or y + dy < 0 or y + dy >= self.size_n:
                        continue

                    check = True
                    cell = self.map_matrix[y + dy][x + dx]
                    for value in cell:
                        if isinstance(value, dict):
                            if not ignore_groups:
                                if value['type_object'] in self.groups:
                                    check = False

                            if value['type_object'] in self.groups:
                                if value['i'] == y2 and value['j'] == x2:
                                    check = True

                            if value['type_object'] == 'block':
                                if not value['passability']:
                                    check = False

                    if check:
                        dn = d.get((x + dx, y + dy), -1)
                        if dn == -1:
                            prev[(x + dx, y + dy)] = (x, y)
                            d[(x + dx, y + dy)] = d.get((x, y), -1) + 1
                            v.append((x + dx, y + dy))
        # Восстановление пути
        path = []
        if (x2, y2) in prev:
            current = (x2, y2)
            while current is not None:
                path.append(current)
                current = prev[current]
            path.reverse()
        if path:
            path.pop(0)
        # print('Кратчайший путь', path, len(path))
        return path

    # Функция активации способности
    def click_action(self):
        self.last_point = (-1, -1)
        index = self.actionsComboBox.currentIndex()
        if self.active_character and index > -1 and 'actions' in self.active_character.keys():
            for key, value in self.active_character['actions'].items():
                if value['name'] == self.actionsComboBox.currentText():
                    if self.active_action:
                        self.active_action = None
                        self.render_map()
                    self.active_action = value
            y = self.active_character['i']
            x = self.active_character['j']
            if self.active_action['distance'] > 0 and self.active_action['type'] == 'moving':
                d = self.active_action['distance']
                for i in range(y - d, y + d + 1):
                    for j in range(x - d, x + d + 1):
                        if (0 <= i < self.size_n and 0 <= j < self.size_m and 'select_blue'
                                not in self.map_matrix[i][j]):
                            if 0 < len(self.has_path(x, y, j, i)) <= self.active_action['distance'] + 1:
                                check = True
                                for value in self.map_matrix[i][j]:
                                    if isinstance(value, dict):
                                        if value['type_object'] == 'block' and not value['passability']:
                                            check = False
                                        if value['type_object'] in self.groups:
                                            check = False
                                if check:
                                    self.map_matrix[i][j].append('select_blue')

            if self.active_action['distance'] > 0 and self.active_action['type'] == 'damage':
                d = self.active_action['distance']
                for i in range(y - d, y + d + 1):
                    for j in range(x - d, x + d + 1):
                        if (0 <= i < self.size_n and 0 <= j < self.size_m and 'select_blue'
                                not in self.map_matrix[i][j]):
                            check = False
                            for value in self.map_matrix[i][j]:
                                if isinstance(value, dict):
                                    if value['type_object'] in self.groups and value['type_object'] != \
                                            self.active_character['type_object']:
                                        check = True
                            if check:
                                self.map_matrix[i][j].append('select_blue')

            if self.active_action['type'] == 'regeneration':
                d = self.active_action['distance']
                for i in range(y - d, y + d + 1):
                    for j in range(x - d, x + d + 1):
                        if (0 <= i < self.size_n and 0 <= j < self.size_m and 'select_blue'
                                not in self.map_matrix[i][j]):
                            check = False
                            for value in self.map_matrix[i][j]:
                                if isinstance(value, dict):
                                    if value['type_object'] in self.groups and value['type_object'] == \
                                            self.active_character['type_object']:
                                        check = True
                            if check:
                                self.map_matrix[i][j].append('select_blue')

        self.render_map()

    # Функция обновления таймера
    def update_timer(self):
        if not self.start:
            return

        index = self.groups[self.queue]
        if len(self.characters[index]):
            self.queueLabel.setText(self.groups_dict[index])
            if index == 'player':
                self.actionsComboBox.setEnabled(True)
                self.activeActionPushButton.setEnabled(True)
            else:
                enemy_characters = []
                for group in self.groups:
                    if group != self.groups[self.queue]:
                        for character in self.characters[group]:
                            enemy_characters.append(character)

                if self.active_character is None:
                    print('Выбирается противник')
                    if not enemy_characters:
                        self.next = True
                    self.active_character = random.choice(self.characters[index])

                    if self.active_character:
                        self.select_cell(x=self.active_character['j'], y=self.active_character['i'])

                elif self.active_action is None:
                    print('Противник думает что делать')
                    if 'actions' in self.active_character:
                        enemies = sorted([(self.has_path(self.active_character['j'], self.active_character['i'],
                                                         i['j'], i['i']), i, True) for i in
                                          enemy_characters],
                                         key=lambda x: len(x[0]))
                        friends = sorted([(self.has_path(self.active_character['j'], self.active_character['i'],
                                                         i['j'], i['i']), i) for i in self.characters[index]],
                                         key=lambda x: len(x[0]))

                        damage_action = []
                        regen_action = []
                        action_move = None
                        for key, action in self.active_character['actions'].items():
                            if action['type'] == 'damage':
                                for enemy in enemies:
                                    if len(enemy[0]) <= action['distance']:
                                        damage_action.append(action.copy())
                                        break

                            if action['type'] == 'regeneration':
                                for friend in friends:
                                    if (len(friend[0]) <= action['distance'] and
                                            friend[1]['max_health'] > friend[1]['health']):
                                        regen_action.append(action.copy())

                            if action['type'] == 'moving':
                                action_move = action.copy()

                        print('Атаки', damage_action)
                        print('Лечение', regen_action)
                        print('Движение', action_move)
                        if damage_action and regen_action:
                            if random.randint(0, 4):
                                self.active_action = random.choice(damage_action)
                                self.set_combobox(self.active_action)
                                print('Выбрана атака')
                            else:
                                self.active_action = random.choice(regen_action)
                                self.set_combobox(self.active_action)
                                print('Выбрано лечение')
                        elif damage_action:
                            self.active_action = random.choice(damage_action)
                            self.set_combobox(self.active_action)
                            print('Выбрана атака')
                        elif regen_action:
                            self.active_action = random.choice(regen_action)
                            if action_move:
                                if random.randint(0, 1):
                                    self.active_action = action_move
                            self.set_combobox(self.active_action)
                            print('Выбрано лечение')
                        elif action_move:
                            self.active_action = action_move
                            self.set_combobox(self.active_action)
                            print('Выбрано движение')
                        else:
                            self.next = True

                        if not self.next:
                            self.click_action()
                    else:
                        self.next = True
                elif self.active_action:
                    print(self.active_action['type'])
                    enemies = sorted([(self.has_path(self.active_character['j'], self.active_character['i'],
                                                     i['j'], i['i']), i, True) for i in enemy_characters],
                                     key=lambda x: len(x[0]))
                    friends = sorted([(self.has_path(self.active_character['j'], self.active_character['i'],
                                                     i['j'], i['i']), i, True) for i in self.characters[index]],
                                     key=lambda x: len(x[0]))

                    if self.active_action['type'] == 'damage':
                        self.select_cell(enemies[0][1]['j'], enemies[0][1]['i'])
                        print('атакуем')
                    elif self.active_action['type'] == 'regeneration':
                        for friend in friends:
                            if friend[1]['max_health'] > friend[1]['health']:
                                self.select_cell(friend[1]['j'], friend[1]['i'])
                                print('лечимся')
                                break
                    elif self.active_action['type'] == 'moving':
                        print('идём')
                        enemy = min([(self.has_path(self.active_character['j'], self.active_character['i'],
                                                    i['j'], i['i']), i) for i in enemy_characters],
                                    key=lambda x: len(x[0]))
                        x, y = None, None
                        print(enemy[0])
                        for i in range(self.active_action['distance']):
                            if len(enemy[0]):
                                if enemy[0][0] != enemy[0][-1]:
                                    x, y = enemy[0].pop(0)

                        if x is None or y is None:
                            self.next = True
                        else:
                            self.select_cell(x, y)

                    print('Противник действует')
                    self.next = True
        else:
            self.next = True

        if self.next:
            print('Следующий ход')
            self.clear_select_cell()
            self.actionsComboBox.setEnabled(False)
            self.activeActionPushButton.hide()
            self.passPushButton.hide()
            self.last_point = (-1, -1)

            self.queue += 1
            if self.queue >= len(self.groups):
                self.queue = 0
            self.next = False
            self.render_map()

        if self.start and self.queue == 0:
            self.passPushButton.show()

    # Пропуск хода
    def pass_queue(self):
        if self.queue == 0:
            self.next = True

    # Показать силу команды
    def show_team_power(self):
        characters = {f"{enemy['character']}_{group}_{index}": enemy for group in self.groups for index, enemy in
                      enumerate(self.characters[group]) if group == 'player'}
        print(characters)

        self.helpers['class_app'].open_power_team(characters)

    # Показать силу противника
    def show_enemy_power(self):
        characters = {f"{enemy['character']}_{group}_{index}": enemy for group in self.groups for index, enemy in
                      enumerate(self.characters[group]) if group != 'player'}
        print(characters)

        self.helpers['class_app'].open_power_team(characters)

    # Установка настроек сетки
    def set_size_cells(self):
        self.font_size = self.fontSpinBox.value()
        self.cell_size_height = self.heightSpinBox.value()
        self.cell_size_width = self.widthSpinBox.value()
        self.time_speed = self.speedTimeSpinBox.value()
        # Создаем и настраиваем таймер
        self.timer.stop()
        self.timer = QTimer()
        self.timer.setInterval(self.time_speed)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start()
        self.render_map()

    # Функция запуска игры
    def start_game(self):
        self.start = not self.start
        if self.start:
            self.startPushButton.setText('Пауза')
            self.actionsComboBox.setEnabled(False)
            self.activeActionPushButton.hide()
            self.passPushButton.hide()
        else:
            self.startPushButton.setText('Запуск')

    # Функция выхода в меню кампании
    def back(self):
        self.timer.stop()
        count_enemy = len([enemy for group in self.groups for enemy in self.characters[group] if group != 'player'])
        count_player = len(self.characters['player'])
        if count_player and not count_enemy:
            self.helpers['class_save_user'].budget += self.map_data['prize']
            self.helpers['class_save_user'].experience += self.map_data['experience']
            if str(self.map_id) not in self.helpers['class_save_user'].campaign:
                self.helpers['class_save_user'].campaign.append(str(self.map_id))
            self.helpers['class_save_user'].save_data()
            self.helpers['class_app'].show_message_box('Победа!')
        else:
            self.helpers['class_app'].show_message_box('Поражение!')

        self.window.show()
        self.window.refresh_maps()
        self.helpers['class_sound'].play_music("resources/music/menu.mp3")
        self.close()
