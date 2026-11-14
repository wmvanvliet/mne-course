"""
===========
Config file
===========

Configuration parameters for the study.
"""

import getpass
import os
from socket import getfqdn

from filename_templates import FileNames

########################################################################################
# System setup. SET THIS TO MATCH YOUR OWN SYSTEM.
########################################################################################

user = getpass.getuser()  # Username of the user running the scripts
host = getfqdn()  # Hostname of the machine running the scripts

# You want to add your machine to this list.
# data_path - Folder containing the original ds000117 data.
# processed_path - Folder to write the processed MEG data to.
# reports_path - Folder to write the HTML reports to.
# n_jobs - number of CPU cores to use
if host == "deepthought1":
    # Marijn's workstation
    data_path = "../ds000117"
    processed_path = "../processed"
    reports_path = "../reports"
    n_jobs = 32
elif host == "marijn-laptop":
    # Marijn's Linux laptop:
    data_path = "/m/nbe/scratch/conpy/ds000117"
    processed_path = "../processed"
    reports_path = "../reports"
    n_jobs = 14
    os.environ["QT_QPA_PLATFORM"] = "xcb"  # needed for 3d graphics to work
elif "triton" in host:
    # Aalto's Triton HPC cluster
    data_path = "/m/nbe/scratch/conpy/ds000117"
    processed_path = "../processed"
    reports_path = "../reports"
    n_jobs = 1
else:
    raise ValueError(f"Please add your system to config.py ({user=} {host=}).")

# For numpy to use the right amount of cores
os.environ["OMP_NUM_THREADS"] = str(n_jobs)


########################################################################################
# Experiment design: subjects, session, runs, tasks, event codes, etc.
########################################################################################

# The subjects to include in the analysis pipeline. You can comment-out subjects to
# remove them from the analysis if there was some problem with the data.
subjects = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
]

# "Runs" are blocks of trials, run during the same session. For example, all the trials
# before the participant took a break could be a "run". "Tasks" are different
# experimental paradigms. We often have a different number of runs per task.
runs = [1, 2, 3, 4, 5, 6]

# Events and their trigger-codes.
# "description of the event": trigger-code
event_id = {
    "face/famous/first": 5,
    "face/famous/immediate": 6,
    "face/famous/long": 7,
    "face/unfamiliar/first": 13,
    "face/unfamiliar/immediate": 14,
    "face/unfamiliar/long": 15,
    "scrambled/first": 17,
    "scrambled/immediate": 18,
    "scrambled/long": 19,
}

# Names for the experimental conditions (don't use "/" in condition names) and the
# events to use for each condition.
conditions = ["face", "unfamiliar", "famous", "scrambled"]

# Manually defined bad channels.
# subject -> bad channels
bad_channels = {
    1: ["EEG064", "EEG002"],
}

########################################################################################
# Common parameters used in multiple analysis scripts.
########################################################################################

# Whether to perform maxfiltering on the data. This can help filter out noise, but also
# drops a lot of rank in the signal and makes it less suitable for beamforming.
use_maxfilter = False

# Bandpass filter to apply.
bandpass = (0.05, 40)

# Resample to this frequency.
resample = 300

# Various analysis windows. In seconds relative to stimulus onset.
epochs_window = (-1.0, 2.0)
baseline = (-0.2, 0)
evokeds_window = (-0.2, 1.0)

# Source "spacing" controlling the resolution of the source estimate.
# Common choices fow a "low" resolution are: "ico4" or "oct5"
# Common choices fow a "high" resolution are: "ico5" or "oct6"
spacing = "ico4"

########################################################################################
# Templates for filenames.
#
# These are all the filenames used in the analysis in one place. Try to be consistent
# and always define your filenames here, instead of in individual analysis scripts.
# See here for documentation on how these templates work:
# https://github.com/wmvanvliet/filename-templates#filename-templates
#
# In short:
#  - Placeholders, such as `{subject}`, become parameters for the filename function.
#  - Placeholders that already exist as a filename alias, such as `{data_path}`, are
#    filled automatically.
#  - Placeholders follow Python's string formatting syntax.
#    For example: `{subject:02d}` means a zero-padded number.
#    See: https://docs.python.org/3/library/string.html#format-examples
########################################################################################


fname = FileNames()
# fmt: off
# ruff: disable[E501]

# These are the folders specified at the top of this config file.
# `mkdir=True` means that the folder will be created if it doesn't exist yet.
fname.add("data_path", data_path)
fname.add("processed_path", processed_path, mkdir=True)
fname.add("reports_path", reports_path, mkdir=True)

# Original raw data.
fname.add("raw", "{data_path}/sub-{subject:02d}/ses-meg/meg/sub-{subject:02d}_ses-meg_task-facerecognition_run-{run:02d}_meg.fif")

# Scanner-specific calibration files. Same for each subject.
fname.add("calibration", "{data_path}/sub-01/ses-meg/meg/sub-01_ses-meg_acq-calibration_meg.dat")
fname.add("cross_talk", "{data_path}/sub-01/ses-meg/meg/sub-01_ses-meg_acq-crosstalk_meg.fif")

# Freesurfer files.
fname.add("subjects_dir", "{data_path}/derivatives/freesurfer")
fname.add("surface", "{subjects_dir}/sub-{subject:02d}/surf/{hemi}.{surface}")
fname.add("bem_surface", "{subjects_dir}/sub-{subject:02d}/bem/{surface}.surf")
fname.add("trans", "{subjects_dir}/sub-{subject:02d}/sub-{subject:02d}_trans.fif", mkdir=True)

# Files produced by our analysis.
fname.add("ica", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_run-{run:02d}_ica.fif", mkdir=True)
fname.add("epochs", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_epo.fif", mkdir=True)
fname.add("evokeds", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_list-ave.fif", mkdir=True)
fname.add("power", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_power.h5", mkdir=True)
fname.add("itc", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_itc.h5", mkdir=True)
fname.add("bem_sol", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_bem-sol.fif", mkdir=True)
fname.add("src", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_src.fif", mkdir=True)
fname.add("fwd", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_fwd.fif", mkdir=True)
fname.add("noise_cov", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_cov.fif", mkdir=True)
fname.add("inv", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_inv.fif", mkdir=True)
fname.add("stc", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_cond-{condition}", mkdir=True)
fname.add("stc_hemi", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_cond-{condition}-{hemi}.stc", mkdir=True)
fname.add("stc_morph", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_cond-{condition}_morphed", mkdir=True)
fname.add("stc_morph_hemi", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_cond-{condition}_morphed-{hemi}.stc", mkdir=True)
fname.add("ga_evokeds", "{processed_path}/grand_average/grand_average_list-ave.fif", mkdir=True)
fname.add("ga_stc", "{processed_path}/grand_average/grand_average_cond-{condition}", mkdir=True)
fname.add("ga_stc_hemi", "{processed_path}/grand_average/grand_average_cond-{condition}-{hemi}.stc", mkdir=True)

# HTML reports
fname.add("report", "{reports_path}/sub-{subject:02d}_report.h5", mkdir=True)
fname.add("report_html", "{reports_path}/sub-{subject:02d}_report.html", mkdir=True)
fname.add("ga_report", "{reports_path}/grand_average_report.h5", mkdir=True)
fname.add("ga_report_html", "{reports_path}/grand_average_report.html", mkdir=True)

# Misc.
fname.add("system_check", "./.system_check.txt")

# fmt: on
# ruff: enable[E501]

# Add `subjects_dir` as an environment variable for convenience. This way, you don't
# have to specify `subjects_dir=subjects_dir` all the time when using MNE-Python
# functions.
os.environ["SUBJECTS_DIR"] = str(fname.subjects_dir)
