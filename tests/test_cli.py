import json
from devhealth.cli import main


def test_json_output_and_exit_code(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr("devhealth.checks.check_python",
                        lambda: {"name": "python", "status": "ok", "details": {}})
    monkeypatch.setattr("devhealth.checks.check_disk",
                        lambda path: {"name": "disk", "status": "ok", "details": {}})
    monkeypatch.setattr("devhealth.checks.check_environment",
                        lambda: {"name": "environment", "status": "ok", "details": {}})
    monkeypatch.setattr("devhealth.checks.check_tools",
                        lambda tools: {"name": "developer_tools", "status": "ok",
                                       "details": {"tools": [], "missing": []}})
    code = main(["--json", "--tools", "git"])
    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["overall_status"] == "ok"


def test_bad_event_file_returns_input_error(tmp_path, capsys):
    event_file = tmp_path / "bad.json"
    event_file.write_text("{broken", encoding="utf-8")
    assert main(["--events", str(event_file)]) == 3
    assert "devhealth:" in capsys.readouterr().err
