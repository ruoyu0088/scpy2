# -*- coding: utf-8 -*-
import cv2
import numpy as np
from traits.api import Trait, Float, Tuple, Instance, Array
from traitsui.api import View, VGroup, Item, TupleEditor
from .demobase import ImageProcessDemo

Options = {
    u"以种子为标准-4联通": cv2.FLOODFILL_FIXED_RANGE | 4,
    u"以种子为标准-8联通": cv2.FLOODFILL_FIXED_RANGE | 8,
    u"以邻点为标准-4联通": 4,
    u"以邻点为标准-8联通": 8
}


class FloodFillDemo(ImageProcessDemo):
    SETTINGS = ["point", "lo_diff", "hi_diff", "option", "fill_color"]
    TITLE = u"FloodFill Demo"
    DEFAULT_IMAGE = "lena.jpg"

    lo_diff = Tuple((5, 5, 5, 5))
    hi_diff = Tuple((5, 5, 5, 5))
    fill_color = Tuple((255, 0, 0, 255))
    point = Tuple((0, 0))
    option = Trait(u"以邻点为标准-4联通", Options)

    def __init__(self, **kw):
        super(FloodFillDemo, self).__init__(**kw)
        self.connect_dirty("point,lo_diff,hi_diff,option,fill_color")
        self.overlay_artist = self.axe.imshow(self.img, alpha=0.5, zorder=2000)
        self.marker, = self.axe.plot(self.point[0], self.img.shape[0] - self.point[1], "bo")

    def control_panel(self):
        return VGroup(
            Item("lo_diff", label=u"负方向范围",  width=-20, editor=TupleEditor(cols=2)),
            Item("hi_diff", label=u"正方向范围", editor=TupleEditor(cols=2)),
            Item("fill_color", label=u"填充颜色", editor=TupleEditor(cols=2)),
            Item("point", label=u"种子坐标", editor=TupleEditor(cols=2, labels=["x", "y"])),
            Item("option", label=u"算法标志")
        )

    def init_draw(self):
        self.figure.canvas.mpl_connect('button_press_event', self.on_mouse_press)

    def on_mouse_press(self, event):
        if event.inaxes is self.axe:
            x, y = event.xdata, event.ydata
            y = self.img.shape[0] - y
            self.point = int(x), int(y)

    def draw(self):
        img = self.img.copy()
        cv2.floodFill(img, None, self.point,
                      self.fill_color,
                      loDiff=self.lo_diff,
                      upDiff=self.hi_diff,
                      flags=self.option_)
        self.marker.set_data(self.point[0], self.img.shape[0] - self.point[1])
        self.draw_image(self.img, draw=False)
        self.draw_image(img, artist=self.overlay_artist, draw=True)

if __name__ == '__main__':
    demo = FloodFillDemo()
    demo.configure_traits()
