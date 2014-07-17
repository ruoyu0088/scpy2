# -*- coding: utf-8 -*-
from example_cut_plane import read_data
from tvtk.api import tvtk

if __name__ == "__main__":      
    plot3d = read_data()
    contours = tvtk.ContourFilter(input = plot3d.output) 
    contours.generate_values(8, plot3d.output.point_data.scalars.range) #{1}
    mapper = tvtk.PolyDataMapper(input = contours.output,
        scalar_range = plot3d.output.point_data.scalars.range) #{2}
    actor = tvtk.Actor(mapper = mapper)
    actor.property.opacity = 0.3 #{3}
    
    # StructuredGridÍø¸ñµÄÍâ¿ò
    outline = tvtk.StructuredGridOutlineFilter(input = plot3d.output)
    outline_mapper = tvtk.PolyDataMapper(input = outline.output)
    outline_actor = tvtk.Actor(mapper = outline_mapper)
    outline_actor.property.color = 0.3, 0.3, 0.3
    
    from scpy2.tvtk.tvtkhelp import ivtk_scene
    win = ivtk_scene([actor, outline_actor])
    win.scene.isometric_view()

    from pyface.api import GUI
    gui = GUI()
    gui.start_event_loop()    