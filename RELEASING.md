# Releasing `oc-opsdevnz`

Publish to TestPyPI first, verify, then ship to PyPI.

## Prerequisites

- Access to the `startmeup-nz` TestPyPI/PyPI tokens (stored in 1Password).
- `twine` and `build` installed (`pip install -e .[dev]` in your venv).
- Clean `main` and tests green.

## Workflow

1. **Guardrails** 

Default API target is staging; prod requires `--prod`. (Future change will flip default to prod—update docs when that happens.)

2. **Version + changelog** 

Bump `project.version` in `pyproject.toml` and add a `CHANGELOG.md` entry.

3. **Tests**

   ```
   pytest
   ```

4. **Build**

   ```
   rm -rf dist/
   python -m build
   python -m twine check dist/*
   ```

5. **TestPyPI**

   ```
   twine upload --repository testpypi dist/*
   ```

   Smoke-test:

   ```
   python -m venv /tmp/oc-opsdevnz-test && source /tmp/oc-opsdevnz-test/bin/activate
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple oc-opsdevnz==<new-version>
   oc-opsdevnz version
   ```

6. **PyPI**

   ```
   python -m twine upload --repository pypi dist/*
   ```

   Smoke-test:
   
   ```
   pip install oc-opsdevnz==<new-version>
   oc-opsdevnz version
   ```

7. **Tag + push**

   ```
   # prefer prefixed tag
   git tag -a oc-opsdevnz-v<new-version> -m "Release <new-version>"
   git push origin main oc-opsdevnz-v<new-version>
   ```
