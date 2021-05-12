"""
python /home/olh001/Python/surge_validation/src/surge_validation/diagnostics/resps/plot_bss_and_crps.py \
  --paths  ~/R/resps_verification_plots/work/ci3/scratch_RESPS_Surge_HIV2020_REFvsRESPS_Surge_HIV2020_NEW_2020010100_2020031512/RESPS_Surge_HIV2020_REF \
           ~/R/resps_verification_plots/work/ci3/scratch_RESPS_Surge_HIV2020_REFvsRESPS_Surge_HIV2020_NEW_2020010100_2020031512/RESPS_Surge_HIV2020_NEW/ \
  --labels "RESPS (Surge, REF)" "RESPS (Surge, NEW)" \
  --colors b r --lead_hour_max 360 \
  --out_dir ~/R/resps_verification_plots/work/ci3/scratch_RESPS_Surge_HIV2020_REFvsRESPS_Surge_HIV2020_NEW_2020010100_2020031512/RESPS_Surge_HIV2020_REF_vs_RESPS_Surge_HIV2020_NEW_bsss_crps/
  --bsslim 0 0.6 --crpslim 0.03 0.1
"""
