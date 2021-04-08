"""
= GDSPS ===============
"""
import logging
from collections import OrderedDict
from pathlib import Path

from surge_validation.detiding_validation import io_manager
from surge_validation.detiding_validation.config import default_params
from datetime import datetime

from surge_validation.detiding_validation.experiments.FC70H17V2 import compare_forecast

# EXP_ID = "GDSPS_vs_RDSPS_FC_FCH2020_V3"
EXP_ID = "GDSPS_vs_RDSPS_FC_FCH2020_testing"

station_dict = default_params.station_dict

# generalized plotting to several simulations


def fc(station_dict=default_params.station_dict,
       st_date=None,
       en_date=None):

    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    inp_data_root = Path("/home/olh001/Python/loadprogs_python_experiments/data/gdsps/")

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    label = f"{EXP_ID}_{st_s}_{en_s}"
    img_dir = Path(f"data/plots/{label}")

    exp_id_to_path = OrderedDict([
        ("RDSPS (FC, TWL)",
            next((inp_data_root / f"HIV2020_fc_V3").rglob("data_for_scoring_rdsps_FC_fc_H2020_cycles_twl_*")) / "surge_rdsps_FC_fc_H2020_cycles_twl_V3.dat"),
        ("GDSPS (FC, TWL)",
            next((inp_data_root / f"HIV2020_fc_V3").rglob("data_for_scoring_gdsps_FC_fc_H2020_cycles_twl_*")) / "surge_gdsps_FC_fc_H2020_cycles_twl_V3.dat"),
    ])

    exp_id_labels = list(exp_id_to_path)

    b2b_nhours = {
        lbl: 12 for lbl in exp_id_labels
    }

    score_plots_params = {
        "forecast_hour_tick_multiplier": 24,
        "max_lead_hour": 243,
        "agg_hours": [0, 12]
    }

    b2b_split_seasons = {
        f"{t:%b}": (t.month, ) for t in [datetime(2001, m, 1) for m in range(1, 3)]
    }

    options = {
        "do_full_forecast_timeseries": False,
        "calculate_scores": False,
        "do_b2b_timeseries": False,
        "b2b_split_seasons": b2b_split_seasons,
        "score_map_figsize": (14, 5.5),
        "score_map_marker_size": 12,
        "score_map_colorbar_fraction": "2%",
        "plot_spectra": False,
        "plot_tide_constituents": True
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

    st_date = datetime(2020, 1, 1, 0)
    en_date = datetime(2020, 2, 29, 12)

    fc(station_dict=station_dict, st_date=st_date, en_date=en_date)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
