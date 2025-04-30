
import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import itertools
import warnings
from matplotlib.ticker import MaxNLocator
from sklearn.metrics import r2_score

def plot_annual_extremes(model_label_to_series: dict[str, pd.DataFrame], 
                                    station_id: str,
                                    station_name: str,
                                    label_to_color: dict,
                                    options: dict,
                                    img_dir: Path):
    """

    Find the time of the extreme event in the obs and look for the extremes in the vicinity of the
    observed extreme time extreme(mod_data[te-dt_event:te+dt_event])

    Args:
        model_label_to_series (dict): timeseries data, observation time series has the key "obs"
        station_id (str): station id
        station_name (str): station name
        options (dict): extreme paramters
        img_dir (Path): folder for the scatter plots
    """

    obs_key = "obs"

    
    if obs_key not in label_to_color:
        label_to_color[obs_key] = "k"

    if not img_dir.exists():
        img_dir.mkdir(parents=True, exist_ok=True)
    
    # year_duration = options.get("year_duration", pd.Timedelta(days=365))
    # year_start_month = options.get("year_start_month", 1)

    max_event_duration = options["max_event_duration"]
    n_extremes_per_year = options["n_extremes_per_year"]

    et_to_name = {
        "min": f"mean of {n_extremes_per_year} annual min",
        "max": f"mean of {n_extremes_per_year} annual max"
    }



    extreme_types = options["extreme_types"]

    extreme_type_to_function = {
        "min": min, "max": max
    }

    # {model: {year: {extremetype: extremevalue}}}
    label_to_year_to_extreme = {obs_key: {}}

    obs_data = model_label_to_series["obs"]

    year_to_et_to_te_obs = {}
    
    # get extrema values and timings from obs
    for year, data in obs_data.groupby(obs_data.index.year):
        year_to_et_to_te_obs[year] = {}
        
        label_to_year_to_extreme[obs_key][year] = {}
        for et in extreme_types:
            
            cur_obs = data
            cur_e_values_obs = []
            cur_t_values_obs = []
            

            for _ in range(n_extremes_per_year):

                if len(cur_obs) == 0:
                    print(f"No data to calculate extremes: {station_id}")
                    cur_e_values_obs.append(np.NaN)
                    cur_t_values_obs.append(None)
                    continue
                    

                if et == "max":
                    t_e = cur_obs.idxmax()
                elif et == "min":
                    t_e = cur_obs.idxmin()
                else:
                    raise ValueError(f"Unknown extreme type: {et}")
                
                cur_e_values_obs.append(cur_obs[t_e])
                cur_t_values_obs.append(t_e)
                e_mask = (cur_obs.index <= t_e + max_event_duration) & (cur_obs.index >= t_e - max_event_duration)
                cur_obs = cur_obs[~e_mask]

            year_to_et_to_te_obs[year][et] = cur_t_values_obs
            label_to_year_to_extreme[obs_key][year][et] = np.mean(cur_e_values_obs)


    # find corresponding model extreme values 
    for label, ts in model_label_to_series.items():
        if label == "obs":
            continue

        label_to_year_to_extreme[label] = {}
        for year, data in ts.groupby(ts.index.year):
            label_to_year_to_extreme[label][year] = {}
            cur_obs = obs_data[obs_data.index.year == year]
            for et in extreme_types:
                cur_e_values_mod = []

                for t_e in year_to_et_to_te_obs[year][et]:

                    if t_e is None:
                        cur_e_values_mod.append(np.NaN)
                        continue

                    e_mask_mod = (data.index <= t_e + max_event_duration) & (data.index >= t_e - max_event_duration)
                    if e_mask_mod.any():
                        cur_e_values_mod.append(extreme_type_to_function[et](data[e_mask_mod]))
                    else:
                        cur_e_values_mod.append(np.NaN)

                label_to_year_to_extreme[label][year][et] = np.mean(cur_e_values_mod)


    # plotting
    for et in extreme_types:
        img_file = img_dir / f"{station_id}_{et}.png"

        years = sorted(
            label_to_year_to_extreme[obs_key]
        )

        fig = plt.figure()
        ax = fig.gca()

        for label, year_to_extreme in label_to_year_to_extreme.items():
            values = [(year_to_extreme[year][et] if year in year_to_extreme else np.nan) for year in years ]

            ax.plot(years, values, label=label, color=label_to_color[label], marker="o")

        ax.set_title(f"{station_name} ({station_id})\n{et_to_name[et]}")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend(bbox_to_anchor=(0, -0.1), loc='upper left', borderaxespad=0)
        ax.grid(True)

        fig.savefig(str(img_file), bbox_inches="tight")
        plt.close(fig)

    return label_to_year_to_extreme 


def plot_all_stations_annual_extrema_scatter(stid_label_to_year_to_extreme,
                                             label_to_color: dict,
                                             options: dict,
                                             img_dir: Path):
    
    """Plot scatter plot for each model with obs on x-axis for all stations at the same time

    Args:
        stid_label_to_year_to_extreme (dict): _description_
        label_to_color (dict): _description_
        options (dict): _description_
        img_dir (Path): _description_
    """
    
    obs_key = "obs"

    if "b2b_annual_extremes" not in options:
        return

    print(f"plot_all_stations_annual_extrema_scatter: {img_dir = }")
    n_extremes_per_year = options["b2b_annual_extremes"]["n_extremes_per_year"]


    labels = [] # list of models to compare, including obs.
    years = [] # list of years
    e_types = [] # types of extremes, i.e.: min, max
    st_ids = [stid for stid in stid_label_to_year_to_extreme]

    # determine the list of extreme types
    for stid, label_to_year_to_extrema in stid_label_to_year_to_extreme.items():
        labels = [label for label in label_to_year_to_extrema]
        for label, year_to_extrema in label_to_year_to_extrema.items():
            years = [y for y in year_to_extrema]
            for year, et_to_values in year_to_extrema.items():
                e_types = [et for et in et_to_values]
                break
            break
        break
    
    
    for et in e_types:
        label_to_values = {ml: [] for ml in labels}

        skip = set()
        for label in labels:
            label_to_values[label] = []
            for st_id, year in itertools.product(st_ids, years):
                
                if year in stid_label_to_year_to_extreme[st_id][label]:
                    ex_value = stid_label_to_year_to_extreme[st_id][label][year][et]
                    label_to_values[label].append(ex_value)
                else:
                    warnings.warn(f"annual extremes analysis, no data for {st_id = }; {label = }; {year = }")


        # remove data if nan is encountered in either model
        to_remove = None
        for label, values in label_to_values.items():
            if to_remove is None:
                to_remove = np.isnan(values)
            else:
                to_remove = to_remove | np.isnan(values)

        label_to_values = {label: np.array(values)[~to_remove] for label, values in label_to_values.items()}
        
        # check that all models have the same number of points
        # all should be aligned with obs
        count = None
        label_to_count = {}
        for label, values in label_to_values.items():
            if count is None:
                count = len(values)
            
            label_to_count[label] = len(values)
            assert count == len(values), f"number of extremes should be the same for all models, got {label_to_count}"

        img_file = img_dir / f"scatter_all_stations_{et}_y{years[0]}-{years[-1]}.png"
        fig = plt.figure()
        ax = fig.gca()

        obs_data = label_to_values[obs_key]
        for label in labels:
            
            if label == obs_key:
                continue
           
            r2 = r2_score(obs_data, label_to_values[label])
            legend_label = f"{label}, $R^2 = {r2:.2f}$"

            plt.scatter(obs_data, label_to_values[label], label=legend_label, c=label_to_color[label], zorder=2, s=10)

        ax.set_title(f"Mean of {n_extremes_per_year} annual {et}\nAll stations ({years[0]}-{years[-1]})")
        ax.legend(bbox_to_anchor=(0, -0.1), loc='upper left', borderaxespad=0)
        ax.grid(True)
        xlim = ax.get_xlim()
        ax.axline((xlim[0], xlim[0]), slope=1, color="k", zorder=1)
        fig.savefig(str(img_file), bbox_inches="tight")

        ax.set_xlabel("Observation")
        ax.set_ylabel("Model")

        plt.close(fig)





