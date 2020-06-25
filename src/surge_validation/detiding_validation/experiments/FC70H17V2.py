#  ========== FC70H16V2 vs op (RDSPS, forecast) ===============
import logging
from collections import OrderedDict
from multiprocessing import Process
from pathlib import Path
from datetime import datetime

from ..config import default_params
from ..maps.b2b_scores_scatter import plot_score_maps
from ..plot_timeseries_per_station import compare_sims_timeseries_back2back, compare_sims_timeseries_one_plot_per_fc
from ..surge_stats_entry import compare_2_simulations
import numpy as np

EXP_ID = "FC70H17V2"
exp_label = f"rdsps_fc_{EXP_ID}"


def compare_forecast(station_dict=default_params.station_dict,
                     img_dir=None,
                     exp_id_to_path: dict = None,
                     exp_id_list=None, b2b_nhours=24,
                     n_subplot_cols=4, plot_params=None,
                     score_plots_params=None,
                     qq_lead_hour_range=range(1, 1, 5),
                     b2b_cutoff_hours=1000,
                     st_time=None, en_time=None, options=None,
                     member_id=""):
    """

    :param member_id:
    :param options: dictionary of some convenience options, should be True by default
    :param b2b_cutoff_hours:
    :param en_time:
    :param st_time:
    :param qq_lead_hour_range: lead hours for qq plots
    :param score_plots_params: dictionary of parameters for the score plots
    :param plot_params:
    :param n_subplot_cols:
    :param station_dict:
    :param img_dir:
    :param exp_id_to_path:
    :param exp_id_list:
    :param b2b_nhours: if negative, don't do the back to back series, if dict: b2b_nhours = {label: b2b_nhours}
    """

    if isinstance(b2b_nhours, int):
        b2b_nhours = {label: b2b_nhours for label in exp_id_list}

    if options is None:
        options = {
            "do_full_forecast_timeseries": True,
            "calculate_scores": True,
            "do_b2b_timeseries": True
        }

    if img_dir is None:
        img_dir = Path(f"data/plots/{exp_label}_{datetime.utcnow():%Y%m%d%H%M}")

    if score_plots_params is None:
        score_plots_params = {
            "forecast_hour_tick_multiplier": 24
        }

    if plot_params is None:
        plot_params = {
            "figure.figsize": (10, 14),
            "font.size": 8,
        }

    labels = [
        f"{exp_id}" for exp_id in exp_id_list
    ]

    swl_path_old, swl_path_new = [exp_id_to_path[exp_id] for exp_id in exp_id_list]

    if options.get("calculate_scores", True):
        compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                              label_old=labels[0],
                              label_new=labels[1],
                              forecast_hour_tick_multiplier=score_plots_params["forecast_hour_tick_multiplier"],
                              max_lead_hour=score_plots_params.get("max_lead_hour", None),
                              custom_rc_params=plot_params, n_subplot_cols=n_subplot_cols,
                              qq_lead_hour_range=qq_lead_hour_range, show_avg_diff=len(np.unique(labels)) > 1,
                              member_id=member_id, select_stations=list(station_dict))

    data_paths = OrderedDict(zip(labels, [swl_path_old, swl_path_new]))
    data_colors = OrderedDict(zip(labels, ["b", "r"]))

    # plot time series

    # a) back to back
    if options.get("do_b2b_timeseries", True):
        if b2b_cutoff_hours is not None:
            b2b_cutoff_hours_token = f"_zoom_{b2b_cutoff_hours}h"
        else:
            b2b_cutoff_hours_token = ""

        ts_plots_dir = img_dir / f"timeseries_b2b_{b2b_cutoff_hours_token}"
        ts_plots_dir.mkdir(exist_ok=True, parents=True)
        station_scores = compare_sims_timeseries_back2back(labels, data_paths, data_colors,
                                          ts_plots_dir,
                                          station_dict=station_dict,
                                          st_time=st_time, en_time=en_time,
                                          run_freq_hours=b2b_nhours, linewidth=0.3,
                                          b2b_cutoff_hours=b2b_cutoff_hours, member_id=member_id)

        plot_score_maps(station_scores, labels, data_paths, img_dir=img_dir)

    # b) full forecasts
    if options.get("do_full_forecast_timeseries", True):
        ts_plots_dir = img_dir / f"timeseries_complete_forecast"
        compare_sims_timeseries_one_plot_per_fc(labels, data_paths, data_colors,
                                                ts_plots_dir,
                                                station_dict=station_dict,
                                                st_time=st_time, en_time=en_time,
                                                linewidth=0.3, member_id=member_id)


def main():
    st_time = datetime(2016, 12, 25, 9)
    en_time = datetime(2017, 3, 10, 12)

    st_s = f"{st_time:%Y%m%d%H}"
    en_s = f"{en_time:%Y%m%d%H}"

    swl_path_old = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_op_during_{EXP_ID}_{st_s}_{en_s}/surge_rdsps_forecast_op_during_{EXP_ID}.dat"
    swl_path_new = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_{EXP_ID}_{st_s}_{en_s}/surge_rdsps_forecast_{EXP_ID}.dat"

    exp_id_list = ["op", EXP_ID]
    exp_id_store = {
        "op": swl_path_old, EXP_ID: swl_path_new
    }

    # img_dir = Path(f"data/plots/{exp_label}_{datetime.utcnow():%Y%m%d%H%M}")
    img_dir = Path(f"data/plots/{exp_label}_test")
    img_dir.mkdir(exist_ok=True, parents=True)

    compare_forecast(img_dir=img_dir, exp_id_list=exp_id_list, exp_id_to_path=exp_id_store,
                     b2b_nhours=24)


def main_36h():
    st_time = datetime(2016, 12, 25, 9)
    en_time = datetime(2017, 3, 10, 12)

    st_s = f"{st_time:%Y%m%d%H}"
    en_s = f"{en_time:%Y%m%d%H}"

    swl_path_old = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_op_during_{EXP_ID}_36h_{st_s}_{en_s}/surge_rdsps_forecast_op_during_{EXP_ID}_36h.dat"
    swl_path_new = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_{EXP_ID}_36h_{st_s}_{en_s}/surge_rdsps_forecast_{EXP_ID}_36h.dat"

    exp_id_list = ["op", EXP_ID]
    exp_id_store = {
        "op": swl_path_old, EXP_ID: swl_path_new
    }

    # img_dir = Path(f"data/plots/{exp_label}_{datetime.utcnow():%Y%m%d%H%M}")
    img_dir = Path(f"data/plots/{exp_label}_dev_36h")
    img_dir.mkdir(exist_ok=True, parents=True)

    compare_forecast(img_dir=img_dir, exp_id_list=exp_id_list, exp_id_to_path=exp_id_store,
                     b2b_nhours=36)


def main_36h_dc101():
    st_time = datetime(2016, 12, 25, 9)
    en_time = datetime(2017, 3, 10, 12)

    st_s = f"{st_time:%Y%m%d%H}"
    en_s = f"{en_time:%Y%m%d%H}"

    swl_path_old = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_{EXP_ID}_36h_{st_s}_{en_s}/surge_rdsps_forecast_{EXP_ID}_36h.dat"
    swl_path_new = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_{EXP_ID}_36h_dc101_{st_s}_{en_s}/surge_rdsps_forecast_{EXP_ID}_36h_dc101.dat"

    logging.basicConfig(level=logging.DEBUG)
    logging.info(f"Comparing\n (old): {swl_path_old}\n and \n(new): {swl_path_new}")

    exp_id_list = [EXP_ID, EXP_ID + "_dc101"]
    exp_id_store = {
        exp_id_list[0]: swl_path_old, exp_id_list[1]: swl_path_new
    }

    # img_dir = Path(f"data/plots/{exp_label}_{datetime.utcnow():%Y%m%d%H%M}")
    img_dir = Path(f"data/plots/{exp_label}_dev_36h_dc101")
    img_dir.mkdir(exist_ok=True, parents=True)

    compare_forecast(img_dir=img_dir,
                     exp_id_list=exp_id_list,
                     exp_id_to_path=exp_id_store,
                     b2b_nhours=36, )


if __name__ == '__main__':
    # main()
    # Process(target=main_36h).start()
    Process(target=main_36h_dc101).start()
