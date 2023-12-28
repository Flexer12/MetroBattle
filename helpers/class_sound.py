# Импорт библиотек
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist


# Класс по работе со звуками и музыкой
class ClassSound:
    # Фукнция инициализации
    def __init__(self):
        self.sound_content = None
        self.sound_player = None
        self.playlist = None
        self.sounds_volume = 30
        self.media_player_volume = 30
        self.media_player = None
        self.media_content = None

    # Функция для проигрывания музыки
    def play_music(self, path):
        if self.media_player:
            self.media_player.stop()
            self.media_content = None
            self.media_player = None

        self.media_player = QMediaPlayer()
        self.media_content = QMediaContent(QUrl.fromLocalFile(path))

        self.playlist = QMediaPlaylist()
        self.playlist.addMedia(self.media_content)
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)

        self.media_player.setPlaylist(self.playlist)
        self.media_player.setVolume(self.media_player_volume)
        self.media_player.play()

    # Установка громкости для медиаплеера
    def set_media_player_volume(self, volume):
        self.media_player_volume = volume

        if self.media_player:
            self.media_player.setVolume(self.media_player_volume)

    # Функция для проигрывания звука с определенной громкостью один раз
    def play_sound(self, sound_file):
        self.sound_player = QMediaPlayer()
        self.sound_content = QMediaContent(QUrl.fromLocalFile(sound_file))
        self.sound_player.setMedia(self.sound_content)
        self.sound_player.setVolume(self.sounds_volume)
        self.sound_player.play()

    # Установка громкости для звуков
    def set_sounds_volume(self, volume):
        self.sounds_volume = volume
