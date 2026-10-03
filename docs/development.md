# Development and documentation

## Set up a checkout

```sh
git clone https://github.com/eddiethedean/heatfall.git
cd heatfall
python -m venv .venv
```

Activate the environment with `source .venv/bin/activate` on macOS/Linux, or
`.venv\Scripts\Activate.ps1` in Windows PowerShell. Install development tools:

```sh
python -m pip install -e ".[dev]"
python -m pytest
python -m tox -e ruff,mypy
```

Ordinary tests use mock map tiles. Tests explicitly marked `integration` may
request real tiles. CI covers Python 3.8–3.13 on Linux, Python 3.13 on macOS and
Windows, linting, type checks, package builds, and the documentation build.

## Build the documentation

Documentation tooling requires **Python 3.12 or newer**; Read the Docs and the CI
documentation job use Python 3.13. In an environment with that Python version:

```sh
python -m pip install -e ".[docs]"
python -m sphinx -b html -W --keep-going docs docs/_build/html
```

Open `docs/_build/html/index.html` in a browser. Warnings fail the build so broken
references and missing pages are caught before publishing. The API reference
imports the installed package; its displayed version comes from
`heatfall.__version__`.

The Furo theme supplies responsive navigation, search, and light/dark modes.
Heatfall's ember and amber palette is configured in `docs/conf.py`, with landing
page, card, and content styles in `docs/_static/heatfall.css`. Code examples have
copy buttons. Preview both color modes and a narrow viewport when changing the
layout; keep actual map examples and their attribution visible.

The transparent logo is `docs/heatfall_logo.png`, shared by the README, docs
navigation, and browser icon. It was generated with the built-in imagegen tool;
the [generation prompt](https://github.com/eddiethedean/heatfall/blob/main/examples/heatfall_logo_prompt.txt)
records its hexagonal flame motif and ember, orange, and amber colors.

With tox installed and Python 3.13 available, the equivalent isolated build is:

```sh
python -m tox -e docs
```

The checked-in map images are reused during documentation builds. To regenerate
them from synthetic observations and real OpenStreetMap tiles:

```sh
python examples/generate_doc_maps.py
```

The image generator needs network access when tiles are not cached. Building the
HTML documentation does not render maps or download tiles.

## Connect Read the Docs

Heatfall's documentation is published at
[heatfall.readthedocs.io](https://heatfall.readthedocs.io/en/latest/index.html).
The repository's `.readthedocs.yaml` defines the OS, Python version, package
installation with the `docs` extra, Sphinx configuration, and strict warnings.
To configure hosting for a fork or reconnect the project:

1. Sign in to [Read the Docs](https://app.readthedocs.org/) and connect your GitHub
   account.
2. Import `eddiethedean/heatfall`, choose `main` as the default branch, and keep
   the root `.readthedocs.yaml` as the configuration file.
3. Trigger the first build and verify the documentation URL assigned to the
   project. For a fork, set the README and package documentation links to its
   own published URL.
4. Optionally activate release-tag versions and pull request previews in the
   project's settings.

See the [Read the Docs Sphinx guide](https://docs.readthedocs.com/platform/stable/intro/sphinx.html)
for the import workflow. Account connection and project import are separate from
the repository configuration.

## Prepare a release

See the [release guide](releasing.md) for 1.1.0 compatibility notes, package
validation, and the tag, upload, and verification steps.
