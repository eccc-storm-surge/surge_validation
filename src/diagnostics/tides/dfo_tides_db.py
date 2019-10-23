from pathlib import Path

import pandas as pd
import sqlite3

import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

DEFAULT_DFO_TIDES_DB = "/home/smco500/.suites/rdsps/forecast/hub/eccc-ppp1/archive_db/archive_tid.sqlite"


class DfoTides(object):
    """
    To access tides sqlite db provided to Devon by DFO
    """
    TIDE_TABLE_NAME = "tide"

    def __init__(self, db_path=DEFAULT_DFO_TIDES_DB):
        self.dbpath = Path(db_path)
        if not self.dbpath.exists():
            raise IOError(f"The sqlite db file does not exist at {self.dbpath}")

        self.conn = sqlite3.connect(str(self.dbpath))

    def get_data_for_stn(self, stn_id=""):
        df = pd.read_sql_query(f"select * from {self.TIDE_TABLE_NAME} where StnId = '{int(stn_id):04d}'", self.conn,
                               parse_dates={"validTime": "%Y-%m-%d %H:%M"})
        df.set_index("validTime", inplace=True)
        return df

    def cleanup(self):
        self.conn.close()


def test():
    dfo_tides = DfoTides(db_path="/home/smco500/.suites/rdsps/forecast/hub/eccc-ppp1/archive_db/archive_tid.sqlite")

    stn_id = "215"
    data = dfo_tides.get_data_for_stn(stn_id=stn_id)

    logger.debug(data)


if __name__ == '__main__':
    test()
