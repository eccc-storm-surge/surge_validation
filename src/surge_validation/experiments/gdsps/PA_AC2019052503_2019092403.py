"""
= CIOPS-E hindcast===============
Filtering tides in ciopse and obs for validation
"""
import logging
from pathlib import Path
from surge_validation.config import default_params
from datetime import datetime

from surge_validation.experiments.validation_experiment_base import compare_forecast
import numpy as np
EXP_ID = "gdsps_AC201905_201909"


station_dict = default_params.station_dict


def fc(station_dict=default_params.station_dict, st_date=None, en_date=None):

    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    inp_data_root = Path("/home/olh001/Python/dev/loadprogs_python/data/gdsps/fc/")

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    label = f"{EXP_ID}_{st_s}_{en_s}"
    img_dir = Path(f"data/plots/{label}")

    swl_path_old = next(inp_data_root.rglob(f"*{st_s}*{en_s}*/surge*gdsps*twl*.dat"))
    swl_path_new = next(inp_data_root.rglob(f"*{st_s}*{en_s}*/surge*gdsps*twl*.dat"))

    exp_id_labels = [
        "GDSPS(PA) (twl)",
        "GDSPS(PA) (twl)",
    ]

    b2b_nhours = {
        exp_id_labels[0]: 6,
        exp_id_labels[1]: 6
    }

    score_plots_params = {
        "forecast_hour_tick_multiplier": 1,
        "max_lead_hour": 6
    }

    b2b_split_seasons = {
        f"{t:%b}": (t.month, ) for t in [datetime(2001, m, 1) for m in range(6, 10)]
    }

    # b2b_split_seasons = {
    #         "MAM": (3, 4, 5),
    #         "JJA": (6, 7, 8),
    #         "SON": (9, 10, 11),
    #         "DJF": (12, 1, 2)
    # }

    options = {
        "do_full_forecast_timeseries": False,
        "calculate_scores": False,
        "b2b_split_seasons": b2b_split_seasons,
        "score_map_figsize": (14, 5.5)
    }

    default_params.vname_to_limits = {
        "stde": (0, 1.),
        "gamma": (0, None),
        "stde_obs": (0, 1.),
        "gamma_varobsallvhour": (0, None)
    }

    default_params.score_clevs = {
        "gamma2": np.arange(0, 0.6, 0.05),
        "sigma": np.arange(0, 0.4, 0.02),
        "gamma2_diff": np.arange(-0.205, 0.21, 0.01),
        "sigma_diff": np.arange(-0.065, 0.07, 0.01),
    }

    # debug
    # station_dict = OrderedDict([("491", station_dict["491"])])

    exp_id_to_path = dict(zip(exp_id_labels, [swl_path_old, swl_path_new]))
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

    st_date = datetime(2019, 5, 25, 3)
    en_date = datetime(2019, 9, 24, 3)

    fc(station_dict=station_dict, st_date=st_date, en_date=en_date)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
