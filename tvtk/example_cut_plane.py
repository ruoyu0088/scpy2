# -*- coding: utf-8 -*-
import sip

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import os
from os import path

os.environ['ETS_TOOLKIT'] = 'qt4'

import numpy as np
from tvtk.api import tvtk


def read_data():
    # 读入数据
    folder = path.dirname(__file__)
    plot3d = tvtk.MultiBlockPLOT3DReader(
        xyz_file_name=path.join(folder, "combxyz.bin"),
        q_file_name=path.join(folder, "combq.bin"),
        scalar_function_number=100, vector_function_number=200
    )
    plot3d.update()
    return plot3d


if __name__ == "__main__":
    plot3d = read_data()
    grid = plot3d.output.get_block(0)

    # 创建颜色映射表
    lut = tvtk.LookupTable()
    import pylab as pl

    lut.table = pl.cm.cool(np.arange(0, 256)) * 255

    # 显示StructuredGrid中的一个网格面
    plane = tvtk.StructuredGridGeometryFilter(extent=(0, 100, 0, 100, 6, 6))
    plane.set_input_data(grid)
    plane_mapper = tvtk.PolyDataMapper(input_connection=plane.output_port, lookup_table=lut)
    plane_mapper.scalar_range = grid.scalar_range
    plane_actor = tvtk.Actor(mapper=plane_mapper)

    cut_plane = tvtk.Plane(origin=grid.center, normal=(-0.287, 0, 0.9579))
    cut = tvtk.Cutter(cut_function=cut_plane)
    cut.set_input_data(grid)
    cut_mapper = tvtk.PolyDataMapper(lookup_table=lut, input_connection=cut.output_port)
    cut_actor = tvtk.Actor(mapper=cut_mapper)

    outline = tvtk.StructuredGridOutlineFilter()
    outline.set_input_data(grid)
    outline_mapper = tvtk.PolyDataMapper(input_connection=outline.output_port)
    outline_actor = tvtk.Actor(mapper=outline_mapper)
    outline_actor.property.color = 0.3, 0.3, 0.3

    from scpy2.tvtk.tvtkhelp import ivtk_scene

    win = ivtk_scene([plane_actor, cut_actor, outline_actor])
    win.scene.isometric_view()

    from pyface.api import GUI

    gui = GUI()
    gui.start_event_loop()