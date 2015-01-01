import numpy as np
from matplotlib import pyplot as plt

fig, ax = plt.subplots()
rect = plt.Rectangle((np.pi, -0.5), 1, 1, fc=np.random.random(3), picker=True)
ax.add_patch(rect)
x = np.linspace(0, np.pi * 2, 100)
y = np.sin(x)
line, = plt.plot(x, y, picker=8.0)


def on_pick(event):
    artist = event.artist
    if isinstance(artist, plt.Line2D):
        lw = artist.get_linewidth()
        artist.set_linewidth(lw % 5 + 1)
    else:
        artist.set_fc(np.random.random(3))
    fig.canvas.draw_idle()


fig.canvas.mpl_connect('pick_event', on_pick)
plt.show()