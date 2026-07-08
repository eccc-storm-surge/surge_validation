"""
Plot amplitudes and phases for different constituents calculated by ttide
for different obs points
"""
from collections import OrderedDict
from datetime import timedelta
from pathlib import Path

from matplotlib.gridspec import GridSpec
from ttide import TTideCon

from surge_validation.config import default_params
from ..utils import log_utils
from .. import io_manager
import numpy as np
import pandas as pd
import ttide
import matplotlib.pyplot as plt

from ..utils.strutils import stname_to_fname2


def calc_tides_spectra(ts_data, dt=timedelta(hours=1), lat=None) -> TTideCon:
    """

    :param ts_data: timeseries with time as index, and only one data column
    :param dt:
    :param lat:
    :return:
    """
    # removes leading and trailing nans
    ts_clean = ts_data[~ts_data.isna()].asfreq(dt)

    x = ts_clean.values.copy()

    # fill remaining nans with 0s
    nan_places = np.isnan(x)
    if np.any(nan_places):
        x[nan_places] = 0.

    return ttide.t_tide(
        x, dt=dt.total_seconds() / 3600., synth=0, ray=0.5,
        lat=lat, stime=ts_clean.index[0],
        out_style="classic"
    )


def plot_ttide_tide_spectra(lbl_to_station_to_ts: dict, img_dir: Path,
                            lbl_to_color: dict,
                            station_dict=default_params.station_dict,
                            fs=timedelta(hours=1), **kwargs):
    logger = log_utils.get_logger(__name__)
    img_dir.mkdir(exist_ok=True, parents=True)

    options = kwargs.get("options", {})
    plot_file_format = options.get("plot_file_format", "pdf")



    # cleanup the image dir
    for f in img_dir.iterdir():
        if f.is_file():
            f.unlink()

    _lbl_to_color = lbl_to_color.copy()
    _lbl_to_color.update({
        io_manager.OBS_COL_NAME: "k"
    })

    def __mysin(x):
        return np.sin(np.radians(x))

    def __mycos(x):
        return np.cos(np.radians(x))


    # get list off all stations
    all_stations = set()

    for lbl, station_to_ts in lbl_to_station_to_ts.items():
        all_stations.update({s for s in station_to_ts})

    lbl_list = sorted(lbl_to_station_to_ts)
    amp_limit = 0.01

    # calculate tide amplitudes and phases using ttide
    all_tide_props_mod = {}
    all_tide_props_obs = {}
    for station_id in all_stations:
        tide_props_mod = OrderedDict()
        tide_props_obs = OrderedDict()
        all_tide_props_mod[station_id] = tide_props_mod
        all_tide_props_obs[station_id] = tide_props_obs
        for lbl_idx, lbl in enumerate(lbl_list):

            data = lbl_to_station_to_ts[lbl][station_id]

            if len(data) == 0:
                logger.info(f"no data for {lbl} at {station_id}")
                continue

            lat = data[io_manager.LAT_COL_NAME].values[0]

            # calc obs
            # make it a list for uniformity
            tide_props_obs[lbl] = [calc_tides_spectra(data[io_manager.OBS_COL_NAME], dt=fs, lat=lat), ]

            # initialize to a list in case we deal with ensembles
            tide_props_mod[lbl] = []
            for cname in data.columns:
                if not cname.startswith("mod"):
                    continue

                tide_props_mod[lbl] += [calc_tides_spectra(data[cname], dt=fs, lat=lat)]

    # plotting =====================
    for station_id, tide_props_mod in all_tide_props_mod.items():

        fig = plt.figure(figsize=(10, 8), dpi=96)
        gs = GridSpec(3, 1, hspace=0.3)

        ax_amp = fig.add_subplot(gs[0, 0])
        ax_amp.set_title(f"{station_dict.get(station_id, station_id)}")

        ax_pha = fig.add_subplot(gs[1, 0])
        # ax_pha.set_title(f"Tide phase at {station_dict.get(station_id, station_id)}")

        ax_cpha = fig.add_subplot(gs[2, 0])

        tide_props_mod.update(
            {io_manager.OBS_COL_NAME: all_tide_props_obs[station_id][next(k for k in all_tide_props_obs[station_id])]}
        )

        for lbl, tide_con_list in tide_props_mod.items():

            label = "Obs" if lbl == io_manager.OBS_COL_NAME else lbl

            # actual plotting

            for tidecon_idx, tide_con in enumerate(tide_con_list):
                # logger.debug(tide_con)

                df = tidecon_to_dataframe(tide_con)

                ax_amp.plot(df.index, df["amp"], label=label, color=_lbl_to_color[lbl])
                ax_amp.fill_between(df.index, 
                                    df["amp"] - df["amp_err"], 
                                    df["amp"] + df["amp_err"],
                                    color=_lbl_to_color[lbl], alpha=0.4)

                ax_pha.plot(df.index, df["pha"], label=label, color=_lbl_to_color[lbl])
                ax_pha.fill_between(df.index, df["pha"] - df["pha_err"], df["pha"] + df["pha_err"],
                                    color=_lbl_to_color[lbl],
                                    alpha=0.4)

                label = None  # put the model label only once, relevant for ensembles

        # special metric to calculate phase errors
        for lbl, tide_con_list in tide_props_mod.items():
            if lbl == io_manager.OBS_COL_NAME:
                continue

            tide_con_obs = all_tide_props_obs[station_id][lbl][0]

            df_obs = tidecon_to_dataframe(tide_con_obs)

            # actual plotting
            for tide_con in tide_con_list:

                df_mod = tidecon_to_dataframe(tide_con)

                d = ((df_mod["pha"].map(__mycos) - df_obs["pha"].map(__mycos)) ** 2 +
                     (df_mod["pha"].map(__mysin) - df_obs["pha"].map(__mysin)) ** 2) ** 0.5

                xlabels = d.index.map(lambda s: "{}".format(s.decode().strip()))

                assert len(d) == len(df_obs)
                to_plot = np.ma.masked_where(df_obs.loc[d.index, "amp"].values.squeeze() <= amp_limit, d.values.squeeze())
                ax_cpha.plot(xlabels, to_plot, label=lbl, color=_lbl_to_color[lbl], marker=".")
                ax_cpha.set_xlim(ax_amp.get_xlim())

        ax_amp.set_ylabel("Amplitude [m]")
        ax_pha.set_ylabel(f"Phase")
        ax_cpha.set_ylabel(r"$\sqrt{\Delta^2\cos(\theta_0) + \Delta^2\sin(\theta_0)}$" + "\nphase error proxy" 
                           f"\n(for amplitudes > {amp_limit} [m])")


        # align x ticks labels
        for tick_lbl in ax_cpha.get_xticklabels():
            tick_lbl.set_ha("right")

        for idx, ax in enumerate(fig.get_axes()):
            ax.tick_params(axis="x", rotation=45)
            ax.grid(linestyle="dashed")

        ax_amp.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

        img_file = img_dir / f"{station_id}_{stname_to_fname2(station_dict[station_id])}.{plot_file_format}"
        fig.savefig(img_file, bbox_inches="tight", transparent=True)
        plt.close(fig)


def tidecon_to_dataframe(tidecon: TTideCon):
    logger = log_utils.get_logger(__name__)

    # change endiannes if needed
    # fu is read from file
    fu = tidecon["fu"]
    if fu.dtype.byteorder == ">":
        # force native byteorder
        fu = tidecon["fu"]
        fu = fu.view(fu.dtype.newbyteorder())

    df = pd.DataFrame({
        "nameu": tidecon["nameu"],
        "fu": fu * 24,
        "amp": tidecon["tidecon"][:, 0],
        "amp_err": tidecon["tidecon"][:, 1],
        "pha": tidecon["tidecon"][:, 2],
        "pha_err": tidecon["tidecon"][:, 3],

    })

    return df.sort_values("fu").set_index("nameu")
