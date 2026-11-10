"""
Step 5: perform source estimation

- Estimate the noise covariance matrix
- Create an inverse operator
- Perform source estimation of the evoked responses for each condition
"""

import mne

# Data paths
processed_path = "../processed"
subjects_dir = "../data/freesurfer"
figure_path = "../figures"

# Load the epochs for all the runs.
all_epochs = list()
for run in [1, 2, 3, 4, 5, 6]:
    # Load the epochs
    epochs_fname = f"{processed_path}/sub-01/sub-01_run-0{run}_epo.fif"
    epochs = mne.read_epochs(epochs_fname)
    all_epochs.append(epochs)
epochs = mne.concatenate_epochs(all_epochs)
del all_epochs

# Compute the noise covariance matrix.
noise_cov = mne.compute_covariance(
    epochs,
    tmin=-0.2,  # use the baseline
    tmax=0.0,
    rank="info",
)
noise_cov.save(f"{processed_path}/sub-01/sub-01_cov.fif", overwrite=True)

# Plot some information about the noise covariance matrix.
fig_cov, fig_rank = mne.viz.plot_cov(noise_cov, info=epochs.info)
fig_cov.savefig(f"{figure_path}/sub-01/sub-01_cov.pdf")
fig_rank.savefig(f"{figure_path}/sub-01/sub-01_cov_rank.pdf")

del epochs

# Load the evokeds.
evokeds = mne.read_evokeds(f"{processed_path}/sub-01/sub-01_ave.fif")

# Compute the inverse operator.
fwd = mne.read_forward_solution(f"{processed_path}/sub-01/sub-01_fwd.fif")
info = evokeds[0].info
inv = mne.minimum_norm.make_inverse_operator(info, fwd, noise_cov, loose=0.2, depth=0.8)

# Perform source estimation.
for ev in evokeds:
    condition = ev.comment
    ev.set_eeg_reference("average", projection=True)  # needed for EEG source estimation
    ev.info["bads"] = ["EEG002"]
    stc = mne.minimum_norm.apply_inverse(ev, inv, lambda2=1 / 9, method="dSPM")
    stc.save(f"{processed_path}/sub-01/sub-01_{condition}_stc", overwrite=True)
