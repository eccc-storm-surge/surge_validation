from matplotlib.axes import Axes
from matplotlib.transforms import Bbox
import matplotlib as mpl


def full_extent(ax, pad=0.0):
    """Get the full extent of an axes, including axes labels, tick labels, and
    titles."""
    # For text objects, we need to draw the figure first, otherwise the extents
    # are undefined.
    assert isinstance(ax, Axes)

    # ax.figure.canvas.draw()

    fig = ax.figure
    items = [ax.title, ] + [c for c in ax.get_children() if isinstance(c, mpl.legend.Legend)]
    # items = [c for c in ax.get_children() if isinstance(c, mpl.legend.Legend)]
    bbox = Bbox.union([item.get_window_extent().transformed(fig.dpi_scale_trans.inverted()) for item in items])

    return bbox.expanded(1.0 + pad, 1.0 + pad)