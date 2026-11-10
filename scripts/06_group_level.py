"""
Step 6: Group-level analysis.

- Sensor-level grand average evokeds
- Source-level: grand average source estimates
- Spatio-temporal cluster permutation testing
"""

import mne

# Data paths
processed_path = "../processed"
subjects_dir = "../data/freesurfer"
figure_path = "../figures"

# Figure out the experimental conditions.
evokeds = mne.read_evokeds(f"{processed_path}/sub-01/sub-01_list-ave.fif")
conditions = [ev.comment for ev in evokeds]

# Average all the source estimates.
stcs = dict()
n_ave = dict()
for subject in [1]:
    for cond in conditions:
        stc = mne.read_source_estimate(
            f"{processed_path}/sub-{subject:02d}/sub-{subject:02d}_{cond}_fsaverage"
        )
        if cond not in stcs:
            stcs[cond] = stc
            n_ave[cond] = 1
        else:
            stcs[cond] += stc
            n_ave[cond] += 1
for cond in conditions:
    stcs[cond] /= n_ave[cond]
