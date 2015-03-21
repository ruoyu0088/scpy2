# -*- coding: utf-8 -*-
from example_cut_plane import read_data
import numpy as np
from tvtk.api import tvtk
from scpy2.tvtk.tvtkhelp import ivtk_scene, event_loop, make_outline


plot3d = read_data()
grid = plot3d.output.get_block(0)

mask = tvtk.MaskPoints(random_mode=True, on_ratio=50)
mask.set_input_data(grid)

arrow_source = tvtk.ArrowSource()
arrows = tvtk.Glyph3D(input_connection=mask.output_port,
                      scale_factor=2/np.max(grid.point_data.scalars.to_array()))
arrows.set_source_connection(arrow_source.output_port)

arrows_mapper = tvtk.PolyDataMapper(scalar_range=grid.point_data.scalars.range, input_connection=arrows.output_port)
arrows_actor = tvtk.Actor(mapper=arrows_mapper)

center = grid.center
sphere = tvtk.SphereSource(
    center=(2, center[1], center[2]), radius=2,
    phi_resolution=6, theta_resolution=6)
sphere_mapper = tvtk.PolyDataMapper(input_connection=sphere.output_port)

sphere_actor = tvtk.Actor(mapper=sphere_mapper)
sphere_actor.property.set(
    representation="wireframe", color=(0, 0, 0))

streamer = tvtk.StreamLine(
    step_length=0.0001,
    integration_direction="forward",
    integrator=tvtk.RungeKutta4())
streamer.set_input_data(grid)
streamer.set_source_connection(sphere.output_port)

tube = tvtk.TubeFilter(
    input_connection=streamer.output_port,
    radius=0.05,
    number_of_sides=6,
    vary_radius="vary_radius_by_scalar")

tube_mapper = tvtk.PolyDataMapper(
    input_connection=tube.output_port,
    scalar_range=grid.point_data.scalars.range)

tube_actor = tvtk.Actor(mapper=tube_mapper)
tube_actor.property.backface_culling = True

outline_actor = make_outline(grid)

win = ivtk_scene([outline_actor, sphere_actor, tube_actor, arrows_actor])
win.scene.isometric_view()
event_loop()