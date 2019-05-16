from pathlib import Path
import os
import percache
import numpy as np

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def my_repr(o):
    if isinstance(o, np.ndarray):
        return np.array_repr(o, precision=6)
    return repr(o)


def get_cache(cache_dir=None, token=""):
    """
    get cache decorator for caching purposes
    :param cache_dir:
    :return:
    """
    if cache_dir is None:
        # cache_dir = Path(os.environ["HOME"]) / "data" / os.environ["TRUE_HOST"]
        cache_dir = Path(os.environ["HOME"]) / "data" / "eccc-ppp1" / "caches"
        if not cache_dir.exists():
            raise IOError(f"The cache directory {cache_dir} does not exist, please create appropriate links")

    cache_dir.mkdir(exist_ok=True, parents=True)
    if len(token) == 0:
        cache_file = cache_dir / f"cache"
    else:
        cache_file = cache_dir / f"cache_{token}"

    logger.debug(f"cache file: {cache_file}")
    cache = percache.Cache(str(cache_file), repr=my_repr)
    return cache

