# -*- coding: utf-8 -*-
import numpy as np
import time
from traits.api import HasTraits, Code, Instance, Button, Str, Float, List, on_trait_change
from traitsui.api import (View, Item, VGroup, VSplit, HSplit, HGroup, ValueEditor,
                          TableEditor, InstanceEditor, ObjectColumn)
from matplotlib.figure import Figure
from scpy2.traits import MPLFigureEditor

###1###
class Point(HasTraits):
    x = Float()
    y = Float()


point_table_editor = TableEditor(
    columns=[ObjectColumn(name='x', width=100, format="%g"),
             ObjectColumn(name='y', width=100, format="%g")],
    editable=True,
    sortable=False,
    sort_model=False,
    auto_size=False,
    row_factory=Point
)
###1###
###2###
class FunctionPlotter(HasTraits):
    figure = Instance(Figure, ()) #❶
    code = Code()  #❷
    points = List(Instance(Point), [])  #❸
    draw_button = Button("Plot")

    view = View(
        VSplit(
            Item("figure", editor=MPLFigureEditor(toolbar=True), show_label=False), #❶
            HSplit(
                VGroup(
                    Item("code", style="custom"),  #❷
                    HGroup(
                        Item("draw_button", show_label=False),
                    ),
                    show_labels=False
                ),
                Item("points", editor=point_table_editor, show_label=False)  #❸
            )
        ),
        width=800, height=600, title="Function Plotter", resizable=True
    )
###2###
###3###
    def __init__(self, **kw):
        super(FunctionPlotter, self).__init__(**kw)
        self.figure.canvas_events = [ #❶
            ("button_press_event", self.memory_location),
            ("button_release_event", self.update_location)
        ]
        self.button_press_status = None #保存鼠标按键按下时的状态
        self.lines = [] #保存所有曲线
        self.functions = [] #保存所有的曲线函数
        self.env = {} #代码的执行环境

        self.axe = self.figure.add_subplot(1, 1, 1)
        self.axe.callbacks.connect('xlim_changed', self.update_data) #❷
        self.axe.set_xlim(0, 1)
        self.axe.set_ylim(0, 1)
        self.points_line, = self.axe.plot([], [], "kx", ms=8, zorder=1000) #数据点
###3###
###6###
    def update_data(self, axe):
        xmin, xmax = axe.get_xlim()
        x = np.linspace(xmin, xmax, 500)
        for line, func in zip(self.lines, self.functions):
            y = func(x)
            line.set_data(x, y)
        self.update_figure()
###6###
###4###
    def memory_location(self, evt):
        if evt.button in (1, 3):
            self.button_press_status = time.clock(), evt.x, evt.y
        else:
            self.button_press_status = None

    def update_location(self, evt):
        if evt.button in (1, 3) and self.button_press_status is not None:
            last_clock, last_x, last_y = self.button_press_status
            if time.clock() - last_clock > 0.5: #❶
                return
            if ((evt.x - last_x) ** 2 + (evt.y - last_y) ** 2) ** 0.5 > 4: #❷
                return

        if evt.button == 1:
            if evt.xdata is not None and evt.ydata is not None:
                point = Point(x=evt.xdata, y=evt.ydata) #❸
                self.points.append(point)
        elif evt.button == 3:
            if self.points:
                self.points.pop() #❹
###4###
###5###
    @on_trait_change("points[]")
    def _points_changed(self, obj, name, new):
        for point in new:
            point.on_trait_change(self.update_points, name="x, y") #❶
        self.update_points()

    def update_points(self): #❷
        arr = np.array([(point.x, point.y) for point in self.points])
        if arr.shape[0] > 0:
            self.points_line.set_data(arr[:, 0], arr[:, 1])
        else:
            self.points_line.set_data([], [])
        self.update_figure()

    def update_figure(self): #❸
        if self.figure.canvas is not None: #❹
            self.figure.canvas.draw_idle()
###5###
###7###
    def _draw_button_fired(self):
        self.plot_lines()

    def plot_lines(self):
        xmin, xmax = self.axe.get_xlim() #❶
        x = np.linspace(xmin, xmax, 500)
        self.env = {"points": np.array([(point.x, point.y) for point in self.points])} #❷
        exec self.code in self.env

        results = []
        for line in self.lines:
            line.remove()
        self.axe.set_color_cycle(None) #重置颜色循环
        self.functions = []
        self.lines = []
        for name, value in self.env.items(): #❸
            if name.startswith("_"): #忽略以_开头的名字
                continue
            if callable(value):
                try:
                    y = value(x)
                    if y.shape != x.shape: #输出数组应该与输入数组的形状一致
                        raise ValueError("the return shape is not the same as x")
                except Exception as ex:
                    import traceback
                    print "failed when call function {}\n".format(name)
                    traceback.print_exc()
                    continue

                results.append((name, y))
                self.functions.append(value)

        for (name, y), function in zip(results, self.functions):
            #如果函数有plot_parameters属性,则用其作为plot()的参数
            kw = getattr(function, "plot_parameters", {})  #❹
            label = kw.get("label", name)
            line, = self.axe.plot(x, y, label=label, **kw)
            self.lines.append(line)

        points = self.env.get("points", None) #❺
        if points is not None:
            self.points = [Point(x=x, y=y) for x, y in np.asarray(points).tolist()]

        self.axe.legend()
        self.update_figure()
###7###

demo_fit = """
import numpy as np
from scipy import optimize

def _func(x, p):
    A, k, theta = p
    return A*np.sin(2*np.pi*k*x+theta)

def _residuals(p, y, x):
    return y - _func(x, p)

x = np.linspace(0, 2*np.pi, 100)
A, k, theta = 10, 0.34, np.pi/6
y0 = _func(x, [A, k, theta])
y1 = y0 + 2 * np.random.randn(len(x))

points = np.c_[x, y1]

p0 = [7, 0.40, 0]
plsq = optimize.leastsq(_residuals, p0, args=(y1, x))

def leastsq_fit(x):
    return _func(x, plsq[0])

def real_function(x):
    return _func(x, [A, k, theta])

parameters = dict(lw=3, alpha=0.8)
leastsq_fit.plot_parameters = parameters
real_function.plot_parameters = parameters
""".strip()


if __name__ == '__main__':
    plotter = FunctionPlotter(code=demo_fit)
    plotter.configure_traits()