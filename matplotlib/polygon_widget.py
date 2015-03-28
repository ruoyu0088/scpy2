# -*- coding: utf-8 -*-
import numpy as np
from traits.api import (HasTraits, Str, Int, List, Instance, Button, Bool,
                        on_trait_change, Array, Dict, Event)
from traitsui.api import View, Item, Handler, VGroup, HGroup, EnumEditor
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
from scpy2.traits import PositionHandler, MPLFigureEditor


class PolygonWidget(HasTraits):
    points = Array(dtype=float, shape=(None, 2))
    axe = Instance(Axes)
    style = Dict()
    line = Instance(Line2D)
    _selected_index = Int(-1)
    changed = Event

    view = View(
        "points"
    )

    def __init__(self, **kw):
        super(PolygonWidget, self).__init__(**kw)
        x, y = self.get_xy()
        self.line, = self.axe.plot(x, y, **self.style)
        canvas = self.axe.figure.canvas
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)

    def button_press_callback(self, event):
        if event.inaxes is self.axe and event.button == 1:
            self._selected_index = self.get_nearest_index(event.x, event.y)

    def button_release_callback(self, event):
        self._selected_index = -1

    def motion_notify_callback(self, event):
        if event.button == 1 and self._selected_index >= 0:
            self.points[self._selected_index] = event.xdata, event.ydata
            self.update()

    def get_nearest_index(self, x, y):
        points = self.axe.transData.transform(self.points)
        diff = points - [x, y]
        dist = np.sum(diff**2, axis=1)**0.5
        index = np.argmin(dist)
        return index if dist[index] < 5 else -1

    def get_xy(self):
        points = np.vstack((self.points, self.points[:1]))
        return points.T

    def update(self):
        x, y = self.get_xy()
        self.line.set_data(x, y)
        self.changed = True

    def set_points(self, points):
        self.points = points
        self.update()


class PolygonWidgetDemo(HasTraits):
    figure = Instance(Figure, ())
    polygon = Instance(PolygonWidget)

    view = View(
        Item("figure", editor=MPLFigureEditor(toolbar=True), show_label=False),
        resizable=True,
        width=800,
        height=600,
        handler=PositionHandler()
    )

    def __init__(self, **kw):
        super(PolygonWidgetDemo, self).__init__(**kw)
        self.axe = self.figure.add_subplot(111)

    def on_position(self):
        points = np.array([[0, 0], [1, 0], [0, 1.0]])
        style = {"marker": "o"}
        self.polygon = PolygonWidget(axe=self.axe, points=points, style=style)
        self.polygon.on_trait_change(lambda:self.figure.canvas.draw(), "changed")


if __name__ == '__main__':
    demo = PolygonWidgetDemo()
    demo.configure_traits()