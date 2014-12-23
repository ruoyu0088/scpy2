# -*- coding: utf-8 -*-
print "fonts"
import os
from os import path
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager

def show_chinese_fonts():
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    plt.subplots_adjust(0, 0, 1, 1, 0, 0)
    plt.xticks([])
    plt.yticks([])
    x, y = 0.05, 0.05
    fonts = [font.name for font in fontManager.ttflist if
                 path.exists(font.fname) and os.stat(font.fname).st_size>1e6] #❶
    font = set(fonts)
    dy = (1.0 - y) / (len(fonts) // 4 + (len(fonts)%4 != 0))

    for font in fonts:
        t = ax.text(x, y + dy / 2, u"中文字体",
                    {'fontname':font, 'fontsize':14}, transform=ax.transAxes) #❷
        ax.text(x, y, font, {'fontsize':12}, transform=ax.transAxes)
        x += 0.25
        if x >= 1.0:
            y += dy
            x = 0.05
    plt.show()

if __name__ == '__main__':
    show_chinese_fonts()