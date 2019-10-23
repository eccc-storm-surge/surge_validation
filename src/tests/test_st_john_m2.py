

import pandas as pd
import ttide
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


def test():
    # path = "/home/olh001/Python/loadprogs_python/data/data_for_scoring_prog_tidesbc_only_2018041600_2019041600/surge_prog_tidesbc_only.dat"
    # path = "/fs/site2/dev/eccc/cmd/e/olh001/loadprogs_python_data/data_for_scoring_prog_tidesbc_only_nwatl_2018041600_2018051500/surge_prog_tidesbc_only_nwatl.dat"
    # path = "/fs/site2/dev/eccc/cmd/e/olh001/loadprogs_python_data/data_for_scoring_webtide_nwatl_2018041600_2018051500/surge_webtide_nwatl.dat"
    path = "/fs/site2/dev/eccc/cmd/e/olh001/loadprogs_python_data/data_for_scoring_prog_tidesbc_only_nwatl_wtbathymetry_debug_2018041600_2018050100/surge_prog_tidesbc_only_nwatl_wtbathymetry_debug.dat"

    data = pd.read_csv(path, sep=r"\s+", header=None, converters={4: str})

    st_john_id = 65
    eastport_id = 8410140

    data_sel = data[data[1] == st_john_id]
    # data_sel = data_sel[data_sel[0] <= 36]

    print(data_sel.iloc[:5, :6])
    data_sel.loc[:, "date"] = data_sel[4].map(lambda ts: datetime.strptime(ts, "%Y%m%d%H"))

    data_sel.loc[:, "do"] = data_sel.loc[:, "date"] - data_sel.loc[:, 0].map(lambda xi: timedelta(hours=int(xi)))
    data_sel = data_sel[data_sel["do"] == (datetime(2018, 5, 1) + 0 * timedelta(hours=36))]

    data_sel.set_index("date", inplace=True)
    data_sel.sort_index(inplace=True)
    data_sel = data_sel.asfreq(timedelta(hours=1))

    data_sel.plot(y=[5, 6])

    print(data_sel.index[0], type(data_sel.index[0]))

    tc = ttide.t_tide(data_sel[6].values, stime=data_sel.index[0].to_pydatetime(), lat=data_sel.iloc[0, 2], ray=0.5,
                      out_style=None)

    for cn, cvals in zip(tc["nameu"], tc["tidecon"]):
        cn = cn.decode()
        if "M2" in cn:
            print(f"{cn}: {cvals[0]}")
            break

    plt.show()


if __name__ == '__main__':
    test()

