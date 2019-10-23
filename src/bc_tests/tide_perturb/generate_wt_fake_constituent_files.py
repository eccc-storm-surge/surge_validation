from pathlib import Path
import numpy as np
import pandas as pd

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_perturbation_fractions(fract_max, n_members=21):
    res = [0]

    # factors are symmetric around 0, not including it
    factors = list(np.linspace(-fract_max, 0, 50))[:-1]
    factors += list([-fi for fi in factors[::-1]])

    np.random.shuffle(factors)

    return np.asarray(res + [factors[i] for i in range(n_members - 1)])


def generate_members(n_members=21, stamp_dir: Path = None,
                     out_dir: Path = None,
                     fake_name_to_base_name: dict = None,
                     max_perturbation_fraction: dict = None):

    n_header_lines = 3

    for new_name, base_name in fake_name_to_base_name.items():

        base_file = stamp_dir / f"{base_name}.barotropic.s2c"

        base_data = pd.read_csv(base_file, header=None, skiprows=n_header_lines, sep=r"\s+")

        # read header to use in the output later
        with base_file.open() as bf:
            header_lines = [next(bf) for _ in range(n_header_lines)]

        famp = get_perturbation_fractions(max_perturbation_fraction[new_name]["amp"], n_members=n_members)
        fphi = get_perturbation_fractions(max_perturbation_fraction[new_name]["phase"], n_members=n_members)

        logger.debug(base_data.head())
        logger.debug(f"phase perturbation factors: {fphi}")
        logger.debug(f"amplitude perturbation factors: {famp}")

        # matrices containing amplitudes and phases for all members
        damp = base_data.loc[:, 1].values.reshape((len(base_data), 1)).dot(famp.reshape((len(famp), 1)).T)
        dphi = base_data.loc[:, 2].values.reshape((len(base_data), 1)).dot(fphi.reshape((len(fphi), 1)).T)

        # add perturbations to the base values
        damp = damp + base_data.loc[:, 1].values[:, np.newaxis]
        dphi = dphi + base_data.loc[:, 2].values[:, np.newaxis]

        logger.debug(f"damp.shape={damp.shape}")

        logger.debug(f"perturbed phases: {dphi[1, :]}")

        # save the perturbed amplitudes and phases into files
        for m_index in range(n_members):
            m_id = f"{m_index:03d}"

            out_file = out_dir / f"{new_name}.{m_id}.barotropic.s2c"

            with out_file.open("w") as of:
                of.writelines(header_lines)

            base_data[1] = damp[:, m_index]
            base_data[2] = dphi[:, m_index]

            base_data.to_csv(out_file, header=None, sep=" ", float_format="%.6f", mode="a", index=False)


def test():
    stm_dir = Path("/home/olh001/C_CPP/WebTide_batch/data/HRglobal")
    out_dir = Path("data/wt_perturbations")

    fake_name_to_base_name = {
        "M2": "M2"
    }

    max_perturbation_fraction = {
        "M2": {"amp": 0.1, "phase": 0.1}
    }

    # make sure that member 0 is not perturbed
    n_members = 21

    out_dir.mkdir(exist_ok=True, parents=True)

    generate_members(stamp_dir=stm_dir, out_dir=out_dir,
                     fake_name_to_base_name=fake_name_to_base_name,
                     max_perturbation_fraction=max_perturbation_fraction, n_members=n_members)


def gen_perturbations_nwatl():
    """
    perutrbations of nwatl webtide dataset
    """
    stm_dir = Path("/home/olh001/C_CPP/WebTide_batch/data/nwatl")
    out_dir = Path("data/wt_perturbations_nwatl_1.0.3_O1")

    fake_name_to_base_name = {
        # "M2": "M2",
        "O1": "O1"
    }

    max_perturbation_fraction = {
        # "M2": {"amp": 0.1, "phase": 0.1},
        "O1": {"amp": 0.1, "phase": 0.1}
    }

    # make sure that member 0 is not perturbed
    n_members = 21

    out_dir.mkdir(exist_ok=True, parents=True)

    generate_members(stamp_dir=stm_dir, out_dir=out_dir,
                     fake_name_to_base_name=fake_name_to_base_name,
                     max_perturbation_fraction=max_perturbation_fraction, n_members=n_members)


def test_get_perturbation_fractions():
    # make sure that member 0 is not perturbed
    n_members = 21

    for _ in range(50):
        f = get_perturbation_fractions(0.01, n_members=n_members)
        logger.debug(
            f
        )
        logger.debug(np.std(f))

        f_unique = np.unique(f)
        logger.debug(len(f_unique))

        if len(f_unique) != n_members:
            for fi in f_unique:
                logger.debug(f"{fi}: {sum(f == fi)} occ.")

        logger.debug(f"pos_count={sum(f > 0)}; neg_count={sum(f < 0)}")


if __name__ == '__main__':
    # test_get_perturbation_fractions()
    # test()
    gen_perturbations_nwatl()
