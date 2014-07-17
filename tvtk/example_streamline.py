# -*- coding: utf-8 -*-
from example_cut_plane import read_data
import numpy as np
from tvtk.api import tvtk

###1###
# 读入数据
plot3d = read_data()

# 矢量箭头
mask = tvtk.MaskPoints(input = plot3d.output, random_mode=True,
                        on_ratio=50, maximum_number_of_points=10000) #{1}
arrow_source = tvtk.ArrowSource() #{2}
arrows = tvtk.Glyph3D(input = mask.output, source=arrow_source.output, #{3}
    scale_factor=2/np.max(plot3d.output.point_data.scalars.to_array())) 
arrows_mapper = tvtk.PolyDataMapper(input = arrows.output, 
    scalar_range = plot3d.output.point_data.scalars.range)
arrows_actor = tvtk.Actor(mapper = arrows_mapper)
###1###
###2###
# 作为流线起点的球
center = plot3d.output.center
sphere = tvtk.SphereSource(  #{1}
    center=(2, center[1], center[2]), radius=2, 
    phi_resolution=6, theta_resolution=6)
sphere_mapper = tvtk.PolyDataMapper(input = sphere.output)
sphere_actor = tvtk.Actor(mapper = sphere_mapper)
sphere_actor.property.set(
    representation = "wireframe", color=(0,0,0))

# 流线    
streamer = tvtk.StreamLine( #{2}
    input = plot3d.output,
    source = sphere.output,
    step_length = 0.0001,
    integration_direction = "forward", 
    integrator = tvtk.RungeKutta4()) #{3}
    
tube = tvtk.TubeFilter( #{4}
    input = streamer.output,
    radius = 0.05,
    number_of_sides = 6,
    vary_radius = "vary_radius_by_scalar")

tube_mapper = tvtk.PolyDataMapper(
    input = tube.output,
    scalar_range = plot3d.output.point_data.scalars.range)
tube_actor = tvtk.Actor(mapper = tube_mapper)  
tube_actor.property.backface_culling = True
###2###
# StructuredGrid网格的外框
outline = tvtk.StructuredGridOutlineFilter(input = plot3d.output)
outline_mapper = tvtk.PolyDataMapper(input = outline.output)
outline_actor = tvtk.Actor(mapper = outline_mapper)
outline_actor.property.color = 0.3, 0.3, 0.3

from scpy2.tvtk.tvtkhelp import ivtk_scene
win = ivtk_scene([outline_actor, sphere_actor, tube_actor, arrows_actor])
win.scene.isometric_view()

from pyface.api import GUI
gui = GUI()
gui.start_event_loop()