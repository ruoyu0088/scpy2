# -*- coding: utf-8 -*-

from traits.api import HasTraits, Instance, Button
from traitsui.api import View, Item, HGroup, VGroup
from tvtk.api import tvtk
from tvtk.pyface.scene_editor import SceneEditor
from tvtk.pyface.scene import Scene
from tvtk.pyface.scene_model import SceneModel
from matplotlib.figure import Figure
from scpy2.traitslib import MPLFigureEditor


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
            HGroup(
                Item(name="figure", editor=MPLFigureEditor(toolbar=True)),
                Item(name="scene", editor=SceneEditor(scene_class=Scene)),
                show_labels=False
            )
        ),
        width=800,
        height=600,
        resizable=True,
    )

    def __index__(self, **kw):
        super(StereoDemo, self).__index__(**kw)


if __name__ == '__main__':
    demo = StereoDemo()
    demo.configure_traits()