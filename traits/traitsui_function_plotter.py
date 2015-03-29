# -*- coding: utf-8 -*-
import numpy as np
import time
from traits.api import HasTraits, Code, Instance, Button, Str, Float, List, on_trait_change
from traitsui.api import (View, Item, VGroup, VSplit, HSplit, HGroup, ValueEditor,
                          TableEditor, InstanceEditor, ObjectColumn)
from matplotlib.figure import Figure
from scpy2.traits import MPLFigureEditor


class Point(HasTraits):
    x = Float()
    y = Float()

    view = View(HGroup(
        Item("x", format_str="%g"),
        Item("y", format_str="%g")))


point_table_editor = TableEditor(
    columns=[ObjectColumn(name='x', width=100, format="%g"),
             ObjectColumn(name='y', width=100, format="%g")],
    editable=True,
    sortable=False,
    sort_model=False,
    auto_size=False,
    row_factory=Point
)


class FunctionPlotter(HasTraits):
    code = Code()
    points = List(Instance(Point), [])
    figure = Instance(Figure, ())
    draw_button = Button("Plot")

    view = View(
        VSplit(
            Item("figure", editor=MPLFigureEditor(toolbar=True), show_label=False),
            HSplit(
                VGroup(
                    Item("code", style="custom"),
                    HGroup(
                        Item("draw_button", show_label=False),
                    ),
                    show_labels=False
                ),
                Item("points",
                     editor=point_table_editor,
                     show_label=False),
            )
        ),
        width=800, height=600, title="Function Plotter", resizable=True
    )

    def __init__(self, **kw):
        super(FunctionPlotter, self).__init__(**kw)
        self.figure.canvas_events = [
            ("button_press_event", self.memory_location),
            ("button_release_event", self.update_location)
        ]
        self.lines = []
        self.functions = []
        self.env = {}
        self.button_press_status = None

        self.axe = self.figure.add_subplot(1, 1, 1)
        self.axe.callbacks.connect('xlim_changed', self.update_data)
        self.axe.set_xlim(0, 1)
        self.axe.set_ylim(0, 1)
        self.points_line, = self.axe.plot([], [], "kx", ms=8, zorder=1000)

    def update_data(self, axe):
        xmin, xmax = axe.get_xlim()
        x = np.linspace(xmin, xmax, 500)
        for line, func in zip(self.lines, self.functions):
            y = func(x)
            line.set_data(x, y)
        self.update_figure()

    def memory_location(self, evt):
        if evt.button in (1, 3):
            self.button_press_status = time.clock(), evt.x, evt.y
        else:
            self.button_press_status = None

    def update_location(self, evt):
        if evt.button in (1, 3) and self.button_press_status is not None:
            last_clock, last_x, last_y = self.button_press_status
            if time.clock() - last_clock > 0.5:
                return
            if ((evt.x - last_x) ** 2 + (evt.y - last_y) ** 2) ** 0.5 > 4:
                return

        if evt.button == 1:
            if evt.xdata is not None and evt.ydata is not None:
                point = Point(x=evt.xdata, y=evt.ydata)
                self.points.append(point)
        elif evt.button == 3:
            if self.points:
                self.points.pop()

    @on_trait_change("points[]")
    def _points_changed(self, obj, name, new):
        for point in new:
            point.on_trait_change(self.update_points, name="x, y")
        self.update_points()

    def update_points(self):
        arr = np.array([(point.x, point.y) for point in self.points])
        if arr.shape[0] > 0:
            self.points_line.set_data(arr[:, 0], arr[:, 1])
        else:
            self.points_line.set_data([], [])
        self.update_figure()

    def update_figure(self):
        if self.figure.canvas is not None:
            self.figure.canvas.draw_idle()

    def _draw_button_fired(self):
        self.plot_lines()

    def plot_lines(self):
        xmin, xmax = self.axe.get_xlim()
        x = np.linspace(xmin, xmax, 500)
        self.env = {"points": np.array([(point.x, point.y) for point in self.points])}
        exec self.code in self.env
        results = []
        for line in self.lines:
            line.remove()
        self.axe.set_color_cycle(None)
        self.functions = []
        self.lines = []
        for name, value in self.env.items():
            if callable(value):
                try:
                    y = value(x)
                    if y.shape != x.shape:
                        raise ValueError("the return shape is not the same as x")
                except Exception as ex:
                    import traceback

                    print "failed when call function {}\n".format(name)
                    traceback.print_exc()
                    continue
                results.append((name, y))
                self.functions.append(value)

        for name, y in results:
            line, = self.axe.plot(x, y, label=name)
            self.lines.append(line)

        self.axe.legend()
        self.update_figure()


if __name__ == '__main__':
    plotter = FunctionPlotter(code="""
from numpy import sin, cos
""".strip())
    plotter.configure_traits()