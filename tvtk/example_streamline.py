# -*- coding: utf-8 -*-
from example_cut_plane import read_data
import numpy as np
from tvtk.api import tvtk
from tvtk.common import configure_input, configure_source_data

plot3d = read_data()
grid = plot3d.output.get_block(0)

mask = tvtk.MaskPoints(random_mode=True,
                       on_ratio=50, maximum_number_of_points=1000)
configure_input(mask, grid)

arrow_source = tvtk.ArrowSource()
arrows = tvtk.Glyph3D()
arrows.set_source_connection(arrow_source.output_port)
configure_input(arrows, mask)

arrows_mapper = tvtk.PolyDataMapper(scalar_range=grid.point_data.scalars.range)
configure_input(arrows_mapper, arrows)

arrows_actor = tvtk.Actor(mapper=arrows_mapper)

center = grid.center
sphere = tvtk.SphereSource(
    center=(2, center[1], center[2]), radius=2,
    phi_resolution=6, theta_resolution=6)
sphere_mapper = tvtk.PolyDataMapper()
configure_input(sphere_mapper, sphere)

sphere_actor = tvtk.Actor(mapper=sphere_mapper)
sphere_actor.property.set(
    representation="wireframe", color=(0, 0, 0))

streamer = tvtk.StreamLine(
    step_length=0.0001,
    integration_direction="forward",
    integrator=tvtk.RungeKutta4())
configure_input(streamer, grid)
configure_source_data(streamer, sphere.output)

tube = tvtk.TubeFilter(
    radius=0.05,
    number_of_sides=6,
    vary_radius="vary_radius_by_scalar")
configure_input(tube, streamer)

tube_mapper = tvtk.PolyDataMapper(
    scalar_range=grid.point_data.scalars.range)
configure_input(tube_mapper, tube)

tube_actor = tvtk.Actor(mapper=tube_mapper)
tube_actor.property.backface_culling = True

outline = tvtk.StructuredGridOutlineFilter()
configure_input(outline, grid)

outline_mapper = tvtk.PolyDataMapper()
configure_input(outline_mapper, outline)

outline_actor = tvtk.Actor(mapper=outline_mapper)
outline_actor.property.color = 0.3, 0.3, 0.3

from scpy2.tvtk.tvtkhelp import ivtk_scene

win = ivtk_scene([outline_actor, sphere_actor, tube_actor, arrows_actor])
win.scene.isometric_view()

from pyface.api import GUI

gui = GUI()
gui.start_event_loop()