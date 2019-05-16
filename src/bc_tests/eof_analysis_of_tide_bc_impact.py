from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from eofs.standard import Eof
import numpy as np

from utils.io_utils import fst
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

from utils.io_utils.fst import get_b2b_data_from_dir_for_member_id


def main():
    root_dir = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp1/gridpt/")
    img_dir = Path("data/plots/eof_tides")
    neofs = 5
    n_members = 21

    beg_time = datetime(2018, 4, 16, tzinfo=timezone.utc)
    end_time = datetime(2018, 4, 18, tzinfo=timezone.utc)

    img_dir = img_dir / f"{beg_time:%Y%m%d%H}_{end_time:%Y%m%d%H}"

    grid_file = Path("/home/olh001/.suites/resps/constants/griddefs/grid-atlantic_1_12.fst")
    lons, lats, mask = fst.get_coords_and_mask(grid_file, nomvar="MGB", use_maskrec=False)

    data_query = {
        "beg_time": beg_time,
        "end_time": end_time,
        "nomvar": "ETAS",
        "n_b2b_hours": 12
    }

    label_to_data_dir = OrderedDict([
        ("DC_tides", root_dir / "prog_tides"),
        ("DC_surge", root_dir / "prog_surge"),
        ("DC_surge_tides", root_dir / "prog_surge_tides")
    ])

    img_dir.mkdir(parents=True, exist_ok=True)

    member_ids = [f"{iid:03d}" for iid in range(n_members)]

    label_to_member_ids = {
        "DC_tides": ["000"] * n_members, "DC_surge": member_ids, "DC_surge_tides": member_ids
    }

    # Create an EOF solver to do the EOF analysis. Square-root of cosine of
    # latitude weights are applied before the computation of EOFs.
    coslat = np.cos(np.deg2rad(lats)).clip(0., 1.)
    wgts = np.sqrt(coslat)

    for mi in range(n_members):

        data = OrderedDict()
        mi_disp = f"{mi:03d}"

        #  sequential version
        for label, data_dir in label_to_data_dir.items():
            inp = [data_dir, label_to_member_ids[label][mi], data_query]
            data[label] = get_b2b_data_from_dir_for_member_id(inp)

        # signal of surge-tide interactions
        etas = data["DC_surge_tides"] - data["DC_surge"] - data["DC_tides"]

        # Calculate anomalies for EOF
        etas -= etas.mean(axis=0)[np.newaxis, ...]

        solver = Eof(etas, weights=wgts)

        # Retrieve the leading EOF, expressed as the covariance between the leading PC
        # time series and the input etas anomalies at each grid point.
        eof_list = solver.eofsAsCorrelation(neofs=neofs)
        var_expl_frac = solver.varianceFraction(neigs=neofs)

        for eofi, eof in enumerate(eof_list):
            eofi_disp = f"{eofi + 1:03d}"

            fig = plt.figure()
            clevs = np.linspace(-0.5, 0.5, 11)
            proj = ccrs.Orthographic(central_longitude=-60, central_latitude=50)
            ax = plt.axes(projection=proj)
            ax.coastlines(resolution='50m', linewidth=0.5)

            to_plot = np.ma.masked_where(~mask, eof)
            cs = ax.contourf(lons, lats, to_plot, levels=clevs,
                        cmap=plt.cm.RdBu_r, transform=ccrs.PlateCarree(), extend="both")

            plt.colorbar(cs, ax=ax, shrink=0.98)
            title = f"EOF{eofi_disp} expressed as correlation\n member {mi_disp}, variance fraction {var_expl_frac[eofi]*100:.3f}%"
            ax.set_title(title, fontsize=10)

            img_name = f"eof_corr_m{mi_disp}_eof{eofi_disp}.png"
            img_path = img_dir / img_name
            fig.savefig(img_path, bbox_inches="tight", dpi=300)
            plt.close(fig)


if __name__ == '__main__':
    import time
    t0 = time.clock()
    main()
    print(f"Process time {time.clock() - t0} seconds")

