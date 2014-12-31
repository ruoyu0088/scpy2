# -*- coding: utf-8 -*-
import numpy as np


def draw_grid(grid, size=6, margin=0.02, fontsize=16):
    from matplotlib import pyplot as plt
    cols = len(grid[0])
    rows = len(grid)
    aspect = rows / float(cols)
    fig, ax = plt.subplots(figsize=(6, 6*aspect))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_axis_off()
    fig.patch.set_facecolor("white")
    
    line_props = dict(transform=ax.transAxes, lw=1, color="#777777")
    
    width = (1-2*margin) / cols
    height = (1-2*margin) / rows

    for i in np.linspace(margin, 1-margin, rows+1):
        line = plt.Line2D([margin, 1-margin], [i, i], **line_props)
        ax.add_artist(line)
        
    for i in np.linspace(margin, 1-margin, cols+1):
        line = plt.Line2D([i, i], [margin, 1-margin], **line_props)
        ax.add_artist(line)
        
    for (r, c), v in np.ndenumerate(grid):
        text = plt.Text(margin + c*width + width*0.5, 
                        margin + (rows-r-1)*height + height*0.5, 
                        "%s" % v, transform=ax.transAxes, 
                        va="center", ha="center", fontsize=fontsize)
        ax.add_artist(text)
        
    fig.show()

if __name__ == "__main__":
    import numpy as np
    grid = np.random.randint(0, 10, (4, 6))
    print grid
    draw_grid(grid)    