Material for the MNE-Python course
==================================

Contents
--------
.. toctree::
   :maxdepth: 1

   Preprocessing <1-preprocessing>
   Sensor-level analysis: ERP/ERF <2-sensor-level>
   Sensor-level analysis: Time-frequency <3-time-frequency>
   Forward modelling <4-forward-modelling>
   Source estimation <5-source-level>
   Group-level analysis <6-group-level>
   Multivariate analysis <7-multivariate>
   Analyis pipeline design <8-pipeline-design>



About the lesson materials
--------------------------
The HTML version of the lesson materials are hosted at: https://users.aalto.fi/~vanvlm1/mne-course.
The git repository can be found at: https://github.com/wmvanvliet/mne-course.

:download:`Download the lesson materials <https://github.com/wmvanvliet/mne-course/archive/refs/heads/main.zip>`.

Authors of the material:

- Natalie Schaworonkow, ESI Frankfurt
- Simon Kern, ZI Mannheim
- Marijn van Vliet, Aalto University, Department of Neuroscience and Biomedical Engineering
- Britta Westner, Radboud University Nijmegen, Donders Institute
- Alexandre Gramfort, Inria, CEA Neurospin
- Denis A. Engemann, Inria, CEA Neurospin


Required software
-----------------
To follow along with the course, you will need a Python installation with MNE-Python and its dependencies.
See `MNE-Python's installation page <https://mne.tools/stable/install/index.html>`__ on information how to do this.

In addition, you will need a good Python development environment, such as `Spyder <https://www.spyder-ide.org>`__ or `Visual Studio Code <https://code.visualstudio.com/>`__.
Make sure to run Python in interactive mode.
In Spyder, this is the default mode.
In Visual Studio Code, install both the Python and Jupyter extensions and use the command palette (``CTRL+P``) to execute the command ``Jupyter: Create Interactive Window``.

You can test your interactive Python setup by executing the following code::

    import mne
    mne.sys_info()
    data_path = "./data"  # set this to where you've extracted the data package
    mne.viz.Brain("fsaverage", subjects_dir=f"{data_path}/freesurfer")

You should have an interactive brain figure in a separate window, while the interactive Python console remains responsive to new commands.

Download and extract the data package
-------------------------------------
To follow along with the analysis, you will need the following data package (1.6GB):
:download:`download <https://drive.google.com/file/d/1UyLeX6VLKrCf02TzkWEbTa8kuwo5evgP/view?usp=sharing>`

Unzip it somewhere you have plenty of disk space and note the location.
The lesson materials assume it is unzipped in the ``mne-course`` folder alongside the lesson materials, however this is not a requirement.


Executing the full example analysis pipeline
--------------------------------------------
You can find a full example analysis pipeline in the ``scripts`` folder of the lesson materials.
To run it for yourself, will need the ``doit`` and ``filename_templates`` packages, which can be installed through PIP: ``pip install doit filename_templates``.
You will also need to download the entire Wakeman and Henson (2025) dataset (version 2): https://openneuro.org/datasets/ds000117/.
A convenient way to download datasets from openneuro is with the help of the `openneuro-py <https://github.com/openneuro-py/openneuro-py>`_ package.
In addition, you need the FreeSurfer derivatives for that dataset (4.3GB): :download:`download <https://drive.google.com/file/d/1de-D9gppug1LJl-oa8o-Ncg1gscEx3fV/view?usp=sharing>`.
Extract it inside the ``ds000117`` folder.

If all this is installed, edit the ``scripts/config.py`` file and add your system configuration to the top of that file, indicating where the data is located on your system and how many CPU cores are available.
Then, you can run the analysis pipeline in its entirety by executing on the command line::

    cd mne-course/scripts
    doit


Where to go from here? 
-----------------------
After you have completed the contents of this lesson, you will know the basics of MNE-Python, but there is a lot more to learn.

In the `Documentation of MNE-Python <https://mne.tools>`__, there are tutorials that go in-depth on certain topics and quick examples that show you how to do specific things.

While these lesson materials focus on how to technically make MNE-Python do certain computations, it is important to know what those computations are, what purpose they serve, and how to interpret the results.
For this, we recommend taking a proper university-level neuroimaging course, such as:
Aalto University: `NBE-E4045 Functional Brain Imaging D (5 cr) <https://sisu.aalto.fi/student/courseunit/otm-ef8f2dea-edd6-4651-8702-f61dedaa9c2c/brochure>`__. 

To get started with your own data analysis pipelines, it is helpful to have an example pipeline to copy from.
`This git repository <https://github.com/wmvanvliet/mne-example-pipeline>`__ contains such an example pipeline, in three flavors: minimal, advanced, and expert.
Each flavor adds more bells and whistles to the pipeline to make it more complete and robust.


References and credit
~~~~~~~~~~~~~~~~~~~~~
The code from this tutorial is heavily inspired from this article:

Mainak Jas, Eric Larson, Denis Engemann, Jaakko Leppakangas, Samu Taulu, Matti Hämäläinen,
and Alexandre Gramfort. 2018. A Reproducible MEG/EEG Group Study With the MNE Software:
Recommendations, Quality Assessments, and Good Practices.
Frontiers in Neuroscience. 12, doi: `10.3389/fnins.2018.00530 <https://doi.org/10.3389/fnins.2018.00530>`__

The MNE software when used in publications should be acknowledged using citations.

To cite MNE-C or the inverse imaging implementations provided by the MNE software, please use:

A. Gramfort, M. Luessi, E. Larson, D. Engemann, D. Strohmeier, C. Brodbeck, L. Parkkonen,
M. Hämäläinen, MNE software for processing MEG and EEG data, NeuroImage, Volume 86,
1 February 2014, Pages 446-460, ISSN 1053-8119. doi: `10.1016/j.neuroimage.2013.10.027 <https://doi.org/10.1016/j.neuroimage.2013.10.027>`__

To cite the MNE-Python package, please use:

A. Gramfort, M. Luessi, E. Larson, D. Engemann, D. Strohmeier, C. Brodbeck, R. Goj, M. Jas,
T. Brooks, L. Parkkonen, M. Hämäläinen, MEG and EEG data analysis with MNE-Python,
Frontiers in Neuroscience, Volume 7, 2013, ISSN 1662-453X. doi: `10.3389/fnins.2013.00267 <https://doi.org/10.3389/fnins.2013.00267>`__

The example analysis pipeline is inspired from this article:

van Vliet, M. (2020). Seven quick tips for data analysis pipelines in neuroimaging. PLOS Computational Biology, 16(3), e1007358. doi: `0.1371/journal.pcbi.1007358 <https://doi.org/10.1371/journal.pcbi.1007358>`__
