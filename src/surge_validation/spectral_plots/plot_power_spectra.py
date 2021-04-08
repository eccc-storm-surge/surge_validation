"""
General spectral analysis
"""
from datetime import timedelta
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from scipy import signal

from ..detiding_validation.config import default_params
from ..utils import log_utils
from ..utils.crosspec import crosspec

from ..detiding_validation import io_manager
import numpy as np


def plot_using_cross_spectra(lbl_to_station_to_ts: dict, img_dir: Path,
                             lbl_to_color: dict,
                             station_dict=default_params.station_dict,
                             fs=timedelta(hours=1)):
    """
    This plots spectra for stations using function developed by Natacha Bernier
    (see comments in utils/crosspec.py)
    m: smoothing parameter

    Update: found equivalent of crosspec in scipy.signal.csd, using it (equivalence is ok)

    create 1 plot per station
    """
    logger = log_utils.get_logger(__name__)

    img_dir.mkdir(exist_ok=True, parents=True)

    # get list off all stations
    all_stations = set()

    m_fraction = 0.25

    for lbl, station_to_ts in lbl_to_station_to_ts.items():
        all_stations.update({s for s in station_to_ts})

    freq_mul = 24 * 3600

    lbl_list = sorted(lbl_to_station_to_ts)

    for station_id in all_stations:
        logger.info(f"Plotting power spectre for {station_id}")
        fig = plt.figure()
        ax = fig.gca()
        assert isinstance(ax, Axes)

        title = f"{station_id}" if not station_id in station_dict else f"{station_dict[station_id]} ({station_id})"

        mod_artists = []
        obs_artists = []

        for lbl_idx, lbl in enumerate(lbl_list):
            # calculate power spectra
            if lbl_idx == 0:
                ts_obs = lbl_to_station_to_ts[lbl][station_id][io_manager.OBS_COL_NAME].asfreq(fs)
                m = int(m_fraction * len(ts_obs))
                x = np.where(ts_obs.isna(), 0, ts_obs.values)
                # freq, px_obs = crosspec(m, x)
                freq, px_obs = signal.csd(x, x, fs=1. / fs.total_seconds(), nperseg=m)
                obs_lines = ax.semilogy(freq * freq_mul, px_obs, color="k", linewidth=2, label="Obs")
                obs_artists.append(obs_lines[0])

                # freq_1, px_1 = signal.csd(x, x, fs=1. / fs.total_seconds(), scaling="spectrum", nperseg=m, detrend=False)

            logger.debug(lbl_to_station_to_ts[lbl][station_id].head())
            for c in lbl_to_station_to_ts[lbl][station_id].columns:
                if not c.startswith("mod"):
                    continue

                ts = lbl_to_station_to_ts[lbl][station_id][c].asfreq(fs)
                m = int(m_fraction * len(ts))
                # freq, px = crosspec(m, ts.values)
                x = np.where(ts.isna(), 0, ts.values)
                freq, px = signal.csd(x, x, fs=1. / fs.total_seconds(), nperseg=m)
                # print(np.real(px), np.imag(px))
                mod_lines = ax.semilogy(freq * freq_mul, px, color=lbl_to_color[lbl], label=lbl)
                mod_artists.append(mod_lines[0])

        ax.legend(handles=obs_artists + mod_artists)
        ax.set_title(title)
        ax.grid(True)
        ax.set_xlabel("Cycles per day")
        ax.set_ylabel(f"m$^2$ / Hz")
        # plt.show()

        fig.savefig(img_dir / f"{station_id}_csd.png")
        plt.close(fig)

