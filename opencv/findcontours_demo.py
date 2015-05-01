# -*- coding: utf-8 -*-
import cv2
import numpy as np
from matplotlib.collections import PolyCollection
from traits.api import Enum
from traitsui.api import VGroup
from .demobase import ImageProcessDemo

MODES = ["RETR_EXTERNAL", "RETR_LIST", "RETR_CCOMP", "RETR_TREE"]
METHODS = [name for name in dir(cv2) if name.startswith("CHAIN_APPROX_")]


def get_hierarchy_depth(parent):
    depth = []
    for p in parent:
        d = 0
        while p != -1:
            p = parent[p]
            d += 1
        depth.append(d)
    return np.array(depth)


class FindContoursDemo(ImageProcessDemo):
    TITLE = u"Find Contours Demo"
    DEFAULT_IMAGE = "coins.png"

    mode = Enum(MODES)
    method = Enum(METHODS)

    def __init__(self, **kw):
        super(FindContoursDemo, self).__init__(**kw)
        self.connect_dirty("mode, method")

    def control_panel(self):
        return VGroup(
            "mode",
            "method"
        )

    def _img_changed(self):
        if self.img.dtype != np.uint8:
            return
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        img_binary = cv2.adaptiveThreshold(img_gray, 255,
                              cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                              51, 0)
        kernel = np.ones((3, 3), "u8")
        cv2.morphologyEx(img_binary, cv2.MORPH_OPEN, kernel,
                         iterations=2, dst=img_binary)
        cv2.dilate(img_binary, kernel, dst=img_binary, iterations=3)
        self.img[:] = img_binary[:, :, None]
        self.img_binary = img_binary

    def draw(self):
        mode = getattr(cv2, self.mode)
        method = getattr(cv2, self.method)
        contours, hierarchy = cv2.findContours(self.img_binary, mode, method)
        parents = hierarchy[0, :, -1]
        depth = get_hierarchy_depth(parents)
        poly_points = [c.squeeze() + (0.5, 0.5) for c in contours if len(c) > 1]
        polys = PolyCollection(poly_points, facecolors="none", array=depth, linewidths=2)
        self.axe.collections = []
        self.axe.add_collection(polys)
        self.draw_image(self.img)


if __name__ == '__main__':
    demo = FindContoursDemo()
    demo.configure_traits()