# -*- coding: utf-8 -*-
from .select_compiler import show_compiler, set_msvc_version, set_compiler


def tabulate_it(rows, cols, func, label_fmt=u"**{}**", row_label=True):
    from tabulate import tabulate
    result = []

    fmt = label_fmt.format

    for row in rows:
        res_row = [fmt(row)] if row_label else []
        result.append(res_row)
        for col in cols:
            res_row.append(func(row, col))
    return tabulate(result, [fmt(col) for col in cols], "pipe")