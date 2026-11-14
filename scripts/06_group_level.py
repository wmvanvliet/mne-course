"""
Step 6: Group-level analysis.

- Sensor-level grand average evokeds
- Source-level: grand average source estimates
- Spatio-temporal cluster permutation testing
"""

import mne

from config import conditions, fname, subjects

# Average all the sensor-level evokeds.
ga_evokeds = list()
for cond in conditions:
    ga_evoked = mne.grand_average(
        [
            mne.read_evokeds(fname.evokeds(subject=sub), condition=cond)
            for sub in subjects
        ]
    )
    ga_evoked.comment = cond
    ga_evokeds.append(ga_evoked)
mne.write_evokeds(fname.ga_evokeds, ga_evokeds, overwrite=True)

# Average all the source estimates.
stcs = dict()
n_ave = dict()
for subject in subjects:
    for cond in conditions:
        stc = mne.read_source_estimate(fname.stc_morph(subject=subject, condition=cond))
        if cond not in stcs:
            stcs[cond] = stc
            n_ave[cond] = 1
        else:
            stcs[cond] += stc
            n_ave[cond] += 1
for cond in conditions:
    stcs[cond] /= n_ave[cond]

# Save the grans-average source estimates.
for cond in conditions:
    stcs[cond].save(fname.ga_stc(condition=cond), overwrite=True)

    # Write STC figures to the HTML report.
    with mne.open_report(fname.ga_report) as report:
        report.add_stc(
            stcs[cond],
            title=cond,
            section="source-level",
            subject="fsaverage",
            subjects_dir=fname.subjects_dir,
            replace=True,
        )
        report.save(
            fname.ga_report_html, open_browser=False, overwrite=True
        )
