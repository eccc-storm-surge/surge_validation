import logging
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

from surge_validation.experiments import compare_forecast

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    station_dict = OrderedDict([
        ("575", "PORT HAWKESBURY, NS"),
    ])

    st_time = datetime(1900, 1, 1, 0)
    en_time = datetime(2018, 12, 9, 18)

    st_s = f"{st_time:%Y%m%d%H}"
    en_s = f"{en_time:%Y%m%d%H}"

    exp_id = "new_stations_request_201812_Devon"

    swl_path_old = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_new_stations_request_201812_Devon_{st_s}_{en_s}_update/surge_new_stations_request_201812_Devon.dat"
    swl_path_new = swl_path_old

    logger.info(f"Comparing\n (old): {swl_path_old}\n and \n(new): {swl_path_new}")

    exp_id_list = ["new_stations_201812", "new_stations_201812"]
    exp_id_store = {
        exp_id_list[0]: swl_path_old, exp_id_list[1]: swl_path_new
    }

    exp_label = exp_id_list[0]

    # img_dir = Path(f"data/plots/{exp_label}_{datetime.utcnow():%Y%m%d%H%M}")
    img_dir = Path(f"data/plots/{exp_label}")
    img_dir.mkdir(exist_ok=True, parents=True)

    compare_forecast(img_dir=img_dir,
                     exp_id_list=exp_id_list,
                     exp_id_to_path=exp_id_store,
                     b2b_nhours=24,
                     calculate_scores=True, station_dict=station_dict)


if __name__ == '__main__':
    main()
