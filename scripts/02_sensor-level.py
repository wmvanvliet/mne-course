"""
Step 2: perform sensor-level analysis.

- Split by experimental condition
- Average across epochs to make evokeds
- Create a summary figure of the evoked responses
"""

import argparse

import matplotlib.pyplot as plt
import mne

from config import evokeds_window, fname

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-sub", required=True, type=int, help="The subject to process")
args = parser.parse_args()

subject = args.sub

# Compute the evoked response for each experimental condition.
epochs = mne.read_epochs(fname.epochs(subject=subject))

# For the evokeds, we focus on this time window.
epochs.crop(*evokeds_window)

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
            sphere="eeg",
            axes=ax,  # draw in these two matplotlib axes objects
        )
        ax[0].set_title(f"{hemi}-{region} (mags)")
        ax[1].set_title(f"{hemi}-{region} (grads)")
ax[1].legend()

# Save the figure in the HTML report.
with mne.open_report(fname.report(subject=subject)) as report:
    report.add_figure(fig, "evokeds", section="sensor-level", replace=True)
    report.save(fname.report_html(subject=subject), open_browser=False, overwrite=True)
