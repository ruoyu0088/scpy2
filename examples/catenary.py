# -*- coding: utf-8 -*-
from traits.api import HasTraits, Float, Int, Property, Instance, Range
from traitsui.api import View, Item, Controller, Group
import numpy as np
from scipy import integrate
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

from scpy2.traits.mpl_figure_editor import MPLFigureEditor


class Catenary(HasTraits):
    
    N = Int(31)
    dump = Range(0.0, 0.5, 0.1)
    k = Range(1.0, 100.0, 20.0)
    length = Range(1.0, 3.0, 1.0)
    g = Range(0.0, 0.1, 0.01)
    t = Float(0.0)
    x = Property()
    y = Property()
    
    def __init__(self, *args, **kw):
        super(Catenary, self).__init__(*args, **kw)
        
        x0 = np.linspace(0, 1, self.N)
        y0 = np.zeros_like(x0)
        vx0 = np.zeros_like(x0)
        vy0 = np.zeros_like(x0)
        
        self.status0 = np.r_[x0, y0, vx0, vy0]
        
    def diff_status(self, t, status):
        x, y, vx, vy = status.reshape(4, -1)
        dvx = np.zeros_like(x)
        dvy = np.zeros_like(x)
        dx = vx
        dy = vy
        
        s = np.s_[1:-1]
        
        l = self.length / (self.N - 1)
        k = self.k
        g = self.g
        dump = self.dump
        
        l1 = np.sqrt((x[s] - x[:-2])**2 + (y[s] - y[:-2])**2)
        l2 = np.sqrt((x[s] - x[2:])**2 + (y[s] - y[2:])**2)
        dl1 = (l1 - l) / l1
        dl2 = (l2 - l) / l2
        dvx[s] = - (x[s] - x[:-2]) * k * dl1 - (x[s] - x[2:]) * k * dl2
        dvy[s] = - (y[s] - y[:-2]) * k * dl1 - (y[s] - y[2:]) * k * dl2 + g
        dvx[s] -= vx[s] * dump
        dvy[s] -= vy[s] * dump
        return np.r_[dx, dy, dvx, dvy]        
        
    def ode_init(self):
        self.t = 0
        self.system = integrate.ode(self.diff_status)
        self.system.set_integrator("vode", method="bdf")
        self.system.set_initial_value(self.status0, 0)
        self.status = self.status0
        
    def ode_step(self, dt):
        self.system.integrate(self.t + dt)
        self.t = self.system.t
        self.status = self.system.y
        
    def _get_x(self):
        return self.status[:self.N]
        
    def _get_y(self):
        return self.status[self.N:self.N*2]


class TimerController(Controller):
    
    def position(self, info):
        super(TimerController, self).position(info)
        self.model.start_timer()
        
    def close(self, info, is_ok):
        super(TimerController, self).close(info, is_ok)
        self.model.stop_timer()
        return True
        
        
class AnimationGui(HasTraits):
    
    figure = Instance(Figure, ())
    system = Instance(Catenary, ())

    view = View(
        Group(
            Group(
                Item("object.system.g"),
                Item("object.system.length"),
                Item("object.system.k"),
                Item("object.system.dump"),
            ),
            Item("figure", editor=MPLFigureEditor(toolbar=True)),
            show_labels = False,
            orientation = 'horizontal'
        ),
        width = 800,
        height = 600,
        resizable = True)
        
    def __init__(self, **kw):
        super(AnimationGui, self).__init__(**kw)
        self.axe = self.figure.add_subplot(111)
        
    def start_timer(self):
        self.system.ode_init()
        self.line, = self.axe.plot(self.system.x, -self.system.y, 
                                       "-o", animated=True)
        self.axe.set_xlim(-0.1, 1.1)
        self.axe.set_ylim(-1, 0.1)
        self.ani = FuncAnimation(self.figure, self.update_figure, 
                                 blit=True, interval=20)
                                 
    def stop_timer(self):
        self.ani._stop()
        
    def update_figure(self, frame):
        self.system.ode_step(0.2)
        self.line.set_data(self.system.x, -self.system.y)
        return self.line,


def test_catenary():
    system = Catenary()
    system.ode_init()
    for i in range(1000):
        system.ode_step()
    import pylab as pl
    pl.plot(system.x, -system.y)    
    
if __name__ == "__main__":
    ani = AnimationGui()
    ani.configure_traits(handler=TimerController(ani))   
