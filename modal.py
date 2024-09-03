import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import integrate
import math
from scipy.interpolate import make_interp_spline


class ModalSolution:
    """Модальный расчёт"""

    def __init__(self, dz, nm, eb):
        self.f = None
        self.rdm = pd.read_csv('rdm.csv', delimiter=';')
        self.n = self.rdm.shape[0]
        self.dz = dz  # отметка 0.000, [м]
        self.xi = np.hstack((0.0, self.level(self.n, self.dz)))
        self.nm = nm  # количество учитываемых форм колебаний
        self.eb = eb  # модуль упругости бетона, [МПа]

    def plot_rdm(self, x):
        """Рисунок динамической модели"""

        img = plt.imread('rdm.png')
        fig, ax = plt.subplots()
        ax.imshow(img, extent=[0, x[self.n] / 1.5, 0, x[self.n]])
        plt.title('Расчётная динамическая модель РДМ')
        ax.axes.xaxis.set_visible(False)
        plt.show()

    def level(self, n, dz):
        """Отметки этажей:"""

        x = np.zeros(n)
        x_0 = dz
        for i in range(0, n):
            x[i] = x_0 + self.rdm['hi'][i]
            x_0 = x[i]
        return x

    def mass(self):
        """Матрица масс"""

        m = np.zeros((self.n, self.n))
        for i in range(0, self.n):
            m[i, i] = self.rdm['Mp'][i]
        return m

    @staticmethod
    def mi(x, xi, xj, s, ei):
        """Моменты от единичных сил"""

        if x <= xi:
            m0 = s * xi - s * x
        else:
            m0 = 0
        if x <= xj:
            m1 = s * xj - s * x
        else:
            m1 = 0
        m = (m0 * m1) / ei
        return m

    @staticmethod
    def m_i(x, xi, s):
        """Моменты от единичных сил"""

        if x <= xi:
            m = s * xi - s * x
        else:
            m = 0
        return m

    def m_d(self, xi, ei):
        """Матрица податливости"""

        md = np.zeros((self.n, self.n))
        for i in range(0, self.n):
            for j in range(0, self.n):
                md[i, j] = \
                    integrate.quad(self.mi, 0, xi[self.n - 1], args=(xi[i], xi[j], 1, ei[i]))[0]
        return md

    @staticmethod
    def ww(mv):
        """Круговая частота"""

        w = math.sqrt(1 / mv)
        return w

    def plotmode(self, xi, u):
        """График форм колебаний"""

        x0 = xi
        xnew = np.linspace(x0.min(), x0.max(), 200)
        for i in range(0, self.nm):
            vy = np.hstack((0, u[:, i]))
            spl = make_interp_spline(x0, vy, k=3)
            y = spl(xnew)
            plt.plot(xnew, y, label='U' + str(i))
        plt.legend()
        ax = plt.gca()
        ax.set_xlabel("z, [м]", fontsize=15, color='blue')
        plt.title('Формы колебаний')
        plt.show()

    def calc(self):
        """Расчёт"""

        print('Модальный расчёт:')
        mm = self.mass()
        ei = self.eb * self.rdm['It'] * 1000
        md = self.m_d(self.xi, ei)
        dd = md @ mm
        mv, u = np.linalg.eig(dd)
        vw = np.vectorize(self.ww)
        w = vw(np.real(np.real(mv)[:self.nm]))
        print('Круговая частота, [рад/с]:')
        print(w[:4])
        t = 2 * math.pi / w
        print('Период, [с]:')
        print(t[:4])
        self.f = w / (2 * math.pi)
        print('Техническая частота, [Гц]:')
        print(self.f[:4])
        print('Собственные векторы:')
        print(np.real(u)[:self.nm, :self.nm])
