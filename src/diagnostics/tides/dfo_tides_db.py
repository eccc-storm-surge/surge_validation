from datetime import datetime
from pathlib import Path

import pandas as pd
import sqlite3

import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

DEFAULT_DFO_TIDES_DB = "/home/smco500/.suites/rdsps/forecast/hub/eccc-ppp4/archive_db/archive_tid.sqlite"


class DfoTides(object):
    """
    To access tides sqlite db provided to Devon by DFO
    """
    TIDE_TABLE_NAME = "tide"
    DATETIME_COL_NAME = "validTime"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M"

    def __init__(self, db_path=DEFAULT_DFO_TIDES_DB):
        self.dbpath = Path(db_path)
        if not self.dbpath.exists():
            raise IOError(f"The sqlite db file does not exist at {self.dbpath}")

        self.conn = sqlite3.connect(str(self.dbpath))

    def get_data_for_stn(self, stn_id="", start_time: datetime = None, end_time: datetime = None):
        """

        :param stn_id:
        :param start_time: inclusive minimum time, use None (default) to disable lower limit
        :param end_time: inclusive maximum time, use None (default) to disable upper limit
        :return: pandas dataframe with levels and dates
        """
        query = f"select * from {self.TIDE_TABLE_NAME} where StnId = '{int(stn_id):04d}'"
        if start_time is not None:
            query += f"and {self.DATETIME_COL_NAME} >= '{start_time.strftime(self.DATETIME_FORMAT)}'"

        if end_time is not None:
            query += f"and {self.DATETIME_COL_NAME} <= '{end_time.strftime(self.DATETIME_FORMAT)}'"

        df = pd.read_sql_query(query,
                               self.conn,
                               parse_dates={"validTime": self.DATETIME_FORMAT})

        df.set_index("validTime", inplace=True)
        return df

    def cleanup(self):
        self.conn.close()


def test():
    dfo_tides = DfoTides(db_path="/home/smco500/.suites/rdsps_20191231/forecast/hub/eccc-ppp4/archive_db/archive_tid.sqlite")

    stn_id = "215"
    data = dfo_tides.get_data_for_stn(stn_id=stn_id, start_time=datetime(2020, 12, 25, 12),
                                      end_time=datetime(2020, 12, 27, 12))

    logger.debug(data)


if __name__ == '__main__':
    test()
