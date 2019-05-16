from pathlib import Path
import pandas as pd

def entry001():
    """
    for 2018/10 CPOP presentation plot variation and mean level for a year
    """
    # archive of the model outputs
    data_dir = Path()

    stations_obs_file = Path("/home/olh001/Python/station_positions_vis/stations_storm_surge_1_30.obs")

    # get list of stations
    obs_df = pd.read_csv(stations_obs_file, skiprows=2, sep="\s+", converters={"NO": lambda s: s.strip()})




def main():
    pass


if __name__ == '__main__':
    main()