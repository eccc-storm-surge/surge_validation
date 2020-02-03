from pathlib import Path
import re
import numpy as np
import logging



token_to_sign = {
    "N": 1, "S": -1, "E": 1, "W": -1
}


def parse_lon_lat(s):
    tokens = re.split(r"\s+", s)

    def __parse_coord_value(sel_tokens):
        return (float(sel_tokens[0]) + float(sel_tokens[1]) / 60.) * token_to_sign[sel_tokens[-1]]



    # generalize for the cases where there is no space between the minutes
    # and SNWE directions
    coord_pattern = r"(\d+\.?\d*)\s+(\d+\.?\d*)\s*([NWES])"

    lon, lat = 0, 0
    for token in re.findall(coord_pattern, s):
        if token[-1] in ["N", "S"]:
            lon = __parse_coord_value(token)
        elif token[-1] in ["W", "E"]:
            lat = __parse_coord_value(token)

    return lon, lat


def parse_data_line(s) -> (str, float, float, float):
    tokens = re.split(r"\s+", s)

    period = float(tokens[1])

    freq = 1. / period if period > 0 else np.inf

    return tokens[0], freq, float(tokens[2]), float(tokens[3])


def read_constituent_info(wlev_path: Path):
    """
    :param wlev_path:

    Notes:
    1. station coordinates are on the second line of the file
    2. header lines are terminated with ||
    """

    logger = logging.getLogger(__name__)

    res = {
        "names": [],
        "amp": [],
        "pha": [],
        "freq": [],
        "lon": 0,
        "lat": 0,
        "id": "unknown",
        "station_id": "unknown",
        "station_name": "unknown"
    }


    id_pattern = re.compile(r"\d+")
    with wlev_path.open() as f:
        for i, line in enumerate(f):
            line = line.strip()

            logger.debug(line)

            if i == 0:
                # parse station id
                for m in id_pattern.finditer(line):
                    res["station_id"] = m.group().lstrip("0")
                    break

                # parse station name
                res["station_name"] = re.split(id_pattern, line)[1].strip()

            if i == 1:
                # parse coordinates
                res["lon"], res["lat"] = parse_lon_lat(line)
                pass

            if not line.endswith("||") and len(line) > 0:
                name, freq, amp, pha = parse_data_line(line)
                res["names"].append(name)
                res["amp"].append(amp)
                res["pha"].append(pha)
                res["freq"].append(freq)

    logger.debug(res)
    return res


def read_constituent_info_all_points(data_dir: Path):
    """

    :param data_dir:
    :return: list of dictionaries with the amplitudes, phases and names of the constituents found in `data_dir`
    """
    res = []
    for f in data_dir.iterdir():
        if f.is_dir():
            logger.info(f"Skipping directory {f}")
            continue

        res.append(read_constituent_info(f))

    return res


def test():
    f = Path("/home/olh001/data/ppp1-sitestore/TidalConstituents_UTC/00020const_UTC.wlev")
    read_constituent_info(f)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    test()
