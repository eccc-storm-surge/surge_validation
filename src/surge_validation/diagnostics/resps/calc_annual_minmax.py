from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import pytz
from rpnpy.rpndate import RPNDate

from surge_validation.utils.io_utils import fst
import numpy as np

from rpnpy.librmn import all as rmn


def get_coords_from_dir(a_dir: Path, nomvar="ETAS"):
    """
    Assuming the files are fst and contain LO and LA 2d fields
    :param a_dir:
    :return:
    """
    for f in a_dir.iterdir():
        fu = rmn.fstopenall(str(f))
        lon = rmn.fstlir(fu, nomvar="LO")
        lat = rmn.fstlir(fu, nomvar="LA")
        xrec = rmn.fstlir(fu, nomvar=">>")
        yrec = rmn.fstlir(fu, nomvar="^^")
        maskrec = rmn.fstlir(fu, nomvar=nomvar, typvar="@@")
        rmn.fstcloseall(fu)
        return lon, lat, xrec, yrec, maskrec


def main():
    inp_dir = Path("/home/pat003/data/eccc-ppp4/maestro_hubs/resps/forecast/gridpt/prog_surge_tides_leveled")
    out_dir = Path("data/annual_min_max/")

    out_dir_txt = out_dir / "txt"
    out_dir_fst = out_dir / "fst"

    for f in [out_dir_fst, out_dir_txt]:
        f.mkdir(parents=True, exist_ok=True)

    limit_month = 7
    beg_time = datetime(1980, limit_month, 1, tzinfo=pytz.utc)

    # TODO: redo 2010 without caching as cache contains not complete set (folder content changed since the first run)
    #
    end_time = datetime(2010, limit_month, 1, tzinfo=pytz.utc)

    nomvar = "ETAS"
    lon, lat, xrec, yrec, mask_rec = get_coords_from_dir(inp_dir, nomvar=nomvar)

    file_count = len([fi for fi in inp_dir.iterdir()])

    for y in range(beg_time.year, end_time.year):
        q = OrderedDict([
            ("nomvar", "ETAS"),
            ("typvar", "P@"),
            ("beg_time", beg_time.replace(year=y)),
            ("end_time", beg_time.replace(year=y+1)),
            ("member_ids", ("",)),
            ("n_b2b_hours", 12),
            ("file_count", file_count)  # to catch changes in the number of files in the directory
        ])

        data = fst.get_b2b_data_from_dir(inp_dir, data_query=q).squeeze()

        print(f"data.shape={data.shape}")

        the_min = data.min(axis=0)
        the_max = data.max(axis=0)

        fmt = "%.4f"
        np.savetxt(out_dir_txt / f"min_{y}.txt", X=the_min, fmt=fmt)
        np.savetxt(out_dir_txt / f"max_{y}.txt", X=the_max, fmt=fmt)
        np.savetxt(out_dir / "lon.txt", X=lon["d"], fmt=fmt)
        np.savetxt(out_dir / "lat.txt", X=lat["d"], fmt=fmt)
        np.savetxt(out_dir / "mask.txt", X=mask_rec["d"], fmt=fmt)

        data_rec = mask_rec.copy()
        t = datetime(y, limit_month, 1)
        t_rpn = RPNDate(mydate=t)
        print(f"Assigning: time to the min-max = {t}")
        data_rec["datev"] = t_rpn
        data_rec["dateo"] = t_rpn.dateo
        data_rec["nomvar"] = nomvar
        data_rec["typvar"] = "P@"
        data_rec["datyp"] = rmn.FST_DATYP_LIST["float16_compressed"]
        data_rec["nbits"] = 16

        mask_rec["datev"] = data_rec["datev"]
        mask_rec["dateo"] = data_rec["dateo"]
        extremes = {
            "min": the_min, "max": the_max
        }

        for ext_type, ext_vals in extremes.items():
            data_rec["d"] = np.asfortranarray(ext_vals)

            recs = [data_rec, mask_rec, xrec, yrec]

            out_file = out_dir_fst / f"{ext_type}_{y}.fst"
            out_file.unlink(missing_ok=True)
            fu = rmn.fstopenall(str(out_file), filemode=rmn.FST_RW)
            for rec in recs:
                rmn.fstecr(fu, rec)

            rmn.fstcloseall(fu)


if __name__ == "__main__":
    main()
