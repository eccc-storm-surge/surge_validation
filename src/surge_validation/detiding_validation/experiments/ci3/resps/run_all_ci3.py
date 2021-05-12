from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Pool
from pathlib import Path
from joblib import Parallel, delayed

import importlib


# to call each experiment in a pool
def smap(func):
    func()
    return 0


def main():
    all_configs = []
    for mfile in Path(__file__).parent.glob("resps*.py"):
        m = importlib.import_module(mfile.name[:-3], package=".")
        all_configs.append(m)

    print(f"{len(all_configs)} configs to launch in parallel")
    for cfg in all_configs:
        print(cfg.__name__)

    # start a process for each config (use with so it fails correctly when a proc fails)
    # with Pool(processes=len(all_configs)) as p:
    #     p.map(smap, [amodule.main for amodule in all_configs])

    for cfg in all_configs:
        cfg.main()


if __name__ == '__main__':
    main()
