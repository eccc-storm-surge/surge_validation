"""
Calculation of stats of model outputs and obs per station and overall
"""

import pandas as pd

from detiding_validation.io_manager import VALIDH_COL_NAME, STID_COL_NAME

from detiding_validation import io_manager


def stde(data, stids_not_overall=()):
    """

    :param stids_not_overall: ids of the stations excluded from the overall stats
    :param data: pandas DataFrame containing columns
        {valid_hour, time, station_id, obs, mod000, mod001, ..., mod00n or just mod for rdsps}

        returns a dataframe (df) with columns
        {(valid_hour, station_id)=>, modiii_stde or just mod for rdsps} and a dataframe
        (overall_stde) with {(valid_hour)=>, mod000_stde, ..., modnnn_stde}
    """

    mod_columns = io_manager.get_model_column_names(data)

    tmp_data = pd.DataFrame(index=data.index,
                            data={VALIDH_COL_NAME: data[VALIDH_COL_NAME],
                            "station_id": data["station_id"]})

    for c in mod_columns:
        tmp_data[f"{c}_stde"] = data[c] - data["obs"]

    res_by_station_and_vhour = tmp_data.groupby([VALIDH_COL_NAME, STID_COL_NAME]).std()

    res_by_vhour = tmp_data[~tmp_data["station_id"].isin(stids_not_overall)].groupby(VALIDH_COL_NAME).std()

    res_by_station_and_vhour.sort_values(VALIDH_COL_NAME, inplace=True)
    res_by_vhour.sort_values(VALIDH_COL_NAME, inplace=True)

    return res_by_station_and_vhour, res_by_vhour


def gamma(data, stids_not_overall=()):
    """
    Check the stde method for returned objects and input parameter description, the difference here is in the
    calculated statistics gamma = var(O-P)/var(O)
    :param data:
    """

    mod_columns = io_manager.get_model_column_names(data)

    tmp_data = pd.DataFrame(index=data.index,
                            data={VALIDH_COL_NAME: data[VALIDH_COL_NAME],
                            "station_id": data["station_id"]})

    tmp_data["obs"] = data["obs"]

    for c in mod_columns:
        tmp_data[f"{c}_gamma"] = data[c] - data["obs"]

    g = tmp_data.groupby([STID_COL_NAME, VALIDH_COL_NAME])

    res_by_station_and_vhour = g.std()

    res_by_vhour = tmp_data[~tmp_data["station_id"].isin(stids_not_overall)].groupby(VALIDH_COL_NAME).std()

    for c in mod_columns:
        c = f"{c}_gamma"
        res_by_station_and_vhour[c] = res_by_station_and_vhour[c] ** 2 / res_by_station_and_vhour["obs"] ** 2
        res_by_vhour[c] = res_by_vhour[c] ** 2 / res_by_vhour["obs"] ** 2

    res_by_station_and_vhour.sort_values(VALIDH_COL_NAME, inplace=True)
    res_by_vhour.sort_values(VALIDH_COL_NAME, inplace=True)

    return res_by_station_and_vhour, res_by_vhour


def gamma_varobsallvhour(data, stids_not_overall=()):
    mod_columns = io_manager.get_model_column_names(data)

    tmp_data = pd.DataFrame(index=data.index,
                            data={VALIDH_COL_NAME: data[VALIDH_COL_NAME],
                                  "station_id": data["station_id"]})

    tmp_data["obs"] = data["obs"]

    for c in mod_columns:
        tmp_data[f"{c}_gamma_varobsallvhour"] = data[c] - data["obs"]

    g = tmp_data.groupby([STID_COL_NAME, VALIDH_COL_NAME])

    res_by_station_and_vhour = g.std()

    res_by_vhour = tmp_data[~tmp_data["station_id"].isin(stids_not_overall)].groupby(VALIDH_COL_NAME).std()

    var_obs = tmp_data.groupby("station_id").std()["obs"]



    var_obs_all = tmp_data["obs"].std()

    for st_id in var_obs.index:
        for c in mod_columns:
            c = f"{c}_gamma_varobsallvhour"

            res_by_station_and_vhour.loc[(st_id, slice(None)), c] = res_by_station_and_vhour.loc[(st_id, slice(None)), c] ** 2 / var_obs.loc[st_id] ** 2

    for c in mod_columns:
        c = f"{c}_gamma_varobsallvhour"
        res_by_vhour[c] = res_by_vhour[c] ** 2 / var_obs_all ** 2

    res_by_station_and_vhour.sort_values(VALIDH_COL_NAME, inplace=True)
    res_by_vhour.sort_values(VALIDH_COL_NAME, inplace=True)

    return res_by_station_and_vhour, res_by_vhour


def stde_obs(data, stids_not_overall=()):
    mod_columns = io_manager.get_model_column_names(data)

    tmp_data = pd.DataFrame(index=data.index,
                            data={VALIDH_COL_NAME: data[VALIDH_COL_NAME],
                                  "station_id": data["station_id"]})

    tmp_data["obs"] = data["obs"]

    g = tmp_data.groupby([STID_COL_NAME, VALIDH_COL_NAME])

    res_by_station_and_vhour = g.std()

    res_by_vhour = tmp_data[~tmp_data["station_id"].isin(stids_not_overall)].groupby(VALIDH_COL_NAME).std()

    for c in mod_columns:
        c = f"{c}_stde_obs"
        res_by_station_and_vhour[c] = res_by_station_and_vhour["obs"]
        res_by_vhour[c] = res_by_vhour["obs"]

    res_by_station_and_vhour.sort_values(VALIDH_COL_NAME, inplace=True)
    res_by_vhour.sort_values(VALIDH_COL_NAME, inplace=True)
    return res_by_station_and_vhour, res_by_vhour

