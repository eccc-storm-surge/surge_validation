from pathlib import Path

import numpy as np


class Mask(object):
    """
    Representation of a mask field constructed from slices=[slices_x, slices_y]
    """
    def __init__(self, nx, ny, ind_slices=None):
        self.__mask_field = np.zeros((nx, ny), dtype=np.bool)

        if ind_slices is not None:
            for x_slice, y_slice in zip(*ind_slices):
                self.__mask_field[x_slice, y_slice] = True

    @property
    def mask_field(self):
        return self.__mask_field


def tok_to_slice(tok, ni):
    """
    Taken from the fst_create_mask project (in my personal projects on gitlab)
    :param tok:
    :param ni:
    :return:
    """
    if ":" in tok:
        lims = [f.strip() for f in tok.split(":")]
        if lims[0] == "":
            lims[0] = 0
        if lims[1] == "":
            lims[1] = ni
        lims = [int(l) for l in lims]
        lims = [l if l >= 0 else ni + l for l in lims]
        sl = slice(int(lims[0]), int(lims[1]))
    else:
        i = int(tok)
        if i == -1:
            i = ni - 1
        sl = slice(i, i + 1)
    # print(f"{tok} --> {sl}")
    return sl


def get_bc_mask_resps_1_12():



    pass
