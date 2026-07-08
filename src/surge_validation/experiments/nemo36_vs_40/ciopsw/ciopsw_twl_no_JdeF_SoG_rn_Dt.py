"""

Filtering tides in ciopse and obs for validation
"""
import logging
from pathlib import Path
from surge_validation.config import default_params
from datetime import datetime

from surge_validation.experiments.validation_experiment_base import compare_forecast
from surge_validation import io_manager
EXP_ID = "ciopsw_pa_twl_with_tides_no_JdeF_SoG_rnDt"

import numpy as np
station_dict = default_params.station_dict


def fc(station_dict=default_params.station_dict, st_date=None, en_date=None):

    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    inp_data_root = Path("/home/olh001/Python/loadprogs_python_experiments/data/ciopsw_nemo36/ciops/ciopsw/nep/pa/")

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    label = f"{EXP_ID}_{st_s}_{en_s}"
    img_dir = Path(f"data/plots/nemo36_vs_40/ciopsw/pa/twl/{label}")


    score_plots_params = {
        "forecast_hour_tick_multiplier": 6,
        "max_lead_hour": 48
    }

    # b2b_split_seasons = {
    #     f"{t:%b}": (t.month, ) for t in [datetime(2001, m, 1) for m in range(1, 13)]
    # }

    options = {
        "do_full_forecast_timeseries": False,
        "calculate_scores": False,
        "b2b_split_seasons": dict(),
        "score_map_figsize": (18, 16),
        "plot_tide_constituents": True
    }

    default_params.vname_to_limits = {
        "stde": (0, 1.),
        "gamma": (0, None),
        "stde_obs": (0, 1.),
        "gamma_varobsallvhour": (0, None)
    }

    exp_id_to_path = {
        "nemo36_twl": inp_data_root / "data_for_scoring_pa_nep_nemo36_twl_2022070100_2022093000/surge_pa_nep_nemo36_twl.dat",
        "nemo4_rn_Dt_twl": inp_data_root / "data_for_scoring_pa_nep_nemo40_twl_rn_Dt_2022070100_2022093000/surge_pa_nep_nemo40_twl_rn_Dt.dat",
    }

    b2b_nhours = {
        lbl: 25 for lbl in exp_id_to_path
    }
    # b2b_nhours.update({
    #     "nemo36_twl": 25
    # })

    compare_forecast(station_dict=station_dict, exp_id_to_path=exp_id_to_path,
                     exp_id_list=list(exp_id_to_path),
                     img_dir=img_dir, qq_lead_hour_range=range(1, 1, 1),
                     b2b_nhours=b2b_nhours,
                     score_plots_params=score_plots_params,
                     options=options, st_time=st_date, en_time=en_date,
                     b2b_cutoff_hours=None)


def main():
    # forecast
    # st_date = datetime(2017, 1, 1, 0)
    # en_date = datetime(2017, 12, 31, 18)

    st_date = datetime(2022, 7, 1, 0)
    en_date = datetime(2022, 9, 30, 0)

    obs_file = Path("/home/olh001/Python/obs_to_grid_mapping/ciopsw_opt_v001.obs")
    station_dict = io_manager.read_station_dict_from_obs(obs_file)

    default_params.score_clevs["sigma"] = np.arange(-0.02, 0.025, 0.005)

    skip = [
        "9443090", "9444090", "9444900",
        "7120", "9449880", "7277", "9449424", 
        "7917", "8074", "7795", "7735"
    ]

    station_dict = {k: v for k, v in station_dict.items() if k not in skip}

    fc(station_dict=station_dict, st_date=st_date, en_date=en_date)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
