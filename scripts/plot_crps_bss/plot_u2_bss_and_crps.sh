#!/usr/bin/env bash

set -x
data_root=~/R/resps_verification_plots/work/u2/

declare  -A bss_plot_limits
declare  -A crps_plot_limits

bss_plot_limits["Surge_HIV2020"]="0 0.6"
crps_plot_limits["Surge_HIV2020"]="0.03 0.09"
bss_plot_limits["TWL_HIV2020"]="0.4 0.8"
crps_plot_limits["TWL_HIV2020"]="0.075 0.2"

bss_plot_limits["Surge_ETE2019"]="0 0.6"
crps_plot_limits["Surge_ETE2019"]="0.03 0.09"
bss_plot_limits["TWL_ETE2019"]="0 1"
crps_plot_limits["TWL_ETE2019"]="0. 0.2"


season=PAR
for leadmax in 72 384; do
    for v in Surge TWL; do
    common_root=/home/olh001/R/resps_verification_plots/work/u2/scratch_RESPS_${v}_PAR_REFvsRESPS_${v}_PAR_NEW_*_384h/

    for cr in ${common_root}; do
        outdir=${cr}/${leadmax}
        mkdir -p ${outdir}
        break
    done
    python /home/olh001/Python/surge_validation/src/surge_validation/diagnostics/resps/plot_bss_and_crps.py \
        --paths  ${common_root}/RESPS_${v}_${season}_REF \
                ${common_root}/RESPS_${v}_${season}_NEW \
        --labels "RESPS (${v}, REF)" "RESPS (${v}, NEW)" \
        --colors b r --lead_hour_max ${leadmax} \
        --out_dir ${outdir}/
    #      --bsslim ${bss_plot_limits["${v}_${season}"]} \
    #      --crpslim ${crps_plot_limits["${v}_${season}"]}
    done
done
