"""
Calculation of stats of model outputs and obs per station and overall
"""

import pandas as pd
from numpy.random import default_rng

from ..io_manager import VALIDH_COL_NAME, STID_COL_NAME
from .. import io_manager
import numpy as np
from ...utils import log_utils


def weighted_avg(vals_df, counts_df, grouping_col=VALIDH_COL_NAME):
    # return (vals_df * counts_df).groupby(grouping_col).sum() / counts_df.groupby(grouping_col).sum()
    return vals_df.loc[:, :].multiply(counts_df.iloc[:, 0], axis="index").groupby(grouping_col).sum().divide(
        counts_df.groupby(grouping_col).sum().iloc[:, 0], axis="index")


def calculate_conf_intervals(grouped_data, statfunc, nbootstrap=0, alpha_ci=0.05, rnd=default_rng(seed=42)):
    """

    :param statfunc: like numpy.std,...
    :param grouped_data: key -> dataframe of numbers
    :param nbootstrap:
    :param alpha_ci:
    """
    logger = log_utils.get_logger(__name__)
    ci_ranges = {}
    for key, data in grouped_data:
        try:
            from resample.bootstrap import confidence_interval

            ci_min, ci_max = confidence_interval(statfunc, data.values.flatten(), cl=1 - alpha_ci,
                                                 ci_method="bca",
                                                 size=nbootstrap,
                                                 random_state=rnd)
        except ImportError:
            logger.warn("resample module is not installed, using simple percentile "
                        "method for bootstrap confidence interval")
            bst = rnd.choice(data, size=(nbootstrap, len(data)), replace=True)
            all_stat = statfunc(bst, axis=1)
            ci_min, ci_max = np.percentile(all_stat, [alpha_ci / 2. * 100, 100 - alpha_ci / 2. * 100])

        ci_ranges[key] = (ci_min, ci_max)

    return ci_ranges


def stde(data, stids_not_overall=(), nbootstrap=0, alpha_ci=0.05, **kwargs):
    """

    :param alpha_ci: probability for the values to fall outside the confidence interval (default=0.05),
            used to define confidence intervals during bootstrap

    :param nbootstrap: nbootstrap - number of bootstrap iterations, if <=1, then no bootstrap
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

    suffix = "_stde"

    for c in mod_columns:
        tmp_data[f"{c}{suffix}"] = data[c] - data["obs"]

    # group by valid hour and station id
    g = tmp_data.groupby([VALIDH_COL_NAME, STID_COL_NAME])
    res_by_station_and_vhour = g.std()
    counts_by_station_and_vhour = g.count()

    if nbootstrap > 1:

        for c in mod_columns:
            col_name = f"{c}{suffix}"
            # get confidence intervals
            ci_ranges = calculate_conf_intervals(g[col_name], np.std,
                                                 nbootstrap=nbootstrap,
                                                 alpha_ci=alpha_ci)

            ci_min_cname = f"{col_name}_ci_min"
            ci_max_cname = f"{col_name}_ci_max"

            res_by_station_and_vhour[ci_min_cname] = res_by_station_and_vhour.index.map(lambda i: ci_ranges[i][0])
            res_by_station_and_vhour[ci_max_cname] = res_by_station_and_vhour.index.map(lambda i: ci_ranges[i][1])

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


def gamma(data, stids_not_overall=(), nbootstrap=0, alpha_ci=0.05, **kwargs):
    """
    Check the stde method for returned objects and input parameter description, the difference here is in the
    calculated statistics gamma = var(O-P)/var(O)
    :param data:
    """

    suffix = "_gamma"

    mod_columns = io_manager.get_model_column_names(data)

    tmp_data = pd.DataFrame(index=data.index,
                            data={VALIDH_COL_NAME: data[VALIDH_COL_NAME],
                                  STID_COL_NAME: data["station_id"]})

    tmp_data["obs"] = data["obs"]

    for c in mod_columns:
        tmp_data[f"{c}{suffix}"] = data[c] - data["obs"]

    g = tmp_data.groupby([STID_COL_NAME, VALIDH_COL_NAME])

    res_by_station_and_vhour = g.std()
    counts_by_station_and_vhour = g.count()

    # do bootstrapping if requested
    if nbootstrap > 1:

        rnd = default_rng(seed=42)

        #
        for c in mod_columns:
            colname = f"{c}{suffix}"

            # get confidence intervals (same random seeds so that obs and mod-obs are resampled coherently)
            ci_ranges_num = calculate_conf_intervals(g[colname],
                                                 lambda x: np.std(x) ** 2,
                                                 nbootstrap=nbootstrap,
                                                 alpha_ci=alpha_ci, rnd=rnd)

            ci_ranges_den = calculate_conf_intervals(g["obs"],
                                                 lambda x: np.std(x) ** 2,
                                                 nbootstrap=nbootstrap,
                                                 alpha_ci=alpha_ci, rnd=rnd)

            ci_min_cname = f"{colname}_ci_min"
            ci_max_cname = f"{colname}_ci_max"

            res_by_station_and_vhour[ci_min_cname] = res_by_station_and_vhour.index.map(
                lambda i: ci_ranges_num[i][0] / ci_ranges_den[i][1])

            res_by_station_and_vhour[ci_max_cname] = res_by_station_and_vhour.index.map(
                lambda i: ci_ranges_num[i][1] / ci_ranges_den[i][0])

    for c in mod_columns:
        c = f"{c}{suffix}"
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


def gamma_varobsallvhour(data, stids_not_overall=(), nbootstrap=0, alpha_ci=0.05, **kwargs):
    mod_columns = io_manager.get_model_column_names(data)

    tmp_data = pd.DataFrame(index=data.index,
                            data={VALIDH_COL_NAME: data[VALIDH_COL_NAME],
                                  STID_COL_NAME: data[STID_COL_NAME]})

    suffix = "_gamma_varobsallvhour"

    tmp_data["obs"] = data["obs"]

    for c in mod_columns:
        tmp_data[f"{c}{suffix}"] = data[c] - data["obs"]

    g = tmp_data.groupby([STID_COL_NAME, VALIDH_COL_NAME])

    res_by_station_and_vhour = g.std()
    counts_by_station_and_vhour = g.count()

    g_obs = tmp_data.groupby(STID_COL_NAME)
    var_obs = g_obs.std()[io_manager.OBS_COL_NAME]

    idx = pd.IndexSlice

    for st_id in var_obs.index:
        for c in mod_columns:
            c = f"{c}{suffix}"
            res_by_station_and_vhour.loc[idx[st_id, :], c] = res_by_station_and_vhour.loc[idx[st_id, :], c] ** 2 / \
                                                             var_obs.loc[st_id] ** 2

    # do bootstrapping if requested
    if nbootstrap > 1:
        rnd = default_rng(seed=42)

        for c in mod_columns:
            colname = f"{c}{suffix}"

            # get confidence intervals (same random seeds so that obs and mod-obs are resampled coherently)
            ci_ranges_num = calculate_conf_intervals(g[colname],
                                                 lambda x: np.std(x) ** 2,
                                                 nbootstrap=nbootstrap,
                                                 alpha_ci=alpha_ci, rnd=rnd)

            ci_ranges_den = calculate_conf_intervals(g_obs["obs"],
                                                 lambda x: np.std(x) ** 2,
                                                 nbootstrap=nbootstrap,
                                                 alpha_ci=alpha_ci, rnd=rnd)

            ci_min_cname = f"{colname}_ci_min"
            ci_max_cname = f"{colname}_ci_max"

            res_by_station_and_vhour[ci_min_cname] = res_by_station_and_vhour.index.map(
                lambda i: ci_ranges_num[i][0] / ci_ranges_den[i[0]][1])

            res_by_station_and_vhour[ci_max_cname] = res_by_station_and_vhour.index.map(
                lambda i: ci_ranges_num[i][1] / ci_ranges_den[i[0]][0])




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


def stde_obs(data, stids_not_overall=(), nbootstrap=0, alpha_ci=0.05, **kwargs):
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
        res_by_station_and_vhour[c] = res_by_station_and_vhour[io_manager.OBS_COL_NAME]
        counts_by_station_and_vhour[c] = counts_by_station_and_vhour[io_manager.OBS_COL_NAME]

    # do not consider some stations in the overall scores
    subset = ~res_by_station_and_vhour.index.get_level_values(STID_COL_NAME).isin(stids_not_overall)
    res_by_station_and_vhour_filt = res_by_station_and_vhour[subset]
    counts_by_station_and_vhour = counts_by_station_and_vhour[subset]

    res_by_vhour = weighted_avg(res_by_station_and_vhour_filt, counts_by_station_and_vhour,
                                grouping_col=VALIDH_COL_NAME)

    res_by_station_and_vhour.sort_values(VALIDH_COL_NAME, inplace=True)
    res_by_vhour.sort_values(VALIDH_COL_NAME, inplace=True)
    return res_by_station_and_vhour, res_by_vhour
