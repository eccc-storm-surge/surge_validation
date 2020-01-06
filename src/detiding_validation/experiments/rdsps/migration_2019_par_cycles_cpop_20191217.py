from collections import OrderedDict
from datetime import datetime
from pathlib import Path

from detiding_validation.config import default_params
from detiding_validation.experiments.FC70H17V2 import compare_forecast
import numpy as np

EXP_ID = "migration_rdsps_170par_vs_160ops_cpop_20191217"


def fc(station_dict=default_params.station_dict, st_date=None, en_date=None):

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    label = f"{EXP_ID}_{st_s}_{en_s}"
    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    img_dir = Path(f"data/plots/{label}")

    inp_data_root = "/home/olh001/Python/loadprogs_python/data/migration_2019_par_cycles/rdsps/cpop_20191217"

    swl_path_old = Path(inp_data_root) / f"data_for_scoring_rdsps_160_fc_{st_s}_{en_s}/surge_rdsps_160_fc.dat"
    swl_path_new = Path(inp_data_root) / f"data_for_scoring_rdsps_170_fc_{st_s}_{en_s}/surge_rdsps_170_fc.dat"

    exp_id_labels = [
        "160-ops", "170-par"
    ]

    b2b_nhours = 36

    score_plots_params = {
        "forecast_hour_tick_multiplier": 24,
        "max_lead_hour": 6 * 24,

    }

    default_params.vname_to_limits = {
        "stde": (0, 0.16),
        "gamma": (0, 1.15),
        "stde_obs": (0, 0.3),
        "gamma_varobsallvhour": (0, 1.15)
    }

    exp_id_to_path = dict(zip(exp_id_labels, [swl_path_old, swl_path_new]))
    compare_forecast(station_dict=station_dict, exp_id_to_path=exp_id_to_path,
                     exp_id_list=exp_id_labels,
                     img_dir=img_dir, qq_lead_hour_range=[1, 24, 36, 48, 72, 96],
                     b2b_nhours=b2b_nhours, score_plots_params=score_plots_params)


if __name__ == '__main__':
    d_beg = datetime(2019, 10, 29, 12)
    d_end = datetime(2019, 12, 3, 0)

    # reject_stations = [
    #     "1970", "2330", "2780", "2985", "8443970", "8418150", "990"
    # ]

    reject_stations = ["8418150"]

    # select stations with data
    items = [(st_id, st_name) for st_id, st_name in default_params.station_dict.items()
               if st_id not in reject_stations]
    st_dict = OrderedDict(items)

    fc(st_date=d_beg, en_date=d_end, station_dict=st_dict)
