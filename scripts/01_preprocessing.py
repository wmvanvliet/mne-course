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
from config import bad_channels, fname, runs
from move_head import move_head

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-sub", required=True, type=int, help="The subject to process")
args = parser.parse_args()

subject = args.sub

epochs_per_run = list()

for run in runs:
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
    raw.info["bads"] = bad_channels.get(subject, list())

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

    # Apply maxfilter.
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

    # Collect the epochs for each run.
    epochs_per_run.append(epochs_clean)

# When concatenating epochs across runs, the head position inside the helmet must be the
# same. We will virtually move the head position of all runs to the position of the head
# during run 3.
for epochs in epochs_per_run:
    move_head(epochs, epochs_per_run[2])

# Save the epochs.
epochs.save(fname.epochs(subject=subject), overwrite=True)
