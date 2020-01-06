"""
Plot BSS and CRPS scores calculated by the Syd's stats scripts (written in R)

Note: only CRPS files contain sample counts

"""

import logging
import argparse
from pathlib import Path
from collections import OrderedDict
import pandas as pd
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from detiding_validation.config.default_params import station_dict
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SKIP_STATIONS = ["1430", ]
BSS_MARK = "bsss"
CRPS_MARK = "scores"
CRPS_INDEX = 1
BSS_INDEX = 2


STAT_TO_YLIM = {
    BSS_MARK: (0.4, 0.8),
    CRPS_MARK: (0, 0.2)
}

STID_PATTERN = re.compile(r"\d+.txt$")


def get_st_id(in_file: Path):
    """
    :param in_file:
    :return: station id or None if not found
    """
    m = re.search(STID_PATTERN, in_file.name)
    if m:
        return m.group()[:-4]
    return None


def read_files(data_paths, usecols, contains=BSS_MARK):
    """
    Read files from the disk
    :param data_paths:
    :param usecols:
    :param contains:
    :return:
    """
    result = OrderedDict()
    for label, folder in data_paths.items():
        result[label] = OrderedDict()
        for pth in folder.iterdir():

            if contains not in pth.name:
                continue

            st_id = get_st_id(pth)

            if st_id in SKIP_STATIONS:
                logger.info(f"Skipping {st_id} ... ")
                continue

            if st_id is None:
                continue

            cols = pd.read_csv(pth, header=None, sep=r"\s+", nrows=1).columns
            result[label][st_id] = pd.read_csv(pth, header=None, sep=r"\s+", usecols=[cols[use] for use in usecols])

    return result


def read_bss_files(data_paths: dict) -> dict:
    """
    :param data_paths:
    :return: {label: {stid: dataframe}}
    """
    return read_files(data_paths, usecols=(0, 1, 2, 3, 4))


def read_crps_files(data_paths: dict) -> dict:
    return read_files(data_paths, usecols=(0, 1, 2, 3, -1), contains=CRPS_MARK)


def plot_panel(ax, data, out_dir=None):
    """
    plot a subplot or a new figure if ax is None
    :param ax:
    :param data:
    :param out_dir:
    """
    pass


def plot_crps_bss(data: dict, data_colors: dict,
                  out_dir: Path,
                  stats="BSS", ycol=BSS_INDEX, cur_station_dict=None, lead_hour_max=240,
                  ylims=(0, 1)):
    ncols = 4

    logger.debug(f"data = {data}")

    station_ids = next(iter(data.items()))[1].keys()
    station_ids = list(station_ids)

    logger.debug(f"Plotting scores for {station_ids} ")

    nsubplots = len(station_ids)

    nrows = nsubplots // ncols + int(nsubplots % ncols != 0)

    fig = plt.figure(figsize=(20, 20))
    gs = GridSpec(nrows=nrows, ncols=ncols)

    stats_clean = stats.replace(" ", "")

    # fig.suptitle(stats)
    for i, st_id in enumerate(station_ids):
        r = i // ncols
        c = i % ncols
        ax = fig.add_subplot(gs[r, c])

        ax.set_title(cur_station_dict[st_id])

        for label, stid_to_vals in data.items():
            yvals = stid_to_vals[st_id].iloc[:, ycol]

            yvals_min = stid_to_vals[st_id].iloc[:, ycol + 1]
            yvals_max = stid_to_vals[st_id].iloc[:, ycol + 2]

            hours = stid_to_vals[st_id].iloc[:, 0].map(lambda t: int(t[:-1]))
            sel_hours = hours <= lead_hour_max

            xvals =  hours // 24 + 1

            ax.plot(xvals[sel_hours], yvals[sel_hours], label=label, c=data_colors[label], zorder=100)
            ax.fill_between(xvals[sel_hours], yvals_min[sel_hours], yvals_max[sel_hours], color=data_colors[label],
                            alpha=0.3)

            ax.xaxis.set_major_locator(MultipleLocator())
            # ax.set_ylim(ylims)
            ax.set_xlabel("Lead, days")

        if i == 0:
            ax.set_ylabel(stats)

        # add the legend
        if i == nsubplots - 1:
            ax.legend()

    fig.tight_layout()
    fig.savefig(out_dir / f"{stats_clean}_subplots.png", bbox_inches="tight")


    # plot all stations separately
    fig = plt.figure()
    ax = fig.gca()
    st_id = "all"

    ax.set_title(cur_station_dict[st_id])
    for label, stid_to_vals in data.items():
        yvals = stid_to_vals[st_id].iloc[:, ycol]

        hours = stid_to_vals[st_id].iloc[:, 0].map(lambda t: int(t[:-1]))
        xvals = hours // 24 + 1

        sel_hours = hours <= lead_hour_max

        yvals_min = stid_to_vals[st_id].iloc[:, ycol + 1]
        yvals_max = stid_to_vals[st_id].iloc[:, ycol + 2]

        ax.plot(xvals[sel_hours], yvals[sel_hours], label=label, c=data_colors[label], lw=2, zorder=100)
        ax.fill_between(xvals[sel_hours], yvals_min[sel_hours], yvals_max[sel_hours], color=data_colors[label],
                        alpha=0.3)
        ax.xaxis.set_major_locator(MultipleLocator())
        ax.set_ylim(ylims)

    ax.set_xlabel("Lead, days")
    ax.set_ylabel(stats)

    ax.legend()
    fig.savefig(out_dir / f"{stats_clean}_all_stations.png", bbox_inches="tight")



def main():
    """
    plot bss and crps scores produced by Syd's scripts

    call as
        python plot_bss_and_crps.py --paths <path1> <path2> ... <pathn> \
                                    --labels <label1> <label2> ... <labeln> \
                                  [ --out_dir ./ ]

    """

    parser = argparse.ArgumentParser("Plot CRPS and BSS computed by R scripts.")

    parser.add_argument("--paths", nargs="+",
                    help="space separated paths to the folders containing txt files with CRPS and BSS for each station")

    parser.add_argument("--labels",
                        help="labels of the corresponding paths",
                        nargs="+")

    parser.add_argument("--colors",
                        help="colors of the corresponding labels",
                        nargs="+")

    parser.add_argument("--out_dir", nargs="?", default="./",
                        help="Path to the folder, where to store plots",
                        required=False)


    parser.add_argument("--lead_hour_max", nargs="?", default=240,
                        help="Path to the folder, where to store plots",
                        required=False, type=int)



    args = parser.parse_args()
    # logger.debug(args)

    cur_station_dict = station_dict.copy()
    cur_station_dict.update({"all": "All stations"})

    data_paths = OrderedDict(list(zip(args.labels, [Path(p) for p in args.paths])))
    data_colors = OrderedDict(list(zip(args.labels, args.colors)))

    logger.debug([data_paths, data_colors])

    bss_data = read_bss_files(data_paths)
    crps_data = read_crps_files(data_paths)

    # add nsamples to the bss_data
    for label, stid_to_bss_vals in bss_data.items():
        stid_to_crps_vals = crps_data[label]

        for st_id, crps_vals in stid_to_crps_vals.items():
            stid_to_bss_vals[st_id].loc[:, "nsamples"] = crps_vals.iloc[:, -1]

    bss_thresh = None
    # compute all station means
    for label, stid_to_bss_vals in bss_data.items():
        bss_avg = None
        crps_avg = None

        total_samples = None

        stid_to_crps_vals = crps_data[label]
        for st_id, bss_vals in stid_to_bss_vals.items():
            crps_vals = stid_to_crps_vals[st_id]
            if bss_avg is None:
                bss_avg = bss_vals.copy()
                crps_avg = crps_vals.copy()

                bss_thresh = bss_vals.iloc[0, 1]

                # calculate mean limits as well, if available
                for di in [0, 1, 2]:
                    bss_avg.iloc[:, BSS_INDEX + di] = bss_vals.iloc[:, BSS_INDEX + di] * crps_vals.iloc[:, -1]
                    crps_avg.iloc[:, CRPS_INDEX + di] = crps_vals.iloc[:, CRPS_INDEX + di] * crps_vals.iloc[:, -1]

                total_samples = crps_vals.iloc[:, -1]
            else:

                # calculate mean limits as well, if available
                for di in [0, 1, 2]:
                    bss_avg.iloc[:, BSS_INDEX + di] += bss_vals.iloc[:, BSS_INDEX + di] * crps_vals.iloc[:, -1]
                    crps_avg.iloc[:, CRPS_INDEX + di] += crps_vals.iloc[:, CRPS_INDEX + di] * crps_vals.iloc[:, -1]

                total_samples += crps_vals.iloc[:, -1]

                # update the total number of samples
                bss_avg.iloc[:, -1] = total_samples
                crps_avg.iloc[:, -1] = total_samples


        # create a dummy station all
        stid_to_crps_vals["all"] = crps_avg
        stid_to_bss_vals["all"] = bss_avg

        # means for all stations
        # calculate mean limits as well, if available
        for di in [0, 1, 2]:
            stid_to_crps_vals["all"].iloc[:, CRPS_INDEX + di] = crps_avg.iloc[:, CRPS_INDEX + di] / total_samples
            stid_to_bss_vals["all"].iloc[:, BSS_INDEX + di] = bss_avg.iloc[:, BSS_INDEX + di] / total_samples


    # create the directory for output figures if it does not exist
    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True, parents=True)

    # do the plotting
    plot_crps_bss(bss_data, data_colors, out_dir=out_dir,
                  stats=f"BSS ({bss_thresh})", ycol=BSS_INDEX,
                  cur_station_dict=cur_station_dict, lead_hour_max=args.lead_hour_max,
                  ylims=STAT_TO_YLIM[BSS_MARK])

    plot_crps_bss(crps_data, data_colors, out_dir=out_dir,
                  stats=f"CRPS", ycol=CRPS_INDEX,
                  cur_station_dict=cur_station_dict, lead_hour_max=args.lead_hour_max,
                  ylims=STAT_TO_YLIM[CRPS_MARK])


if __name__ == '__main__':
    # plot_crps_bss()
    main()
