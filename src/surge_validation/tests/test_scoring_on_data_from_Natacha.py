from pathlib import Path

from surge_validation.config import default_params
from surge_validation.detiding_validation import compare_2_simulations


def test():
    img_dir = Path("data/plots/rdsps_parallel_vs_operational_std_gamma_test_2017")
    swl_path_old = "/home/olh001/MATLAB/detide/data/SSM_from_Natacha/SSM/RESPS/prep_for_ensemble_R_verif/surge_ensemble_jf2017.dat"
    swl_path_new = "/home/olh001/MATLAB/detide/data/SSM_from_Natacha/SSM/RESPS/prep_for_ensemble_R_verif/surge_ensemble_jf2017.dat"

    compare_2_simulations(swl_path_old, swl_path_new, img_dir, station_dict=default_params.station_dict,
                          label_new="Test", label_old="Test")


if __name__ == '__main__':
    test()