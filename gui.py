from PyQt6 import QtWidgets, uic
import sys
import modal
import wind


class Ui(QtWidgets.QMainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self):
        super(Ui, self).__init__(parent=None)
        uic.loadUi('windLoad.ui', self)
        self.mod = modal.ModalSolution()
        self.mod.calc()
        n = self.mod.n
        xi = self.mod.xi
        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')  # Find the button
        self.button.clicked.connect(self.push_button_pressed)
        self.comboRegion = self.findChild(QtWidgets.QComboBox, 'comboBox')
        self.input = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        wr = self.comboRegion.currentText()
        a = self.input.text()
        f = self.mod.f
        self.win = wind.WindLoads(wr, n, xi, a, f)
        self.windRegions = ['Ia', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
        for wR in self.windRegions:
            self.comboRegion.addItem(wR)
        self.show()

    def push_button_pressed(self):
        print('Расчёт ветровой нагрузки по СП 20.13330.2016')  # Press Ctrl+F8 to toggle the breakpoint.
        self.win.wind_region = self.comboRegion.currentText()
        self.win.a = self.input.text()
        self.win.calc()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec())
