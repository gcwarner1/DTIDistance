#!/usr/local/bin/bash
#set -x  # Uncomment this for debugging purposes
set -e   # Bail out if any unchecked command fails.

#####
# Set up the paths for all required software.
#####

#PATH=/usr/pubsw/bin:$PATH                            # MATLAB
#PATH=/usr/pubsw/fsl/bin:$PATH                        # FSL/dtifit
#PATH=/usr/pubsw/packages/dtk/current:$PATH           # DTK/dti_recon
#PATH=/autofs/cluster/qtim/users/jevans/bin:$PATH
#PATH=/usr/pubsw/packages/AFNI/current:$PATH         # AFNI

#FREESURFER_HOME=/usr/local/freesurfer/stable5_3_0    # Freesurfer/dt_recon
#source $FREESURFER_HOME/FreeSurferEnv.sh

#export FREESURFER_HOME
#export PATH

#source /autofs/cluster/qtim/users/jevans/bin/qtimcommon.lib

#####
# Usage
#####

usage="
   DiffRecon <options> <Input Directory> <Output Directory>
   Copyright 2013 Michael A. Levine
   Almost totally rewritten by John Evans
   Modified by Xiao Da
   Massachusetts General Hospital

   Optional Flags:
     -b comma-delimited list of b-values
     -i <Input Directory>
     -o <Output Directory>
     -h \"Help\" Displays Usage (this message)
     -v Turn on verbose mode.
     -s reconstructure scheme (default is dtifit)

   Flags -i and -o can be used to specify the input and output directories
   respectively.  

   The -b flag allows you to restrict the b-values to a particular subset.
   If not provided, diffusion reconstruction will use all b-values available.

   The reconstruction scheme can be specified with the -s flag and may be 
   chosen to be any of 

       * dt_recon (Freesurfer)
       * dti_recon (Diffusion Toolkit)
       * dtifit (FSL, the default)

   Summary:
   DiffRecon Reconstructs ADC and FA maps (among other things) from
   the raw Diffusion Data.  Gradient Directions and B-Values must
   be found in DICOM headers.  Bugs may be reported to Mike Levine
   <levine@nmr.mgh.harvard.edu>

" 

#####
# Input Handling
#####
bvalues=
scheme=dtifit
verbose=0
while test $# -gt 0
do
    case $1 in 

        -b )
            bvalues="$2"
            shift
            ;;

        -h )
            echo  "$usage"; exit               ;;

        -v | --v )
            set -x
            verbose=1
            ;;

        -i )
            indir=`readlink -f "$2"`
            shift
            ;;

        -o )
            outdir=$(readlink -f "$2")
            if [ -z "$outdir" ]
            then
                outdir=$2
            fi
            shift
            ;;

        -s )
            if echo $2 | egrep "^(dtifit|dti_recon|dt_recon)$" > /dev/null 2>&1
            then
                scheme=$2
            else
                echo "Unrecognized scheme." >&2
                exit 1
            fi
            shift
            ;;

        * )
           echo "Unrecognized option \"$1"\" >&2
           exit

    esac
    shift
done

if [ -z "$indir" ] && [ -z "$outdir" ]; then
    indir=$(readlink -f $1)
    outdir=$(readlink -f $2)
fi

if [ -z "$outdir" ]; then
   outdir=$2
fi

if [ -z "$indir" ]; then
   echo "$usage"
   exit
fi

if [ ! -d "$indir" ]; then
   echo "Invalid Input Dir. Enter flag -h for usage"
   exit
fi

if [ ! -d "$outdir" ]; then
   mkdir -p "$outdir"
   if [ ! -d "$outdir" ]; then echo "Output Dir can't be written. Exiting..."; exit; fi
fi

# Now use the directory of uncompressed DICOMs as the input directory.
#indir=$uncompressed_dicom_dir
diffusion_volume="$indir"/*.nii.gz
runDirectory=`basename $indir`
subjectDirectory=`dirname $indir`
subjectDirectoryName=`basename $subjectDirectory`
newOut=$outdir/$subjectDirectoryName/$runDirectory
mkdir -p $newOut
echo
echo "#####"
echo Motion Correction
echo "#####"
echo

/usr/pubsw/packages/fsl/current/bin/eddy_correct $diffusion_volume "$newOut"/diff_mc.nii.gz 0
cp $indir/*bval $newOut #outdir

echo
echo "#####"
echo Rotate B vector after eddy correction
echo "#####"
echo

/space/jazz/1/users/gwarner/Code/DTIProcessing/linux_openmp_64/1d_tool.py -infile "$indir"/*bvec -transpose -write "$newOut"/bvec_t
/space/jazz/1/users/gwarner/Code/DTIProcessing/fdt_rotate_bvecs.sh "$newOut"/bvec_t "$newOut"/bvec_rotate "$newOut"/diff_mc.ecclog
echo
echo "#####"
echo Skull Stripping
echo "#####"
echo

/usr/pubsw/packages/fsl/current/bin/bet "$newOut"/diff_mc.nii.gz "$newOut"/temp.nii.gz -m -f 0.315
mv $newOut/temp.nii.gz $newOut/diff_mc_st.nii.gz
mv "$newOut"/temp_mask.nii.gz "$newOut/mask.nii.gz"

echo
echo "#####"
echo DTI Reconstruction
echo "#####"
echo
# The assumption here is that we are running dtifit.

if [ $scheme = "dtifit" ]
then
    if [ $verbose -eq 1 ]
    then
        /usr/pubsw/packages/fsl/current/bin/dtifit -V --sse -k "$newOut"/diff_mc.nii.gz -o "$newOut"/fsl -m "$newOut"/mask.nii.gz -r "$newOut"/bvec_rotate -b "$newOut"/*.bval
    else
        /usr/pubsw/packages/fsl/current/bin/dtifit --sse -k "$newOut"/diff_mc.nii.gz -o "$newOut"/fsl -m "$newOut"/mask.nii.gz -r "$newOut"/bvec_rotate -b "$newOut"/*.bval
    fi


fi

rm -rf $uncompressed_dicom_dir
rm -rf $diffusion_staging_dir
