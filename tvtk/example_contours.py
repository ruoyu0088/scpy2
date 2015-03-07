# -*- coding: utf-8 -*-
from example_cut_plane import read_data
from tvtk.api import tvtk
from tvtk.common import configure_input

if __name__ == "__main__":      
    plot3d = read_data()
    grid = plot3d.output.get_block(0)

    contours = tvtk.ContourFilter()
    configure_input(contours, grid)
    contours.generate_values(8, grid.point_data.scalars.range)
    mapper = tvtk.PolyDataMapper(scalar_range = grid.point_data.scalars.range)
    configure_input(mapper, contours)
    actor = tvtk.Actor(mapper = mapper)
    #actor.property.opacity = 0.3

    outline = tvtk.StructuredGridOutlineFilter()
    configure_input(outline, grid)
    outline_mapper = tvtk.PolyDataMapper()
    configure_input(outline_mapper, outline)
    outline_actor = tvtk.Actor(mapper = outline_mapper)
    outline_actor.property.color = 0.3, 0.3, 0.3
    
    from scpy2.tvtk.tvtkhelp import ivtk_scene
    win = ivtk_scene([actor, outline_actor])
    win.scene.isometric_view()

    from pyface.api import GUI
    gui = GUI()
    gui.start_event_loop()    