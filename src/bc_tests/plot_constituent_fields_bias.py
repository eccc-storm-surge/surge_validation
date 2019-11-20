from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from matplotlib.gridspec import GridSpec

from tidal_constituents.get_constituents_nd import get_constituents
from utils.io_utils import fst
import numpy as np
import matplotlib.pyplot as plt

from utils.io_utils.fst import get_b2b_data_from_dir
from cartopy import crs as ccrs

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


NWATL_CONSTITUENTS = ["K1", "O1", "M2", "N2", "S2"]

def calculate_mean_difference(field1, field2, multipliers=(1, -1)):
    """
    compute mean difference between 2 fields in %
    :param field1:
    :param field2:
    :return:
    """
    bias = np.abs(field1 * multipliers[0] + field2 * multipliers[1])
    return bias.mean() / (0.5 * np.abs(field2) + 0.5 * np.abs(field1)).flatten().mean() * 100.


def __inspect_field(data, label):
    lims = (data.min(), data.max())
    stats = (data.mean(), data.std()) + lims

    logger.debug(f"stats for {label}: {stats}")


def exp_010():
    """
    Based on nwatl simulations for 1993, remove 3500m cutoff, K1 values not diffs (DC modif bathy)
    """

    img_dir = Path("data/plots/constituent_fields/DC_tides_v010_1993_modif_bathy")

    for cn in NWATL_CONSTITUENTS:
        root_dir = Path(
            f"/home/olh001/.suites/resps_tides_perturb_nwatl_O1M2_1993_K1only_wtbathy/forecast/hub/eccc-ppp2/gridpt_{cn}")

        if not root_dir.is_dir():
            continue

        nprocs = 4

        beg_time = datetime(1993, 1, 10, tzinfo=timezone.utc)
        end_time = datetime(1993, 2, 10, tzinfo=timezone.utc)

        main(root_dir=root_dir,
             img_dir=img_dir,
             constitnames=[cn],
             nprocs=nprocs,
             beg_time=beg_time, end_time=end_time, n_b2b_hours=720, diff_multipliers=(1, 0), title="DC (modif. bathy)")



def exp_009():
    """
    Based on nwatl simulations for 1993, remove 3500m cutoff, K1 values not diffs (WT)
    """

    img_dir = Path("data/plots/constituent_fields/WT_tides_v009_1993")

    for cn in ["K1", ]:
        root_dir = Path(
            f"/home/olh001/.suites/resps_tides_perturb_nwatl_O1M2_1993_K1only_DCbathy/forecast/hub/eccc-ppp2/gridpt_{cn}")

        if not root_dir.is_dir():
            continue

        constitnames = [cn, ]
        nprocs = 4

        beg_time = datetime(1993, 1, 10, tzinfo=timezone.utc)
        end_time = datetime(1993, 2, 10, tzinfo=timezone.utc)

        main(root_dir=root_dir,
             img_dir=img_dir,
             constitnames=constitnames,
             nprocs=nprocs,
             beg_time=beg_time, end_time=end_time, n_b2b_hours=720, diff_multipliers=(0, 1), title="WT")



def exp_009a():
    """
    Based on nwatl simulations for 1993, values not diffs (DC orig bathymetry)
    """

    img_dir = Path("data/plots/constituent_fields/WT_tides_v009a_1993")

    for cn in NWATL_CONSTITUENTS:
        root_dir = Path(
            f"/home/olh001/.suites/resps_tides_perturb_nwatl_O1M2_1993_scaling_invert/forecast/hub/eccc-ppp1/gridpt")

        if not root_dir.is_dir():
            continue

        nprocs = 4

        beg_time = datetime(1993, 1, 10, tzinfo=timezone.utc)
        end_time = datetime(1993, 2, 10, tzinfo=timezone.utc)

        main(root_dir=root_dir,
             img_dir=img_dir,
             constitnames=[cn],
             nprocs=nprocs,
             beg_time=beg_time, end_time=end_time, n_b2b_hours=720, diff_multipliers=(0, 1), title="WT")




def exp_008a():
    """
    Based on nwatl simulations for 1993, remove 3500m cutoff, K1 values not diffs (DC orig bathymetry)
    """

    img_dir = Path("data/plots/constituent_fields/DC_tides_v008a_1993_origbathy_biases_scaling_invert")

    for cn in NWATL_CONSTITUENTS:
        root_dir = Path(
            f"/home/olh001/.suites/resps_tides_perturb_nwatl_O1M2_1993_scaling_invert/forecast/hub/eccc-ppp1/gridpt")

        if not root_dir.is_dir():
            continue

        nprocs = 4

        beg_time = datetime(1993, 1, 10, tzinfo=timezone.utc)
        end_time = datetime(1993, 2, 10, tzinfo=timezone.utc)

        main(root_dir=root_dir,
             img_dir=img_dir,
             constitnames=[cn],
             nprocs=nprocs,
             beg_time=beg_time, end_time=end_time, n_b2b_hours=720, diff_multipliers=(1, -1), title="DC - WT")



def exp_008b():
    """
    Based on nwatl simulations for 1993, remove 3500m cutoff, K1 values not diffs (DC orig bathymetry)
    """

    img_dir = Path("data/plots/constituent_fields/DC_tides_v008b_1993_origbathy")

    for cn in NWATL_CONSTITUENTS:
        root_dir = Path(
            f"/home/olh001/.suites/resps_tides_perturb_nwatl_O1M2_1993/forecast/hub/eccc-ppp1/gridpt")

        if not root_dir.is_dir():
            continue

        nprocs = 4

        beg_time = datetime(1993, 1, 10, tzinfo=timezone.utc)
        end_time = datetime(1993, 2, 10, tzinfo=timezone.utc)

        main(root_dir=root_dir,
             img_dir=img_dir,
             constitnames=[cn],
             nprocs=nprocs,
             beg_time=beg_time, end_time=end_time, n_b2b_hours=720, diff_multipliers=(1, 0), title="DC (orig bathy)")



def exp_007():
    """
    Based on nwatl simulations for 1993, remove 3500m cutoff, K1 values not diffs
    """
    root_dir = Path("/home/olh001/.suites/resps_tides_perturb_nwatl_O1M2_1993_K1only_wtbathy/forecast/hub/eccc-ppp2/gridpt")
    img_dir = Path("data/plots/constituent_fields/DC_tides_minus_WT_v007_1993")

    constitnames = ["K1", ]
    nprocs = 4

    beg_time = datetime(1993, 1, 10, tzinfo=timezone.utc)
    end_time = datetime(1993, 2, 10, tzinfo=timezone.utc)

    main(root_dir=root_dir,
         img_dir=img_dir,
         constitnames=constitnames,
         nprocs=nprocs,
         beg_time=beg_time, end_time=end_time, n_b2b_hours=720)




def exp_006():
    """
    Based on nwatl simulations for 1993, remove 3500m cutoff
    """
    root_dir = Path("/home/olh001/.suites/resps_tides_perturb_nwatl_O1M2_1993_K1only_wtbathy/forecast/hub/eccc-ppp2/gridpt")
    img_dir = Path("data/plots/constituent_fields/DC_tides_minus_WT_v006_1993")

    constitnames = ["K1", ]
    nprocs = 4

    beg_time = datetime(1993, 1, 10, tzinfo=timezone.utc)
    end_time = datetime(1993, 2, 10, tzinfo=timezone.utc)

    main(root_dir=root_dir,
         img_dir=img_dir,
         constitnames=constitnames,
         nprocs=nprocs,
         beg_time=beg_time, end_time=end_time, n_b2b_hours=720)



def exp_005():
    """
    Based on nwatl simulations for 1993
    """
    root_dir = Path("/home/olh001/.suites/resps_tides_perturb_nwatl_O1M2_1993_K1only_DCbathy/forecast/hub/eccc-ppp2/gridpt")
    img_dir = Path("data/plots/constituent_fields/DC_tides_minus_WT_v005_1993")

    constitnames = ["K1", ]
    nprocs = 4

    beg_time = datetime(1993, 1, 10, tzinfo=timezone.utc)
    end_time = datetime(1993, 2, 10, tzinfo=timezone.utc)

    main(root_dir=root_dir,
         img_dir=img_dir,
         constitnames=constitnames,
         nprocs=nprocs,
         beg_time=beg_time, end_time=end_time, n_b2b_hours=720)


def exp_004():
    """
    Based on nwatl simulations
    """
    root_dir = Path("/home/olh001/.suites/resps_tides_perturb_nwatl/forecast/hub/eccc-ppp2/gridpt/")
    img_dir = Path("data/plots/constituent_fields/DC_tides_minus_WT_v004")

    constitnames = ["K1", ]
    nprocs = 8

    main(root_dir=root_dir,
         img_dir=img_dir,
         constitnames=constitnames,
         nprocs=nprocs)


def exp_003():
    """
    Based on nwatl simulations
    """
    root_dir = Path("/home/olh001/.suites/resps_tides_perturb_nwatl/forecast/hub/eccc-ppp2/gridpt/")
    img_dir = Path("data/plots/constituent_fields/DC_tides_minus_WT_v003")

    constitnames = ["M2", "O1", ]
    nprocs = 2

    main(root_dir=root_dir, img_dir=img_dir, constitnames=constitnames,
         nprocs=nprocs)


def main(root_dir: Path = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp2/gridpt/"),
    img_dir: Path = Path("data/plots/constituent_fields/DC_tides_minus_WT_v002"),
    constitnames=None, nprocs=10, beg_time=None, end_time=None, n_b2b_hours=12,
    diff_multipliers=(1, -1), title=None):

    bias_units = r""

    if beg_time is None or end_time is None:
        beg_time = datetime(2018, 4, 16, tzinfo=timezone.utc)
        end_time = datetime(2019, 4, 16, tzinfo=timezone.utc)

    img_dir = img_dir / f"{beg_time:%Y%m%d%H}_{end_time:%Y%m%d%H}"

    grid_file = Path("/home/olh001/.suites/resps/constants/griddefs/grid-atlantic_1_12.fst")
    lons, lats, mask = fst.get_coords_and_mask(grid_file, nomvar="MGB", use_maskrec=False)

    bc_mask_file = Path("/home/olh001/Python/fst_create_mask/test.fst")
    _, _, bc_mask = fst.get_coords_and_mask(bc_mask_file, nomvar="MGB", use_maskrec=False)

    data_query = OrderedDict([
        ("beg_time", beg_time),
        ("end_time", end_time),
        ("nomvar", "ETAS"),
        ("n_b2b_hours", n_b2b_hours)
    ])

    ref_label = "WT"

    label_to_data_dir = OrderedDict([
        ("DC_tides", root_dir / "prog_tides"),
        ("WT",       root_dir / "tides"),
    ])

    img_dir.mkdir(parents=True, exist_ok=True)

    label_to_member_ids = {
        "DC_tides": ["000"], "WT": ["000"]
    }

    label_to_nomvar = {
        "DC_tides": "ETAS",
        "WT": "SSHT"
    }

    i_list, j_list = np.where(mask)
    logger.debug(
        f"lon0={lons[0, 0]:.6f}; lat0={lats[0, 0]:.6f}, dlon={(lons[-1, -1] - lons[0, 0]) / lons.shape[0]:.6f}")

    label_to_constit_dict = OrderedDict()

    for label, data_dir in label_to_data_dir.items():
        data_query["nomvar"] = label_to_nomvar[label]

        data = get_b2b_data_from_dir(data_dir,
                   member_ids=label_to_member_ids[label], data_query=data_query)

        logger.debug(f"data.shape = {data.shape}")

        etas = data.squeeze()

        ts_list = np.asarray([etas[:, i, j] for i, j in zip(i_list, j_list)])
        ts_list = ts_list.T

        logger.debug(f"ts_list.shape = {ts_list.shape}")

        lat_list = [lats[i, j] for i, j in zip(i_list, j_list)]

        label_to_constit_dict[label] = get_constituents(ts_list, lat=lat_list,
                                                    dt_hours=1., nprocs=nprocs,
                                                    errcalc="cboot",
                                                    constitnames=constitnames,
                                                    stime=beg_time)

        logger.debug(list(label_to_constit_dict[label].keys()))

        del etas
        logger.info("Successfully executed get_constituents")

    constit_dict_structured = OrderedDict([(k, OrderedDict()) for k in label_to_constit_dict[ref_label]])
    field_differences = OrderedDict([(k, OrderedDict()) for k in label_to_constit_dict[ref_label]])

    for cn, cdata in label_to_constit_dict[ref_label].items():
        for cparam, cvals in cdata.items():
            constit_dict_structured[cn][cparam] = np.ma.masked_all(mask.shape)

            bias = label_to_constit_dict["DC_tides"][cn][cparam] * diff_multipliers[0] + label_to_constit_dict["WT"][cn][cparam] * diff_multipliers[1]
            constit_dict_structured[cn][cparam][i_list, j_list] = bias
            field_differences[cn][cparam] = calculate_mean_difference(label_to_constit_dict["DC_tides"][cn][cparam],
                                                                      label_to_constit_dict["WT"][cn][cparam])

    # set the title, depending on what is requested
    if title is not None:
        label = title
    else:
        label = f"DC_tides-WT"

    plot_amp_and_phase(constit_dict_structured, img_dir, lons, lats, mask,
                       select_constituents=constitnames,
                       label=label, bias_units=bias_units, field_differences=field_differences)


def plot_amp_and_phase(constit_dict, img_dir: Path, lons, lats, mask,
                       select_constituents=("MM", "MF"), label="",
                       bias_units=r"", field_differences=None):

    if not img_dir.exists():
        img_dir.mkdir(exist_ok=True)

    # params_to_plot = ["amp", "phase"]
    params_to_plot = ["amp", "phase"]

    param_units = {
        "amp": "m", "phase": "degrees"
    }

    n_clevs = 23

    if bias_units == "%":
        param_to_clev = {
            "amp": np.linspace(-100, 100, n_clevs),
            "phase": np.linspace(-100, 100, n_clevs)
        }
    else:
        param_to_clev = {
            "amp": np.linspace(-0.15, 0.15, n_clevs),
            "phase": np.linspace(-45, 45, n_clevs),
            "amp_M2": np.arange(0, 3, 0.5),
            "amp_O1": np.arange(0, 0.2, 0.01),
            "amp_K1": np.arange(0, 0.2, 0.01),
            "amp_S2": np.arange(0, 1, 0.1),
            "amp_N2": np.arange(0, 1, 0.1),
        }

    proj = ccrs.Orthographic(central_longitude=-60, central_latitude=50)

    for cn in select_constituents:

        gs = GridSpec(len(params_to_plot), 1, hspace=0.4)

        fig = plt.figure()
        for row, param in enumerate(params_to_plot):

            ax = fig.add_subplot(gs[row, 0], projection=proj)
            ax.coastlines(resolution='50m', linewidth=0.5)

            to_plot = np.ma.masked_where(~mask, constit_dict[cn][param])

            if param == "phase":
                good = ~to_plot.mask
                g_to_plot = to_plot[good]
                # g_to_plot[g_to_plot > 180] = g_to_plot[g_to_plot > 180] - 360
                # g_to_plot[g_to_plot < -180] = g_to_plot[g_to_plot < -180] + 360
                # to_plot[good] = g_to_plot

                g_to_plot[g_to_plot < 0] += 360

            if param == "phase" and not field_differences:
                cs = ax.contour(lons, lats, to_plot, levels=np.arange(10, 360, 20),
                                 transform=ccrs.PlateCarree(), colors="0.75", linewidths=0.5)

                ax.clabel(cs, fontsize=3, fmt="%d")

                cb = plt.colorbar(cs, ax=ax, shrink=0.98)
                cb.ax.set_visible(False)
            else:
                clevs = param_to_clev[f"{param}_{cn}"]

                cs = ax.contourf(lons, lats, to_plot, levels=clevs,
                                 cmap=plt.cm.get_cmap("coolwarm", n_clevs),
                                 transform=ccrs.PlateCarree(), extend="both")

                # __inspect_field(to_plot, f"{param}, {cn}")
                plt.colorbar(cs, ax=ax, shrink=0.98)

            title = fr"{cn}, {label} ({param_units[param]})"
            if field_differences is not None:
                pass
                # title += "\n" + r"${\overline{|\Delta|}}/{\overline{|X|}} = $" + f"{field_differences[cn][param]:.1f}%"

            ax.set_title(title, fontsize=10)

        img_name = f"{cn}.png"
        img_path = img_dir / img_name
        logger.info(f"Saving plots to {img_path}")
        fig.savefig(img_path, bbox_inches="tight", dpi=300)
        plt.close(fig)


if __name__ == '__main__':
    # main()
    # exp_008b()
    exp_008a()
    # exp_009a()
    # exp_010()
