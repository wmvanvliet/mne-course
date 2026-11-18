"""
Step 5: perform source estimation

- Estimate the noise covariance matrix
- Create an inverse operator
- Perform source estimation of the evoked responses for each condition
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
subject_fs = f"sub-{subject:02d}"

# Compute the noise covariance matrix.
epochs = mne.read_epochs(fname.epochs(subject=subject))
noise_cov = mne.compute_covariance(
    epochs,
    tmin=-0.2,  # use the baseline
    tmax=0.0,
    rank="info",
)
noise_cov.save(fname.noise_cov(subject=subject), overwrite=True)

# Plot some information about the noise covariance matrix.
with mne.open_report(fname.report(subject=subject)) as report:
    report.add_covariance(
        noise_cov, info=epochs.info, title="Noise co-variance", replace=True
    )
    report.save(fname.report_html(subject=subject), open_browser=False, overwrite=True)

# Free up some memory.
del epochs

# Load the evokeds.
evokeds = mne.read_evokeds(fname.evokeds(subject=subject))
evokeds = [ev.crop(*config.stc_window) for ev in evokeds]

# Compute the inverse operator.
fwd = mne.read_forward_solution(fname.fwd(subject=subject))
info = evokeds[0].info
inv = mne.minimum_norm.make_inverse_operator(info, fwd, noise_cov, loose=0.2, depth=0.8)

# Prepare morphing to fsaverage template brain.
morph = mne.compute_source_morph(
    inv["src"],
    subject_from=subject_fs,
    subject_to="fsaverage",
    subjects_dir=fname.subjects_dir,
    spacing=4,
)

# Perform source estimation.
for ev in evokeds:
    condition = ev.comment
    ev.set_eeg_reference("average", projection=True)  # needed for EEG source estimation
    ev.info["bads"] = ["EEG002"]
    stc = mne.minimum_norm.apply_inverse(ev, inv, lambda2=1 / 9, method="dSPM")
    stc.save(fname.stc(subject=subject, condition=condition), overwrite=True)

    # Morph to fsaverage template brain.
    stc_morph = morph.apply(stc)
    stc_morph.save(
        fname.stc_morph(subject=subject, condition=condition), overwrite=True
    )

    # Write STC figures to the HTML report.
    with mne.open_report(fname.report(subject=subject)) as report:
        report.add_stc(
            stc_morph,
            title=condition,
            section="source-level",
            subject="fsaverage",
            subjects_dir=fname.subjects_dir,
            replace=True,
        )
        report.save(
            fname.report_html(subject=subject), open_browser=False, overwrite=True
        )
