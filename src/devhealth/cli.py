"""Command-line interface for DevHealth."""

import argparse
import json
import sys
from pathlib import Path

from .checks import DEFAULT_TOOLS, collect_report


def render_human(report: dict) -> str:
    lines = [
        f"DevHealth {report['tool']['version']} — {report['overall_status'].upper()}",
        "=" * 58,
    ]
    for check in report["checks"]:
        lines.append(f"[{check['status'].upper():7}] {check['name']}")
        details = check["details"]
        if check["name"] == "python":
            lines.append(f"         {details['version']} ({details['implementation']})")
        elif check["name"] == "disk":
            lines.append(
                f"         {details['free_percent']}% free "
                f"({details['free_bytes']} bytes) at {details['path']}"
            )
        elif check["name"] == "environment":
            set_names = [key for key, value in details.items() if value]
            lines.append(f"         Set: {', '.join(set_names) if set_names else 'none'}")
        elif check["name"] == "developer_tools":
            for tool in details["tools"]:
                state = tool["path"] or "not found"
                lines.append(f"         {tool['name']}: {state}")
        elif check["name"] == "diagnostic_events":
            lines.append(
                f"         {details['event_count']} events; "
                f"{details['error_events']} errors; "
                f"{details['missing_latency_events']} missing latencies"
            )
    lines.extend(["", f"Exit code: {report['exit_code']}"])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="devhealth",
        description="Inspect a developer environment and produce a health report.",
    )
    parser.add_argument("--json", action="store_true", help="print structured JSON")
    parser.add_argument("--output", type=Path, help="write report to this file")
    parser.add_argument(
        "--tools", default=",".join(DEFAULT_TOOLS),
        help="comma-separated executable names to check",
    )
    parser.add_argument("--events", type=Path, help="optional diagnostic events JSON file")
    parser.add_argument("--disk-path", default=".", help="path whose filesystem is checked")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        event_payload = None
        if args.events:
            event_payload = json.loads(args.events.read_text(encoding="utf-8"))
        tools = [item.strip() for item in args.tools.split(",") if item.strip()]
        report = collect_report(tools=tools, disk_path=args.disk_path,
                                events=event_payload)
        rendered = (json.dumps(report, indent=2, sort_keys=True) if args.json
                    else render_human(report))
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
        return report["exit_code"]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"devhealth: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
