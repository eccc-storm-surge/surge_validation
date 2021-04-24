from multiprocessing import Pool

from surge_validation.detiding_validation.experiments.ci3 import \
    gdsps_new_vs_gdsps_ref_surge_fcst_ete2019, \
    gdsps_new_vs_gdsps_ref_surge_fcst_hiv2020, \
    gdsps_new_vs_gdsps_ref_twl_fcst_ete2019, \
    gdsps_new_vs_gdsps_ref_twl_fcst_hiv2020, \
    gdsps_ref_vs_rdsps_ref_surge_fcst_ete2019, gdsps_ref_vs_rdsps_ref_surge_fcst_hiv2020, \
    gdsps_ref_vs_rdsps_ref_twl_fcst_ete2019, gdsps_ref_vs_rdsps_ref_twl_fcst_hiv2020, \
    gdsps_new_vs_rdsps_ref_surge_fcst_ete2019, gdsps_new_vs_rdsps_ref_surge_fcst_hiv2020, \
    gdsps_new_vs_rdsps_ref_twl_fcst_ete2019, gdsps_new_vs_rdsps_ref_twl_fcst_hiv2020


# to call each experiment in a pool
def smap(func):
    func()
    return 0


def main():
    all_surge = [
        gdsps_new_vs_gdsps_ref_surge_fcst_ete2019,
        gdsps_new_vs_gdsps_ref_surge_fcst_hiv2020,
        gdsps_ref_vs_rdsps_ref_surge_fcst_hiv2020,
        gdsps_ref_vs_rdsps_ref_surge_fcst_ete2019,
        gdsps_new_vs_rdsps_ref_surge_fcst_ete2019,
        gdsps_new_vs_rdsps_ref_surge_fcst_hiv2020
    ]

    all_twl = [
        gdsps_new_vs_gdsps_ref_twl_fcst_hiv2020,
        gdsps_new_vs_gdsps_ref_twl_fcst_ete2019,
        gdsps_ref_vs_rdsps_ref_twl_fcst_ete2019,
        gdsps_ref_vs_rdsps_ref_twl_fcst_hiv2020,
        gdsps_new_vs_rdsps_ref_twl_fcst_hiv2020,
        gdsps_new_vs_rdsps_ref_twl_fcst_ete2019
    ]

    all_configs = all_surge + all_twl

    # run all configs (use a pool of processes for a proper error handling)

    # start a process for each config (use with so it fails correctly when a proc fails)
    with Pool(processes=len(all_configs)) as p:
        p.map(smap, [amodule.main for amodule in all_configs])


if __name__ == '__main__':
    main()
