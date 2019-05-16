from datetime import datetime

from pathlib import Path

from matplotlib.dates import HourLocator, DateFormatter, DayLocator
from matplotlib.font_manager import FontProperties
from matplotlib.gridspec import GridSpec
from rpnpy.librmn import all as rmn
import numpy as np
from rpnpy.rpndate import RPNDate
import pandas as pd
import matplotlib.pyplot as plt


def read_and_plot_ts_at_bc(bc_mask_file: Path, tides_data_file: Path,
                           dalcoast_data_file: Path, plots_dir: Path,
                           beg_date=None, end_date=None, nomvar="SSHT"):
    funit = rmn.fstopenall(str(bc_mask_file))
    msk = rmn.fstluk(rmn.fstinl(funit, nomvar="MGB")[0])["d"]

    # remove the borders
    msk[0, :] = 0
    msk[-1, :] = 0
    msk[:, 0] = 0
    msk[:, 1] = 0
    msk[:, -1] = 0

    print(msk.sum())

    rmn.fstcloseall(funit)

    i_arr, j_arr = np.where(msk > 0.5)

    models = ["WT", "DC"]
    models_to_paths = dict(zip(models, [tides_data_file, dalcoast_data_file]))
    models_to_nomvars = dict(zip(models, [nomvar, "ETAS"]))
    model_to_bathy = {}

    df_list = []
    for m, data_file in models_to_paths.items():

        data = {"time": []}
        data.update({(i + 1, j + 1, m): [] for i, j in zip(i_arr, j_arr)})

        funit = rmn.fstopenall(str(data_file))
        for key in rmn.fstinl(funit, nomvar=models_to_nomvars[m], typvar="P@"):
            rec = rmn.fstluk(key)

            d = RPNDate(rec["datev"]).toDateTime().replace(tzinfo=None)
            if d > end_date or d < beg_date:
                continue

            data["time"].append(d)

            for i, j in zip(i_arr, j_arr):
                data[(i + 1, j + 1, m)].append(rec["d"][i, j])

        model_to_bathy[m] = rmn.fstluk(rmn.fstinl(funit, nomvar="BTMY")[0])["d"]

        rmn.fstcloseall(funit)

        df = pd.DataFrame.from_dict(data)
        df.set_index("time", inplace=True, verify_integrity=True)

        df.sort_index(inplace=True)

        df_list.append(df)

    df = pd.concat(df_list, axis=1)

    print(df)

    # do the plotting
    plots_dir.mkdir(exist_ok=True)
    ncols = 4
    n_subplots = len(df.columns) // len(models)
    nrows = n_subplots // ncols + int(n_subplots % ncols != 0)

    gs = GridSpec(nrows=nrows, ncols=ncols)
    fig = plt.figure(figsize=(10, 10))
    ax = None
    for i, point in enumerate(zip(i_arr + 1, j_arr + 1)):
        r, c = i // ncols, i % ncols
        ax = fig.add_subplot(gs[r, c], sharex=ax, sharey=ax)
        # ax.xaxis.set_minor_formatter(NullFormatter())
        ax.xaxis.set_major_formatter(DateFormatter("%d"))
        ax.xaxis.set_major_locator(DayLocator())

        hwt = model_to_bathy[models[0]][point[0] - 1, point[1] - 1]
        hdc = model_to_bathy[models[1]][point[0] - 1, point[1] - 1]

        cols = [point + (m,) for m in models]
        if len(models) >= 2:
            mod_col_key = point + (f"{models[0]}*", )
            df[mod_col_key] = df[point + (f"{models[0]}", )] * hwt / hdc
            cols.append(mod_col_key)

        df.plot(y=cols, ax=ax, linewidth=0.7, x_compat=True, legend=False)
        ax.grid(linewidth=0.3, linestyle="dashed")
        ax.legend(loc="upper right", prop=FontProperties(size=5))

        info = "; ".join([f"h({m})={model_to_bathy[m][point[0] - 1, point[1] - 1]:.1f}" for m in models])

        if len(models) >= 2:
            info += f"; h({models[0]})/h({models[1]}) = { hwt / hdc :.1f}"

        ax.text(0.01, 0.01, info, va="bottom", ha="left", transform=ax.transAxes, fontproperties=FontProperties(size=5))

    img_file = plots_dir / f"bc_timeseries_{nomvar}_v003.png"
    fig.savefig(img_file, dpi=400, bbox_inches="tight")


def main():
    plots_dir = Path("data/bc_tests")
    beg_date = datetime(2017, 1, 21)
    end_date = datetime(2017, 1, 23)

    bc_mask_file = Path("/home/olh001/.suites/resps_tides_only_nwatl/forecast/hub/eccc-ppp2/gridpt/tides/bc_mask.fst")
    tides_data_file = Path("/home/olh001/.suites/resps_tides_only_nwatl/forecast/hub/eccc-ppp2/gridpt/tides/2016121500")
    dalcoast_data_file = Path(
        "/home/olh001/.suites/resps_tides_only_nwatl/forecast/hub/eccc-ppp2/gridpt/prog_tides/2016121500_000")

    var_names = ["SSHT", ]

    for nomvar in var_names:
        read_and_plot_ts_at_bc(bc_mask_file, tides_data_file, dalcoast_data_file, plots_dir,
                               beg_date=beg_date, end_date=end_date, nomvar=nomvar)


if __name__ == '__main__':
    main()
