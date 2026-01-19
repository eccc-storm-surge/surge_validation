"""
= GDSPS ===============
"""
import logging
from collections import OrderedDict
from pathlib import Path

from cartopy.crs import Robinson

from surge_validation import io_manager
from surge_validation.config import default_params
from datetime import datetime
import pandas as pd

from surge_validation.config.default_params import OptionNames
from surge_validation.experiments.validation_experiment_base import compare_forecast

# EXP_ID = "GDSPS_vs_RDSPS_FC_FCH2020_V3"
from surge_validation.utils import log_utils


# generalized plotting to several simulations

def fc(station_dict=default_params.station_dict,
       st_date=None,
       en_date=None, exp_id="NOT_SET"):

    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    inp_data_root = Path("/home/olh001/Python/loadprogs_python_experiments/data/gdsps/ci4-snd/prog/")

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    label = f"{exp_id}_{st_s}_{en_s}"
    img_dir = Path(f"data/plots/gdps-sn-ai/GDSPS/final_cycles/{label}")

    exp_id_to_path = {
        "GDSPS (CI4, TWL)":  next(inp_data_root.rglob(f"data_for_scoring_gdsps_prog_global_twl_ci4_{st_s}_{en_s}/surge*.dat")),
        "GDSPS (SNAI, TWL)": next(inp_data_root.rglob(f"data_for_scoring_gdsps_prog_global_twl_snd_{st_s}_{en_s}/surge*.dat"))
    }

    exp_id_labels = list(exp_id_to_path)

    b2b_nhours = {
        lbl: 36 for lbl in exp_id_labels
    }

    score_plots_params = {
        "forecast_hour_tick_multiplier": 24,
        "max_lead_hour": 240,
        "min_lead_hour": 0,
        "agg_hours": [0, 12],
        "single_panel_figsize": (7.5, 5.5),
        "do_subplots_per_station": True
    }

    b2b_split_seasons = {
        f"{t:%b}": (t.month, ) for t in pd.date_range(st_date, en_date, freq="m")
    }

    options = {
        "do_full_forecast_timeseries": False,
        "calculate_scores": True,
        "do_b2b_timeseries": True,
        "b2b_split_seasons": {},
        "score_map_figsize": (20, 10),
        "score_map_marker_size": 20,
        "score_map_colorbar_fraction": "8%",
        "score_map_fontsize": 13,
        "score_map_projection":  Robinson(),
        "score_map_colorbar_position": "bottom",
        "plot_spectra": False,
        "plot_tide_constituents": False,
        # number of forecasts to ignore to avoid transients from filtering
        OptionNames.IGNORE_EDGE_FORECASTS: {
            "beg": 0,
            "end": 0
        },
        "nprocs": 20
    }

    default_params.vname_to_limits = {
        "stde": None,
        "gamma": None,
        "stde_obs": None,
        "gamma_varobsallvhour": None,
        "mean_error_PmO": None, 
        "rmse": None
    }

    # select only stations existing in both data files
    stid_list = io_manager.get_station_id_intersect(
        exp_id_to_path
    )
    station_dict = {sid: sname for sid, sname in station_dict.items() if sid in stid_list}

    compare_forecast(station_dict=station_dict, exp_id_to_path=exp_id_to_path,
                     exp_id_list=exp_id_labels,
                     img_dir=img_dir, qq_lead_hour_range=range(12, 12, 12),
                     b2b_nhours=b2b_nhours,
                     score_plots_params=score_plots_params,
                     options=options, st_time=st_date, en_time=en_date,
                     b2b_cutoff_hours=None)


def main():
    # forecast
    # st_date = datetime(2017, 1, 1, 0)
    # en_date = datetime(2017, 12, 31, 18)

    st_date = datetime(2022, 1, 1, 0)
    en_date = datetime(2022, 4, 9, 12)

    EXP_ID = "GDSPS_SNDAI_vs_GDSPS_CI4_PROG_TWL_GLOBAL"

    logger = log_utils.get_logger(__name__)
    logger.info("Running %s for %s -- %s", EXP_ID, st_date, en_date)

    obs_file = Path("/home/olh001/Python/obs_to_grid_mapping/gdsps/gdsps_global_uhslc_bathy65ts.obs")
    station_dict = io_manager.read_station_dict_from_obs(obs_file)

    # station_dict = OrderedDict([(k, station_dict[k]) for k in ["174", "370"]])
    station_dict = OrderedDict([(k, v) for k, v in station_dict.items() if k not in ["8"]])

    # for debug subset
    # station_dict_debug = OrderedDict()
    # for i, (k, v) in enumerate(station_dict.items()):
    #     if i % 10 == 0:
    #         station_dict_debug[k] = v
    # station_dict = station_dict_debug


    # evaluation entry point
    fc(station_dict=station_dict, 
       st_date=st_date, 
       en_date=en_date,
       exp_id=EXP_ID)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
