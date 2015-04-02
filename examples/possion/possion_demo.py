# -*- coding: utf-8 -*-
from os import path
import numpy as np
from traits.api import HasTraits, Instance, Int, Button, File
from traitsui.api import View, Group, Item, Controller, HGroup, VGroup
from matplotlib.figure import Figure
from scpy2.traits.mpl_figure_editor import MPLFigureEditor
from scpy2.matplotlib.freedraw_widget import ImageMaskDrawer
import cv2


FOLDER = path.dirname(__file__)


def possion_mix(src, dst, src_mask, offset):
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve

    offset_x, offset_y = offset
    src_mask = (src_mask > 128).astype(np.uint8)
    src_y, src_x = np.where(src_mask)

    src_laplacian = cv2.Laplacian(src, cv2.CV_16S, ksize=1)[src_y, src_x, :]

    dst_mask = np.zeros(dst.shape[:2], np.uint8)
    dst_x, dst_y = src_x + int(offset_x), src_y + int(offset_y)
    dst_mask[dst_y, dst_x] = 1

    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
    dst_mask2 = cv2.dilate(dst_mask, kernel=kernel)

    dst_y2, dst_x2 = np.where(dst_mask2)
    dst_ye, dst_xe = np.where(dst_mask2 - dst_mask)

    variable_count = len(dst_x2)
    variable_index = np.arange(variable_count)

    variables = np.zeros(dst.shape[:2], np.int)
    variables[dst_y2, dst_x2] = variable_index

    x0 = variables[dst_y, dst_x]
    x1 = variables[dst_y - 1, dst_x]
    x2 = variables[dst_y + 1, dst_x]
    x3 = variables[dst_y, dst_x - 1]
    x4 = variables[dst_y, dst_x + 1]
    x_edge = variables[dst_ye, dst_xe]

    inner_count = len(x0)
    edge_count = len(x_edge)

    r = np.r_[x0, x0, x0, x0, x0, x_edge]
    c = np.r_[x0, x1, x2, x3, x4, x_edge]
    v = np.ones(inner_count * 5 + edge_count)
    v[:inner_count] = -4

    A = coo_matrix((v, (r, c))).tocsc()

    order = np.argsort(np.r_[variables[dst_y, dst_x], variables[dst_ye, dst_xe]])

    result = dst.copy()

    for ch in (0, 1, 2):
        b = np.r_[src_laplacian[:, ch], dst[dst_ye, dst_xe, ch]]
        u = spsolve(A, b[order])
        u = np.clip(u, 0, 255)
        result[dst_y2, dst_x2, ch] = u

    return result


class PossionDemo(HasTraits):
    left_mask = Instance(ImageMaskDrawer)
    right_mask = Instance(ImageMaskDrawer)
    left_file = File(path.join(FOLDER, "vinci_src.png"))
    right_file = File(path.join(FOLDER, "vinci_target.png"))
    figure = Instance(Figure, ())
    load_button = Button(u"Load")
    clear_button = Button(u"Clear")
    mix_button = Button(u"Mix")

    view = View(
        Item("left_file"),
        Item("right_file"),
        VGroup(
            HGroup(
                "load_button", "clear_button", "mix_button",
                show_labels=False
            ),
            Group(
                Item("figure", editor=MPLFigureEditor(toolbar=False)),
                show_labels=False,
                orientation='horizontal'
            )
        ),
        width=800,
        height=600,
        resizable=True,
        title="Possion Demo")

    def __init__(self, **kw):
        super(PossionDemo, self).__init__(**kw)
        self.left_axe = self.figure.add_subplot(121)
        self.right_axe = self.figure.add_subplot(122)

    def load_images(self):
        self.left_pic = cv2.imread(self.left_file, 1)
        self.right_pic = cv2.imread(self.right_file, 1)

        shape = [max(v1, v2) for v1, v2 in
                 zip(self.left_pic.shape[:2], self.right_pic.shape[:2])]

        self.left_img = self.left_axe.imshow(self.left_pic[::-1, :, ::-1], origin="lower")
        self.left_axe.axis("off")
        self.left_mask = ImageMaskDrawer(self.left_axe, self.left_img, mask_shape=shape)

        self.right_img = self.right_axe.imshow(self.right_pic[::-1, :, ::-1], origin="lower")
        self.right_axe.axis("off")
        self.right_mask = ImageMaskDrawer(self.right_axe, self.right_img, mask_shape=shape)

        self.left_mask.on_trait_change(self.mask_changed, "drawed")
        self.right_mask.on_trait_change(self.mask_changed, "drawed")
        self.figure.canvas.draw_idle()

    def mask_changed(self, obj, name, new):
        if obj is self.left_mask:
            src, target = self.left_mask, self.right_mask
        else:
            src, target = self.right_mask, self.left_mask
        target.array.fill(0)
        target.array[:, :] = src.array[:, :]
        target.update()
        self.figure.canvas.draw()

    def _load_button_fired(self):
        self.load_images()

    def _mix_button_fired(self):
        lh, lw, _ = self.left_pic.shape
        rh, rw, _ = self.right_pic.shape

        left_mask = self.left_mask.array[-lh:, :lw, -1]
        if np.all(left_mask==0):
            return

        dx, dy = self.right_mask.get_mask_offset()
        result = possion_mix(self.left_pic, self.right_pic, left_mask, (dx, rh - lh - dy))

        self.right_img.set_data(result[::-1, :, ::-1])
        self.right_mask.mask_img.set_visible(False)
        self.figure.canvas.draw()

    def _clear_button_fired(self):
        self.left_mask.array.fill(0)
        self.right_mask.array.fill(0)
        self.left_mask.update()
        self.right_mask.update()
        self.figure.canvas.draw()
