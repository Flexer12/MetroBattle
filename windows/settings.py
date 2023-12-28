# Импортируем библиотеки
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QDialogButtonBox


# Диалоговое окно настроек
class Settings(QDialog):
    # Функция иницилизации
    def __init__(self, helpers):
        super().__init__()
        self.helpers = helpers
        self.initUI()

    # Функция инилизации интерфейса
    def initUI(self):
        uic.loadUi('templates/settings.ui', self)

        # Загрузка иконки
        icon = QIcon('resources/images/icon.ico')
        self.setWindowIcon(icon)

        self.buttonBox.button(QDialogButtonBox.Save).setText("Сохранить")
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Отмена")

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.buttonBox.accepted.connect(self.save_settings)

        self.downVolumeMusicPushButton.clicked.connect(self.down_volume_music)
        self.upVolumeMusicPushButton.clicked.connect(self.up_volume_music)
        self.musicHorizontalSlider.valueChanged.connect(self.update_volume_music)
        self.musicHorizontalSlider.setValue(self.helpers['class_app'].settings['volume_music'])

        self.downVolumeSoundsPushButton.clicked.connect(self.down_volume_sounds)
        self.upVolumeSoundsPushButton.clicked.connect(self.up_volume_sounds)
        self.soundsHorizontalSlider.valueChanged.connect(self.update_volume_sounds)
        self.soundsHorizontalSlider.setValue(self.helpers['class_app'].settings['volume_sounds'])

        self.nameAppLineEdit.setText(self.helpers['class_app'].settings['name_app'])
        print(self.helpers['class_app'].debug_mode)
        self.debugModeCheckBox.setChecked(self.helpers['class_app'].debug_mode)

    # Функция понижения громкости звуков
    def down_volume_sounds(self):
        value = int(self.soundsHorizontalSlider.value())
        if value > 0:
            value -= 1
        self.soundsHorizontalSlider.setValue(value)
        self.volumeSoundsLabel.setText(str(value) + "%")

    # Функция повышения громкости звуков
    def up_volume_sounds(self):
        value = int(self.soundsHorizontalSlider.value())
        if value < 100:
            value += 1
        self.soundsHorizontalSlider.setValue(value)
        self.volumeSoundsLabel.setText(str(value) + "%")

    # Функция обновления значения громкости звуков
    def update_volume_sounds(self):
        self.volumeSoundsLabel.setText(str(self.soundsHorizontalSlider.value()) + "%")

    # Функция понижения громкости музыки
    def down_volume_music(self):
        value = int(self.musicHorizontalSlider.value())
        if value > 0:
            value -= 1
        self.musicHorizontalSlider.setValue(value)
        self.volumeMusicLabel.setText(str(value) + "%")

    # Функция повышения громкости музыки
    def up_volume_music(self):
        value = int(self.musicHorizontalSlider.value())
        if value < 100:
            value += 1
        self.musicHorizontalSlider.setValue(value)
        self.volumeMusicLabel.setText(str(value) + "%")

    # Функция обновления значения громкости музыки
    def update_volume_music(self):
        self.volumeMusicLabel.setText(str(self.musicHorizontalSlider.value()) + "%")

    # Функция сохранения настроек
    def save_settings(self):
        settings = {
            'volume_music': self.musicHorizontalSlider.value(),
            'volume_sounds': self.soundsHorizontalSlider.value(),
            'name_app': self.nameAppLineEdit.text(),
            'debug_mode': int(self.debugModeCheckBox.isChecked()),
        }
        self.helpers['class_app'].apply_setting(settings)
