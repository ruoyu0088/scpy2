import numpy as np
from matplotlib import pyplot as plt

fig, ax = plt.subplots()
x = np.linspace(0, 10, 1000)
line, = ax.plot(x, np.sin(x))


def on_key_press(event):
    if event.key in 'rgbcmyk':
        line.set_color(event.key)
    fig.canvas.draw_idle()


fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
fig.canvas.mpl_connect('key_press_event', on_key_press)

plt.show()