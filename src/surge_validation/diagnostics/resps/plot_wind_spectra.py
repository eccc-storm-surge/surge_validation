"""
Get wind cross spectra at sel points
"""
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import percache
import pytz
from pykdtree.kdtree import KDTree
from rpnpy.librmn import all as rmn
import numpy as np
from rpnpy.rpndate import RPNDate

from surge_validation.detiding_validation.config import default_params
from surge_validation.utils.crosspec import crosspec
from surge_validation.utils.geo import lat_lon

import pandas as pd

from joblib import Parallel, delayed

cache_path = Path("/home/olh001/data/ppp4/caches/surge_validation_plot_wind_spectra")

get_ts_cache = percache.Cache(str(cache_path))


def read_file(f: Path, t_beg: datetime, t_end: datetime, indices, nomvar="UU", max_leadhour=12):
    fu = rmn.fstopenall(str(f))
    keys = rmn.fstinl(fu, nomvar=nomvar)

    data_store = {}
    for rec in [rmn.fstluk(k) for k in keys]:
        t = RPNDate(rec["datev"]).toDateTime()

        if t > t_end:
            continue
        if t < t_beg:
            continue

        if max_leadhour >= 0:
            if rec["npas"] * rec["deet"] / 60 >= max_leadhour:
                continue

        data_store[t] = rec["d"].flatten()[indices]

    rmn.fstcloseall(fu)
    return pd.DataFrame.from_dict(data_store, orient="index")


@get_ts_cache
def get_ts(inp_dir: Path,
           t_beg: datetime, t_end: datetime,
           stid_to_lonlat: OrderedDict,
           member_id: str = "000", max_lead=12,
           nomvar="UU", n_jobs=5):
    """
    :param member_id: file names should end with member_id
    :param inp_dir:
    :param t_beg:
    :param t_end:
    :param stid_to_lonlat:
    """

    stid_list = [stid for stid in stid_to_lonlat]
    coords_t = np.array([stid_to_lonlat[stid] for stid in stid_list])

    indices = get_point_indices_on_grid(inp_dir=inp_dir,
                                        nomvar=nomvar,
                                        coords_target=coords_t)

    f_list = [f for f in inp_dir.iterdir() if f.name.endswith(member_id)]

    df_list = Parallel(n_jobs=n_jobs)(delayed(read_file)(f, t_beg, t_end, indices, nomvar=nomvar) for f in f_list)
    df = pd.concat(df_list, axis=0)
    df.columns = stid_list
    df.sort_index(inplace=True)
    return df


def get_point_indices_on_grid(inp_dir: Path, coords_target, nomvar="UU"):
    for f in inp_dir.iterdir():
        fu = rmn.fstopenall(str(f))
        keys = rmn.fstinl(fu, nomvar=nomvar)

        # get indices of the points of interest
        rec = rmn.fstprm(keys[0])
        grd = rmn.readGrid(fu, rec)

        coords_0 = rmn.gdll(grd["subgrid"][0])
        coords_1 = rmn.gdll(grd["subgrid"][1])

        lon_s = np.hstack([coords_1["lon"], coords_0["lon"]])
        lat_s = np.hstack([coords_1["lat"], coords_0["lat"]])

        xs, ys, zs = lat_lon.lon_lat_to_cartesian(lon_s.flatten(), lat_s.flatten())
        data_s = np.array(list(zip(xs, ys, zs)), dtype="f4")
        ktree = KDTree(data_s)
        xt, yt, zt = lat_lon.lon_lat_to_cartesian(coords_target[:, 0], coords_target[:, 1])

        dists, indices = ktree.query(np.array(list(zip(xt, yt, zt)), dtype="f4"), k=1)
        return indices


def main():
    img_dir = Path("data/plots/wind_spectra")
    img_dir.mkdir(exist_ok=True, parents=True)

    stid_to_lonlat = OrderedDict([
        ("1700", (-63.080000, 46.170000)),
        ("2985", (-68.420000, 48.580000))
    ])

    stid_dict = default_params.station_dict

    member_id = "000"

    ws_dict = OrderedDict()
    pn_dict = OrderedDict()

    # phase 1
    t_beg = datetime(2018, 9, 1, tzinfo=pytz.utc)
    t_end = datetime(2019, 4, 1, tzinfo=pytz.utc)
    data_dir = Path("/home/olh001/data/ppp4/model_data/geps/wind_phase1")

    uu = get_ts(data_dir,
                t_beg=t_beg, t_end=t_end, stid_to_lonlat=stid_to_lonlat,
                member_id=member_id, nomvar="UU", n_jobs=20)

    vv = get_ts(data_dir,
                t_beg=t_beg, t_end=t_end, stid_to_lonlat=stid_to_lonlat,
                member_id=member_id, nomvar="VV", n_jobs=20)

    pn = get_ts(data_dir,
                t_beg=t_beg, t_end=t_end, stid_to_lonlat=stid_to_lonlat,
                member_id=member_id, nomvar="PN", n_jobs=20)


    ws_dict["phase1"] = (uu ** 2 + vv ** 2) ** 0.5
    pn_dict["phase1"] = pn

    # phase 2
    t_beg = datetime(2019, 9, 1, tzinfo=pytz.utc)
    t_end = datetime(2020, 4, 1, tzinfo=pytz.utc)

    data_dir = Path("/home/olh001/data/ppp4/model_data/geps/wind_phase2")

    uu = get_ts(data_dir,
                t_beg=t_beg, t_end=t_end, stid_to_lonlat=stid_to_lonlat,
                member_id=member_id, nomvar="UU", n_jobs=20)

    vv = get_ts(data_dir,
                t_beg=t_beg, t_end=t_end, stid_to_lonlat=stid_to_lonlat,
                member_id=member_id, nomvar="VV", n_jobs=20)

    pn = get_ts(data_dir,
                t_beg=t_beg, t_end=t_end, stid_to_lonlat=stid_to_lonlat,
                member_id=member_id, nomvar="PN", n_jobs=20)

    ws_dict["phase2"] = (uu ** 2 + vv ** 2) ** 0.5
    pn_dict["phase2"] = pn

    import matplotlib.pyplot as plt
    plt.rcParams["font.size"] = 13

    fontweight = "semibold"
    plt.rcParams["font.weight"] = fontweight
    plt.rcParams["axes.titleweight"] = fontweight
    plt.rcParams["axes.labelsize"] = 13
    plt.rcParams["axes.labelweight"] = fontweight
    plt.rcParams["figure.titleweight"] = fontweight

    M = 100
    for stid in stid_to_lonlat:
        fig = plt.figure(figsize=(8.5, 5.5))
        ax = fig.gca()
        ax.set_title(f"{stid_dict[stid]} ({stid})")
        for label, wspd in ws_dict.items():
            f, p = crosspec(M, wspd[stid].values)
            ax.semilogy(24 * f, p, label=label)
        ax.legend()
        ax.grid(linestyle="dashed")

        fig.savefig(img_dir / f"wsp_power_spectra_{stid}.pdf")


    for stid in stid_to_lonlat:
        fig = plt.figure(figsize=(8.5, 5.5))
        ax = fig.gca()
        ax.set_title(f"{stid_dict[stid]} ({stid})")
        for label, pn in pn_dict.items():
            f, p = crosspec(M, pn[stid].values)
            ax.semilogy(24 * f, p, label=label)
        ax.legend()
        ax.set_xlabel("Cycles per day")
        ax.grid(linestyle="dashed")

        fig.savefig(img_dir / f"pn_power_spectra_{stid}.pdf")



if __name__ == '__main__':
    main()
