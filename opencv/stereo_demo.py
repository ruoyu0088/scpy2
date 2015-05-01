# -*- coding: utf-8 -*-
from os import path
import numpy as np
import cv2
from traits.api import HasTraits, Instance, Button
from traitsui.api import View, Item, HGroup, VGroup, HSplit
from tvtk.api import tvtk
from tvtk.pyface.scene_editor import SceneEditor
from tvtk.pyface.scene import Scene
from tvtk.pyface.scene_model import SceneModel
from matplotlib.figure import Figure
from scpy2.traits import MPLFigureEditor

FOLDER = path.join(path.dirname(__file__), "stereo")


class StereoDemo(HasTraits):

    update_button = Button(u"Update")
    scene = Instance(SceneModel, ())
    figure = Instance(Figure, ())

    view = View(
        VGroup(
            HGroup(
                "update_button",
                show_labels=False
            ),
            HSplit(
                Item(name="figure", editor=MPLFigureEditor(toolbar=False)),
                Item(name="scene", editor=SceneEditor(scene_class=Scene)),
                show_labels=False
            )
        ),
        title="Stereo Camera Demo",
        width=800,
        height=400,
        resizable=True,
    )

    def __init__(self, **kw):
        super(StereoDemo, self).__init__(**kw)
        self.axes = self.figure.add_subplot(111)

    def _update_button_fired(self):
        self.calc()

    def calc(self):
        img_left = cv2.pyrDown(cv2.imread(path.join(FOLDER, 'aloeL.jpg')))
        img_right = cv2.pyrDown(cv2.imread(path.join(FOLDER, 'aloeR.jpg')))

        img_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2RGB)
        img_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2RGB)

        stereo_parameters = dict(
            SADWindowSize=5,
            numDisparities=192,
            preFilterCap=4,
            minDisparity=-24,
            uniquenessRatio=1,
            speckleWindowSize=150,
            speckleRange=2,
            disp12MaxDiff=10,
            fullDP=False,
            P1=600,
            P2=2400)

        stereo = cv2.StereoSGBM(**stereo_parameters)
        disparity = stereo.compute(img_left, img_right).astype(np.float32) / 16

        h, w = img_left.shape[:2]
        ygrid, xgrid = np.mgrid[:h, :w]
        ygrid = ygrid.astype(np.float32)
        xgrid = xgrid.astype(np.float32)

        Bf = w * 0.8
        x = (xgrid - w * 0.5)
        y = (ygrid - h * 0.5)
        d = (disparity + 1e-6)
        z = (Bf / d).ravel()
        x = (x / d).ravel()
        y = -(y / d).ravel()

        mask = (z > 0) & (z < 30)
        points = np.c_[x, y, z][mask]
        colors = img_left.reshape(-1, 3)[mask]

        poly = tvtk.PolyData()
        poly.points = points
        poly.verts = np.arange(len(points)).reshape(-1, 1)
        poly.point_data.scalars = colors.astype(np.uint8)
        mapper = tvtk.PolyDataMapper()
        mapper.set_input_data(poly)
        actor = tvtk.Actor(mapper=mapper)
        self.scene.add_actor(actor)
        self.scene.camera.position = (0, 20, -60)
        self.scene.camera.view_up = 0, 1, 0
        self.scene.render()

        self.axes.clear()
        self.axes.imshow(disparity)
        self.figure.canvas.draw()


if __name__ == '__main__':
    demo = StereoDemo()
    demo.configure_traits()