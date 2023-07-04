import logging
from collections import OrderedDict
from pathlib import Path

import matplotlib
# matplotlib.use('agg')
from matplotlib.artist import Artist

from surge_validation.config import default_params
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MultipleLocator, NullLocator

from surge_validation import io_manager
from .qq_plot import qqplot
from surge_validation.verification_stats.calc_stats_with_obs import stde, gamma, stde_obs, gamma_varobsallvhour
from surge_validation.verification_stats import calc_stats_with_obs
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

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


def plot_scores_generalize(ax, lbl_to_series: dict,
                           lbl_to_color: dict,
                           col_name, shared_ax=None,
                           title="", show_avg_diff=True,
                           ylimits=None):
    """
    Plot scores as function of forcast hour
    :param ylimits:
    :param lbl_to_color:
    :param lbl_to_series: Ordered dict {label: data}
    :param show_avg_diff: True/False whether show or not the average difference between the models
    :param ax:
    :param old_series:
    :param new_series:
    :param col_name:
    :param shared_ax:
    :param title:
    """

    plotted_labels = []
    info_top_right = 0.99

    renderer = None
    for idx, (lbl, series) in enumerate(lbl_to_series.items()):

        if lbl in plotted_labels:
            logger.info(f"Already plotted timeseries for {lbl}, skipping!")
            continue

        color = lbl_to_color[lbl]
        ax = series.plot(y=col_name, legend=False,
                         color=color,
                         lw=2,
                         ax=ax,
                         sharex=shared_ax, sharey=None,
                         rot=45, label=lbl, ylim=ylimits)

        # check if confidence intervals are present, plot them if they are
        cname_ci_min = None
        cname_ci_max = None
        for cname in series.columns:
            if cname.endswith(f"{col_name}_ci_min"):
                cname_ci_min = cname
            elif cname.endswith(f"{col_name}_ci_max"):
                cname_ci_max = cname

        if cname_ci_min is not None:
            ax.fill_between(series.index, series[cname_ci_min], series[cname_ci_max], alpha=0.1, color=color)
            logger.info(f"Will show confidence intervals for: {lbl}, {col_name} ")
            # raise Exception

        # display averaged difference for all forecast hours if requested
        if show_avg_diff and idx > 0:
            diff = series - lbl_to_series[plotted_labels[0]]
            txt_artist = ax.text(0.99, info_top_right,
                                 f"$<\Delta>_t$: {diff[col_name].mean():.4f}",
                                 transform=ax.transAxes,
                                 ha="right", va="top",
                                 color=color)

            if renderer is None:
                ax.figure.canvas.draw()
                renderer = ax.figure.canvas.renderer

            assert isinstance(txt_artist, Artist)

            # get the bottom of the current label for the next one (in axes fraction units)
            info_top_right = ax.transAxes.inverted().transform(txt_artist.get_window_extent(renderer))[0, 1]

        plotted_labels.append(lbl)

    ax.set_title(title)
    return ax


def plot_scores(ax, old_series, new_series, col_name, shared_ax=None,
                title="", labels=None, show_avg_diff=True, ylimits=None):
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
                    rot=45, label=labels["old"], ylim=ylimits)

    if labels["new"] != labels["old"]:

        new_series.plot(y=col_name, legend=False, color=default_params.COLOR_NEW, lw=0.5,
                        ax=ax,
                        sharex=shared_ax, sharey=None,
                        rot=45, label=labels["new"], ylim=ylimits)

        # display averaged difference for all forecast hours if requested
        if show_avg_diff:
            ax.text(0.99, 0.99, f"<new-old>$_t$: {(new_series - old_series)[col_name].mean():.4f}",
                    transform=ax.transAxes, ha="right", va="top")
    else:
        logger.info(f"Labels are the same, plotting just 1 line")

    return ax


def compare_n_simulations(lbl_to_data: dict, lbl_to_color: dict, img_dir,
                          station_dict=default_params.station_dict,
                          member_id="",
                          select_stations=None, n_subplot_cols=4,
                          custom_rc_params=None,
                          show_avg_diff=True,
                          qq_lead_hour_range=range(244),
                          confidence_level=0.9,
                          score_plots_params=None):

    logging.info("Start compare_n_simulations ...")

    if score_plots_params is None:
        score_plots_params = {}

    forecast_hour_tick_multiplier = score_plots_params["forecast_hour_tick_multiplier"]
    max_lead_hour = score_plots_params.get("max_lead_hour", None)
    min_lead_hour = score_plots_params.get("min_lead_hour", None)

    nbootstrap_default = 100

    if custom_rc_params is None:
        custom_rc_params = {}

    img_dir.mkdir(exist_ok=True, parents=True)

    # select only up to the lead hour required
    if max_lead_hour is not None:
        lbl_to_data = {key: data[data[io_manager.VALIDH_COL_NAME] <= max_lead_hour]
                       for key, data in lbl_to_data.items()}

    if min_lead_hour is not None:
        lbl_to_data = {key: data[data[io_manager.VALIDH_COL_NAME] >= min_lead_hour]
                       for key, data in lbl_to_data.items()}


    # set font size
    # if custom_rc_params is None:
    #     matplotlib.rcParams.update({'font.size': 5})
    # else:
    #     matplotlib.rcParams.update(custom_rc_params)

    # TODO: add a flag to be able to disable qqplots

    logger.debug(list(lbl_to_data.keys()))

    for lead in qq_lead_hour_range:
        qqplot(
            label_to_dataframe=lbl_to_data, label_to_color=lbl_to_color,
            station_dict=station_dict,
            plot_params=custom_rc_params, n_subplot_cols=n_subplot_cols,
            img_dir=img_dir,
            lead_h_min=lead, lead_h_max=lead
        )

    if not img_dir.exists():
        img_dir.mkdir(parents=True, exist_ok=True)

    # clean image direcrotry
    for f in img_dir.rglob("*"):
        if f.is_file():
            f.unlink()

    statname_to_disp = {
        "stde": r"$\sigma_{\varepsilon}$ (m)",
        "gamma": r"$\gamma^2$",
        "stde_obs": r"$\sigma_{Obs}$ (m)",
        "gamma_varobsallvhour": r"$\gamma^2_{adj}$",
        "mean_error_PmO": r"ME(P-O)",
        "rmse": r"RMSE/EQM",
    }

    if member_id is None or len(member_id) == 0:
        member_id = 0

    stids_not_overall = default_params.ignore_in_overall
    xlims = None
    all_axes_except_last = []

    data_any = next(v for v in lbl_to_data.values())

    stats_functions = {
        "_stde": stde,
        "_gamma": gamma,
        "_stde_obs": stde_obs,
        "_gamma_varobsallvhour": gamma_varobsallvhour,
        "_mean_error_PmO": calc_stats_with_obs.mean_error_PmO,
        "_rmse": calc_stats_with_obs.rmse
    }

    conf_level_pcnt = confidence_level * 100
    alpha_ci = 1 - confidence_level
    stats_functions_params = {
        "_stde": {"nbootstrap": nbootstrap_default,
                  "alpha_ci": alpha_ci,
                  "legend_title": f"{conf_level_pcnt}% conf. interval"},
        "_gamma": {"nbootstrap": nbootstrap_default,
                   "alpha_ci": alpha_ci,
                   "legend_title": f"{conf_level_pcnt}% conf. interval"},
        "_stde_obs": {},
        "_gamma_varobsallvhour": {"nbootstrap": nbootstrap_default,
                                  "alpha_ci": alpha_ci,
                                  "legend_title": f"{conf_level_pcnt}% conf. interval"},
        "_mean_error_PmO": {"nbootstrap": nbootstrap_default,
                  "alpha_ci": alpha_ci,
                  "legend_title": f"{conf_level_pcnt}% conf. interval"},
        "_rmse": {"nbootstrap": nbootstrap_default,
                  "alpha_ci": alpha_ci,
                  "legend_title": f"{conf_level_pcnt}% conf. interval"},
    }

    member_col_index = 0
    current_station_ids = data_any["station_id"].drop_duplicates()
    for suffix, afunc in stats_functions.items():
        col_names = io_manager.get_model_column_names(data_any, suffix=suffix)

        lbl_to_stats = OrderedDict([
            (lbl, afunc(data, stids_not_overall=stids_not_overall, **stats_functions_params[suffix]))
                for lbl, data in lbl_to_data.items()
        ])

        # determine number of rows in the panel plot
        if select_stations is None:
            nsubplots = 1 + len(current_station_ids)
        else:
            nsubplots = 1 + len([cid for cid in current_station_ids if cid in select_stations])

        nrows = nsubplots // n_subplot_cols + int(nsubplots % n_subplot_cols != 0)

        panel_width, panel_height = score_plots_params.get("single_panel_figsize", (7.5, 5.5))
        fig = plt.figure(figsize=(panel_width * n_subplot_cols, panel_height * nrows), dpi=96)
        gs = GridSpec(nrows, n_subplot_cols, top=0.90, wspace=0.4)
        shared_ax = None

        logger.debug(current_station_ids)
        logger.debug("number of stations to process = {}".format(len(current_station_ids)))
        logger.debug(f"Subplots: nrows={nrows}, ncols={n_subplot_cols}")

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

            if len(col_names) > 1:
                logging.warning(f"Using member: {col_names[member_col_index]}")

            logger.debug(f"i={i}, st_id={st_id}")

            # get stats for the current station, hence stats[0]
            lbl_to_series = OrderedDict([
                (lbl, stats[0].xs(st_id, level="station_id")) for lbl, stats in lbl_to_stats.items()
            ])

            plot_scores_generalize(ax, lbl_to_series=lbl_to_series,
                                   lbl_to_color=lbl_to_color,
                                   col_name=col_names[member_col_index],
                                   shared_ax=shared_ax,
                                   title=f"{st_name} ({st_id})",
                                   show_avg_diff=show_avg_diff)

            style_axes(ax, locator_base=forecast_hour_tick_multiplier)
            all_axes_except_last.append(ax)
            i += 1

        # add overall stats plot
        i = nsubplots - 1
        row, col = plot_index_to_row_col(i, n_subplot_cols)
        ax = fig.add_subplot(gs[row, col])

        # get stats for all stations
        lbl_to_series = OrderedDict([
            (lbl, stats[1]) for lbl, stats in lbl_to_stats.items()
        ])

        plot_scores_generalize(ax, lbl_to_series=lbl_to_series,
                               lbl_to_color=lbl_to_color,
                               col_name=col_names[member_col_index],
                               shared_ax=shared_ax,
                               title="All stations",
                               show_avg_diff=show_avg_diff)

        style_axes(ax, locator_base=forecast_hour_tick_multiplier)

        legend_title = stats_functions_params[suffix].get("legend_title", None)
        ax.legend(loc="upper right", bbox_to_anchor=(1, -0.4),
                  borderaxespad=0.,
                  title=legend_title)

        # get min/max origin times for titles
        t_origin = data_any[io_manager.DATEO_COL_NAME]
        st_time = t_origin.min()
        en_time = t_origin.max()

        period_s = f"{st_time:%Y%m%d%H}-{en_time:%Y%m%d%H}"
        fig.suptitle(f"{statname_to_disp[suffix[1:]]}, {period_s}")

        if max_lead_hour is not None:
            img_file = img_dir / f"{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}{suffix}_max_lead_{max_lead_hour}.pdf"
        else:
            img_file = img_dir / f"{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}{suffix}.pdf"

        fig.savefig(str(img_file), bbox_inches="tight", transparent=True)

        # save for overall stats into a separate file
        fig = plt.figure(figsize=score_plots_params.get("single_panel_figsize", (5, 3)), dpi=96)
        ax = fig.gca()

        plot_scores_generalize(ax, lbl_to_series=lbl_to_series,
                               lbl_to_color=lbl_to_color,
                               col_name=col_names[member_col_index], shared_ax=None,
                               title="All stations",
                               show_avg_diff=show_avg_diff,
                               ylimits=default_params.vname_to_limits[suffix[1:]])

        style_axes(ax, locator_base=forecast_hour_tick_multiplier)
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1), 
                  title=stats_functions_params[suffix].get("legend_title", None))
        fig.suptitle(f"{statname_to_disp[suffix[1:]]}, {period_s}")

        if max_lead_hour is not None:
            img_file = img_dir / f"all_stations_{suffix[1:]}_max_lead_{max_lead_hour}.pdf"
        else:
            img_file = img_dir / f"all_stations_{suffix[1:]}.pdf"

        fig.savefig(img_file, bbox_inches="tight", transparent=True)
        plt.close(fig)

    logging.info("Finished compare_n_simulations ...")


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

    t_origin = swl_old[io_manager.TIME_COL_NAME] - pd.TimedeltaIndex(swl_old[io_manager.TIME_COL_NAME], unit="hour")
    period_s = f"{t_origin.min():%Y%m%d%H}-{t_origin.max():%Y%m%d%H}"


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
        gs = GridSpec(nrows, n_subplot_cols, top=0.90, wspace=0.4)
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

        fig.suptitle(f"{statname_to_disp[suffix[1:]]}, {period_s}")
        st_time = swl_old[io_manager.TIME_COL_NAME].min()
        en_time = swl_old[io_manager.TIME_COL_NAME].max()

        if max_lead_hour is not None:
            img_file = img_dir / f"{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}{suffix}_max_lead_{max_lead_hour}.png"
        else:
            img_file = img_dir / f"{st_time:%Y%m%d%H}_{en_time:%Y%m%d%H}{suffix}.png"

        fig.savefig(str(img_file), bbox_inches="tight")

        # save for overall stats into a separate file
        fig = plt.figure(figsize=(5, 5))
        ax = fig.gca()

        plot_scores(ax, old_series, new_series, col_name=col_names[member_col_index], shared_ax=None,
                    title="All stations", labels=labels, show_avg_diff=show_avg_diff,
                    ylimits=default_params.vname_to_limits[suffix[1:]])

        style_axes(ax, locator_base=forecast_hour_tick_multiplier)
        ax.legend(loc="upper left")
        fig.suptitle(f"{statname_to_disp[suffix[1:]]}, {period_s}")

        if max_lead_hour is not None:
            img_file = img_dir / f"all_stations_{suffix[1:]}_max_lead_{max_lead_hour}.pdf"
        else:
            img_file = img_dir / f"all_stations_{suffix[1:]}.pdf"

        fig.savefig(img_file, bbox_inches="tight", transparent=True)
        plt.close(fig)

    logging.info("Finished compare_2_simulations ...")


def aggregate_in_time(lbl_to_data, agg_hours=0):
    """
    assign data within [vh-agg_hours, vh+agg_hours] to correspond to vh.

    so that the valid hour changes
    from [0, 1, 2, 3, ...]
    to [agg_hours, 2 * agg_hours, 3 * agg_hours, ...]
    """

    if agg_hours == 0:
        return lbl_to_data

    res = OrderedDict()

    for lbl, data in lbl_to_data.items():

        df = data.copy()

        vh_orig = df[io_manager.VALIDH_COL_NAME]

        df.loc[:, io_manager.VALIDH_COL_NAME] = (df.loc[:, io_manager.VALIDH_COL_NAME] // agg_hours) * agg_hours

        max_vh = (vh_orig.max() // agg_hours) * agg_hours

        # select so that each interval is represented by the same number of points (the rest is discarded)
        df = df[df[io_manager.VALIDH_COL_NAME] < max_vh]

        if len(df) == 0:
            logger.info(f"Not doing aggregated scores for {lbl}, not enough data")
            continue
        
        res[lbl] = df

    return res


def get_b2b_timeseries(lbl_to_data: dict, b2b_nhours: dict, min_valid_hour=0):
    """
    convert data to timeseries by removing overlapping sections
    :param min_valid_hour: minimum valid hour to consider for concatenation (inclusive)
    :param lbl_to_data:
    :param n_b2b_hours:

    :returns {label: {stationid: timeseries}}
    """

    lbl_to_station_to_ts = {}

    for lbl, exp_data in lbl_to_data.items():
        lbl_to_station_to_ts[lbl] = {}
        for st_id, st_data in exp_data.groupby(io_manager.STID_COL_NAME):
            ts = st_data[st_data[io_manager.VALIDH_COL_NAME] < b2b_nhours[lbl]].sort_values(io_manager.TIME_COL_NAME)
            ts = ts[ts[io_manager.VALIDH_COL_NAME] >= min_valid_hour]
            ts = ts.drop_duplicates(subset=io_manager.TIME_COL_NAME, keep="first").set_index(io_manager.TIME_COL_NAME)
            lbl_to_station_to_ts[lbl][st_id] = ts

    return lbl_to_station_to_ts


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
