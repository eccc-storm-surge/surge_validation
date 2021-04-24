from multiprocessing import Pool

from surge_validation.detiding_validation.experiments.ci3 import \
    gdsps_new_vs_rdsps_ref_surge_fcst_ete2019, \
    gdsps_new_vs_rdsps_ref_surge_fcst_hiv2020, \
    gdsps_new_vs_rdsps_ref_twl_fcst_ete2019, \
    gdsps_new_vs_rdsps_ref_twl_fcst_hiv2020


# to call each experiment in a pool
def smap(func):
    func()
    return 0


def main():
    import sys
    all_configs = [
        v for k, v in sys.modules.items() if "gdsps_new_vs_rdsps_ref" in k
    ]

    # run all configs (use a pool of processes for a proper error handling)

    # start a process for each config (use with so it fails correctly when a proc fails)
    with Pool(processes=len(all_configs)) as p:
        p.map(smap, [amodule.main for amodule in all_configs])


if __name__ == '__main__':
    main()
