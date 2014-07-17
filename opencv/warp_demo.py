# -*- coding: utf-8 -*-
import cv2
import numpy as np
from traits.api import Array, Instance, Tuple, Int, Enum, Dict
from traitsui.api import View, Item, VGroup, ArrayEditor
from scpy2.matplotlib.polygon_widget import PolygonWidget
from .demobase import ImageProcessDemo


class WrapDemo(ImageProcessDemo):
    TITLE = u"Affine & Perspective Demo"
    DEFAULT_IMAGE = "lena.jpg"

    m_afffine = Array(np.float, (2, 3))
    m_perspective = Array(np.float, (3, 3))
    size = Tuple(Int, Int)
    method = Enum(["Affine", "Perspective"])
    poly = Instance(PolygonWidget)
    points = Dict

    def __init__(self, **traits):
        super(WrapDemo, self).__init__(**traits)

        def on_method_changed(obj, name, old_value, new_value):
            self.points["{}_dst".format(old_value)] = self.poly.points.copy()
            self.poly.set_points(self.points["{}_dst".format(new_value)])

        self.on_trait_change(on_method_changed, "method")
        self.connect_dirty("poly.changed,size,method")

    def control_panel(self):
        return VGroup(
            Item("size", label=u"图像大小"),
            Item("method", label=u"变换类型", width=250),
            Item("m_afffine", label=u"变换矩阵",
                 editor=ArrayEditor(format_str="%g"), visible_when="method=='Affine'"),
            Item("m_perspective", label=u"变换矩阵",
                 editor=ArrayEditor(format_str="%g"), visible_when="method=='Perspective'"),
        )

    def init_draw(self):
        style = {"marker": "o"}
        self.poly = PolygonWidget(axe=self.axe, points=np.zeros((3, 2)), style=style)
        self.setup_widgets()

    def setup_widgets(self):
        h, w = self.img.shape[:2]
        self.size = w * 2, h * 2
        self.points = {
            "Affine_dst": np.array([[w * 0.5, h * 0.5], [w * 1.5, h * 0.5], [w * 0.5, h * 1.5]]),
            "Perspective_dst": np.array([[w * 0.5, h * 0.5], [w * 1.5, h * 0.5],
                                         [w * 1.5, h * 1.5], [w * 0.5, h * 1.5]])
        }
        offset = [w * 0.5, h * 0.5]
        self.points["Affine_src"] = (self.points["Affine_dst"] - offset).astype(np.float32)
        self.points["Perspective_src"] = (self.points["Perspective_dst"] - offset).astype(np.float32)
        self.poly.points = self.points["{}_dst".format(self.method)]
        self.poly.update()

    def _img_changed(self):
        if self.poly is not None:
            self.setup_widgets()

    def draw(self):
        if self.poly is not None:
            dst = self.poly.points.copy()
            src = self.points["{}_src".format(self.method)]
            self.points["{}_dst".format(self.method)] = dst

            dst = dst.astype(np.float32)
            if self.method == "Affine":
                self.m_afffine = cv2.getAffineTransform(src, dst)
                img2 = cv2.warpAffine(self.img, self.m_afffine,
                                      self.size, borderValue=[255]*4)
            elif self.method == "Perspective":
                self.m_perspective = cv2.getPerspectiveTransform(src, dst)
                img2 = cv2.warpPerspective(self.img, self.m_perspective,
                                           self.size, borderValue=[255]*4)
            self.draw_image(img2)
        else:
            self.draw_image(self.img)


if __name__ == '__main__':
    demo = WrapDemo()
    demo.configure_traits()