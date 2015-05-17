# -*- coding: utf-8 -*-
import os
from os import path
import numpy as np
from tvtk.api import tvtk
from scpy2.tvtk.tvtkhelp import make_outline

make_outline
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

    import pylab as pl

    lut = tvtk.LookupTable()
    lut.table = pl.cm.cool(np.arange(0, 256)) * 255

    # 显示StructuredGrid中的一个网格面
    plane = tvtk.StructuredGridGeometryFilter(extent=(0, 100, 0, 100, 6, 6))
    plane.set_input_data(grid)
    plane_mapper = tvtk.PolyDataMapper(input_connection=plane.output_port, lookup_table=lut)
    plane_mapper.scalar_range = grid.scalar_range
    plane_actor = tvtk.Actor(mapper=plane_mapper)

    lut2 = tvtk.LookupTable()
    lut2.table = pl.cm.cool(np.arange(0, 256)) * 255

    cut_plane = tvtk.Plane(origin=grid.center, normal=(-0.287, 0, 0.9579))
    cut = tvtk.Cutter(cut_function=cut_plane)
    cut.set_input_data(grid)
    cut_mapper = tvtk.PolyDataMapper(lookup_table=lut2, input_connection=cut.output_port)
    cut_actor = tvtk.Actor(mapper=cut_mapper)

    outline_actor = make_outline(grid)

    from scpy2.tvtk.tvtkhelp import ivtk_scene, event_loop

    win = ivtk_scene([plane_actor, cut_actor, outline_actor])
    win.scene.isometric_view()
    event_loop()