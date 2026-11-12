"""
Step 1: Load the raw data and perform preprocessing.

- Set the channel types and references
- Maxfilter
- Resampling
- Apply bandpass filtering
- Fit ICA and detect EOG and ECG components
- Cut epochs
- Apply ICA to clean the epochs
"""

import argparse

import mne

import config
from config import fname

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-sub", required=True, type=int, help="The subject to process")
parser.add_argument("-run", required=True, type=int, help="The run to process")
args = parser.parse_args()

subject = args.sub
run = args.run

# Use the manually pre-selected bad channels in the config file.
# Alternatively, we can use automatic detection of bad channels.
current_bads = config.bad_channels.query(
    f"subject=={subject} and run=={run}"
).channels.tolist()

print(f"Processing subject {subject}, run {run}...")

# Load the raw data.
raw = mne.io.read_raw(fname.raw(subject=subject, run=run), preload=True)

# Set channel types.
raw.set_channel_types(
    {
        "EEG061": "eog",  # actually EOG not EEG
        "EEG062": "eog",  # actually EOG not EEG
        "EEG063": "ecg",  # actually ECG not EEG
        "EEG064": "misc",
    }
)  # EEG064 free-floating electrode

# We also rename the EOG and ECG channels.
raw.rename_channels({"EEG061": "EOG061", "EEG062": "EOG062", "EEG063": "ECG063"})

# Mark "bad" channels
raw.info["bads"] = current_bads

# Set the EEG reference.
raw.set_eeg_reference(ref_channels="average", projection=False)

# Drop some superfluous channels.
raw.drop_channels(
    [
        "STI201",
        "STI301",
        "MISC201",
        "MISC202",
        "MISC203",
        "MISC204",
        "MISC205",
        "MISC206",
        "MISC301",
        "MISC302",
        "MISC303",
        "MISC304",
        "MISC305",
        "MISC306",
    ]
)

# Apply maxfilter
raw = mne.preprocessing.maxwell_filter(
    raw,
    calibration=fname.calibration,
    cross_talk=fname.cross_talk,
    st_duration=60,
    destination=fname.raw(run=3),
)

# Apply bandpass filter.
raw.filter(*config.bandpass)

# Resample the data to save memory and speed things along.
raw.resample(config.resample)

# Fit an ICA model to the data.
raw_highpass = raw.copy().filter(1, None)
ica = mne.preprocessing.ICA(0.95, random_state=68454).fit(raw_highpass)

# Mark ICA components associated with EOG and ECG artifacts.
bads_eog, eog_scores = ica.find_bads_eog(raw_highpass)
bads_ecg, ecg_scores = ica.find_bads_ecg(raw_highpass)
ica.exclude = bads_eog + bads_ecg

# Save the ICA model.
ica.save(fname.ica(subject=subject, run=run), overwrite=True)

# No longer need this.
del raw_highpass

# Find events.
events = mne.find_events(raw, stim_channel="STI101")

# Cut epochs.
epochs = mne.Epochs(
    raw,
    events,
    config.event_id,
    *config.epochs_window,
    baseline=config.baseline,
    preload=True,
)

# Account for projector delay.
epochs.shift_time(0.034)

# Apply the ICA to the epochs to clean the artifacts.
epochs_clean = ica.apply(epochs)
epochs_clean.apply_baseline()  # after ICA, we need to re-do this

# Save the clean epochs.
epochs_clean.save(fname.epochs(subject=subject, run=run), overwrite=True)
