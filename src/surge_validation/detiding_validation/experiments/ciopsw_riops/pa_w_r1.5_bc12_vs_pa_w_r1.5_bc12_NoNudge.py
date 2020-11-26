"""
= CIOPS-E hindcast===============
Filtering tides in ciopse and obs for validation
"""
import logging
from pathlib import Path
from surge_validation.detiding_validation.config import default_params
from datetime import datetime

from surge_validation.detiding_validation.experiments.FC70H17V2 import compare_forecast

EXP_ID = "ciopswv1.5_bc12_vs_bc12_NoNudge_v002"


station_dict = default_params.station_dict


def fc(station_dict=default_params.station_dict, st_date=None, en_date=None):

    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    inp_data_root = Path("/fs/homeu1/eccc/cmd/cmde/olh001/Python/loadprogs_python_experiments/data/ciopsw_v1.5_pa_v002/")

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    label = f"{EXP_ID}_{st_s}_{en_s}"
    img_dir = Path(f"data/plots/{label}")

    swl_path_old = next(inp_data_root.rglob(f"*{st_s}*{en_s}*/surge*pa_w_r1.5_bc12.dat"))
    swl_path_new = next(inp_data_root.rglob(f"*{st_s}*{en_s}*/surge*pa_w_r1.5_bc12_NoNudge.dat"))

    exp_id_labels = [
        "CIOPSW (PA, surge, r1.5_bc12)", "CIOPSW (PA, surge, r1.5_bc12_NoNudge)"
    ]

    b2b_nhours = {
        exp_id_labels[0]: 1,
        exp_id_labels[1]: 1
    }

    score_plots_params = {
        "forecast_hour_tick_multiplier": 6,
        "max_lead_hour": 48
    }

    # b2b_split_seasons = {
    #     f"{t:%b}": (t.month, ) for t in [datetime(2001, m, 1) for m in range(1, 13)]
    # }

    b2b_split_seasons = {
            "MAM": (3, 4, 5),
            "JJA": (6, 7, 8),
            "SON": (9, 10, 11),
            "DJF": (12, 1, 2)
    }

    options = {
        "do_full_forecast_timeseries": False,
        "calculate_scores": False,
        "b2b_split_seasons": b2b_split_seasons
    }

    default_params.vname_to_limits = {
        "stde": (0, 1.),
        "gamma": (0, None),
        "stde_obs": (0, 1.),
        "gamma_varobsallvhour": (0, None)
    }

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

    st_date = datetime(2016, 1, 1, 0)
    en_date = datetime(2017, 1, 1, 0)

    fc(station_dict=station_dict, st_date=st_date, en_date=en_date)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
