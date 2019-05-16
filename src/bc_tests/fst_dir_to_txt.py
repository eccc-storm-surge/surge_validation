
"""
Convert all fst files in a folder to txt
"""
import logging
from collections import OrderedDict
from datetime import datetime, timezone
from multiprocessing.pool import Pool
from pathlib import Path

from rpnpy.librmn import all as rmn
import numpy as np
from rpnpy.rpndate import RPNDate
import itertools as itt

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _fname_to_exp_date(fn):
    return datetime.strptime(fn.split("_")[0], "%Y%m%d%H").replace(tzinfo=timezone.utc)


def _convert_to_txt_par(args):
    f_in, out_path, data_query = args

    funit = rmn.fstopenall(str(f_in))
    keys = rmn.fstinl(funit, nomvar=data_query["nomvar"], typvar="P@")
    metas = [rmn.fstprm(k) for k in keys]
    vh_list = [rmn.convertIPtoPK(0, meta["ip2"], 0)[1].v1 for meta in metas]

    t_list = [RPNDate(m["datev"]).toDateTime() for m in metas]

    t_to_key = dict(zip(t_list, keys))
    t_to_vh = dict(zip(t_list, vh_list))

    # remove the 0 time step
    t_to_key = {t: k for t, k in t_to_key.items() if t_to_vh[t] > 0}

    if len(t_to_key) == 0:
        logger.debug(f"No eligible data in {f_in}")
        rmn.fstcloseall(funit)
        return

    data_3d = [rmn.fstluk(t_to_key[t])["d"] for t in sorted(t_to_key)]

    data_2d = np.concatenate(
        data_3d, axis=-1
    )

    np.savetxt(out_path, data_2d.T, fmt="%.4f")

    rmn.fstcloseall(funit)


def export_to_txt(src_dir: Path, dst_dir: Path, data_query=None, ncpus=30):

    if data_query is None:
        data_query = {
            "nomvar": "ETAS",
            "beg_time": None,
            "end_time": None
        }

    beg_time = data_query["beg_time"]
    end_time = data_query["end_time"]

    inp_files = []
    out_files = []

    for f_in in src_dir.iterdir():

        out_path = dst_dir / f_in.name

        exp_t = _fname_to_exp_date(f_in.name)

        if beg_time is not None:
            if exp_t < beg_time:
                continue

        if end_time is not None:
            if exp_t > end_time:
                continue

        if out_path.exists():
            logger.info(f"{out_path} already exists, skipping")
            continue

        inp_files.append(str(f_in))
        out_files.append(str(out_path))

    pool = Pool(processes=ncpus)
    pool.map(_convert_to_txt_par, list(zip(inp_files, out_files, itt.repeat(data_query, len(inp_files)))))





def main():

    # root_dir = Path("/home/olh001/.suites/resps_tides_surge_tide_interactions/forecast/hub/eccc-ppp1/gridpt/")

    root_dir = Path("/fs/cetus3/fs2/cmd/e/afsg/olh/fst")
    txt_dir = Path("data/txt/resps_tides_experiments/")

    beg_time = datetime(2018, 4, 16, tzinfo=timezone.utc)
    end_time = datetime(2019, 4, 16, tzinfo=timezone.utc)

    txt_dir = txt_dir / f"{beg_time:%Y%m%d%H}_{end_time:%Y%m%d%H}_complete_forecasts"

    data_query = {
        "beg_time": beg_time,
        "end_time": end_time,
        "nomvar": "ETAS",
    }

    label_to_data_dir = OrderedDict([
        ("DC_tides", root_dir / "prog_tides"),
        ("WT", root_dir / "tides"),
        ("DC_surge", root_dir / "prog_surge"),
        ("DC_surge_tides", root_dir / "prog_surge_tides")

    ])

    label_to_nomvar = {
        "DC_tides": "ETAS",
        "DC_surge": "ETAS",
        "DC_surge_tides": "ETAS",
        "WT": "SSHT"
    }

    txt_dir.mkdir(parents=True, exist_ok=True)

    for label, data_dir in label_to_data_dir.items():
        dst_dir = txt_dir / label
        logger.info(f"Converting {data_dir} -> {dst_dir}")

        data_query["nomvar"] = label_to_nomvar[label]

        dst_dir.mkdir(exist_ok=True, parents=True)
        export_to_txt(data_dir, dst_dir, data_query=data_query)


if __name__ == '__main__':
    main()

