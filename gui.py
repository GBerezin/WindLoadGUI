import pandas as pd
from PyQt6 import QtWidgets, uic
import sys
import modal
import wind


class Ui(QtWidgets.QMainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self):
        super(Ui, self).__init__(parent=None)
        uic.loadUi('windLoad.ui', self)
        self.data = pd.read_csv('data.csv', delimiter=';')
        wr = self.data['wr'][0]  # ветровой район
        ter = self.data['ter'][0]  # тип местности
        bld = self.data['bld'][0]  # сооружение
        a = self.data['a'][0]  # размер здания в направлении расчетного ветра, [м]
        d = self.data['d'][0]  # размер здания в направлении перпендикулярном расчетному направлению ветра, [м]
        dz = self.data['dz'][0]  # отметка 0.000, [м]
        eb = self.data['eb'][0]  # модуль упругости бетона, [МПа]
        nm = self.data['nm'][0]  # количество учитываемых форм колебаний
        c = self.data['c'][0]  # аэродинамический коэффициент
        delta = self.data['delta'][0]  # логарифмический декремент
        xyz = self.data['xyz'][0]  # расчётная поверхность
        gf = 1.4  # коэффициент надёжности по нагрузке ветра
        self.mod = modal.ModalSolution(dz, nm, eb)
        self.mod.calc()
        n = self.mod.n
        xi = self.mod.xi
        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')  # Find the button
        self.button.clicked.connect(self.push_button_pressed)
        self.comboRegion = self.findChild(QtWidgets.QComboBox, 'comboBox')
        self.input = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.input.setText(str(a))
        self.win = wind.WindLoads(wr, ter, bld, a, d, c, delta, xyz, gf, n, xi, self.mod.f)
        self.windRegions = ['Ia', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
        for wR in self.windRegions:
            self.comboRegion.addItem(wR)
        self.show()

    def push_button_pressed(self):
        """Кнопка расчёт"""

        print('Расчёт ветровой нагрузки по СП 20.13330.2016')  # Press Ctrl+F8 to toggle the breakpoint.
        self.win.wind_region = self.comboRegion.currentText()
        self.win.a = self.input.text()
        self.win.calc()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec())
