# Contributing

Heatfall is a small Python library with a test suite, strict documentation
build, and release workflow. Start with a focused issue or pull request and
include a minimal example when changing observable behavior.

## Development setup

Heatfall supports Python 3.8–3.13 at runtime. The documentation toolchain
requires Python 3.12 or newer; CI uses Python 3.13.

```sh
git clone https://github.com/eddiethedean/heatfall.git
cd heatfall
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,docs]"
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. Use a
Python 3.13 environment for the documentation build.

## Run checks

```sh
python -m pytest
python -m tox -e ruff,mypy
python -m sphinx -b html -W --keep-going docs docs/_build/html
```

The test configuration requires 100% statement coverage for the `heatfall`
package. Ordinary tests use mock tiles; only tests explicitly marked
`integration` may request live map tiles. Keep examples and tests offline where
possible. `ruff` checks lint and formatting, `mypy` checks the source and
examples, and the Sphinx build treats warnings as errors.

To exercise composed maps with Landfall's optional GeoPandas and Shapely
dependencies, use a Python 3.13 environment:

```sh
python -m tox -e geo
```

This runs the same suite with `heatfall[geo]` installed. The core suite skips
the GeoDataFrame check when its optional dependencies are absent. GIS CI runs
it with those dependencies present and uses mock tiles. The same CI job installs
the Cairo extra and exercises the actual Cairo renderer.

With the native Cairo development libraries installed, run the optional
renderer suite locally:

```sh
python -m tox -e cairo
```

See [Cairo setup](basemaps.md#optional-cairo-rendering) for system requirements.

To verify outbound links as well, run:

```sh
python -m sphinx -b linkcheck -W --keep-going docs docs/_build/linkcheck
```

## Change documentation and images

Update the relevant Markdown or reStructuredText page when behavior or defaults
change. Add a changelog entry under `Unreleased` for user-visible changes.
Representative README and guide snippets are exercised by
`tests/test_documentation_examples.py` with tiles disabled.

To regenerate map images, follow the instructions in
[Development and documentation](development.md#build-the-documentation). Map
tiles can change over time; inspect image diffs and retain attribution before
including regenerated files.

## Open a pull request

- Explain the user problem and the behavior changed.
- Add or update tests and docs for behavior changes.
- Run the relevant checks above and report their results.
- Keep the change focused; include a small reproducible example when useful.

Open an [issue](https://github.com/eddiethedean/heatfall/issues) for bugs,
questions, or proposed features. Do not put vulnerability details in a public
issue; follow the [security policy](security.md).

## Release process

Only maintainers publish releases. The [release guide](releasing.md) documents
version updates, package validation, the annotated tag workflow, PyPI
publication, and post-release verification.
