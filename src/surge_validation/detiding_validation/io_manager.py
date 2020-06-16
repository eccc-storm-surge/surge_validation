import logging
from datetime import datetime
from pathlib import Path
import re
from surge_validation.detiding_validation.config import default_params
import pandas as pd



TIME_COL_NAME = "time"
VALIDH_COL_NAME = "valid_hour"
STID_COL_NAME = "station_id"
LAT_COL_NAME = "lat"
LON_COL_NAME = "lon"

# indices of the columns in the input file
INFILE_STID_INDEX = 1
INFILE_LAT_INDEX = 2
INFILE_LON_INDEX = 3

SPACE_SEPARATED_XDAT = 1
MODEL_AND_OBS_ONE_FILE = 2

known_formats = [SPACE_SEPARATED_XDAT, MODEL_AND_OBS_ONE_FILE]


def read_wl_station_data(data_store, station_dict=default_params.station_dict,
                         format=MODEL_AND_OBS_ONE_FILE, fname_suffix=".dat", max_lead_hour=None):
    """
    The data is returned as a pandas dataframe {time, station_id, obs, model1, model2, ... modeln}

    :param data_store: if data_store is a folder, look for data files containing station id in their names
    :param station_dict:
    :param format:
    :param fname_suffix:
    """

    data_store_p = Path(data_store)

    assert data_store_p.exists(), f"{data_store_p} does not exist"

    id_to_data_file = {}

    logging.info(f"Reading {data_store_p} ...")

    if data_store_p.is_file():
        df = pd.read_csv(data_store_p, sep=r"\s+", header=None, index_col=False,
                         converters={1: str,
                                     0: int,
                                     2: float, 3: float,
                                     4: lambda s: datetime.strptime(s, "%Y%m%d%H")})

        col_names = [VALIDH_COL_NAME, STID_COL_NAME, LAT_COL_NAME, LON_COL_NAME, TIME_COL_NAME, "obs", ]

        if len(df.columns) - len(col_names) > 1:
            col_names = col_names + [f"mod{i:03d}" for i in range(len(df.columns) - len(col_names))]
        else:
            col_names = col_names + ["mod", ]

        df.columns = col_names

        # select only data for selected station ids
        select_ids = list(station_dict)
        df = df[df["station_id"].isin(select_ids)]

    elif data_store_p.is_dir():
        for p in data_store_p.iterdir():
            if not p.name.endswith(fname_suffix):
                continue

            d = int(re.findall(r"\d+", p.name)[0])
            id_to_data_file[d] = p

        df_list = []
        for st_id, st_name in station_dict.items():
            df_list.append(get_df_from_space_separated_xdat(id_to_data_file[st_id], st_id))

        df = pd.concat(df_list)
    else:
        raise IOError(f"{data_store}: Does not exist or unknown data store type")

    # filter only lead hour less than the maximum specified
    if max_lead_hour is not None:
        df = df[df[VALIDH_COL_NAME] <= max_lead_hour]

    return df


def get_df_from_space_separated_xdat(fpath, station_id):
    data = {TIME_COL_NAME: [], "obs": [], "station_id": []}

    with fpath.open() as f:
        for line in f:
            row = line.split()
            data[TIME_COL_NAME].append(datetime.strptime(f"{row[0]}{row[1]}{row[2]}{row[3]}", "%Y%m%d%H"))

            data["station_id"].append(station_id)

            data["obs"].append(float(row[-1]))

    return pd.DataFrame.from_dict(data)


def get_model_column_names(df, suffix=""):
    return [f"{c}{suffix}" for c in df if c.startswith("mod")]
