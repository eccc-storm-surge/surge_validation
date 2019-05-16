from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import pandas as pd
from matplotlib.gridspec import GridSpec
from rpnpy.librmn import all as rmn
from rpnpy.rpndate import RPNDate

import matplotlib.pyplot as plt


def main():
    """
     Point definitions come from a .obs file
     """
    beg_date = datetime(2017, 1, 1, 0)
    beg_date_s = f"{beg_date:%Y%m%d%H}_"

    end_date = datetime(2018, 10, 1, 18)
    end_date_s = f"{end_date:%Y%m%d%H}_"

    img_dir = Path(f"data/running_and_pass_avg_timeseries_{beg_date_s}{end_date_s}")
    img_dir.mkdir(exist_ok=True)

    nday_running_mean = 365
    data_dir = Path("/home/olh001/Python/storm_surge_pp/data/rdsps/precalculated_daily_and_rolling_avg_real_20181011")



    member_id = ""

    obs_file = Path("/home/olh001/Python/station_positions_vis/stations_storm_surge_1_30.obs")

    obs_df = pd.read_csv(obs_file, skiprows=2, sep="\s+")
    nomvar = "ETAS"
    typvar = "P@"

    etikets = OrderedDict([
        ("pass", "RDPASSAVG"),
        ("roll", "RDROLLAVG"),
    ])

    # read in the timeseries data from fst files
    ij_to_stname = {(i, j): stname for i, j, stname in zip(obs_df["DATA.I"] - 1, obs_df["DATA.J"] - 1, obs_df["ID"])}

    data_files = [str(f) for f in data_dir.iterdir() if beg_date_s <= f.name <= end_date_s]

    etiket_to_data = {etiket: {(i, j): [] for i, j in ij_to_stname} for etiket in etikets.values()}
    etiket_to_dates = {etiket: [] for etiket in etikets.values()}

    # read in the data for all points
    funit = rmn.fstopenall(data_files)

    for etiket in list(etikets.values()):
        keys = rmn.fstinl(funit, nomvar=nomvar, typvar=typvar, etiket=etiket)
        for k in keys:
            rec = rmn.fstluk(k)

            for (i, j), st_name in ij_to_stname.items():
                etiket_to_data[etiket][i, j].append(rec["d"][i, j])

            etiket_to_dates[etiket].append(RPNDate(rec["datev"]).toDateTime())

    rmn.fstcloseall(funit)

    etiket_to_df = {etiket: pd.DataFrame.from_dict(etiket_to_data[etiket]) for etiket in etiket_to_dates}
    for etiket, df in etiket_to_df.items():
        df.index = etiket_to_dates[etiket]
        df.sort_index(inplace=True)

    gs = GridSpec(2, 1)

    for (i,j), stname in ij_to_stname.items():
        fig = plt.figure(figsize=(8, 6))
        fig_path = img_dir / f"{stname}_I{i + 1}_J{j + 1}.png"


        ax = None
        for subplot_ind, (etiket, df) in enumerate(etiket_to_df.items()):
            ax = fig.add_subplot(gs[subplot_ind, 0], sharex=ax)
            df[i, j].plot(ax=ax, grid=True, label=etiket)
            ax.legend()
            if subplot_ind == 0:
                ax.set_title(f"{stname}, running and pass means")


        fig.savefig(str(fig_path), bbox_inches="tight", dpi=300)
        plt.close(fig)


if __name__ == '__main__':
    main()