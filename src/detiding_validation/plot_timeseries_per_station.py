import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

from detiding_validation import io_manager
from detiding_validation.config import default_params
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def plot_time_series_for_station_all(twl_obs, swl, st_id, station_dict=default_params.station_dict,
                                     st_time=None, en_time=None, img_dir=None):
    time_points = []
    dt = timedelta(hours=1)
    d = st_time
    while d <= en_time:
        time_points.append(d)
        d += dt

    twl_sel = dict(list(twl_obs.groupby("station_id")))[st_id]
    twl_sel.set_index(io_manager.TIME_COL_NAME, inplace=True)
    twl_sel = twl_sel.reindex(time_points)

    # Plot total water level
    axes = twl_sel.plot(subplots=True,
                        y=["obs", ],
                        label=[r"$\eta_{obs}$", ],
                        color="k",
                        legend=True, lw=0.5, figsize=(8, 6))

    # detided data
    st_sel = dict(list(swl.groupby("station_id")))[st_id]

    st_sel["do"] = [tv - timedelta(hours=int(hv)) for tv, hv in
                    zip(st_sel[io_manager.TIME_COL_NAME], st_sel[io_manager.VALIDH_COL_NAME])]

    st_sel.sort_values(["do", io_manager.VALIDH_COL_NAME], inplace=True)

    # st_sel = st_sel.drop_duplicates(io_manager.TIME_COL_NAME)
    #
    # st_sel.set_index(io_manager.TIME_COL_NAME, inplace=True)
    # st_sel = st_sel.reindex(time_points)
    #
    # st_sel.sort_values(io_manager.TIME_COL_NAME, inplace=True)

    st_sel.groupby("do").head(23).plot(x=io_manager.TIME_COL_NAME, y=["mod", "obs"],
                                       label=[r"$\eta_{S}$", r"$\eta_{obs} - \eta_{TD}$"],
                                       ax=axes[0], color=["r", "k"], legend=False)

    # st_sel.plot(y=["obs", ], exp_label=[r"$\eta_{obs} - \eta_{TD}$", ], ax=axes[0], color="r")
    # st_sel.plot(y=["mod", ], exp_label=[r"$\eta_{S}$", ], ax=axes[0], color="b")

    axes[0].set_xlim(st_time, en_time)
    # axes[0].legend(title=station_dict[st_id])

    plt.savefig(str(img_dir / f"{st_id:05d}.png"), dpi=300, bbox_inches="tight")
    plt.close(axes[0].figure)


def plot_time_series_for_station(twl_obs, swl, st_id, station_dict=default_params.station_dict,
                                 st_time=None, en_time=None, img_dir=None, sim_start_freq_hours=24):
    fig = plt.figure(figsize=(8, 6))
    axes = [fig.gca()]

    # detided data
    st_sel = dict(list(swl.groupby("station_id")))[st_id]

    st_sel = st_sel[st_sel[io_manager.VALIDH_COL_NAME] <= sim_start_freq_hours]
    st_sel.sort_values(io_manager.VALIDH_COL_NAME, inplace=True)

    g = st_sel.set_index(io_manager.TIME_COL_NAME)
    g.resample("1H").asfreq().plot(y=["mod", "obs"],
                                   label=[r"$\eta_{S}$", r"$\eta_{obs} - \eta_{T}$"],
                                   ax=axes[0], color=["r", "k"], legend=False)

    axes[0].set_xlim(st_time, en_time)
    axes[0].legend(title=station_dict[st_id], handles=[
        Line2D([0], [0], color="k", label=r"$\eta_{obs} - \eta_{T}$"),
        Line2D([0], [0], color="r", label=r"$\eta_{S}$")
    ])

    plt.savefig(str(img_dir / f"{st_id:05d}.png"), dpi=300, bbox_inches="tight")
    plt.close(axes[0].figure)


def plot_diff_time_series_for_station(swl, st_id, station_dict=default_params.station_dict,
                                      st_time=None, en_time=None, img_dir=None, sim_start_freq_hours=24):
    fig = plt.figure(figsize=(8, 6))
    axes = [fig.gca()]

    # detided data
    st_sel = dict(list(swl.groupby("station_id")))[st_id]

    st_sel = st_sel[st_sel[io_manager.VALIDH_COL_NAME] <= sim_start_freq_hours]
    st_sel.sort_values(io_manager.VALIDH_COL_NAME, inplace=True)
    g = st_sel.set_index(io_manager.TIME_COL_NAME)
    g["diff"] = g["obs"][:] - g["mod"][:]

    label = r"$\eta_{obs} - \eta_{T} - \eta_{S}$"
    g.resample("1H").asfreq().plot(y="diff",
                                   label=label,
                                   ax=axes[0],
                                   color="k",
                                   legend=False)

    axes[0].set_xlim(st_time, en_time)
    axes[0].legend(title=station_dict[st_id], handles=[
        Line2D([0], [0], color="k", label=label),
    ])

    plt.savefig(str(img_dir / f"diff_{st_id:05d}.png"), dpi=300, bbox_inches="tight")
    plt.close(axes[0].figure)


def plot_time_series_for_station_many_models(swl_list, st_id, station_dict=default_params.station_dict,
                                             st_time=None, en_time=None, img_dir=None, model_label_list=(),
                                             model_colors=("b", "r"),
                                             run_freq_hours=6, ylim=None, linewidth=1, member_id=""):
    """
    :param swl_list:
    :param st_id:
    :param station_dict:
    :param st_time:
    :param en_time:
    :param img_dir:
    :param model_label_list:
    :param model_colors:
    :param run_freq_hours:
    :param ylim:
    :param linewidth:
    :param member_id:
    :return: a dictionary of {label: {gamma2: value, sigma: value}}
    """
    if isinstance(run_freq_hours, int):
        run_freq_hours = {label: run_freq_hours for label in model_label_list}

    model_label_to_color = OrderedDict(zip(model_label_list, model_colors))
    model_label_to_series = OrderedDict()

    # Select and plot obs on top of the model data
    st_sel_obs = swl_list[0][swl_list[0][io_manager.STID_COL_NAME] == st_id]
    st_sel_obs = st_sel_obs[st_sel_obs[io_manager.VALIDH_COL_NAME] <= run_freq_hours[model_label_list[0]]]
    st_sel_obs.sort_values([io_manager.TIME_COL_NAME, io_manager.VALIDH_COL_NAME], inplace=True)
    st_sel_obs.drop_duplicates(subset=io_manager.TIME_COL_NAME, keep="last", inplace=True)
    st_sel_obs.set_index(io_manager.TIME_COL_NAME, inplace=True)
    st_sel_obs = st_sel_obs.asfreq("60T")

    if len(st_sel_obs) == 0:
        logging.warning(f"No obs data for {st_id}, skipping it.")
        return

    fig = plt.figure(figsize=(8, 6))
    axes = [fig.gca()]

    for swl, model_label, model_color in zip(swl_list, model_label_list, model_colors):
        st_sel_mod = swl[swl[io_manager.STID_COL_NAME] == st_id]
        st_sel_mod = st_sel_mod[st_sel_mod[io_manager.VALIDH_COL_NAME] <= run_freq_hours[model_label]]

        st_sel_mod.sort_values([io_manager.TIME_COL_NAME, io_manager.VALIDH_COL_NAME], inplace=True)
        st_sel_mod.drop_duplicates(subset=io_manager.TIME_COL_NAME, keep="last", inplace=True)

        if len(st_sel_mod) == 0:
            logger.warning(f"No model data data for {st_id}, skipping")
            continue

        st_sel_mod.set_index(io_manager.TIME_COL_NAME, inplace=True)
        to_plot = st_sel_mod.asfreq("60T")
        to_plot.plot(y=["mod" + member_id, ],
                     ax=axes[0], color=[model_color, ], legend=False, grid=True, linewidth=linewidth)

        model_label_to_series[model_label] = to_plot["mod" + member_id]

    st_sel_obs.plot(y=["obs"], ax=axes[0], color=["k"], legend=False, linewidth=linewidth)
    model_label_to_series["obs"] = st_sel_obs["obs"]

    same_mod = len(set(model_label_list)) == 1

    line_obs = Line2D([0], [0], color="k", label="Obs", linewidth=linewidth * 2)
    lines_mod = [
        Line2D([0], [0], color=c, label=f"{model_label}", linewidth=linewidth) for
        c, model_label in zip(model_colors, model_label_list if not same_mod else [model_label_list[0], ])
    ]
    legend_handles = [line_obs, ] + lines_mod

    axes[0].set_xlim(st_time, en_time)
    axes[0].legend(title=station_dict[st_id],
                   handles=legend_handles)
    axes[0].grid(which="minor", linestyle="dashed", linewidth=0.3)
    if ylim is not None:
        axes[0].set_ylim(*ylim)

    label_to_scores = draw_mpl_table(model_label_to_color, model_label_to_series)

    fig.savefig(str(img_dir / f"{st_id}.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    return label_to_scores


def draw_mpl_table(lab_to_color: dict, lab_to_series: dict):
    columns = (r"$\gamma^2$", r"$\sigma_{\varepsilon}$")
    rows = [rk for rk in lab_to_color]
    cell_text = []

    label_to_scores = {}

    obs = lab_to_series["obs"].dropna()

    for lab in rows:

        logger.debug("\nobs\n%s\nmod\n%s", obs.head(), lab_to_series[lab].head())
        mod = lab_to_series[lab]

        indices = mod.index.intersection(obs.index)

        mod = mod.loc[indices]
        obs_sel = obs.loc[indices]

        gamma2 = np.std(mod.values - obs_sel.values) ** 2 / np.std(obs_sel.values) ** 2
        sigma = np.std(mod.values - obs_sel.values)

        cell_text.append([f"{gamma2:.2f}", f"{sigma:.4f}"])

        label_to_scores[lab] = {"gamma2": gamma2, "sigma": sigma, "count": len(indices)}

    plt.table(
        cellText=cell_text,
        rowLabels=rows,
        colLabels=columns,
        loc="top"
    )

    return label_to_scores


def plot_time_series_for_station_many_models_one_plot_per_fc(swl_list, st_id, station_dict=default_params.station_dict,
                                                             st_time=None, en_time=None, img_dir=None,
                                                             model_label_list=(), model_colors=("b", "r"),
                                                             ylim=None, linewidth=1, member_id=""):
    # detided data
    st_sel_by_station = swl_list[0][swl_list[0][io_manager.STID_COL_NAME] == st_id]

    if len(st_sel_by_station) == 0:
        logger.info(f"No data for {st_id}, skipping")
        return

    # calculate date of origin to identify different forecasts
    do_series = st_sel_by_station[io_manager.TIME_COL_NAME] - st_sel_by_station[io_manager.VALIDH_COL_NAME].map(
        lambda vh: timedelta(hours=vh))
    st_sel_by_station = st_sel_by_station.assign(dateo=do_series)
    st_sel_by_station = st_sel_by_station.sort_values(["dateo", io_manager.TIME_COL_NAME])

    gs = GridSpec(nrows=2, ncols=1)
    for do, st_sel in st_sel_by_station.groupby("dateo"):
        st_sel = st_sel.sort_values(io_manager.TIME_COL_NAME)
        st_sel = st_sel.set_index(io_manager.TIME_COL_NAME)
        st_sel = st_sel.asfreq("60T")
        if len(st_sel.dropna()) == 0:
            logger.warning(f"No obs data for {st_id} and {do}, skipping it.")
            continue


        fig = plt.figure(figsize=(8, 6))
        axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0])]

        only_one_model_to_plot = len(set(model_label_list)) == 1

        # complete timeseries
        for swl, model_label, model_color in zip(swl_list, model_label_list, model_colors):
            st_sel_mod = swl[swl[io_manager.STID_COL_NAME] == st_id]

            do_series = st_sel_by_station[io_manager.TIME_COL_NAME] - st_sel_by_station[io_manager.VALIDH_COL_NAME].map(
                lambda vh: timedelta(hours=vh))
            st_sel_mod = st_sel_mod.assign(dateo=do_series)
            st_sel_mod = st_sel_mod[st_sel_mod["dateo"] == do]

            st_sel_mod = st_sel_mod.sort_values(io_manager.TIME_COL_NAME)

            assert len(st_sel_mod) > 0, f"No model data data for {st_id}"

            mod_cols = [c for c in st_sel_mod if c.startswith("mod")]

            st_sel_mod.set_index(io_manager.TIME_COL_NAME, inplace=True)

            if len(mod_cols) > 1:
                # ensemble
                mod_members_to_plot = st_sel_mod[mod_cols]
                median = mod_members_to_plot.median(axis=1).asfreq("60T")
                qmax = mod_members_to_plot.quantile(0.9, axis=1).asfreq("60T")
                qmin = mod_members_to_plot.quantile(0.1, axis=1).asfreq("60T")

                median.plot(ax=axes[0], color=model_color, legend=False, linewidth=linewidth)
                axes[0].fill_between(median.index, qmin, qmax, facecolor=model_color, alpha=0.2)
                qmin.plot(ax=axes[0], color=model_color, legend=False, linewidth=linewidth, style="--")
                qmax.plot(ax=axes[0], color=model_color, legend=False, linewidth=linewidth, style="--")

                # biases for each member
                for m_col in mod_cols:
                    (st_sel_mod.asfreq("60T")[m_col] - st_sel["obs"]).plot(
                        ax=axes[1], color=[model_color, ], legend=False, grid=True,
                        linewidth=linewidth * 0.5)

            else:
                # deterministic
                for m_col in mod_cols:
                    st_sel_mod.asfreq("60T").plot(y=[m_col, ],
                                              ax=axes[0], color=[model_color, ], legend=False, grid=True,
                                              linewidth=linewidth)

                    # biases
                    (st_sel_mod.asfreq("60T")[m_col] - st_sel["obs"]).plot(
                                            ax=axes[1], color=[model_color, ], legend=False, grid=True,
                                            linewidth=linewidth)
                    axes[1].set_title("Bias (mod-obs)")

            # only one system is scored
            if only_one_model_to_plot:
                break

        st_sel.plot(y=["obs"], ax=axes[0], color=["k"], legend=False, linewidth=linewidth * 2.5, zorder=10)

        axes[0].set_title(f"forecast start: {do}")
        # axes[0].set_xlim(st_time, en_time)

        legend_handles = [Line2D([0], [0], color="k", label=r"Obs", linewidth=linewidth * 2), ] + \
                         [Line2D([0], [0], color=c, label=f"{model_label}", linewidth=linewidth) for c, model_label in
                          zip(model_colors, model_label_list)]

        axes[0].legend(title=station_dict[st_id], handles=legend_handles)
        axes[0].grid(which="minor", linestyle="dashed", linewidth=0.3)
        if ylim is not None:
            axes[0].set_ylim(*ylim)

        plt.savefig(str(img_dir / f"{st_id}_{do:%Y%m%d%H}.png"), dpi=300, bbox_inches="tight")
        plt.close(axes[0].figure)


def main(station_dict=default_params.station_dict):
    # Plotting period
    st_time = datetime(2018, 6, 1)
    en_time = datetime(2018, 7, 1)

    detiding_plots_dir = Path(f"data/plots/detiding_comparisons/{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}_chunks2")
    if not detiding_plots_dir.is_dir():
        detiding_plots_dir.mkdir(parents=True, exist_ok=True)

    twl_obs_path = "/home/olh001/MATLAB/detide/data/obs_from_Natacha/Observations/tide_gauge/2018"
    twl = io_manager.read_wl_station_data(twl_obs_path, station_dict=station_dict)

    swl_path = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_parallel_2018042400_2018072000_datefix/surge_rdsps_parallel.dat"
    swl = io_manager.read_wl_station_data(swl_path, station_dict=station_dict)

    logger.debug(swl.head())

    for st_id in default_params.station_dict:
        plot_time_series_for_station(twl, swl, st_id, st_time=st_time, en_time=en_time,
                                     img_dir=detiding_plots_dir)

        plot_diff_time_series_for_station(swl, st_id, st_time=st_time, en_time=en_time,
                                          img_dir=detiding_plots_dir)


def compare_sims_timeseries_back2back(data_labels: list = None,
                                      data_paths: dict = None, data_colors: dict = None,
                                      plots_dir: Path = None,
                                      station_dict=default_params.station_dict, st_time=None, en_time=None,
                                      run_freq_hours=12, linewidth=1,
                                      b2b_cutoff_hours=1000, member_id=""):
    """
    Use for comparing timeseries, more or less general interface
    :param member_id:
    :param run_freq_hours: if dict {data_label: run_freq_hours}
    :param linewidth:
    :param b2b_cutoff_hours: only plot first b2b_cutoff_hours
    :param data_labels:
    :param data_paths: Paths to the dat files prepared by loadprogs_python
    :param data_colors:
    :param plots_dir:
    :param station_dict:
    :param st_time:
    :param en_time:
    :return: dictionary of gamma^2 and sigma scores for each station
    """
    if plots_dir is None:
        plots_dir = Path(f"data/plots/detiding_comparisons/{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}_rdsps_par_vs_opr")

    if not plots_dir.is_dir():
        plots_dir.mkdir(parents=True, exist_ok=True)

    swl_list = [io_manager.read_wl_station_data(data_paths[label], station_dict=station_dict) for label in data_labels]
    model_labels = data_labels
    model_colors = [data_colors[label] for label in data_labels]

    if b2b_cutoff_hours is not None:
        if st_time is not None:
            en_time = st_time + timedelta(hours=b2b_cutoff_hours)
        else:
            logger.info(f"st_time={st_time}, b2b_cutoff_hours is ignored!")

    station_scores = {}
    for st_id in station_dict:
        label_to_scores = plot_time_series_for_station_many_models(swl_list, st_id, st_time=st_time, en_time=en_time,
                                                 img_dir=plots_dir, model_label_list=model_labels,
                                                 model_colors=model_colors, run_freq_hours=run_freq_hours,
                                                 linewidth=linewidth, station_dict=station_dict, member_id=member_id)
        station_scores[st_id] = label_to_scores

    return station_scores


def compare_sims_timeseries_one_plot_per_fc(data_labels: list = None, data_paths: dict = None, data_colors: dict = None,
                                            plots_dir: Path = None,
                                            station_dict=default_params.station_dict, st_time=None, en_time=None,
                                            linewidth=1, member_id=""):
    """
    Use for comparing timeseries, more or less general interface
    :param data_labels:
    :param data_paths: Paths to the dat files prepared by loadprogs_python
    :param data_colors:
    :param plots_dir:
    :param station_dict:
    :param st_time:
    :param en_time:
    """

    if not plots_dir is None:
        plots_dir.mkdir(parents=True, exist_ok=True)
    else:
        raise ValueError("The folder for output plots should be specified.")

    logging.info(f"reading data from {data_paths}")
    swl_list = [io_manager.read_wl_station_data(data_paths[label], station_dict=station_dict) for label in data_labels]
    model_labels = data_labels
    model_colors = [data_colors[label] for label in data_labels]

    for st_id in station_dict:
        plot_time_series_for_station_many_models_one_plot_per_fc(swl_list, st_id, st_time=st_time, en_time=en_time,
                                                                 img_dir=plots_dir, model_label_list=model_labels,
                                                                 model_colors=model_colors,
                                                                 linewidth=linewidth, station_dict=station_dict,
                                                                 member_id=member_id)


def main_compare_sims(station_dict=default_params.station_dict):
    # Plotting period
    st_time = datetime(2018, 6, 1)
    en_time = datetime(2018, 7, 1)

    detiding_plots_dir = Path(f"data/plots/detiding_comparisons/{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}_rdsps_par_vs_opr")
    if not detiding_plots_dir.is_dir():
        detiding_plots_dir.mkdir(parents=True, exist_ok=True)

    twl_obs_path = "/home/olh001/MATLAB/detide/data/obs_from_Natacha/Observations/tide_gauge/2018"
    twl = io_manager.read_wl_station_data(twl_obs_path, station_dict=station_dict)

    swl_paths = [
        "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_parallel_2018042400_2018072000_datefix/surge_rdsps_parallel.dat",
        "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_operational_2018042400_2018072000_datefix/surge_rdsps_operational.dat"
    ]

    swl_list = [io_manager.read_wl_station_data(swl_path, station_dict=station_dict) for swl_path in swl_paths]
    model_labels = ["RDSPS, parallel", "RDSPS, operational"]
    model_colors = ["r", "b"]

    for st_id in default_params.station_dict:
        plot_time_series_for_station_many_models(swl_list, st_id, st_time=st_time, en_time=en_time,
                                                 img_dir=detiding_plots_dir, model_label_list=model_labels,
                                                 model_colors=model_colors)


def main_compare_sims_levelling(station_dict=default_params.station_dict):
    # Plotting period
    st_time = datetime(2018, 8, 1, 0)
    en_time = datetime(2018, 10, 10, 0)

    detiding_plots_dir = Path(
        f"data/plots/detiding_comparisons/{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}_rdsps_lvl_vs_nolvl_{datetime.utcnow():%Y%m%d%H}")
    if not detiding_plots_dir.is_dir():
        detiding_plots_dir.mkdir(parents=True, exist_ok=True)

    twl_obs_path = "/home/olh001/MATLAB/detide/data/obs/merged_2017_201809"
    twl = io_manager.read_wl_station_data(twl_obs_path, station_dict=station_dict)

    swl_paths = [
        "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_lev_2018080100_2018100918_update/surge_rdsps_pseudo-analysis_lev.dat",
        "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_nolev_2018080100_2018100918_update/surge_rdsps_pseudo-analysis_nolev.dat"
    ]

    swl_list = [io_manager.read_wl_station_data(swl_path, station_dict=station_dict) for swl_path in swl_paths]
    model_labels = ["storm surge (levelled)", "unadjusted storm surge"]
    model_colors = ["r", "b"]

    for st_id in default_params.station_dict:
        plot_time_series_for_station_many_models(swl_list, st_id, st_time=st_time, en_time=en_time,
                                                 img_dir=detiding_plots_dir, model_label_list=model_labels,
                                                 model_colors=model_colors)


def main_compare_sims_levelling_long_period(station_dict=default_params.station_dict):
    # Plotting period
    st_time = datetime(2017, 1, 1, 0)
    en_time = datetime(2018, 10, 9, 18)

    detiding_plots_dir = Path(
        f"data/plots/detiding_comparisons/{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}_rdsps_lvl_vs_nolvl_{datetime.utcnow():%Y%m%d%H}_same_scale_001")
    if not detiding_plots_dir.is_dir():
        detiding_plots_dir.mkdir(parents=True, exist_ok=True)

    twl_obs_path = "/home/olh001/MATLAB/detide/data/obs/merged_2017_201809"
    twl = io_manager.read_wl_station_data(twl_obs_path, station_dict=station_dict)

    swl_paths = [
        "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_lev_2017010100_2018100918_update/surge_rdsps_pseudo-analysis_lev.dat",
        "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_pseudo-analysis_nolev_2017010100_2018100918_update/surge_rdsps_pseudo-analysis_nolev.dat"
    ]

    swl_list = [io_manager.read_wl_station_data(swl_path, station_dict=station_dict) for swl_path in swl_paths]
    model_labels = ["storm surge (levelled)", "unadjusted storm surge"]
    model_colors = ["r", "b"]

    for st_id in default_params.station_dict:
        plot_time_series_for_station_many_models(swl_list, st_id, st_time=st_time, en_time=en_time,
                                                 img_dir=detiding_plots_dir, model_label_list=model_labels,
                                                 model_colors=model_colors)


def main_compare_sims_pn_vs_p0(station_dict=default_params.station_dict):
    # Plotting period
    st_time = datetime(2018, 4, 24, 0)
    en_time = datetime(2018, 10, 22, 12)

    detiding_plots_dir = Path(
        f"data/plots/detiding_comparisons/{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}_rdsps_PN_vs_P0_{datetime.utcnow():%Y%m%d%H}_ts_with_obs_001")
    if not detiding_plots_dir.is_dir():
        detiding_plots_dir.mkdir(parents=True, exist_ok=True)

    twl_obs_path = "/home/olh001/MATLAB/detide/data/obs/merged_2017_201810"
    twl = io_manager.read_wl_station_data(twl_obs_path, station_dict=station_dict)

    swl_paths = [
        "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_PN_2018042400_2018102212/surge_rdsps_forecast_PN.dat",
        "/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_P0_2018042400_2018102212/surge_rdsps_forecast_P0.dat"
    ]

    swl_list = [io_manager.read_wl_station_data(swl_path, station_dict=station_dict) for swl_path in swl_paths]
    model_labels = ["storm surge (PN)", "storm surge (P0)"]
    model_colors = ["r", "b"]

    for st_id in default_params.station_dict:
        plot_time_series_for_station_many_models(swl_list, st_id, st_time=st_time, en_time=en_time,
                                                 img_dir=detiding_plots_dir, model_label_list=model_labels,
                                                 model_colors=model_colors, run_freq_hours=36)


if __name__ == '__main__':
    # main()
    # main_compare_sims_levelling_long_period()
    main_compare_sims_pn_vs_p0()
