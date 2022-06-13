from pathlib import Path

from datetime import datetime

from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

from surge_validation import io_manager
from surge_validation.config import default_params
import matplotlib.pyplot as plt
import numpy as np



def plot_time_series_per_station_subplots_multiple_sims(swl_list, st_id, st_time=None, en_time=None, img_dir=None, sim_start_freq_hours=24,
                                                        station_dict=default_params.station_dict,
                                                        sim_labels=(), sim_colors=()):
    fig = plt.figure(figsize=(8, 6))
    gs = GridSpec(2, 1)

    ax_vals = None
    ax_diff = None

    obs_legend_handle = Line2D([0], [0], color="k", label=r"$\eta_{obs} - \eta_{T}$")
    mod_legend_handles = []
    bias_legend_handles = []
    biases = {}
    sim_label_to_handle = {}

    for swl, sim_label, sim_color in zip(swl_list, sim_labels, sim_colors):

        # detided data
        st_sel = dict(list(swl.groupby("station_id")))[st_id]

        st_sel = st_sel[st_sel[io_manager.VALIDH_COL_NAME] <= sim_start_freq_hours]
        st_sel.sort_values(io_manager.VALIDH_COL_NAME, inplace=True)
        g = st_sel.set_index(io_manager.TIME_COL_NAME)
        g["diff"] = g["obs"][:] - g["mod"][:]
        # Take into account cases when dates are not in whole hours
        g = g.resample("60T", base=g.index[0].minute).asfreq()

        # ===== plotting

        ax_vals = fig.add_subplot(gs[0, 0]) if ax_vals is None else ax_vals
        ax_vals.set_xlim(st_time, en_time)
        g.plot(y=["mod", "obs"], legend=False, color=[sim_color, "k"], ax=ax_vals)
        mod_legend_handles.append(
            Line2D([0], [0], color=sim_color, label=f"{sim_label} " + r"($\eta_{S}$)")
        )
        bias_legend_handles.append(
            Line2D([0], [0], color=sim_color, label=f"{sim_label} " + r"($\delta\eta_{S}$)")
        )

        ax_diff = fig.add_subplot(gs[1, 0], sharex=ax_vals) if ax_diff is None else ax_diff
        label = r"$\eta_{obs} - \eta_{T} - \eta_{S}$"
        g.plot(y="diff",
               label=label,
               ax=ax_diff,
               color=sim_color,
               legend=False)
        biases[sim_label] = np.abs(g["diff"].dropna().values)
        sim_label_to_handle[sim_label] = bias_legend_handles[-1]

    percentage_time_best = {}

    for label, vals in biases.items():
        percentage_time_best[label] = (vals <= np.min([v for v in biases.values()], axis=0)).sum() / len(vals) * 100
        sim_label_to_handle[label]._label += f", best {percentage_time_best[label]:.1f}% of time"

    ax_vals.legend(title=station_dict[st_id], handles=[obs_legend_handle, ] + mod_legend_handles)
    ax_diff.legend(title="Biases", handles=bias_legend_handles)

    plt.savefig(str(img_dir / f"subplots_{st_id:05d}_.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_time_series_per_station_subplots(swl, st_id, st_time=None, en_time=None, img_dir=None, sim_start_freq_hours=24,
                                          station_dict=default_params.station_dict,
                                          sim_label=""):
    fig = plt.figure(figsize=(8, 6))
    gs = GridSpec(2, 1)

    # detided data
    st_sel = dict(list(swl.groupby("station_id")))[st_id]

    st_sel = st_sel[st_sel[io_manager.VALIDH_COL_NAME] <= sim_start_freq_hours]
    st_sel.sort_values(io_manager.VALIDH_COL_NAME, inplace=True)
    g = st_sel.set_index(io_manager.TIME_COL_NAME)
    g["diff"] = g["obs"][:] - g["mod"][:]
    # Take into account cases when dates are not in whole hours
    g = g.resample("60T", base=g.index[0].minute).asfreq()

    # ===== plotting
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(st_time, en_time)
    g.plot(y=["mod", "obs"], legend=False, color=["r", "k"], ax=ax)

    ax.legend(title=station_dict[st_id], handles=[
        Line2D([0], [0], color="k", label=r"$\eta_{obs} - \eta_{T}$"),
        Line2D([0], [0], color="r", label=r"$\eta_{S}$"),
    ])
    ax.set_title(sim_label)

    ax = fig.add_subplot(gs[1, 0], sharex=ax)
    label = r"$\eta_{obs} - \eta_{T} - \eta_{S}$"
    g.plot(y="diff",
           label=label,
           ax=ax,
           color="k",
           legend=False)

    ax.legend(title=station_dict[st_id], handles=[
        Line2D([0], [0], color="k", label=label),
    ])

    plt.savefig(str(img_dir / f"subplots_{st_id:05d}.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    plt.close(ax.figure)



def rdsps_panal_levelling_vs_nolevelling(station_dict=default_params.station_dict):
    # Plotting period
    st_time = datetime(2016, 12, 24)
    en_time = datetime(2017, 2, 28)

    detiding_plots_dir = Path(f"data/plots/detiding_comparisons_H17YY15NWPH8A_vs_experimental/{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}_ts")
    if not detiding_plots_dir.is_dir():
        detiding_plots_dir.mkdir(parents=True, exist_ok=True)

    labels = []
    colors = []
    data = []


    swl_path = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_pseudo-analysis_experimental_2016121500_2017123118_v03/surge_rdsps_pseudo-analysis_experimental.dat"
    swl = io_manager.read_wl_station_data(swl_path, station_dict=station_dict)
    data.append(swl)
    labels.append("RDSPS experimental")
    colors.append("b")

    swl_path = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_pseudo-analysis_H17YY15NWPH8A_2016121500_2017123118_v03/surge_rdsps_pseudo-analysis_H17YY15NWPH8A.dat"
    swl = io_manager.read_wl_station_data(swl_path, station_dict=station_dict)
    data.append(swl)
    labels.append("RDSPS H17YY15NWPH8A")
    colors.append("r")

    for st_id in station_dict:
        plot_time_series_per_station_subplots_multiple_sims(data, st_id,
                                              st_time=st_time,
                                              en_time=en_time,
                                              img_dir=detiding_plots_dir,
                                              sim_labels=labels, sim_colors=colors)



def rdsps_panal_H17YY15NWPH8A_vs_experimental(station_dict=default_params.station_dict):
    # Plotting period
    st_time = datetime(2016, 12, 24)
    en_time = datetime(2017, 2, 28)

    detiding_plots_dir = Path(f"data/plots/detiding_comparisons_H17YY15NWPH8A_vs_experimental/{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}_ts")
    if not detiding_plots_dir.is_dir():
        detiding_plots_dir.mkdir(parents=True, exist_ok=True)

    labels = []
    colors = []
    data = []


    swl_path = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_pseudo-analysis_experimental_2016121500_2017123118_v03/surge_rdsps_pseudo-analysis_experimental.dat"
    swl = io_manager.read_wl_station_data(swl_path, station_dict=station_dict)
    data.append(swl)
    labels.append("RDSPS experimental")
    colors.append("b")

    swl_path = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_pseudo-analysis_H17YY15NWPH8A_2016121500_2017123118_v03/surge_rdsps_pseudo-analysis_H17YY15NWPH8A.dat"
    swl = io_manager.read_wl_station_data(swl_path, station_dict=station_dict)
    data.append(swl)
    labels.append("RDSPS H17YY15NWPH8A")
    colors.append("r")

    for st_id in station_dict:
        plot_time_series_per_station_subplots_multiple_sims(data, st_id,
                                              st_time=st_time,
                                              en_time=en_time,
                                              img_dir=detiding_plots_dir,
                                              sim_labels=labels, sim_colors=colors)


def rdsps_panal_H17YY15NWPH8A(station_dict=default_params.station_dict):
    # Plotting period
    st_time = datetime(2016, 12, 24)
    en_time = datetime(2017, 2, 28)

    detiding_plots_dir = Path(f"data/plots/detiding_comparisons_H17YY15NWPH8A/{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}_chunks_v03")
    if not detiding_plots_dir.is_dir():
        detiding_plots_dir.mkdir(parents=True, exist_ok=True)

    swl_path = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_pseudo-analysis_experimental_2016121500_2017123118_v03/surge_rdsps_pseudo-analysis_experimental.dat"
    swl = io_manager.read_wl_station_data(swl_path, station_dict=station_dict)

    for st_id in station_dict:
        plot_time_series_per_station_subplots(swl, st_id,
                                              st_time=st_time,
                                              en_time=en_time,
                                              img_dir=detiding_plots_dir,
                                              sim_label="RDSPS experimental")


def rdsps_panal_experimental(station_dict=default_params.station_dict):
    # Plotting period
    st_time = datetime(2016, 12, 24)
    en_time = datetime(2017, 2, 28)

    detiding_plots_dir = Path(f"data/plots/detiding_comparisons_experimental/{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}_chunks_v03")
    if not detiding_plots_dir.is_dir():
        detiding_plots_dir.mkdir(parents=True, exist_ok=True)

    swl_path = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_pseudo-analysis_experimental_2016121500_2017123118_v03/surge_rdsps_pseudo-analysis_experimental.dat"
    swl = io_manager.read_wl_station_data(swl_path, station_dict=station_dict)

    for st_id in station_dict:
        plot_time_series_per_station_subplots(swl, st_id,
                                              st_time=st_time,
                                              en_time=en_time,
                                              img_dir=detiding_plots_dir,
                                              sim_label="RDSPS experimental")




def main(station_dict=default_params.station_dict):
    # Plotting period
    st_time = datetime(2018, 6, 1)
    en_time = datetime(2018, 7, 1)

    detiding_plots_dir = Path(f"data/plots/detiding_comparisons/{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}_chunks_v01")
    if not detiding_plots_dir.is_dir():
        detiding_plots_dir.mkdir(parents=True, exist_ok=True)

    twl_obs_path = "/home/olh001/MATLAB/detide/data/obs_from_Natacha/Observations/tide_gauge/2018"
    twl = io_manager.read_wl_station_data(twl_obs_path, station_dict=station_dict)

    swl_path = "/home/olh001/MATLAB/detide/data/data_for_scoring_rdsps_parallel_2018042400_2018072000_v01/surge_rdsps_parallel.dat"
    swl = io_manager.read_wl_station_data(swl_path, station_dict=station_dict)

    for st_id in station_dict:
        plot_time_series_per_station_subplots(swl, st_id,
                                              st_time=st_time,
                                              en_time=en_time,
                                              img_dir=detiding_plots_dir,
                                              sim_label="RDSPS parallel")


if __name__ == '__main__':
    # main()
    # rdsps_panal_H17YY15NWPH8A()
    rdsps_panal_H17YY15NWPH8A_vs_experimental()
