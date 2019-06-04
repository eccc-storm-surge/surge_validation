from datetime import datetime, timezone
from pathlib import Path
import numpy as np

from tidal_constituents.get_constituents_nd import get_constituents
from utils.io_utils.fst import get_coords_and_mask, get_b2b_data_from_dir

from rpnpy.librmn import all as rmn
rmn.fstopt(rmn.FSTOP_MSGLVL, rmn.FSTOPI_MSG_FATAL)

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def t_exp(fp: Path):
    return datetime.strptime(fp.name.split("_")[0], "%Y%m%d%H").replace(tzinfo=timezone.utc)


def calculate_rmse_between_files(f1: Path, query1: dict, f2: Path, query2: dict,
                                 mask=None,
                                 lead_hours_max=None):
    """
    Calculate rmse between 2 fst files
    :param mask:
    :param f1:
    :param query1:
    :param f2:
    :param query2:
    :return: 1d array of rmse for each point where mask (if provided) is 1
    """

    logger.debug(f"rmse for {f1.name} and {f2.name}")

    d1, d2 = query1["beg_time"], query1["end_time"]

    d = t_exp(f1)
    if not (d1 <= d <= d2):
        msg = f"Nothing to do for:\n {f1}\n{f2}\nSkipping ..."
        logger.debug(msg)
        return None, None

    funit1 = rmn.fstopenall(str(f1))
    funit2 = rmn.fstopenall(str(f2))

    # read the keys and make sure that the records are aligned in time
    keys1 = rmn.fstinl(funit1, nomvar=query1["nomvar"], typvar=query1["typvar"])

    metas1 = [rmn.fstprm(k) for k in keys1]

    keys2 = [rmn.fstinf(funit2, datev=m["datev"], nomvar=query2["nomvar"], typvar=query2["typvar"])["key"] for m in metas1]

    # select only first lead hours
    if lead_hours_max is not None:
        keys1 = [k for k, m in zip(keys1, metas1) if m["deet"] * m["npas"] <= lead_hours_max * 3600]
        keys2 = [k for k, m in zip(keys2, metas1) if m["deet"] * m["npas"] <= lead_hours_max * 3600]

    n = len(keys1)

    diffs = [rmn.fstluk(k2)["d"] - rmn.fstluk(k1)["d"] for k1, k2 in zip(keys1, keys2)]
    diffs = np.asarray(diffs)

    if mask is not None:
        i, j = np.where(mask)
        diffs = diffs[:, i, j]

    rmse = np.linalg.norm(diffs, axis=0)

    rmse = rmse.flatten()

    rmn.fstcloseall(funit1)
    rmn.fstcloseall(funit2)

    return rmse, n


def calculate_rmse(dir1: Path, query1: dict,
                   dir2: Path, query2: dict,
                   mask: np.ndarray = None,
                   lead_hours_max=12):
    """
    Calculate rmse between 2 simulations over a region defined by the mask, or over the complete domain if the
    mask is None
    :param lead_hours_max:
    :param mask:
    :param query2:
    :param query1:
    :param dir1:
    :param dir2: directory containing fst files
    """

    flist1 = sorted([f for f in dir1.iterdir() if f.name.endswith(query1["member_id"])], key=lambda x: x.name)
    flist2 = sorted([f for f in dir2.iterdir() if f.name.endswith(query2["member_id"])], key=lambda x: x.name)

    n_cur, rmse_cur = None, None

    msg = f"The number of files should be the same in {dir1} and {dir2}, but found {len(flist1)} and {len(flist2)}, respectively"
    assert len(flist1) == len(flist2), msg

    for f1, f2 in zip(flist1, flist2):

        rmse, n = calculate_rmse_between_files(f1=f1, query1=query1,
                                               f2=f2, query2=query2,
                                               mask=mask, lead_hours_max=lead_hours_max)

        if n is None:
            continue

        if n_cur is None:
            n_cur = n
            rmse_cur = rmse

        else:
            rmse_cur = ((rmse_cur ** 2 * n_cur + rmse ** 2 * n) / (n_cur + n)) ** 0.5
            n_cur += n

    return rmse_cur


def reshape_constituents_to_mask(constit_dict: dict, mask):
    for cn, param_to_vals in constit_dict.items():
        for param, cvals in param_to_vals.items():
            d = np.ma.masked_all(mask.shape)
            d[mask] = cvals
            param_to_vals[param] = d



def test():

    p1 = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp1/gridpt/prog_tides")
    p2 = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp1/gridpt/tides")

    beg_time = datetime(2018, 4, 16, tzinfo=timezone.utc)
    end_time = datetime(2019, 4, 16, tzinfo=timezone.utc)

    lead_hours_max = 6

    q1 = {
        "nomvar": "ETAS", "typvar": "P@", "member_id": "000",
        "beg_time": beg_time, "end_time": end_time,
        "member_ids": ("000",)
    }
    q2 = {
        "nomvar": "SSHT", "typvar": "P@", "member_id": "",
        "beg_time": beg_time, "end_time": end_time,
        "member_ids": ("",)
    }

    # get coordinates and mask
    lons, lats, msk = None, None, None
    for cf in p1.iterdir():
        lons, lats, msk = get_coords_and_mask(cf, nomvar=q1["nomvar"], use_maskrec=True)
        break

    # rmse between two simulation for the same period
    rmse = calculate_rmse(p1, q1, p2, q2, mask=msk, lead_hours_max=lead_hours_max)

    rmse_2d = np.ma.masked_all(msk.shape)
    rmse_2d[msk] = rmse

    i, j = np.where(msk)

    # get constituents from DC_tide outputs
    data = get_b2b_data_from_dir(p1, data_query=q1).squeeze()
    constituents1 = get_constituents(data[:, i, j], lat=lats[i, j], nprocs=10)

    # get tide constituents from WT outputs
    data = get_b2b_data_from_dir(p2, data_query=q2).squeeze()
    constituents2 = get_constituents(data[:, i, j], lat=lats[i, j], nprocs=10)

    del data

    # calculate relative error of amplitude

    reshape_constituents_to_mask(constituents1, mask=msk)
    reshape_constituents_to_mask(constituents2, mask=msk)

    ratio_amplitude = rmse_2d / constituents2["M2"]["amp"] * 100

    # calculate relative error, phase
    dphi = (constituents2["M2"]["phase"] - constituents1["M2"]["phase"])

    # get the shortest angular distance
    to_shift = np.abs(dphi) > np.abs(360 + dphi)
    dphi[to_shift] += 360 + dphi[to_shift]

    to_shift = np.abs(dphi) > np.abs(-360 + dphi)
    dphi[to_shift] += -360 + dphi[to_shift]

    phi = constituents2["M2"]["phase"]
    ratio_phase = dphi / np.abs(phi) * 100

    # diagnostic plotting
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, sharex="all", sharey="all", figsize=(10, 8))

    # plot rmse
    ax = axes[0, 0]
    cs = ax.contourf(rmse_2d.T, np.arange(0, 0.61, 0.01), extend="max")
    plt.colorbar(cs, ax=ax)
    ax.set_title(f"<rmse>={rmse.mean():.2f} m; lead={lead_hours_max:.1f} h")

    # plot rmse/A(M2)
    ax = axes[1, 0]
    cs = ax.contourf(ratio_amplitude.T, np.arange(0, 51, 1), extend="max")
    plt.colorbar(cs, ax=ax)
    ax.set_title(f"<rmse/A(M2)>={ratio_amplitude.mean():.1f} %; lead={lead_hours_max:.1f} h")

    # phase ratio
    ax = axes[0, 1]
    cs = ax.contourf(ratio_phase.T, np.arange(-20, 21, 1), extend="both")
    plt.colorbar(cs, ax=ax)
    ax.set_title(f"<dphi/|phi(M2)|>={ratio_phase.mean():.1f} %; lead={lead_hours_max:.1f} h")

    axes[1, 1].set_visible(False)

    beg_time_s = beg_time.strftime("%Y%m%d%H")
    end_time_s = end_time.strftime("%Y%m%d%H")
    fig.savefig(f"data/plots_rmse_DC_WT_{beg_time_s}-{end_time_s}_{lead_hours_max}h.png", dpi=300)

    logger.debug(f"Spatial mean rmse of surge (DC_tides - WT): {rmse.mean():.4f}")


if __name__ == '__main__':
    test()
