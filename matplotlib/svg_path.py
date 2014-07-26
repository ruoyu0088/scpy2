# -*- coding: utf-8 -*-
import re
from xml.etree.ElementTree import iterparse
from matplotlib.path import Path
from matplotlib.patches import PathPatch

codemap = {"M": Path.LINETO, "C": Path.CURVE4,
           "Z": Path.CLOSEPOLY, "L": Path.LINETO}


def get_number(s):
    return int(re.search(r"\d+", s).group())


def make_path(d, style):
    items = []
    for c in d.split():
        if c.upper() in codemap:
            items.append(c)
        else:
            x, y = (float(v) for v in c.split(","))
            items.append((x, y))
    codes = []
    vertices = []
    i = 0
    lx, ly = 0, 0
    last_code = "M"
    while i < len(items):
        code = items[i]
        if not isinstance(code, str):
            code = last_code
        else:
            i += 1
        ucode = code.upper()
        if code.isupper():
            relative = False
        else:
            relative = True
        if ucode in ("M", "L"):
            x, y = items[i]
            i += 1
            if relative:
                x += lx
                y += ly
            codes.append(codemap[ucode])
            vertices.append((x, y))
            lx, ly = x, y
        if ucode == "C":
            if not relative:
                points = items[i:i + 3]
            else:
                points = [(_x + lx, _y + ly) for _x, _y in items[i:i + 3]]
            codes.extend([codemap[ucode]] * 3)
            vertices.extend(points)
            lx, ly = points[-1]
            i += 3
        if ucode == "Z":
            break
        last_code = code

    codes[0] = Path.MOVETO
    patch = PathPatch(Path(vertices, codes))
    patch.set_linewidth(get_number(style.get("stroke-width", "1px")))
    fill = style.get("fill", "none")
    if fill == "none":
        patch.set_fill(None)
    else:
        patch.set_facecolor(fill)
    edge = style.get("stroke", "none")
    patch.set_edgecolor(edge)

    return patch


def read_svg_path(fn):
    patches = []
    for _, element in iterparse(fn):
        tag = re.split("}", element.tag)[-1].lower()
        if tag == "path":
            d = element.attrib["d"]
            style = {k: v for (k, v) in (item.split(":")
                                         for item in element.attrib["style"].split(";"))}
            patches.append(make_path(d, style))
    return patches