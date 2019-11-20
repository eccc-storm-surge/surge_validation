# Warning: it is better to submit this script, might take a lot of memory and time to ttide

# plot co-tidal range for different members
import logging
from datetime import datetime, timezone
from pathlib import Path

from matplotlib.gridspec import GridSpec
from rpnpy.librmn import all as rmn

from tidal_constituents.get_constituents_nd import get_constituents, reshape_constituents_to_mask
from utils.io_utils import fst

import numpy as np

from cartopy import crs as ccrs
import matplotlib.pyplot as plt
from matplotlib import cm

rmn.fstopt(rmn.FSTOP_MSGLVL, rmn.FSTOPI_MSG_FATAL)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_projection():
    return ccrs.Orthographic(central_longitude=-60, central_latitude=50)
    # return ccrs.PlateCarree(central_longitude=-60)


def plot_cotidal_range_for_member(member_id, ax, data, amp_clevs=np.arange(0, 1.5, 0.05), show_cb=False,
                                  plot_phase=True, plot_perturbations=True):
    lons, lats = data["coords"]
    amp = data["amp"]

    if plot_phase:
        pha = data["phase"]
    else:
        pha = None

    if not plot_perturbations:
        csf = ax.contourf(lons, lats, amp,
                          levels=amp_clevs,
                          transform=ccrs.PlateCarree(),
                          cmap=cm.get_cmap("Spectral_r", len(amp_clevs) - 1),
                          extend="max")
    else:
        amp_clevs = np.arange(-0.1, 0.11, 0.01)
        csf = ax.contourf(lons, lats, amp,
                          levels=amp_clevs,
                          transform=ccrs.PlateCarree(),
                          cmap=cm.get_cmap("bwr", len(amp_clevs) - 1),
                          extend="both")


    if plot_phase:
        cs = ax.contour(lons, lats, pha,
                        levels=np.arange(-360, 360, 10),
                        transform=ccrs.PlateCarree(),
                        colors="k",
                        linewidths=0.1)

        ax.clabel(cs, cs.levels[::3], fmt="%d", fontsize=2)

    cb = plt.colorbar(csf, ax=ax, shrink=0.98)
    ax.coastlines(resolution='50m', linewidth=0.1)

    # ax.set_title(m_id)
    ax.annotate(member_id, (0.1, 0.7), xycoords="axes fraction")
    cb.ax.set_visible(show_cb)


def plot_amp_phase_ens_rmsd(lons, lats, constituents, img_dir: Path, sel_constituent_names=("M2",)):
    # Plotting
    proj = get_projection()

    ncols = 2
    nrows = 1
    gs = GridSpec(nrows, ncols, hspace=0.0, wspace=0.1)

    fig = plt.figure(figsize=(10, 4))

    par_to_clevs = {
        "amp": np.arange(0, 0.21, 0.01),
        "phase": np.arange(0, 20.5, 0.5)

    }

    ref_member_id = "000"

    for cn in sel_constituent_names:
        img_file = img_dir / f"amp_pha_rmsd_{cn}.png"

        for i, par in enumerate(["amp", "phase"]):
            show_cb = True

            ref = constituents[ref_member_id][cn][par]
            other = np.asarray([constituents[m][cn][par] for m in constituents if m != ref_member_id])

            delta = other - ref[np.newaxis, :]
            if par.startswith("pha"):
                delta = np.ma.min([(delta + 360) ** 2, (delta - 360) ** 2, delta ** 2], axis=0)
            else:
                delta = delta ** 2

            rmsd = (np.mean(delta, axis=0)) ** 0.5

            logger.debug(f"rmsd({par}): min={rmsd.min()}; max={rmsd.max()}")

            to_plot = {
                "coords": (lons, lats),
                "amp": rmsd,
                "phase": None

            }

            r, c = i // ncols, i % ncols

            ax = fig.add_subplot(gs[r, c], projection=proj)

            plot_cotidal_range_for_member(member_id=par, ax=ax, data=to_plot,
                                          show_cb=show_cb, amp_clevs=par_to_clevs[par],
                                          plot_phase=False)

        fig.savefig(img_file, bbox_inches="tight", dpi=300)


def plot_cotidal_range(lons, lats, constituents: dict, img_dir: Path = Path("data/plots"), sel_constituent_names=("M2",)):
    """
    :param lats:
    :param lons:
    :param sel_constituent_names: names of constituents to be plotted
    :param constituents: {member_id: dictionary of constituent phase and amplitude fields}
    :param img_dir:
    """

    # Plotting
    proj = get_projection()

    ncols = 4

    nrows = len(constituents) // ncols + int(len(constituents) % ncols != 0)
    gs = GridSpec(nrows, ncols, hspace=0.1, wspace=-0.1)

    debug_points = [
        (308, 13),
        (83, 39)
    ]

    fig = plt.figure(figsize=(16, 16))

    for cn in sel_constituent_names:
        img_file = img_dir / f"cotidal_range_{cn}.png"

        control_amp = None

        for i, (member_id, constit_fields) in enumerate(constituents.items()):
            show_cb = (i == 0) or (i == len(constituents) - 1)

            amp = constit_fields[cn]["amp"] if i == 0 else constit_fields[cn]["amp"] - control_amp

            to_plot = {
                "coords": (lons, lats),
                "amp": amp,
                "phase": constit_fields[cn]["phase"]
            }

            if i == 0:
                control_amp = amp

            r, c = i // ncols, i % ncols

            ax = fig.add_subplot(gs[r, c], projection=proj)

            plot_cotidal_range_for_member(member_id=member_id, ax=ax, data=to_plot, show_cb=show_cb,
                                          plot_perturbations=(i > 0))

            # debug output
            logger.debug(f"----member {member_id}----")
            for p in debug_points:
                logger.debug(f"point {p}")
                logger.debug(f"lat={lats[p[0], p[1]]}; lon={lons[p[0], p[1]]}")
                logger.debug(f"amp={constit_fields[cn]['amp'][p[0], p[1]]}")
                logger.debug(f"phase={constit_fields[cn]['phase'][p[0], p[1]]}")

        fig.savefig(img_file, bbox_inches="tight", dpi=400)


def test():
    exp_label = "WT_out_1yr_ttide"
    img_dir = Path(f"data/plots/cotidal_ranges_{exp_label}")

    data_dir = Path("/home/olh001/.suites/resps_tides_perturb/forecast/hub/eccc-ppp2/gridpt/tides_1yr")

    assert data_dir.is_dir()

    beg_time = datetime(2018, 4, 16, tzinfo=timezone.utc)
    end_time = datetime(2019, 4, 16, tzinfo=timezone.utc)

    n_members = 21

    img_dir = img_dir / f"{beg_time:%Y%m%d%H}_{end_time:%Y%m%d%H}"
    img_dir.mkdir(exist_ok=True, parents=True)

    grid_file = Path("/home/olh001/.suites/resps/constants/griddefs/grid-atlantic_1_12.fst")
    lons, lats, mask = fst.get_coords_and_mask(grid_file, nomvar="MGB", use_maskrec=False)

    query = {
        "nomvar": "SSHT", "typvar": "P@",
        "beg_time": beg_time, "end_time": end_time,
        "n_b2b_hours": (end_time - beg_time).total_seconds() // 3600
    }

    member_ids = [f"{i:03d}" for i in range(n_members)]

    data = fst.get_b2b_data_from_dir(src_dir=data_dir, member_ids=member_ids, data_query=query, data_mask=mask).squeeze()

    logger.debug([data[0, 0].shape, type(data[0, 0])])

    logger.debug(f"Finished reading data into memory: data.shape = {data.shape}")

    constituents = {
        member_id: get_constituents(data[member_index, :, :], lat=lats[mask], dt_hours=1, nprocs=6)
        for member_index, member_id in enumerate(member_ids)
    }

    # reshape constituents to 2d fields
    for member_id, member_costituents in constituents.items():
        reshape_constituents_to_mask(member_costituents, mask=mask)

    # do the plotting
    plot_cotidal_range(
        lons, lats, constituents, img_dir=img_dir,
    )

    plot_amp_phase_ens_rmsd(lons, lats, constituents, img_dir=img_dir, sel_constituent_names=("M2",))


def plot_M2O1K1S2N2_perturbations():
    """
    5 constituents perturbed with nwatl
    """

    constit_names = ["M2", "O1", "K1", "S2", "N2"]

    exp_label = "WT_perturb_" + "".join(constit_names)
    img_dir = Path(f"data/plots/cotidal_ranges_{exp_label}")

    data_dir = Path("/home/olh001/.suites/resps_tides_perturb_nwatl_O1M2K1N2S2_invert_scaling/forecast/hub/eccc-ppp2/gridpt/tides")

    assert data_dir.is_dir()

    beg_time = datetime(2018, 8, 25, tzinfo=timezone.utc)
    end_time = datetime(2019, 4, 16, tzinfo=timezone.utc)

    n_members = 21

    img_dir = img_dir / f"{beg_time:%Y%m%d%H}_{end_time:%Y%m%d%H}"
    img_dir.mkdir(exist_ok=True, parents=True)

    grid_file = Path("/home/olh001/.suites/resps/constants/griddefs/grid-atlantic_1_12.fst")
    lons, lats, mask = fst.get_coords_and_mask(grid_file, nomvar="MGB", use_maskrec=False)

    query = {
        "nomvar": "SSHT", "typvar": "P@",
        "beg_time": beg_time, "end_time": end_time,
        "n_b2b_hours": 24
    }

    member_ids = [f"{i:03d}" for i in range(n_members)]

    data = fst.get_b2b_data_from_dir(src_dir=data_dir, member_ids=member_ids, data_query=query, data_mask=mask).squeeze()

    logger.debug([data[0, 0].shape, type(data[0, 0])])

    logger.debug(f"Finished reading data into memory: data.shape = {data.shape}")

    constituents = {
        member_id: get_constituents(data[member_index, :, :], lat=lats[mask], dt_hours=1, nprocs=3,
                                    constitnames=constit_names)
        for member_index, member_id in enumerate(member_ids)
    }

    # reshape constituents to 2d fields
    for member_id, member_costituents in constituents.items():
        reshape_constituents_to_mask(member_costituents, mask=mask)

    # do the plotting
    plot_cotidal_range(
        lons, lats, constituents, img_dir=img_dir,
    )

    plot_amp_phase_ens_rmsd(lons, lats, constituents, img_dir=img_dir, sel_constituent_names=constit_names)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "plot_M2O1K1S2N2_perturbations":
            logger.info(f"Launching {sys.argv[1]}")
            plot_M2O1K1S2N2_perturbations()
    else:
        test()


