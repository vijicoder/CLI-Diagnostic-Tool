import pytest
from devhealth.events import summarize_events


def test_sample_event_summary():
    payload = {"events": [
        {"service": "billing-api", "level": "INFO", "latency_ms": 148, "status_code": 200},
        {"service": "billing-api", "level": "WARN", "latency_ms": 920, "status_code": 200},
        {"service": "profile-api", "level": "ERROR", "latency_ms": 1210, "status_code": 503},
        {"service": "profile-api", "level": "INFO", "latency_ms": 205, "status_code": 200},
        {"service": "billing-api", "level": "ERROR", "latency_ms": None, "status_code": 500},
    ]}
    result = summarize_events(payload)
    assert result["event_count"] == 5
    assert result["levels"] == {"ERROR": 2, "INFO": 2, "WARN": 1}
    assert result["services"] == {"billing-api": 3, "profile-api": 2}
    assert result["error_events"] == 2
    assert result["missing_latency_events"] == 1
    assert result["latency_ms"] == {"count": 4, "average": 620.75, "maximum": 1210.0}


def test_invalid_events_payload_fails():
    with pytest.raises(ValueError):
        summarize_events({"records": []})
