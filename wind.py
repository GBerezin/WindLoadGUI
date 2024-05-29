import math
import numpy as np
import pandas as pd
import scipy.constants as const
from matplotlib import pyplot as plt


def zetai(tb, z):
    """Интерполяция таблицы 11.4"""

    tb.index = pd.to_numeric(tb.index)
    new_index = np.unique(list(tb.index) + [z])
    new_tb = tb.reindex(new_index).interpolate(method='polynomial', order=2)
    return new_tb


class WindLoads:
    def __init__(self, wr, n, xi, a, f):
        self.g = const.g
        self.t11_2 = pd.read_csv('table11_2.csv', delimiter=';')
        self.t11_4 = pd.read_csv('table11_4.csv', delimiter=';')
        self.tksi = pd.read_csv('table_ksi.csv', delimiter=';')
        self.t11_6 = pd.read_csv('table11_6.csv', delimiter=';')
        index = ['Ia', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
        self.table_11_1 = pd.Series([0.17, 0.23, 0.3, 0.38, 0.48, 0.6, 0.73, 0.85], index=index)
        self.wind_region = wr  # Ветровой район
        self.n = n
        self.xi = xi
        self.ter = 'B'  # тип местности
        self.bld = 'здание'  # сооружение
        self.a = a  # размер здания в направлении расчетного ветра, [м]
        self.f = f
        self.d = 60.0  # размер здания в направлении перпендикулярном расчетному направлению ветра, [м]
        self.gf = 1.4  # коэффициент надёжности по нагрузке ветра
        self.c = 1.3  # аэродинамический коэффициент
        self.delta = 0.3  # логарифмический декремент
        self.xyz = 'z0y'  # расчётная поверхность

    def zei(self, h, z, d):
        """Эквивалентная высота"""

        ze = 0.0
        if self.bld == "здание":
            if h <= z:
                ze = h
            elif d < h <= 2 * d:
                if z >= h - d:
                    ze = h
                elif 0 < z < h - d:
                    ze = d
                else:
                    ze = z
            elif h > 2 * d:
                if z >= h - d:
                    ze = h
                elif d < z < h - d:
                    ze = z
                elif 0 <= z <= d:
                    ze = d
                else:
                    ze = z
            else:
                ze = z
        return ze

    @staticmethod
    def plot_zei(zi, ze_i):
        """График эквивалентной высоты"""

        plt.plot(zi, ze_i, label='$z_{e}$')
        plt.legend()
        plt.xlabel('z, [м]')
        plt.ylabel('$z_e$, [м]')
        plt.title('Эквивалентная высота $z_{e}$, м')
        plt.show()

    @staticmethod
    def plot_w(w, txt, ind):
        """График ветровой нагрузки"""

        plt.plot(w, label='w' + ind)
        plt.legend()
        plt.xlabel('$z_e$, [м]')
        plt.ylabel('w' + ind + '[ кПа]')
        plt.title(txt + 'w' + ind)
        plt.show()

    @staticmethod
    def ki(tb, z):
        """Интерполяция таблицы 11.2"""

        tb.index = pd.to_numeric(tb.index)
        new_index = np.unique(list(tb.index) + [z])
        new_tb = tb.reindex(new_index).interpolate(method='polynomial', order=2)
        return new_tb

    @staticmethod
    def plot_ki(z_i, k):
        """График коэффициента k"""

        plt.plot(z_i, k, label='k')
        plt.legend()
        plt.xlabel('$z_{e}$, [м]')
        plt.ylabel('k')
        plt.title('Коэффициенты учитывающие изменение ветрового давления k')
        plt.show()

    def k_i(self, h, ze_i):
        """Коэффициенты учитывающие изменение ветрового давления k"""

        tbl = self.t11_2.set_index(['zei'])
        i = 0
        for z in ze_i:
            tbl = self.ki(tbl, z)
            i = i + 1
        tb = tbl[tbl.index <= h]
        z_i = tb.index
        k = tb[self.ter]
        return k, z_i

    @staticmethod
    def plot_zeta(z_i, zeta_i):
        """График коэффициента zeta"""

        plt.plot(z_i, zeta_i, label=r"$\zeta$")
        plt.legend()
        plt.xlabel('$z_{ei}$')
        plt.ylabel(r'$\zeta$')
        plt.title(r'Коэффициенты пульсаций давления ветра $\zeta$')
        plt.show()

    def zeta(self, h, ze_i):
        """Коэффициенты пульсаций давления ветра"""

        tbl = self.t11_4.set_index(['zei'])
        i = 0
        for z in ze_i:
            tbl = zetai(tbl, z)
            i = i + 1
        tb = tbl[tbl.index <= h]
        zeta_i = tb[self.ter]
        return zeta_i

    @staticmethod
    def plot_txi(table_xi):
        """Коэффициенты динамичности по рис. 11.1"""

        plt.plot(table_xi.index, table_xi['0.15'], label=r'$\delta = 0.15$')
        plt.legend()
        plt.xlabel('$T_{g,1}$')
        plt.ylabel(r'$\xi$')
        plt.plot(table_xi.index, table_xi['0.22'], label=r'$\delta = 0.22$')
        plt.legend()
        plt.ylabel(r'$\xi$')
        plt.plot(table_xi.index, table_xi['0.3'], label=r'$\delta = 0.3$')
        plt.legend()
        plt.ylabel(r'$\xi$')
        plt.title(r'$Коэффициенты динамичности \ \xi$')
        plt.show()

    @staticmethod
    def plot_fl(k, fl):
        """График fl"""

        plt.plot(k, fl, label='f_lim')
        plt.legend()
        plt.xlabel('k, [м]')
        plt.ylabel('$f_{lim}$, [Гц]')
        plt.title('Предельные значения частоты собственных колебаний f_lim')
        plt.show()

    def tg_1(self, k, f, w0):
        """Безразмерный период"""

        tg1 = math.sqrt(w0 * k * self.gf * 1000) / (940 * f)
        return tg1

    def plot_xi_(self, ti, xi_):
        """График xi"""
        plt.plot(ti, xi_, label=r"$\xi$")
        plt.legend()
        plt.xlabel('$T_{g,1}$')
        plt.ylabel(r'$\xi$')
        plt.title(r'Коэффициенты динамичности для $\delta$=' + str(self.delta))
        plt.show()

    @staticmethod
    def xii(tbl, tg1):
        """Интерполяция коэффициентов динамичности"""

        tbl.index = pd.to_numeric(tbl.index)
        new_index = np.unique(np.union1d(list(tbl.index), tg1))
        new_tb = tbl.reindex(new_index).interpolate(method='polynomial', order=2)
        return new_tb

    def xi_i(self, tbl, tg1):
        """Коэффициенты динамичности"""

        for t in tg1:
            tbl = self.xii(tbl, t)
        tb = tbl[tbl.index <= max(tg1)]
        ti = tb.index
        xi_ = tb[str(self.delta)]
        return ti, xi_

    @staticmethod
    def vi(tbl, rho):
        """Интерполяция таблицы 11_6"""

        tbl.index = pd.to_numeric(tbl.index)
        new_index = np.unique(np.union1d(list(tbl.index), rho))
        new_tb = tbl.reindex(new_index).interpolate(method='polynomial', order=2)
        return new_tb

    def v_i(self, tbl, rho, chi):
        """Коэффициент корреляции"""

        tbl = self.vi(tbl, rho)
        tb = tbl[tbl.index <= 640]
        v_ = tb[str(chi)]
        return v_

    def x_y_z(self, h):
        """Параметры коэффициента корреляции"""

        b = self.d
        if self.xyz == 'z0y':
            rho = b
            chi = h
        elif self.xyz == 'z0x':
            rho = 0.4 * self.a
            chi = h
        else:
            rho = b
            chi = self.a
        return rho, chi

    @staticmethod
    def w_g(f, fl, wm, zet, xi, v):
        """Пульсационная составляющая основной ветровой нагрузки"""

        if f[0] >= fl:
            wg = (wm * zet) * v
        elif f[0] < fl <= f[1]:
            wg = ((wm * xi) * zet) * v
        else:
            wg = wm * 0
            print('Вторая собственная частота меньше предельной !', np.round(f[1], 4), '<', np.round(fl, 4))
        return wg

    def calc(self):
        """Расчёт"""

        print('Расчёт ветровой нагрузки:')
        print('Ветровой район:', self.wind_region)
        w0 = self.table_11_1.loc[self.wind_region]  # нормативное значение ветрового давления
        print('Нормативное значение ветрового давления: w0=', w0, 'кПа')
        print('Размер здания в направлении расчетного ветра: a=', self.a, 'м')
        h = self.xi[self.n]  # высота здания от поверхности земли
        vzei = np.vectorize(self.zei)
        ze_i = vzei(h, self.xi, self.d)
        k, z_i = self.k_i(h, ze_i)
        wm = w0 * k * self.c
        zeta_i = self.zeta(h, ze_i)
        table_xi = self.tksi.set_index(['Tgi'])
        vtg_1 = np.vectorize(self.tg_1)
        tg1 = vtg_1(k, self.f[0], w0)  # безразмерный период
        ti, xi_ = self.xi_i(table_xi, tg1)  # коэффициенты динамичности
        if self.delta == 0.15:
            tglim = 0.0077
        elif self.delta == 0.22:
            tglim = 0.014
        else:
            tglim = 0.023
        fl = vtg_1(k, tglim, w0)
        flim = fl[k.shape[0] - 1]  # предельное значение частоты собственных колебаний
        print('Нормативное значение ветрового давления w0=', w0, ', [кПа]')
        print('Предельное значение частоты собственных колебаний f_lim=', np.round(flim, 3), ', [Гц]')
        rho, chi = self.x_y_z(h)
        cols = [0]
        for col in self.t11_6.columns:
            cols.append(col)
        chii = list(map(int, cols[2:]))
        chi1 = max(filter(lambda x: x <= chi, chii), default=None)
        chi2 = min(filter(lambda x: x >= chi, chii), default=None)
        table_v = self.t11_6.set_index(['rho'])
        v1 = self.v_i(table_v, rho, chi1)
        v2 = self.v_i(table_v, rho, chi2)
        v = (v1 + (v2 - v1) / (chi2 - chi1) * (chi - chi1))[self.d]  # коэффициент корреляции
        print('Коэффициент корреляции v=', np.round(v, 3))
        wg = self.w_g(self.f, flim, wm, zeta_i, xi_[tg1].to_numpy(), v)
        if self.f[1] >= flim:
            self.plot_w(wg, 'Норм. пульсационная составляющая основной ветровой нагрузки ', 'g')
            self.plot_w(wm + wg, 'Нормативное значение основной ветровой нагрузки ', '')
