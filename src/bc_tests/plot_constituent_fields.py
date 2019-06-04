from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from matplotlib.gridspec import GridSpec

from tidal_constituents.get_constituents_nd import get_constituents
from utils.io_utils import fst
import numpy as np
import matplotlib.pyplot as plt

from utils.io_utils.fst import get_b2b_data_from_dir
from cartopy import crs as ccrs

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def __inspect_field(data, label):
    lims = (data.min(), data.max())
    stats = (data.mean(), data.std()) + lims

    logger.debug(f"stats for {label}: {stats}")


def main():
    root_dir = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp1/gridpt/")
    img_dir = Path("data/plots/constituent_fields/DC_tides_minus_WT_v002")

    beg_time = datetime(2018, 4, 16, tzinfo=timezone.utc)
    end_time = datetime(2019, 4, 16, tzinfo=timezone.utc)

    img_dir = img_dir / f"{beg_time:%Y%m%d%H}_{end_time:%Y%m%d%H}"

    grid_file = Path("/home/olh001/.suites/resps/constants/griddefs/grid-atlantic_1_12.fst")
    lons, lats, mask = fst.get_coords_and_mask(grid_file, nomvar="MGB", use_maskrec=False)

    bc_mask_file = Path("/home//olh001/Python/fst_create_mask/test.fst")
    _, _, bc_mask = fst.get_coords_and_mask(bc_mask_file, nomvar="MGB", use_maskrec=False)

    data_query = OrderedDict([
        ("beg_time", beg_time),
        ("end_time", end_time),
        ("nomvar", "ETAS"),
        ("n_b2b_hours", 12)
    ])

    ref_label = "WT"

    label_to_data_dir = OrderedDict([
        ("DC_tides", root_dir / "prog_tides"),
        ("WT",       root_dir / "tides"),
    ])

    img_dir.mkdir(parents=True, exist_ok=True)

    label_to_member_ids = {
        "DC_tides": ["000"], "WT": [""]
    }

    label_to_nomvar = {
        "DC_tides": "ETAS",
        "WT": "SSHT"
    }

    i_list, j_list = np.where(mask)
    logger.debug(
        f"lon0={lons[0, 0]:.6f}; lat0={lats[0, 0]:.6f}, dlon={(lons[-1, -1] - lons[0, 0]) / lons.shape[0]:.6f}")

    label_to_constit_dict = OrderedDict()

    for label, data_dir in label_to_data_dir.items():
        data_query["nomvar"] = label_to_nomvar[label]
        data = get_b2b_data_from_dir(data_dir, member_ids=label_to_member_ids[label], data_query=data_query)
        logger.debug(f"data.shape = {data.shape}")

        etas = data.squeeze()

        ts_list = np.asarray([etas[:, i, j] for i, j in zip(i_list, j_list)])
        ts_list = ts_list.T

        logger.debug(f"ts_list.shape = {ts_list.shape}")

        lat_list = [lats[i, j] for i, j in zip(i_list, j_list)]

        label_to_constit_dict[label] = get_constituents(ts_list, lat=lat_list, dt_hours=1., nprocs=10, errcalc="cboot")

        del etas
        logger.info("Successfully executed get_constituents")

    constit_dict_structured = OrderedDict([(k, OrderedDict()) for k in label_to_constit_dict[ref_label]])

    for cn, cdata in label_to_constit_dict[ref_label].items():
        for cparam, cvals in cdata.items():
            constit_dict_structured[cn][cparam] = np.ma.masked_all(mask.shape)
            constit_dict_structured[cn][cparam][i_list, j_list] = label_to_constit_dict["DC_tides"][cn][cparam] - label_to_constit_dict["WT"][cn][cparam]

    plot_amp_and_phase(constit_dict_structured, img_dir, lons, lats, mask,
                       select_constituents=["O1", "K1", "S2", "M2", "N2"], label=f"DC_tides-WT")


def plot_amp_and_phase(constit_dict, img_dir: Path, lons, lats, mask, select_constituents=("MM", "MF"), label=""):
    if not img_dir.exists():
        img_dir.mkdir(exist_ok=True)

    # params_to_plot = ["amp", "phase"]
    params_to_plot = ["amp", "phase"]
    n_clevs = 23
    param_to_clev = {
        "amp": np.linspace(-0.1, 0.1, n_clevs),
        "phase": np.linspace(-60, 60, n_clevs)
    }

    proj = ccrs.Orthographic(central_longitude=-60, central_latitude=50)

    for cn in select_constituents:

        gs = GridSpec(len(params_to_plot), 1)

        fig = plt.figure()
        for row, param in enumerate(params_to_plot):

            clevs = param_to_clev[param]
            ax = fig.add_subplot(gs[row, 0], projection=proj)
            ax.coastlines(resolution='50m', linewidth=0.5)

            to_plot = np.ma.masked_where(~mask, constit_dict[cn][param])

            if param == "phase":
                to_plot[to_plot > 180] = to_plot[to_plot > 180] - 360
                to_plot[to_plot < -180] = to_plot[to_plot < -180] + 360

            cs = ax.contourf(lons, lats, to_plot, levels=clevs,
                             cmap=plt.cm.get_cmap("coolwarm", n_clevs),
                             transform=ccrs.PlateCarree(), extend="both")

            # __inspect_field(to_plot, f"{param}, {cn}")

            plt.colorbar(cs, ax=ax, shrink=0.98)
            title = fr"{cn}, ${{\Delta}}${param} = {label}"
            ax.set_title(title, fontsize=10)

        img_name = f"{cn}.png"
        img_path = img_dir / img_name
        fig.savefig(img_path, bbox_inches="tight", dpi=300)
        plt.close(fig)


if __name__ == '__main__':
    main()
