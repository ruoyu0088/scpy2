# -*- coding: utf-8 -*-
from math import pi
from traits.api import HasTraits, Int, Str, Instance, Enum, on_trait_change
from traitsui.api import View, Item, VGroup, HGroup, InstanceEditor, VSplit


class Point(HasTraits):
    x = Int
    y = Int
    view = View(HGroup(Item("x"), Item("y")))

###1###
class Shape(HasTraits):
    info = Str
    view_info = View(Item("info", style="custom", show_label=False))

    def __init__(self, **traits):
        super(Shape, self).__init__(**traits)
        self.set_info() 
###1###


class Triangle(Shape):
    a = Instance(Point, ())
    b = Instance(Point, ())
    c = Instance(Point, ())
    
    view = View(
        VGroup(
            Item("a", style="custom"),
            Item("b", style="custom"),
            Item("c", style="custom"),
        )
    )
    
    @on_trait_change("a.[x,y],b.[x,y],c.[x,y]")
    def set_info(self):
        a,b,c = self.a, self.b, self.c
        l1 = ((a.x-b.x)**2+(a.y-b.y)**2)**0.5
        l2 = ((c.x-b.x)**2+(c.y-b.y)**2)**0.5
        l3 = ((a.x-c.x)**2+(a.y-c.y)**2)**0.5
        self.info = "edge length: %f, %f, %f" % (l1,l2,l3)
    
class Circle(Shape):
    center = Instance(Point, ())
    r = Int
    
    view = View(
        VGroup(
            Item("center", style="custom"), 
            Item("r"),
        )
    )
    
    @on_trait_change("r")
    def set_info(self):
        self.info = "area:%f" % (pi*self.r**2)


class ShapeSelector(HasTraits):
    select = Enum(*[cls.__name__ for cls in Shape.__subclasses__()]) 
    shape = Instance(Shape) 
###2### 
    view = View(
        VGroup(
            Item("select", show_label=False),
            VSplit( #❶
                Item("shape", style="custom", editor=InstanceEditor(view="view")), #❷
                Item("shape", style="custom", editor=InstanceEditor(view="view_info")), 
                show_labels = False
            )

        ),
        width = 350, height = 300, resizable = True
    )
###2###
    def __init__(self, **traits):
        super(ShapeSelector, self).__init__(**traits)
        self._select_changed()
    
    def _select_changed(self):
        klass =  [c for c in Shape.__subclasses__() if c.__name__ == self.select][0]
        self.shape = klass()
        
if __name__ == "__main__":
    demo = ShapeSelector()
    demo.configure_traits()