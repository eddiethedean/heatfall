# Releasing Heatfall

This guide covers preparation for 1.3.0, records the published 1.2.0 behavior,
and gives a version-neutral release process. A pushed stable `vX.Y.Z` tag runs
the complete CI suite and publishes its validated source archive and wheel to
PyPI when all checks pass.

## Heatfall 1.3.0 compatibility notes

Version 1.3.0 requires Landfall 0.5.0 or newer and keeps Python 3.8–3.13 support.
The new `rng` and plotting `api_key` arguments are optional and keyword-only;
existing calls keep their behavior. The `geo` and `cairo` extras install
Landfall's optional dependencies for GIS overlays and Cairo rendering.

## Heatfall 1.2.0 compatibility notes

Heatfall 1.2.0 added default-on legends, precise legend placement and styling,
sequential colors, explicit count palettes, and immutable heat-layer metadata.
It also changed the default color scheme from `"distinct"` to the ordered
five-step `"heatmap"` palette.

| Change | Existing behavior and upgrade path |
| --- | --- |
| Legend enabled by default | Set `legend=False` or `context.set_legend(False)` to hide it. |
| Default palette changed | Set `color_scheme="distinct"` to retain the 1.1.0 palette. Disabling the legend alone does not change the palette. |
| Old 1.1.0 default appearance | Set both `color_scheme="distinct"` and `legend=False` (or disable the context legend). |
| Heatmap legend labels | The five-step default palette labels inclusive count ranges; cells still contain raw counts. Other palettes show one entry per observed count. |
| Shared count colors | Supply the same complete `count_colors` mapping to each map. |
| Other call behavior | Existing positional arguments, return types, fill opacity, and map fitting retain their behavior. |
| Python support | Runtime: 3.8–3.13. Documentation tools: 3.12 or newer. |

See the [changelog](changelog.md) for the published notes and later
documentation corrections.

## Prepare a release candidate

Start from a clean checkout of the commit intended for release. Choose the next
version and update `pyproject.toml`, `src/heatfall/__init__.py`, and the new
changelog section together. Do not reuse a version already published on PyPI.

Create a Python 3.13 environment. On macOS/Linux:

```sh
python3.13 -m venv .venv-release
```

In Windows PowerShell, use the Python launcher:

```powershell
py -3.13 -m venv .venv-release
```

Activate with `source .venv-release/bin/activate` on macOS/Linux, or
`.venv-release\Scripts\Activate.ps1` in PowerShell. Then install and run:

```sh
python -m pip install -e ".[dev,docs]" build twine
python -m pytest
python -m tox -e ruff,mypy,docs
python -m sphinx -b linkcheck -W --keep-going docs docs/_build/linkcheck
```

Build the source archive and wheel, then validate their metadata. Set the
version once in the shell before running these commands. In macOS/Linux:

```sh
RELEASE_VERSION=1.3.0  # Replace with the version being prepared
python -m build --outdir "dist/${RELEASE_VERSION}"
python -m twine check --strict "dist/${RELEASE_VERSION}/heatfall-${RELEASE_VERSION}.tar.gz" "dist/${RELEASE_VERSION}/heatfall-${RELEASE_VERSION}-py3-none-any.whl"
```

In Windows PowerShell, use:

```powershell
$RELEASE_VERSION = "1.3.0"  # Replace with the version being prepared
python -m build --outdir "dist/${RELEASE_VERSION}"
python -m twine check --strict "dist/${RELEASE_VERSION}/heatfall-${RELEASE_VERSION}.tar.gz" "dist/${RELEASE_VERSION}/heatfall-${RELEASE_VERSION}-py3-none-any.whl"
```

`python -m build` creates the source archive, then builds the wheel from that
archive. This verifies that the source distribution builds independently.
`twine check --strict` validates package metadata and README rendering.

## Verify the installed wheel

Use a separate environment so the test imports the built artifact rather than
an editable checkout:

On macOS/Linux:

```sh
python3.13 -m venv .venv-wheel
```

In Windows PowerShell:

```powershell
py -3.13 -m venv .venv-wheel
```

Activate with `source .venv-wheel/bin/activate` on macOS/Linux or
`.venv-wheel\Scripts\Activate.ps1` in PowerShell. Keep `RELEASE_VERSION` set
to the version being checked, and run:

```sh
python -m pip install "dist/${RELEASE_VERSION}/heatfall-${RELEASE_VERSION}-py3-none-any.whl" pytest pytest-cov
python -m pip check
python -c "from importlib.metadata import version; import heatfall; assert heatfall.__version__ == version('heatfall') == '${RELEASE_VERSION}'; print(heatfall.__file__)"
python -m pytest /path/to/heatfall/tests  # Replace with the repository's absolute tests path
```

Run the test command from outside the checkout and replace `/path/to/heatfall`
with the repository's absolute path (use a native Windows path in PowerShell).
The printed module path should be inside this environment's `site-packages`.
Keep `PYTHONPATH` unset.

## Confirm CI and package contents

Wait for every check on the release commit to pass. CI covers:

- Tests with 100% statement coverage on Python 3.8–3.13 on Linux, plus Python
  3.13 on macOS and Windows.
- Formatting, linting, and type checking.
- Composed GIS layers and native Cairo rendering with optional dependencies.
- Strict Sphinx documentation and external-link checks.
- Source archive and wheel builds, strict metadata checks, dependency checks,
  and installed-wheel tests on Python 3.8 and 3.13.

The Python 3.13 package job saves a `heatfall-distributions` artifact for 14
days. Use artifacts from the exact release commit.

The wheel must contain runtime modules, `py.typed`, bundled fonts, and the MIT
license. The source archive must also include tests, documentation sources and
images (including SVGs), the changelog, Read the Docs configuration, and
development files. Generated HTML, coverage reports, environments,
credentials, and OS metadata do not belong in release artifacts.

## Tag and publish

Pushing a tag matching `v*.*.*` starts `.github/workflows/release.yml`. It
accepts stable `vX.Y.Z` tags only when the tag, `pyproject.toml`, and
`heatfall.__version__` agree. The release workflow calls the full CI suite, then
publishes the Python 3.13 distribution artifact to PyPI after every check
passes. Branch pushes and pull requests do not publish.

The publishing job uses GitHub OIDC with `id-token: write`, the `pypi`
environment, and the PyPA publishing action; it does not need a PyPI API token.
The trusted publisher on PyPI must use owner `eddiethedean`, repository
`heatfall`, workflow `release.yml`, and environment `pypi` if an environment is
configured. Protection rules on that GitHub environment apply before
publication.

After CI passes:

1. Confirm the working tree is clean and the release commit is on `main`.
2. Keep `RELEASE_VERSION` set to the version being released, then create and
   push its annotated tag in macOS/Linux or PowerShell:

   ```sh
   git tag -a "v${RELEASE_VERSION}" -m "Heatfall ${RELEASE_VERSION}"
   git push origin "v${RELEASE_VERSION}"
   ```

3. Follow the Release workflow through successful PyPI publication.
4. Create a GitHub release for that tag using its changelog entry.
5. If Read the Docs hosting is connected, activate the tag's documentation
   version and confirm the build. See the
   [Read the Docs connection guide](development.md#connect-read-the-docs).
6. Verify installation from PyPI in a clean environment:

   ```sh
   python -m pip install --no-cache-dir "heatfall==${RELEASE_VERSION}"
   python -m pip check
   python -c "import heatfall; assert heatfall.__version__ == '${RELEASE_VERSION}'"
   ```

PyPI release files cannot be replaced under the same version. If a published
artifact needs a fix, prepare a new version; re-running a successful publish
job will encounter the existing files.
