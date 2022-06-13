
# ========== FC70E16V2 vs op (RDSPS, forecast) ===============
import logging
from multiprocessing import Process
from pathlib import Path
from datetime import datetime

from surge_validation.experiments.validation_experiment_base import compare_forecast


def main():
    exp_id = "FC70E16V2"
    exp_label = f"rdsps_fc_{exp_id}"

    st_time = datetime(2016, 6, 25, 9)
    en_time = datetime(2016, 9, 10, 12)

    st_s = f"{st_time:%Y%m%d%H}"
    en_s = f"{en_time:%Y%m%d%H}"

    swl_path_old = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_op_during_{exp_id}_{st_s}_{en_s}/surge_rdsps_forecast_op_during_{exp_id}.dat"
    swl_path_new = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_{exp_id}_{st_s}_{en_s}/surge_rdsps_forecast_{exp_id}.dat"

    exp_id_list = ["op", exp_id]
    exp_id_store = {
        "op": swl_path_old, exp_id: swl_path_new
    }

    img_dir = Path(f"data/plots/{exp_label}_{datetime.utcnow():%Y%m%d%H%M}")

    compare_forecast(img_dir=img_dir, exp_id_to_path=exp_id_store, b2b_nhours=24, exp_id_list=exp_id_list)


def main_36h():
    exp_id = "FC70E16V2"
    exp_label = f"rdsps_fc_{exp_id}"

    st_time = datetime(2016, 6, 25, 9)
    en_time = datetime(2016, 9, 10, 12)

    st_s = f"{st_time:%Y%m%d%H}"
    en_s = f"{en_time:%Y%m%d%H}"

    swl_path_old = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_op_during_{exp_id}_36h_{st_s}_{en_s}/surge_rdsps_forecast_op_during_{exp_id}_36h.dat"
    swl_path_new = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_{exp_id}_36h_{st_s}_{en_s}/surge_rdsps_forecast_{exp_id}_36h.dat"

    exp_id_list = ["op", exp_id]
    exp_id_store = {
        "op": swl_path_old, exp_id: swl_path_new
    }

    img_dir = Path(f"data/plots/{exp_label}_dev_36h")

    compare_forecast(img_dir=img_dir, exp_id_to_path=exp_id_store, b2b_nhours=36, exp_id_list=exp_id_list)


def main_36h_dc101():
    exp_id = "FC70E16V2"
    exp_label = f"rdsps_fc_{exp_id}"

    st_time = datetime(2016, 6, 25, 9)
    en_time = datetime(2016, 9, 10, 12)

    st_s = f"{st_time:%Y%m%d%H}"
    en_s = f"{en_time:%Y%m%d%H}"

    swl_path_old = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_{exp_id}_36h_{st_s}_{en_s}/surge_rdsps_forecast_{exp_id}_36h.dat"
    swl_path_new = f"/home/olh001/Python/loadprogs_python/data/data_for_scoring_rdsps_forecast_{exp_id}_36h_dc101_{st_s}_{en_s}/surge_rdsps_forecast_{exp_id}_36h_dc101.dat"

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Comparing\n (old): {swl_path_old}\n and \n(new): {swl_path_new}")

    exp_id_list = [exp_id, exp_id + "_dc101"]
    exp_id_store = {
        exp_id_list[0]: swl_path_old, exp_id_list[1]: swl_path_new
    }

    # img_dir = Path(f"data/plots/{exp_label}_{datetime.utcnow():%Y%m%d%H%M}")
    img_dir = Path(f"data/plots/{exp_label}_dev_36h_dc101")
    img_dir.mkdir(exist_ok=True, parents=True)

    compare_forecast(img_dir=img_dir, exp_id_list=exp_id_list, exp_id_to_path=exp_id_store,
                     b2b_nhours=36, calculate_scores=True)


if __name__ == '__main__':
    # main()
    Process(target=main_36h_dc101).start()
