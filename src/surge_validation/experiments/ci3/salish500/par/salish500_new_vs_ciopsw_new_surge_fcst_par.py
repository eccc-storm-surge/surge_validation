"""
"""
import logging
from collections import OrderedDict
from pathlib import Path

from cartopy.crs import LambertConformal

from surge_validation import io_manager
from surge_validation.config import default_params
from datetime import datetime
import pandas as pd

from surge_validation.experiments.validation_experiment_base import compare_forecast



# generalized plotting to several simulations
from surge_validation.utils import log_utils


def fc(station_dict=default_params.station_dict,
       st_date=None,
       en_date=None,
       exp_id="NOT_SET"):

    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    inp_data_root = Path("/home/olh001/Python/loadprogs_python_experiments/data/ci3/")

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    label = f"{exp_id}_{st_s}_{en_s}"
    img_dir = Path(f"data/plots/ci3_seasonal_cycles/ciopsw/{label}")

    exp_id_to_path = OrderedDict([
        ("CIOPSW (FCST-REF, Surge)",
            next((inp_data_root / "ciopsw/par").rglob(f"data_for_scoring_*ciopsw*_ref_*blend_surge_{st_s}_{en_s}/surge*.dat"))),
        ("CIOPSW (FCST-NEW, Surge)",
            next((inp_data_root / "ciopsw/par").rglob(f"data_for_scoring_*ciopsw*_new_*blend_surge_{st_s}_{en_s}/surge*.dat"))),
        ("SALISH500 (FCST-NEW, Surge)",# data_for_scoring_salish500_new_par_blend_surge_2021080500_2021092600
            next((inp_data_root / "ciopsw/ss500/par").rglob(f"data_for_scoring_*salish500*_new_*par_blend_surge_*{st_s}_{en_s}/surge*.dat"))),
    ])

    exp_id_labels = list(exp_id_to_path)

    b2b_nhours = {
        lbl: 25 for lbl in exp_id_labels
    }

    score_plots_params = {
        "forecast_hour_tick_multiplier": 6,
        "max_lead_hour": 49,
        "min_lead_hour": 1,
        "agg_hours": [0, 12],
        "single_panel_figsize": (7.5, 5.5)
    }

    b2b_split_seasons = {
        f"{t:%b}": (t.month, ) for t in pd.date_range(st_date, en_date, freq="m")
    }

    options = {
        "do_full_forecast_timeseries": False,
        "calculate_scores": True,
        "do_b2b_timeseries": True,
        "b2b_split_seasons": b2b_split_seasons,
        "score_map_figsize": (16, 10),
        "score_map_marker_size": 80,
        "score_map_colorbar_fraction": "8%",
        "score_map_fontsize": 13,
        "score_map_projection":  LambertConformal(),
        "score_map_colorbar_position": "right",
        "plot_spectra": True,
        "plot_tide_constituents": True,
        "min_lead_hour": 1,
        # number of forecasts to ignore to avoid transients from filtering
        default_params.OptionNames.IGNORE_EDGE_FORECASTS: {
            "beg": 3,
            "end": 6
        }

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
                     options=options, st_time=st_date, en_time=en_date,
                     b2b_cutoff_hours=None)


def main():
    # forecast
    # st_date = datetime(2017, 1, 1, 0)
    # en_date = datetime(2017, 12, 31, 18)

    st_date = datetime(2021, 8, 5, 0)
    en_date = datetime(2021, 9, 26, 0)
    EXP_ID = "SALISH500_NEW_vs_CIOPSW_NEW_FCST_PAR_BLEND_SURGE_blueredgreen"

    logger = log_utils.get_logger(__name__)
    logger.info("Running %s for %s -- %s", EXP_ID, st_date, en_date)
    station_dict = default_params.station_dict.copy()
    fc(station_dict=station_dict, st_date=st_date, en_date=en_date, exp_id=EXP_ID)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
