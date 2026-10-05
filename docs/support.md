# Support and troubleshooting

Start with [Troubleshooting](troubleshooting.md) for tile access, coordinate
validation, colors, legends, and version-specific options. Check your Python
interpreter and Heatfall version with:

```sh
python -c "import sys, heatfall; print(sys.executable); print(heatfall.__version__)"
```

## Ask a question or report a bug

Use [GitHub Issues](https://github.com/eddiethedean/heatfall/issues). Include
the Python and Heatfall versions, operating system, grid and precision, relevant
palette and options, expected behavior, and a full traceback or screenshot.
Reduce the report to a short example; use synthetic coordinates when the source
data is private. Check whether it reproduces with
`staticmaps.tile_provider_None` to distinguish rendering from tile-provider
issues.

Heatfall has no published response-time guarantee or paid support service.
Feature requests are tracked as issues, but an issue is not a delivery
commitment.

## Security issues

Report suspected vulnerabilities privately through the repository's
[security policy](security.md). Do not post exploit details or sensitive data
in a public issue.
