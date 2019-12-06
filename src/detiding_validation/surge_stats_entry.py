import logging
from collections import OrderedDict
from pathlib import Path

import matplotlib
# matplotlib.use('agg')

from detiding_validation.config import default_params
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MultipleLocator, NullLocator

from detiding_validation import io_manager
from detiding_validation.plot_utils import full_extent
from detiding_validation.qq_plot import qqplot
from detiding_validation.verification_stats.calc_stats_with_obs import stde, gamma, stde_obs, gamma_varobsallvhour
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test():
    station_dict = default_params.station_dict

    swl_path_old = "/fs/home/fs1/eccc/cmd/cmde/olh001/MATLAB/detide/data/SSM_from_Natacha/SSM/RESPS/prep_for_ensemble_R_verif/surge_ensemble_jf2017.dat"
    swl = io_manager.read_wl_station_data(swl_path_old, station_dict=station_dict)

    print(swl.head())

    per_station_stde, overall_stde = stde(swl)
    per_station_gamma, overall_gamma = gamma(swl)

    print(per_station_stde.head())

    subplots = False

    per_station_stde.xs(2985, level="station_id").plot(subplots=subplots,
                                                       y=io_manager.get_model_column_names(swl, suffix="_stde"))
    # per_station_stde.xs(365, level="station_id").plot(subplots=subplots, y=io_manager.get_model_column_names(swl, suffix="_stde"))
    overall_stde.plot(subplots=subplots, y=io_manager.get_model_column_names(swl, suffix="_stde"))

    per_station_gamma.xs(2985, level="station_id").plot(subplots=subplots,
                                                        y=io_manager.get_model_column_names(swl, suffix="_gamma"))
    # per_station_gamma.xs(365, level="station_id").plot(subplots=subplots, y=io_manager.get_model_column_names(swl, suffix="_gamma"))
    overall_gamma.plot(subplots=subplots, y=io_manager.get_model_column_names(swl, suffix="_gamma"))

    plt.show()


def plot_index_to_row_col(i, ncols):
    row = i // ncols
    col = i % ncols
    return row, col


def style_axes(ax, locator_base=24):
    ax.xaxis.set_major_locator(MultipleLocator(base=locator_base))
    ax.grid(True, linestyle="--", linewidth=0.2)
    ax.set_xlabel("forecast hour")
    ax.xaxis.set_minor_locator(NullLocator())
    ax.tick_params(axis="x", which="minor", bottom=False)


def plot_scores(ax, old_series, new_series, col_name, shared_ax=None,
                title="", labels=None, show_avg_diff=True):
    """
    Plot scores as function of forcast hour
    :param show_avg_diff: True/False whether show or not the average difference between the models
    :param labels: dict of new and old labels {"old": "...", "new": "..."}
    :param ax:
    :param old_series:
    :param new_series:
    :param col_name:
    :param shared_ax:
    :param title:
    """

    if labels is None:
        labels = {
            "old": "", "new": ""
        }

    old_series.plot(y=col_name, legend=False, color=default_params.COLOR_OLD, lw=0.5,
                    ax=ax,
                    title=title, sharex=shared_ax,
                    sharey=None,
                    rot=45, label=labels["old"])

    if labels["new"] != labels["old"]:

        new_series.plot(y=col_name, legend=False, color=default_params.COLOR_NEW, lw=0.5,
                        ax=ax,
                        sharex=shared_ax, sharey=None,
                        rot=45, label=labels["new"])

        # display averaged difference for all forecast hours if requested
        if show_avg_diff:
            ax.text(0.99, 0.99, f"<new-old>$_t$: {(new_series - old_series)[col_name].mean():.4f}",
                    transform=ax.transAxes, ha="right", va="top")
    else:
        logger.info(f"Labels are the same, plotting just 1 line")

    return ax


def compare_2_simulations(swl_path_old, swl_path_new, img_dir,
                          station_dict=default_params.station_dict,
                          label_old="RDSPS, operational",
                          label_new="RDSPS, parallel", member_id="",
                          forecast_hour_tick_multiplier=24,
                          select_stations=None, n_subplot_cols=4, custom_rc_params=None,
                          color_old="b", color_new="r", show_avg_diff=True,
                          qq_lead_hour_range=range(244), max_lead_hour=None):
    logging.info("Start compare_2_simulations ...")
    if custom_rc_params is None:
        custom_rc_params = {}

    img_dir.mkdir(exist_ok=True, parents=True)

    # read the data into memory
    swl_old = io_manager.read_wl_station_data(swl_path_old, station_dict=station_dict, max_lead_hour=max_lead_hour)
    swl_new = io_manager.read_wl_station_data(swl_path_new, station_dict=station_dict, max_lead_hour=max_lead_hour)

    # set font size
    if custom_rc_params is None:
        matplotlib.rcParams.update({'font.size': 5})
    else:
        matplotlib.rcParams.update(custom_rc_params)

    # TODO: add a flag to be able to disable qqplots
    label_to_data = OrderedDict([(label_old, swl_old), (label_new, swl_new)])
    label_to_color = OrderedDict([(label_old, color_old), (label_new, color_new)])

    logger.debug(list(label_to_data.keys()))

    for lead in qq_lead_hour_range:
        qqplot(
            label_to_dataframe=label_to_data, label_to_color=label_to_color,
            station_dict=station_dict, plot_params=custom_rc_params, n_subplot_cols=n_subplot_cols,
            img_dir=img_dir,
            lead_h_min=lead, lead_h_max=lead
        )

    if not img_dir.exists():
        img_dir.mkdir(parents=True, exist_ok=True)

    statname_to_disp = {
        "stde": r"$\sigma_{\varepsilon}$ (m)",
        "gamma": r"$\gamma^2$",
        "stde_obs": r"$\sigma_{Obs}$ (m)",
        "gamma_varobsallvhour": r"$\gamma^2_{adj}$"
    }

    if member_id is None or len(member_id) == 0:
        member_id = 0

    stids_not_overall = default_params.ignore_in_overall
    xlims = None
    all_axes_except_last = []

    for suffix in ["_stde", "_gamma", "_stde_obs", "_gamma_varobsallvhour"]:
        col_names = io_manager.get_model_column_names(swl_old, suffix=suffix)

        if suffix == "_gamma":
            swl_stats_old = gamma(swl_old, stids_not_overall=stids_not_overall)
            swl_stats_new = gamma(swl_new, stids_not_overall=stids_not_overall)
        elif suffix == "_stde_obs":
            swl_stats_old = stde_obs(swl_old, stids_not_overall=stids_not_overall)
            swl_stats_new = stde_obs(swl_new, stids_not_overall=stids_not_overall)
        elif suffix == "_gamma_varobsallvhour":
            swl_stats_old = gamma_varobsallvhour(swl_old, stids_not_overall=stids_not_overall)
            swl_stats_new = gamma_varobsallvhour(swl_new, stids_not_overall=stids_not_overall)
        else:
            swl_stats_old = stde(swl_old, stids_not_overall=stids_not_overall)
            swl_stats_new = stde(swl_new, stids_not_overall=stids_not_overall)

        current_station_ids = swl_stats_old[0].index.get_level_values("station_id").unique()
        # determine number of rows in the panel plot
        if select_stations is None:
            nsubplots = 1 + len(current_station_ids)
        else:
            nsubplots = 1 + len([cid for cid in current_station_ids if cid in select_stations])

        nrows = nsubplots // n_subplot_cols + int(nsubplots % n_subplot_cols != 0)

        fig = plt.figure(figsize=custom_rc_params.get("figure.figsize", (9, 12)))
        gs = GridSpec(nrows, n_subplot_cols, top=0.90)
        shared_ax = None

        logger.debug(current_station_ids)
        logger.debug("number of stations to process = {}".format(len(current_station_ids)))
        logger.debug(f"Subplots: nrows={nrows}, ncols={n_subplot_cols}")

        _label_old = label_old
        _label_new = label_new

        # TODO: find a better way to handle ensembles
        member_col_index = 0

        if len(col_names) > 1:
            if member_id == "":
                _label_old = f"{label_old} ({col_names[0][3:6]})" if len(col_names) > 1 else label_old
                _label_new = f"{label_new} ({col_names[0][3:6]})" if len(col_names) > 1 else label_new
            else:
                _label_old = f"{label_old} ({member_id})" if len(col_names) > 1 else label_old
                _label_new = f"{label_new} ({member_id})" if len(col_names) > 1 else label_new

        labels = {
            "new": _label_new, "old": _label_old
        }

        i = 0
        for _i, st_id in enumerate(sorted(current_station_ids)):

            # plot only selected stations
            if select_stations is not None:
                if st_id not in select_stations:
                    continue

            st_name = station_dict[st_id]

            row, col = plot_index_to_row_col(i, n_subplot_cols)
            ax = fig.add_subplot(gs[row, col], label=f"{row}_{col}_{st_id}")

            if shared_ax is None:
                shared_ax = ax
                xlims = (swl_stats_old[1].index.min(), swl_stats_old[1].index.max())

            if len(col_names) > 1:
                logging.warning(f"Using member: {col_names[0]}")

            logger.debug(f"i={i}, st_id={st_id}")
            old_series = swl_stats_old[0].xs(st_id, level="station_id")
            new_series = swl_stats_new[0].xs(st_id, level="station_id")

            plot_scores(ax, old_series, new_series,
                        col_name=col_names[member_col_index],
                        shared_ax=shared_ax,
                        title=f"{st_name} ({st_id})",
                        show_avg_diff=show_avg_diff, labels=labels)

            style_axes(ax, locator_base=forecast_hour_tick_multiplier)
            all_axes_except_last.append(ax)
            i += 1

        # add overall stats plot
        i = nsubplots - 1
        row, col = plot_index_to_row_col(i, n_subplot_cols)
        ax = fig.add_subplot(gs[row, col])

        old_series = swl_stats_old[1]
        new_series = swl_stats_new[1]

        plot_scores(ax, old_series, new_series, col_name=col_names[member_col_index], shared_ax=shared_ax,
                    title="All stations", labels=labels, show_avg_diff=show_avg_diff)

        style_axes(ax, locator_base=forecast_hour_tick_multiplier)
        ax.legend(loc="upper right", bbox_to_anchor=(1, -0.4), borderaxespad=0.)

        period_s = f"{swl_old[io_manager.TIME_COL_NAME].min():%Y%m%d%H}-{swl_old[io_manager.TIME_COL_NAME].max():%Y%m%d%H}"
        fig.suptitle(f"{statname_to_disp[suffix[1:]]}, {period_s}")
        st_time = swl_old[io_manager.TIME_COL_NAME].min()
        en_time = swl_old[io_manager.TIME_COL_NAME].max()

        if max_lead_hour is not None:
            img_file = img_dir / f"{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}{suffix}_max_lead_{max_lead_hour}.png"
        else:
            img_file = img_dir / f"{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}{suffix}.png"
        fig.savefig(str(img_file), dpi=400, bbox_inches="tight")

        # save for overall stats into a separate file
        fig = plt.figure(figsize=(5, 5))
        ax = fig.gca()

        plot_scores(ax, old_series, new_series, col_name=col_names[member_col_index], shared_ax=None,
                    title="All stations", labels=labels, show_avg_diff=show_avg_diff)

        style_axes(ax, locator_base=forecast_hour_tick_multiplier)
        ax.legend(loc="upper left")
        fig.suptitle(f"{statname_to_disp[suffix[1:]]}, {period_s}")

        if max_lead_hour is not None:
            img_file = img_dir / f"all_stations_{suffix[1:]}_max_lead_{max_lead_hour}.png"
        else:
            img_file = img_dir / f"all_stations_{suffix[1:]}.png"

        fig.savefig(img_file, dpi=400, bbox_inches="tight")
        plt.close(fig)

    logging.info("Finish compare_2_simulations ...")


def compare_rdsps_2018(station_dict=default_params.station_dict):
    img_dir = Path("data/plots/rdsps_parallel_vs_operational_std_gamma_test")
    swl_path_old = "/home/olh001/MATLAB/detide/data/old_data/data_for_scoring_rdsps_operational_2018050100_2018072000/surge_rdsps_operational.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/old_data/data_for_scoring_rdsps_parallel_2018050100_2018072000/surge_rdsps_parallel.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict)


def compare_rdsps_2018_datefix(station_dict=default_params.station_dict):
    img_dir = Path("data/plots/rdsps_parallel_vs_operational_std_gamma_test_datefix")
    swl_path_old = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_operational_2018042400_2018072000_datefix/surge_rdsps_operational.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_parallel_2018042400_2018072000_datefix/surge_rdsps_parallel.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict)


def compare_rdsps_2018_v01(station_dict=default_params.station_dict):
    img_dir = Path("data/plots/rdsps_parallel_vs_operational_std_gamma_v01")
    swl_path_old = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_operational_2018042400_2018072000_v01/surge_rdsps_operational.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_parallel_2018042400_2018072000_v01/surge_rdsps_parallel.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict)


def check_nodalcorr(station_dict=default_params.station_dict):
    img_dir = Path("data/plots/rdsps_operational_std_gamma_test_nodalcorr")
    swl_path_old = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_operational_2018042400_2018072000_datefix/surge_rdsps_operational.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_operational_2018042400_2018072000_datefix_nodalcorr/surge_rdsps_operational.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                          label_new="RDSPS, operational+nodal corr.")


def compare_resps_2018(station_dict=default_params.station_dict):
    img_dir = Path("data/plots/resps_experimental_vs_parallel_std_gamma_test")
    swl_path_old = "/home/olh001/MATLAB/detide/data/data_for_scoring_resps_experimental_2018041700_2018072000_datefix/surge_resps_experimental.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/data_for_scoring_resps_parallel_2018041700_2018072000_datefix/surge_resps_parallel.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                          label_old="RESPS, experimental", label_new="RESPS, parallel")


def compare_resps_2018_v01(station_dict=default_params.station_dict):
    img_dir = Path("data/plots/resps_experimental_vs_parallel_std_gamma_v01")
    swl_path_old = "/home/olh001/MATLAB/detide/data/data_for_scoring_resps_experimental_2018041700_2018072000_v01/surge_resps_experimental.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/data_for_scoring_resps_parallel_2018041700_2018072000_v01/surge_resps_parallel.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                          label_old="RESPS, experimental", label_new="RESPS, parallel")


# ==============================v03 of loadprogs

def compare_resps_2018_v03(station_dict=default_params.station_dict):
    img_dir = Path("data/plots/resps_experimental_vs_parallel_std_gamma_v03")
    swl_path_old = "/home/olh001/MATLAB/detide/data/data_for_scoring_resps_experimental_2018041700_2018072000_v03/surge_resps_experimental.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/data_for_scoring_resps_parallel_2018041700_2018072000_v03/surge_resps_parallel.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                          label_old="RESPS, experimental", label_new="RESPS, parallel")


def compare_rdsps_2018_v03(station_dict=default_params.station_dict):
    img_dir = Path("data/plots/rdsps_parallel_vs_operational_std_gamma_v03")
    swl_path_old = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_operational_2018042400_2018072000_v03/surge_rdsps_operational.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_parallel_2018042400_2018072000_v03/surge_rdsps_parallel.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict)


# ==============================v03 of loadprogs


# ==============================gem5 research cycle testing


def compare_rdsps_panal_H17YY15NWPH8A_v03(station_dict=default_params.station_dict):
    img_dir = Path("data/plots/rdsps_experimental_vs_H17YY15NWPH8A_v03")
    swl_path_old = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_pseudo-analysis_experimental_2016121500_2017123118_v03/surge_rdsps_pseudo-analysis_experimental.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_pseudo-analysis_H17YY15NWPH8A_2016121500_2017123118_v03/surge_rdsps_pseudo-analysis_H17YY15NWPH8A.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                          label_old="RDSPS (PA), experimental", label_new="RDSPS(PA), H17YY15NWPH8A",
                          forecast_hour_tick_multiplier=1)


def compare_rdsps_forecast_2018_v03(station_dict=default_params.station_dict):
    # TODO: change the paths before using

    img_dir = Path("data/plots/rdsps_parallel_vs_operational_std_gamma_v03")
    swl_path_old = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_operational_2018042400_2018072000_v03/surge_rdsps_operational.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_parallel_2018042400_2018072000_v03/surge_rdsps_parallel.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict)


# ==============================gem5 research cycle testing


# ========== levelling vs no-levelling in rdsps ===============
def compare_rdsps_panal_levelling(station_dict=default_params.station_dict):
    img_dir = Path(f"data/plots/rdsps_levelling_vs_nolevelling_2017010100_2018100918_{datetime.utcnow():%Y%m%d%H%M}")
    # swl_path_old = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_nolev_2018080100_2018100918/surge_rdsps_pseudo-analysis_nolev.dat"
    # swl_path_new = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_lev_2018080100_2018100918/surge_rdsps_pseudo-analysis_lev.dat"

    swl_path_old = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_nolev_2017010100_2018100918_update/surge_rdsps_pseudo-analysis_nolev.dat"
    swl_path_new = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_lev_2017010100_2018100918_update/surge_rdsps_pseudo-analysis_lev.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                          # label_old="RDSPS (PA),-levelling", label_new="RDSPS(PA),+levelling", forecast_hour_tick_multiplier=1)
                          label_old="unadjusted storm surge", label_new="storm surge (levelled)",
                          forecast_hour_tick_multiplier=1)


# ========== levelling vs no-levelling in rdsps ===============
def compare_rdsps_panal_levelling_v000(station_dict=default_params.station_dict):
    img_dir = Path(f"data/plots/rdsps_levelling_vs_nolevelling_2018080100_2018100918_{datetime.utcnow():%Y%m%d%H%M}")
    # swl_path_old = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_nolev_2018080100_2018100918/surge_rdsps_pseudo-analysis_nolev.dat"
    # swl_path_new = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_lev_2018080100_2018100918/surge_rdsps_pseudo-analysis_lev.dat"

    swl_path_old = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_nolev_2018080100_2018100918_update/surge_rdsps_pseudo-analysis_nolev.dat"
    swl_path_new = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_lev_2018080100_2018100918_update/surge_rdsps_pseudo-analysis_lev.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                          # label_old="RDSPS (PA),-levelling", label_new="RDSPS(PA),+levelling", forecast_hour_tick_multiplier=1)
                          label_old="unadjusted storm surge", label_new="storm surge (levelled)",
                          forecast_hour_tick_multiplier=1)


# ========== levelling vs no-levelling in rdsps ===============
def compare_rdsps_panal_levelling_select_stations(station_dict=default_params.station_dict):
    img_dir = Path(f"data/plots/rdsps_levelling_vs_nolevelling_2017010100_2018100918_select_stations")
    # swl_path_old = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_nolev_2018080100_2018100918/surge_rdsps_pseudo-analysis_nolev.dat"
    # swl_path_new = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_lev_2018080100_2018100918/surge_rdsps_pseudo-analysis_lev.dat"

    swl_path_old = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_nolev_2017010100_2018100918_update/surge_rdsps_pseudo-analysis_nolev.dat"
    swl_path_new = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_lev_2017010100_2018100918_update/surge_rdsps_pseudo-analysis_lev.dat"

    plot_params = {
        "figure.figsize": (9, 6),
        "font.size": 10,
    }

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                          # label_old="RDSPS (PA),-levelling", label_new="RDSPS(PA),+levelling", forecast_hour_tick_multiplier=1)
                          label_old="unadjusted storm surge", label_new="storm surge (levelled)",
                          forecast_hour_tick_multiplier=1,
                          select_stations=[365, 1805, 1430, 2330, 835], n_subplot_cols=3,
                          custom_rc_params=plot_params)


# ========== PN vs P0 in rdsps ===============
def compare_rdsps_forecast_pn_vs_p0_v000(station_dict=default_params.station_dict):
    img_dir = Path(f"data/plots/rdsps_pn_vs_p0_2018042400_2018102212_{datetime.utcnow():%Y%m%d%H%M}")
    # swl_path_old = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_nolev_2018080100_2018100918/surge_rdsps_pseudo-analysis_nolev.dat"
    # swl_path_new = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_lev_2018080100_2018100918/surge_rdsps_pseudo-analysis_lev.dat"

    swl_path_old = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_P0_2018042400_2018102212/surge_rdsps_forecast_P0.dat"
    swl_path_new = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_PN_2018042400_2018102212/surge_rdsps_forecast_PN.dat"

    default_params.vname_to_limits = {
        "stde": (0, 0.3),
        "gamma": (0, 3),
        "stde_obs": (0, 0.3),
        "gamma_varobsallvhour": (0, 3)
    }

    plot_params = {
        "figure.figsize": (10, 12),
        "font.size": 8,
    }

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                          # label_old="RDSPS (PA),-levelling", label_new="RDSPS(PA),+levelling", forecast_hour_tick_multiplier=1)
                          label_old="storm surge (P0)", label_new="storm surge (PN)", forecast_hour_tick_multiplier=24,
                          custom_rc_params=plot_params)


# ========== PN vs P0 in rdsps ===============
def compare_rdsps_forecast_pn_vs_p0_v001(station_dict=default_params.station_dict):
    img_dir = Path(f"data/plots/rdsps_pn_vs_pn_2018042400_2018102212_{datetime.utcnow():%Y%m%d%H%M}")
    # swl_path_old = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_nolev_2018080100_2018100918/surge_rdsps_pseudo-analysis_nolev.dat"
    # swl_path_new = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_lev_2018080100_2018100918/surge_rdsps_pseudo-analysis_lev.dat"

    swl_path_old = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_PN_2018042400_2018102212/surge_rdsps_forecast_PN.dat"
    swl_path_new = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_PN_2018042400_2018102212/surge_rdsps_forecast_PN.dat"

    default_params.vname_to_limits = {
        "stde": (0, 0.3),
        "gamma": (0, 3),
        "stde_obs": (0, 0.3),
        "gamma_varobsallvhour": (0, 3)
    }

    plot_params = {
        "figure.figsize": (10, 12),
        "font.size": 8,
    }

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                          # label_old="RDSPS (PA),-levelling", label_new="RDSPS(PA),+levelling", forecast_hour_tick_multiplier=1)
                          label_old="storm surge (PN)", label_new="storm surge (PN)", forecast_hour_tick_multiplier=24,
                          custom_rc_params=plot_params)


#  ================================================================================================================================

def main(station_dict=default_params.station_dict):
    swl_path_old = "/home/olh001/MATLAB/detide/data/old_data/data_for_scoring_rdsps_operational_2018050100_2018072000/surge_rdsps_operational.dat"
    swl = io_manager.read_wl_station_data(swl_path_old, station_dict=station_dict)

    print(swl.head())

    per_station_stde, overall_stde = stde(swl)
    per_station_gamma, overall_gamma = gamma(swl)

    print(per_station_stde.head())

    per_station_stde.xs(65, level="station_id").plot(subplots=True,
                                                     y=io_manager.get_model_column_names(swl, suffix="_stde"))
    per_station_stde.xs(365, level="station_id").plot(subplots=True,
                                                      y=io_manager.get_model_column_names(swl, suffix="_stde"))
    overall_stde.plot(subplots=True, y=io_manager.get_model_column_names(swl, suffix="_stde"))

    per_station_gamma.xs(65, level="station_id").plot(subplots=True,
                                                      y=io_manager.get_model_column_names(swl, suffix="_gamma"))
    per_station_gamma.xs(365, level="station_id").plot(subplots=True,
                                                       y=io_manager.get_model_column_names(swl, suffix="_gamma"))
    overall_gamma.plot(subplots=True, y=io_manager.get_model_column_names(swl, suffix="_gamma"))

    plt.show()


if __name__ == '__main__':
    # main()
    # compare_rdsps_2018()
    # compare_rdsps_2018_v01()
    # compare_resps_2018_v01()

    # compare_rdsps_2018_v03()
    # compare_resps_2018_v03()

    # compare_rdsps_panal_H17YY15NWPH8A_v03()

    # compare_rdsps_panal_levelling_select_stations()

    # compare_rdsps_panal_levelling_v000()

    # check_nodalcorr()
    # compare_resps_2018()

    # compare_rdsps_forecast_pn_vs_p0_v000()
    compare_rdsps_forecast_pn_vs_p0_v001()  # for PN only
