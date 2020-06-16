

# convert folder with rpn files to txt
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from surge_validation.utils.io_utils.fst import get_b2b_data_from_dir_for_member_id
from surge_validation.utils.io_utils import fst
import numpy as np


import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def save_coords_and_mask_to_txt(txt_dir: Path, lons, lats, mask):
    print("Saving lons, lats and mask to txt")
    np.savetxt(txt_dir / "lons.txt", lons.T, fmt="%.6e")
    np.savetxt(txt_dir / "lats.txt", lats.T, fmt="%.6e")
    np.savetxt(txt_dir / "mask.txt", mask.T, fmt="%.6e")


def main():
    n_hours_b2b = 12
    n_members = 21

    root_dir = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp1/gridpt/")
    txt_dir = Path("data/txt/resps_tides_experiments/")

    beg_time = datetime(2018, 4, 16, tzinfo=timezone.utc)
    end_time = datetime(2019, 2, 12, tzinfo=timezone.utc)

    txt_dir = txt_dir / f"{beg_time:%Y%m%d%H}_{end_time:%Y%m%d%H}"

    grid_file = Path("/home/olh001/.suites/resps/constants/griddefs/grid-atlantic_1_12.fst")
    lons, lats, mask = fst.get_coords_and_mask(grid_file, nomvar="MGB", use_maskrec=False)

    regenerate_coords_and_mask = False
    if regenerate_coords_and_mask:
        save_coords_and_mask_to_txt(txt_dir, lons, lats, mask)

    bc_mask_file = Path("/home//olh001/Python/fst_create_mask/test.fst")

    _, _, bc_mask = fst.get_coords_and_mask(bc_mask_file, nomvar="MGB", use_maskrec=False)

    data_query = {
        "beg_time": beg_time,
        "end_time": end_time,
        "nomvar": "ETAS",
        "n_b2b_hours": n_hours_b2b
    }

    label_to_data_dir = OrderedDict([
        # ("DC_tides", root_dir / "prog_tides"),
        # ("WT", root_dir / "tides"),
        ("DC_surge", root_dir / "prog_surge"),
        ("DC_surge_tides", root_dir / "prog_surge_tides")

    ])

    txt_dir.mkdir(parents=True, exist_ok=True)

    member_ids = [f"{i:03d}" for i in range(n_members)]

    label_to_member_ids = {
        "DC_tides": ["000"], "WT": [""],
        "DC_surge": member_ids,
        "DC_surge_tides": member_ids,
    }

    label_to_nomvar = {
        "DC_tides": "ETAS",
        "DC_surge": "ETAS",
        "DC_surge_tides": "ETAS",
        "WT": "SSHT"
    }

    for label, data_dir in label_to_data_dir.items():
        data_query["nomvar"] = label_to_nomvar[label]
        for member_id in label_to_member_ids[label]:
            cur_data_file = txt_dir / label / f"{beg_time:%Y%m%d%H}_{member_id}.txt"

            cur_data_file.parent.mkdir(exist_ok=True)

            if cur_data_file.exists():
                logger.info(f"{cur_data_file} already exists, won't redo.")
                continue

            args = [data_dir, member_id, data_query]
            data = get_b2b_data_from_dir_for_member_id(args)

            data_2d = np.concatenate([d for d in data], axis=-1)

            logger.debug(f"{data.shape}, {data_2d.shape}")

            logger.debug(f"Saving data into: {cur_data_file}")
            np.savetxt(cur_data_file, data_2d.T, fmt="%.6e")


if __name__ == '__main__':
    main()
