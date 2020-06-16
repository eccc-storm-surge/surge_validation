"""
==========RDSPS par_160 vs ops_150===============
"""

from collections import OrderedDict
from pathlib import Path
from surge_validation.detiding_validation.config import default_params
from datetime import datetime

from surge_validation.detiding_validation import compare_2_simulations
from surge_validation.detiding_validation.experiments import compare_forecast

EXP_ID = "par_160_vs_ops_150"


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


def fc(station_dict=default_params.station_dict, st_date=None, en_date=None):
    label = f"rdsps_fc_{EXP_ID}"
    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    img_dir = Path(f"data/plots/{label}_test")

    inp_data_root = "/home/olh001/Python/loadprogs_python/data/"

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    swl_path_old = inp_data_root + f"data_for_scoring_rdsps_fc_ops_150_{st_s}_{en_s}/surge_rdsps_fc_ops_150.dat"
    swl_path_new = inp_data_root + f"data_for_scoring_rdsps_fc_par_160_{st_s}_{en_s}/surge_rdsps_fc_par_160.dat"

    exp_id_labels = [
        "ops, 150", "par, 160"
    ]

    b2b_nhours = 36

    score_plots_params = {
        "forecast_hour_tick_multiplier": 24,
        "max_lead_hour": 6 * 24
    }

    exp_id_to_path = dict(zip(exp_id_labels, [swl_path_old, swl_path_new]))
    compare_forecast(station_dict=station_dict, exp_id_to_path=exp_id_to_path,
                     exp_id_list=exp_id_labels,
                     img_dir=img_dir, qq_lead_hour_range=range(0, 0, 6),
                     b2b_nhours=b2b_nhours, score_plots_params=score_plots_params)


def pa(station_dict=default_params.station_dict):
    label = f"rdsps_pa_{EXP_ID}"
    img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")

    inp_data_root = "/home/olh001/Python/loadprogs_python/data/"

    swl_path_old = inp_data_root + f"data_for_scoring_rdsps_pa_ops_150_2018111400_2018122818/surge_rdsps_pa_ops_150.dat"
    swl_path_new = inp_data_root + f"data_for_scoring_rdsps_pa_par_160_2018111400_2018122818/surge_rdsps_pa_par_160.dat"

    default_params.vname_to_limits = {
        "stde": (0, 0.3),
        "gamma": (0, 3),
        "stde_obs": (0, 0.3),
        "gamma_varobsallvhour": (0, 3)
    }

    plot_params = {
        "figure.figsize": (10, 12),
        "font.size": 8,
    }

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=station_dict,
                          label_old="storm surge (ops, 150)",
                          label_new="storm surge (par, 160)", forecast_hour_tick_multiplier=1,
                          custom_rc_params=plot_params)


def main():
    do_pa = False

    if do_pa:
        pa(station_dict=station_dict)

    # forecast
    st_date = datetime(2019, 3, 6, 12)
    en_date = datetime(2019, 5, 30, 12)

    fc(station_dict=station_dict, st_date=st_date, en_date=en_date)


if __name__ == '__main__':
    main()
