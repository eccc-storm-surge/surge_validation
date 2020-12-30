"""
= CIOPS-E hindcast===============
Filtering tides in ciopse and obs for validation
"""
import logging
from collections import OrderedDict
from pathlib import Path

from surge_validation.detiding_validation import io_manager
from surge_validation.detiding_validation.config import default_params
from datetime import datetime

from surge_validation.detiding_validation.experiments.FC70H17V2 import compare_forecast

EXP_ID = "CC130E19V2_iceload_and_lowvisc_vs_REF"

station_dict = default_params.station_dict

# TODO: test to generalize plotting to several simulations


def fc(station_dict=default_params.station_dict,
       st_date=None,
       en_date=None):

    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    inp_data_root = Path("/home/olh001/Python/loadprogs_python_experiments/data/wcps_pa_dec_2020")

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    label = f"{EXP_ID}_{st_s}_{en_s}"
    img_dir = Path(f"data/plots/{label}")

    exp_id_to_path = OrderedDict([
        ("REF (PA, TWL)", next(inp_data_root.rglob(f"data_for_scoring_*_{st_s}_{en_s}/surge_CC130E19_REF.dat"))),
        ("CC130E19V2 (PA, TWL)", next(inp_data_root.rglob(f"data_for_scoring_*_{st_s}_{en_s}/surge_CC130E19V2.dat"))),
        ("CC130E19V3 (PA, TWL)", next(inp_data_root.rglob(f"data_for_scoring_*_{st_s}_{en_s}/surge_CC130E19V3.dat"))),
    ])

    print("Experiments to compare:")
    for k, pth in exp_id_to_path.items():
        print(f"{k} --> {pth}")

    exp_id_labels = list(exp_id_to_path)

    b2b_nhours = {
        lbl: 0 for lbl in exp_id_labels
    }

    score_plots_params = {
        "forecast_hour_tick_multiplier": 6,
        "max_lead_hour": 84
    }

    b2b_split_seasons = {
        f"{t:%b}": (t.month, ) for t in [datetime(2001, m, 1) for m in range(7, 9)]
    }

    options = {
        "do_full_forecast_timeseries": False,
        "calculate_scores": False,
        "b2b_split_seasons": b2b_split_seasons,
        # "b2b_remove_ndays_mean": 5
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
                     img_dir=img_dir, qq_lead_hour_range=range(1, 1, 1),
                     b2b_nhours=b2b_nhours,
                     score_plots_params=score_plots_params,
                     options=options, st_time=st_date, en_time=en_date,
                     b2b_cutoff_hours=None)


def main():
    # forecast
    # st_date = datetime(2017, 1, 1, 0)
    # en_date = datetime(2017, 12, 31, 18)

    st_date = datetime(2019, 7, 1, 0)
    en_date = datetime(2019, 8, 31, 0)

    fc(station_dict=station_dict, st_date=st_date, en_date=en_date)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
