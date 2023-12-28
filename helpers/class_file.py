# Импортируем библиотеки
import os.path
import shutil


# Класс по работе с файлами
class ClassFile:
    # Функция инициализации
    def __init__(self):
        pass

    def get_dirs(self, dir):
        if self.check_file(dir):
            return os.listdir(dir)
        else:
            return []

    # Функция проверки существования файла / директории
    def check_file(self, path):
        if os.path.exists(path):
            return True
        return False

    # Функция копирования файла
    def copy_file(self, path, new_path):
        try:
            shutil.copy(path, new_path)
            return True
        except Exception as e:
            print(f"Ошибка при копировании {e}")
            return False

    # Функция создания директории
    def create_dir(self, path):
        try:
            if not self.check_file(path):
                os.mkdir(path)
            return True
        except Exception as e:
            print(f"Ошибка при создании директории {e}")
            return False

    # Функция удаления файла
    def delete_file(self, path):
        try:
            if self.check_file(path):
                os.remove(path)
            return True
        except Exception as e:
            print(f"Ошибка при удалении файла {e}")
            return False

    # Функция удаления директории
    def delete_dir(self, path):
        try:
            # Обход всех папок и файлов в выбранной директории
            for dirpath, dirnames, filenames in os.walk(path):
                # Удаление всех файлов в текущей папке
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    os.remove(file_path)
                # Удаление текущей папки
                shutil.rmtree(dirpath)
            return True
        except Exception as e:
            print(f"Ошибка при удалении директории {e}")
            return False

    # Функция чтения текстовых файлов
    def read_file_txt(self, path):
        if self.check_file(path):
            data = []
            with open(path, "r", encoding="utf-8") as f:
                data = f.readlines()
            return data
        else:
            return False

    # Функция записи текстовых файлов
    def write_file_txt(self, path, value):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(value)
            return True
        except Exception as e:
            print(f"Ошибка при чтении {e}")
            return False

    # Функция получения словаря с текстового файла
    def get_file_dict(self, path):
        file = self.read_file_txt(path)
        if file:
            result_dict = {}
            for i in file:
                if i:
                    line = i.split(':')
                    line[2] = line[2].replace('\n', '')
                    print(line)
                    if line[2] == 'int':
                        result_dict[line[0]] = int(line[1])

                    if line[2] == 'str':
                        result_dict[line[0]] = line[1]

                    if line[2] == 'float':
                        result_dict[line[0]] = float(line[1])

                    if line[2] == 'bool':
                        result_dict[line[0]] = bool(int(line[1]))

                    if line[2] == 'tuple':
                        line[1] = line[1].replace('(', '')
                        line[1] = line[1].replace(')', '')
                        line[1] = tuple(line[1].split(','))
                        result_dict[line[0]] = line[1]

                    if line[2] == 'range':
                        print(line[1])
                        line[1] = tuple(map(int, line[1].split('-')))
                        print(line[1])
                        line[1] = tuple(range(line[1][0], line[1][-1] + 1))
                        print(line[1])
                        result_dict[line[0]] = line[1]
                    print(i)
            return  result_dict
        return False
