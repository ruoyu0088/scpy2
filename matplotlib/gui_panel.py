import math
import itertools
from collections import namedtuple

Info = namedtuple("info", "text,min,max,label,slider,value_label")
SliderResolution = 1000


class TkSliderPanel(object):
    def __init__(self, fig, parameters, callback, cols=1, min_value_width=None):
        import Tkinter as tk

        root = fig.canvas.manager.window
        panel = tk.Frame(root)

        panel.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        rows = int(math.ceil(len(parameters) / float(cols)))

        items = {}

        for i, (row, col) in enumerate(itertools.product(range(rows), range(cols))):
            if i == len(parameters):
                break
            text, vmin, vmax = parameters[i]
            label = tk.Label(panel, text=text)
            label.grid(row=row, column=col * 2)
            slider = tk.Scale(panel, from_=vmin, to=vmax, orient=tk.HORIZONTAL,
                              resolution=(vmax - vmin) / SliderResolution,
                              command=lambda val, key=text: self.on_value_changed(key, val))
            slider.grid(row=row, column=col * 2 + 1, sticky=tk.E + tk.W)

            item = Info(text, vmin, vmax, label, slider, None)
            items[text] = item

        for x in range(cols * 2):
            tk.Grid.columnconfigure(panel, x, weight=1)

        for y in range(rows):
            tk.Grid.rowconfigure(panel, y, weight=1)

        self.panel = panel
        self.callback = callback
        self.items = items
        self.values = {}

    def set_parameters(self, **kw):
        self.values.update(kw)
        for key, val in kw.items():
            self.items[key].slider.set(val)

    def on_value_changed(self, key, val):
        self.values[key] = float(val)
        if len(self.values) == len(self.items):
            self.callback(**self.values)


class QtSliderPanel(object):
    def __init__(self, fig, parameters, callback, cols=1, min_value_width=None):
        from PyQt4 import QtGui
        from PyQt4 import QtCore
        from PyQt4.QtCore import Qt

        root = fig.canvas.manager.window
        panel = QtGui.QWidget()
        grid = QtGui.QGridLayout()

        rows = int(math.ceil(len(parameters) / float(cols)))

        items = {}

        for i, (row, col) in enumerate(itertools.product(range(rows), range(cols))):
            if i == len(parameters):
                break
            text, vmin, vmax = parameters[i]
            label = QtGui.QLabel(text, parent=panel)
            grid.addWidget(label, row, col * 3)
            slider = QtGui.QSlider(parent=panel)
            slider.setMinimum(0)
            slider.setMaximum(SliderResolution)
            slider.setObjectName(text)
            slider.setOrientation(Qt.Horizontal)
            grid.addWidget(slider, row, col * 3 + 1)
            slider.valueChanged.connect(self.on_value_changed)
            value_label = QtGui.QLabel("test", parent=panel)
            if min_value_width is not None:
                value_label.setMinimumWidth(min_value_width)
            grid.addWidget(value_label, row, col * 3 + 2)

            items[text] = Info(text, vmin, vmax, label, slider, value_label)

        panel.setLayout(grid)
        dock = QtGui.QDockWidget("control", root)
        root.addDockWidget(Qt.BottomDockWidgetArea, dock)
        dock.setWidget(panel)

        self.panel = panel
        self.callback = callback
        self.items = items
        self.values = {}
        self._call_flag = True

    def set_parameters(self, **kw):
        self.values.update(kw)
        try:
            self._call_flag = False
            for key, val in kw.items():
                item = self.items[key]
                value = int((float(val) - item.min) / (item.max - item.min) * SliderResolution)
                item.value_label.setText("{:g}".format(value))
                item.slider.setValue(value)
        finally:
            self._call_flag = True
        self.callback(**self.values)

    def on_value_changed(self, val):
        from PyQt4 import QtCore

        slider = self.panel.sender()
        name = slider.objectName()
        item = self.items[name]
        val = item.min + (item.max - item.min) / float(SliderResolution) * val
        item.value_label.setText("{:g}".format(val))
        self.values[name] = val
        if self._call_flag:
            self.callback(**self.values)