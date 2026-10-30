"""Deterministic summaries for optional JSON diagnostic-event input."""

from collections import Counter


def summarize_events(payload: dict) -> dict:
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise ValueError("event input must be a JSON object containing an 'events' array")

    events = payload["events"]
    levels = Counter()
    services = Counter()
    error_events = 0
    missing_latency = 0
    latency_values = []

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError(f"event at index {index} must be an object")
        level = str(event.get("level", "UNKNOWN")).upper()
        service = str(event.get("service", "unknown"))
        levels[level] += 1
        services[service] += 1
        status_code = event.get("status_code")
        if level == "ERROR" or (
            isinstance(status_code, int) and status_code >= 500
        ):
            error_events += 1
        latency = event.get("latency_ms")
        if latency is None:
            missing_latency += 1
        elif isinstance(latency, (int, float)) and not isinstance(latency, bool):
            latency_values.append(float(latency))
        else:
            raise ValueError(f"event at index {index} has invalid latency_ms")

    return {
        "event_count": len(events),
        "levels": dict(sorted(levels.items())),
        "services": dict(sorted(services.items())),
        "error_events": error_events,
        "missing_latency_events": missing_latency,
        "latency_ms": {
            "count": len(latency_values),
            "average": round(sum(latency_values) / len(latency_values), 2)
                        if latency_values else None,
            "maximum": max(latency_values) if latency_values else None,
        },
    }
