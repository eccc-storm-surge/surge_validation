"""
= CIOPS-E hindcast===============
Filtering tides in ciopse and obs for validation
"""
import logging
from collections import OrderedDict
from pathlib import Path
from surge_validation.detiding_validation.config import default_params
from datetime import datetime

from surge_validation.detiding_validation.experiments.FC70H17V2 import compare_forecast

EXP_ID = "RU22ROYE19_vs_REF"

station_dict = default_params.station_dict

# TODO: test to generalize plotting to several simulations


def fc(station_dict=default_params.station_dict,
       st_date=None,
       en_date=None):

    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    inp_data_root = Path("/home/olh001/Python/loadprogs_python_experiments/data/riops_ru_nov_2020")

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    label = f"{EXP_ID}_{st_s}_{en_s}"
    img_dir = Path(f"data/plots/{label}")

    exp_id_to_path = OrderedDict([
        ("REF (Surge)", inp_data_root / f"data_for_scoring_RU22REFE19_{st_s}_{en_s}" / "surge_RU22REFE19.dat"),
        ("RU22ROYE19 (Surge)", inp_data_root / f"data_for_scoring_RU22ROYE19_{st_s}_{en_s}" / "surge_RU22ROYE19.dat"),
    ])

    exp_id_labels = list(exp_id_to_path)

    b2b_nhours = {
        lbl: 24 for lbl in exp_id_labels
    }

    score_plots_params = {
        "forecast_hour_tick_multiplier": 6,
        "max_lead_hour": 24
    }

    b2b_split_seasons = {
        f"{t:%b}": (t.month, ) for t in [datetime(2001, m, 1) for m in range(6, 9)]
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

    st_date = datetime(2019, 6, 13, 0)
    en_date = datetime(2019, 8, 31, 0)

    fc(station_dict=station_dict, st_date=st_date, en_date=en_date)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
