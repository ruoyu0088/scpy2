# -*- coding: utf-8 -*-
from os import path
import numpy as np

from matplotlib.figure import Figure
from matplotlib.colors import LogNorm
from matplotlib import cm
from traitsui.api import View, Item, Handler, VGroup, HGroup, EnumEditor
from traits.api import (HasTraits, Str, Int, List, Instance, Button, Bool,
                        on_trait_change)
from pyface.timer.api import Timer
from scpy2.traits import MPLFigureEditor, SettingManager
from .fastfractal import IFS

FOLDER = path.dirname(__file__)
DATA_FILE = path.join(FOLDER, "IFS_data.json")

###1###
def solve_eq(triangle1, triangle2):
    """
    解方程，从triangle1变换到triangle2的变换系数
        triangle1,2是二维数组：
        x0,y0
        x1,y1
        x2,y2
    """
    x0, y0 = triangle1[0]
    x1, y1 = triangle1[1]
    x2, y2 = triangle1[2]

    a = np.zeros((6, 6), dtype=np.float)
    b = triangle2.reshape(-1)
    a[0, 0:3] = x0, y0, 1
    a[1, 3:6] = x0, y0, 1
    a[2, 0:3] = x1, y1, 1
    a[3, 3:6] = x1, y1, 1
    a[4, 0:3] = x2, y2, 1
    a[5, 3:6] = x2, y2, 1

    x = np.linalg.solve(a, b)
    x.shape = (2, 3)
    return x
###1###
###2###
def triangle_area(triangle):
    """
    计算三角形的面积
    """
    A, B, C = triangle
    AB = A - B
    AC = A - C
    return np.abs(np.cross(AB, AC)) / 2.0
###2###

class IFSTriangles(HasTraits):
    """
    三角形编辑器
    """
    version = Int(0)  # 三角形更新标志

    def __init__(self, ax):
        super(IFSTriangles, self).__init__()
        self.colors = ["r", "g", "b", "c", "m", "y", "k"]
        self.points = np.array([(0, 0), (2, 0), (2, 4), (0, 1), (1, 1),
                                (1, 3), (1, 1), (2, 1), (2, 3)], dtype=np.float)
        self.equations = self.get_eqs()
        self.ax = ax
        self.ax.set_ylim(-10, 10)
        self.ax.set_xlim(-10, 10)
        canvas = ax.figure.canvas
        # 绑定canvas的鼠标事件
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas = canvas
        self._ind = None
        self.background = None
        self.update_lines()

    def refresh(self):
        """
        重新绘制所有的三角形
        """
        self.update_lines()
        self.canvas.draw()
        self.version += 1

    def del_triangle(self):
        """
        删除最后一个三角形
        """
        self.points = self.points[:-3].copy()
        self.refresh()

    def add_triangle(self):
        """
        添加一个三角形
        """
        self.points = np.vstack((self.points, np.array([(0, 0), (1, 0), (0, 1)], dtype=np.float)))
        self.refresh()

    def set_points(self, points):
        """
        直接设置三角形定点
        """
        self.points = points[:]
        self.refresh()

    def get_eqs(self):
        """
        计算所有的仿射方程
        """
        eqs = []
        for i in range(1, len(self.points) / 3):
            eqs.append(solve_eq(self.points[:3, :], self.points[i * 3:i * 3 + 3, :]))
        return np.vstack(eqs)

    def get_areas(self):
        """
        通过三角形的面积计算仿射方程的迭代概率
        """
        areas = []
        for i in range(1, len(self.points) / 3):
            areas.append(triangle_area(self.points[i * 3:i * 3 + 3, :]))
        s = sum(areas)
        return [x / s for x in areas]

    def update_lines(self):
        """
        重新绘制所有的三角形
        """
        del self.ax.lines[:]
        for i in xrange(0, len(self.points), 3):
            color = self.colors[i / 3 % len(self.colors)]
            x0, x1, x2 = self.points[i:i + 3, 0]
            y0, y1, y2 = self.points[i:i + 3, 1]
            type = color + "%so"
            if i == 0:
                linewidth = 3
            else:
                linewidth = 1
            self.ax.plot([x0, x1], [y0, y1], type % "-", linewidth=linewidth)
            self.ax.plot([x1, x2], [y1, y2], type % "--", linewidth=linewidth)
            self.ax.plot([x0, x2], [y0, y2], type % ":", linewidth=linewidth)

        self.ax.set_ylim(-10, 10)
        self.ax.set_xlim(-10, 10)

    def button_release_callback(self, event):
        """
        鼠标按键松开事件
        """
        self._ind = None

    def button_press_callback(self, event):
        """
        鼠标按键按下事件
        """
        if event.inaxes != self.ax: return
        if event.button != 1: return
        self._ind = self.get_ind_under_point(event.xdata, event.ydata)

    def get_ind_under_point(self, mx, my):
        """
        找到距离mx, my最近的顶点
        """
        for i, p in enumerate(self.points):
            if abs(mx - p[0]) < 0.5 and abs(my - p[1]) < 0.5:
                return i
        return None

    def motion_notify_callback(self, event):
        """
        鼠标移动事件
        """
        self.event = event
        if self._ind is None: return
        if event.inaxes != self.ax: return
        if event.button != 1: return
        x, y = event.xdata, event.ydata

        # 更新定点坐标
        self.points[self._ind, :] = [x, y]

        i = self._ind / 3 * 3
        # 更新顶点对应的三角形线段
        x0, x1, x2 = self.points[i:i + 3, 0]
        y0, y1, y2 = self.points[i:i + 3, 1]
        self.ax.lines[i].set_data([x0, x1], [y0, y1])
        self.ax.lines[i + 1].set_data([x1, x2], [y1, y2])
        self.ax.lines[i + 2].set_data([x0, x2], [y0, y2])

        # 背景为空时，捕捉背景
        if self.background == None:
            self.ax.clear()
            self.ax.set_axis_off()
            self.canvas.draw()
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)
            self.update_lines()

        # 快速绘制所有三角形
        self.canvas.restore_region(self.background)  # 恢复背景
        # 绘制所有三角形
        for line in self.ax.lines:
            self.ax.draw_artist(line)
        self.canvas.blit(self.ax.bbox)

        self.version += 1


class IFSHandler(Handler):
    """
    在界面显示之前需要初始化的内容
    """

    def init(self, info):
        info.object.init_gui_component()
        return True


class IFSDesigner(HasTraits):
    color_maps = List
    current_map = Str("Greens")
    figure = Instance(Figure)  # 控制绘图控件的Figure对象
    ifs_triangle = Instance(IFSTriangles)
    add_button = Button(u"添加三角形")
    del_button = Button(u"删除三角形")
    settings = Instance(SettingManager)
    clear = Bool(True)

    view = View(
        VGroup(
            HGroup(
                Item("add_button"),
                Item("del_button"),
                Item("settings", style="custom"),
                Item("current_map", editor=EnumEditor(name="color_maps")),
                show_labels=False
            ),
            Item("figure", editor=MPLFigureEditor(toolbar=False),
                 show_label=False),
        ),
        resizable=True,
        height=450,
        width=800,
        title=u"迭代函数系统设计器",
        handler=IFSHandler()
    )

    def _settings_default(self):
        settings = SettingManager(target=self)
        return settings

    def _color_maps_default(self):
        return sorted(cm.cmap_d.keys())

    def load_settings(self, setting):
        self.ifs_triangle.set_points(np.array(setting["points"]))
        self.current_map = setting["cmap"]

    def get_settings(self):
        return dict(points=self.ifs_triangle.points.tolist(),
                    cmap=self.current_map)

    def _add_button_fired(self):
        """
        添加三角形按钮事件处理
        """
        self.ifs_triangle.add_triangle()

    def _del_button_fired(self):
        self.ifs_triangle.del_triangle()

    def ifs_calculate(self):
        if self.clear == True:
            self.clear = False
            self.initpos = [0, 0]
            p = self.ifs_triangle.get_areas()
            eqs = self.ifs_triangle.get_eqs()
            self.ifs = IFS(p, eqs, 100000, size=600)
            self.ax2.clear()
            self.img = self.ax2.imshow(np.ones((10, 10)), norm=LogNorm(),
                                       cmap=self.current_map, origin="lower")
            self.ax2.set_aspect("equal")
            self.ax2.axis("off")

        try:
            count = self.ifs.update()
        except ZeroDivisionError:
            count = None
        if count is None:
            return
        self.img.set_data(count)
        self.img.norm.autoscale(count)
        self.img.set_cmap(self.current_map)
        h, w = count.shape
        self.img.set_extent([0, w, 0, h])
        self.ax2.set_xlim(0, w)
        self.ax2.set_ylim(0, h)
        self.figure.canvas.draw()

    @on_trait_change("ifs_triangle.version")
    def on_ifs_version_changed(self):
        """
        当三角形更新时，重新绘制所有的迭代点
        """
        self.clear = True

    def _figure_default(self):
        """
        figure属性的缺省值，直接创建一个Figure对象
        """
        figure = Figure(figsize=(8, 4), dpi=100)
        self.ax = figure.add_subplot(121)
        self.ax2 = figure.add_subplot(122)
        self.ax.set_axis_off()
        figure.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
        figure.patch.set_facecolor("w")
        return figure

    def init_gui_component(self):
        self.ifs_triangle = IFSTriangles(self.ax)
        self.figure.canvas.draw()
        self.settings.select_last()
        self.timer = Timer(10, self.ifs_calculate)


if __name__ == "__main__":
    designer = IFSDesigner()
    designer.configure_traits()