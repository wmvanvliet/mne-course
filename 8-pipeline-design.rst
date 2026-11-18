Design of data analysis pipelines
---------------------------------

Authors: Marijn van Vliet

Ideally, analysis code should be a testament to the scientific rigor and technological creativity of the researcher, in much the same way as the scientific articles we write. 
In this lesson, we will go over some design principles and practical tips to structure our analysis code.

An example pipeline on the `Wakeman and Henson ds000117 dataset <https://openneuro.org/datasets/ds000117>`_ is part of the `repository containing these lesson materials <https://github.com/wmvanvliet/mne-course>`_ and can be downloaded :download:`here <https://github.com/wmvanvliet/mne-course/archive/refs/heads/main.zip>`.
The analysis pipeline itself resides in the ``scripts`` folder.


The pipeline is split into multiple files
=========================================

To keep things manageable, the Python code in this pipeline is spread out across 6 scripts, which are numbered to indicate in which order they should be run::

    01_preprocessing.py
    02_sensor-level.py
    03_time_freq.py
    04_forward.py
    05_source.py
    06_group_level.py

This makes it easier to focus on a single part of the analysis pipeline in isolation, either when working on it or on trying to decipher the programming code.

The decision where one script ends and a new one begins is often made on the basis of:

- **Theme:** when something feels like a different analysis step
- **Complexity:** when a script becomes too long and convoluted
- **Runtime:** when running a script takes too much time to be convenient


Start scripts with a comment explaining what it does
====================================================

Without spending too long on documenting your code, it is recommended to write a note to yourself and your readers about what the purpose of the script is::

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

Maintain a central configuration file across scripts 
====================================================

With the pipeline split-up into multiple scripts, it will be a common occurrence to have values that should be the same in multiple scripts.
For example, the list of experimental conditions, or the baseline period to use.
Instead of copy-pasting values across script, it is highly recommended to define them in a central file that is ``import``-ed across the script.
This way, when you ever change the value, you ensure that all scripts will use the updated one.

Another important role for the central file, and why it is called ``config.py``, is to provide a single place to define the information needed to run the analysis on a specific system.
For example, it can contain the location where the dataset has been downloaded, and where to write the processed files.
To make the code portable across systems, you can make the script query the hostname and username and set the configuration based on that::

    import getpass
    from socket import getfqdn

    user = getpass.getuser()  # Username of the user running the scripts
    host = getfqdn()  # Hostname of the machine running the scripts

    if host == "deepthought1":
        # Marijn's workstation
        data_path = "../ds000117"
        processed_path = "../ds000117/derivatives/example_pipeline"
        reports_path = "../reports"
        n_jobs = 32
    elif host == "marijn-laptop":
        # Marijn's Linux laptop:
        data_path = "/m/nbe/scratch/conpy/ds000117"
        processed_path = "../processed"
        reports_path = "../reports"
        n_jobs = 14
        os.environ["QT_QPA_PLATFORM"] = "xcb"  # needed for 3d graphics to work
    else:
        raise ValueError(f"Please add your system to config.py ({user=} {host=}).")


Manage filenames in a central location
======================================

There is a general mantra in computer programming: *"Don't repeat yourself"*.
This holds particularly true for file names.
As one script produces a file that is consumed by another script, it is vital that they agree on the exact filename.
Rather than copy-pasting filenames between scripts, keep them in a central file, for example the configuration file.
The example pipeline uses the `filename_templates <https://github.com/wmvanvliet/filename-templates>`_ module for this::

    fname = FileNames()
    fname.add("data_path", data_path)
    fname.add("processed_path", processed_path, mkdir=True)

    # Original raw data.
    fname.add("raw", "{data_path}/sub-{subject:02d}/ses-meg/meg/sub-{subject:02d}_ses-meg_task-facerecognition_run-{run:02d}_meg.fif")

    # Freesurfer files.
    fname.add("subjects_dir", "{data_path}/derivatives/freesurfer")
    fname.add("surface", "{subjects_dir}/sub-{subject:02d}/surf/{hemi}.{surface}")
    fname.add("bem_surface", "{subjects_dir}/sub-{subject:02d}/bem/{surface}.surf")
    fname.add("trans", "{subjects_dir}/sub-{subject:02d}/sub-{subject:02d}_trans.fif", mkdir=True)

    # Files produced by our analysis.
    fname.add("ica", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_run-{run:02d}_ica.fif", mkdir=True)
    fname.add("epochs", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_epo.fif", mkdir=True)
    fname.add("evokeds", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_list-ave.fif", mkdir=True)
    fname.add("power", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_power.h5", mkdir=True)
    fname.add("itc", "{processed_path}/sub-{subject:02d}/sub-{subject:02d}_itc.h5", mkdir=True)

Some notable features:

- We give filenames a short "handle" to refer to them, saving us typing out long file paths.
- We store filename templates with placeholder values to be filled-in when the filename is used, using the same formatting system as Python's `f-strings <https://docs.python.org/3/library/argparse.html>`_. Placeholders with the same name as filenames specified earlier are automatically filled-in (e.g. ``data_path`` and ``processed_path``).
- By specifying ``mkdir=True``, the system checks when a filename is accessed whether the parent folder exists, and creates it if it does not.

Each script operates on a single subject
========================================

All scripts (except ``06_group_level.py``) take the subject to process as a command-line parameter, using Python's build-in `argparse <https://docs.python.org/3/library/argparse.html>`_ module::

    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-sub", required=True, type=int, help="The subject to process")
    args = parser.parse_args()
    subject = args.sub

This is again to facilitate running only part of the pipeline.
As each recording has its own quirks and oddities, you will often find yourself working on the data for one specific subject.
Hence, no big ``for``-loop across subjects, except in script ``06_group_level.py`` which aggregates across the records of all subjects.


One command to run the entire analysis
======================================

With the analysis pipeline split-up into multiple scripts and each script only processing a single subject, we need a convenient way to run the entire thing.
This "master script" can be a shell script or Windows batch file that simply calls each script in order.
However, with a bit of investment in reading its documentation, you can make use of a build system like `doit <https://pydoit.org>`_ to make it more intelligent.
In such a system, you specify for each script which files it consumes and which files it produces.
Then, it can figure out which analysis steps need to be run and which can be safely skipped::

    def task_preprocessing():
        """Step 01: Run preprocessing."""
        # Define a sub-task for each subject.
        for sub in subjects:
            yield dict(
                # Give the sub-task a name.
                name=f"sub-{sub:02d}",
                file_dep=(
                    [fname.raw(subject=sub, run=run) for run in runs] +
                    [fname.calibration, fname.cross_talk, "01_preprocessing.py"]
                ),
                targets=(
                    [fname.ica(subject=sub, run=run) for run in runs] +
                    [fname.epochs(subject=sub)]
                ),
                actions=[
                    f"python 01_preprocessing.py -sub={sub}"
                ],
            )

With such a setup, one can list all the steps of the analysis pipeline on the command line::

    doit list

And run the entire thing with::

    doit

Credits
-------

This lesson was heavily inspired from this article:

van Vliet, M. (2020). Seven quick tips for data analysis pipelines in neuroimaging. PLOS Computational Biology, 16(3), e1007358. `doi: 0.1371/journal.pcbi.1007358 <https://doi.org/10.1371/journal.pcbi.1007358>`__
