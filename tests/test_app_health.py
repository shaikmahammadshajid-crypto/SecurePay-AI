from utils.app_health import file_check, health_summary


def test_file_check_reports_missing_file(tmp_path):
    result = file_check("Missing", tmp_path / "missing.pkl")

    assert result["ok"] is False
    assert "missing or empty" in result["detail"]


def test_health_summary_reports_attention_for_failed_checks():
    result = health_summary([
        {"name": "A", "ok": True, "detail": "ok"},
        {"name": "B", "ok": False, "detail": "failed"},
    ])

    assert result["status"] == "attention"
    assert "1 check" in result["message"]
