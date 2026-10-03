# Releasing Heatfall

## 1.1.0 release notes

This release builds on 1.0.0 with H3 geometry fixes, configurable transparency,
stronger input validation, and expanded documentation. The complete changes are
in the [changelog](changelog.md).

### Compatibility

- Existing positional plotting arguments retain their order. `opacity` is a new
  keyword-only option on both plotting functions and both context heat methods.
- Heat fills now default to **60% opacity**. Set `opacity=1.0` to restore the
  previous solid appearance.
- H3 boundaries now use the correct latitude/longitude order. Crossing cells
  split at ±180°, retaining one count and one opacity application per cell.
- Invalid coordinates, including non-finite values, raise `ValueError` in
  context heat methods as well as plotting functions.
- Runtime support remains **Python 3.8–3.13**. Minimum dependencies are
  `landfall>=0.4.2`, `geodude>=0.1.1`, and `h3>=4.0.0`.
- The optional documentation extra requires Python 3.12 or newer. Documentation
  CI, tox, and Read the Docs use Python 3.13.

Color palettes continue to represent distinct count levels within a layer;
this release does not introduce a sequential heat scale or density normalization.

## Validate the release candidate

Use a clean checkout of the commit intended for release. Confirm that
`pyproject.toml`, `heatfall.__version__`, and the changelog all identify `1.1.0`.
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
python -m build --outdir dist/1.1.0
python -m twine check --strict dist/1.1.0/heatfall-1.1.0.tar.gz dist/1.1.0/heatfall-1.1.0-py3-none-any.whl
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
python -m pip install dist/1.1.0/heatfall-1.1.0-py3-none-any.whl pytest pytest-cov
python -m pip check
python -c "from importlib.metadata import version; import heatfall; assert heatfall.__version__ == version('heatfall') == '1.1.0'; print(heatfall.__file__)"
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

Perform these steps when the candidate and its CI results have been accepted.
Repository preparation does not publish to PyPI or create a release tag.

1. Confirm the working tree is clean and the release commit is on `main`.
2. Create and push the annotated tag:

   ```sh
   git tag -a v1.1.0 -m "Heatfall 1.1.0"
   git push origin v1.1.0
   ```

3. Upload the exact validated artifacts using your normal PyPI authentication:

   ```sh
   python -m twine upload dist/1.1.0/heatfall-1.1.0.tar.gz dist/1.1.0/heatfall-1.1.0-py3-none-any.whl
   ```

4. Create a GitHub release for `v1.1.0` using this version's changelog notes.
5. If Read the Docs hosting is connected, activate the tag's documentation
   version and verify its build. The [connection guide](development.md#connect-read-the-docs)
   covers the initial project setup.
6. Verify the published version in a fresh environment:

   ```sh
   python -m pip install --no-cache-dir "heatfall==1.1.0"
   python -m pip check
   python -c "import heatfall; assert heatfall.__version__ == '1.1.0'"
   ```

PyPI version files cannot be replaced with corrected files under the same
filename. If a published artifact needs a fix, prepare a new version rather
than reusing 1.1.0.
