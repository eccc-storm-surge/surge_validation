from collections import OrderedDict
from pathlib import Path


def main():
    label_to_data_file = OrderedDict([
        ("HRglobal", Path("/home/olh001/.suites/resps_tides_only_hrglobal/forecast/hub/eccc-ppp2/gridpt/prog_tides/2016121500_000")),
        ("nwatl", Path("/home/olh001/.suites/resps_tides_only_nwatl/forecast/hub/eccc-ppp2/gridpt/prog_tides/2016121500_000"))
    ])

    pass


if __name__ == '__main__':
    main()