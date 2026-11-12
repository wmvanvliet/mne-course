"""
Step 4: create the forward model.

- Compute the BEM model
- Setup the source space
- Perform co-registration
- Compute the forward model
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

# Plot the BEM surfaces.
fig_bem = mne.viz.plot_bem(subject=subject_fs, subjects_dir=fname.subjects_dir)

# Create the BEM solution.

# conductivity = (0.3,)  # for single layer
conductivity = (0.3, 0.006, 0.3)  # for three layers
model = mne.make_bem_model(
    ico=4,
    conductivity=conductivity,
    subject=subject_fs,
    subjects_dir=fname.subjects_dir,
)
bem_sol = mne.make_bem_solution(model)
mne.write_bem_solution(fname.bem(subject=subject), bem_sol, overwrite=True)

# Setup the source space.
src = mne.setup_source_space(
    subject=subject_fs,
    spacing=config.spacing,
    subjects_dir=fname.subjects_dir,
    n_jobs=-1,
)
src.save(fname.src(subject=subject), overwrite=True)

# # Manual co-registration.
# coreg = mne.gui.coregistration(
#     subject=subject_fs,
#     subjects_dir=fname.subjects_dir,
#     inst=f"fname.raw(subject=subject, run=3),
# )
# trans = coreg.coreg.trans
# trans.save(fname.trans(subject=subject), overwrite=True)

# Read a previously performed manual co-registration.
trans = mne.read_trans(fname.trans(subject=subject))

# Compute the forward model.
fwd = mne.make_forward_solution(
    fname.epochs(subject=subject),
    trans=trans,
    src=src,
    bem=bem_sol,
    meg=True,  # include MEG channels
    eeg=True,  # exclude EEG channels
    mindist=5.0,  # ignore sources <= 5mm from inner skull
    n_jobs=-1,  # number of jobs to run in parallel
)
fwd.save(fname.fwd(subject=subject), overwrite=True)

# Visualize the entire head model.
fig_head = mne.viz.plot_alignment(
    info=fwd["info"],
    trans=trans,
    fwd=fwd,
    surfaces=["white", "head"],
    subject=subject_fs,
    subjects_dir=fname.subjects_dir,
)

# Save the figures in the HTML report.
with mne.open_report(fname.report(subject=subject)) as report:
    report.add_figure(fig_bem, "BEM", section="head model")
    report.add_figure(fig_head, "Head model", section="head model")
    report.save(fname.report_html(subject=subject), open_browser=False, overwrite=True)
