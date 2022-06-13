from collections import OrderedDict
from pathlib import Path

from surge_validation import io_manager


def main():
    inp_data_root = Path("/home/olh001/Python/loadprogs_python_experiments/data/gdsps/")
    exp_id_to_path = OrderedDict([
        ("RDSPS (FC, TWL)",
            next((inp_data_root / f"HIV2020_fc").rglob("data_for_scoring_rdsps_FC_fc_H2020_cycles_twl_*")) / "surge_rdsps_FC_fc_H2020_cycles_twl.dat"),
        ("GDSPS (FC, TWL)",
            next((inp_data_root / f"HIV2020_fc").rglob("data_for_scoring_gdsps_FC_fc_H2020_cycles_twl_*")) / "surge_gdsps_FC_fc_H2020_cycles_twl.dat"),
    ])

    for lbl, pth in exp_id_to_path.items():
        data = io_manager.read_wl_station_data(pth)
        print(data.head())


if __name__ == '__main__':
    main()