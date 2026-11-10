"""
Step 2: perform sensor-level analysis.

- Split by experimental condition
- Average across epochs to make evokeds
- Create a summary figure of the evoked responses
"""

import os

import matplotlib.pyplot as plt
import mne

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

# Compute the evoked response for each experimental condition.
evokeds = list()
for condition in ["face", "scrambled", "famous", "unfamiliar"]:
    ev = epochs[condition].average()
    ev.comment = condition
    evokeds.append(ev)

# Save the evokeds.
mne.write_evokeds(f"{processed_path}/sub-01/sub-01_ave.fif", evokeds, overwrite=True)

# Create a 3x4 grid of panels, which matplotlib calls "axes".
fig, axes = plt.subplots(
    nrows=3, ncols=4, sharex=True, figsize=(14, 10), layout="constrained"
)

# Fill the panels with evoked plots.
for row, region in enumerate(["frontal", "temporal", "occipital"]):
    for column, hemi in enumerate(["Left", "Right"]):
        ax = axes[row][[column, column + 2]]
        channel_group = mne.channels.read_vectorview_selection(
            f"{hemi}-{region}", info=epochs.info
        )
        mne.viz.plot_compare_evokeds(
            evokeds,
            picks=channel_group,
            legend=False,
            show=False,
            axes=ax,  # draw in these two matplotlib axes objects
        )
        ax[0].set_title(f"{hemi}-{region} (mags)")
        ax[1].set_title(f"{hemi}-{region} (grads)")
ax[1].legend()

# Save the figure.
os.makedirs(f"{figure_path}/sub-01", exist_ok=True)
fig.savefig("../figures/sub-01/evokeds.pdf")
