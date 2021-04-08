#  ========== FC70H16V2 vs op (RDSPS, forecast) ===============
import logging
from collections import OrderedDict
from multiprocessing import Process
from pathlib import Path
from datetime import datetime

from surge_validation.detiding_validation import io_manager, surge_stats_entry
from surge_validation.detiding_validation.config.default_params import get_color_list
from surge_validation.spectral_plots import plot_power_spectra
from surge_validation.tidal_constituents import ttide_plot_amplitudes_and_phases_at_stations
from ..config import default_params
from ..maps.b2b_scores_scatter import plot_score_maps, save_scores_to_txt
from ..plot_timeseries_per_station import compare_sims_timeseries_back2back, compare_sims_timeseries_one_plot_per_fc
from ..surge_stats_entry import compare_2_simulations, compare_n_simulations
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

    exp_id_to_color = OrderedDict(zip(exp_id_to_path, get_color_list()))

    # read data into memory to be re-used
    lbl_to_data = OrderedDict([
        (lbl, io_manager.read_wl_station_data(path, station_dict=station_dict, max_lead_hour=None))
        for lbl, path in exp_id_to_path.items()
    ])

    if options.get("calculate_scores", True):
        # assign close hours to the same lead time +/- agg_hour
        agg_periods = score_plots_params.get("agg_hours", [0, ])

        for agg_hour in agg_periods:
            lbl_to_data_agg = surge_stats_entry.aggregate_in_time(lbl_to_data=lbl_to_data, agg_hours=agg_hour)
            agg_img_dir = img_dir / f"agg_{agg_hour}hrs"
            compare_n_simulations(lbl_to_data_agg, exp_id_to_color, agg_img_dir, station_dict=station_dict,
                                  forecast_hour_tick_multiplier=score_plots_params["forecast_hour_tick_multiplier"],
                                  max_lead_hour=score_plots_params.get("max_lead_hour", None),
                                  custom_rc_params=plot_params, n_subplot_cols=n_subplot_cols,
                                  qq_lead_hour_range=qq_lead_hour_range, show_avg_diff=len(np.unique(labels)) > 1,
                                  member_id=member_id, select_stations=list(station_dict))


    # plot time series

    # a) back to back
    if options.get("do_b2b_timeseries", True):
        if b2b_cutoff_hours is not None:
            b2b_cutoff_hours_token = f"_zoom_{b2b_cutoff_hours}h"
        else:
            b2b_cutoff_hours_token = ""

        split_seasons = options.get("b2b_split_seasons", {})

        if len(split_seasons) > 0:
            # sanity check
            months = []
            for season, mlist in split_seasons.items():
                months.extend(mlist)

            assert len(set(months)) == len(months), "Different seasons should not contain the same month!"

        ts_plots_dir = img_dir / f"timeseries_b2b_{b2b_cutoff_hours_token}"
        ts_plots_dir.mkdir(exist_ok=True, parents=True)

        # cleanup old plots
        for f in ts_plots_dir.rglob("*"):
            if f.is_file():
                f.unlink()

        station_scores, season_to_stid_to_score = compare_sims_timeseries_back2back(lbl_to_data, exp_id_to_color,
                                                                                    ts_plots_dir,
                                                                                    station_dict=station_dict,
                                                                                    st_time=st_time, en_time=en_time,
                                                                                    run_freq_hours=b2b_nhours,
                                                                                    linewidth=0.3,
                                                                                    b2b_cutoff_hours=b2b_cutoff_hours,
                                                                                    member_id=member_id,
                                                                                    split_seasons=split_seasons,
                                                                                    remove_ndays_mean=options.get("b2b_remove_ndays_mean", None))

        plot_score_maps(station_scores, labels, exp_id_to_path, img_dir=img_dir,
                        plot_params=options)

        save_scores_to_txt(station_scores, labels, img_dir)

        # plot score maps per season
        img_dir_season = img_dir / "seasonal_maps"
        img_dir_season.mkdir(exist_ok=True, parents=True)
        for season, scores in season_to_stid_to_score.items():
            plot_score_maps(scores, labels, exp_id_to_path,
                            img_dir=img_dir_season,
                            map_label=f"{season}",
                            plot_params=options)

    # b) full forecasts
    if options.get("do_full_forecast_timeseries", True):
        ts_plots_dir = img_dir / f"timeseries_complete_forecast"
        compare_sims_timeseries_one_plot_per_fc(labels, exp_id_to_path, exp_id_to_color,
                                                ts_plots_dir,
                                                station_dict=station_dict,
                                                st_time=st_time, en_time=en_time,
                                                linewidth=0.3, member_id=member_id)

    plot_spectra = options.get("plot_spectra", True)
    plot_tide_constituents = options.get("plot_tide_constituents", False)

    # prepare timeseries if any of the spectra or tide plots are requested
    lbl_to_station_to_ts = {}
    if plot_spectra or plot_tide_constituents:
        lbl_to_station_to_ts = surge_stats_entry.get_b2b_timeseries(lbl_to_data=lbl_to_data,
                                                                    b2b_nhours=b2b_nhours)

    # plot power spectra
    if plot_spectra:
        spectra_plots_dir = img_dir / "spectra"
        plot_power_spectra.plot_using_cross_spectra(img_dir=spectra_plots_dir,
                                                    lbl_to_station_to_ts=lbl_to_station_to_ts,
                                                    lbl_to_color=exp_id_to_color,
                                                    station_dict=station_dict)

    # plot constituents calculated using ttide
    if plot_tide_constituents:
        tide_plots_dir = img_dir / "ttide-analysis"
        ttide_plot_amplitudes_and_phases_at_stations.plot_ttide_tide_spectra(
            lbl_to_station_to_ts, img_dir=tide_plots_dir, lbl_to_color=exp_id_to_color,
            station_dict=station_dict
        )


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
