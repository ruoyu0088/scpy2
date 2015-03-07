# -*- coding: utf-8 -*-

from tvtk.api import tvtk
from scpy2.tvtk.tvtkhelp import ivtk_scene, event_loop

cs = tvtk.ConeSource(height=3.0, radius=1.0, resolution=36)
m = tvtk.PolyDataMapper(input_connection=cs.output_port)
a = tvtk.Actor(mapper=m)

win = ivtk_scene([a])
win.scene.isometric_view()
event_loop()