

def stname_to_fname(stname):
    """
    :param stname:
    :return: station name prepared to be used as part of a file name
    """
    return stname.lower().replace(" ", "_").replace("'", "")