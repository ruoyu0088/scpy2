from vispy import gloo
from vispy import app
import numpy as np

VERT_SHADER = """
attribute vec3  a_position;

void main (void) {
    gl_Position = vec4(1.0, 0, 0, 1);
    gl_PointSize = 100;
}
"""

FRAG_SHADER = """
void main() {
    gl_FragColor = vec4(0, 0, 0, 1);
}
"""

class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')

    def on_initialize(self, event):
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program["a_position"] = np.zeros((10, 3))
        gloo.set_state(clear_color='white', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

    def on_resize(self, event):
        w, h = event.size
        s = min(w, h)
        gloo.set_viewport(0, 0, s, s)

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw('points')


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()