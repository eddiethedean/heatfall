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
    "sphinx_copybutton",
]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
root_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
autodoc_member_order = "bysource"
autodoc_typehints = "description"
myst_heading_anchors = 3
myst_enable_extensions = ["substitution", "colon_fence"]
myst_substitutions = {"release": release}

html_theme = "furo"
html_logo = "heatfall_logo.png"
html_favicon = "heatfall_logo.png"
html_title = f"{project} {release}"
html_static_path = ["_static"]
html_css_files = ["heatfall.css"]
html_theme_options = {
    "source_repository": "https://github.com/eddiethedean/heatfall/",
    "source_branch": "main",
    "source_directory": "docs/",
    "light_css_variables": {
        "color-brand-primary": "#a63416",
        "color-brand-content": "#a63416",
        "color-brand-visited": "#8c2944",
        "color-foreground-primary": "#30211e",
        "color-foreground-secondary": "#66514a",
        "color-foreground-muted": "#736058",
        "color-background-primary": "#fffcf8",
        "color-background-secondary": "#f7efe7",
        "color-background-hover": "#f2e3d5",
        "color-background-border": "#e8d8ca",
        "color-api-name": "#a63416",
        "color-api-pre-name": "#a63416",
        "hf-hero-background": "linear-gradient(135deg, #fff1dc, #fce5df)",
        "hf-label": "#9a391a",
    },
    "dark_css_variables": {
        "color-brand-primary": "#ffb378",
        "color-brand-content": "#ffb378",
        "color-brand-visited": "#f6a7b8",
        "color-foreground-primary": "#f5e6db",
        "color-foreground-secondary": "#d0b8a9",
        "color-foreground-muted": "#bfa797",
        "color-background-primary": "#1e1715",
        "color-background-secondary": "#281e1a",
        "color-background-hover": "#38271f",
        "color-background-border": "#50382d",
        "color-api-name": "#ffb378",
        "color-api-pre-name": "#ffb378",
        "hf-hero-background": "linear-gradient(135deg, #38261a, #3c2020)",
        "hf-label": "#ffba7a",
    },
}
pygments_style = "friendly"
pygments_dark_style = "monokai"
copybutton_prompt_text = r">>> |\.\.\. "
copybutton_prompt_is_regexp = True
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "")
