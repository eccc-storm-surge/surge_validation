from collections import defaultdict
from pathlib import Path
import logging
import numpy as np

from rpnpy.librmn import all as rmn
import itertools as itt

from utils.io_utils import fst

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


stat_funcs = {
    "ensmean": lambda x: np.mean(x, axis=0),
    "ensmedian": lambda x: np.median(x, axis=0),
}


def prefix(f: Path):
    return f.name.split("_")[0] + "_"


def get_grouped_files(inp_dir: Path):
    # group all files by the prefix
    files = [f for f in inp_dir.iterdir()]

    files = sorted(files, key=prefix)
    return itt.groupby(files, key=prefix)


def read_file_group(file_group):
    """
    returns dictionary {t: record}
    :param file_group:
    """
    query_params = dict(
        typvar="P@",
        nomvar="ETAS"
    )

    funit = rmn.fstopenall([str(f) for f in file_group])

    keys = rmn.fstinl(funit, **query_params)

    data = defaultdict(list)

    for k in keys:
        dv = rmn.fstprm(k)["datev"]
        data[dv].append(rmn.fstluk(k))

    rmn.fstcloseall(funit)

    return data


def compute_ens_stat(inp_dir: Path, stat_name="ensmean", nomvar="ETAS"):
    out_dir = inp_dir.parent / f"{inp_dir.name}_{stat_name}"
    out_dir.mkdir(exists_ok=True, parents=True)

    coord_recs, mask_rec = None, None

    for exp_prefix, exp_files in get_grouped_files(inp_dir):

        exp_files = list(exp_files)

        if coord_recs is None:
            coord_recs, mask_rec = fst.get_records_for_coords_and_mask(exp_files[0], nomvar=nomvar)

        data = read_file_group(exp_files)

        out_recs = {dv: recs[0].copy() for dv, recs in data.items()}

        for dv, recs in data.items():
            out_recs[dv] = stat_funcs[stat_name]([r["d"] for r in recs])

        # save the results to the corresponding target files per experiment
        funit = rmn.fstopenall(out_dir / exp_prefix, rmn.FST_RW)

        for c in coord_recs:
            rmn.fstecr(funit, c)

        for dv, out_rec in out_recs.items():

            # write the data
            rmn.fstecr(funit, out_rec)

            # write the mask with the corresponding validity date
            mask_rec.update({"datev": dv})
            rmn.fstecr(funit, mask_rec)

        rmn.fstcloseall(funit)


def compute_ens_median(inp_dir: Path, nomvar="ETAS"):
    """
    Compute ensemble mean
    :param inp_dir:
    :param nomvar:
    """
    compute_ens_stat(inp_dir, stat_name="ensmedian", nomvar=nomvar)


def compute_ens_mean(inp_dir: Path, nomvar="ETAS"):
    """
    Compute ensemble median
    :param inp_dir:
    :param nomvar:
    """
    compute_ens_stat(inp_dir, stat_name="ensmean", nomvar=nomvar)

