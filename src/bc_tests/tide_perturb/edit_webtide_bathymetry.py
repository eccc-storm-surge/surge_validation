from pathlib import Path

from rpnpy.librmn import all as rmn


def set_wt_bathy_when_deeper(depth_limit_m=3500):

    bathy_dir = Path("/home/olh001/.suites/resps_tides_perturb_nwatl_wtbathymetry/forecast/constants/griddefs/")
    dalcoast_bth = bathy_dir / "grid-atlantic_1_12.fst.orig"
    wt_bth = bathy_dir / "grid-atlantic_1_12.fst.webtide"
    out_bth = bathy_dir / f"grid-atlantic_1_12.fst.edit_deeper{depth_limit_m}"

    # remove the output file first
    if out_bth.exists():
        out_bth.unlink()

    # read Dalcoast bathymetry
    funit_dc = rmn.fstopenall(str(dalcoast_bth))
    h_dc = rmn.fstlir(funit_dc, nomvar="BTMY")["d"]
    # h_dc[h_dc <= 0] = 1.
    rmn.fstcloseall(funit_dc)

    # edit the webtide bathymetry
    funit_wt = rmn.fstopenall(str(wt_bth))
    funit_out = rmn.fstopenall(str(out_bth), rmn.FST_RW)

    all_keys = rmn.fstinl(funit_wt)
    for k in all_keys:
        rec_in = rmn.fstluk(k)
        # do some editing
        if rec_in["nomvar"] == "BTMY":
            h_wt = rec_in["d"].copy()

            places_lt = h_wt <= 3500

            h_wt[places_lt] = h_dc[places_lt]

            rec_in["d"][:, :] = h_wt[:, :]

        rmn.fstecr(funit_out, rec_in)

    rmn.fstcloseall(funit_wt)
    rmn.fstcloseall(funit_out)


def main():
    dalcoast_bth = Path("/home/olh001/.suites/resps_tides_perturb_nwatl_wtbathymetry/forecast/constants/griddefs/grid-atlantic_1_12.fst.orig")
    wt_bth = Path("/home/olh001/.suites/resps_tides_perturb_nwatl_wtbathymetry/forecast/constants/griddefs/grid-atlantic_1_12.fst.webtide")
    out_bth = Path("/home/olh001/.suites/resps_tides_perturb_nwatl_wtbathymetry/forecast/constants/griddefs/grid-atlantic_1_12.fst.edit")

    # remove the output file first
    if out_bth.exists():
        out_bth.unlink()

    # read Dalcoast bathymetry
    funit_dc = rmn.fstopenall(str(dalcoast_bth))
    h_dc = rmn.fstlir(funit_dc, nomvar="BTMY")["d"]
    h_dc[h_dc <= 0] = 1.
    rmn.fstcloseall(funit_dc)

    # edit the webtide bathymetry
    funit_wt = rmn.fstopenall(str(wt_bth))
    funit_out = rmn.fstopenall(str(out_bth), rmn.FST_RW)

    all_keys = rmn.fstinl(funit_wt)
    for k in all_keys:
        rec_in = rmn.fstluk(k)
        # do some editing
        if rec_in["nomvar"] == "BTMY":
            h_wt = rec_in["d"].copy()
            h_wt[h_wt < 1] = 1.

            places_gt = (h_wt / h_dc > 5)
            places_lt = (h_dc / h_wt > 5)

            rec_in["d"][places_gt | places_lt] = h_dc[places_gt | places_lt]

        rmn.fstecr(funit_out, rec_in)

    rmn.fstcloseall(funit_wt)
    rmn.fstcloseall(funit_out)


if __name__ == '__main__':
    # main()
    set_wt_bathy_when_deeper(depth_limit_m=3500)
