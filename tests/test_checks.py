from devhealth.checks import check_environment, check_python, check_tools


def test_python_check_has_expected_fields():
    result = check_python()
    assert result["name"] == "python"
    assert result["status"] in {"ok", "error"}
    assert "version" in result["details"]


def test_environment_reports_boolean_values_only(monkeypatch):
    monkeypatch.setenv("CI", "secret-value")
    result = check_environment()
    assert result["details"]["CI"] is True
    assert "secret-value" not in repr(result)


def test_tools_are_sorted_and_missing_are_reported(monkeypatch):
    monkeypatch.setattr("devhealth.checks.shutil.which",
                        lambda name: "/bin/" + name if name == "git" else None)
    result = check_tools(["z-tool", "git"])
    assert [x["name"] for x in result["details"]["tools"]] == ["git", "z-tool"]
    assert result["details"]["missing"] == ["z-tool"]
