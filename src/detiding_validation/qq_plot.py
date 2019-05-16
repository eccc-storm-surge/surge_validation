import logging
from collections import OrderedDict
from pathlib import Path

import matplotlib
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from detiding_validation import io_manager
from detiding_validation.config import default_params
import numpy as np
import matplotlib.pyplot as plt


import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_plot(station_id, label_to_color: dict, label_to_data: dict,
                label_to_line_props: dict,
                label_to_handle: dict,
                station_dict: dict,
                lead_h_min=-np.inf, lead_h_max=np.inf,
                add_legend=False,
                ax=None):
    """

    :param lead_h_max:
    :param lead_h_min:
    :param label_to_handle:
    :param label_to_line_props:
    :param station_dict:
    :param add_legend:
    :param station_id: station id
    :param label_to_data: {label: {station_id: data}}
    :param label_to_color: {label: color}
    :param ax: axes to do the plotting, if ax=None a new figure is created

    """

    fig = None
    if ax is None:
        fig = plt.figure(figsize=(8, 6))
        ax = fig.gca()

    lead_t_text = f", [{lead_h_min}h, {lead_h_max}h]"

    if station_id == "all":
        title = f"All stations{lead_t_text}"
    else:
        title = f"{station_dict[station_id]} ({station_id}){lead_t_text}"

    print(list(label_to_data.keys()))

    for label, color in label_to_color.items():

        data_for_station = label_to_data[label]

        for vh, data in data_for_station.groupby(io_manager.VALIDH_COL_NAME):

            if not (lead_h_min <= vh <= lead_h_max):
                continue

            ax.axis("equal")
            ax.plot(data["obs"].sort_values().values, data["mod"].sort_values().values,
                    **label_to_line_props[label])

    ax.grid(True, linewidth=0.3, linestyle="dashed")
    ax.text(0.5, 1.05, title, va="bottom", ha="center", transform=ax.transAxes)

    ax.set_xlabel("obs (m)")
    ax.set_ylabel("mod (m)")

    if add_legend:
        labels = []
        handles = []
        for lab, han in label_to_handle.items():
            labels.append(lab)
            handles.append(han)

        ax.legend(handles, labels, loc="lower left", bbox_to_anchor=(1.1, 0), borderaxespad=0)

    the_min, the_max = ax.get_xlim()
    the_min = min(ax.get_ylim()[0], the_min)
    the_max = max(ax.get_ylim()[1], the_max)

    ax.plot([the_min, the_max], [the_min, the_max], "k--", linewidth=0.6)

    ax.set_ylim(the_min, the_max)
    ax.set_xlim(the_min, the_max)

    ax.yaxis.set_major_locator(ax.xaxis.get_major_locator())

    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    return fig


def qqplot(label_to_dataframe: dict,
           label_to_color: dict,
           station_dict: dict = default_params.station_dict,
           plot_params=None, n_subplot_cols=4,
           img_dir: Path = None,
           label_to_display_label=None, lead_h_min=0, lead_h_max=243):
    """
    :param n_subplot_cols:
    :param lead_h_max:
    :param lead_h_min:
    :param label_to_display_label:
    :param img_dir:
    :param plot_params:
    :param label_to_color:
    :param label_to_dataframe: label and corresponding dataframe containing model and obs for each experiment
    :param station_dict: subset of stations to consider
    """

    logging.getLogger().setLevel(logging.INFO)
    dpi = 300

    qq_plot_dir = img_dir / "qq"
    qq_plot_dir.mkdir(exist_ok=True, parents=True)

    if label_to_display_label is None:
        label_to_display_label = {lab: lab for lab in label_to_dataframe.keys()}

    logging.debug(label_to_display_label)

    if plot_params is not None:
        matplotlib.rcParams.update(plot_params)

    # do the plotting
    fig = plt.figure()

    _station_dict = station_dict.copy()
    _station_dict["all"] = "All stations"

    label_to_line_props = {
        label: dict(color=color, lw=0.5, marker="o", linestyle="none", fillstyle="none",
                    markersize=3, markeredgewidth=0.3, label=label) for label, color in label_to_color.items()
    }
    label_to_handle = {
        label: Line2D([0], [0], **label_to_line_props[label]) for label, color in label_to_color.items()
    }

    # put the data into a convenient structure
    station_id_to_label_to_data = {}
    for station_id in _station_dict:

        station_id_to_label_to_data[station_id] = {}

        for label, df in label_to_dataframe.items():

            if station_id not in ["all", "All"]:
                select_data = df[df[io_manager.STID_COL_NAME] == station_id]
            else:
                select_data = df

            # print(len(select_data), station_id, label)

            station_id_to_label_to_data[station_id].update({label: select_data})

    n_subplots = len(station_id_to_label_to_data)
    n_subplot_rows = n_subplots // n_subplot_cols

    if n_subplot_cols * n_subplot_rows < n_subplots:
        n_subplot_rows += 1

    gs = GridSpec(n_subplot_rows, n_subplot_cols, hspace=0.4, wspace=0.3)

    for subplot_index, station_id in enumerate(station_id_to_label_to_data):

        r, c = subplot_index // n_subplot_cols, subplot_index % n_subplot_cols

        ax = fig.add_subplot(gs[r, c])

        logger.debug(station_id)

        # subplot panel
        create_plot(station_id, label_to_color=label_to_color,
                    label_to_data=station_id_to_label_to_data[station_id],
                    label_to_line_props=label_to_line_props,
                    label_to_handle=label_to_handle,
                    station_dict=_station_dict,
                    lead_h_min=lead_h_min, lead_h_max=lead_h_max,
                    add_legend=subplot_index == n_subplots - 1, ax=ax)

        # separate image
        # plot a separate image only for all stations (for performance and space saving)
        if station_id == "all":
            sep_figure = create_plot(station_id, label_to_color=label_to_color,
                                     label_to_data=station_id_to_label_to_data[station_id],
                                     label_to_line_props=label_to_line_props,
                                     label_to_handle=label_to_handle,
                                     station_dict=_station_dict,
                                     lead_h_min=lead_h_min, lead_h_max=lead_h_max,
                                     add_legend=True, ax=None)

            # save and close separate figures
            qq_plot_dir_for_station = qq_plot_dir / station_id
            qq_plot_dir_for_station.mkdir(exist_ok=True, parents=True)

            img_per_station = qq_plot_dir_for_station / f"qq_plot_{station_id}_leadt_from_{lead_h_min}_to_{lead_h_max}.png"
            sep_figure.savefig(img_per_station, dpi=dpi, bbox_inches="tight")
            plt.close(sep_figure)

        ax.yaxis.get_label().set_visible(c == 0)
        ax.xaxis.get_label().set_visible(subplot_index >= n_subplots - n_subplot_cols)

    fig.align_ylabels()

    fig.savefig(qq_plot_dir / f"qq_plot_leadt_from_{lead_h_min}h_to_{lead_h_max}h.png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    logging.getLogger().info(f"Finished plotting qq plots for lead times {lead_h_min}h to {lead_h_max}h!")
    logging.getLogger().setLevel(logging.INFO)
