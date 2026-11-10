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

import os

import mne

# Data paths
data_path = "../data"
processed_path = "../processed"

# Make sure the subdir for the subject exists.
os.makedirs(f"{processed_path}/sub-01", exist_ok=True)

for run in [1, 2, 3, 4, 5, 6]:
    print(f"Processing run {run}...")

    # Load the raw data.
    raw_fname = (
        f"{data_path}/sub-01/sub-01_ses-meg_task-facerecognition_run-0{run}_meg.fif"
    )
    raw = mne.io.read_raw(raw_fname, preload=True)

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
    raw.info["bads"] = ["EEG064"]

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
        calibration=f"{data_path}/meg_calibration/sss_cal.dat",
        cross_talk=f"{data_path}/meg_calibration/ct_sparse.fif",
        st_duration=60,
        destination=f"{data_path}/sub-01/sub-01_ses-meg_task-facerecognition_run-03_meg.fif",
    )

    # Apply bandpass filter.
    raw.filter(0.05, 40)

    # Resample the data to save memory and speed things along.
    raw.resample(300)

    # Fit an ICA model to the data.
    raw_highpass = raw.copy().filter(1, None)
    ica = mne.preprocessing.ICA(0.95, random_state=68454).fit(raw_highpass)

    # Mark ICA components associated with EOG and ECG artifacts.
    bads_eog, eog_scores = ica.find_bads_eog(raw_highpass)
    bads_ecg, ecg_scores = ica.find_bads_ecg(raw_highpass)
    ica.exclude = bads_eog + bads_ecg

    # Save the ICA model.
    ica.save(f"{processed_path}/sub-01/sub-01_run-0{run}_ica.fif", overwrite=True)

    # No longer need this.
    del raw_highpass

    # Find events.
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
    events = mne.find_events(raw, stim_channel="STI101")

    # Cut epochs.
    tmin = -0.5  # start of each epoch (500ms before the trigger)
    tmax = 2.0  # end of each epoch (2000ms after the trigger)
    baseline = (-0.2, 0)  # means from 200ms before to stim onset (t = 0)

    epochs = mne.Epochs(
        raw, events, event_id, tmin, tmax, baseline=baseline, preload=True
    )

    # Account for projector delay.
    epochs.shift_time(0.034)

    # Apply the ICA to the epochs to clean the artifacts.
    epochs_clean = ica.apply(epochs)
    epochs_clean.apply_baseline()  # after ICA, we need to re-do this

    # Save the clean epochs.
    epochs_clean.save(
        f"{processed_path}/sub-01/sub-01_run-0{run}_epo.fif", overwrite=True
    )
