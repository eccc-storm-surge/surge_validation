"""
==========RESPS par_120lev vs par_120===============
"""

from collections import OrderedDict
from pathlib import Path
from surge_validation.config import default_params
from datetime import datetime

from surge_validation.experiments.validation_experiment_base import compare_forecast

EXP_ID = "resps_120-ops_vs_130-par"


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


def fc(station_dict=default_params.station_dict, st_date=None, en_date=None, member_id=""):

    st_s = f"{st_date:%Y%m%d%H}"
    en_s = f"{en_date:%Y%m%d%H}"


    label = f"{EXP_ID}_{member_id}_cpop_20191217_{st_s}-{en_s}"
    # img_dir = Path(f"data/plots/{label}_{datetime.utcnow():%Y%m%d%H%M}")
    img_dir = Path(f"data/plots/{label}")

    inp_data_root = "/home/olh001/Python/loadprogs_python/data/migration_2019_par_cycles/resps/cpop_20191217"


    swl_path_old = Path(inp_data_root) / f"data_for_scoring_resps_120-ops_{st_s}_{en_s}/surge_resps_120-ops.dat"
    swl_path_new = Path(inp_data_root) / f"data_for_scoring_resps_130-par_{st_s}_{en_s}/surge_resps_130-par.dat"

    exp_id_labels = [
        "120-ops", "130-par"
    ]

    b2b_nhours = 36

    score_plots_params = {
        "forecast_hour_tick_multiplier": 24,
        "max_lead_hour": 3 * 24
    }

    exp_id_to_path = dict(zip(exp_id_labels, [swl_path_old, swl_path_new]))
    compare_forecast(station_dict=station_dict, exp_id_to_path=exp_id_to_path,
                     exp_id_list=exp_id_labels,
                     img_dir=img_dir, qq_lead_hour_range=range(0, 0, 6),
                     b2b_nhours=b2b_nhours, score_plots_params=score_plots_params,
                     member_id=member_id)


def main():
    # forecast
    st_date = datetime(2019, 11, 11, 0)
    en_date = datetime(2019, 12, 3, 0)


    # reject_stations = [
    #     "1970", "2330", "2780", "2985", "8443970", "8418150", "990"
    # ]

    reject_stations = ["8418150", ]


    # select stations with data
    items = [(st_id, st_name) for st_id, st_name in default_params.station_dict.items()
             if st_id not in reject_stations]
    st_dict = OrderedDict(items)



    # control member
    fc(station_dict=st_dict,
       st_date=st_date, en_date=en_date, member_id="000")


if __name__ == '__main__':
    main()
