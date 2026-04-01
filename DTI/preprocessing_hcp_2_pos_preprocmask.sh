#!/bin/bash -e
umask 0002
# SUBJID=SUBJ050
# cd /dados1/PROJETOS/PRJ1509_MA_FORMACAO/03_PROCS/SCRIPTS/MRTRIX-BIDS
# idor_sub -n 8 -q mrtrix.q -N "PREPROC_$SUBJID" ./preprocessing_hcp.sh $SUBJID /dados1/PROJETOS/PRJ1509_MA_FORMACAO/03_PROCS/RAW_DATA/BIDS /dados1/PROJETOS/PRJ1509_MA_FORMACAO/03_PROCS/PROC_DATA/MULTI_DWI/HCP

SUBJID=$1
BIDSIN=$(realpath $2)
OUTDIR=$(realpath $3)/$SUBJID
CWD=$(pwd)
RAWDIR=$OUTDIR/raw
PREPROCDIR=$OUTDIR/preproc
DWI1_TYPE=dMRIdir98AP
DWI2_TYPE=dMRIdir98PA
DWI3_TYPE=dMRIdir99AP
DWI4_TYPE=dMRIdir99PA

NTHREADS=$OMP_NUM_THREADS
[ -z "$NTHREADS" ] && NTHREADS=0

# IN FILES
T1FILE=( $BIDSIN/sub-$SUBJID/anat/*T1w.nii* )
DWI1nii=( $BIDSIN/sub-$SUBJID/dwi/*${DWI1_TYPE}_dwi.nii* )
DWI1json=( $BIDSIN/sub-$SUBJID/dwi/*${DWI1_TYPE}_dwi.json )
DWI1bval=( $BIDSIN/sub-$SUBJID/dwi/*${DWI1_TYPE}_dwi.bval )
DWI1bvec=( $BIDSIN/sub-$SUBJID/dwi/*${DWI1_TYPE}_dwi.bvec )
DWI2nii=( $BIDSIN/sub-$SUBJID/dwi/*${DWI2_TYPE}_dwi.nii* )
DWI2json=( $BIDSIN/sub-$SUBJID/dwi/*${DWI2_TYPE}_dwi.json )
DWI2bval=( $BIDSIN/sub-$SUBJID/dwi/*${DWI2_TYPE}_dwi.bval )
DWI2bvec=( $BIDSIN/sub-$SUBJID/dwi/*${DWI2_TYPE}_dwi.bvec )
DWI3nii=( $BIDSIN/sub-$SUBJID/dwi/*${DWI3_TYPE}_dwi.nii* )
DWI3json=( $BIDSIN/sub-$SUBJID/dwi/*${DWI3_TYPE}_dwi.json )
DWI3bval=( $BIDSIN/sub-$SUBJID/dwi/*${DWI3_TYPE}_dwi.bval )
DWI3bvec=( $BIDSIN/sub-$SUBJID/dwi/*${DWI3_TYPE}_dwi.bvec )
DWI4nii=( $BIDSIN/sub-$SUBJID/dwi/*${DWI4_TYPE}_dwi.nii* )
DWI4json=( $BIDSIN/sub-$SUBJID/dwi/*${DWI4_TYPE}_dwi.json )
DWI4bval=( $BIDSIN/sub-$SUBJID/dwi/*${DWI4_TYPE}_dwi.bval )
DWI4bvec=( $BIDSIN/sub-$SUBJID/dwi/*${DWI4_TYPE}_dwi.bvec )

# convert raw data (BIDS)
[ ! -d $RAWDIR ] && mkdir -p $RAWDIR
[ ! -f $RAWDIR/T1w.nii.gz ] && cp $T1FILE $RAWDIR/T1w.nii.gz
[ ! -f $RAWDIR/dwi_1.mif ] && echo 2 | mrconvert $DWI1nii $RAWDIR/dwi_1.mif -json_import $DWI1json -fslgrad $DWI1bvec $DWI1bval -force -nthreads $NTHREADS
[ ! -f $RAWDIR/dwi_2.mif ] && echo 2 | mrconvert $DWI2nii $RAWDIR/dwi_2.mif -json_import $DWI2json -fslgrad $DWI2bvec $DWI2bval -force -nthreads $NTHREADS
[ ! -f $RAWDIR/dwi_3.mif ] && echo 2 | mrconvert $DWI3nii $RAWDIR/dwi_3.mif -json_import $DWI3json -fslgrad $DWI3bvec $DWI3bval -force -nthreads $NTHREADS
[ ! -f $RAWDIR/dwi_4.mif ] && echo 2 | mrconvert $DWI4nii $RAWDIR/dwi_4.mif -json_import $DWI4json -fslgrad $DWI4bvec $DWI4bval -force -nthreads $NTHREADS

# set up preprocessing directory
if [ ! -d $PREPROCDIR ]; then
    mkdir -p $PREPROCDIR    
fi
cd $PREPROCDIR

# denoising
[ ! -f dwi_AP.mif ] && mrcat ../raw/dwi_1.mif ../raw/dwi_3.mif dwi_AP.mif
[ ! -f dwi_PA.mif ] && mrcat ../raw/dwi_2.mif ../raw/dwi_4.mif dwi_PA.mif
[ ! -f preproc_mask_AP.mif ] && dwi2mask -clean_scale 0 -bvalue_scaling 1 dwi_AP.mif -nthreads $NTHREADS - | maskfilter - dilate preproc_mask_AP.mif -npass 8 -nthreads $NTHREADS # optional
[ ! -f preproc_mask_PA.mif ] && dwi2mask -clean_scale 0 -bvalue_scaling 1 dwi_PA.mif -nthreads $NTHREADS - | maskfilter - dilate preproc_mask_PA.mif -npass 8 -nthreads $NTHREADS # optional
[ ! -f noiselevel_AP.mif ] && time dwidenoise dwi_AP.mif denoise_AP.mif -noise noiselevel_AP.mif -mask preproc_mask_AP.mif -nthreads $NTHREADS # (real 3m05s)
[ ! -f noiselevel_PA.mif ] && time dwidenoise dwi_PA.mif denoise_PA.mif -noise noiselevel_PA.mif -mask preproc_mask_PA.mif -nthreads $NTHREADS # (real 3m05s)
# mrcalc dwi_AP.mif denoise_AP.mif -sub preproc_mask_AP.mif -mult - | mrview -    # QA inspection
# mrcalc dwi_PA.mif denoise_PA.mif -sub preproc_mask_PA.mif -mult - | mrview -    # QA inspection

# Gibbs ringing correction
[ ! -f degibbs_AP.mif ] && time mrdegibbs denoise_AP.mif degibbs_AP.mif  # (real 2m25s)
[ ! -f degibbs_PA.mif ] && time mrdegibbs denoise_PA.mif degibbs_PA.mif  # (real 2m25s)

# motion and distortion correction
#echo 1 | mrconvert ../dicom b0PA.mif -force
#dwiextract ../dwi.mif -bzero b0AP.mif -force

#mrconvert b0AP.mif -coord 3 0 -nthreads $NTHREADS - | mrcat - b0PA.mif b0pair.mif -axis 3 -force && rm b0AP.mif b0PA.mif

[ ! -f degibbs.mif ] && mrcat degibbs_AP.mif degibbs_PA.mif degibbs.mif
[ ! -f geomcorr.mif ] && time dwipreproc degibbs.mif geomcorr.mif -rpe_header -eddy_options "--repol --ol_type=both --mb=4 --verbose --data_is_shelled "

# bias field correction
[ ! -f biascorr.mif ] && time dwibiascorrect -ants geomcorr.mif biascorr.mif -bias biasfield.mif -nthreads $NTHREADS

# copy to main directory for subsequent processing (could also be symlinked to save disk space)
[ ! -f ../dwi.mif ] && echo 2 | mrconvert biascorr.mif ../dwi.mif -set_property comments "Preprocessed dMRI data." #'[ ! -f ../dwi.mif ] && echo 2 |' acrescentado por Marina quando necessario reprocessar 5ttgen ou flirt...
cd ..

# mask
[ ! -f mask.mif ] && dwi2mask dwi.mif mask.mif -nthreads $NTHREADS #'[ ! -f mask.mif ] &&' acrescentado por Marina quando necessario reprocessar 5ttgen ou flirt... 

# align T1w to DWI
dwiextract dwi.mif -bzero -nthreads $NTHREADS - | mrmath -axis 3 - mean b0.nii -force
flirt -dof 6 -cost normmi -in raw/T1w -ref b0 -omat T_fsl.txt
transformconvert T_fsl.txt raw/T1w.nii.gz b0.nii flirt_import T_T1toDWI.txt && rm T_fsl.txt
mrtransform -linear T_T1toDWI.txt raw/T1w.nii.gz T1w.nii.gz -force

# 5tt segmentation
5ttgen fsl T1w.nii.gz 5ttseg.mif -force
