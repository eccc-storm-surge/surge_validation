from collections import OrderedDict
from datetime import timedelta
from pathlib import Path
import pandas as pd

from surge_validation.diagnostics import DfoTides
from surge_validation.diagnostics.tides import tide_predictions_based_on_dfo_constituents, wlev

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def compare():

    out_folder = Path("data/dfo_constituents_diags")
    out_folder.mkdir(exist_ok=True, parents=True)

    # ttide tides
    constit_folder = Path("/home/olh001/data/ppp1-sitestore/TidalConstituents_UTC")

    # DFO tides
    dfo_tides_manager = DfoTides()

    dt = timedelta(minutes=15)

    st_id_to_stats = OrderedDict([
        ("st_id",  []),
        ("st_name", []), ("mean_bias", []),
        ("max_bias", []), ("rmse", []),
        ("t_beg", []), ("t_end", []), ("nconstituents", [])
    ])

    for cf in constit_folder.iterdir():
        dfo_constit = wlev.read_constituent_info(cf)

        st_id = dfo_constit["station_id"]

        dfo_tides = dfo_tides_manager.get_data_for_stn(stn_id=st_id)

        if len(dfo_tides) == 0:
            logger.info(f"No dfo tides data for {st_id}, skipping")
            continue

        # for testing
        dfo_tides = dfo_tides.iloc[:1000, :]

        t_beg = dfo_tides.index[0]
        t_end = dfo_tides.index[-1]
        
        logger.debug([t_beg, t_end, len(dfo_tides.index)])
        
        tt_tides = tide_predictions_based_on_dfo_constituents.tides_prediction_accurate(dfo_constit,
                                                                                        t_beg=t_beg, t_end=t_end, dt=dt,
                                                                                        ncpu=40)

        logger.debug("tt_tides\n%s\n%s\n", tt_tides.head(), tt_tides.describe())
        logger.debug("dfo_tides\n%s\n%s\n", dfo_tides.head(), dfo_tides.describe())

        st_name = dfo_constit["station_name"]

        bias = (dfo_tides["tide"] - tt_tides["tide"]).dropna()
        bias = bias.values

        rmse = (bias ** 2).mean() ** 0.5

        st_id_to_stats["st_id"] += [st_id]
        st_id_to_stats["st_name"] += [st_name]
        st_id_to_stats["mean_bias"] += [bias.mean()]
        st_id_to_stats["max_bias"] += [bias.max()]
        st_id_to_stats["rmse"] += [rmse]
        st_id_to_stats["t_beg"] += [t_beg]
        st_id_to_stats["t_end"] += [t_end]
        st_id_to_stats["nconstituents"] += [len(dfo_constit["names"])]

        if rmse >= 0.01:
            import matplotlib.pyplot as plt
            ax = tt_tides.plot(y="tide", label="TTide")
            dfo_tides.plot(ax=ax, y="tide", label="DFO (Devon)")
            plt.title(f"{st_name} ({st_id})")
            plt.legend()
            plt.savefig(out_folder / f"{st_id}.png", bbox_inches="tight")

    df = pd.DataFrame.from_dict(st_id_to_stats)
    logger.debug("\n%s\n", df)
    logger.debug("\n%s\n", df.describe())

    df.sort_values(["rmse", "mean_bias", "max_bias"], inplace=True)

    txt_stats_file = out_folder / Path("tides_comparison_dfo_eccc.csv")
    with txt_stats_file.open("w") as fout:
        fout.write(df.to_string(index=False))


if __name__ == '__main__':
    import time
    t0 = time.perf_counter()
    compare()
    logger.info(f"Execution time {time.perf_counter() - t0:.2f} seconds.")
