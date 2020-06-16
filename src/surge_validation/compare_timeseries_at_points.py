from collections import OrderedDict
from datetime import datetime
from pathlib import Path
import pandas as pd
from matplotlib.dates import HourLocator
from matplotlib.gridspec import GridSpec
from rpnpy.librmn import all as rmn
from rpnstd import RPNDate
import matplotlib.pyplot as plt

from pandas.tseries import offsets



def get_rolling_avg_timeseries_for_points(ij_to_stname, running_avg_dir:Path=None, etiket=""):
    files_to_read = [str(f) for f in running_avg_dir.iterdir()]
    funit = rmn.fstopenall(files_to_read)



    rmn.fstcloseall(funit)

    pass


def prep_for_fname(s):
    return s.replace(" ", "_").lower()


def entry_002():
    """
    3 months: levelled vs not-levelled
    """
    beg_date = datetime(2018, 7, 1, 0)
    end_date = datetime(2018, 10, 1, 0)

    label_base = "Unadjusted storm surge"

    label_to_data_dir = OrderedDict([
        # (label_base, Path("/home/olh001/.suites/rdsps/pseudo-analysis/hub/eccc-ppp2/gridpt/prog_archive_raw")),
        (label_base, Path("/home/olh001/.suites/rdsps/pseudo-analysis/hub/eccc-ppp2/gridpt/prog_archive_raw")),
        ("Storm surge (levelled)", Path("/home/olh001/Python/storm_surge_pp/data/rdsps/levelled_from_rdsps_pa_prog_archive_raw")),
    ])

    label_to_color = {
        "Unadjusted storm surge": "b",
        "Storm surge (levelled)": "r"
    }

    main_points_from_obs_file(beg_date=beg_date, end_date=end_date,
                              label_base=label_base,
                              label_to_data_dir=label_to_data_dir,
                              label_to_color=label_to_color)


def entry_001():
    """
    1 year: levelled vs not-levelled
    """
    beg_date = datetime(2017, 1, 1, 0)
    end_date = datetime(2018, 1, 1, 0)

    label_base = "Unadjusted storm surge"

    label_to_data_dir = OrderedDict([
        # (label_base, Path("/home/olh001/.suites/rdsps/pseudo-analysis/hub/eccc-ppp2/gridpt/prog_archive_raw")),
        (label_base, Path("/home/olh001/.suites/rdsps/pseudo-analysis/hub/eccc-ppp2/gridpt/prog_archive_raw")),
        ("Storm surge (levelled)", Path("/home/olh001/Python/storm_surge_pp/data/rdsps/levelled_from_rdsps_pa_prog_archive_raw")),
    ])

    label_to_color = {
        "Unadjusted storm surge": "b",
        "Storm surge (levelled)": "r"
    }

    main_points_from_obs_file(beg_date=beg_date, end_date=end_date,
                              label_base=label_base,
                              label_to_data_dir=label_to_data_dir,
                              label_to_color=label_to_color, ylim=(-0.3, 0.8))



def entry000():
    """
    Default run config
    """
    beg_date = datetime(2018, 7, 20, 0)
    end_date = datetime(2018, 10, 15, 18)

    label_base = "Unadjusted storm surge"

    label_to_data_dir = OrderedDict([
        # (label_base, Path("/home/olh001/.suites/rdsps/pseudo-analysis/hub/eccc-ppp2/gridpt/prog_archive_raw")),
        (label_base, Path("/home/olh001/.suites/rdsps/pseudo-analysis/hub/eccc-ppp2/gridpt/prog_archive_raw")),
        ("Storm surge (levelled)", Path("/home/olh001/.suites/rdsps/pseudo-analysis/hub/eccc-ppp2/gridpt/prog")),
    ])

    label_to_color = {
        "Unadjusted storm surge": "b",
        "Storm surge (levelled)": "r"
    }

    main_points_from_obs_file(beg_date=beg_date, end_date=end_date,
                              label_base=label_base,
                              label_to_data_dir=label_to_data_dir,
                              label_to_color=label_to_color)


def read_timeseries_for_indices_from_dir(label_to_data_dir, ij_to_stid: dict,
                                         beg_date: datetime = None,
                                         end_date: datetime = None,
                                         nomvar="ETAS", typvar="P@"):

    beg_date_s = f"{beg_date:%Y%m%d%H}_" if beg_date is not None else None
    end_date_s = f"{end_date:%Y%m%d%H}_" if end_date is not None else None

    label_to_ij_to_data = OrderedDict()
    for label in label_to_data_dir:
        label_to_ij_to_data[label] = {(i, j): {} for i, j in ij_to_stid}

    # read in the data for all points
    for label, data_dir in label_to_data_dir.items():
        for fp in data_dir.iterdir():

            # select data only from the region of interest
            if beg_date is not None:
                if fp.name < beg_date_s:
                    continue

            if end_date is not None:
                if fp.name > end_date_s:
                    continue

            funit = rmn.fstopenall(str(fp))
            keys = rmn.fstinl(funit, nomvar=nomvar, typvar=typvar)

            for k in keys:
                rec = rmn.fstluk(k)
                t = RPNDate(rec["datev"]).toDateTime()
                for i, j in ij_to_stid:
                    label_to_ij_to_data[label][i, j].update({t: rec["d"][i, j]})

            rmn.fstcloseall(funit)

    return label_to_ij_to_data


def main_points_from_obs_file(beg_date, end_date, label_base="", label_to_data_dir=None,
                              label_to_color=None, ylim=None, img_dir: Path = None):
    """
    Point definitions come from a .obs file
    :param img_dir:
    :param label_base:
    :param label_to_data_dir:
    :param label_to_color:
    """
    t1 = beg_date
    t2 = end_date
    beg_date_s = f"{t1:%Y%m%d%H}_"
    end_date_s = f"{t2:%Y%m%d%H}_"

    if img_dir is None:
        img_dir = Path(f"data/levelling_vs_nolevelling_timeseries_{beg_date_s}{end_date_s}_ts_only_same_scale_001")

    img_dir.mkdir(exist_ok=True)

    member_id = ""

    obs_file = Path("/home/olh001/Python/station_positions_vis/stations_storm_surge_1_30.obs")

    obs_df = pd.read_csv(obs_file, skiprows=2, sep="\s+")
    nomvar = "ETAS"
    typvar = "P@"

    # read in the timeseries data from fst files
    ij_to_stname = {(i, j): stname for i, j, stname in zip(obs_df["DATA.I"] - 1, obs_df["DATA.J"] - 1, obs_df["ID"])}
    ij_to_stid = {(i, j): stid for i, j, stid in zip(obs_df["DATA.I"] - 1, obs_df["DATA.J"] - 1, obs_df["NO"])}

    label_to_ij_to_data = read_timeseries_for_indices_from_dir(label_to_data_dir=label_to_data_dir,
                                                               ij_to_stid=ij_to_stid,
                                                               beg_date=beg_date,
                                                               end_date=end_date,
                                                               nomvar="ETAS", typvar="P@")
    # do the plotting
    for (i, j), stname in ij_to_stname.items():

        im_file = img_dir / f"{prep_for_fname(stname)}_I{i + 1}_J{j + 1}.png"

        gs = GridSpec(1, 1)
        fig = plt.figure(figsize=(8, 6))

        ax = fig.add_subplot(gs[0, 0])
        df_store = OrderedDict()
        for label in label_to_ij_to_data:
            data = label_to_ij_to_data[label][i, j]
            df = pd.DataFrame.from_dict(data, orient="index", columns=[label])
            df.sort_index(inplace=True)
            df_store[label] = df

            ax.xaxis.set_minor_locator(HourLocator())
            ax = df.plot(y=label, label=label, color=label_to_color[label], ax=ax, grid=True,
                         linewidth=0.5)

            if ylim is not None:
                ax.set_ylim(*ylim)

            ax.set_title(stname)

        # ax = fig.add_subplot(gs[1, 0], sharex=ax)
        # for label, df in df_store.items():
        #
        #     if label == label_base:
        #         continue
        #
        #     (df[label] - df_store[label_base][label_base]).plot(label=f"{label}--{label_base}", ax=ax,
        #                                                         color=label_to_color[label],
        #                                                         grid=True)

        ax.legend()

        fig.savefig(str(im_file), bbox_inches="tight", dpi=300)
        plt.close(fig)


if __name__ == '__main__':
    entry_001()
    # entry_002()