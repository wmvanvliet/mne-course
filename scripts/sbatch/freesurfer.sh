#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=1
#SBATCH --job-name=freesurfer
#SBATCH --array=1-16
#SBATCH --output=out/bem_sub-%a.out

# The subject we are currently processing.
sub=`printf 'sub-%02d' $SLURM_ARRAY_TASK_ID`

# Load required software.
module load neuroimaging-env
module load triton/2024.1-gcc
module load freesurfer

# Run FreeSurfer to create the BEM surfaces.
recon-all -all -s $sub -sd /scratch/nbe/conpy/freesurfer -i /scratch/nbe/conpy/ds000117/${sub}/ses-mri/anat/${sub}_ses-mri_acq-mprage_T1w.nii.gz
mne watershed_bem -a -s $sub -d /scratch/nbe/conpy/freesurfer --overwrite
mne make_scalp_surfaces -s $sub -d /scratch/nbe/conpy/freesurfer --force --overwrite
