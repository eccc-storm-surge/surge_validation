from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def path_to_member_id(fp: Path):
    return fp.name.split(".")[1]


def plot_member_scatter(ax, data_store: dict, control_mem_id="000", logy=False, npoints=None):
    style = "o"
    markersize = 0.05
    for m_id, data in data_store.items():
        data = data[:npoints] if npoints is not None else data
        if m_id != control_mem_id:
            if logy:
                ax.semilogy(data, style, lw=0.05, color="0.55", markersize=markersize)
            else:
                ax.plot(data, style, lw=0.05, color="0.55", markersize=markersize)

    data = data_store[control_mem_id]
    data = data[:npoints] if npoints is not None else data

    if logy:
        ax.semilogy(data, style, color="k", markersize=markersize)
    else:
        ax.plot(data, style, color="k", markersize=markersize)

    ax.set_xlabel("Position index")
    # ax.grid(True)


def plot_wt_perturbations(data_dir: Path, control_mem_id="000", skiprows=3):

    amp = {}
    pha = {}

    for f in data_dir.iterdir():

        if f.name.startswith("."):
            continue

        m_id = path_to_member_id(f)

        print(m_id)
        df = pd.read_csv(f, header=None, sep=r"\s+", skiprows=skiprows)

        amp[m_id] = df[1]
        pha[m_id] = df[2]

    # plotting
    fig, axes = plt.subplots(1, 2)

    # amplitudes
    ax = axes[0]
    ax.set_title("Amp.")
    plot_member_scatter(ax, amp, control_mem_id=control_mem_id, npoints=None)

    # phases
    ax = axes[1]
    ax.set_title("Pha.")
    plot_member_scatter(ax, pha, control_mem_id=control_mem_id, npoints=None)

    fig.savefig("data/plots/wt_perturbation_constit_nwatl.png", dpi=300, bbox_inches="tight")


def test():
    # data_dir = Path("data/wt_perturbations")
    # data_dir = Path("/home/olh001/.suites/resps_tides_perturb/forecast/constants/wt_perturbations")
    data_dir = Path("data/wt_perturbations_nwatl_1.0.0")
    plot_wt_perturbations(data_dir=data_dir)


if __name__ == '__main__':
    test()
