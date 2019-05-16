from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from matplotlib.ticker import FuncFormatter, MultipleLocator

from utils.io_utils.fst import get_b2b_data_from_dir
from tidal_constituents.get_constituents_nd import get_constituents
from utils.io_utils import fst
import numpy as np
import matplotlib.pyplot as plt


import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    root_dir = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp1/gridpt/")
    img_dir = Path("data/plots/tidal_analysis_bc_tides_dalcoast_vs_webtide")

    beg_time = datetime(2018, 4, 16, tzinfo=timezone.utc)
    end_time = datetime(2019, 2, 12, tzinfo=timezone.utc)

    img_dir = img_dir / f"{beg_time:%Y%m%d%H}_{end_time:%Y%m%d%H}"

    grid_file = Path("/home/olh001/.suites/resps/constants/griddefs/grid-atlantic_1_12.fst")
    lons, lats, mask = fst.get_coords_and_mask(grid_file, nomvar="MGB", use_maskrec=False)

    bc_mask_file = Path("/home/olh001/Python/fst_create_mask/test.fst")

    _, _, bc_mask = fst.get_coords_and_mask(bc_mask_file, nomvar="MGB", use_maskrec=False)

    data_query = {
        "beg_time": beg_time, "end_time": end_time, "nomvar": "ETAS", "n_b2b_hours": 12
    }

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

    data = OrderedDict()
    for label, data_dir in label_to_data_dir.items():
        data_query["nomvar"] = label_to_nomvar[label]
        data[label] = get_b2b_data_from_dir(data_dir, member_ids=label_to_member_ids[label], data_query=data_query)
        logger.debug(data[label].shape)

    # signal of surge-tide interactions
    etas = data["DC_tides"] - data["WT"]

    etas = etas.squeeze()

    i_list, j_list = np.where(bc_mask & mask)

    ts_list = np.asarray([etas[:, i, j] for i, j in zip(i_list, j_list)])
    ts_list = ts_list.T

    lat_list = [lats[i, j] for i, j in zip(i_list, j_list)]

    location_names = [f"I={i + 1}; J={j + 1}" for i, j in zip(i_list, j_list)]

    constit_dict = get_constituents(ts_list, lat=lat_list, dt_hours=1., nprocs=1)

    logger.debug(constit_dict["MM"]["amp"].mean())

    plot_constituents(constit_dict, location_names, img_dir=img_dir, snr_limit=0.)


def main_wtonly():
    root_dir = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp1/gridpt/")
    img_dir = Path("data/plots/tidal_analysis_bc_tides_webtideonly")

    beg_time = datetime(2018, 4, 16, tzinfo=timezone.utc)
    end_time = datetime(2019, 2, 12, tzinfo=timezone.utc)

    img_dir = img_dir / f"{beg_time:%Y%m%d%H}_{end_time:%Y%m%d%H}"

    grid_file = Path("/home/olh001/.suites/resps/constants/griddefs/grid-atlantic_1_12.fst")
    lons, lats, mask = fst.get_coords_and_mask(grid_file, nomvar="MGB", use_maskrec=False)

    bc_mask_file = Path("/home//olh001/Python/fst_create_mask/test.fst")

    _, _, bc_mask = fst.get_coords_and_mask(bc_mask_file, nomvar="MGB", use_maskrec=False)

    data_query = {
        "beg_time": beg_time, "end_time": end_time, "nomvar": "ETAS", "n_b2b_hours": 12
    }

    label_to_data_dir = OrderedDict([
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

    data = OrderedDict()
    for label, data_dir in label_to_data_dir.items():
        data_query["nomvar"] = label_to_nomvar[label]
        data[label] = get_b2b_data_from_dir(data_dir, member_ids=label_to_member_ids[label], data_query=data_query)
        print(data[label].shape)

    # signal of surge-tide interactions
    etas = data["WT"]

    etas = etas.squeeze()

    total_mask = bc_mask & mask

    i_list, j_list = np.where(total_mask)

    ts_list = np.asarray([etas[:, i, j] for i, j in zip(i_list, j_list)])
    ts_list = ts_list.T

    lat_list = [lats[i, j] for i, j in zip(i_list, j_list)]

    location_names = [f"I={i + 1}; J={j + 1}" for i, j in zip(i_list, j_list)]

    constit_dict = get_constituents(ts_list, lat=lat_list, dt_hours=1., nprocs=1)

    print(constit_dict["MM"]["amp"].mean())

    plot_constituents(constit_dict, location_names, img_dir=img_dir, snr_limit=0.)


def plot_constituents(constit_dict, location_names: list, img_dir: Path, snr_limit=2.):

    plt_var = "amp"
    constit_names = list(constit_dict.keys())

    for loc_index, loc_name in enumerate(location_names):
        fig = plt.figure()
        ax = plt.gca()

        vals = np.asarray([constit_dict[cn][plt_var][loc_index] for cn in constit_names])
        snr = np.asarray([constit_dict[cn]["snr"][loc_index] for cn in constit_names])
        fu = np.asarray([constit_dict[cn]["fu"][loc_index] for cn in constit_names])

        snr_crit = snr > snr_limit

        vals = vals[snr_crit]
        fu = fu[snr_crit]
        constit_names_cur = [cn for cn, sel in zip(constit_names, snr_crit) if sel]

        ax.grid(True, linewidth=0.3, linestyle="dashed")
        ax.bar(np.arange(len(vals)) + 0.5, vals, align="center", tick_label=constit_names_cur)

        title = f"{loc_name}, snr$\geq${snr_limit}"
        ax.set_title(title)
        ax.set_ylabel(plt_var)

        plt.setp(ax.get_xticklabels(), rotation=90, fontsize=6)

        img_path = img_dir / f"{plt_var}_{loc_name}.png"
        fig.savefig(img_path, bbox_inches="tight", dpi=300)

        # print(dict(zip(constit_names_cur, fu)))

        plt.close(fig)


if __name__ == '__main__':
    import time
    t0 = time.clock()
    main()
    main_wtonly()
    print(f"Execution time {time.clock() - t0} seconds")

