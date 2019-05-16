"""
Generate perturbations to the nodal corrections of tidal amplitudes to be used in webtide

input:
    n_members: number of members
    dc_tides_dir: path to the DC_Tides output directory
    wt_dir: path to the WT output directory (should be for the same period as DC_Tides one)
    cn_names: list of constituent names to be perturbed, i.e. [M2,O1]
    perturb_mask: 2 mask field with 1, at the points where perturbation is needed (read from a standard file, i.e. bc_mask)
    prturb_out_dir: directory where to save files containing perturbations

output:
    text files for each constituent and each member named as df_<constit name>_<member id>.txt containing 5 columns:

    I,J,DF,LON,LAT

    I and J are 0-based indices, DF - perturbation, LON and LAT are the coordinates at the point of perturbation.

Note: member 000 is not perturbed, therefore files are not created for 000

"""

from pathlib import Path


def calculate_perturbations(dc_tides_dir: Path=None,
                            wt_dir: Path=None,
                            n_members=20,
                            cn_names=("M2", ),
                            perturb_mask=None,
                            perturb_out_dir: Path=None):

    # calculate rms between dc_tides_dir and wt_dir for the points where perturb_mask == 1



    pass




def main():
    pass


if __name__ == '__main__':
    main()
