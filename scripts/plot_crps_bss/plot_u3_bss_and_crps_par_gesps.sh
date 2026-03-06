#!/usr/bin/env bash

set -x
data_root=~/R/resps_verification_plots/work/u3/gesps/par/

declare  -A bss_plot_limits
declare  -A crps_plot_limits

bss_plot_limits["Surge_FS22"]="0 0.6"
crps_plot_limits["Surge_FS22"]="0.03 0.09"
bss_plot_limits["TWL_FS22"]="0.4 0.8"
crps_plot_limits["TWL_FS22"]="0.075 0.2"

# bss_plot_limits["Surge_ETE2019"]="0 0.6"
# crps_plot_limits["Surge_ETE2019"]="0.03 0.09"
# bss_plot_limits["TWL_ETE2019"]="0 1"
# crps_plot_limits["TWL_ETE2019"]="0. 0.2"


for v in TWL; do
  common_root=$(ls -d ${data_root}/scratch_GESPS_${v}_REFvsGESPS_${v}_NEW_*)
  python /home/olh001/Python/surge_validation/src/surge_validation/diagnostics/resps/plot_bss_and_crps.py \
    --paths  ${common_root}/GESPS_${v}_REF \
              ${common_root}/GESPS_${v}_NEW/ \
    --labels "GESPS (${v}, REF)" "GESPS (${v}, NEW)" \
    --colors b r --lead_hour_max 72 \
    --out_dir ${data_root}/scratch_GESPS_${v}_REFvsGESPS_${v}_NEW_*/ \
    --obs-file /home/olh001/Python/obs_to_grid_mapping/gesps/gesps_global_obs_v3.0.0.obs \
    --skip-stations 9443090 3980 9449424 6485 6380
done

