from datetime import datetime
from pathlib import Path

from detiding_validation.experiments.FC70H17V2 import compare_rdsps_forecast
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
    ("00001", "Saint Pierre, FR"),
    ("00002", "Springdale, NL"),
    ("00003", "Henley Harbour, NL"),
    ("00004", "Southwest Point, QC")
])


def main():
    st_time = datetime(2017, 1, 1)
    en_time = datetime(2018, 1, 1)

    st_s = f"{st_time:%Y%m%d%H}"
    en_s = f"{en_time:%Y%m%d%H}"

    for tc_domain in ["nwatl", "hrglobal"]:
        swl_path_old = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_webtide_{tc_domain}_{st_s}_{en_s}/surge_webtide_{tc_domain}.dat"
        swl_path_new = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_prog_tides_{tc_domain}_{st_s}_{en_s}/surge_prog_tides_{tc_domain}.dat"

        exp_id_list = ["WT", "DC"]
        exp_id_store = {
            exp_id_list[0]: swl_path_old, exp_id_list[1]: swl_path_new
        }

        exp_label = tc_domain + "_" + "_vs_".join(exp_id_list)

        img_dir = Path(f"data/plots/{exp_label}")
        img_dir.mkdir(exist_ok=True, parents=True)

        score_plots_params = {
            "forecast_hour_tick_multiplier": 960
        }

        compare_rdsps_forecast(img_dir=img_dir, exp_id_list=exp_id_list, exp_id_to_path=exp_id_store,
                               b2b_nhours=96, calculate_scores=True,
                               station_dict=station_dict, score_plots_params=score_plots_params)


if __name__ == '__main__':
    main()
