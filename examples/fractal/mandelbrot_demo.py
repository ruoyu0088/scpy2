# -*- coding: utf-8 -*-
import os
os.environ["QT_API"] = "pyqt"
from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'

import numpy as np
from traits.api import HasTraits, Instance, Float, Str, List, Int, on_trait_change
from traitsui.api import View, Group, Item, Controller, HGroup, VGroup, EnumEditor
from matplotlib.figure import Figure
from matplotlib import cm
from scpy2.traits.mpl_figure_editor import MPLFigureEditor
from .fastfractal import mandelbrot

SIZE = 500

class PlotController(Controller):
    
    def position(self, info):
        super(PlotController, self).position(info)
        self.model.init_plot()
        

class MandelbrotDemo(HasTraits):
    color_maps = List
    current_map = Str("Blues_r")
    loc_info = Str
    figure = Instance(Figure)
    N = Int(100)
    R = Float(10)
    cx = Float(0)
    cy = Float(0)
    d = Float(1.5)
    
    view = View(
        VGroup(
            HGroup(
                Item("current_map", label=u"Color map", 
                     editor=EnumEditor(name="object.color_maps")),
                "R", "N",
                show_labels = True
            ),
            Item("loc_info", show_label=False, style="readonly"),
            Group(
                Item("figure", editor=MPLFigureEditor(toolbar=False)),
                show_labels = False,
                orientation = 'horizontal'
            )
        ),
        width = SIZE,
        height = SIZE + 80,
        title = u"Mandelbrot Demo",
        resizable = True)
        
    def __init__(self, **kw):
        super(MandelbrotDemo, self).__init__(**kw)
        self.array = np.zeros((SIZE, SIZE))
        self.img = self.figure.figimage(self.array, cmap=self.current_map)
        
    def _figure_default(self):
        return Figure(figsize=(SIZE/100.0, SIZE/100.0), dpi=100)
        
    def _color_maps_default(self):
        return sorted(cm.cmap_d.keys())
        
    def init_plot(self):
        self.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.figure.canvas.mpl_connect('motion_notify_event', self.on_move)
        self.figure.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.update_plot()
        
    def _current_map_changed(self):
        self.img.set_cmap(self.current_map)
        self.update_plot()
        
    @on_trait_change("R, N")
    def update_plot(self):
        mandelbrot(self.cx, self.cy, self.d, out=self.array, n=self.N, R=self.R)
        self.loc_info = "%g, %g, d=%g" % (self.cx, self.cy, self.d)
        self.img.set_data(self.array)
        self.figure.canvas.draw()
        
    def on_press(self, evt):
        if evt.button == 1:
            self.last_pos = evt.x, evt.y, self.cx, self.cy
        
    def on_move(self, evt):
        if evt.button != 1:
            return
        
        x, y, cx, cy = self.last_pos
        dx = (x - evt.x) * 2 * self.d / SIZE
        dy = (evt.y - y) * 2 * self.d / SIZE
        self.cx = cx + dx
        self.cy = cy + dy
        self.update_plot()
    
    def on_scroll(self, evt):
        x0, x1, y0, y1 = self.cx-self.d, self.cx+self.d, self.cy-self.d, self.cy+self.d
        x = x0 + float(evt.x) / SIZE * 2 * self.d
        y = y0 + float(SIZE-evt.y) / SIZE * 2 * self.d
        
        if evt.step < 0:
            d2 = self.d * 1.2
        else:
            d2 = self.d / 1.2
            
        scale = d2 / self.d
        
        self.cx = (2 * x + (x0 + x1 - 2 * x) * scale) / 2
        self.cy = (2 * y + (y0 + y1 - 2 * y) * scale) / 2
        self.d = d2
        self.update_plot()

if __name__ == "__main__":
    demo = MandelbrotDemo()
    demo.configure_traits(handler=PlotController(demo))