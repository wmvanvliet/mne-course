"""
Do-it script to execute the entire pipeline using the doit tool:
http://pydoit.org

All the filenames are defined in config.py
"""
# fmt: off
# ruff:disable[E501]

import config
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
        for run in runs:
            yield dict(
                # Give the sub-task a name.
                name=f"sub-{sub:02d}:run-{run:02d}",
                file_dep=[
                    fname.raw(subject=sub, run=run),
                    fname.calibration,
                    fname.cross_talk,
                    "01_preprocessing.py",
                ],
                targets=[
                    fname.ica(subject=sub, run=run),
                    fname.epochs(subject=sub, run=run),
                ],
                actions=[
                    f"python 01_preprocessing.py -sub={sub} -run={run}"
                ],
            )
