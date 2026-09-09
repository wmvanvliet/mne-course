# Configuration file for the Sphinx documentation builder.

import os
import sys

# Project information.
project = "MNE-Python course"
copyright = "2026"
author = "Marijn van Vliet"

# Sphynx extensions to load.
extensions = [
    "myst_nb",
]

# Allow Markdown files to be used as Sphinx source files.
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
    ".ipynb": "myst-nb",
}

# Don't execute the notebooks when building the documentation.
nb_execution_mode = "off"

# Entrypoint to the whole thing.
master_doc = "index"

# HTML output.
html_theme = "sphinx_rtd_theme"
html_title = project

# Files to ignore.
exclude_patterns = [
    "jupyter_execute/**",
]
