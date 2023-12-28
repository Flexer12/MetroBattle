# Класс созданный специально для работы и учета ресурсных файлов для игры
class ClassRegistry:
    # Функция инициализации
    def __init__(self, helpers):
        self.path_resources = 'resources/game/'
        self.helpers = helpers
        self.technologies = {}
        self.characters = {}
        self.maps = {}
        self.bots_maps = {}
        self.blocks = {}

        self.get_technologies()
        self.get_characters()
        self.get_maps()
        self.get_bots_maps()
        self.get_blocks()
        print('Данные реестра --------------------------------')
        print(self.technologies)
        print(self.characters)
        print(self.maps)
        print(self.bots_maps)
        print(self.blocks)
        print('-----------------------------------------------')

    # Функция получения технологий
    def get_technologies(self):
        path = f'{self.path_resources}technologies/'
        self.technologies = {}

        for technology in self.helpers['class_file'].get_dirs(path):
            path_technology = f'{path}/{technology}'

            if (self.helpers['class_file'].check_file(path_technology)
                    and self.helpers['class_file'].check_file(path_technology + '/characteristic.txt')
                    and self.helpers['class_file'].check_file(path_technology + '/image.png')):
                characteristic = self.helpers['class_file'].get_file_dict(path_technology + '/characteristic.txt')
                if characteristic:
                    self.technologies[technology] = characteristic
                    self.technologies[technology]['image'] = path_technology + '/image.png'

    # Функция получения персонажей
    def get_characters(self):
        path = f'{self.path_resources}characters/'
        self.characters = {}

        for character in self.helpers['class_file'].get_dirs(path):
            path_character = f'{path}{character}'

            if (self.helpers['class_file'].check_file(path_character)
                    and self.helpers['class_file'].check_file(path_character + '/characteristic.txt')
                    and self.helpers['class_file'].check_file(path_character + '/image.png')):
                characteristic = self.helpers['class_file'].get_file_dict(path_character + '/characteristic.txt')
                if characteristic:
                    self.characters[character] = characteristic
                    self.characters[character]['max_health'] = self.characters[character]['health']
                    self.characters[character]['image'] = path_character + '/image.png'
                    if self.helpers["class_file"].check_file(path_character + "/sound.mp3"):
                        self.characters[character]['sound'] = path_character + "/sound.mp3"
                    else:
                        self.characters[character]['sound'] = ''

                    actions = self.helpers['class_file'].get_dirs(path_character + '/actions')
                    if actions:
                        self.characters[character]['actions'] = {}
                        for action in actions:
                            self.characters[character]['actions'][action] = (
                                self.helpers['class_file'].get_file_dict(path_character +
                                                                         f'/actions/{action}/action.txt'))
                            if self.helpers["class_file"].check_file(path_character + f'/actions/{action}/sound.mp3'):
                                self.characters[character]['actions'][action]['sound'] = (
                                        path_character + f'/actions/{action}/sound.mp3')
                            else:
                                self.characters[character]['actions'][action]['sound'] = ''
                            self.characters[character]['actions'][action]['image'] = (
                                    path_character + f'/actions/{action}/image.png')

    # Функция получения карт
    def get_maps(self):
        path = f'{self.path_resources}maps/'
        self.maps = {}

        for map_v in self.helpers['class_file'].get_dirs(path):
            path_map = f'{path}/{map_v}'

            if (self.helpers['class_file'].check_file(path_map)
                    and self.helpers['class_file'].check_file(path_map + '/characteristic.txt')
                    and self.helpers['class_file'].check_file(path_map + '/image.png')):
                characteristic = self.helpers['class_file'].get_file_dict(path_map + '/characteristic.txt')
                if characteristic:
                    self.maps[map_v] = characteristic
                    self.maps[map_v]['image'] = path_map + '/image.png'
                    self.maps[map_v]['music'] = path_map + '/music.mp3'

    # Функция получения карт для битвы ботов
    def get_bots_maps(self):
        path = f'{self.path_resources}bots_maps/'
        self.bots_maps = {}

        for map_v in self.helpers['class_file'].get_dirs(path):
            path_map = f'{path}/{map_v}'

            if (self.helpers['class_file'].check_file(path_map)
                    and self.helpers['class_file'].check_file(path_map + '/characteristic.txt')
                    and self.helpers['class_file'].check_file(path_map + '/image.png')):
                characteristic = self.helpers['class_file'].get_file_dict(path_map + '/characteristic.txt')
                if characteristic:
                    self.bots_maps[map_v] = characteristic
                    self.bots_maps[map_v]['image'] = path_map + '/image.png'

    # Функция получения блоков
    def get_blocks(self):
        path = f'{self.path_resources}blocks/'
        self.blocks = {}

        for block in self.helpers['class_file'].get_dirs(path):
            path_block = f'{path}/{block}'

            if (self.helpers['class_file'].check_file(path_block)
                    and self.helpers['class_file'].check_file(path_block + '/characteristic.txt')
                    and self.helpers['class_file'].check_file(path_block + '/image.png')):
                characteristic = self.helpers['class_file'].get_file_dict(path_block + '/characteristic.txt')
                if characteristic:
                    self.blocks[block] = characteristic
                    self.blocks[block]['image'] = path_block + '/image.png'
