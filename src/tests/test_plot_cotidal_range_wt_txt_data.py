from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.gridspec import GridSpec

from bc_tests.tide_perturb.plot_cotidal_range_wt_txt_data import read_wt_lon_lat, get_projection


def test():
    # inp_dir = Path("/home/olh001/.suites/resps_tides_perturb_nwatl/forecast/constants/wt_perturbations")
    inp_dir = Path("/home/olh001/Python/surge_validation/data/wt_perturbations_nwatl_1.0.3_O1")

    tidecor_domain = "nwatl"

    img_dir = Path(f"data/test_plots/cotidal_range_wt_in_{tidecor_domain}_O1")
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

    map_extent = [-80, -30, 40, 60]

    # read the data into memory
    for f in inp_dir.iterdir():
        m_id = f.name.split(".")[1]
        member_to_df[m_id] = pd.read_csv(f, header=None, skiprows=n_header_lines, sep=r"\s+")

    # Plotting
    proj = get_projection()

    ncols = 1
    nrows = 1

    gs = GridSpec(nrows, ncols, hspace=0.0, wspace=0.0)

    fig = plt.figure(figsize=(16, 12))
    amp_clevs = np.arange(0, 1.5, 0.05)
    # print(amp_clevs)

    for i, m_id in enumerate(sorted(member_to_df)):

        data = member_to_df[m_id]

        r, c = i // ncols, i % ncols

        ax = fig.add_subplot(gs[r, c], projection=proj)
        ax.set_extent(map_extent, crs=proj)

        print(f"will plot {len(elem[no_cyclic_elem])} triangles")

        # plot amplitudes
        csf = ax.tricontourf(lons, lats, elem[no_cyclic_elem], data[amp_col].values,
                             levels=amp_clevs,
                             transform=proj,
                             cmap=cm.get_cmap("Spectral_r", len(amp_clevs) - 1),
                             extend="max")

        cb = plt.colorbar(csf, ax=ax, shrink=0.98)
        cb.ax.set_visible(i == len(member_to_df) - 1)

        # plot phases
        print(data[pha_col].values.min(), data[pha_col].values.max())

        cs = ax.tricontour(lons, lats, elem[no_cyclic_elem], data[pha_col].values,
                           levels=np.arange(0, 170, 10),
                           transform=proj,
                           colors="k",
                           linewidths=0.2)
        ax.clabel(cs, cs.levels[::3], fmt="%d", fontsize=2)



        ax.coastlines(resolution='50m', linewidth=0.1)

        ax.annotate(m_id, (0.1, 0.7), xycoords="axes fraction")

        print(f"Processed member {m_id} ...")
        break


    img_file = img_dir / "cot_range_wt_members_in_grid.png"
    print(f"saving plots to {img_file}")
    fig.savefig(img_file, bbox_inches="tight", dpi=300)

    # Plot rmsd
    # plot_amp_phase_ens_rmsd(lons=lons, lats=lats, elements=elem[no_cyclic_elem], constituents=member_to_df, img_dir=img_dir, map_extent=map_extent)

    pass


if __name__ == '__main__':
    test()
