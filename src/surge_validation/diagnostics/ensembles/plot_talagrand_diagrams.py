from collections import OrderedDict
from concurrent.futures import as_completed
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MaxNLocator

from surge_validation import io_manager
from surge_validation.config import default_params
from surge_validation.misc.scheduling import get_process_pool_executor
from surge_validation.utils import log_utils
from surge_validation.utils.io_utils import cleanup
from surge_validation.utils.strutils import stname_to_fname2
from resample.bootstrap import confidence_interval
import pandas as pd
from functools import partial


def ranks_to_probability(ranks: pd.DataFrame, bins, data_colname=io_manager.OBS_COL_NAME):
    """Convert ranks to probabilities"""

    
    # left limit inclusive and the right excluded i.e [lead1, lead2)
    
    probability, bin_edges = np.histogram(ranks[data_colname], density=True, bins=bins)

    return probability


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
    :param ci_limits dictionary containing confidence interval limits {"min": {}, "max": {}}, the
           dicts corresponding to the min and max keys have the same layout as rank_data: {syslabel: dataframe}
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

        for lbl, probability in rank_data[lead_pair].items():

            

            ax.plot(range(1, nbins), probability[io_manager.OBS_COL_NAME], "o", label=lbl, c=lbl_to_color[lbl],
                    markersize=plot_params["marker_size"], alpha=plot_params["alpha"])

            # plot error bars
            if "ci_min" in probability.columns:

                p_min = probability["ci_min"]
                p_max = probability["ci_max"]

                assert ((p_min <= probability) & (probability <= p_max)).all()

                yerr = np.array([probability - p_min, p_max - probability])

                logger.info("p_min=%s\nprob=%s\np_max=%s\n", p_min, probability, p_max)
                ax.errorbar(range(1, nbins), probability, yerr=yerr, c=lbl_to_color[lbl], alpha=plot_params["alpha"])
                

        if i == 0:
            ax.legend(title=plot_params.get("legend_title", ""), loc="upper center")

    fig.tight_layout()
    return fig




def prob_calc(s, rank_method="first", bins=None, bin_index=0):
    ranks = pd.DataFrame(s).rank(method=rank_method, axis=1).values
    return np.histogram(ranks, density=True, bins=bins)[0][bin_index]


def calculate_rank_ci(s, nbootstrap=100, conf_level=0.9, ci_method="bca", bins=None, rank_method="first"):
    
    result = []
    for bin_index, bin in enumerate(bins):
        __prob_calc = partial(prob_calc, bins=bins, rank_method=rank_method, bin_index=bin_index)

        result.append(
            confidence_interval(__prob_calc, s, size=nbootstrap, ci_method=ci_method, cl=conf_level, bin_index=bin_index)
        )

    return result
    


def plot_ranks(lbl_to_data: dict, lbl_to_color: dict,
               leads=None,
               stid_to_name: dict = None,
               plot_params: dict = None,
               img_dir: Path = None,
               alpha_ci=0.1,
               nbootstrap=100,
               rank_method="first"):
    """
    :param img_dir: directory to store plots
    :param lbl_to_data: label to model data (model data in the form of a dataframe)
    :param lbl_to_color:
    :param leads:
    :param stid_to_name:
    :return:
    """

    logger = log_utils.get_logger(__name__)




    ppool = get_process_pool_executor()

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

    nbins = len(col_names)
    bins = np.arange(0.5, nbins + 1.5, 1.)
    logger.debug("\nbins=%s\nlen(bins)=%s", bins, len(bins))



    def __create_data_container():
        dc = OrderedDict()
        for lead_pair in leads:
            dc[lead_pair] = {stid: OrderedDict() for stid in stid_list}
            dc.update({"all": OrderedDict()})

        return dc

    # calculate ranks
    stid_to_lbl_to_data = __create_data_container()
   

    from tqdm import tqdm
                
    
    nbootstrap = 10

    for lead_pair in leads:

        for lbl, data in lbl_to_data.items():

            logger.debug(data.head())

            # select lead hours
            vh = data[io_manager.VALIDH_COL_NAME]
            data = data.loc[(vh >= lead_pair[0]) & (vh < lead_pair[1]), :]

            df = pd.DataFrame()
            df[io_manager.OBS_COL_NAME] = [prob_calc(data[col_names].values, bins=bins, bin_index=i) for i in range(len(bins))]
            df["ci_min"] = np.nan
            df["ci_max"] = np.nan

            if nbootstrap > 0:

                logger.info( "Data summary: \n%s\n",
                    data[col_names].describe()
                )

                ci = calculate_rank_ci(data[col_names].values,
                                    nbootstrap=nbootstrap, conf_level=1 - alpha_ci, ci_method="bca", bins=bins 
                )

                # progress bar   
                ci = list(tqdm(ci,  total=len(df)))

                logger.info(f"len ci 1 = {len(ci)}")
                ci = list(zip(*ci))
                logger.info(f"len ci 2 = {len(ci)}")


                df["ci_min"] = ci[0]
                df["ci_max"] = ci[1]
            
                    


            df[io_manager.VALIDH_COL_NAME] = data[io_manager.VALIDH_COL_NAME]
            df[io_manager.STID_COL_NAME] = data[io_manager.STID_COL_NAME]

            for stid, rank in df.groupby(io_manager.STID_COL_NAME):
                logger.debug("\n %s \n", rank.head())
                stid_to_lbl_to_data[lead_pair][stid][lbl] = rank[[io_manager.OBS_COL_NAME, io_manager.VALIDH_COL_NAME, "ci_min", "ci_max"]]

            stid_to_lbl_to_data[lead_pair]["all"][lbl] = df[[io_manager.OBS_COL_NAME, io_manager.VALIDH_COL_NAME, "ci_min", "ci_max"]]

            logger.info(f"Processed {lbl} ...")

    # nbins = number of members + 1
   
    future_to_stid = {}
    for stid in stid_to_lbl_to_data:
        rank_data = stid_to_lbl_to_data[stid]
        fut = ppool.submit(plot_ranks_for_station,
                           _stid_to_name[stid], bins, leads, rank_data, lbl_to_color, plot_params)
        future_to_stid[fut] = stid

    for a_future in as_completed(future_to_stid):
        stid = future_to_stid[a_future]
        fig = a_future.result()
        img = img_dir / f"{stid}_{stname_to_fname2(_stid_to_name[stid])}.png"
        fig.savefig(img, bbox_inches="tight", transparent=True)
        plt.close(fig)
