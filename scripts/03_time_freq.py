"""
Step 3: perform time-frequency sensor-space analysis.

- Compute spectrum and TFR.
- Create a summary figure of the TFR.
"""

import mne
import numpy as np

# Data paths
processed_path = "../processed"
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

# Compute the power spectrum.
# epochs_psd = epochs.compute_psd(
#     method="multitaper", fmin=2.0, fmax=40.0, bandwidth=2.0, n_jobs=-1
# )
# fig = epochs_psd.plot()
# fig.savefig(f"{figure_path}/sub-01/psd.pdf")

# Compute time-frequency using Morlet wavelets.
power, itc = epochs.compute_tfr(
    method="morlet",
    freqs=np.logspace(*np.log10([5, 30]), num=20),  # frequencies of interest
    n_cycles=3,
    average=True,  # don't return a TFR for each epoch
    return_itc=True,  # also compute ITC
    decim=3,  # for additional speed
    n_jobs=-1,  # use all CPU cores
)

# Crop to remove edge artifacts.
power.crop(-0.45, 1.6)
itc.crop(-0.45, 1.6)

# Create a summary figure of the TFR.
fig = power.plot_topo(
    baseline=[-0.45, -0.1],
    mode="meanlogratio",
    title="Average power",
)
fig.savefig(f"{figure_path}/sub-01/power.pdf")

# Create a summary figure of the ITC.
fig = power.plot_topo(
    baseline=[-0.45, -0.1],
    mode="meanlogratio",
    title="Average power",
)
fig.set_figsize_inches((20, 15))
fig.savefig(f"{figure_path}/sub-01/itc.pdf")
