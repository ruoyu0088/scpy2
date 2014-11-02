# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Qt4Agg")

from os import path
from glob import glob
import numpy as np
import pylab as pl
from itertools import cycle

from matplotlib.collections import CircleCollection, Collection
from matplotlib.transforms import Affine2D
from matplotlib.animation import FuncAnimation


FRAMES = 30


class DataCircleCollection(CircleCollection):

    def set_sizes(self, sizes):
        self._sizes = sizes

    def draw(self, render):
        ax = self.axes

        m = ax.transData.get_affine().get_matrix()
        ms = np.zeros((len(self._sizes), 3, 3))
        ms[:, 0, 0] = self._sizes
        ms[:, 1, 1] = self._sizes
        ms[:, 2, 2] = 1
        self._transforms = [Affine2D(m) for m in ms]

        m = ax.transData.get_affine().get_matrix().copy()
        m[:2, 2:] = 0
        self.set_transform(Affine2D(m))

        return Collection.draw(self, render)


def draw_circles(circles, scale=1.0, lw=0.1, ax=None):
    if ax is None:
        fig, ax = pl.subplots(figsize=(8, 8))
    ax.set_aspect("equal")

    circles = np.asarray(circles)
    radius = circles[:, 2] * scale
    centers = circles[:, :2]
    colors = circles[:, 3:]

    cc = DataCircleCollection(radius,
                           offsets=centers, transOffset=ax.transData,
                           facecolors=colors, edgecolors="white", lw=lw)
    ax.add_collection(cc)
    return ax, cc


def update_circles(circles, cc, scale, random=0):
    circles = np.asarray(circles)
    radius = circles[:, 2] * scale

    centers = circles[:, :2]
    if random > 0:
        centers = centers + np.random.normal(0, random, size=(len(circles), 2))

    colors = circles[:, 3:]
    cc.set_offsets(centers)
    cc.set_facecolors(colors)
    cc.set_sizes(radius)


photo_circles = []
for fn in glob(path.join(path.dirname(__file__), "*.csv")):
    circles = np.loadtxt(fn, delimiter=",")
    circles[:, 3:] /= 256.0
    photo_circles.append(circles)

photos = cycle(photo_circles)


fig, ax = pl.subplots(figsize=(6, 6))
fig.subplots_adjust(0, 0, 1, 1, 0, 0)
ax.axis("off")
ax.axis((0, 512, 512, 0))
current_photo = photos.next().copy()
next_photo = photos.next().copy()
_, cc = draw_circles(current_photo, ax=ax, scale=1.1)
cc.set_animated(True)
rate = 0.05

random_choices = cycle([0.0, 0.5, 1.0])
scale_choices = cycle([1.15, 1.2, 1.05, 1.1])
random_std = random_choices.next()
scale = scale_choices.next()

pause = False

def on_key(event):
    if event.key == "r":
        global random_std
        random_std = random_choices.next()
    elif event.key == "a":
        global scale
        scale = scale_choices.next()
    elif event.key == " ":
        global pause
        pause = not pause

fig.canvas.mpl_connect("key_press_event", on_key)


def ani_function(i):
    global current_photo, next_photo, rate
    if not pause:
        current_photo[:] = current_photo + rate * (next_photo - current_photo)
        rate += 0.02
        if i % FRAMES == FRAMES - 1:
            current_photo = next_photo
            next_photo = photos.next().copy()
            rate = 0.05

    update_circles(current_photo, cc, scale, random=random_std)
    return cc,

ani = FuncAnimation(fig, ani_function, interval=30, blit=True)

pl.show()


