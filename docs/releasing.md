# Releasing Heatfall

::::{container} hf-section-intro
Build, validate, and publish a tagged release. The commands below use **1.2.0**;
replace that version consistently when preparing a later release.
::::

## 1.2.0 compatibility notes

Heatfall 1.2.0 adds map legends, precise placement and styling controls,
sequential colors, explicit count palettes, and immutable heat layer metadata.
See the [changelog](changelog.md) for the complete release notes.

| Change | What existing users should know |
| --- | --- |
| Legends enabled by default | Use `legend=False` or `context.set_legend(False)` to retain the earlier appearance. |
| Translucent legend panel | Map content shows through the panel; text and swatches retain independent styling. |
| Shared count colors | Supply `count_colors` to make equal counts match across maps. |
| Existing plotting calls | Positional arguments, return types, default palettes, fill opacity, and map fitting retain their behavior. |
| Python support | Runtime: 3.8–3.13. Documentation tools: 3.12 or newer. |

::::{container} hf-callout
**Release sequence** · Validate the source → check the installed wheel → confirm
CI → tag and publish → verify the PyPI installation.
::::

## Validate the release candidate

Use a clean checkout of the commit intended for release. Confirm that
`pyproject.toml`, `heatfall.__version__`, and the changelog all identify `1.2.0`.
All release changes must be under that version's changelog entry.

Create a Python 3.13 environment:

```sh
python -m venv .venv-release
```

Activate it with `source .venv-release/bin/activate` on macOS/Linux, or
`.venv-release\Scripts\Activate.ps1` in PowerShell. Then run:

```sh
python -m pip install -e ".[dev,docs]" build twine
python -m pytest --cov-fail-under=100
python -m tox -e ruff,mypy,docs
python -m build --outdir dist/1.2.0
python -m twine check --strict dist/1.2.0/heatfall-1.2.0.tar.gz dist/1.2.0/heatfall-1.2.0-py3-none-any.whl
```

`python -m build` creates the source archive, then builds the wheel from that
archive. This checks that the source distribution can build independently.
`twine check --strict` validates distribution metadata and README rendering.
See the [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
for the build and upload workflow.

## Verify the installed artifact

Create a separate environment to avoid testing an editable installation:

```sh
python -m venv .venv-wheel
```

Activate that environment and install the wheel plus test tools:

```sh
python -m pip install dist/1.2.0/heatfall-1.2.0-py3-none-any.whl pytest pytest-cov
python -m pip check
python -c "from importlib.metadata import version; import heatfall; assert heatfall.__version__ == version('heatfall') == '1.2.0'; print(heatfall.__file__)"
python -m pytest --cov-fail-under=100
```

The printed package path should be inside this environment's `site-packages`,
not the checkout's `src` directory. Keep `PYTHONPATH` unset during this check.
Ordinary rendering tests use mock tiles, including antimeridian and opacity
regressions. Inspect the example maps and both documentation color modes when
preparing changes to rendering or documentation.

## Confirm CI and package contents

Wait for every check on the release commit to pass. CI covers:

- Tests with 100% statement coverage on Python 3.8–3.13 on Linux, plus Python
  3.13 on macOS and Windows.
- Formatting, linting, and type checking.
- A strict documentation build.
- Source archive and wheel builds, strict metadata checks, dependency checks,
  and the test suite against the installed wheel on Python 3.8 and 3.13.

The Python 3.13 package job saves a `heatfall-distributions` artifact for 14 days.
Download it from the successful run if you prefer the CI-built distributions.
Use artifacts from the exact release commit.

The wheel must contain the runtime modules, `py.typed`, and the MIT license.
The source archive must also contain the tests and shared fixtures, documentation
sources and CSS, map images, changelog, Read the Docs config, and development
configuration. Generated HTML, coverage reports, environments, credentials, and
OS metadata files do not belong in the release artifacts.

## Tag and publish

Pushing a tag matching `v*.*.*` starts `.github/workflows/release.yml`. It accepts
stable `vX.Y.Z` versions and rejects tags that do not match both
`pyproject.toml` and `heatfall.__version__`. The workflow calls the full CI suite,
then publishes its Python 3.13 distribution artifact to PyPI after every check
passes. Branch pushes and pull requests run checks without publishing.

The publishing job uses GitHub OIDC with `id-token: write`, the `pypi`
environment, and the PyPA publishing action. It does not need a PyPI API token.
The trusted publisher configured on PyPI must name:

| Setting | Value |
| --- | --- |
| Owner | `eddiethedean` |
| Repository | `heatfall` |
| Workflow filename | `release.yml` |
| Environment, if configured | `pypi` |

See [PyPI's trusted publishing guide](https://docs.pypi.org/trusted-publishers/using-a-publisher/)
for authentication details. Any protection rules on the GitHub `pypi`
environment apply before publication.

Perform these steps when the candidate and its CI results have been accepted:

1. Confirm the working tree is clean and the release commit is on `main`.
2. Create and push the annotated tag:

   ```sh
   git tag -a v1.2.0 -m "Heatfall 1.2.0"
   git push origin v1.2.0
   ```

3. Follow the **Release** workflow in GitHub Actions. It validates the tag,
   runs tests and package checks, and publishes the checked wheel and source
   archive. A failed prerequisite prevents the publishing job from running.
4. After successful publication, create a GitHub release for `v1.2.0` using
   this version's changelog notes.
5. If Read the Docs hosting is connected, activate the tag's documentation
   version and verify its build. The [connection guide](development.md#connect-read-the-docs)
   covers the initial project setup.
6. Verify the published version in a fresh environment:

   ```sh
   python -m pip install --no-cache-dir "heatfall==1.2.0"
   python -m pip check
   python -c "import heatfall; assert heatfall.__version__ == '1.2.0'"
   ```

PyPI version files cannot be replaced with corrected files under the same
filename. If a published artifact needs a fix, prepare a new version rather
than reusing 1.2.0. Re-running a successful publishing job will encounter the
existing files; the workflow does not silently skip them.
