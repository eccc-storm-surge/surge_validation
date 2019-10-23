from pathlib import Path
from rpnpy.librmn import all as rmn
from rpnpy.rpndate import RPNDate
import pandas as pd
import matplotlib.pyplot as plt

rmn.fstopt(rmn.FSTOP_MSGLVL, rmn.FSTOPI_MSG_FATAL)


def main():
    # inp_dir = Path("/home/olh001/.suites/resps_tides_perturb/forecast/hub/eccc-ppp2/gridpt/tides_all_constit")
    # exp_label = "WT_001"

    # inp_dir = Path("/home/olh001/.suites/resps_tides_perturb/forecast/hub/eccc-ppp2/gridpt/tides_M2_dphimax0.5")
    # exp_label = "WT_M2_dphimax0.5"

    # inp_dir = Path("/home/olh001/.suites/resps_tides_perturb/forecast/hub/eccc-ppp2/gridpt/tides_M2")
    # exp_label = "WT_M2"

    inp_dir = Path("/home/olh001/.suites/resps_tides_perturb/forecast/hub/eccc-ppp2/gridpt/tides_1yr")
    exp_label = "WT_1yr"


    img_dir = Path(f"data/plots/points_{exp_label}")

    img_dir.mkdir(parents=True, exist_ok=True)

    exp_t = "2018040612"
    nomvar = "SSHT"
    typvar = "P@"

    bof_i = 83
    bof_j = 39

    #i, j = bof_i, bof_j
    # i, j = 308, 13
    i, j = 226, 34
    flist = [f for f in inp_dir.iterdir() if f.name.startswith(exp_t)]

    data = {"time": [], "value": [], "member": []}

    for f in flist:
        m_id = f.name.split("_")[-1]

        funit = rmn.fstopenall(str(f))

        keys = rmn.fstinl(funit, nomvar=nomvar, typvar=typvar)

        for k in keys:
            rec = rmn.fstluk(k)
            data["time"].append(RPNDate(rec["datev"]).toDateTime())
            data["member"].append(m_id)
            data["value"].append(rec["d"][i, j])

        rmn.fstcloseall(funit)

    df = pd.DataFrame.from_dict(data)

    # do the plotting
    img_file = img_dir / f"{exp_t}_I{i}_J{j}.png"
    fig = plt.figure()
    ax = fig.gca()
    ax.set_title(f"I={i}; J={j}")
    for m_id, m_df in df.groupby("member"):

        m_df = m_df.sort_values("time")

        color = "k" if m_id == "000" else "0.55"
        linewidth = 1 if m_id == "000" else 0.3
        zorder = 10 if m_id == "000" else -1

        m_df.plot(x="time", y="value", lw=linewidth, color=color, ax=ax, grid=True, legend=False, zorder=zorder)

    fig.savefig(str(img_file), bbox_inches="tight", dpi=300)


if __name__ == '__main__':
    main()
