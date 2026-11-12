"""
Step 2: perform sensor-level analysis.

- Split by experimental condition
- Average across epochs to make evokeds
- Create a summary figure of the evoked responses
"""

import argparse

import matplotlib.pyplot as plt
import mne

from config import fname

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-sub", required=True, type=int, help="The subject to process")
args = parser.parse_args()

subject = args.sub

# Load the epochs for all the runs.
all_epochs = list()
for run in [1, 2, 3, 4, 5, 6]:
    # Load the epochs
    epochs = mne.read_epochs(fname.epochs(subject=subject, run=run))
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
mne.write_evokeds(fname.evokeds(subject=subject), evokeds, overwrite=True)

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

# Save the figure in the HTML report.
with mne.open_report(fname.report(subject=subject)) as report:
    report.add_figure(fig, "evokeds", section="sensor-level")
    report.save(fname.report_html(subject=subject), open_browser=False, overwrite=True)
