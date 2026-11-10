"""
Step 4: create the forward model.

- Compute the BEM model
- Setup the source space
- Perform co-registration
- Compute the forward model
"""

import mne
import numpy as np

# Data paths
data_path = "../data"
processed_path = "../processed"
subjects_dir = "../data/freesurfer"
figure_path = "../figures"

# Plot the BEM surfaces.
fig = mne.viz.plot_bem(subject="sub-01", subjects_dir=subjects_dir)
fig.savefig(f"{figure_path}/sub-01/bem_surfaces.pdf")

# Create the BEM solution.

# conductivity = (0.3,)  # for single layer
conductivity = (0.3, 0.006, 0.3)  # for three layers
model = mne.make_bem_model(
    ico=4, conductivity=conductivity, subject="sub-01", subjects_dir=subjects_dir
)
bem_sol = mne.make_bem_solution(model)
mne.write_bem_solution(
    f"{processed_path}/sub-01/sub-01-bem-sol.fif", bem_sol, overwrite=True
)

# Setup the source space.
src = mne.setup_source_space(
    subject="sub-01", spacing="oct6", subjects_dir=subjects_dir, n_jobs=-1
)
src.save(f"{processed_path}/sub-01/sub-01_src.fif", overwrite=True)

# # Manual co-registration.
# coreg = mne.gui.coregistration(
#     subject="sub-01",
#     subjects_dir=subjects_dir,
#     inst=f"{data_path}/sub-01/sub-01_ses-meg_task-facerecognition_run-01_meg.fif",
# )
# trans = coreg.coreg.trans
# trans.save(f"{processed_path}/sub-01/sub-01_trans.fif", overwrite=True)

# Read a previously performed manual co-registration.
trans = mne.read_trans(f"{processed_path}/sub-01/sub-01_trans.fif")

# Compute the forward model.
fwd = mne.make_forward_solution(
    f"{data_path}/sub-01/sub-01_ses-meg_task-facerecognition_run-01_meg.fif",
    trans=trans,
    src=src,
    bem=bem_sol,
    meg=True,  # include MEG channels
    eeg=True,  # exclude EEG channels
    mindist=5.0,  # ignore sources <= 5mm from inner skull
    n_jobs=-1,  # number of jobs to run in parallel
)
fwd.save(f"{processed_path}/sub-01/sub-01_fwd.fif", overwrite=True)

# Visualize the entire head model.
fig = mne.viz.plot_alignment(
    info=fwd["info"],
    trans=trans,
    fwd=fwd,
    surfaces=["white", "head"],
    subject="sub-01",
    subjects_dir=subjects_dir,
)
fig.plotter.save_graphic(f"{figure_path}/sub-01/sub-01_head_model.pdf")
