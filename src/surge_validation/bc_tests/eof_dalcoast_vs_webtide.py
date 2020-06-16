from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from eofs.standard import Eof

from surge_validation.utils.io_utils.fst import get_b2b_data_from_dir
from surge_validation.utils.io_utils import fst
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def main():
    root_dir = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp1/gridpt/")
    img_dir = Path("data/plots/eof_tides_webtide_vs_tidecor")
    neofs = 5
    n_members = 1

    beg_time = datetime(2018, 4, 16, tzinfo=timezone.utc)
    end_time = datetime(2019, 2, 12, tzinfo=timezone.utc)

    img_dir = img_dir / f"{beg_time:%Y%m%d%H}_{end_time:%Y%m%d%H}"

    grid_file = Path("/home/olh001/.suites/resps/constants/griddefs/grid-atlantic_1_12.fst")
    lons, lats, mask = fst.get_coords_and_mask(grid_file, nomvar="MGB", use_maskrec=False)

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
        print(data[label].shape)

    # signal of surge-tide interactions
    etas = data["DC_tides"] - data["WT"]

    # Calculate anomalies for EOF
    etas -= etas.mean(axis=1)[:, np.newaxis, ...]

    # Create an EOF solver to do the EOF analysis. Square-root of cosine of
    # latitude weights are applied before the computation of EOFs.
    coslat = np.cos(np.deg2rad(lats)).clip(0., 1.)
    wgts = np.sqrt(coslat)

    member_to_eofs = OrderedDict()
    member_to_expl_frac = OrderedDict()

    for mi in range(n_members):
        etas_cur = etas[mi].squeeze()

        print(f"etas ranges: std ({etas_cur.std(axis=0).min()}, {etas_cur.std(axis=0).max()})")

        solver = Eof(etas_cur, weights=wgts)

        # Retrieve the leading EOF, expressed as the covariance between the PC
        # time series and the input etas anomalies at each grid point.
        member_to_eofs[mi] = solver.eofsAsCorrelation(neofs=neofs)
        member_to_expl_frac[mi] = solver.varianceFraction(neigs=neofs)

    for mi, eof_list in member_to_eofs.items():
        mi_disp = f"{mi:03d}"
        for eofi, eof in enumerate(eof_list):
            eofi_disp = f"{eofi + 1:03d}"

            fig = plt.figure()
            clevs = np.linspace(-1, 1, 11)
            proj = ccrs.Orthographic(central_longitude=-60, central_latitude=50)
            ax = plt.axes(projection=proj)
            ax.coastlines(resolution='50m', linewidth=0.5)

            to_plot = np.ma.masked_where(~mask, eof)
            cs = ax.contourf(lons, lats, to_plot, levels=clevs,
                        cmap=plt.cm.RdBu_r,
                        transform=ccrs.PlateCarree(), extend="both")

            plt.colorbar(cs, ax=ax, shrink=0.98)
            title = f"EOF{eofi_disp} expressed as correlation\n member {mi_disp}, variance fraction {member_to_expl_frac[mi][eofi]*100:.3f}%"
            ax.set_title(title, fontsize=10)

            img_name = f"eof_corr_m{mi_disp}_eof{eofi_disp}.png"
            img_path = img_dir / img_name
            fig.savefig(img_path, bbox_inches="tight", dpi=300)
            plt.close(fig)


if __name__ == '__main__':
    main()

