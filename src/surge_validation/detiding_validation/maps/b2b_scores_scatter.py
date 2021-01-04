"""
Plot maps of points (scatter) with gamma^2 and \sigma_{\varepsilon} as colors
"""
import logging
from pathlib import Path

import cartopy
import pandas as pd
from matplotlib import cm
from matplotlib.colors import BoundaryNorm
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1 import make_axes_locatable

from surge_validation.detiding_validation import io_manager
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from surge_validation.detiding_validation.config import default_params

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_stid_to_coord_mapping(data_path) -> pd.DataFrame:
    df_meta = pd.read_csv(data_path, header=None, sep=r"\s+",
                          usecols=(io_manager.INFILE_STID_INDEX,
                                   io_manager.INFILE_LAT_INDEX,
                                   io_manager.INFILE_LON_INDEX),
                          converters={1: str}
                          )  # the file contains the station id lat and lon

    df_meta.columns = [
        io_manager.STID_COL_NAME,
        io_manager.LAT_COL_NAME,
        io_manager.LON_COL_NAME
    ]

    # group by station id the coordinates
    df_meta = df_meta.groupby(df_meta[io_manager.STID_COL_NAME]).mean()

    logger.debug("\n%s\n", df_meta.head())
    return df_meta


def plot_score_maps(station_to_scores, mod_labels, data_paths,
                    img_dir: Path, map_label="",
                    plot_params=None):

    if plot_params is None:
        plot_params = {}

    img_dir.mkdir(exist_ok=True, )
    station_info = get_stid_to_coord_mapping(data_path=data_paths[mod_labels[0]])
    score_ids = ["gamma2", "sigma"]
    score_labels = {
        "gamma2": r"$\gamma^2$",
        "sigma": r"$\sigma_{\varepsilon}$"
    }

    projection = ccrs.PlateCarree()

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

    fig = plt.figure(figsize=figsize)

    val_mean = None

    # create grid of axes
    for i, score_id in enumerate(score_ids):

        labels = mod_labels if only_one_model_label else mod_labels + [r"$\Delta$" + f"[{mod_labels[1]} -\n  {mod_labels[0]}]"]
        for j, mod_label in enumerate(labels):
            ax = fig.add_subplot(gs[i, j], projection=projection)

            if i == 0:
                ax.set_title(mod_label)

            # plotting
            coords_x = []
            coords_y = []
            vals = []
            counts = []

            for stid in station_info.index:

                if stid not in station_to_scores or station_to_scores[stid] is None:
                    logger.info(f"Stats were not calculated for {stid}, not mapping it.")
                    continue

                lat, lon = [station_info.loc[stid, cn] for cn in [io_manager.LAT_COL_NAME, io_manager.LON_COL_NAME]]

                coords_x.append(lon)
                coords_y.append(lat)

                # plotting values
                if j < len(mod_labels):
                    vals.append(station_to_scores[stid][mod_label][score_id])

                    # mean score for all stations
                    counts.append(station_to_scores[stid][mod_label]["count"])
                    val_mean = sum([v * c for v, c in zip(vals, counts)]) / sum(counts)

                else:
                    vals.append(station_to_scores[stid][mod_labels[1]][score_id] - station_to_scores[stid][mod_labels[0]][score_id])


            # plotting values
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
                             s=plot_params.get("score_map_marker_size", None))

            logger.debug("\nvals=%s", vals)
            # create an axes on the right side of ax. The width of cax will be 5%
            # of ax and the padding between cax and ax will be fixed at 0.05 inch.
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right",
                                      size=plot_params.get("score_map_colorbar_fraction", "5%"),
                                      pad=0.05, axes_class=plt.Axes)
            cb = plt.colorbar(img, cax=cax, extend=extend)
            cb.ax.set_visible(j > 0 or only_one_model_label)
            ax.coastlines(resolution="10m", linewidth=0.2)
            lakes = cartopy.feature.NaturalEarthFeature(
                "physical", "lakes", "10m",
                edgecolor="k",
                facecolor="none",
                linewidth=0.2
            )
            ax.add_feature(lakes)

            bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9)

            if j < len(mod_labels):
                ax.annotate(f"$\overline{{{score_labels[score_id][1:-1]}}} = {val_mean:.2f}$",
                            xy=(-0.0, 0.99), xycoords="axes fraction", va="top", ha="right",
                            bbox=bbox_props)

            if j == 0:
                ax.text(-0.07, 0.55, score_labels[score_id], va="bottom", ha="center",
                        rotation="vertical", rotation_mode="anchor",
                        transform=ax.transAxes)

            if only_one_model_label:
                logger.info(f"There is only 1 unique model label ({mod_label}), only plotting its scores.")
                break

    img = img_dir / f"map_scores{map_label}.png"
    fig.canvas.draw()
    # fig.tight_layout()
    fig.savefig(img, bbox_inches="tight", dpi=300)
    plt.close(fig)


def save_scores_to_txt(station_scores: dict, labels, img_dir: Path):
    """
    Dump scores to txt file
    :param station_scores: {station_id: {model_label: {score_label: score_value}}}
    :param labels:
    :param img_dir:
    """

    txt_dir = img_dir / "txt_scores"
    txt_dir.mkdir(exist_ok=True)

    station_ids = sorted(station_scores)
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
