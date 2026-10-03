"""Sphinx configuration shared by local, CI, and Read the Docs builds."""

import os

import heatfall

project = "Heatfall"
author = "Odos Matthews"
copyright = "2026, Odos Matthews"
release = heatfall.__version__
version = release

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
root_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
autodoc_member_order = "bysource"
autodoc_typehints = "description"
myst_heading_anchors = 3
myst_enable_extensions = ["substitution"]
myst_substitutions = {"release": release}

html_theme = "sphinx_rtd_theme"
html_logo = "heatfall_logo.png"
html_title = f"{project} {release}"
html_theme_options = {"navigation_depth": 3}
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "")
