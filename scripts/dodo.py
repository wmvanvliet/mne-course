"""
Do-it script to execute the entire pipeline using the doit tool:
http://pydoit.org

All the filenames are defined in config.py
"""
# fmt: off
# ruff:disable[E501]

from config import conditions, fname, runs, subjects

# Configuration for the "doit" tool.
DOIT_CONFIG = dict(
    # While running scripts, output everything the script is printing to the
    # screen.
    verbosity=2,
    # When the user executes "doit list", list the tasks in the order they are
    # defined in this file, instead of alphabetically.
    sort="definition",
)

def task_check():
    """Step 00: Check the system for python dependencies and the presence of data."""
    return dict(
        file_dep=["check_system.py"],
        targets=[fname.system_check],
        actions=["python check_system.py"],
    )


def task_preprocessing():
    """Step 01: Run preprocessing."""
    for sub in subjects:
        yield dict(
            # Give the sub-task a name.
            name=f"sub-{sub:02d}",
            file_dep=(
                [fname.raw(subject=sub, run=run) for run in runs] +
                [fname.calibration, fname.cross_talk, "02_preprocessing.py"]
            ),
            targets=(
                [fname.ica(subject=sub, run=run) for run in runs] +
                [fname.epochs(subject=sub)]
            ),
            actions=[
                f"python 01_preprocessing.py -sub={sub}"
            ],
        )

def task_sensor_level():
    """Step 02: Run sensor-level analysis."""
    for sub in subjects:
        yield dict(
            # Give the sub-task a name.
            name=f"sub-{sub:02d}",
            file_dep=[
                fname.epochs(subject=sub),
                "02_sensor-level.py",
            ],
            targets=[
                fname.evokeds(subject=sub),
            ],
            actions=[
                f"python 02_sensor-level.py -sub={sub}"
            ],
        )

def task_time_freq():
    """Step 03: Run time-frequency analysis."""
    for sub in subjects:
        yield dict(
            # Give the sub-task a name.
            name=f"sub-{sub:02d}",
            file_dep=[
                fname.epochs(subject=sub),
                "03_time_freq.py",
            ],
            targets=[
                fname.power(subject=sub),
                fname.itc(subject=sub),
            ],
            actions=[
                f"python 03_time_freq.py -sub={sub}"
            ],
        )

def task_forward():
    """Step 04: Create the forward head model."""
    for sub in subjects:
        yield dict(
            # Give the sub-task a name.
            name=f"sub-{sub:02d}",
            file_dep=[
                fname.surface(subject=sub, surface="inner_skull"),
                fname.surface(subject=sub, surface="outer_skull"),
                fname.surface(subject=sub, surface="outer_skin"),
                fname.surface(subject=sub, surface="white"),
                fname.epochs(subject=sub, run=1),
                "04_forward.py",
            ],
            targets=[
                fname.fwd(subject=sub),
            ],
            actions=[
                f"python 04_forward.py -sub={sub}"
            ],
        )

def task_source():
    """Step 05: Source estimation."""
    for sub in subjects:
        yield dict(
            # Give the sub-task a name.
            name=f"sub-{sub:02d}",
            file_dep=[
                fname.epochs(subject=sub),
                fname.evokeds(subject=sub),
                fname.fwd(subject=sub),
                "05_source.py",
            ],
            targets=(
                [fname.stc_hemi(subject=sub, condition=cond, hemi=hemi) for cond in conditions for hemi in ["lh", "rh"]] +
                [fname.stc_morph_hemi(subject=sub, condition=cond, hemi=hemi) for cond in conditions for hemi in ["lh", "rh"]]
            ),
            actions=[
                f"python 05_source.py -sub={sub}"
            ],
        )

def task_group_level():
    """Step 06: Group-level analysis."""
    return dict(
        file_dep=(
            [fname.stc_morph_hemi(subject=sub, condition=cond, hemi=hemi) for sub in subjects for cond in conditions for hemi in ["lh", "rh"]] +
            [fname.evokeds(subject=sub) for sub in subjects] +
            ["06_group_level.py"]
        ),
        targets=(
            [fname.ga_stc_hemi(condition=cond, hemi=hemi) for cond in conditions for hemi in ["lh", "rh"]] +
            [fname.ga_evokeds]
        ),
        actions=[
            "python 06_group_level.py"
        ],
    )
