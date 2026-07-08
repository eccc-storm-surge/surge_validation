# Introduction

This project uses outputs from loadprogs_python to compute and plot scores. Can compare multiple model runs with observations at points (tide gauge locations).

# Usage

Configuration is done in python code. See examples in: `src/experiments/`. Just duplicate a script from `src/experiments/`, modify the copy to your needs and run the script.

# Pixi

To load pixi on science use the following (or a more recent version):

```bash
. r.load.dot /fs/ssm/eccc/cmd/cmds/apps/pixi/202605/00/pixi_0.69.0_all
```

* Install dependencies (need to run only once on set up, after clone for example) 

  ```bash
  pixi install
  ```

* Run selected experiment:

  ```bash
  pixi run python -u src/surge_validation/experiments/nemo36_vs_40/ciopsw/ciopsw_twl_no_JdeF_SoG_rn_Dt.py
  ```
