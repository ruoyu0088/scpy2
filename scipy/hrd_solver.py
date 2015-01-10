# -*- coding: utf-8 -*-
from collections import deque
from itertools import chain, product
import matplotlib
matplotlib.use("Qt4Agg")
import pylab as pl
import numpy as np
from .hrd import find_path

SPEED = 5

W, H = 4, 5

BLOCKS = {
    "A": (0, 1, W, W+1),
    "B": (0, W),
    "C": (0, 1),
    "D": (0,)
}

SIZES = {
    "A": (2, 2),
    "B": (2, 1),
    "C": (1, 2),
    "D": (1, 1)
}


def status2positions(status):
    status = list(status)
    positions = []
    spaces = []
    for r in range(H):
        for c in range(W):
            idx = r * W + c
            block_type = status[idx]
            if block_type in BLOCKS:
                positions.append((block_type, r, c))
                for delta in BLOCKS[block_type]:
                    status[idx + delta] = ""
            elif block_type == " ":
                spaces.append((r, c))
    return positions, spaces


def interpolate_position(from_pos, to_pos, count):
    from_row, from_col = from_pos
    to_row, to_col = to_pos

    for i in range(count):
        k = float(i) / (count - 1)
        yield from_row * (1 - k) + to_row * k, from_col * (1 - k) + to_col * k


class HrdSolver(object):

    def __init__(self, status):
        self.fig, self.ax = pl.subplots(figsize=(4, 5))
        self.fig.canvas.set_window_title(u'华容道求解器')
        self.fig.patch.set_facecolor("white")
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        self.fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_move)
        self.init_rectangles(status)
        self.mode = "solve"
        self.pause = True
        self.current_block = None

    def init_rectangles(self, status):
        self.ax.clear()
        self.ax.axis((-0.1, 4.1, 5.1, -0.1))
        self.ax.axis("off")
        self.positions, self.spaces = status2positions(status)
        self.rectangles = {}
        for name, r, c in self.positions:
            h, w = SIZES[name]
            color = np.random.uniform(0.4, 0.8, 3)
            rect = pl.Rectangle((c, r), w, h, facecolor=color)
            self.ax.add_patch(rect)
            self.rectangles[r, c] = rect

        self.solution = list(find_path( status))
        self.solution.insert(0, status)
        self.current_index = 0

        self.move_queue = deque()
        self.timer = self.fig.canvas.new_timer(interval=25)
        self.timer.add_callback(self.on_timer)
        self.timer.start()

    def fill_move_queue(self, step=1):
        self.current_index += step
        self.current_index = max(min(self.current_index, len(self.solution)-1), 0)

        status = self.solution[self.current_index]
        positions, spaces = status2positions(status)
        set_prev = set(self.positions)
        set_next = set(positions)

        if set_prev == set_next:
            return

        from_pos = (set_prev - set_next).pop()[1:]
        to_pos = (set_next - set_prev).pop()[1:]

        rect = self.rectangles[from_pos]
        del self.rectangles[from_pos]
        self.rectangles[to_pos] = rect

        is_corner = from_pos[0] - to_pos[0] != 0 and from_pos[1] - to_pos[1] != 0
        if not is_corner:
            for pos in interpolate_position(from_pos, to_pos, SPEED):
                self.move_queue.append((rect, pos[::-1]))
        else:
            middle_positions = {(from_pos[0], to_pos[1]), (to_pos[0], from_pos[1])}
            target = (middle_positions & set(self.spaces)).pop()

            move_postions = chain(interpolate_position(from_pos, target, SPEED),
                                  interpolate_position(target, to_pos, SPEED))
            for pos in move_postions:
                self.move_queue.append((rect, pos[::-1]))

        self.positions, self.spaces = positions, spaces

    def on_timer(self):
        if self.mode != "solve":
            return

        if not self.move_queue:
            if not self.pause:
                self.fill_move_queue()

        if self.move_queue:
            rect, pos = self.move_queue.popleft()
            rect.set_xy(pos)
            self.fig.canvas.draw()

    def on_key(self, event):
        if event.key == " ":
            if self.mode == "solve":
                self.pause = not self.pause
            elif self.mode == "create":
                self.current_block.remove()
                self.current_block = None
                self.init_rectangles(self.get_status())
                self.pause = False
                self.mode = "solve"

        elif event.key == "right":
            self.fill_move_queue(step=1)
        elif event.key == "left":
            self.fill_move_queue(step=-1)
        elif event.key == "c":
            for rect in self.rectangles.itervalues():
                rect.remove()
            self.empty_pos = set(product(range(H), range(W)))
            self.rectangles.clear()
            self.fig.canvas.draw()
            self.mode = "create"
            self.set_current_block("A")
        elif self.mode == "create" and event.key in "1234":
            self.set_current_block("ABCD"[int(event.key)-1])

    def set_current_block(self, name):
        self.current_block_type = name
        h, w = SIZES[self.current_block_type]
        if self.current_block is not None:
            self.current_block.remove()
        self.current_block = pl.Rectangle((0, 0), w, h)
        self.ax.add_patch(self.current_block)
        self.current_block.set_visible(False)

    def get_blocks(self, x, y):
        h, w = SIZES[self.current_block_type]
        return {(y + dy, x + dx) for dy, dx in product(range(h), range(w))}

    def can_place_block(self, x, y):
        return self.get_blocks(x, y).issubset(self.empty_pos)

    def get_status(self):
        name_map = {v: k for k, v in SIZES.items()}
        board = [" "] * (W * H)
        for pos, rect in self.rectangles.iteritems():
            size = rect.get_height(), rect.get_width()
            idx = pos[0] * W + pos[1]
            name = name_map[size]
            for delta in BLOCKS[name]:
                board[idx + delta] = name
        return "".join(board)

    def add_block(self, x, y):
        blocks = self.get_blocks(x, y)
        self.empty_pos -= blocks
        h, w = SIZES[self.current_block_type]
        rect = pl.Rectangle((x, y), w, h, color=np.random.uniform(0.4, 0.8, 3))
        self.ax.add_patch(rect)
        self.rectangles[(y, x)] = rect
        self.fig.canvas.draw()

    def del_block(self, x, y):
        pos = (y, x)
        if pos in self.rectangles:
            rect = self.rectangles[pos]
            rect.remove()
            del self.rectangles[pos]
            self.fig.canvas.draw()
            blocks = self.get_blocks(x, y)
            self.empty_pos.update(blocks)

    def on_press(self, event):
        if self.mode != "create":
            return
        if event.inaxes is not self.ax:
            return

        x, y = int(event.xdata), int(event.ydata)

        if event.button == 1:
            if self.can_place_block(x, y):
                self.add_block(x, y)
        elif event.button == 3:
            self.del_block(x, y)

    def on_move(self, event):
        if self.mode != "create":
            return
        if event.inaxes is not self.ax:
            return

        x, y = int(event.xdata), int(event.ydata)
        if self.can_place_block(x, y):
            self.current_block.set_visible(True)
            self.current_block.set_xy((x, y))
        else:
            self.current_block.set_visible(False)
        self.fig.canvas.draw_idle()


if __name__ == '__main__':
    import sys
    try:
        board = sys.argv[1]
    except:
        board = "BAABBAABBCCBBDDBD  D"
    solver = HrdSolver(board)
    pl.show()