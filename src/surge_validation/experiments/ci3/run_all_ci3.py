import importlib
from multiprocessing import Pool
from pathlib import Path


def smap(func):
    func()
    return 0


def main():
    all_configs = []
    for mfile in Path(__file__).parent.glob("gdsps_*.py"):
        m = importlib.import_module(mfile.name[:-3], package=".")
        all_configs.append(m)

    print(f"{len(all_configs)} configs to launch in parallel")
    for cfg in all_configs:
        print(cfg.__name__)

    # run all configs (use a pool of processes for a proper error handling)

    # start a process for each config (use with so it fails correctly when a proc fails)
    with Pool(processes=len(all_configs)) as p:
        p.map(smap, [amodule.main for amodule in all_configs])


if __name__ == '__main__':
    main()
