# -*- coding: utf-8 -*-
from example_cut_plane import read_data
from tvtk.api import tvtk
from scpy2.tvtk.tvtkhelp import ivtk_scene, event_loop, make_outline

plot3d = read_data()
grid = plot3d.output.get_block(0)

contours = tvtk.ContourFilter()
contours.set_input_data(grid)
contours.generate_values(8, grid.point_data.scalars.range)
mapper = tvtk.PolyDataMapper(scalar_range = grid.point_data.scalars.range, input_connection=contours.output_port)
actor = tvtk.Actor(mapper = mapper)
actor.property.opacity = 0.3

outline_actor = make_outline(grid)

win = ivtk_scene([actor, outline_actor])
win.scene.isometric_view()
event_loop()