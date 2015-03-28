# -*- coding: utf-8 -*-
from os import path
from glob import glob
import cv2
import numpy as np
from traits.api import HasTraits, Array, Bool, Instance, List, Str, Property, Any, Unicode
from traitsui.api import View, Item, HGroup, VGroup, Handler, EnumEditor
from pyface.timer.api import Timer
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from scpy2.traits import MPLFigureEditor, SettingManager, PositionHandler

FOLDER = path.dirname(__file__)
IMAGE_FOLDER = path.join(FOLDER, "images")
SETTING_FOLDER = path.join(FOLDER, "settings")


def get_images(exts):
    for ext in exts:
        pattern = path.join(IMAGE_FOLDER, "*." + ext)
        for fn in glob(pattern):
            yield path.basename(fn)


class ImageProcessDemo(HasTraits):
    YAXIS_DIRECTION = "down"
    DEFAULT_IMAGE = ""
    SIZE = 900, 600
    TITLE = u"Image Process Demo"
    SPLITTER = HGroup
    SETTINGS = []

    is_dirty = Bool(False)
    figure = Instance(Figure, ())
    axe = Instance(Axes)
    filenames = List
    current_filename = Str
    image_path = Property()
    img = Array

    settings = Instance(SettingManager)

    def default_traits_view(self):
        panel = self.control_panel()

        return View(
            self.SPLITTER(
                VGroup(
                    Item("current_filename", editor=EnumEditor(name="object.filenames")),
                    Item("settings", style="custom", defined_when="bool(object.SETTINGS)"),
                    panel,
                    show_labels=False
                ),
                Item("figure", editor=MPLFigureEditor(toolbar=True), show_label=False)
            ),
            resizable=True,
            title=self.TITLE,
            width=self.SIZE[0],
            height=self.SIZE[1],
            handler=PositionHandler()
        )

    def __init__(self, **kwargs):
        super(ImageProcessDemo, self).__init__(**kwargs)
        self.axe = self.figure.add_subplot(111)
        self.figure.subplots_adjust(0, 0, 1, 1)
        self.img = np.zeros((10, 10, 3), np.uint8)
        self.image_artist = self.axe.imshow(self.img, interpolation="nearest")
        self.axe.axis("off")
        self.axe.set_aspect("equal")
        self.settings = SettingManager(target=self)

    def init_timer(self):
        self.timer = Timer(100, self.check_dirty)

    def check_dirty(self):
        if self.is_dirty:
            self.draw()
            self.is_dirty = False

    def set_dirty(self):
        self.is_dirty = True

    def connect_dirty(self, traits):
        self.on_trait_change(self.set_dirty, traits)

    def control_panel(self):
        return VGroup()

    def _filenames_default(self):
        names = list(get_images(["png", "jpg"]))
        if self.DEFAULT_IMAGE not in names:
            self.current_filename = names[0]
        else:
            self.current_filename = self.DEFAULT_IMAGE
        return names

    def _get_image_path(self):
        return path.join(IMAGE_FOLDER, self.current_filename)

    def _current_filename_changed(self):
        self.load_image()
        self.draw()

    def load_image(self):
        self.img = cv2.imread(self.image_path)[:, :, ::-1].copy()

    def draw_image(self, img, artist=None, draw=True):
        if artist is None:
            artist = self.image_artist
        artist.set_data(img)
        h, w = img.shape[:2]
        if self.YAXIS_DIRECTION == "up":
            artist.set_extent([0, w, 0, h])
        else:
            artist.set_extent([0, w, h, 0])
        if self.figure.canvas and draw:
            self.figure.canvas.draw()

    def get_settings(self):
        setting = {}
        for attr in self.SETTINGS:
            value = getattr(self, attr)
            if isinstance(value, np.ndarray):
                value = value.tolist()
            setting[attr] = value
        return setting

    def load_settings(self, setting):
        for attr in self.SETTINGS:
            try:
                value = setting[attr]
            except KeyError:
                continue
            now_value = getattr(self, attr)
            if isinstance(now_value, np.ndarray):
                value = np.array(value)
            elif isinstance(now_value, tuple):
                value = tuple(value)
            setattr(self, attr, value)
        self.settings_loaded()

    def settings_loaded(self):
        pass

    def on_position(self):
        self.init_timer()
        if hasattr(self, "init_draw"):
            self.init_draw()
        self.draw()