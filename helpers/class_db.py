# Импорт библиотек
import os.path
import sqlite3


# Класс работы с базой данных
class ClassDB:
    # Функция иницаилизации
    def __init__(self, name):
        self.name_db = name

    # Единая функция исполнения запросов
    def query_execute(self, query, return_value=None):
        try:
            connection = sqlite3.connect(self.name_db)
            cur = connection.cursor()
            res = True
            if not return_value:
                if query == '':
                    print('Проверка соединения!')
                else:
                    cur.execute(query)
            elif return_value == "one":
                res = cur.execute(query).fetchone()
            elif return_value == "all":
                res = cur.execute(query).fetchall()
            else:
                print(f"Запрос не корректный: {query}!")
                print("Можно вернуть только one или all!")
                return False

            # Применяем изменения и закрываем соединение
            connection.commit()
            connection.close()
            print("Запрос выполнен!")
            return res
        except Exception as e:
            print(f"Произошла ошибка: {e}! \n Запрос: {query}")
            return False

    # Функция проверки соединения
    def check_connection(self):
        return self.query_execute("")

    # Функция для добавления строки в выбранную таблицу
    def insert(self, table, columns, values):
        query = f"""
                INSERT INTO {table}({columns}) VALUES({values})
                """

        if not self.query_execute(query):
            return False
        return True

    # Функция для удаления строки в выбранной таблице
    def delete(self, table, column=None, value=None):
        query = f"""
                DELETE FROM {table}
                """

        if column:
            query += f""" WHERE {column} = {value}"""

        if not self.query_execute(query):
            return False
        return True

    # Функция для обновления строки в выбранной таблице
    def update(self, table, column, value, find_column, find_value):
        query = f"""
                UPDATE {table} SET {column} = {value} WHERE {find_column} = {find_value}
                """
        if not self.query_execute(query):
            return False
        return True

    # Функция для вывода данных с таблицы
    def select(self, table, columns="*", column=None, value=None, return_value=None):
        query = f"""
                    SELECT {columns} FROM {table}
                    """
        if column:
            query += f""" WHERE {column} = {value}"""

        if return_value:
            res = self.query_execute(query, return_value)
        else:
            res = self.query_execute(query)

        if not res:
            return False
        return res
