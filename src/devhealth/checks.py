"""Read-only machine checks. Environment values are never exposed."""

from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Iterable

ENV_KEYS = ("CI", "CONDA_PREFIX", "PATH", "PYTHONPATH", "VIRTUAL_ENV")
DEFAULT_TOOLS = ("git", "docker", "node", "npm", "code", "pytest")
GIB = 1024 ** 3


def _result(name: str, status: str, details: dict) -> dict:
    return {"name": name, "status": status, "details": details}


def check_python() -> dict:
    version = platform.python_version()
    major, minor = sys.version_info[:2]
    status = "ok" if (major, minor) >= (3, 10) else "error"
    return _result("python", status, {
        "version": version,
        "implementation": platform.python_implementation(),
        "minimum_version": "3.10",
        "executable": str(Path(sys.executable)),
    })


def check_disk(path: str | os.PathLike[str] = ".") -> dict:
    target = Path(path).resolve()
    usage = shutil.disk_usage(target)
    free_percent = round((usage.free / usage.total) * 100, 2) if usage.total else 0.0
    if usage.free < GIB or free_percent < 5:
        status = "error"
    elif usage.free < 5 * GIB or free_percent < 15:
        status = "warning"
    else:
        status = "ok"
    return _result("disk", status, {
        "path": str(target),
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
        "free_percent": free_percent,
    })


def check_environment() -> dict:
    return _result("environment", "ok", {
        key: bool(os.environ.get(key)) for key in ENV_KEYS
    })


def check_tools(tools: Iterable[str] = DEFAULT_TOOLS) -> dict:
    entries = []
    for name in sorted(set(tools)):
        location = shutil.which(name)
        entries.append({"name": name, "available": location is not None,
                        "path": location})
    missing = [entry["name"] for entry in entries if not entry["available"]]
    return _result("developer_tools", "warning" if missing else "ok", {
        "tools": entries,
        "missing": missing,
    })


def collect_report(tools: Iterable[str] = DEFAULT_TOOLS,
                   disk_path: str | os.PathLike[str] = ".",
                   events: dict | None = None) -> dict:
    """Collect checks in a fixed order; no timestamp makes output repeatable."""
    checks = [
        check_python(),
        check_disk(disk_path),
        check_environment(),
        check_tools(tools),
    ]
    if events is not None:
        from .events import summarize_events
        checks.append(_result("diagnostic_events", "ok", summarize_events(events)))

    statuses = [check["status"] for check in checks]
    overall = "error" if "error" in statuses else (
        "warning" if "warning" in statuses else "ok"
    )
    return {
        "schema_version": "1.0",
        "tool": {"name": "devhealth", "version": "1.0.0"},
        "overall_status": overall,
        "checks": checks,
        "exit_code": {"ok": 0, "warning": 1, "error": 2}[overall],
    }
