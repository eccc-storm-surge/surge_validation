"""



objective:
    Calculate ampl and phase rmses for use to limit perturbations

algorithm:
    1. Calculate tide amplitudes and phases for 2 simulations for a given list of constituents

Computationally expensive, better to submit to a node

ord_soumet= -cpus

"""
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from pprint import pprint

from tidal_constituents.get_constituents_nd import get_constituents
from utils.io_utils import fst
from utils.io_utils.fst import get_b2b_data_from_dir
import numpy as np

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def calc_max_perturbation(dir1: Path,
                          dir2: Path,
                          data_query1: dict = None,
                          data_query2: dict = None,
                          dt_hours=1.):
    dirs = [dir1, dir2]
    queries = [data_query1, data_query2]

    # read in the data into memory, not ideal but required for quick de-tiding
    data = [
        get_b2b_data_from_dir(d, data_query=q).squeeze() for d, q in zip(dirs, queries)
    ]

    logger.debug(len(data))

    lons, lats, data_mask = None, None, None
    for f in dirs[0].iterdir():
        lons, lats, data_mask = fst.get_coords_and_mask(f, nomvar=data_query1["nomvar"], use_maskrec=True)
        break

    i, j = np.where(data_mask)

    logger.debug(f"i={i}")
    logger.debug(f"j={j}")

    for d in data:
        logger.debug(d.shape)

    # calculate constituents
    constituents = [
        get_constituents(d[:, i, j], lat=lats[i, j], dt_hours=dt_hours, nprocs=10, errcalc="cboot") for d in data
    ]

    con1, con2 = constituents

    rms_dict = {}
    for cn in con1:

        rms_dict[cn] = {}
        for param in con1[cn]:
            n1 = len(con1[cn][param])
            n2 = len(con2[cn][param])
            assert n1 == n2, f"Number of points should be the same in both simulations, but got n1={n1}; n2={n2}"

            diff = con1[cn][param] - con2[cn][param]

            if param.lower() == "phase":
                pprint(diff)

                diff[diff > 180] -= 360
                diff[diff < -180] += 360

                pprint(diff)
                pprint(n1)

            rms_dict[cn][param] = np.linalg.norm(diff) / n1 ** 0.5

    return rms_dict


def main():

    beg_time = datetime(2018, 4, 16, tzinfo=timezone.utc)
    end_time = datetime(2019, 4, 16, tzinfo=timezone.utc)

    d1 = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp1/gridpt/prog_tides")
    d2 = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp1/gridpt/tides")

    data_query = OrderedDict([
            ("beg_time", beg_time),
            ("end_time", end_time),
            ("nomvar", "ETAS"),
            ("n_b2b_hours", 12)
    ])

    data_query1 = data_query.copy()
    data_query2 = data_query.copy()

    data_query2["nomvar"] = "SSHT"
    data_query2["member_ids"] = ("",)

    data_query1["member_ids"] = ("000",)

    pprint(calc_max_perturbation(d1, d2, data_query1=data_query1, data_query2=data_query2, dt_hours=1.))



if __name__ == '__main__':
    main()
