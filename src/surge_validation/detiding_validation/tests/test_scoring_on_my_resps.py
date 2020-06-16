from pathlib import Path

from surge_validation.detiding_validation.config import default_params
from surge_validation.detiding_validation import compare_2_simulations


def test():
    img_dir = Path("data/plots/resps_parallel_vs_experimental_std_gamma_test_2017")
    swl_path_old = "/home/olh001/MATLAB/detide/data/data_for_scoring_resps_experimental_2018041700_2018072000/surge_resps_experimental.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/data_for_scoring_resps_parallel_2018041700_2018072000/surge_resps_parallel.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=default_params.station_dict,
                          label_new="RESPS parallel", label_old="RESPS experimental")


if __name__ == '__main__':
    test()