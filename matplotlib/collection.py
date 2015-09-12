import numpy as np
from matplotlib.collections import CircleCollection, Collection, LineCollection
from matplotlib.transforms import Affine2D, blended_transform_factory


class DataCircleCollection(CircleCollection):

    def set_sizes(self, sizes):
        self._sizes = sizes

    def draw(self, render):
        ax = self.axes
        ms = np.zeros((len(self._sizes), 3, 3))
        ms[:, 0, 0] = self._sizes
        ms[:, 1, 1] = self._sizes
        ms[:, 2, 2] = 1
        self._transforms = ms

        m = ax.transData.get_affine().get_matrix().copy()
        m[:2, 2:] = 0
        self.set_transform(Affine2D(m))

        return Collection.draw(self, render)


def axvlines(ax, x, **kw):
    x = np.asanyarray(x)
    y0 = np.zeros_like(x)
    y1 = np.ones_like(x)
    data = np.c_[x, y0, x, y1].reshape(-1, 2, 2)
    trans = blended_transform_factory(ax.transData, ax.transAxes)
    lines = LineCollection(data, transform=trans, **kw)
    ax.add_collection(lines)

