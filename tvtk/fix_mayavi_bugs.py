"""
fix Contours don't update when `auto contours` is checked
fix cut plane doesn't update when the plane is changed
"""


def _do_auto_contours(self):
    if not self._has_input():
        return
    if self.auto_contours:
        minc, maxc = self.minimum_contour, self.maximum_contour
        self.contour_filter.generate_values(self.number_of_contours,
                                            min(minc, maxc),
                                            max(minc, maxc))
        self.contour_filter.update()
        self.data_changed = True


def _cut_function_changed(self):
    self.cutter.cut_function.on_trait_change(self.cutter.update, "normal, origin")


def _mask_input_points_changed(self, value):
    from tvtk.common import configure_input
    inputs = self.inputs
    if len(inputs) == 0:
        return
    if value:
        mask = self.mask_points
        configure_input(mask, inputs[0].outputs[0])
        self.configure_connection(self.glyph, mask)
    else:
        self.configure_connection(self.glyph, inputs[0])


def fix_mayavi_bugs():
    from mayavi.components.contour import Contour
    Contour._do_auto_contours = _do_auto_contours

    from mayavi.components.cutter import Cutter
    from traits.trait_notifiers import StaticTraitChangeNotifyWrapper
    Cutter._cut_function_changed = _cut_function_changed
    Cutter.__class_traits__["cut_function"]._notifiers(1).append(
        StaticTraitChangeNotifyWrapper(_cut_function_changed))

    from mayavi.components.glyph import Glyph
    Glyph._mask_input_points_changed.im_func.func_code = _mask_input_points_changed.func_code