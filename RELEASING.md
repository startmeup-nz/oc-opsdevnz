# Releasing oc-opsdevnz

1. Ensure staging/prod guardrails still hold: default is staging; prod must be explicit (`for_prod`/`--prod`).
2. Run tests: `pytest`.
3. Update `CHANGELOG.md` and bump the version in `pyproject.toml`.
4. Build the wheel and sdist: `python -m build`.
5. Publish to TestPyPI first, verify install, then publish to PyPI.
6. Tag the release and announce in the OpsDev.nz ops channel.
