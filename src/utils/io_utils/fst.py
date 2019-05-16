from pathlib import Path

import pandas as pd
from rpnpy.librmn import all as rmn
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from rpnpy.rpndate import RPNDate

from utils.cache_utils import get_cache

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_txy(in_file: Path, vname: str):
    pass


def get_coords_and_mask(in_file: Path, nomvar="ETAS", use_maskrec=True):
    """

    :param in_file:
    :param nomvar:
    :param use_maskrec: if True uses a corresonding @@ record of the nomvar to get the mask values
    :return: lons, lats, mask
    """
    funit = rmn.fstopenall(str(in_file))

    typvar = "@@" if use_maskrec else ""
    key_mask = rmn.fstinl(funit, nomvar=nomvar, typvar=typvar)[0]

    meta_mask = rmn.fstprm(key_mask)
    mask = rmn.fstluk(key_mask)["d"] > 0.5

    grid = rmn.readGrid(funit, meta_mask)
    grid_ll = rmn.gdll(grid)
    lons, lats = grid_ll["lon"], grid_ll["lat"]

    rmn.fstcloseall(funit)

    return lons, lats, mask


def test_get_coords_and_mask():
    coords_path = Path("/home/olh001/.suites/resps/constants/griddefs/grid-atlantic_1_12.fst")

    lons, lats, mask = get_coords_and_mask(coords_path, nomvar="MGB", use_maskrec=False)

    # Plot the leading EOF expressed as covariance in the European/Atlantic domain.
    clevs = np.linspace(-75, 75, 11)
    proj = ccrs.Orthographic(central_longitude=-60, central_latitude=50)
    ax = plt.axes(projection=proj)
    ax.coastlines(resolution='50m', linewidth=0.5)
    ax.contourf(lons, lats, mask, levels=clevs,
                cmap=plt.cm.RdBu_r, transform=ccrs.PlateCarree())
    plt.title('EOF1 expressed as covariance', fontsize=16)

    plt.show()


if __name__ == '__main__':
    test_get_coords_and_mask()


def get_b2b_data_from_dir_parallel(args):
    src_dir, member_ids, data_query = args
    return get_b2b_data_from_dir(src_dir=src_dir, member_ids=member_ids, data_query=data_query)


def get_b2b_data_from_dir_for_member_id(args):
    src_dir, member_id, data_query = args

    if data_query is None:
        data_query = {}

    beg_t = data_query.get("beg_time", None)
    end_t = data_query.get("end_time", None)
    n_b2b_hours = data_query.get("n_b2b_hours", 12)

    file_list = [f for f in src_dir.iterdir() if f.name.endswith(member_id)]

    df_list = []

    for fpath in file_list:
        funit = rmn.fstopenall(str(fpath))

        keys = rmn.fstinl(funit, nomvar=data_query["nomvar"], typvar="P@")

        meta_list = [rmn.fstprm(k) for k in keys]
        vh_list = [rmn.convertIPtoPK(0, meta["ip2"], 0)[1].v1 for meta in meta_list]
        date_list = [RPNDate(meta["datev"]).toDateTime() for meta in meta_list]

        df = pd.DataFrame.from_dict(
            {"key": keys, "vh": vh_list, "vd": date_list}
        )
        df["path"] = fpath

        # filter by date
        if None not in [beg_t, end_t]:
            df = df[(df["vd"] >= beg_t) & (df["vd"] <= end_t)]

        # filter by valid hour
        df = df[(df["vh"] > 0) & (df["vh"] <= n_b2b_hours)]

        df_list.append(df)

        rmn.fstcloseall(funit)

    df = pd.concat(df_list)

    # read in the data into memory
    res = []
    for path, meta_df in df.groupby("path"):
        funit = rmn.fstopenall(str(path))
        res.extend([rmn.fstluk(int(k))["d"] for k in meta_df["key"].values])

        logger.debug(f"Read {len(res)} fields into memory")

        rmn.fstcloseall(funit)

    return np.asarray(res)


@get_cache()
def get_b2b_data_from_dir(src_dir: Path, member_ids, data_query=None):
    n_members = len(member_ids)
    input_list = list(zip([src_dir, ] * n_members, member_ids, [data_query, ] * n_members))
    return np.asarray([get_b2b_data_from_dir_for_member_id(inp) for inp in input_list])
