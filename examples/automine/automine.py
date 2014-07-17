# -*- coding: utf-8 -*-
from os import path
from collections import defaultdict
from itertools import combinations
import random
import time

import numpy as np
from PIL import ImageGrab, Image
from scipy.spatial import distance

from scpy2.utils import autoit as auto
from scpy2.cycosat import CoSAT

FOLDER = path.dirname(__file__)

IMG_INIT = path.join(FOLDER, "mine_init.png")
IMG_NUMBERS = path.join(FOLDER, "mine_numbers.png")

MINE_PATH = ur"c:\Program Files\Microsoft Games\Minesweeper\MineSweeper.exe"
WIN_TITLE = u"扫雷"
MINE_COUNT = 99

X0, Y0, SIZE, COLS, ROWS = 30, 30, 18, 30, 16
SHAPE = ROWS, SIZE, COLS, SIZE, -1

mine_area = np.s_[Y0:Y0+SIZE*ROWS, X0:X0+SIZE*COLS, :]

def imread(fn):
    img = Image.open(fn)
    return np.asarray(img)

img_init = imread(IMG_INIT)[mine_area].copy()
img_numbers = imread(IMG_NUMBERS) 

def run_minesweeper():
    auto.run(MINE_PATH)
    auto.win_wait(WIN_TITLE)
    auto.win_set_on_top(WIN_TITLE, 1)

def get_client_rect():
    import win32gui    
    handle = auto.control_get_handle(WIN_TITLE, u"Static1")
    rect = win32gui.GetWindowRect(handle)
    return rect

def capture_image():
    rect = get_client_rect()
    img = ImageGrab.grab(rect)
    return np.asarray(img)[mine_area]
    
def capture_board():
    img_mine = capture_image()
    mask = (img_init != img_mine).reshape(SHAPE)
    block_mask = np.mean(mask, axis=(1, 3, 4)) > 0.3
    img_mine2 = np.swapaxes(img_mine.reshape(SHAPE), 1, 2)
    
    blocks = img_mine2[block_mask][:, 3:-3, 3:-3, :].copy()
    if blocks.shape[0] == 0:
        return [], [], []
    blocks = blocks.reshape(blocks.shape[0], -1)
    
    img_numbers.shape = 8, -1
    numbers = np.argmin(distance.cdist(blocks, img_numbers), axis=1)
    rows, cols = np.where(block_mask)
    return rows, cols, numbers

def restart():
    if not auto.win_active(WIN_TITLE):
        auto.win_activate(WIN_TITLE)
    auto.send(u"{F2}")
    time.sleep(0.1)
    auto.send(u"n")   

def click(row, col):
    left, top, _, _ = get_client_rect()
    x = col * SIZE + X0 + SIZE // 2 + left
    y = row * SIZE + Y0 + SIZE // 2 + top
    if not auto.win_active(WIN_TITLE):
        auto.win_activate(WIN_TITLE)
    auto.mouse_move(x, y, 1)
    auto.send(u"{SPACE}")
    

class AutoMine(object):
    
    def __init__(self):
        self.mines = set()
        self.opened = set()
        self.make_neighbors()

    def make_neighbors(self):
        variable_neighbors = defaultdict(list)
        
        directs = [(-1, -1), (-1,  0), (-1,  1), (0, -1), 
                   ( 0,  1), ( 1, -1), ( 1,  0), (1,  1)]
        
        variables = np.arange(1, COLS*ROWS+1).reshape(ROWS, COLS)
        
        for (i, j), v in np.ndenumerate(variables):
            for di, dj in directs:
                i2 = i + di
                j2 = j + dj
                if 0 <= i2 < ROWS and 0 <= j2 < COLS:
                    variable_neighbors[v].append(variables[i2, j2])
                    
        self.variable_neighbors = variable_neighbors
        self.variables = variables
            
    def get_clauses(self, var_id, num):
        clauses = []
        neighbors = self.variable_neighbors[var_id]
        neg_neighbors = [-x for x in neighbors]
        clauses.extend(combinations(neg_neighbors, num + 1))
        clauses.extend(combinations(neighbors, len(neighbors) - num + 1))
        clauses.append([-var_id])
        return clauses

    def solve_step(self):
        rows, cols, numbers = capture_board()
        sat = CoSAT()
        vars_index = self.variables[rows, cols]
        self.opened = set(vars_index)
        for idx, num in zip(vars_index, numbers):
            sat.add_clauses(self.get_clauses(idx, num))
            
        failed_assumes = sat.get_failed_assumes()
        vars_set = set(vars_index)
        to_click = []
        self.mines.clear()
        for v in failed_assumes:
            if v > 0 and v not in vars_set:
                to_click.append(v)
            if v < 0:
                self.mines.add(-v)
        return to_click
        
    def solve_action(self):
        toclick = self.solve_step()
        for idx in toclick:
            self.click(idx)
        if toclick:
            time.sleep(0.3)
            if auto.win_exists(u"游戏胜利"):
                return "WIN"
        return bool(toclick)
        
    def random_click(self):
        print "random_click"
        blocks = set(range(1, COLS*ROWS+1))
        blocks -= set(self.opened)
        blocks -= set(self.mines)
        blocks = list(blocks)
        idx = random.choice(blocks)
        self.click(idx)
        time.sleep(0.5)
        if auto.win_exists(u"游戏失败"):
            return False 
        return True
        
    def click(self, idx):
        tmp = idx - 1
        col, row = tmp % COLS, tmp // COLS
        click(row, col)


def main():
    run_minesweeper()
    time.sleep(2.0)
    automine = AutoMine()
    while True:
        res = automine.solve_action()
        
        if len(automine.mines) == MINE_COUNT:
            break
        
        if res == "WIN":
            break
        if res == False:
            res = automine.random_click()
            if not res:
                break    
    
if __name__ == "__main__":
    main()