Material for the MNE-Python course
====================================

Authors of the material::

- Natalie Schaworonkow, ESI Frankfurt
- Simon Kern, ZI Mannheim
- Marijn van Vliet, Aalto University, Department of Neuroscience and Biomedical Engineering
- Britta Westner, Radboud University Nijmegen, Donders Institute
- Alexandre Gramfort, Inria, CEA Neurospin
- Denis A. Engemann, Inria, CEA Neurospin

Data package
------------
To follow along with the analysis, you will need the following data package (4.3GB):
`download link <https://drive.google.com/file/d/1UyLeX6VLKrCf02TzkWEbTa8kuwo5evgP/view?usp=sharing>`__

Unzip it somewhere you have plenty of disk space and note the location.

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

Where to go from here? 
-----------------------

After you have completed the contents of this lesson, you will know the basics of MNE-Python, but there is a lot more to learn.

In the `Documentation of MNE-Python <https://mne.tools>`__, there are tutorials that go in-depth on certain topics and quick examples that show you how to do specific things.

While these lesson materials focus on how to technically make MNE-Python do certain computations, it is important to know what those computations are, what purpose they serve, and how to interpret the results.
For this, we recommend taking a proper university-level neuroimaging course, such as:
Aalto University: `NBE-E4045 Functional Brain Imaging D (5 cr) <https://sisu.aalto.fi/student/courseunit/otm-ef8f2dea-edd6-4651-8702-f61dedaa9c2c/brochure>`__. 

To get started with your own data analysis pipelines, it is helpful to have an example pipeline to copy from.
`This git repository <https://version.aalto.fi/gitlab/biomag-pipelines/mne-standard/-/tree/minimal?ref_type=heads>`__ contains such an example pipeline, in three flavors: minimal, advanced, and expert.
Each flavor adds more bells and whistles to the pipeline to make it more complete and robust.

References and credit
~~~~~~~~~~~~~~~~~~~~~

The code from this tutorial is heavily inspired from this article:

*Mainak Jas, Eric Larson, Denis Engemann, Jaakko Leppakangas, Samu Taulu, Matti Hämäläinen,
and Alexandre Gramfort. 2018. A Reproducible MEG/EEG Group Study With the MNE Software:
Recommendations, Quality Assessments, and Good Practices.
Frontiers in Neuroscience. 12, doi: 10.3389/fnins.2018.00530*

The MNE software when used in publications should be acknowledged using citations.

To cite MNE-C or the inverse imaging implementations provided by the MNE software, please use:

*A. Gramfort, M. Luessi, E. Larson, D. Engemann, D. Strohmeier, C. Brodbeck, L. Parkkonen,
M. Hämäläinen, MNE software for processing MEG and EEG data, NeuroImage, Volume 86,
1 February 2014, Pages 446-460, ISSN 1053-8119.*

To cite the MNE-Python package, please use:

*A. Gramfort, M. Luessi, E. Larson, D. Engemann, D. Strohmeier, C. Brodbeck, R. Goj, M. Jas,
T. Brooks, L. Parkkonen, M. Hämäläinen, MEG and EEG data analysis with MNE-Python,
Frontiers in Neuroscience, Volume 7, 2013, ISSN 1662-453X.*
