import numpy as np
import matplotlib

matplotlib.use("TkAgg")  # This program works with Qt only

def exp_sin(x, A, f, z, p):
    return A * np.sin(2 * np.pi * f * x + p)  * np.exp(z * x)


import pylab as pl

fig, ax = pl.subplots()

x = np.linspace(1e-6, 1, 500)
pars = {"A":1.0, "f":2, "z":-0.2, "p":0}
y = exp_sin(x, **pars)

line, = pl.plot(x, y)

def update(**kw):
    y = exp_sin(x, **kw)
    line.set_data(x, y)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw_idle()

from scpy2.matplotlib.gui_panel import TkSliderPanel

panel = TkSliderPanel(fig, [("A", 0, 10), ("f", 0, 10), ("z", -3, 0), ("p", 0, 2*np.pi)],
                      update, cols=2, min_value_width=80)
panel.set_parameters(**pars)

pl.show()