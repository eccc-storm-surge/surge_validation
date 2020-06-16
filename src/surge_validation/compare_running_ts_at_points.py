from datetime import datetime, timedelta, timezone
from pathlib import Path
import pandas as pd
from dateutil.relativedelta import relativedelta
from matplotlib.dates import DateFormatter, MonthLocator, DayLocator
from matplotlib.gridspec import GridSpec
from rpnpy.librmn import all as rmn
from rpnpy.rpndate import RPNDate
import matplotlib.pyplot as plt

from surge_validation.utils import strutils
import numpy as np


values_range = {
    "ETAS": (-0.1, 0.25)
}


def get_data_for_obs_points(obs_df: pd.DataFrame, data_dir: Path,
                            case_id="", subcase_id="",
                            etiket="", nomvar="ETAS"):
    """

    :returns
                a data frame with column headers as tuples (station_id, case_id, subcase_id)

    :param obs_df: dataframe containing point information
    :param data_dir: path to the data directory.
    """

    data_dict = {(st_id, case_id, subcase_id): [] for st_id in obs_df["NO"].values}
    st_id_to_ij = {st_id: (i, j) for st_id, i, j in zip(obs_df["NO"].values,
                                                        obs_df["DATA.I"].values - 1,
                                                        obs_df["DATA.J"].values - 1)}

    times = []

    for data_file in data_dir.iterdir():
        funit = rmn.fstopenall(str(data_file))

        keys = rmn.fstinl(funit, etiket=etiket, typvar="P@", nomvar=nomvar)

        assert len(keys) > 0

        for k in keys:
            meta = rmn.fstprm(k)

            if "ROLL" not in meta["etiket"]:
                continue

            rec = rmn.fstluk(k)
            times.append(RPNDate(rec["datev"]).toDateTime())
            for st_id, (i, j) in st_id_to_ij.items():
                data_dict[(st_id, case_id, subcase_id)].append(rec["d"][i, j])

        rmn.fstcloseall(funit)

    res = pd.DataFrame.from_dict(data=data_dict)
    res.index = times

    print(res.head(40))

    return res


def entry_002():
    """
    compare different running averaging interval lengths, i.e 30, 60, 90, 120,...days,
    during different seasons for 1 month ending at the same time

    1 plot per station, containing a panel for different seasons, each panel has several plots (i.e for different
    durations of running means)

    :return:
    """
    running_avg_window_list = list(range(30, 390, 30))
    ends_on_list = [
        datetime(2017, 2, 1),
        datetime(2017, 5, 1),
        datetime(2017, 8, 1),
        datetime(2017, 11, 1),

    ]

    backtrack_dt = relativedelta(months=1)

    # set timezone (UTC)
    for i in range(len(ends_on_list)):
        ends_on_list[i] = ends_on_list[i].replace(tzinfo=timezone.utc)

    nomvar = "ETAS"
    etiket = ""

    img_dir = Path(f"data/rolling_testing_stabilization_and_length_1month_same_end_date")

    stations_obs_file = Path("/home/olh001/Python/station_positions_vis/stations_storm_surge_1_30.obs")
    data_dir_template = "/home/olh001/Python/storm_surge_pp/data/rdsps/precalculated_daily_and_rolling_avg_real_20181011_nd{:03d}_end_on_{:%Y%m%d%H}"

    # ===================================================

    # get list of stations
    obs_df = pd.read_csv(stations_obs_file, skiprows=2, sep="\s+", converters={"NO": lambda s: s.strip()})

    # get data for points from different folders
    rmn.fstopt(rmn.FSTOP_MSGLVL, rmn.FSTOPI_MSG_CATAST)
    df_list = []

    case_id_to_date_limits = {}

    for i_nd, nd in enumerate(running_avg_window_list):
        for end_t in ends_on_list:
            data_dir = Path(data_dir_template.format(nd, end_t))

            case_id = f"{end_t:%Y%m%d%H}"
            if case_id not in case_id_to_date_limits:
                start_t = end_t - backtrack_dt

                case_id_to_date_limits[case_id] = (start_t, end_t)

            df_list.append(get_data_for_obs_points(obs_df=obs_df, data_dir=data_dir,
                                                   case_id=case_id, subcase_id=f"{nd:03d}d",
                                                   nomvar=nomvar, etiket=etiket))

            print(case_id_to_date_limits)

    df_data = pd.concat(df_list, axis=1, sort=False)

    # do the plotting: 1 file per point containing a panel for a case, each panel containing a line for a case
    img_dir.mkdir(exist_ok=True)

    gs = None
    ncols = 2

    for st_id, st_name in zip(obs_df["NO"].values, obs_df["ID"].values):

        case_ids = sorted(np.unique([c[1] for c in df_data if c[0] == st_id]))

        # group on subplots
        nsubplots = len(case_ids)

        if gs is None:
            ncols = min(2, nsubplots)
            nrows = nsubplots // ncols + (0 if nsubplots % ncols == 0 else 1)
            gs = GridSpec(nrows, ncols, hspace=0.5)

        fig = plt.figure(figsize=(8, 6))

        ax = None
        color_cycle = None
        for sp_ind, ends_on in enumerate(case_ids):

            row = sp_ind // ncols
            col = sp_ind % ncols

            ax = fig.add_subplot(gs[row, col], sharey=ax)

            my_columns = sorted([c for c in df_data if c[0] == st_id and c[1] == ends_on])

            if color_cycle is None:
                color_cycle = [plt.cm.get_cmap("cool")(i) for i in np.linspace(0, 1, len(my_columns))]
            ax.set_prop_cycle("color", color_cycle)

            for c in my_columns:
                # select only data for the tracking period
                df_data[c][df_data.index >= case_id_to_date_limits[ends_on][0]].plot(ax=ax,
                                                                                     grid=True,
                                                                                     label=c[-1],
                                                                                     linewidth=0.7,
                                                                                     x_compat=True, rot=0,
                                                                                     )

            # styling
            ax.set_title(f"until {c[1]}")
            ax.grid(which="both", linestyle="dashed", linewidth=0.3)
            ax.set_ylim(*values_range[nomvar])
            ax.set_xlim(*case_id_to_date_limits[ends_on])
            if row == 0 and col == ncols - 1:
                ax.legend(loc="upper left", bbox_to_anchor=(1.03, 1), borderaxespad=0)

            ax.xaxis.set_major_locator(MonthLocator(bymonthday=1))
            ax.xaxis.set_major_formatter(DateFormatter("\n%b\n%Y"))
            ax.xaxis.set_minor_locator(DayLocator(bymonthday=range(5,30, 5)))
            ax.xaxis.set_minor_formatter(DateFormatter("%d"))

            for tick in ax.xaxis.get_major_ticks():
                tick.label1.set_horizontalalignment('center')

        fig.suptitle(f"{st_name} ({st_id})")

        fig_path = img_dir / f"{st_id}_{strutils.stname_to_fname(st_name)}.png"
        fig.savefig(str(fig_path), bbox_inches="tight", dpi=300)
        plt.close(fig)


def entry_001():
    """
    compare different running averaging interval lengths, i.e 30, 60, 90, 120,...days,
    during different seasons

    1 plot per station, containing a panel for different seasons, each panel has several plots (i.e for different
    durations of running means)

    :return:
    """

    running_avg_window_list = list(range(30, 390, 30))
    starts_on_list = [
        datetime(2016, 1, 1),
        datetime(2016, 4, 1),
        datetime(2016, 7, 1),
        datetime(2016, 10, 1),

    ]

    # set timezone (UTC)
    for i in range(len(starts_on_list)):
        starts_on_list[i] = starts_on_list[i].replace(tzinfo=timezone.utc)

    minimum_date = starts_on_list[0] + timedelta(days=360)

    nomvar = "ETAS"
    etiket = ""

    img_dir = Path(f"data/rolling_testing_stabilization_and_length_mindate{minimum_date:%Y%m%d%H}_fixed_ylim")

    stations_obs_file = Path("/home/olh001/Python/station_positions_vis/stations_storm_surge_1_30.obs")
    data_dir_template = "/home/olh001/Python/storm_surge_pp/data/rdsps/precalculated_daily_and_rolling_avg_real_20181011_nd{:03d}_start_on_{:%Y%m%d%H}"

    # ===================================================

    # get list of stations
    obs_df = pd.read_csv(stations_obs_file, skiprows=2, sep="\s+", converters={"NO": lambda s: s.strip()})

    # get data for points from different folders
    rmn.fstopt(rmn.FSTOP_MSGLVL, rmn.FSTOPI_MSG_CATAST)
    df_list = []
    for i_nd, nd in enumerate(running_avg_window_list):
        for start_t in starts_on_list:
            data_dir = Path(data_dir_template.format(nd, start_t))
            df_list.append(get_data_for_obs_points(obs_df=obs_df, data_dir=data_dir,
                                                   case_id=f"{start_t:%Y%m%d%H}", subcase_id=f"{nd:03d}d",
                                                   nomvar=nomvar, etiket=etiket))

    df_data = pd.concat(df_list, axis=1, sort=False)

    df_data = df_data[df_data.index >= minimum_date]

    # do the plotting: 1 file per point containing a panel for a case, each panel containing a line for a case
    img_dir.mkdir(exist_ok=True)

    gs = None
    ncols = 2

    for st_id, st_name in zip(obs_df["NO"].values, obs_df["ID"].values):

        case_ids = sorted(np.unique([c[1] for c in df_data if c[0] == st_id]))

        # group on subplots
        nsubplots = len(case_ids)

        if gs is None:
            ncols = min(2, nsubplots)
            nrows = nsubplots // ncols + (0 if nsubplots % ncols == 0 else 1)
            gs = GridSpec(nrows, ncols, hspace=0.2)

        fig = plt.figure(figsize=(8, 6))

        ax = None
        color_cycle = None
        for sp_ind, starts_on in enumerate(case_ids):
            row = sp_ind // ncols
            col = sp_ind % ncols

            ax = fig.add_subplot(gs[row, col], sharex=ax, sharey=ax)

            my_columns = sorted([c for c in df_data if c[0] == st_id and c[1] == starts_on])

            if color_cycle is None:
                color_cycle = [plt.cm.get_cmap("cool")(i) for i in np.linspace(0, 1, len(my_columns))]
            ax.set_prop_cycle("color", color_cycle)

            for c in my_columns:
                df_data[c].plot(ax=ax, grid=True, label=c[-1], linewidth=0.7)

            # styling
            ax.set_title(f"start from {c[1]}")
            ax.grid(which="major", linestyle="dashed", linewidth=0.3)
            ax.set_ylim(*values_range[nomvar])
            if row == 0 and col == ncols - 1:
                ax.legend(loc="upper left", bbox_to_anchor=(1.03, 1), borderaxespad=0)

        fig.suptitle(f"{st_name} ({st_id})")

        fig_path = img_dir / f"{st_id}_{strutils.stname_to_fname(st_name)}.png"
        fig.savefig(str(fig_path), bbox_inches="tight", dpi=300)
        plt.close(fig)


def main():
    # common start time
    entry_001()

    # common end time
    # entry_002()


if __name__ == '__main__':
    main()