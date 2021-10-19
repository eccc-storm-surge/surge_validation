"""

python /home/olh001/Python/surge_validation/src/surge_validation/diagnostics/resps/plot_bss_and_crps.py \
  --paths  ~/R/resps_verification_plots/work/ci3/scratch_RESPS_Surge_PAR_REFvsRESPS_Surge_PAR_NEW_2021052612_2021100900/RESPS_Surge_PAR_REF \
           ~/R/resps_verification_plots/work/ci3/scratch_RESPS_Surge_PAR_REFvsRESPS_Surge_PAR_NEW_2021052612_2021100900/RESPS_Surge_PAR_NEW/ \
  --labels "RESPS (Surge, REF)" "RESPS (Surge, NEW)" \
  --colors b r --lead_hour_max 384 \
  --out_dir ~/R/resps_verification_plots/work/ci3/scratch_RESPS_Surge_PAR_REFvsRESPS_Surge_PAR_NEW_2021052612_2021100900/RESPS_Surge_PAR_REF_vs_RESPS_Surge_PAR_NEW_bsss_crps/ \
  --bsslim 0 0.6 --crpslim 0.03 0.1


python /home/olh001/Python/surge_validation/src/surge_validation/diagnostics/resps/plot_bss_and_crps.py \
  --paths  ~/R/resps_verification_plots/work/ci3/scratch_RESPS_TWL_PAR_REFvsRESPS_TWL_PAR_NEW_2021052612_2021100900/RESPS_TWL_PAR_REF \
           ~/R/resps_verification_plots/work/ci3/scratch_RESPS_TWL_PAR_REFvsRESPS_TWL_PAR_NEW_2021052612_2021100900/RESPS_TWL_PAR_NEW/ \
  --labels "RESPS (TWL, REF)" "RESPS (TWL, NEW)" \
  --colors b r --lead_hour_max 384 \
  --out_dir ~/R/resps_verification_plots/work/ci3/scratch_RESPS_TWL_PAR_REFvsRESPS_TWL_PAR_NEW_2021052612_2021100900/RESPS_TWL_PAR_REF_vs_RESPS_TWL_PAR_NEW_bsss_crps/ \
  --bsslim 0 0.6 --crpslim 0.03 0.1

"""