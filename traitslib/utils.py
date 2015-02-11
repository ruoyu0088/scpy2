# -*- coding: utf-8 -*-
import json
from os import path
from collections import OrderedDict
from traitsui.api import View, Item, HGroup, EnumEditor, Handler
from traitsui.menu import OKCancelButtons
from traits.api import HasTraits, Unicode, List, Any, Button, Instance


class PositionHandler(Handler):
    def position(self, info):
        super(PositionHandler, self).position(info)
        info.object.on_position()


class AskName(HasTraits):
    name = Unicode(u"")
    view = View(
        Item("name", label=u"名称"),
        kind="modal",
        buttons=OKCancelButtons
    )


class SettingManager(HasTraits):
    current_name = Unicode
    settings = Any
    names = List
    save_button = Button(u"保存设置")
    remove_button = Button(u"删除设置")
    target = Any

    view = View(
        HGroup(
            Item("current_name", editor=EnumEditor(name="object.names")),
            "save_button", "remove_button",
            show_labels=False
        )
    )

    def __init__(self, **kw):
        super(SettingManager, self).__init__(**kw)
        try:
            with open(self.setting_path(), "rb") as f:
                settings = json.load(f)
                self.settings = OrderedDict(settings)
        except IOError:
            self.settings = OrderedDict()
        self.names = self.settings.keys()

    def setting_path(self):
        import inspect

        klass = self.target.__class__
        folder = path.dirname(inspect.getabsfile(klass))
        filename = klass.__name__.lower() + ".json"
        setting_folder = path.join(folder, "settings")
        if path.exists(setting_folder):
            return path.join(setting_folder, filename)
        else:
            return path.join(folder, filename)

    def _save_button_fired(self):
        ask = AskName(name=self.current_name)
        if ask.configure_traits():
            setting = self.target.get_settings()
            self.settings[ask.name] = setting
            self.names = self.settings.keys()
            self.save_settings()
            self.current_name = ask.name

    def save_settings(self):
        with open(self.setting_path(), "wb") as f:
            json.dump(self.settings.items(), f)

    def _remove_button_fired(self):
        if self.current_name in self.settings:
            names = self.names
            index = names.index(self.current_name)
            del self.settings[self.current_name]
            self.names = self.settings.keys()
            if index >= len(self.settings):
                index = len(self.settings) - 1
            self.current_name = self.names[index]
            self.save_settings()

    def _current_name_changed(self):
        setting = self.settings[self.current_name]
        current_setting = self.target.get_settings()
        if setting != current_setting:
            self.target.load_settings(setting)

    def select_last(self):
        names = self.names
        if names:
            self.current_name = names[-1]


class SettingTest(HasTraits):
    x = Unicode
    y = Unicode
    settings = Instance(SettingManager)

    view = View(
        Item("settings", style="custom"),
        "x", "y"
    )

    def _settings_default(self):
        return SettingManager(target=self)

    def get_settings(self):
        return {"x": self.x, "y": self.y}

    def load_settings(self, setting):
        self.x = setting["x"]
        self.y = setting["y"]


if __name__ == '__main__':
    test = SettingTest()
    test.configure_traits()