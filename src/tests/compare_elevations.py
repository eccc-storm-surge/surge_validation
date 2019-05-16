from pathlib import Path

import pandas as pd
import requests

import json



def main():
    url_template = "https://maps.googleapis.com/maps/api/elevation/json?locations={},{}&key={}"

    key = json.load(open("/home/olh001/.google_elevation_api_key"))["key"]

    interpolated_nwatl_path = Path("/home/olh001/C_CPP/WebTide_batch/data/tides_out_locxy_eta_1_12.dat/tides_20180101000000_20180111000000_60min_nwatl.bat")
    interpolated_hrglobal_path = Path("/home/olh001/C_CPP/WebTide_batch/data/tides_out_locxy_eta_1_12.dat/tides_20180101000000_20180111000000_60min_HRglobal.bat")

    df_nwatl = pd.read_csv(interpolated_nwatl_path, sep="\s+", header=None)
    df_hrglobal = pd.read_csv(interpolated_hrglobal_path, sep="\s+", header=None)

    print(df_nwatl.head())

    print(df_nwatl.head(44))

    json_data = []
    for lon, lat in zip(df_nwatl[1].values, df_nwatl[2].values):
        j = requests.get(url_template.format(lat, lon, key)).json()
        print(lon, lat, j)
        json_data.append(j)

    google_elev = [j["results"][0]["elevation"] for j in json_data]

    df_nwatl = df_nwatl.loc[:, [0, ]]
    df_hrglobal = df_hrglobal.loc[:, [0, ]]

    df_nwatl = df_nwatl.rename({0: "nwatl"}, axis=1)
    df_hrglobal = df_hrglobal.rename({0: "HRglobal"}, axis=1)
    df = pd.concat([df_nwatl, df_hrglobal], axis=1)
    df["Google"] = google_elev

    df.to_csv("elev_comparison.csv")

if __name__ == '__main__':
    main()