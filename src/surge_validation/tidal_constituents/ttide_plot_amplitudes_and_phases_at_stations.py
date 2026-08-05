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
from collections import defaultdict

from ..utils.strutils import stname_to_fname2


def calc_tides_spectra(ts_data, dt=timedelta(hours=1), lat=None) -> pd.DataFrame:
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

    tcon = ttide.t_tide(
        x, dt=dt.total_seconds() // 3600, synth=0, ray=0.9,
        lat=lat, stime=ts_clean.index[0],
        out_style="classic"
    )

    return tidecon_to_dataframe(tcon)



def get_constituent_names(all_tide_props):
    # get all constituent names
    const_sets = []
    for stid, tide_props_dict in all_tide_props.items():
        for lbl, [df, ] in tide_props_dict.items():
            const_sets.append(set(df.index))

    return sorted(set.intersection(*const_sets))

def plot_tide_error_summary_html(out_dir: Path, all_tide_props: dict, 
                                 station_dict: dict, station_id_to_coords: dict | None = None):
    """

    produce one summary file for each constituent

    Args:
        all_tide_props: dictionary station_id to dict {model-run-label or obs: dataframe}.
    """
    import cmath
    import hvplot
    import hvplot.pandas
    import panel
    import holoviews as hv
    from holoviews import opts as hvopts
    panel.extension("mathjax")

    out_dir.mkdir(exist_ok=True, parents=True)

    
    station_id_list = sorted(all_tide_props)
    all_labels = []
    for cname in get_constituent_names(all_tide_props):

        err_dict = defaultdict(list)
        
        for station_id in station_id_list:
            lbl_to_data = all_tide_props[station_id]
            
            if len(all_labels) == 0:
                all_labels = list([lbl for lbl in lbl_to_data if lbl != io_manager.OBS_COL_NAME])

            df_obs = lbl_to_data[io_manager.OBS_COL_NAME][0]


            for lbl, [df, ] in lbl_to_data.items():

                if lbl == io_manager.OBS_COL_NAME:
                    continue

                err_dict[("amp_bias", lbl)].append(df.loc[cname, "amp"] - df_obs.loc[cname, "amp"])
                err_dict[("amp_bias_unc_95", lbl)].append(df.loc[cname, "amp_err"] + df_obs.loc[cname, "amp_err"])

                # make sure the phase shift accounts for the 360deg periodicity
                err_dict[("phase_bias", lbl)].append(
                    np.angle(np.exp(1j * (
                        np.radians(
                            df.loc[cname, "pha"] - df_obs.loc[cname, "pha"]))
                        ), deg=True
                    )
                )
                
                err_dict[("phase_bias_unc_95", lbl)].append(df.loc[cname, "pha_err"] + df_obs.loc[cname, "pha_err"])

                err_dict[("complex_amp_error", lbl)].append(abs( df.loc[cname, "amp"] * cmath.exp(1j * np.radians(df.loc[cname, "pha"])) - 
                                                        df_obs.loc[cname, "amp"] * cmath.exp(1j * np.radians(df_obs.loc[cname, "pha"]))))

        err_df = pd.DataFrame.from_dict(err_dict)
        err_df["Station_Id"] = station_id_list
        err_df["Station_Name"] = [station_dict[sid] for sid in station_id_list]
        err_df = err_df.set_index("Station_Id")

        table_view = panel.widgets.Tabulator(err_df.sort_index(axis="columns"), disabled=True)


        opts = dict(shared_axes=False, xrotation=90)
        amp_err_title = "Amplitude bias [m]"
        cmplx_amp_err_title = r"$$\text{{Complex amplitude error }}|A_p e^{{i\phi_p}} - A_o e^{{i\phi_o}}|\text{{ [m]}}$$"
        phase_err_title = "Phase bias [deg]"
        amp_err_gr = err_df["amp_bias"].hvplot.line(title=amp_err_title).opts(**opts)
        complex_amp_err_gr = err_df["complex_amp_error"].hvplot.line(title="Complex amplitude error [m]").opts(**opts)
        phase_err_gr = err_df["phase_bias"].hvplot.line(title="Phase bias [deg]").opts(**opts)


        v_to_line_plot = {
            "amp": amp_err_gr, "phase": phase_err_gr
        }

        for lbl in all_labels:

            for v, gr in v_to_line_plot.items():
                sel_err_df = err_df[[(f"{v}_bias_unc_95", lbl), (f"{v}_bias", lbl)]]
                sel_err_df.columns = [f"{v}_bias_unc_95", f"{v}_bias"]
                v_to_line_plot[v] = (gr * sel_err_df.hvplot.errorbars(y=f"{v}_bias", yerr1=f"{v}_bias_unc_95")).opts(axiswise=True, **opts)



        column = panel.Column(
                f"Constituent: {cname}",
                panel.Row(table_view),
                v_to_line_plot["amp"], 
                panel.Row(complex_amp_err_gr), 
                panel.Row(v_to_line_plot["phase"])
        )

        if station_id_to_coords is not None:

            lon, lat = [[station_id_to_coords[sid][i] for sid in station_id_list] for i in range(2)]
            
            err_name_to_title = {
                "amp_bias": amp_err_title,
                "complex_amp_error": cmplx_amp_err_title, 
                "phase_bias": phase_err_title
            }

            for err_name, err_title in err_name_to_title.items():
                sel_err_df = err_df[err_name]
                clim = (sel_err_df[all_labels].min().min(), 
                        sel_err_df[all_labels].max().max())
                
                if clim[0] < 0:
                    abs_max = max([abs(v) for v in clim])
                    clim = (-abs_max, abs_max)
                    
                # plot error maps
                sel_err_df["lon"] = lon
                sel_err_df["lat"] = lat
                sel_err_df["Station_Name"] = [station_dict[sid] for sid in station_id_list]

                plots = []
                for lbl in all_labels:
                    cur_err_map = sel_err_df.hvplot.points(
                        x="lon", y="lat", c=lbl, cmap="seismic", title=f"{lbl}", 
                        geo=True, tiles="OSM", hover_cols=["Station_Id", "Station_Name"],
                        frame_width=500, frame_height=500, colorbar=True, clim=clim
                    )
                    plots.append(cur_err_map)
                
                layout = hv.Layout(plots).cols(len(plots))
                layout.opts(shared_axes=True)
                layout.values()[-1].Points.I.opts(colorbar=True)

                column.append(panel.Column(err_title, layout))

        hvplot.save(
            column, out_dir / f"{cname}.html"
        )



def plot_ttide_tide_spectra(lbl_to_station_to_ts: dict, img_dir: Path,
                            lbl_to_color: dict,
                            station_dict=default_params.station_dict,
                            fs=timedelta(hours=1), **kwargs):
    logger = log_utils.get_logger(__name__)
    img_dir.mkdir(exist_ok=True, parents=True)

    options = kwargs.get("options", {})
    plot_file_format = options.get("plot_file_format", "pdf")

    station_id_to_coords = {}

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

            if station_id not in station_id_to_coords:
                station_id_to_coords[station_id] = (data[io_manager.LON_COL_NAME].values[0], 
                                                    data[io_manager.LAT_COL_NAME].values[0])

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

            for tidecon_idx, df in enumerate(tide_con_list):
                # logger.debug(tide_con)

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

            df_obs = all_tide_props_obs[station_id][lbl][0]

            # df_obs = tidecon_to_dataframe(tide_con_obs)

            # actual plotting
            for df_mod in tide_con_list:

                d = ((df_mod["pha"].map(__mycos) - df_obs["pha"].map(__mycos)) ** 2 +
                     (df_mod["pha"].map(__mysin) - df_obs["pha"].map(__mysin)) ** 2) ** 0.5

                xlabels = d.index

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

    plot_tide_error_summary_html(img_dir / "tide-summary-html", 
                                 all_tide_props_mod, 
                                 station_dict=station_dict, 
                                 station_id_to_coords=station_id_to_coords)


def tidecon_to_dataframe(tidecon: TTideCon):
    # change endiannes if needed
    # fu is read from file
    fu = tidecon["fu"]
    # if fu.dtype.byteorder == ">":
    #     # force native byteorder
    #     fu = tidecon["fu"]
    #     fu = fu.view(fu.dtype.newbyteorder())

    df = pd.DataFrame({
        "nameu": [c if isinstance(c, str) else c.decode().strip() for c in tidecon["nameu"]],
        "fu": fu * 24,
        "amp": tidecon["tidecon"][:, 0],
        "amp_err": tidecon["tidecon"][:, 1],
        "pha": tidecon["tidecon"][:, 2],
        "pha_err": tidecon["tidecon"][:, 3],

    })

    return df.sort_values("fu").set_index("nameu")
