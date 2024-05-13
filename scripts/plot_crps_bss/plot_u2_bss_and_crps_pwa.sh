#!/usr/bin/env bash

. ssmuse-sh -p /fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64

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


outdir=data/pwa_test
mkdir -p ${outdir}

season=ptb
for leadmax in 240; do
    for v in twl; do
    common_root=/home/pwa001/resps_verification_plots/work/scratch_${v}_NA_2020030100_2020070100/

   python /home/olh001/Python/surge_validation/src/surge_validation/diagnostics/resps/plot_bss_and_crps.py \
        --paths  ${common_root}/${v}_ptb \
                ${common_root}/${v}_ptb2 \
        --labels "GESPS (${v}, ptb)" "GESPS (${v}, ptb2)" \
        --colors b r --lead_hour_max ${leadmax} \
	--skip-stations False \
        --out_dir ${outdir}/
    #      --bsslim ${bss_plot_limits["${v}_${season}"]} \
    #      --crpslim ${crps_plot_limits["${v}_${season}"]}
    done
done
