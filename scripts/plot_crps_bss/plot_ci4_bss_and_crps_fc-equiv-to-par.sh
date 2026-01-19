#!/usr/bin/env bash

set -x
data_root=~/R/resps_verification_plots/work/ci4/

declare  -A bss_plot_limits
declare  -A crps_plot_limits

bss_plot_limits["Surge_MAM"]="0 0.6"
crps_plot_limits["Surge_MAM"]="0.03 0.09"
bss_plot_limits["TWL_MAM"]="0.4 0.8"
crps_plot_limits["TWL_MAM"]="0.075 0.2"

# bss_plot_limits["Surge_ETE2019"]="0 0.6"
# crps_plot_limits["Surge_ETE2019"]="0.03 0.09"
# bss_plot_limits["TWL_ETE2019"]="0 1"
# crps_plot_limits["TWL_ETE2019"]="0. 0.2"


for season in MAM; do
  for v in Surge TWL; do
    common_root=$(ls -d ${data_root}/scratch_RESPS_${v}_${season}_REFvsRESPS_${v}_${season}_NEW_*)
    python /home/olh001/Python/surge_validation/src/surge_validation/diagnostics/resps/plot_bss_and_crps.py \
      --paths  ${common_root}/RESPS_${v}_${season}_REF \
               ${common_root}/RESPS_${v}_${season}_NEW/ \
      --labels "RESPS (${v}, REF)" "RESPS (${v}, NEW)" \
      --colors b r --lead_hour_max 360 \
      --out_dir ${data_root}/scratch_RESPS_${v}_${season}_REFvsRESPS_${v}_${season}_NEW_*/
#      --bsslim ${bss_plot_limits["${v}_${season}"]} \
#      --crpslim ${crps_plot_limits["${v}_${season}"]}

       # plot talagrands
    python /home/olh001/Python/surge_validation/src/surge_validation/diagnostics/resps/plot_talagrands_mean.py \
    --paths ${common_root}/RESPS_${v}_${season}_REF/figs/  \
            ${common_root}/RESPS_${v}_${season}_NEW/figs/ \
    --labels "RESPS (${v}, REF)" "RESPS (${v}, NEW)" \
    --colors b r \
    --out_dir ${common_root}/talagrand 
  done
done

