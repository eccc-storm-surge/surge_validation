
import argparse
from collections import OrderedDict, defaultdict
from pathlib import Path
import pandas as pd
import re

import matplotlib.pyplot as plt


def parse_lead(f_name: str) -> int:
    """
    parse lead time from file names
    """
    pat = re.compile(r".*?(?P<lead>\d+)h")
    m = pat.match(f_name)
    if m:
        return int(m.group("lead"))
    else:
        raise ValueError(f"file name is not recognized: {f_name}")


def read_data(inp_dir: Path, file_ext: str = "csv") -> dict:
    """
    return dict {lead_token: dataframe}
    """

    lead_to_pth_list = defaultdict(list)

    for p in inp_dir.iterdir():
        
        if not p.name.endswith(file_ext):
            continue

        lead = parse_lead(p.name)
        lead_to_pth_list[lead].append(p)

    
    lead_to_data = {}

    for lead, pth_list in lead_to_pth_list.items():
        lead_to_data[lead] = pd.concat([
            pd.read_csv(p) for p in pth_list]).groupby("bin").mean()

    return lead_to_data


def main():
    """
    plot bss and crps scores produced by Syd's scripts

    call as
        python plot_talagrands_mean.py --paths <path1> <path2> ... <pathn> \
                                    --labels <label1> <label2> ... <labeln> \
                                    --colors c1 c2 ... cn \
                                  [ --out_dir ./ ]

    """

    parser = argparse.ArgumentParser("Talagrand rank plots with error bars computed by R scripts.")

    parser.add_argument("--paths", nargs="+",
                    help="space separated paths to the folders containing txt files with CRPS and BSS for each station")

    parser.add_argument("--labels",
                        help="labels of the corresponding paths",
                        nargs="+")

    parser.add_argument("--colors",
                        help="colors of the corresponding labels",
                        nargs="+")

    parser.add_argument("--out_dir", nargs="?", default="./",
                        type=Path,
                        help="Path to the folder, where to store plots",
                        required=False)


    args = parser.parse_args()
    # logger.debug(args)
    
    data_paths = OrderedDict(list(zip(args.labels, [Path(p) for p in args.paths])))
    data_colors = OrderedDict(list(zip(args.labels, args.colors)))
    

    lead_to_fig_ax = {}
    for label in args.labels:
        # read in the data and calculate mean
        data = read_data(data_paths[label])

        # plot
        for lead, df in data.items():

            df["density_lower"] = df.density - df["density_lower"]
            df["density_upper"] = df["density_upper"] - df.density

            if lead in lead_to_fig_ax:
                fig, ax = lead_to_fig_ax[lead]
            else:
                fig = plt.figure()
                ax = fig.gca()
                lead_to_fig_ax[lead] = (fig, ax)

            # ax.plot(df.index, df.density, c=data_colors[label])
            ax.errorbar(df.index, df.density, yerr=df[["density_lower", "density_upper"]].values.T, 
                        c=data_colors[label], label=label, fmt="o")


    for lead, (fig, ax) in lead_to_fig_ax.items():
        ax.set_title(f"Lead={lead} h")
        ax.legend()
        fig.savefig(f"lead_{lead}.png", bbox_inches="tight")
        plt.close(fig)
    

if __name__ == "__main__":
    main()
