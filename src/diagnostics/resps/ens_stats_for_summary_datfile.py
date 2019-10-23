from pathlib import Path
import pandas as pd
import numpy as np


OBS_COL_INDEX = 5

stat_funcs = {
    "ensmean": lambda x: np.mean(x, axis=1),
    "ensmedian": lambda x: np.median(x, axis=1),
}


def calc_stats(in_file: Path, stat_names=("ensmean", "ensmedian")):

    data = pd.read_csv(in_file, sep=r"\s+", header=None)

    print(data.shape)
    print(data.head())
    for a_stat in stat_names:

        stat_values = stat_funcs[a_stat](data.iloc[:, OBS_COL_INDEX + 1:].values)

        print(stat_values.shape)

        data.iloc[:, OBS_COL_INDEX + 1] = stat_values

        out_file = in_file.parent / f"{in_file.name[:-4]}_{a_stat}.dat"

        data.to_csv(out_file, header=None, index=False, sep=" ")


def do_all():
    data_root = Path("/home/olh001/Python/loadprogs_python/data")

    path_list = [
        data_root / "data_for_scoring_par_120_2019041912_2019061900/surge_par_120.dat",
        data_root / "data_for_scoring_par_120_lev_2019041912_2019061900/surge_par_120_lev.dat",
        data_root / "data_for_scoring_exp_110_2019041912_2019061900/surge_exp_110.dat"
    ]

    for p in path_list:
        calc_stats(p)


if __name__ == '__main__':
    do_all()
