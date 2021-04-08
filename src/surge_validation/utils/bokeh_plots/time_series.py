
"""
Timeseries plots with zoom capability
"""
import logging
from collections import OrderedDict
from datetime import timedelta
from pathlib import Path

from bokeh.colors import RGB
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from matplotlib import colors

from surge_validation.detiding_validation import io_manager
from surge_validation.detiding_validation.config import default_params
from surge_validation.utils.log_utils import get_logger

import bokeh.plotting as bpl
import pandas as pd

from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from bokeh.models.widgets import NumberFormatter

from surge_validation.utils.strutils import stname_to_fname2


def convert_mpl_colors_to_bokeh_rgb(mpl_colors):
    res = []
    for c in mpl_colors:
        c = colors.to_rgba(c)
        c_b = [int(cv * 255) for cv in c[:3]]
        a = 1
        if len(c) == 4:
            a = c[-1]
        res.append(RGB(*c_b, a=a))
    return res


def plot_time_series_for_station_many_models(swl_list, st_id, label_to_scores=None, station_dict=default_params.station_dict,
                                             st_time=None, en_time=None, img_dir=None, model_label_list=(),
                                             model_colors=("b", "r"),
                                             run_freq_hours=6, ylim=None, linewidth=1, member_id="",
                                             remove_ndays_mean=None):
    """
    :param label_to_scores: labels to scores, if provided will be shown in a table
    :param remove_ndays_mean: before plotting n-day mean is removed (rolling)
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

    logger = get_logger(__name__)

    # make lines in bokeh wider
    linewidth = linewidth * 5

    if isinstance(run_freq_hours, int):
        run_freq_hours = {label: run_freq_hours for label in model_label_list}

    st_name = station_dict.get(st_id, "")

    model_colors = convert_mpl_colors_to_bokeh_rgb(model_colors)

    model_label_to_color = OrderedDict(zip(model_label_list, model_colors))
    model_label_to_series = OrderedDict()

    # Select and plot obs on top of the model data
    st_sel_obs = swl_list[0][swl_list[0][io_manager.STID_COL_NAME] == st_id].copy()
    st_sel_obs = st_sel_obs[st_sel_obs[io_manager.VALIDH_COL_NAME] <= run_freq_hours[model_label_list[0]]]
    st_sel_obs.sort_values([io_manager.TIME_COL_NAME, io_manager.VALIDH_COL_NAME], inplace=True)
    st_sel_obs.drop_duplicates(subset=io_manager.TIME_COL_NAME, keep="last", inplace=True)
    st_sel_obs.set_index(io_manager.TIME_COL_NAME, inplace=True)
    st_sel_obs = st_sel_obs.asfreq("60T")["obs"]

    if len(st_sel_obs) == 0:
        logger.warn(f"No obs data for {st_id}, skipping it.")
        return {}

    out_plot = img_dir / "interactive" / f"{st_id}_{stname_to_fname2(station_dict[st_id])}.html"



    out_plot.parent.mkdir(exist_ok=True, parents=True)
    bpl.output_file(str(out_plot),  title=f"{st_name} ({st_id})")
    p = bpl.figure(sizing_mode="stretch_both", x_axis_type="datetime")

    for swl, model_label in zip(swl_list, model_label_list):
        model_color = model_label_to_color[model_label]
        st_sel_mod = swl[swl[io_manager.STID_COL_NAME] == st_id].copy()
        st_sel_mod = st_sel_mod[st_sel_mod[io_manager.VALIDH_COL_NAME] <= run_freq_hours[model_label]]

        st_sel_mod.sort_values([io_manager.TIME_COL_NAME, io_manager.VALIDH_COL_NAME], inplace=True)
        st_sel_mod.drop_duplicates(subset=io_manager.TIME_COL_NAME, keep="last", inplace=True)

        if len(st_sel_mod) == 0:
            logger.warning(f"No model data data for {st_id}, skipping")
            continue

        st_sel_mod.set_index(io_manager.TIME_COL_NAME, inplace=True)
        to_plot = st_sel_mod.asfreq("60T")["mod" + member_id]

        if remove_ndays_mean is not None:
            to_plot = to_plot - to_plot.rolling(timedelta(days=remove_ndays_mean)).mean()

        p.line(pd.to_datetime(to_plot.index), to_plot.values, color=model_color, legend_label=model_label,
               line_width=linewidth)

        model_label_to_series[model_label] = to_plot

        # remove n-day rolling mean
    if remove_ndays_mean is not None:
        to_plot = st_sel_obs - st_sel_obs.rolling(timedelta(days=remove_ndays_mean)).mean()
    else:
        to_plot = st_sel_obs

    p.line(pd.to_datetime(to_plot.index), to_plot.values, color="black",  line_width=linewidth, legend_label="Obs")
    model_label_to_series["obs"] = st_sel_obs

    same_mod = len(set(model_label_list)) == 1

    p.legend.click_policy = "hide"

    # draw a table if necessary
    if label_to_scores is not None:

        systems = list(label_to_scores)
        scores = list(label_to_scores[systems[0]])

        data = {
            "system": systems,
        }

        data.update(
            {score: [label_to_scores[lbl][score] for lbl in systems] for score in scores}
        )

        source = ColumnDataSource(data)

        def __get_formatter(key):
            if key == "system":
                return None
            else:
                return NumberFormatter(format="0[.]00000")

        columns = [
            TableColumn(field=key, title=key, formatter=__get_formatter(key)) for key in data
        ]
        data_table = DataTable(columns=columns, source=source)
        p = column(p, data_table, sizing_mode="stretch_both")

    bpl.save(p)
