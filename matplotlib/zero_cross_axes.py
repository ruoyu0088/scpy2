def make_zerocross_axes(figsize, loc):
    from matplotlib import pyplot as plt
    from mpl_toolkits.axes_grid.axislines import SubplotZero


    fig = plt.figure(figsize=figsize)
    ax = SubplotZero(fig, loc)
    ax.set_aspect("equal")
    fig.add_subplot(ax)

    for direction in ["xzero", "yzero"]:
        axis = ax.axis[direction]
        axis.set_visible(True)

    for direction in ["left", "right", "bottom", "top"]:
        ax.axis[direction].set_visible(False)

    return ax