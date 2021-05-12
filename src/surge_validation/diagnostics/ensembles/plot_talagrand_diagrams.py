from collections import OrderedDict
from concurrent.futures import as_completed
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MaxNLocator

from surge_validation.detiding_validation import io_manager
from surge_validation.detiding_validation.config import default_params
from surge_validation.misc.scheduling import get_thread_pool_executor, get_process_pool_executor
from surge_validation.utils import log_utils
from surge_validation.utils.io_utils import cleanup
from surge_validation.utils.strutils import stname_to_fname2


def plot_ranks_for_station(stname, bins, leads, rank_data, lbl_to_color: dict, plot_params: dict = None):
    """
    Make a panel with subplots for each lead interval, each subplot containing rank plots for
    different runs
    :param stname: Human readable station name
    :param bins:
    :param leads:
    :param rank_data:
    :param lbl_to_color:
    :param plot_params:
    :return: figure object
    """
    logger = log_utils.get_logger(__name__)
    if plot_params is None:
        plot_params = dict(marker_size=2, alpha=0.7)

    ncols = 2
    nrows = len(leads) // 2 + int(len(leads) % ncols != 0)

    fig = plt.figure(figsize=(ncols * 5.5, nrows * 4), dpi=96)
    gs = GridSpec(nrows, ncols)

    nbins = len(bins)

    for i, lead_pair in enumerate(leads):

        lead_label = f"Day {lead_pair[1] // 24}"

        row = i // ncols
        col = i % ncols
        ax = fig.add_subplot(gs[row, col])
        ax.set_ylabel("frequency")
        ax.set_xlabel("bins")

        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title(f"{stname}: {lead_label}")

        ax.hlines(1. / nbins, 1, nbins, color="magenta", lw=2)

        for lbl, ranks in rank_data.items():

            # left limit inclusive and the right excluded i.e [lead1, lead2)
            vh = ranks[io_manager.VALIDH_COL_NAME]
            current_lead_ranks = ranks[(vh >= lead_pair[0]) & (vh < lead_pair[1])]

            probability, bin_edges = np.histogram(current_lead_ranks, density=True, bins=bins)

            ax.plot(range(1, nbins), probability, "o", label=lbl, c=lbl_to_color[lbl],
                    markersize=plot_params["marker_size"], alpha=plot_params["alpha"])

        if i == 0:
            ax.legend(title=plot_params.get("legend_title", ""), loc="upper center")

    fig.tight_layout()
    return fig


def plot_ranks(lbl_to_data: dict, lbl_to_color: dict,
               leads=None,
               stid_to_name: dict = None,
               plot_params: dict = None,
               img_dir: Path = None):
    """
    :param img_dir: directory to store plots
    :param lbl_to_data: label to model data (model data in the form of a dataframe)
    :param lbl_to_color:
    :param leads:
    :param stid_to_name:
    :return:
    """

    logger = log_utils.get_logger(__name__)

    if stid_to_name is None:
        _stid_to_name = default_params.get_station_dict()
    else:
        _stid_to_name = stid_to_name.copy()

    _stid_to_name["all"] = "All stations"

    img_dir.mkdir(exist_ok=True, parents=True)
    cleanup.cleanup_out_dir(img_dir)

    if leads is None:
        leads = [(0, 24), (48, 72), (96, 120), (144, 168)]

    if plot_params is None:
        plot_params = dict(
            alpha=0.7, marker_size=8
        )

    # select only relevant columns
    col_names = []
    stid_list = None
    for lbl, data in lbl_to_data.items():
        col_names.extend(sorted([cn for cn in data.columns if cn.startswith("mod")]))
        stid_list = list(data[io_manager.STID_COL_NAME].drop_duplicates().values)
        break

    col_names = [io_manager.OBS_COL_NAME] + col_names

    # calculate ranks
    stid_to_lbl_to_data = {stid: OrderedDict() for stid in stid_list}
    stid_to_lbl_to_data["all"] = OrderedDict()
    for lbl, data in lbl_to_data.items():
        logger.debug(data.head())
        df = pd.DataFrame()
        df[io_manager.OBS_COL_NAME] = data[col_names].rank(axis=1, method="first")[io_manager.OBS_COL_NAME]
        df[io_manager.VALIDH_COL_NAME] = data[io_manager.VALIDH_COL_NAME]
        df[io_manager.STID_COL_NAME] = data[io_manager.STID_COL_NAME]

        for stid, rank in df.groupby(io_manager.STID_COL_NAME):
            logger.debug("\n %s \n", rank.head())
            stid_to_lbl_to_data[stid][lbl] = rank[[io_manager.OBS_COL_NAME, io_manager.VALIDH_COL_NAME]]

        stid_to_lbl_to_data["all"][lbl] = df[[io_manager.OBS_COL_NAME, io_manager.VALIDH_COL_NAME]]

    # nbins = number of members + 1
    nbins = len(col_names)
    bins = np.arange(0.5, nbins + 1.5, 1.)
    logger.debug("\nbins=%s\nlen(bins)=%s", bins, len(bins))

    future_to_stid = {}
    ppool = get_process_pool_executor()
    for stid in stid_to_lbl_to_data:
        rank_data = stid_to_lbl_to_data[stid]
        fut = ppool.submit(plot_ranks_for_station,
                           _stid_to_name[stid], bins, leads, rank_data, lbl_to_color, plot_params)
        future_to_stid[fut] = stid

    for a_future in as_completed(future_to_stid):
        stid = future_to_stid[a_future]
        fig = a_future.result()
        img = img_dir / f"{stid}_{stname_to_fname2(_stid_to_name[stid])}.pdf"
        fig.savefig(img, bbox_inches="tight", transparent=True)
        plt.close(fig)
