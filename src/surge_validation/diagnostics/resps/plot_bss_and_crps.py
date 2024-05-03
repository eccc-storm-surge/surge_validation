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

from surge_validation.config.default_params import station_dict
import numpy as np
import re


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# SKIP_STATIONS = ["1430", "491"]
BSS_MARK = "bsss"
CRPS_MARK = "scores"
CRPS_INDEX = 1
BSS_INDEX = 2


STAT_TO_YLIM = {
    BSS_MARK: (None, None),
    CRPS_MARK: (None, None)
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


def read_files(data_paths, usecols, contains=BSS_MARK, skip_stations=()):
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

            if st_id in skip_stations:
                logger.info(f"Skipping {st_id} ... ")
                continue

            if st_id is None:
                continue

            cols = pd.read_csv(pth, header=None, sep=r"\s+", nrows=1).columns
            result[label][st_id] = pd.read_csv(pth, header=None, sep=r"\s+", usecols=[cols[use] for use in usecols])

    return result


def read_bss_files(data_paths: dict, skip_stations: list = ()) -> dict:
    """
    :param data_paths:
    :return: {label: {stid: dataframe}}
    """
    return read_files(data_paths, usecols=(0, 1, 2, 3, 4), 
                      skip_stations=skip_stations)


def read_crps_files(data_paths: dict, skip_stations: list = ()) -> dict:
    return read_files(data_paths, usecols=(0, 1, 2, 3, -1), 
                      contains=CRPS_MARK, 
                      skip_stations=skip_stations)


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
    ncols = 3

    plt.rcParams["font.size"] = 13

    fontweight = "semibold"
    plt.rcParams["font.weight"] = fontweight
    plt.rcParams["axes.titleweight"] = fontweight
    plt.rcParams["figure.titleweight"] = fontweight
    plt.rcParams["axes.labelweight"] = fontweight
    plt.rcParams["errorbar.capsize"] = 2

    logger.debug(f"data = {data}")

    station_ids = next(iter(data.items()))[1].keys()
    station_ids = list(station_ids)

    logger.debug(f"Plotting scores for {station_ids} ")

    nsubplots = len(station_ids)

    nrows = nsubplots // ncols + int(nsubplots % ncols != 0)

    fig = plt.figure(figsize=(5.5 * ncols, 3.5 * nrows))
    gs = GridSpec(nrows=nrows, ncols=ncols)

    stats_clean = "".join(list(c for c in stats if c.isalnum() or c in [".", "-"]))

    # fig.suptitle(stats)
    for i, st_id in enumerate(station_ids):
        r = i // ncols
        c = i % ncols
        ax = fig.add_subplot(gs[r, c])

        ax.set_title(cur_station_dict.get(st_id, st_id))

        for label, stid_to_vals in data.items():
            yvals = stid_to_vals[st_id].iloc[:, ycol]

            yvals_min = stid_to_vals[st_id].iloc[:, ycol + 1]
            yvals_max = stid_to_vals[st_id].iloc[:, ycol + 2]

            hours = stid_to_vals[st_id].iloc[:, 0].map(lambda t: int(t[:-1]))
            sel_hours = hours <= lead_hour_max

            xvals =  hours // 24 + 1

            ax.plot(xvals[sel_hours], yvals[sel_hours], label=label, c=data_colors[label], zorder=100)

            errors = [yvals[sel_hours] - yvals_min[sel_hours], yvals_max[sel_hours] - yvals[sel_hours]]
            ax.errorbar(xvals[sel_hours], yvals[sel_hours], yerr=np.array(errors), color=data_colors[label], lw=0.5)
            # ax.fill_between(xvals[sel_hours], yvals_min[sel_hours], yvals_max[sel_hours], color=data_colors[label],
            #                 alpha=0.3)

            ax.xaxis.set_major_locator(MultipleLocator())
            # ax.set_ylim(ylims)
            ax.set_xlabel("Lead, days")

        if i == 0:
            ax.set_ylabel(stats)

        # add the legend
        if i == nsubplots - 1:
            ax.legend()

    fig.tight_layout()
    fig.savefig(out_dir / f"{stats_clean}_subplots.pdf",
                bbox_inches="tight", transparent=True)


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

        ax.plot(xvals[sel_hours], yvals[sel_hours], label=label, c=data_colors[label], lw=1, zorder=100)
        errors = [yvals[sel_hours] - yvals_min[sel_hours], yvals_max[sel_hours] - yvals[sel_hours]]
        ax.errorbar(xvals[sel_hours], yvals[sel_hours], yerr=np.array(errors), color=data_colors[label], lw=0.5)


        # ax.fill_between(xvals[sel_hours], yvals_min[sel_hours], yvals_max[sel_hours], color=data_colors[label],
        #                 alpha=0.3)
        ax.xaxis.set_major_locator(MultipleLocator())
        ax.set_ylim(ylims)

    ax.set_xlabel("Lead, days")
    ax.set_ylabel(stats)

    ax.legend()
    fig.savefig(out_dir / f"{stats_clean}_all_stations.pdf",
                bbox_inches="tight", transparent=True)


def main():
    """
    plot bss and crps scores produced by Syd's scripts

    call as
        python plot_bss_and_crps.py --paths <path1> <path2> ... <pathn> \
                                    --labels <label1> <label2> ... <labeln> \
                                    --colors c1 c2 ... cn \
                                  [ --out_dir ./ ] [--bsslim min max] [--crpslim min max]

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

    parser.add_argument("--bsslim", nargs="+",
                        default=STAT_TO_YLIM[BSS_MARK],
                        required=False, type=float, help="y axis limits on the plot (BSS)")

    parser.add_argument("--crpslim", nargs="+", default=STAT_TO_YLIM[CRPS_MARK],
                        required=False, type=float, help="y axis limits on the plot (CRPS)")

    parser.add_argument("--skip-stations", nargs="+", 
                        required=False, default=[], 
                        help="list of station ids to skip")



    args = parser.parse_args()
    logger.debug(args)

    cur_station_dict = station_dict.copy()
    cur_station_dict.update({"all": "All stations"})

    data_paths = OrderedDict(list(zip(args.labels, [Path(p) for p in args.paths])))

    data_colors = OrderedDict(list(zip(args.labels, args.colors)))

    logger.debug([data_paths, data_colors])

    bss_data = read_bss_files(data_paths, skip_stations=args.skip_stations)
    crps_data = read_crps_files(data_paths, skip_stations=args.skip_stations)

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

        stid_to_crps_vals = crps_data[label]

        weights = {stid: df.iloc[:, -1] for stid, df in stid_to_crps_vals.items()}

        norms_for_lead = np.array([w for w in weights.values()]).sum(axis=0)

        print(label, norms_for_lead)

        for stid in weights:
            weights[stid] /= norms_for_lead

        

        for st_id, bss_vals in stid_to_bss_vals.items():
            crps_vals = stid_to_crps_vals[st_id]
            if bss_avg is None:
                bss_avg = bss_vals.copy()
                crps_avg = crps_vals.copy()

                bss_thresh = bss_vals.iloc[0, 1]

                # calculate mean limits as well, if available
                for di in [0, 1, 2]:
                    bss_avg.iloc[:, BSS_INDEX + di] = bss_vals.iloc[:, BSS_INDEX + di] * weights[stid]
                    crps_avg.iloc[:, CRPS_INDEX + di] = crps_vals.iloc[:, CRPS_INDEX + di] * weights[stid]

            else:

                # calculate mean limits as well, if available
                for di in [0, 1, 2]:
                    bss_avg.iloc[:, BSS_INDEX + di] += bss_vals.iloc[:, BSS_INDEX + di] * weights[stid]
                    crps_avg.iloc[:, CRPS_INDEX + di] += crps_vals.iloc[:, CRPS_INDEX + di] * weights[stid]


            # update the total number of samples / not really used?
            bss_avg.iloc[:, -1] = norms_for_lead
            crps_avg.iloc[:, -1] = norms_for_lead


        # create a dummy station all
        stid_to_crps_vals["all"] = crps_avg
        stid_to_bss_vals["all"] = bss_avg
        print(crps_avg.iloc[0, CRPS_INDEX])
        
        for stid in weights:
            print(weights[stid][0], stid, stid_to_crps_vals[stid].iloc[0, CRPS_INDEX], stid_to_crps_vals[stid].iloc[0, -1], norms_for_lead[0])
        

    # create the directory for output figures if it does not exist
    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True, parents=True)

    # do the plotting
    plot_crps_bss(bss_data, data_colors, out_dir=out_dir,
                  stats=f"BSS ({bss_thresh})", ycol=BSS_INDEX,
                  cur_station_dict=cur_station_dict,
                  lead_hour_max=args.lead_hour_max,
                  ylims=args.bsslim)

    plot_crps_bss(crps_data, data_colors, out_dir=out_dir,
                  stats=f"CRPS", ycol=CRPS_INDEX,
                  cur_station_dict=cur_station_dict,
                  lead_hour_max=args.lead_hour_max,
                  ylims=args.crpslim)


if __name__ == '__main__':
    # plot_crps_bss()
    main()
