import sys
from matplotlib import pyplot as plt

fig, ax = plt.subplots()
text = ax.text(0.5, 0.5, "event", ha="center", va="center", fontdict={"size": 20})

def on_key_press(event):
    text.set_text(event.key)
    fig.canvas.draw_idle()


fig.canvas.mpl_connect('key_press_event', on_key_press)

plt.show()