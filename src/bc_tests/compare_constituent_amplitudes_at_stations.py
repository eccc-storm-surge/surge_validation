from datetime import datetime
from pathlib import Path


def main():
    plots_dir = Path("data/bc_tests")
    beg_date = datetime(2017, 1, 1)
    end_date = datetime(2018, 1, 1)

    bc_mask_file = Path("/home/olh001/.suites/resps_tides_only_nwatl/forecast/hub/eccc-ppp2/gridpt/tides/bc_mask.fst")
    tides_data_file = Path("/home/olh001/.suites/resps_tides_only_nwatl/forecast/hub/eccc-ppp2/gridpt/tides/2016121500")
    dalcoast_data_file = Path(
        "/home/olh001/.suites/resps_tides_only_nwatl/forecast/hub/eccc-ppp2/gridpt/prog_tides/2016121500_000")

    obs_data_dir = Path("")
    obs_meta_file = Path("")

    # TODO: Plot scatter plots for stations




if __name__ == '__main__':
    main()
