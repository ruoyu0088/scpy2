import pylab as pl
import numpy as np


def plot_dataframe_as_colormesh(df, ax=None, inverse_yaxis=False, colorbar=False, xtick_rot=0,
                   xtick_start=0, xtick_step=1, ytick_start=0, ytick_step=1,
                   xtick_format=None, ytick_format=None,
                   **kw):
    nrow, ncol = df.shape
    if ax is None:
        fig_width = 10.0
        fig_height = fig_width / ncol * nrow
        fig, ax = pl.subplots(figsize=(fig_width, fig_height))

    ax.set_aspect("equal")
    if inverse_yaxis:
        ax.invert_yaxis()
    mesh = ax.pcolormesh(df.values, **kw)
    if colorbar:
        pl.colorbar(ax=ax, mappable=mesh)

    xticks_loc = np.arange(xtick_start, ncol, xtick_step)
    yticks_loc = np.arange(ytick_start, nrow, ytick_step)

    xlabels = df.columns.tolist()
    if xtick_format is not None:
        xlabels = [xtick_format(label) for label in xlabels]
    ylabels = df.index.tolist()
    if ytick_format is not None:
        ylabels = [ytick_format(label) for label in ylabels]

    ax.set_xticks(xticks_loc + 0.5)
    ax.set_xticklabels([xlabels[idx] for idx in xticks_loc], rotation=xtick_rot)
    ax.set_yticks(yticks_loc + 0.5)
    ax.set_yticklabels([ylabels[idx] for idx in yticks_loc])
    return ax