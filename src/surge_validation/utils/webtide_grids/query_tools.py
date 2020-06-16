from pathlib import Path
import pandas as pd
from scipy.spatial import KDTree


def get_closest_phases_and_amplitudes(wt_data_dir: Path, perturb_dir: Path, lon, lat):
    """
    :param perturb_dir: folder with perturbed constituents amplitudes and phases
    :param wt_data_dir:
    :param lon:
    :param lat:
    :return: list (for each member) of lists of amplitude and phase pairs ([(A1, phi1), (A2, phi2), (A3, phi3)], )
    """

    res = []

    # read node coordinates
    coords_file = wt_data_dir / "HRgloballl.nod"
    assert coords_file.exists()
    coords = pd.read_csv(coords_file, header=None, sep=r"\s+")
    print(coords.head())

    # read node amplitudes and phases
    df_list = []
    for f in perturb_dir.iterdir():
        df_list.append(pd.read_csv(f, header=None, skiprows=3, sep=r"\s+"))

    # find 3 closest nodes
    kdtree = KDTree(list(zip(coords[1].values, coords[2].values)))

    dists, inds = kdtree.query((lon, lat), k=3)

    # return their amplitudes and phases
    for df in df_list:
        res.append([(df.iloc[i, 1], df.iloc[i, 2]) for i in inds])

    return res


def test():
    inp_dir = Path("/home/olh001/C_CPP/WebTide_batch/data/HRglobal/")
    perturb_dir = Path("/home/olh001/.suites/resps_tides_perturb/forecast/constants/wt_perturbations")
    lon, lat = 313.6665954589844 - 360, 43.08332061767578

    amp_pha = get_closest_phases_and_amplitudes(inp_dir, perturb_dir, lon=lon, lat=lat)

    print(amp_pha)


if __name__ == '__main__':
    test()
