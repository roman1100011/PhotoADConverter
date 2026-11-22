# Film Lab

I'm building Film Lab to process my scanned film negatives. I use Python for the
app, Qt for the interface, and NumPy and OpenCV for the heavier image calculations.

## Current milestone

So far, I've set up the project, the virtual environment, and the first version
of the desktop app. I can test that it starts and package it for macOS. Importing
and editing scans are still on my list.

## Open the application (macOS)

After building, double-click **dist/Film Lab.app** in Finder. I've bundled Python,
Qt, and the native libraries so the app opens directly from Finder. For now, I
use an unsigned, unnotarized build for local development.

## Developer setup

Use Python 3.13 (64-bit). From the project root:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock
.venv/bin/python -m pip install --no-build-isolation -e '.[dev]'
.venv/bin/python -m film_lab
```

I pin the dependency versions I've tested on macOS in `requirements-dev.lock`.
To refresh the lock, install `.[dev]` with `--upgrade` and freeze the environment,
excluding the editable Film Lab entry. Keep setuptools in the lock so the build
can run offline with build isolation disabled. I'll resolve and test dependencies
again when I add support for another platform.

## Verify and build

```sh
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest
.venv/bin/python -m build --no-isolation
.venv/bin/python scripts/build_app.py
```

I use PyInstaller to build `dist/Film Lab.app`. I'm building for macOS right now,
and any future desktop bundles need to be built on their target operating system.
Git ignores the build output and virtual environment. The native libraries come
as precompiled wheels, so the build skips a separate C++ compilation step.

## Layout

```text
src/film_lab/
  app.py              Application startup
  ui/                 Qt windows and controls
  processing/         Native-backed image pipeline
  imaging/            Scan I/O, metadata and export (future)
scripts/              Desktop packaging and launcher
tests/                Application startup verification
docs/architecture.md  Processing constraints and feature roadmap
pyproject.toml        Package metadata, dependencies and tooling
requirements-dev.lock Exact development dependency versions
```

I followed the [Qt for Python documentation](https://doc.qt.io/qtforpython-6/quickstart.html) to set up the interface.
Desktop bundles use [PyInstaller](https://www.pyinstaller.org/en/stable/usage.html).
