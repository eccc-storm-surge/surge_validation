import importlib
from multiprocessing import Pool
from pathlib import Path



def main():
    all_configs = []
    for mfile in Path(__file__).parent.glob("ciopsw_*.py"):
        m = importlib.import_module(mfile.name[:-3], package=".")
        all_configs.append(m)

    print(f"{len(all_configs)} configs to launch in parallel")
    for cfg in all_configs:
        print(cfg.__name__)

    # run all configs (use a pool of processes for a proper error handling)

    for amodule in all_configs:
        amodule.main()


if __name__ == "__main__":
    main()
