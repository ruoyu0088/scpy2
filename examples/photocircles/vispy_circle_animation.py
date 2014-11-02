from glob import glob
from os import path
from itertools import cycle
from vispy import gloo
from vispy import app
import numpy as np


VERT_SHADER = """

uniform float blend;
uniform float view_size;

attribute vec2  a_position;
attribute float a_size;
attribute vec3  a_color;

attribute vec2  a_position2;
attribute float a_size2;
attribute vec3  a_color2;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;

void main (void) {

    v_radius = (a_size * (1.0 - blend) + a_size2 * blend) * view_size;
    v_fg_color  = vec4(0.0, 0.0, 0.0, 0.5);
    v_bg_color  = vec4(a_color, 1.0) * (1 - blend) + vec4(a_color2, 1.0) * blend;

    gl_Position = vec4(a_position, 0, 1.0) * (1 - blend) + vec4(a_position2, 0, 1.0) * blend;
    gl_PointSize = 2.0*v_radius + 2;
}
"""

FRAG_SHADER = """
#version 120

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;
void main()
{

    float size = 2.0*v_radius + 2;
    float r = length((gl_PointCoord.xy - vec2(0.5,0.5))*size);
    if(r < v_radius)
        gl_FragColor = v_bg_color;
    else if(r < v_radius + 1)
    {
        gl_FragColor = vec4(v_bg_color[0], v_bg_color[1], v_bg_color[2], (v_radius + 1 - r) * 0.5);
    }
    else
        gl_FragColor = vec4(0, 0, 0, 0);
}
"""


def load_circles():
    photo_circles = []

    circle_dtype = [("position", np.float32, 2),
                    ("size", np.float32),
                    ("color", np.float32, 3)]

    for fn in glob(path.join(path.dirname(__file__), "*.csv")):
        data = np.loadtxt(fn, delimiter=",")
        circles = np.zeros(len(data), dtype=circle_dtype)
        circles["position"] = data[:, :2] / 256.0 - 1
        circles["size"] = data[:, 2] / 512.0 * 1.01
        circles["color"] = data[:, 3:] / 256.0
        circles["position"][:, 1] *= -1
        photo_circles.append(circles)

    photos = cycle(photo_circles)
    return photos


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(400, 400))
        self.photos = load_circles()

    def set_data(self, circles1, circles2):
        self.program['a_color'] = circles1["color"].copy()
        self.program['a_position'] = circles1["position"].copy()
        self.program['a_size'] = circles1["size"].copy()

        self.program['a_color2'] = circles2["color"].copy()
        self.program['a_position2'] = circles2["position"].copy()
        self.program['a_size2'] = circles2["size"].copy()

    def on_initialize(self, event):
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)

        self.circles1 = next(self.photos)
        self.circles2 = next(self.photos)
        self.set_data(self.circles1, self.circles2)

        self.blend = 0.01
        self.target_blend = 1.0
        self.program['blend'] = self.blend
        self.count = 0

        gloo.set_state(clear_color='white', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

    def on_timer(self, event):
        step = min((self.blend * 0.96 + self.target_blend * 0.04) - self.blend, 0.02)
        self.blend += step

        if self.blend > 0.999 or self.blend < 0.001:
            self.blend = self.target_blend
            self.count += 1
        if self.count == 100:
            self.count = 0
            self.blend = 0.0
            self.circles1, self.circles2 = self.circles2, next(self.photos)
            self.set_data(self.circles1, self.circles2)
        self.program['blend'] = self.blend
        self.update()

    def on_resize(self, event):
        w, h = event.size
        s = min(w, h)
        gloo.set_viewport(0, 0, s, s)
        self.program['view_size'] = s

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw('points')


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()