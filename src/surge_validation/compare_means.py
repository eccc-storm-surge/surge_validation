from collections import OrderedDict
from datetime import datetime
from pathlib import Path

from rpnpy.librmn import all as rmn
import numpy as np
from rpnpy.rpndate import RPNDate


def main_pn():
    beg_date = datetime(2018, 4, 22, 6)
    end_date = datetime(2018, 10, 22, 18)

    label_to_data_dir = OrderedDict([
        ("RDSPSPA_PN", Path("/home/olh001/data/ppp2-sitestore/mean_etas_field_with_PN")),
    ])

    nomvar = "ETAS"
    typvar = "P@"

    work(beg_date, end_date, label_to_data_dir, nomvar=nomvar, typvar=typvar)


def get_out_file_path(beg_date_s, end_date_s, label_to_data_dir, lead_t_range=None):
    fst_out_file = "data/fst_surge_out_{}{}{}_lead".format("vs".join(list(label_to_data_dir)),
                                                           beg_date_s,
                                                           end_date_s)

    if lead_t_range is not None:
        fst_out_file += "_{}h_to_{}h".format(*lead_t_range)

    return fst_out_file + ".fst"


def work(beg_date, end_date, label_to_data_dir, nomvar="ETAS", typvar="P@", lead_t_range=None):
    beg_date_s = f"{beg_date:%Y%m%d%H}_"
    end_date_s = f"{end_date:%Y%m%d%H}_"

    fst_out_file = Path(get_out_file_path(beg_date_s, end_date_s, label_to_data_dir, lead_t_range=lead_t_range))

    if fst_out_file.exists():
        fst_out_file.unlink()

    funit_out = rmn.fstopenall(str(fst_out_file), filemode=rmn.FILE_MODE_RW)

    label_to_means = {label: [] for label in label_to_data_dir}

    coords = []

    meta = None
    mask_rec = None

    # calculate means and save them to standard files
    for label, data_dir in label_to_data_dir.items():
        for fst_path in data_dir.iterdir():

            print(fst_path)

            if fst_path.name < beg_date_s:
                continue

            if fst_path.name > end_date_s:
                continue

            print(f"opening {fst_path}")
            funit_in = rmn.fstopenall(str(fst_path))

            keys = rmn.fstinl(funit_in, nomvar=nomvar, typvar=typvar)

            if len(coords) == 0:
                key = rmn.fstinf(funit_in, typvar=typvar, nomvar=nomvar)["key"]

                meta = rmn.fstprm(key)

                coord_keys = rmn.fstinl(funit_in, ip1=meta["ig1"], ip2=meta["ig2"], ip3=meta["ig3"])

                coords.extend([rmn.fstluk(k) for k in coord_keys])

                mask_key = rmn.fstinf(funit_in, typvar="@@", nomvar=nomvar)
                mask_rec = rmn.fstluk(mask_key["key"])

            # filter the keys to include only the forecast hours of interest
            if lead_t_range is not None:
                meta_list = [rmn.fstprm(k) for k in keys]
                lead_t_list = [m["npas"] * m["deet"] / 3600. for m in meta_list]
                keys = [k for k, lt in zip(keys, lead_t_list) if lead_t_range[0] <= lt <= lead_t_range[-1]]

            label_to_means[label].append(np.mean([rmn.fstluk(k)["d"] for k in keys], axis=0))

            rmn.fstcloseall(funit_in)

    # get mean of means
    for label in label_to_means:
        label_to_means[label] = np.asfortranarray(np.mean(label_to_means[label], axis=0))

    # save the coordinates
    for c in coords:
        rmn.fstecr(funit_out, c)

    # save the data
    mask_fields = ["nbits", "datyp", "d", "typvar"]
    for label, the_mean in label_to_means.items():
        rec = {}
        rec.update(meta)
        rec["d"] = the_mean
        rec["etiket"] = label
        rmn.fstecr(funit_out, rec)

        # save the mask
        cur_mask_rec = rec.copy()
        cur_mask_rec.update(
            {k: mask_rec[k] for k in mask_fields}
        )
        rmn.fstecr(funit_out, cur_mask_rec)

    rmn.fstcloseall(funit_out)


def main():
    beg_date = datetime(2017, 1, 1, 00)
    end_date = datetime(2017, 2, 28, 18)

    label_to_data_dir = OrderedDict([
        ("G4_RDSPSPA", Path("/home/olh001/.suites/rdsps/pseudo-analysis/hub/eccc-ppp2/gridpt/prog_archive_raw")),
        ("G5_RDSPSPA", Path("/home/olh001/.suites/rdsps_gem5_research_cycle/pseudo-analysis/hub/eccc-ppp2/gridpt/prog")),
    ])

    nomvar = "ETAS"
    typvar = "P@"

    work(beg_date, end_date, label_to_data_dir, nomvar=nomvar, typvar=typvar)



if __name__ == '__main__':
    main_pn()