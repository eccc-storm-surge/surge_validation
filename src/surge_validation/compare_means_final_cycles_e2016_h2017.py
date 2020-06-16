from collections import OrderedDict
from datetime import datetime
from pathlib import Path

from surge_validation.compare_means import work


h_beg_date = datetime(2016, 12, 30, 00)
h_end_date = datetime(2017, 2, 23, 18)

e_beg_date = datetime(2016, 6, 30, 00)
e_end_date = datetime(2016, 8, 26, 18)

lead_t_range_fc = (96, 120)


def main_pa_h2017():
    label_to_data_dir = OrderedDict([
        ("op", Path("/home/olh001/data/ppp1-sitestore/rdsps/FC70H17V2_ops/pseudo-analysis")),
        ("FC70H17V2", Path("/home/olh001/data/ppp1-sitestore/rdsps/FC70H17V2_par/pseudo-analysis")),
    ])

    nomvar = "ETAS"
    typvar = "P@"

    work(h_beg_date, h_end_date, label_to_data_dir, nomvar=nomvar, typvar=typvar)

def main_pa_e2016():
    label_to_data_dir = OrderedDict([
        ("op", Path("/home/olh001/data/ppp1-sitestore/rdsps/FC70E16V2_ops/pseudo-analysis")),
        ("FC70E16V2", Path("/home/olh001/data/ppp1-sitestore/rdsps/FC70E16V2_par/pseudo-analysis")),
    ])

    nomvar = "ETAS"
    typvar = "P@"

    work(e_beg_date, e_end_date, label_to_data_dir, nomvar=nomvar, typvar=typvar)



def main_fc_h2017():
    label_to_data_dir = OrderedDict([
        ("op", Path("/home/olh001/data/ppp1-sitestore/rdsps/FC70H17V2_ops/forecast")),
        ("FC70H17V2", Path("/home/olh001/data/ppp1-sitestore/rdsps/FC70H17V2_par/forecast")),
    ])

    nomvar = "ETAS"
    typvar = "P@"
    work(h_beg_date, h_end_date, label_to_data_dir, nomvar=nomvar, typvar=typvar, lead_t_range=lead_t_range_fc)


def main_fc_e2016():
    label_to_data_dir = OrderedDict([
        ("op", Path("/home/olh001/data/ppp1-sitestore/rdsps/FC70E16V2_ops/forecast")),
        ("FC70E16V2", Path("/home/olh001/data/ppp1-sitestore/rdsps/FC70E16V2_par/forecast")),
    ])

    nomvar = "ETAS"
    typvar = "P@"
    work(e_beg_date, e_end_date, label_to_data_dir, nomvar=nomvar, typvar=typvar, lead_t_range=lead_t_range_fc)


def main():
    #    main_fc_h2017()
    #    main_fc_e2016()

    main_pa_h2017()
    main_pa_e2016()


if __name__ == '__main__':
    main()