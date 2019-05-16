
import pandas as pd

def test_1d():

    data_file = "/home/olh001/MATLAB/detide/download_scripts/meds/2017_201812_CPOP_RDSPS/X1430.dat"

    ts = pd.read_csv(data_file, sep="\s+", header=None)

    print(ts)

    pass


def test():
    test_1d()
    pass


if __name__ == '__main__':
    test()
