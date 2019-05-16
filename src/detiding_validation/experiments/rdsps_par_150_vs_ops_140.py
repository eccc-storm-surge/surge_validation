

#==========RDSPS PA par_150 vs ops_140===============
from collections import OrderedDict
from pathlib import Path
from detiding_validation.config import default_params
from datetime import datetime

from detiding_validation.plot_timeseries_per_station import compare_sims_timeseries_back2back
from detiding_validation.surge_stats_entry import compare_2_simulations

from detiding_validation.experiments.FC70H17V2 import compare_rdsps_forecast

EXP_ID = "par_150_vs_ops_140"


station_dict = OrderedDict([
    (65, "Saint John, NB"),
    (365, "Yarmouth, NS"),
    (491, "Halifax, NS"),
    (612, "North Sydney, NS"),
    (1700, "Charlottetown, PEI"),
    (1805, "Shediac Bay, NB"),
    (2000, "Lower Escuminac, NB"),
    (2145, "Belledune, NB"),
    (2330, "Riviere-au-Renard, QC"),
    (2985, "Rimouski, QC"),
    (2780, "Sept-Iles, QC"),
    (1970, "Cap-aux-Meules, QC"),
    (665, "Port-aux-Basques, NFLD"),
    (835, "Argentia, NFLD"),
    (905, "St Johns"),
    (990, "Bonavista, NFLD"),
    (1430, "Nain, NFLD"),
])

station_dict_cpop_17jan2019 = OrderedDict([
    (365, "Yarmouth, NS"),
    (1805, "Shediac Bay, NB"),
    (665, "Port-aux-Basques, NFLD"),
    (835, "Argentia, NFLD"),
    (1430, "Nain, NFLD"),
])


def fc_cpop_17jan2019(station_dict=default_params.station_dict, st_date=None, en_date=None):
    label = f"rdsps_fc_cpop_17jan2019_{EXP_ID}"
    img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")

    inp_data_root = "/home/olh001/Python/loadprogs_python/data/"

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    swl_path_old = inp_data_root + f"data_for_scoring_rdsps_fc_ops_140_{st_s}_{en_s}/surge_rdsps_fc_ops_140.dat"
    swl_path_new = inp_data_root + f"data_for_scoring_rdsps_fc_par_150_{st_s}_{en_s}/surge_rdsps_fc_par_150.dat"

    exp_id_labels = [
        "storm surge (ops, 140)", "storm surge (par, 150)"
    ]

    plot_params = {
        "figure.figsize": (10, 8),
        "font.size": 12,
    }

    exp_id_to_path = dict(zip(exp_id_labels, [swl_path_old, swl_path_new]))
    compare_rdsps_forecast(station_dict=station_dict, exp_id_to_path=exp_id_to_path,
                           exp_id_list=exp_id_labels,
                           img_dir=img_dir,
                           n_subplot_cols=3, plot_params=plot_params)


def fc(station_dict=default_params.station_dict, st_date=None, en_date=None):
    label = f"rdsps_fc_{EXP_ID}"
    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    img_dir = Path(f"data/plots/{label}_test")

    inp_data_root = "/home/olh001/Python/loadprogs_python/data/"

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    swl_path_old = inp_data_root + f"data_for_scoring_rdsps_fc_ops_140_{st_s}_{en_s}/surge_rdsps_fc_ops_140.dat"
    swl_path_new = inp_data_root + f"data_for_scoring_rdsps_fc_par_150_{st_s}_{en_s}/surge_rdsps_fc_par_150.dat"

    exp_id_labels = [
        "ops, 140", "par, 150"
    ]

    exp_id_to_path = dict(zip(exp_id_labels, [swl_path_old, swl_path_new]))
    compare_rdsps_forecast(station_dict=station_dict, exp_id_to_path=exp_id_to_path, exp_id_list=exp_id_labels, img_dir=img_dir)


def fc_all_raw(station_dict=default_params.station_dict, st_date=None, en_date=None):
    label = f"rdsps_fc_{EXP_ID}"
    img_dir = Path(f"data/plots/{label}_all_raw_{datetime.utcnow():%Y%m%d%H%M}")

    inp_data_root = "/home/olh001/Python/loadprogs_python/data/"

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"

    swl_path_old = inp_data_root + f"data_for_scoring_rdsps_fc_ops_140_raw_{st_s}_{en_s}/surge_rdsps_fc_ops_140_raw.dat"
    swl_path_new = inp_data_root + f"data_for_scoring_rdsps_fc_par_150_raw_{st_s}_{en_s}/surge_rdsps_fc_par_150_raw.dat"

    exp_id_labels = [
        "storm surge (ops, 140, raw)", "storm surge (par, 150, raw)"
    ]

    exp_id_to_path = dict(zip(exp_id_labels, [swl_path_old, swl_path_new]))
    compare_rdsps_forecast(station_dict=station_dict, exp_id_to_path=exp_id_to_path, exp_id_list=exp_id_labels, img_dir=img_dir)


def pa(station_dict=default_params.station_dict):
    label = f"rdsps_pa_{EXP_ID}"
    img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")

    inp_data_root = "/home/olh001/Python/loadprogs_python/data/"

    swl_path_old = inp_data_root + f"data_for_scoring_rdsps_pa_ops_140_2018111400_2018122818/surge_rdsps_pa_ops_140.dat"
    swl_path_new = inp_data_root + f"data_for_scoring_rdsps_pa_par_150_2018111400_2018122818/surge_rdsps_pa_par_150.dat"

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
                          label_old="storm surge (ops, 140)",
                          label_new="storm surge (par, 150)", forecast_hour_tick_multiplier=1,
                          custom_rc_params=plot_params)


def main():
    do_pa = False

    if do_pa:
        pa(station_dict=station_dict)

    # forecast
    st_date = datetime(2018, 11, 14, 9)
    en_date = datetime(2018, 12, 24, 12)

    # fc_cpop_17jan2019(station_dict=station_dict_cpop_17jan2019, st_date=st_date, en_date=en_date)

    # fc(station_dict=station_dict_cpop_17jan2019, st_date=st_date, en_date=en_date)

    fc(station_dict=station_dict, st_date=st_date, en_date=en_date)
    #fc_all_raw(station_dict=station_dict, st_date=st_date, en_date=en_date)


if __name__ == '__main__':
    main()