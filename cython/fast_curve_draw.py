import numpy as np
import pylab as pl
from scpy2.cython import get_peaks


def make_noise_sin_wave(period, n):
    np.random.seed(42)

    x = np.random.uniform(0, 2*np.pi*period, n)
    x.sort()
    y = np.sin(x)
    m = int(n*0.01)
    y[np.random.randint(0, n, m)] += np.random.randn(m) * 0.4
    return x, y


def main():
    x, y = make_noise_sin_wave(10, 10000)


    ax = pl.subplot(111)
    x, y = make_noise_sin_wave(20, 100000)
    line, = pl.plot(*get_peaks(x, y, 500))

    ax = pl.gca()

    def update_data(ax):
        x0, x1 = ax.get_xlim()
        line.set_data(*get_peaks(x, y, 500, x0, x1))
        ax.figure.canvas.draw_idle()

    ax.callbacks.connect('xlim_changed', update_data)
    pl.show()


if __name__ == '__main__':
    main()