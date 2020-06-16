"""
==========RESPS par_120 vs exp_110===============
"""

from collections import OrderedDict
from pathlib import Path
from surge_validation.detiding_validation.config import default_params
from datetime import datetime

from surge_validation.detiding_validation.experiments import compare_forecast

EXP_ID = "par_120_vs_exp_110"


station_dict = OrderedDict([
    ("65", "Saint John, NB"),
    ("365", "Yarmouth, NS"),
    ("491", "Halifax, NS"),
    ("612", "North Sydney, NS"),
    ("1700", "Charlottetown, PE"),
    ("1805", "Shediac Bay, NB"),
    ("2000", "Lower Escuminac, NB"),
    ("2145", "Belledune, NB"),
    ("2330", "Riviere-au-Renard, QC"),
    ("2985", "Rimouski, QC"),
    ("2780", "Sept-Iles, QC"),
    ("1970", "Cap-aux-Meules, QC"),
    ("665", "Port-aux-Basques, NF"),
    ("835", "Argentia, NF"),
    ("905", "St Johns, NF"),
    ("990", "Bonavista, NF"),
    ("1430", "Nain, NF"),
])

station_dict = default_params.station_dict


def fc(station_dict=default_params.station_dict, st_date=None, en_date=None, member_id="", stat_name=""):

    label = f"resps_fc_{EXP_ID}_{member_id}"
    if len(stat_name) > 0:
        label = f"{label}_{stat_name}"
    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    img_dir = Path(f"data/plots/{label}")

    inp_data_root = "/home/olh001/Python/loadprogs_python/data/"

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    if stat_name.strip() == "":
        swl_path_old = inp_data_root + f"data_for_scoring_exp_110_{st_s}_{en_s}/surge_exp_110.dat"
        swl_path_new = inp_data_root + f"data_for_scoring_par_120_{st_s}_{en_s}/surge_par_120.dat"
    else:
        swl_path_old = inp_data_root + f"data_for_scoring_exp_110_{st_s}_{en_s}/surge_exp_110_{stat_name}.dat"
        swl_path_new = inp_data_root + f"data_for_scoring_par_120_{st_s}_{en_s}/surge_par_120_{stat_name}.dat"

    exp_id_labels = [
        "exp, 110", "par, 120"
    ]

    b2b_nhours = 36

    score_plots_params = {
        "forecast_hour_tick_multiplier": 24,
        "max_lead_hour": 10 * 24,
    }

    exp_id_to_path = dict(zip(exp_id_labels, [swl_path_old, swl_path_new]))
    compare_forecast(station_dict=station_dict, exp_id_to_path=exp_id_to_path,
                     exp_id_list=exp_id_labels,
                     img_dir=img_dir, qq_lead_hour_range=range(0, 0, 6),
                     b2b_nhours=b2b_nhours, score_plots_params=score_plots_params, member_id=member_id)





def main():
    # forecast
    st_date = datetime(2019, 4, 19, 12)
    en_date = datetime(2019, 6, 19, 0)

    # control member
    # fc(station_dict=station_dict, st_date=st_date, en_date=en_date, member_id="000")
    # fc(station_dict=station_dict, st_date=st_date, en_date=en_date, member_id="", stat_name="ensmean")
    fc(station_dict=station_dict, st_date=st_date, en_date=en_date, stat_name="ensmedian")


if __name__ == '__main__':
    main()
