from datetime import datetime
from pathlib import Path

from detiding_validation.experiments.FC70H17V2 import compare_forecast
from collections import OrderedDict


station_dict = OrderedDict([
    ("8443970", "Boston, MA"),
    ("8418150", "Portland, ME"),
    ("8413320", "Bar Harbor, ME"),
    ("8410140", "Eastport, ME"),
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
    ("755", "St. Lawrence, NF"),
    ("835", "Argentia, NF"),
    ("905",   "St Johns, NF"),
    ("990",   "Bonavista, NF"),
    ("1430",  "Nain, NF"),
    ("1040",  "Carmanville, NL"),
    ("1170",  "St Anthony, NL"),
    ("1630",  "Pictou, NS"),
    ("1915",  "Rustico, PE"),
    ("2550",  "Harrington Harbour, QC"),
    ("880",   "Trepassey, NL"),
    ("325",   "Digby, NS"),
    ("475",   "Mill Cove, NS"),
    ("576",   "Point Tupper, NS"),
    ("2590",  "Forteau, NL"),
    ("2633",  "Savage Cove, NL"),
    ("2685",  "Lark Harbour, NL"),
    ("2840",  "Baie-Comeau, QC"),
    ("2935",  "Ste-Anne-des-Monts, QC"),
    ("550",   "Sable Island, NS"),
    ("900",   "Bay Bulls, NL"),
    ("1050", "Fogo, NL"),
    ("1680", "Wood Islands, PE"),
    ("2246", "Saint Pierre, FR"),
    ("1098", "Springdale, NL"),
    ("1186", "Henley Harbour, NL"),
    ("2375", "Southwest Point, QC")
])


def main():
    st_time = datetime(2018, 4, 16)
    en_time = datetime(2019, 2, 12)

    st_s = f"{st_time:%Y%m%d%H}"
    en_s = f"{en_time:%Y%m%d%H}"

    label = "webtide_debug_hrglobal"
    swl_path_old = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_{label}_{st_s}_{en_s}/surge_{label}.dat"
    swl_path_new = swl_path_old

    exp_id_list = ["WT", "WT"]
    exp_id_store = {
        exp_id_list[0]: swl_path_old, exp_id_list[1]: swl_path_new
    }

    exp_label = label + "_" + "_vs_".join(exp_id_list)

    img_dir = Path(f"data/plots/{exp_label}")
    img_dir.mkdir(exist_ok=True, parents=True)

    score_plots_params = {
        "forecast_hour_tick_multiplier": 24
    }

    options = {
        "do_full_forecast_timeseries": False
    }

    compare_forecast(img_dir=img_dir, exp_id_list=exp_id_list,
                     exp_id_to_path=exp_id_store,
                     b2b_nhours=-1,
                     station_dict=station_dict,
                     score_plots_params=score_plots_params,
                     qq_lead_hour_range=range(1, 2),
                     st_time=st_time, en_time=en_time,
                     options=options)


if __name__ == '__main__':
    main()
