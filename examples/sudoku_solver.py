# -*- coding: utf-8 -*-
from itertools import combinations
import numpy as np
from matplotlib import pyplot as plt
from scpy2.cycosat import CoSAT


class SudokuSolver(object):
    
    def __init__(self):

        index = np.array(list(combinations(range(9), 2)))
        self.bools = bools = np.arange(1, 9*9*9+1).reshape(9, 9, 9)

        def get_conditions(bools):
            conditions = []
            conditions.extend( bools.reshape(-1, 9).tolist() ) 
            conditions.extend( (-bools[:,:,index].reshape(-1, 2)).tolist() ) 
            return conditions
            
        c1 = get_conditions(bools) 
        c2 = get_conditions( np.swapaxes(bools, 1, 2) ) 
        c3 = get_conditions( np.swapaxes(bools, 0, 2) ) 
        
        tmp = np.swapaxes(bools.reshape(3, 3, 3, 3, 9), 1, 2).reshape(9, 9, 9)
        c4 = get_conditions( np.swapaxes(tmp, 1, 2) )
        
        self.conditions = []
        for c in (c1, c2, c3, c4):
            self.conditions.extend(c)
            
    def solve(self, cells):
        sat = CoSAT()
        sat.add_clauses(self.conditions)
        assumes = [self.bools[r, c, v-1] for (r, c), v in cells.iteritems()]       
        solution = sat.assume_solve(assumes)
        if isinstance(solution, list):
            res = np.array(sat.solve())
            mask = (res > 0).reshape(9, 9, 9)
            return (np.where(mask)[2]+1).reshape(9, 9)
        else:
            return None
            

class SudokuBoard(object):
    
    def __init__(self):

        self.fig = plt.figure(figsize=(5, 5))
        self.fig.canvas.set_window_title(u'数独求解器')
        ax = self.fig.add_subplot(1, 1, 1)
        ax.set_aspect("equal")
        ax.set_axis_off()
        self.fig.subplots_adjust(0.0, 0.0, 1, 1)
        self.fig.patch.set_facecolor("white")
        
        for i in range(10):
            loc = 0.05 + i*0.1
            lw = 2 if i % 3 == 0 else 1
            color = "k" if lw > 1 else "#777777"
            line = plt.Line2D([0.05, 0.95], [loc, loc], 
                              transform=ax.transAxes, color=color, lw=lw)
            ax.add_artist(line)
            line = plt.Line2D([loc, loc], [0.05, 0.95], 
                              transform=ax.transAxes, color=color, lw=lw)
            ax.add_artist(line)
            
        self.cells = {}
        for col, row in np.broadcast(*np.ogrid[:9:1, :9:1]):
            x = 0.1 + col * 0.1
            y = 0.9 - row * 0.1
            text = plt.Text(x, y, "0", transform=ax.transAxes, 
                            va="center", ha="center", fontsize=16)
            ax.add_artist(text)
            self.cells[row, col] = text
            
        self.rect = plt.Rectangle((0.05, 0.05), 0.1, 0.1, 
                             transform=ax.transAxes, alpha=0.3)
        ax.add_artist(self.rect)            
            
        self.current_pos = (0, 0)
        self.set_current_cell((0, 0))
        self.setted_cells = {}
        self.solver = SudokuSolver()
        self.calc_solution()
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
            
    def set_current_cell(self, pos):
        row, col = pos
        self.rect.set_xy((0.05 + 0.1 * col, 0.85 - 0.1 * row))
        self.current_pos = pos
    
    def show(self):
        plt.show()
        
    def set_cell_text(self, pos, text, is_setted=True):
        text_obj = self.cells[pos]
        text_obj.set_text(text)
        if is_setted:
            text_obj.set_color("#000000")
        else:
            text_obj.set_color("#cccccc")
            
    def move_current_cell(self, direct):
        y, x = self.current_pos
        if direct == "up":
            y = (y - 1) % 9
        elif direct == "down":
            y = (y + 1) % 9
        elif direct == "left":
            x = (x - 1) % 9
        elif direct == "right":
            x = (x + 1) % 9
        elif direct == "next":
            x += 1
            if x == 9:
                x = 0
                y = (y + 1) % 9                   
        self.set_current_cell((y, x)) 
        
    def on_key(self, evt):
        if evt.key in ("up","down","left","right"):
            self.move_current_cell(evt.key)
        
        elif evt.key.isdigit():
            backup = self.setted_cells.copy()
            self.set_cell_text(self.current_pos, evt.key)
            if evt.key == u"0":
                try:
                    del self.setted_cells[self.current_pos]
                except KeyError:
                    pass
            else:
                self.setted_cells[self.current_pos] = int(evt.key)
            if not self.calc_solution():
                self.setted_cells = backup
                self.calc_solution()
            else:
                self.move_current_cell("next")

        elif evt.key == "ctrl+e":
            self.setted_cells.clear()
            self.calc_solution()
            
        self.fig.canvas.draw_idle()
        
    def calc_solution(self):
        solution = self.solver.solve(self.setted_cells)
        if solution is None:
            return False
        for pos, v in np.ndenumerate(solution):
            self.set_cell_text(pos, v, is_setted = pos in self.setted_cells)
        self.fig.canvas.draw_idle()
        return True
        
if __name__ == "__main__":
    board = SudokuBoard()
    board.show()