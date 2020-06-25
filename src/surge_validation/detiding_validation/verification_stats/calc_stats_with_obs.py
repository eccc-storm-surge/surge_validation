"""
Calculation of stats of model outputs and obs per station and overall
"""

import pandas as pd

from ..io_manager import VALIDH_COL_NAME, STID_COL_NAME
from .. import io_manager


def weighted_avg(vals_df, counts_df, grouping_col=VALIDH_COL_NAME):
    return (vals_df * counts_df).groupby(grouping_col).sum() / counts_df.groupby(grouping_col).sum()


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

    # group by valid hour and station id
    g = tmp_data.groupby([VALIDH_COL_NAME, STID_COL_NAME])
    res_by_station_and_vhour = g.std()
    counts_by_station_and_vhour = g.count()

    # do not consider some stations in the overall scores
    subset = ~res_by_station_and_vhour.index.get_level_values(STID_COL_NAME).isin(stids_not_overall)
    res_by_station_and_vhour_filt = res_by_station_and_vhour[subset]
    counts_by_station_and_vhour = counts_by_station_and_vhour[subset]

    # calculate the weighted average for all stations
    res_by_vhour = weighted_avg(res_by_station_and_vhour_filt, counts_by_station_and_vhour,
                                grouping_col=VALIDH_COL_NAME)

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
                                  STID_COL_NAME: data["station_id"]})

    tmp_data["obs"] = data["obs"]

    for c in mod_columns:
        tmp_data[f"{c}_gamma"] = data[c] - data["obs"]

    g = tmp_data.groupby([STID_COL_NAME, VALIDH_COL_NAME])

    res_by_station_and_vhour = g.std()
    counts_by_station_and_vhour = g.count()

    for c in mod_columns:
        c = f"{c}_gamma"
        res_by_station_and_vhour[c] = res_by_station_and_vhour[c] ** 2 / res_by_station_and_vhour["obs"] ** 2

    # do not consider some stations in the overall scores
    subset = ~res_by_station_and_vhour.index.get_level_values(STID_COL_NAME).isin(stids_not_overall)
    res_by_station_and_vhour_filt = res_by_station_and_vhour[subset]
    counts_by_station_and_vhour = counts_by_station_and_vhour[subset]

    res_by_vhour = weighted_avg(res_by_station_and_vhour_filt, counts_by_station_and_vhour,
                                grouping_col=VALIDH_COL_NAME)

    res_by_station_and_vhour.sort_values(VALIDH_COL_NAME, inplace=True)
    res_by_vhour.sort_values(VALIDH_COL_NAME, inplace=True)

    return res_by_station_and_vhour, res_by_vhour


def gamma_varobsallvhour(data, stids_not_overall=()):
    mod_columns = io_manager.get_model_column_names(data)

    tmp_data = pd.DataFrame(index=data.index,
                            data={VALIDH_COL_NAME: data[VALIDH_COL_NAME],
                                  STID_COL_NAME: data[STID_COL_NAME]})

    tmp_data["obs"] = data["obs"]

    for c in mod_columns:
        tmp_data[f"{c}_gamma_varobsallvhour"] = data[c] - data["obs"]

    g = tmp_data.groupby([STID_COL_NAME, VALIDH_COL_NAME])

    res_by_station_and_vhour = g.std()
    counts_by_station_and_vhour = g.count()

    var_obs = tmp_data.groupby(STID_COL_NAME).std()["obs"]

    idx = pd.IndexSlice

    for st_id in var_obs.index:
        for c in mod_columns:
            c = f"{c}_gamma_varobsallvhour"
            res_by_station_and_vhour.loc[idx[st_id, :], c] = res_by_station_and_vhour.loc[idx[st_id, :], c] ** 2 / \
                                                             var_obs.loc[st_id] ** 2

    # do not consider some stations in the overall scores
    subset = ~res_by_station_and_vhour.index.get_level_values(STID_COL_NAME).isin(stids_not_overall)
    res_by_station_and_vhour_filt = res_by_station_and_vhour[subset]
    counts_by_station_and_vhour = counts_by_station_and_vhour[subset]

    res_by_vhour = weighted_avg(res_by_station_and_vhour_filt, counts_by_station_and_vhour,
                                grouping_col=VALIDH_COL_NAME)

    # for c in mod_columns:
    #     c = f"{c}_gamma_varobsallvhour"
    #     res_by_vhour[c] = res_by_vhour[c] ** 2 / var_obs_all ** 2

    res_by_station_and_vhour.sort_values(VALIDH_COL_NAME, inplace=True)
    res_by_vhour.sort_values(VALIDH_COL_NAME, inplace=True)

    return res_by_station_and_vhour, res_by_vhour


def stde_obs(data, stids_not_overall=()):
    mod_columns = io_manager.get_model_column_names(data)

    tmp_data = pd.DataFrame(index=data.index,
                            data={VALIDH_COL_NAME: data[VALIDH_COL_NAME],
                                  STID_COL_NAME: data["station_id"]})

    tmp_data["obs"] = data["obs"]

    g = tmp_data.groupby([STID_COL_NAME, VALIDH_COL_NAME])

    res_by_station_and_vhour = g.std()
    counts_by_station_and_vhour = g.count()

    for c in mod_columns:
        c = f"{c}_stde_obs"
        res_by_station_and_vhour[c] = res_by_station_and_vhour["obs"]
        counts_by_station_and_vhour[c] = counts_by_station_and_vhour["obs"]

    # do not consider some stations in the overall scores
    subset = ~res_by_station_and_vhour.index.get_level_values(STID_COL_NAME).isin(stids_not_overall)
    res_by_station_and_vhour_filt = res_by_station_and_vhour[subset]
    counts_by_station_and_vhour = counts_by_station_and_vhour[subset]

    res_by_vhour = weighted_avg(res_by_station_and_vhour_filt, counts_by_station_and_vhour,
                                grouping_col=VALIDH_COL_NAME)

    res_by_station_and_vhour.sort_values(VALIDH_COL_NAME, inplace=True)
    res_by_vhour.sort_values(VALIDH_COL_NAME, inplace=True)
    return res_by_station_and_vhour, res_by_vhour
