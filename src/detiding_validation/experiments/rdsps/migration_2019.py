from datetime import datetime
from pathlib import Path

from detiding_validation.config import default_params
from detiding_validation.experiments.FC70H17V2 import compare_forecast
import numpy as np

EXP_ID = "migration_rdsps_170_vs_160"


def fc(station_dict=default_params.station_dict, st_date=None, en_date=None):
    label = f"{EXP_ID}"
    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    img_dir = Path(f"data/plots/{label}")

    inp_data_root = "/home/olh001/Python/loadprogs_python/data/"

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    swl_path_old = inp_data_root + f"data_for_scoring_rdsps_160_fc_{st_s}_{en_s}/surge_rdsps_160_fc.dat"
    swl_path_new = inp_data_root + f"data_for_scoring_rdsps_170_fc_{st_s}_{en_s}/surge_rdsps_170_fc.dat"

    exp_id_labels = [
        "160", "170"
    ]

    b2b_nhours = 36

    score_plots_params = {
        "forecast_hour_tick_multiplier": 24,
        "max_lead_hour": 10 * 24
    }

    exp_id_to_path = dict(zip(exp_id_labels, [swl_path_old, swl_path_new]))
    compare_forecast(station_dict=station_dict, exp_id_to_path=exp_id_to_path,
                     exp_id_list=exp_id_labels,
                     img_dir=img_dir, qq_lead_hour_range=np.arange(1, 240, 20),
                     b2b_nhours=b2b_nhours, score_plots_params=score_plots_params)


if __name__ == '__main__':
    d_beg = datetime(2016, 12, 25, 0)
    d_end = datetime(2017, 2, 28, 12)
    fc(st_date=d_beg, en_date=d_end)
