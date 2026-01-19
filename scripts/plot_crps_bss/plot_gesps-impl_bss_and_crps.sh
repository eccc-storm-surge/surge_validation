#!/usr/bin/env bash

set -x -e -u 
data_root=~/R/resps_verification_plots/work/gesps-impl/prelim/

declare  -A bss_plot_limits
declare  -A crps_plot_limits

bss_plot_limits["TWL"]="0.1 0.9"
crps_plot_limits["TWL"]="0.0 0.2"

bss_plot_limits["SURGE"]="0 0.6"
crps_plot_limits["SURGE"]="0.03 0.5"
# bss_plot_limits["TWL_ETE2019"]="0 1"
# crps_plot_limits["TWL_ETE2019"]="0. 0.2"


  for v in  TWL SURGE; do
    common_root=${data_root}/scratch_RESPS_${v}_REFvsGESPS_${v}_NEW_V2_2021102700_2022061400
    python /home/olh001/Python/surge_validation/src/surge_validation/diagnostics/resps/plot_bss_and_crps.py \
      --paths  ${common_root}/RESPS_${v}_REF \
               ${common_root}/GESPS_${v}_NEW_V2/ \
      --labels "RESPS (${v}, REF)" "GESPS (${v}, NEW2)" \
      --colors b r --lead_hour_max 360 \
      --out_dir ${common_root} \
      --skip-stations 1970 \
      --bsslim ${bss_plot_limits["${v}"]} \
      --crpslim ${crps_plot_limits["${v}"]}

    # plot talagrands
    python /home/olh001/Python/surge_validation/src/surge_validation/diagnostics/resps/plot_talagrands_mean.py \
    --paths ${common_root}/RESPS_${v}_REF/figs/  \
            ${common_root}/GESPS_${v}_NEW_V2/figs/ \
    --labels "RESPS (${v}, REF)" "GESPS (${v}, NEW2)" \
    --colors b r \
    --out_dir ${common_root}/talagrand 


done


