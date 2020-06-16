from datetime import datetime
from pathlib import Path
import pandas as pd
import csv
import matplotlib.pyplot as plt


def get_annual_maximum_around_mean(obs_file: Path, min_cnt: int=2160):
    data_col = obs_file.name[1:-4]
    print(f"reading {data_col}")
    df = pd.read_fwf(obs_file, widths=[16, 100], header=None, names=["time", data_col])
    print(df.head(10))

    df["time"] = df["time"].map(lambda s: datetime.strptime(s, "%Y %m %d %H %M"))
    df.set_index("time", inplace=True)

    groups = df.groupby(df.index.year)
    annual_max = groups.max()
    annual_avg = groups.mean()
    annual_cnt = groups.count()

    annual_max -= annual_avg
    annual_max = annual_max[annual_cnt[data_col] >= min_cnt]

    annual_max.sort_index(inplace=True)

    print(annual_cnt.head(100))
    print(annual_max.head(100))

    return annual_max.reindex(range(annual_max.index.min(), annual_max.index.max() + 1))


def main():
    obs_dir = Path("/home/olh001/MATLAB/detide/download_scripts/meds/1900_2018")

    df_list = []
    for i, fp in enumerate(obs_dir.iterdir()):
        if not fp.name.endswith(".dat"):
            continue
        df = get_annual_maximum_around_mean(fp)
        df_list.append(df)

    df_out = pd.concat(df_list, sort=True, axis=1)

    df_out.index.names = ["year"]

    for c in df_out:
        print(f"{c}: {len(df_out[c].dropna())}")

    df_out.to_csv("data/annual_max_for_obs.csv", sep=",", na_rep="{:>8s}".format("NaN"), float_format="%8.3f",
                  header=["{:>08d}".format(int(h)) for h in df_out.columns], quoting=csv.QUOTE_NONE, doublequote=False)


    # plot the data
    fig = plt.figure(figsize=(10, 10))
    df_out.plot(subplots=True, grid=True, color="k", ax=fig.gca(), layout=(-1, 4), sharex=False, sharey=False)
    fig.tight_layout()
    fig.savefig("data/annual_max_plot_all_stations.png", bbox_inches="tight", dpi=400)


if __name__ == '__main__':
    main()