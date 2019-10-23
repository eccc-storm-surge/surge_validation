from collections import OrderedDict
from multiprocessing import Pool

import numpy as np
import ttide as tt
import itertools as itt
import logging

from utils.cache_utils import get_cache


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def ttide_fit(args):
    x1d, dt_hours, lat, errcalc, constitnames = args
    # logger.debug(f"{x1d.shape, lat, dt_hours}")
    # synth is -1 for performance, since xout is not used anyway here.
    con = tt.t_tide(x1d, dt=dt_hours, synth=-1, ray=0.5, out_style=None,
                    errcalc=errcalc, constitnames=constitnames)

    con["xin"] = None
    con["xout"] = None
    # logger.debug(con["nameu"])
    return con


@get_cache(token="get_constituents")
def get_constituents(data, lat=None, dt_hours=1, nprocs=10, errcalc="cboot", constitnames=None):
    """
    The first dimension is expected to be time (nans are OK)
    :param errcalc: type of error calculation in ttide (for now ercalc should be only cboot to get correct values for
           amplitudes and phases of constituents)
    :param nprocs:
    :param lat: if not supplied, 0 latitude is used
    :param dt_hours:
    :param data: 3d field (t, x, y) of elevations
    :returns dict(constit_name=dict(amp=amp2d(x, y), phase=phase2d(x, y), snr=snr2d(x, y)))
    """

    if constitnames is None:
        constitnames = ["M2", ]

    data = np.asarray(data)

    in_data = np.asarray(data)

    result = OrderedDict()

    nt = in_data.shape[0]

    in_data = in_data.reshape((nt, -1)).T

    logger.debug(f"in_data.shape={in_data.shape}")
    logger.debug(f"in_data.mean()={in_data.mean()}")
    logger.debug(in_data)

    nprocs = min(nprocs, in_data.shape[0])

    if lat is None:
        lat = np.asarray([0., ] * in_data.shape[0])
    else:
        lat = np.asarray(lat).flatten()

    assert in_data.shape[0] == lat.shape[0], f"lat.shape[0]={lat.shape[0]}, in_data.shape[0]={in_data.shape[0]}"

    in_params = zip([in_data[i, :] for i in range(in_data.shape[0])],
                    itt.repeat(dt_hours, in_data.shape[0]), lat,
                    itt.repeat(errcalc, in_data.shape[0]),
                    itt.repeat(constitnames, in_data.shape[0]))

    logger.debug(f"Spawning {nprocs} processes")

    if nprocs > 1:
        pool = Pool(processes=nprocs)
        con_list = pool.map(ttide_fit, in_params)
    else:
        con_list = [ttide_fit(par) for par in in_params]

    con_names = con_list[0]["nameu"]

    logger.debug("Verification stats")
    logger.debug([con_list[0]["tidecon"].mean(), con_list[0]["tidecon"].std()])
    logger.debug([con_list[-1]["tidecon"].mean(), con_list[-1]["tidecon"].std()])

    # print(con_list[0])

    spatial_shape = data.shape[1:]

    logger.debug(f"Spatial shape: {spatial_shape}")

    for name_i, name in enumerate(con_names):
        name = name.strip().decode()

        amp = [con["tidecon"][name_i, 0] for i, con in enumerate(con_list)]
        phase = [con["tidecon"][name_i, 2] for i, con in enumerate(con_list)]
        snr = [con["snr"][name_i] for i, con in enumerate(con_list)]
        fu = [con["fu"][name_i] for i, con in enumerate(con_list)]

        amp = np.asarray(amp).reshape(spatial_shape)
        phase = np.asarray(phase).reshape(spatial_shape)
        snr = np.asarray(snr).reshape(spatial_shape)
        fu = np.asarray(fu).reshape(spatial_shape)

        # print(name, len(name))
        result[name] = OrderedDict([
            ("amp", amp),
            ("phase", phase),
            ("snr", snr),
            ("fu", fu)
        ])

    return result


def reshape_constituents_to_mask(constit_dict: dict, mask):
    """
    Reshape constituent fields from 1d to 2d masked arrays according to the mask
    :param constit_dict:
    :param mask:
    """
    for cn, param_to_vals in constit_dict.items():
        for param, cvals in param_to_vals.items():
            d = np.ma.masked_all(mask.shape)
            d[mask] = cvals
            param_to_vals[param] = d


def main():
    pass


if __name__ == '__main__':
    main()
