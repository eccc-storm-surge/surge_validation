"""
= GDSPS ===============
"""
import logging
from collections import OrderedDict
from pathlib import Path

from cartopy.crs import LambertConformal

from surge_validation.detiding_validation import io_manager
from surge_validation.detiding_validation.config import default_params
from datetime import datetime
import pandas as pd

from surge_validation.detiding_validation.config.default_params import OptionNames
from surge_validation.detiding_validation.experiments.validation_experiment_base import compare_forecast

# EXP_ID = "GDSPS_vs_RDSPS_FC_FCH2020_V3"
from surge_validation.utils import log_utils


# Set your parameters inside main
def main():
    # forecast
    # st_date = datetime(2017, 1, 1, 0)
    # en_date = datetime(2017, 12, 31, 18)

    EXP_ID = "RESPS_NEW_vs_RESPS_REF_FCST_ETE2019_TWL"
    st_date = datetime(2019, 1, 1, 0)
    en_date = datetime(2020, 1, 1, 0)

    logger = log_utils.get_logger(__name__)
    logger.info("Running %s for %s -- %s", EXP_ID, st_date, en_date)

    station_dict = default_params.station_dict.copy()
    fc(station_dict=station_dict, st_date=st_date, en_date=en_date,
       exp_id=EXP_ID)


# generalized plotting to several simulations
def fc(station_dict=default_params.station_dict,
       st_date=None,
       en_date=None, exp_id="NOT_SET"):

    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    inp_data_root = Path("/home/olh001/Python/loadprogs_python_experiments/data/ci3/")

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    label = f"{exp_id}_{st_s}_{en_s}"
    img_dir = Path(f"data/plots/ci3_seasonal_cycles/resps/{label}")

    exp_id_to_path = OrderedDict([
        ("RESPS (FCST-REF, TWL)",
            next((inp_data_root / "resps").rglob(f"data_for_scoring_*resps*_twl_ref_*{st_s}_{en_s}/surge*.dat"))),
        ("RESPS (FCST-NEW, TWL)",
            next((inp_data_root / "resps").rglob(f"data_for_scoring_*resps*_twl_new_*{st_s}_{en_s}/surge*.dat"))),
    ])

    exp_id_labels = list(exp_id_to_path)

    b2b_nhours = {
        lbl: 36 for lbl in exp_id_labels
    }

    score_plots_params = {
        "forecast_hour_tick_multiplier": 24,
        "max_lead_hour": 360,
        "min_lead_hour": 0,
        "agg_hours": [0, 12],
        "confidence_level": 0.9,
        "single_panel_figsize": (7.5, 5.5)
    }

    b2b_split_seasons = {
        f"{t:%b}": (t.month, ) for t in pd.date_range(st_date, en_date, freq="m")
    }

    options = {
        "do_full_forecast_timeseries": True,
        "calculate_scores": True,
        "do_b2b_timeseries": True,
        "do_b2b_timeseries_interactive": True,
        "b2b_split_seasons": b2b_split_seasons,
        "score_map_figsize": (13.5, 8),
        "score_map_marker_size": 20,
        "score_map_colorbar_fraction": "8%",
        "score_map_fontsize": 13,
        "score_map_projection":  LambertConformal(),
        "score_map_colorbar_position": "right",
        "plot_spectra": True,
        "plot_tide_constituents": True,
        # number of forecasts to ignore to avoid transients from filtering
        OptionNames.IGNORE_EDGE_FORECASTS: None,
        # options for Talagrand plots
        OptionNames.DO_TALAGRAND_RANK_PLOTS: True,
        OptionNames.TALAGRAND_LEADS_LIST: [(0, 24), (48, 72), (96, 120), (144, 168)]

    }

    default_params.vname_to_limits = {
        "stde": None,
        "gamma": None,
        "stde_obs": None,
        "gamma_varobsallvhour": None
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
                     options=options,
                     st_time=st_date, en_time=en_date,
                     b2b_cutoff_hours=None,
                     member_id="000")


if __name__ == '__main__':
    main()
