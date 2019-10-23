from datetime import timedelta, datetime
from pathlib import Path

from ttide import t_predic
import pandas as pd
import numpy as np

from diagnostics.tides import wlev
from multiprocessing import Pool

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def t_predic_parallel(args):
    # logger.info(len(args))
    # logger.info([type(arg) for arg in args])

    # t, cnames, freqs, tidecon, lat = args
    # logger.info(t.dtype.name is np.dtype("O"))

    return t_predic(*args)


def constit_dict_to_tidecon_array(constituents: dict):
    """
    :param constituents:
    :return: tidecon, z0, cnames, freqs
        numpy arrays which can be directly used in t_predic
    """
    z0 = 0
    nc = len(constituents["names"]) - 1
    amps = [0] * nc
    phases = [0] * nc
    cnames = [""] * nc
    freqs = [0] * nc

    ccount = 0
    for i, cn in enumerate(constituents["names"]):
        logger.debug(cn)

        if cn.strip().lower() == "z0":
            z0 = constituents["amp"][i]
            continue

        amps[ccount] = constituents["amp"][i]
        phases[ccount] = constituents["pha"][i]
        cnames[ccount] = constituents["names"][i]
        freqs[ccount] = constituents["freq"][i]
        ccount += 1

    tidecon = np.asarray([amps, [1.e-8, ] * nc, phases, [1.e-8, ] * nc]).T

    return tidecon, z0, cnames, np.asarray(freqs)


def tides_prediction(constituents: dict, t_beg: datetime, t_end: datetime,
                     dt: timedelta = timedelta(hours=1),
                     t_range=None):
    """

    :param constituents:
    :param t_beg:
    :param t_end:
    :param dt:
    :return: tidal height
    """
    t = np.asarray(list(pd.date_range(t_beg, t_end, freq=dt)))

    if len(t) > 3:
        logger.debug([t[0], t[1], t[2], "...", t[-1]])
    else:
        logger.debug([t[0], "...", t[-1]])

    logger.debug(["t.dtype.name = ", t.dtype.name])

    tidecon, z0, cnames, freqs = constit_dict_to_tidecon_array(constituents)

    # log the progress
    if t_range is not None:
        logger.info(f"Working on {t[len(t) // 2]}/{t_range[-1]}")

    # TODO: return a pandas object (time referenced)
    return t_predic(t, cnames, freqs, tidecon, constituents["lat"]) + z0


def tides_prediction_accurate(constituents: dict,
                              t_beg: datetime,
                              t_end: datetime,
                              dt: timedelta = timedelta(hours=1),
                              ncpu=1):

    t_range = pd.date_range(t_beg, t_end, freq=dt)
    # res = [tides_prediction(constituents, t - dt_internal / 2., t + dt_internal / 2., dt=dt, t_range=t_range)[0]
    #        for t in t_range]

    tidecon, z0, cnames, freqs = constit_dict_to_tidecon_array(constituents)

    pool_args = (
        (np.asarray([t, ]), cnames, freqs, tidecon, constituents["lat"]) for t in t_range
    )

    pool = Pool(processes=ncpu)
    res = pool.map(t_predic_parallel, pool_args)
    pool.close()

    # res = [t_predic_parallel(args) for args in pool_args]

    res = np.asarray(res).squeeze() + z0
    df = pd.DataFrame(index=t_range, data=res, columns=["tide"])
    return df


def test():
    test_path = Path("/home/olh001/data/ppp1-sitestore/TidalConstituents_UTC/00215const_UTC.wlev")
    const = wlev.read_constituent_info(test_path)
    t1 = datetime(2019, 1, 1)
    th = tides_prediction_accurate(const, t1, t1 + timedelta(minutes=240), dt=timedelta(minutes=15))

    logger.info(th.loc[:, :])


if __name__ == '__main__':
    test()
