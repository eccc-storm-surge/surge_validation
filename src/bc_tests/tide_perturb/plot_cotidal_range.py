
# plot co-tidal range for different members
from pathlib import Path


def plot_cotidal_range(data_dir: Path, member_ids=("",), img_dir: Path = Path("data/plots")):
    # TODO: implement
    pass


def test():

    exp_label = "WT"
    img_dir = Path(f"data/plots/cotidal_ranges_{exp_label}")

    img_dir.mkdir(exist_ok=True, parents=True)

    data_dir = Path("/home/olh001/.suites/resps_tides_perturb/forecast/hub/eccc-ppp2/gridpt/tides")

    # TODO: implement
    pass


if __name__ == '__main__':
    test()
