# -*- coding: utf-8 -*-
"""
将matplotlib的绘图嵌入TraitsUI界面的控件
"""

###1###
import matplotlib
from traits.api import Bool
from traitsui.api import toolkit
from traitsui.basic_editor_factory import BasicEditorFactory
from traits.etsconfig.api import ETSConfig

if ETSConfig.toolkit == "wx":
    # matplotlib采用WXAgg为后台，这样才能将绘图控件嵌入以wx为后台界面库的traitsUI窗口中
    import wx
    matplotlib.use("WXAgg")
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
    from matplotlib.backends.backend_wx import NavigationToolbar2Wx as Toolbar
    from traitsui.wx.editor import Editor
    
elif ETSConfig.toolkit == "qt4":
    matplotlib.use("Qt4Agg")
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as Toolbar
    from traitsui.qt4.editor import Editor
    from pyface.qt import QtGui
###1###

class _WxFigureEditor(Editor): #{1}
    """
    相当于wx后台界面库中的编辑器，它负责创建真正的控件
    """
    scrollable = True

    def init(self, parent):
        self.control = self._create_canvas(parent)
        self.set_tooltip()

    def update_editor(self): #{2}
        pass

    def _create_canvas(self, parent): #{3}
        """
        创建一个Panel, 布局采用垂直排列的BoxSizer, panel中中添加
        FigureCanvas, NavigationToolbar2Wx, StaticText三个控件
        FigureCanvas的鼠标移动事件调用mousemoved函数，在StaticText
        显示鼠标所在的数据坐标
        """
        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        
        def mousemoved(event):           
            if event.xdata is not None:
                x, y = event.xdata, event.ydata
                name = "Axes"
            else:
                x, y = event.x, event.y
                name = "Figure"
                
            panel.info.SetLabel("%s: %g, %g" % (name, x, y))
            
        panel.mousemoved = mousemoved
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        mpl_control = FigureCanvas(panel, -1, self.value) #{4}
        if hasattr(self.value, "canvas_events"):
            for event_name, callback in self.value.canvas_events:
                mpl_control.mpl_connect(event_name, callback)
        mpl_control.mpl_connect("motion_notify_event", mousemoved)
        
        sizer.Add(mpl_control, 1, wx.LEFT | wx.TOP | wx.GROW)          

        if self.factory.toolbar:
            toolbar = Toolbar(mpl_control)
            sizer.Add(toolbar, 0, wx.EXPAND|wx.RIGHT)            

        panel.info = wx.StaticText(parent, -1)
        sizer.Add(panel.info)

        self.value.canvas.SetMinSize((10,10))
        return panel

###3###
class _QtFigureEditor(Editor):
    scrollable = True

    def init(self, parent): #❶
        self.control = self._create_canvas(parent)
        self.set_tooltip()

    def update_editor(self):
        pass

    def _create_canvas(self, parent):
        
        panel = QtGui.QWidget()
        
        def mousemoved(event):           
            if event.xdata is not None:
                x, y = event.xdata, event.ydata
                name = "Axes"
            else:
                x, y = event.x, event.y
                name = "Figure"
                
            panel.info.setText("%s: %g, %g" % (name, x, y))
            
        panel.mousemoved = mousemoved
        vbox = QtGui.QVBoxLayout()
        panel.setLayout(vbox)
        
        mpl_control = FigureCanvas(self.value) #❷
        vbox.addWidget(mpl_control)
        if hasattr(self.value, "canvas_events"):
            for event_name, callback in self.value.canvas_events:
                mpl_control.mpl_connect(event_name, callback)

        mpl_control.mpl_connect("motion_notify_event", mousemoved)  

        if self.factory.toolbar: #❸
            toolbar = Toolbar(mpl_control, panel)
            vbox.addWidget(toolbar)       

        panel.info = QtGui.QLabel(panel)
        vbox.addWidget(panel.info)
        return panel    
###3###

###4###
class MPLFigureEditor(BasicEditorFactory):
    """
    相当于traits.ui中的EditorFactory，它返回真正创建控件的类
    """    
    if ETSConfig.toolkit == "wx":
        klass = _WxFigureEditor
    elif ETSConfig.toolkit == "qt4":
        klass = _QtFigureEditor  #❶
        
    toolbar = Bool(True)  #❷
###4###

if __name__ == "__main__":
    from matplotlib.figure import Figure    
    from traits.api import HasTraits, Instance
    from traitsui.api import View, Item
    from numpy import sin, linspace, pi

    class TestMplFigureEditor(HasTraits):
        figure = Instance(Figure, ())
        view = View(
            Item("figure", editor=MPLFigureEditor(toolbar=True), show_label=False),
            width = 400,
            height = 300,
            resizable = True)

        def __init__(self):
            super(TestMplFigureEditor, self).__init__()
            self.figure.canvas_events = [
                ("button_press_event", self.figure_button_pressed)
            ]
            axes = self.figure.add_subplot(111)
            t = linspace(0, 2*pi, 200)
            axes.plot(sin(t))

        def figure_button_pressed(self, event):
            print event.xdata, event.ydata

    TestMplFigureEditor().configure_traits()
