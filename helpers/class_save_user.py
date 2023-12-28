# Класс для работы с сохранением пользователя
class SaveUser:
    # Функция инициализации
    def __init__(self, helpers, id=None):
        self.experience_up = 500
        self.id = 1
        self.email = ''
        self.password = ''
        self.nickname = ''
        self.avatar_path = ''
        self.post_id = 2
        self.level = 1
        self.budget = 0
        self.experience = 0
        self.units = []
        self.team = []
        self.technologies = []
        self.campaign = []
        self.helpers = helpers

        if id:
            self.select_user(id)

    # Функция выбора пользователя, с загрузкой данных
    def select_user(self, id):
        user = self.helpers['class_db'].select('users', column='id', value=id, return_value='one')

        if isinstance(user, tuple):
            self.id = int(user[0])
            self.email = user[1]
            self.password = user[2]
            self.nickname = user[3]
            self.avatar_path = user[4]
            self.post_id = int(user[5])

            save = self.helpers['class_db'].select('saves', column='user_id', value=id, return_value='one')
            if isinstance(save, tuple):
                self.level = save[1]
                self.budget = save[2]
                self.experience = save[3]
                self.units = save[4].split()
                self.team = save[5].split()
                self.technologies = save[6].split()
                self.campaign = save[7].split()

                self.set_up_experience_level()

    # Обновление данных БД
    def save_data(self):
        if self.experience_up <= self.experience:
            self.experience = 0
            self.level += 1

        if self.experience < 0:
            self.experience = 0
            if self.level > 1:
                self.level -= 1
            else:
                self.level = 1

        if self.budget < 0:
            self.budget = 0

        self.helpers['class_db'].update('users', column='password', value=f"'{self.password}'",
                                        find_column='id', find_value=self.id)
        self.helpers['class_db'].update('users', column='nickname', value=f"'{self.nickname}'",
                                        find_column='id', find_value=self.id)
        self.helpers['class_db'].update('users', column='avatar_path', value=f"'{self.avatar_path}'",
                                        find_column='id', find_value=self.id)
        self.helpers['class_db'].update('saves', column='level', value=f"{self.level}",
                                        find_column='user_id', find_value=self.id)
        self.helpers['class_db'].update('saves', column='budget', value=f"{self.budget}",
                                        find_column='user_id', find_value=self.id)
        self.helpers['class_db'].update('saves', column='experience', value=f"{self.experience}",
                                        find_column='user_id', find_value=self.id)
        self.helpers['class_db'].update('saves', column='units', value=f"'{' '.join(self.units)}'",
                                        find_column='user_id', find_value=self.id)
        self.helpers['class_db'].update('saves', column='team', value=f"'{' '.join(self.team)}'",
                                        find_column='user_id', find_value=self.id)
        self.helpers['class_db'].update('saves', column='technologies', value=f"'{' '.join(self.technologies)}'",
                                        find_column='user_id', find_value=self.id)
        self.helpers['class_db'].update('saves', column='campaign', value=f"'{' '.join(self.campaign)}'",
                                        find_column='user_id', find_value=self.id)

        self.select_user(self.id)

    # Функция установки опыта при котором достигает новый уровень
    def set_up_experience_level(self):
        self.experience_up = 500
        for i in range(self.level):
            self.experience_up *= (i + 1)
