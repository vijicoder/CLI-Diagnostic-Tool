# DevHealth CLI

A small, installable Python command-line tool that checks a developer machine and
prints a stable, machine-readable health report. It uses only the Python standard
library at runtime.

## Features

- Python interpreter version and implementation
- Disk capacity, free bytes, and free-space percentage
- Safe environment-variable inspection (names and set/unset only; values are never printed)
- Availability of common developer tools (`git`, `docker`, `node`, `npm`, `code`, `pytest`)
- Optional analysis of a JSON diagnostic-event file
- Human-readable or sorted, indented JSON output
- Stable exit codes for automation

## Requirements

Python 3.10 or newer.

## Install in an isolated virtual environment

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Windows PowerShell
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Usage

```bash
# Human-readable machine report
devhealth

# Deterministic JSON report
devhealth --json

# Save JSON report to a file
devhealth --json --output reports/machine.json

# Check selected developer tools
devhealth --tools git,docker,node,python

# Include event-log summary
devhealth --events samples/diagnostic-events.json --json
```

The event file must contain an object with an `events` array. Each event may
contain `timestamp`, `service`, `level`, `latency_ms`, and `status_code`.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All checks passed |
| `1` | Report completed, but one or more checks have warnings |
| `2` | Report completed, but one or more checks failed |
| `3` | Invalid input or report could not be written |

Warnings do not prevent the report from being generated. Disk space below 15%
or 5 GiB is a warning; below 5% or 1 GiB is an error. Python below 3.10 is
an error. Missing selected tools are warnings.

## Determinism and privacy

For an unchanged machine snapshot and identical arguments, the report has the
same content and ordering. It intentionally omits generation timestamps and
environment-variable values. It reports only whether a small allowlist of
useful environment variables is set. Disk values and installed-tool availability
naturally change when the machine changes.

## Development and tests

```bash
python -m pytest
```

## Project layout

```text
devhealth-cli/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/devhealth/
│   ├── __init__.py
│   ├── checks.py
│   ├── events.py
│   └── cli.py
├── tests/
│   ├── test_checks.py
│   ├── test_events.py
│   └── test_cli.py
└── samples/
    ├── diagnostic-events.json
    └── sample-report.json
```
