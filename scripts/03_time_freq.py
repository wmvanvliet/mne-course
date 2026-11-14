"""
Step 3: perform time-frequency sensor-space analysis.

- Compute spectrum and TFR.
- Create a summary figure of the TFR.
"""

import argparse

import mne
import numpy as np

import config
from config import fname

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-sub", required=True, type=int, help="The subject to process")
args = parser.parse_args()

subject = args.sub

epochs = mne.read_epochs(fname.epochs(subject=subject))

# Compute the power spectrum.
epochs_psd = epochs.compute_psd(
    method="multitaper", fmin=2.0, fmax=40.0, bandwidth=2.0, n_jobs=-1
)
fig_psd = epochs_psd.plot(show=False)

# Compute time-frequency using Morlet wavelets.
power, itc = epochs.compute_tfr(
    method="morlet",
    freqs=np.logspace(*np.log10([5, 30]), num=20),  # frequencies of interest
    n_cycles=3,
    average=True,  # don't return a TFR for each epoch
    return_itc=True,  # also compute ITC
    decim=3,  # for additional speed
    n_jobs=config.n_jobs,  # use all CPU cores
)

# Crop to remove edge artifacts.
tmin, tmax = config.epochs_window
tmin += 0.55
tmax -= 0.4
power.crop(tmin, tmax)
itc.crop(tmin, tmax)

# Saving.
power.save(fname.power(subject=subject), overwrite=True)
itc.save(fname.itc(subject=subject), overwrite=True)

# Create a summary figure of the TFR.
fig_power = power.plot_topo(
    baseline=[tmin, -0.1],
    mode="meanlogratio",
    title="Average power",
    show=False,
)
fig_power.set_size_inches(20, 15)

# Create a summary figure of the ITC.
fig_itc = itc.plot_topo(
    baseline=[tmin, -0.1],
    mode="meanlogratio",
    title="Inter-trial coherence",
    show=False,
)
fig_itc.set_size_inches(20, 15)

# Save the figures in the HTML report.
with mne.open_report(fname.report(subject=subject)) as report:
    report.add_figure(fig_psd, "psd", section="sensor-level", replace=True)
    report.add_figure(fig_power, "power", section="sensor-level", replace=True)
    report.add_figure(fig_itc, "", section="sensor-level", replace=True)
    report.save(fname.report_html(subject=subject), open_browser=False, overwrite=True)
