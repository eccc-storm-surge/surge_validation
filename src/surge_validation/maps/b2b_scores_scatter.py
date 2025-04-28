"""
Plot maps of points (scatter) with gamma^2 and \sigma_{\varepsilon} as colors
"""
import logging
from pathlib import Path

import cartopy
import pandas as pd
import numpy as np
from matplotlib import cm
from matplotlib.colors import BoundaryNorm
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from typing import List
import typing

from surge_validation import io_manager
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from surge_validation.config import default_params
import warnings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


SCORE_IDS = ["gamma2", "sigma", "rmse", "mePmO"]


SCORE_LABELS = {
    "gamma2": r"\gamma^2",
    "sigma": r"\sigma_{{\varepsilon}}",
    "mePmO": r"ME(P-O)",
    "rmse": r"RMSE"
}

SCORE_UNITS = {
    "gamma2": r"-",
    "sigma": r"m",
    "rmse": r"m",
    "mePmO": r"m",
}


def get_stid_to_coord_mapping(data_path) -> pd.DataFrame:

    ve_save = None
    for sep in [r"\s+", ","]:
        try:
            df_meta = pd.read_csv(data_path, header=None, sep=sep,
                                usecols=(io_manager.INFILE_STID_INDEX,
                                        io_manager.INFILE_LAT_INDEX,
                                        io_manager.INFILE_LON_INDEX),
                                converters={1: str}
                                )  # the file contains the station id lat and lon
            ve_save = None
            break
        except ValueError as ve:
            ve_save = ve

    if ve_save is not None:
        raise ve_save
    
    column_name_map = {
        io_manager.INFILE_STID_INDEX: io_manager.STID_COL_NAME,
        io_manager.INFILE_LAT_INDEX: io_manager.LAT_COL_NAME,
        io_manager.INFILE_LON_INDEX: io_manager.LON_COL_NAME
    }

    # group by station id the coordinates
    # df_meta = df_meta.groupby(df_meta[io_manager.STID_COL_NAME]).mean()

    df_meta.rename(column_name_map, axis="columns", inplace=True)
    df_meta.drop_duplicates(subset=[io_manager.STID_COL_NAME], inplace=True)
    df_meta.set_index(io_manager.STID_COL_NAME, inplace=True)
    logger.debug("\n%s\n", df_meta.head())
    return df_meta


def plot_score_maps(station_to_scores, 
                    mod_labels, 
                    data_paths,
                    img_dir: Path, map_label="",
                    score_ids: List[str] | None = None,
                    plot_params=None):
    """
    Args:
        station_to_scores: 
        score_ids: list of scores to plot
    """

    if score_ids is None:
        score_ids = SCORE_IDS[:2]


    if plot_params is None:
        plot_params = {}

    img_dir.mkdir(exist_ok=True, )

    station_info_list = [get_stid_to_coord_mapping(data_path=data_paths[mod_label]) for mod_label in mod_labels]
    station_info = pd.concat(station_info_list, axis=1, join="inner")

    # remove duplicated columns
    station_info = station_info.loc[:, ~station_info.columns.duplicated()]



    projection = plot_params.get("score_map_projection", ccrs.PlateCarree())

    only_one_model_label = len(set(mod_labels)) == 1

    gs = GridSpec(len(score_ids), len(set(mod_labels)) + (1 - int(only_one_model_label)),
                  hspace=0.1, wspace=0.2)

    if "score_map_figsize" not in plot_params:
        fig_width = 16
        if only_one_model_label:
            fig_width = 6

        figsize = (fig_width, 6)
    else:
        figsize = plot_params["score_map_figsize"]

    dpi = plot_params.get("score_map_dpi", 96)

    fig = plt.figure(figsize=figsize, dpi=dpi)

    val_mean = None

    labels = mod_labels if only_one_model_label else mod_labels + \
                                                     [r"$\Delta$" + f"[{mod_labels[1]} -\n  {mod_labels[0]}]"]

    # station coords
    coords_x = []
    coords_y = []


    label_to_scores = {}
    label_to_counts = {}
    for stid in station_info.index.intersection(station_to_scores):

        # if stid not in station_to_scores or station_to_scores[stid] is None:
        #     logger.info(f"Stats were not calculated for {stid} , not mapping it.")
        #     continue

        lat, lon = [station_info.loc[stid, cn] for cn in [io_manager.LAT_COL_NAME, io_manager.LON_COL_NAME]]

        x, y = projection.transform_point(lon, lat, ccrs.PlateCarree())

        coords_x.append(x)
        coords_y.append(y)

        for label in station_to_scores[stid]:
            if label not in label_to_scores:
                label_to_scores[label] = {score_id: [] for score_id in score_ids}
                label_to_counts[label] = {score_id: [] for score_id in score_ids}

            for score_id in score_ids:
                label_to_scores[label][score_id].append(station_to_scores[stid][label][score_id])
                label_to_counts[label][score_id].append(station_to_scores[stid][label]["count"])

    # 
    if len(label_to_scores) == 0:
        warnings.warn(f"no scores to plot a map, skipping: \n {station_to_scores = }")
        return

    
    # create grid of axes
    for i, score_id in enumerate(score_ids):
        for j, mod_label in enumerate(labels):

            
            if j < len(mod_labels):
                vals = np.array(label_to_scores[mod_label][score_id])
                counts = np.array(label_to_counts[mod_label][score_id])
            else:
                vals = np.array(label_to_scores[mod_labels[1]][score_id]) - \
                       np.array(label_to_scores[mod_labels[0]][score_id])
                counts = np.array(label_to_counts[mod_labels[1]][score_id])

            val_mean = (vals * counts).sum() / counts.sum()

            # plotting values
            ax = fig.add_subplot(gs[i, j], projection=projection)

            extend = "max"
            if j < len(mod_labels):
                clevs = default_params.score_clevs[score_id]
                cmap = cm.get_cmap("Oranges", len(clevs) - 1)
            else:
                extend = "both"
                clevs = default_params.score_clevs[f"{score_id}_diff"]
                cmap = cm.get_cmap("seismic", len(clevs) - 1)

            norm = BoundaryNorm(clevs, cmap.N)

            assert len(coords_x) == len(vals)

            img = ax.scatter(coords_x, coords_y, c=vals,
                             cmap=cmap,
                             norm=norm,
                             edgecolors="k",
                             linewidths=0.3,
                             s=plot_params.get("score_map_marker_size", None),
                             zorder=10)

            # create an axes on the right side of ax. The width of cax will be 5%
            # of ax and the padding between cax and ax will be fixed at 0.05 inch.
            divider = make_axes_locatable(ax)
            cb_position = plot_params.get("score_map_colorbar_position", "right")
            cax = divider.append_axes(cb_position,
                                      size=plot_params.get("score_map_colorbar_fraction", "5%"),
                                      pad=0.05,
                                      axes_class=plt.Axes)

            orientation = "horizontal" if cb_position in ["top", "bottom"] else "vertical"

            cb = plt.colorbar(img, cax=cax, extend=extend, orientation=orientation)
            cb.ax.set_visible(j > 0 or only_one_model_label)
            if j == len(mod_labels):

                ax.text(1.02, 1, f"$\Delta_{{\\rm min}}$={vals.min():.3f}\n$\Delta_{{\\rm max}}$={vals.max():.3f}", 
                        ha="left", va="top", transform=ax.transAxes)
                
                cb_axis = cb.ax.xaxis if orientation == "horizontal" else cb.ax.yaxis
                ha = "right" if orientation == "horizontal" else "left"
    
                # make sure all the ticks are shown
                cb_axis.set_ticks(cb_axis.get_ticklocs())

                fig.canvas.draw()

                tick_labels = [item for item in cb_axis.get_ticklabels()]
                top_lab = "NEW: better" if score_id not in ["mePmO", ] else "NEW-REF < 0"
                tick_labels[0].set_text(top_lab)
                tick_labels[0].set_color(cmap(0.0))

                bot_lab = "REF: better" if score_id not in ["mePmO", ] else "NEW-REF > 0"
                tick_labels[-1].set_text(bot_lab)
                tick_labels[-1].set_color(cmap(1.0))

                # print("cb ticklabels: ", tick_labels)

                cb_axis.set_ticklabels(tick_labels, ha=ha)

            if orientation == "horizontal":
                cb.ax.set_ylabel(f"({SCORE_UNITS[score_id]})", rotation="horizontal", ha="right", labelpad=20)
            else:
                cb.ax.set_xlabel(f"({SCORE_UNITS[score_id]})", rotation="horizontal")

            cax.tick_params(axis="x", rotation=45)

            ax.coastlines(resolution="10m", linewidth=0.05)
            lakes = cartopy.feature.NaturalEarthFeature(
                "physical", "lakes", "10m",
                edgecolor="k",
                facecolor="none"
            )
            ax.add_feature(lakes, linewidth=0.05)

            # set pannel titles
            if j < len(mod_labels):
                if i == 0:
                    ax.set_title(mod_label + "\n" + f"$\overline{{{SCORE_LABELS[score_id]}}} = {val_mean:.3e}$")
                else:
                    ax.set_title(f"$\overline{{{SCORE_LABELS[score_id]}}} = {val_mean:.3e}$")
            else:
                if i == 0:
                    ax.set_title(mod_label)

            bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9)

            # if j < len(mod_labels):
            #     ax.annotate(f"$\overline{{{score_labels[score_id][1:-1]}}} = {val_mean:.2f}$",
            #                 xy=(0.95, 1),
            #                 xycoords="axes fraction",
            #                 va="top",
            #                 ha="left",
            #                 bbox=bbox_props)

            if j < len(mod_labels):
                ylabel = fr"$\left({SCORE_LABELS[score_id]}\right)$"
                ax.text(0.0, 1, ylabel,
                        va="top",
                        ha="right",
                        transform=ax.transAxes)

            if only_one_model_label:
                logger.info(f"There is only 1 unique model label ({mod_label}), only plotting its scores.")
                break

    img = img_dir / f"map_scores{map_label}_{'-'.join(score_ids)}.pdf"
    
    # fig.tight_layout()
    fig.savefig(img, bbox_inches="tight", transparent=True)
    plt.close(fig)


def save_scores_to_txt(station_scores: dict, labels, img_dir: Path):
    """
    Dump scores to txt file
    :param station_scores: {station_id: {model_label: {score_label: score_value}}}
    :param labels:
    :param img_dir:
    """
    import warnings

    if len(station_scores) == 0:
        warnings.warn("No scores to save to txt: do nothing")
        return

    txt_dir = img_dir / "txt_scores"
    txt_dir.mkdir(exist_ok=True)


    print(station_scores)
    print(labels)

    station_ids = sorted(station_scores)
    
    print(station_ids)

    score_ids = sorted(station_scores[station_ids[0]][labels[0]])

    index = pd.MultiIndex.from_product([station_ids, score_ids], names=["station", "score"])

    data = {lbl: [] for lbl in labels}
    for lbl in labels:
        for st_id in station_ids:
            for score_id in score_ids:
                data[lbl].append(station_scores[st_id][lbl][score_id])

    df = pd.DataFrame(index=index, data=data)

    txt_file = txt_dir / "scores.csv"

    with txt_file.open(mode="w") as f:
        f.write(df.to_string())
