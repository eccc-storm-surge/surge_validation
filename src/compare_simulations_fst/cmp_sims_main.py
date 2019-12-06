"""
Compare multiple simulations laid out similarly between files on disk

python cmp_sims_main.py --labels L1 L2 ... Ln \
                        --paths P1 P2  ... Pn \
                        --colors b r ... \
                        [--base_label Li \]  # label of the base experiment (to which everyone else is compared, L1 if not specified)
                        [--expdate1 d1 --expdate2 d2 --dt_hours dt "all files are used if not specified"] \
                        [--out_dir "./"]
"""

import argparse
from collections import OrderedDict, defaultdict
from datetime import datetime
from pathlib import Path


def parse_cmd_args():
    """
    parse cmd line arguments
    :return:
    """
    parser = argparse.ArgumentParser("Plot differences")

    parser.add_argument("--paths", nargs="+",
                        help="space separated paths to the folders containing fst files of model outputs")

    parser.add_argument("--labels",
                        help="labels of the corresponding paths",
                        nargs="+")

    parser.add_argument("--colors",
                        help="colors of the corresponding labels",
                        nargs="+")

    parser.add_argument("--out_dir", nargs="?", default="./",
                        help="Path to the folder, where to store plots",
                        required=False)

    parser.add_argument("--expdate1", nargs="?", default=None,
                        help="start experiment datetime, inclusive (usually it is a part of  a file name)",
                        required=False)

    parser.add_argument("--expdate2", nargs="?", default=None,
                        help="end experiment datetime, inclusive (usually it is a part of  a file name)",
                        required=False)

    parser.add_argument("--dt_hours", nargs="?", default=None,
                        help="frequency of the experiments to be considered in the comparison",
                        required=False)

    return parser.parse_args()


def infer_member_id(fst_file: Path, sep="_"):
    mid = fst_file.name.split(sep)[-1]
    if mid == "":
        mid = "000"
    return mid


def fname_prefix_to_dtime(fst_file: Path, sep="_"):
    return datetime.strptime(fst_file.name.split(sep)[0], "%Y%m%d%H")


def read_data_into_accumulators(fst_data_dir: Path, query: dict):
    """
    :param fst_data_dir:
    :param query:

    :returns time mean field, and dataframe of timeseries (1 column per member, if available)
    """

    # index paths
    date_to_mid_to_path = defaultdict(dict)

    min_date = None
    max_date = None

    for fin in fst_data_dir.iterdir():
        exp_date = fname_prefix_to_dtime(fin)
        mid = infer_member_id(fin)
        date_to_mid_to_path[exp_date][mid] = fin

        if min_date is None:
            min_date = exp_date
            max_date = exp_date
        else:
            min_date = min(min_date, exp_date)
            max_date = max(max_date, exp_date)

    # variables to hold outputs
    ts_dict = {}
    mid_to_timavg = {}
    field_mask = None

    t_beg = query.get("t_beg", min_date)
    t_end = query.get("t_end", max_date)

    dt = query.get("dt", None)

    for t, mid_to_fin in date_to_mid_to_path.items():

        # check left time limit
        if t < t_beg:
            continue

        # check right time limit
        if t > t_end:
            continue

        for mid, fin in mid_to_fin.items():

            # TODO: finish implementation
            pass





def main():
    """
    Entry point
    """
    label_to_path = OrderedDict()
    label_to_color = OrderedDict()

    args = parse_cmd_args()

    for label, path, color in zip(args.labels, args.paths, args.colors):
        label_to_path[label] = path
        label_to_color[label] = color


if __name__ == '__main__':
    pass