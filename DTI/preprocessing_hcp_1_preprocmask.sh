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
echo $SUBJID, $2, $BIDSIN, $OUTDIR 
echo $OMP_NUM_THREADS

SLEEP 2m

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
