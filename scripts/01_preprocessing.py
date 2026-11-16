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
args = parser.parse_args()

subject = args.sub

epochs_per_run = list()
fig_eog_scores_per_run = list()
fig_ecg_scores_per_run = list()

for run in config.runs:
    print(f"Processing subject {subject}, run {run}...")

    # Load the raw data.
    raw = mne.io.read_raw(fname.raw(subject=subject, run=run), preload=True)

    # Set channel types.
    raw.set_channel_types({"EEG064": "misc"})  # EEG064 free-floating electrode

    # Mark "bad" channels
    raw.info["bads"] = config.bad_channels.get(subject, list())

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

    # Apply maxfilter. For this dataset, we need to estimate the head origin from the
    # digitized EEG electrodes. Normally, you can leave the `origin` parameter to its
    # default setting.
    _, origin, _ = mne.bem.fit_sphere_to_headshape(raw.info, dig_kinds="eeg")
    raw = mne.preprocessing.maxwell_filter(
        raw,
        calibration=fname.calibration,
        cross_talk=fname.cross_talk,
        st_duration=None,  # set to 60 to enable tSSS
        destination=fname.raw(subject=subject, run=3),
        origin=origin,
    )

    # Apply bandpass filter.
    raw.filter(*config.bandpass, n_jobs=config.n_jobs)

    # These recordings have a weird 26Hz signal in them.
    if subject in [2]:
        raw.notch_filter(26)

    # Resample the data to save memory and speed things along.
    raw.resample(config.resample)

    # Set the EEG reference.
    raw.set_eeg_reference(ref_channels="average", projection=False)

    # Fit an ICA model to the data.
    raw_highpass = raw.copy().filter(1, None)
    ica = mne.preprocessing.ICA(40, rng=68454).fit(raw_highpass)

    # Mark ICA components associated with EOG and ECG artifacts.
    bads_eog, eog_scores = ica.find_bads_eog(raw_highpass)
    bads_ecg, ecg_scores = ica.find_bads_ecg(raw_highpass)
    ica.exclude = bads_eog + bads_ecg
    fig_eog_scores_per_run.append(
        ica.plot_scores(eog_scores, bads_eog, title=f"EOG run-{run}", show=False)
    )
    fig_ecg_scores_per_run.append(
        ica.plot_scores(ecg_scores, bads_ecg, title=f"ECG run-{run}", show=False)
    )

    # Save the ICA model.
    ica.save(fname.ica(subject=subject, run=run), overwrite=True)

    # No longer need this.
    del raw_highpass

    # Find events.
    events = mne.find_events(
        raw, stim_channel="STI101", min_duration=2 / raw.info["sfreq"]
    )

    # Cut epochs.
    epochs = mne.Epochs(
        raw,
        events,
        config.event_id,
        *config.epochs_window,
        baseline=config.baseline,
        preload=True,
    )

    # Apply the ICA to the epochs to clean the artifacts.
    epochs_clean = ica.apply(epochs)
    epochs_clean.apply_baseline(config.baseline)  # after ICA, we need to re-do this

    # Collect the epochs for each run.
    epochs_per_run.append(epochs_clean)

# Concatenate the epochs across the runs.
epochs = mne.concatenate_epochs(epochs_per_run)

# One more pass to drop obviously bad epochs.
epochs.drop_bad(reject=dict(grad=4000e-13, mag=4e-12, eeg=150e-6))

# Account for projector delay.
epochs.shift_time(0.034)

# Save the epochs.
epochs.save(fname.epochs(subject=subject), overwrite=True)

# Add a basic plot of the sensor-level signals to the HTML report.
with mne.open_report(fname.report(subject=subject)) as report:
    report.add_figure(
        fig_eog_scores_per_run, title="EOG", section="preprocessing", replace=True
    )
    report.add_figure(
        fig_ecg_scores_per_run, title="ECG", section="preprocessing", replace=True
    )
    report.add_figure(
        epochs.plot_drop_log(show=False),
        title="Drop log",
        section="preprocessing",
        replace=True,
    )
    report.add_evokeds(epochs.average(), titles="after cleaning", replace=True)
    report.save(fname.report_html(subject=subject), open_browser=False, overwrite=True)
