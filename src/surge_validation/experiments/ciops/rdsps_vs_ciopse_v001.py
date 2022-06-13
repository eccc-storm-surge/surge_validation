"""
==========RDSPS PA vs CIOPS-E ===============
"""

from pathlib import Path
from surge_validation.config import default_params
from datetime import datetime

from surge_validation.experiments import compare_forecast

EXP_ID = "rdsps_pa_vs_ciopse_pa_mydetide_specify_constits_2016"


station_dict = default_params.station_dict


def fc(station_dict=default_params.station_dict, st_date=None, en_date=None):

    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    inp_data_root = "/home/olh001/Python/loadprogs_python/data/"

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    label = f"{EXP_ID}_{st_s}-{en_s}"
    img_dir = Path(f"data/plots/{label}")

    swl_path_old = inp_data_root + f"data_for_scoring_rdsps_{st_s}_{en_s}/surge_rdsps.dat"
    swl_path_new = inp_data_root + f"data_for_scoring_ciopse_{st_s}_{en_s}/surge_ciopse.dat"

    exp_id_labels = [
        "RDSPS, PA", "CIOPS-E"
    ]

    b2b_nhours = 6

    score_plots_params = {
        "forecast_hour_tick_multiplier": 1,
        "max_lead_hour": 6
    }

    options = {
        "do_full_forecast_timeseries": False
    }

    exp_id_to_path = dict(zip(exp_id_labels, [swl_path_old, swl_path_new]))
    compare_forecast(station_dict=station_dict, exp_id_to_path=exp_id_to_path,
                     exp_id_list=exp_id_labels,
                     img_dir=img_dir, qq_lead_hour_range=range(1, 7, 1),
                     b2b_nhours=b2b_nhours, score_plots_params=score_plots_params,
                     options=options, st_time=st_date, en_time=en_date,
                     b2b_cutoff_hours=None)


def main():
    # forecast
    # st_date = datetime(2017, 1, 1, 0)
    # en_date = datetime(2017, 12, 31, 18)

    st_date = datetime(2016, 1, 1, 0)
    en_date = datetime(2016, 12, 31, 18)

    fc(station_dict=station_dict, st_date=st_date, en_date=en_date)


if __name__ == '__main__':
    main()
