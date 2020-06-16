"""
Plot cotidal range of the perturbed text files given as input to webtide
"""
from pathlib import Path
import pandas as pd
from cartopy import crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib import cm


def read_wt_lon_lat(coords_file):
    df = pd.read_csv(coords_file, sep=r"\s+", header=None)
    lons, lats = df.iloc[:, 1].values, df.iloc[:, 2].values
    print(lons.min(), lons.max(), lats.min(), lats.max())
    return lons, lats


def get_projection():
    # return ccrs.Orthographic(central_longitude=-60, central_latitude=50)
    return ccrs.PlateCarree(central_longitude=0)


def get_rmsd_wt(member_to_data: dict, control_member="000"):

    amp_col = 1
    pha_col = 2

    res_keys = ["amp", "phase"]

    res = {}

    for col, rk in zip([amp_col, pha_col], res_keys):
        ref = member_to_data[control_member].iloc[:, col].values
        other = np.asarray([member_to_data[m].iloc[:, col].values for m in member_to_data if m != control_member])

        res[rk] = (np.mean((other - ref) ** 2, axis=0)) ** 0.5

    return res


def plot_amp_phase_ens_rmsd(lons, lats, elements, constituents, img_dir: Path, map_extent=None, cn="M2"):
    # Plotting
    proj = get_projection()

    ncols = 2
    nrows = 1
    gs = GridSpec(nrows, ncols, hspace=0.0, wspace=0.1)

    fig = plt.figure(figsize=(12, 4))

    par_to_clevs = {

        "M2": {
            "amp": np.arange(0, 0.21, 0.01),
            "phase": np.arange(0, 20.5, 0.5)
        },
        "O1": {
            "amp": np.arange(0, 0.06, 0.01),
            "phase": np.arange(0, 20.5, 0.5)
        }

    }

    ref_member_id = "000"

    img_file = img_dir / f"amp_pha_rmsd_{cn}.png"

    for i, par in enumerate(["amp", "phase"]):

        # assume that the amplitude is in col=1 and the phase is on col=2
        ref = constituents[ref_member_id][i + 1]
        other = np.asarray([constituents[m][i + 1] for m in constituents if m != ref_member_id])

        rmsd = (np.mean((other - ref[np.newaxis, :]) ** 2, axis=0)) ** 0.5

        r, c = i // ncols, i % ncols

        ax = fig.add_subplot(gs[r, c], projection=proj)
        ax.set_extent(map_extent)

        csf = ax.tricontourf(lons, lats, elements, rmsd,
                             levels=par_to_clevs[cn][par],
                             transform=proj,
                             cmap=cm.get_cmap("Spectral_r", len(par_to_clevs[cn][par]) - 1),
                             extend="max")
        ax.set_title(f"std({par})")

        cb = plt.colorbar(csf, ax=ax, shrink=0.98)
        ax.coastlines(resolution='50m', linewidth=0.1)

    fig.savefig(img_file, bbox_inches="tight", dpi=300)


def main():
    # inp_dir = Path("/home/olh001/.suites/resps_tides_perturb_nwatl/forecast/constants/wt_perturbations")
    inp_dir = Path("/home/olh001/Python/surge_validation/data/wt_perturbations_nwatl_1.0.3_O1")

    tidecor_domain = "nwatl"

    img_dir = Path(f"data/plots/cotidal_range_wt_in_{tidecor_domain}_O1")
    img_dir.mkdir(exist_ok=True, parents=True)

    coords_file = Path(f"/home/olh001/C_CPP/WebTide_batch/data/{tidecor_domain}/{tidecor_domain}_ll.nod")
    lons, lats = read_wt_lon_lat(coords_file)

    bathy_file = Path(f"/home/olh001/C_CPP/WebTide_batch/data/{tidecor_domain}/{tidecor_domain}.bat")
    bathym = pd.read_csv(bathy_file, sep=r"\s+", header=None)[1].values

    elem_file = Path(f"/home/olh001/C_CPP/WebTide_batch/data/{tidecor_domain}/{tidecor_domain}.ele")
    elem = pd.read_csv(elem_file, sep=r"\s+", header=None).iloc[:, 1:].values - 1
    elem = elem.astype(int)

    d = lons[elem].max(axis=1) - lons[elem].min(axis=1)
    no_cyclic_elem = [i for (i, val) in enumerate(d) if val < 100]

    n_header_lines = 3

    amp_col = 1
    pha_col = 2

    member_to_df = {}

    map_extent = [-80, -45, 35, 60]

    # read the data into memory
    for f in inp_dir.iterdir():
        m_id = f.name.split(".")[1]
        member_to_df[m_id] = pd.read_csv(f, header=None, skiprows=n_header_lines, sep=r"\s+")

    # Plotting
    proj = get_projection()

    ncols = 4
    nrows = len(member_to_df) // ncols + int(len(member_to_df) % ncols != 0)

    gs = GridSpec(nrows, ncols, hspace=0.0, wspace=0.0)

    fig = plt.figure(figsize=(16, 12))
    amp_clevs = np.arange(0, 0.3, 0.05)
    print(amp_clevs)

    for i, m_id in enumerate(sorted(member_to_df)):

        data = member_to_df[m_id]

        r, c = i // ncols, i % ncols

        ax = fig.add_subplot(gs[r, c], projection=proj)
        ax.set_extent(map_extent, crs=proj)

        # plot amplitudes
        csf = ax.tricontourf(lons, lats, elem[no_cyclic_elem], data[amp_col].values,
                             levels=amp_clevs,
                             transform=proj, cmap=cm.get_cmap("Spectral_r", len(amp_clevs) - 1),
                             extend="max")

        cb = plt.colorbar(csf, ax=ax, shrink=0.98)
        cb.ax.set_visible(i == len(member_to_df) - 1)

        # plot phases
        print(data[pha_col].values.min(), data[pha_col].values.max())
        cs = ax.tricontour(lons, lats, elem[no_cyclic_elem], data[pha_col].values,
                           levels=np.arange(0, 360, 10),
                           transform=proj,
                           colors="k",
                           linewidths=0.1)

        ax.clabel(cs, cs.levels[::3], fmt="%d", fontsize=2)

        ax.coastlines(resolution='50m', linewidth=0.1)

        ax.annotate(m_id, (0.1, 0.7), xycoords="axes fraction")



        print(f"Processed member {m_id} ...")


    img_file = img_dir / "cot_range_wt_members_in_grid.png"
    print(f"saving plots to {img_file}")
    fig.savefig(img_file, bbox_inches="tight", dpi=300)

    # Plot rmsd
    plot_amp_phase_ens_rmsd(lons=lons, lats=lats, elements=elem[no_cyclic_elem], constituents=member_to_df,
                            img_dir=img_dir, map_extent=map_extent, cn="O1")


if __name__ == '__main__':
    main()
