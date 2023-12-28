# Диалоговое окно для показа силы персонажей
from PyQt5 import uic
from PyQt5.QtChart import QValueAxis, QBarCategoryAxis, QBarSeries, QBarSet, QChartView, QChart
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog


# Класс отображения диалогового окна силы
class PowerCharactersDialog(QDialog):
    # Функция инициализации
    def __init__(self, characters):
        super().__init__()

        self.characters = characters
        self.initUI()

    # Функция инициализации интерфейса
    def initUI(self):
        uic.loadUi('templates/power_characters.ui', self)
        self.resize(800, 600)

        # Загрузка иконки
        icon = QIcon('resources/images/icon.ico')
        self.setWindowIcon(icon)

        self.chart = QChart()

        total_strength = sum(
            character['experience']
            for character in self.characters.values()
        )
        self.chart.setTitle(f"Сила персонажей {total_strength}")
        self.chartView = QChartView(self.chart)

        barSet = QBarSet('Сила')
        for character in self.characters.values():
            barSet.append(character['experience'])

        barSeries = QBarSeries()
        barSeries.append(barSet)

        self.chart.addSeries(barSeries)

        axisX = QBarCategoryAxis()
        axisX.append(self.characters.keys())
        self.chart.setAxisX(axisX, barSeries)

        axisY = QValueAxis()
        self.chart.setAxisY(axisY, barSeries)

        self.gridLayout.addWidget(self.chartView, 0, 0)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.addWidget(self.buttonBox, 1, 0)
