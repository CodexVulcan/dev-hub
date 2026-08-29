"""Tests for /api/testing router."""


def test_submit_results_happy(client):
    r = client.post("/api/testing/results", json={
        "test_suite": "Unit Tests",
        "results": [
            {"test_name": "test_login", "status": "passed", "message": "", "severity": "info"},
            {"test_name": "test_signup", "status": "failed", "message": "AssertionError", "severity": "info"},
        ]
    })
    assert r.status_code == 201
    body = r.json()
    assert body["test_suite"] == "Unit Tests"
    assert len(body["results"]) == 2


def test_auto_severity_from_status(client):
    """failed status with default info severity should be auto-promoted to critical."""
    r = client.post("/api/testing/results", json={
        "test_suite": "Auto Sev",
        "results": [{"test_name": "fail_test", "status": "failed", "message": "", "severity": "info"}]
    })
    result = r.json()["results"][0]
    assert result["severity"] == "critical"


def test_auto_severity_skipped(client):
    r = client.post("/api/testing/results", json={
        "test_suite": "Skip Sev",
        "results": [{"test_name": "skip_test", "status": "skipped", "message": "", "severity": "info"}]
    })
    result = r.json()["results"][0]
    assert result["severity"] == "warning"


def test_list_reports(client):
    client.post("/api/testing/results", json={
        "test_suite": "List Suite",
        "results": [{"test_name": "t1", "status": "passed", "message": ""}]
    })
    r = client.get("/api/testing/reports")
    assert r.status_code == 200
    assert len(r.json()["reports"]) >= 1


def test_get_report_happy(client):
    r = client.post("/api/testing/results", json={
        "test_suite": "Get Suite",
        "results": [{"test_name": "t2", "status": "passed", "message": ""}]
    })
    rid = r.json()["id"]
    r2 = client.get(f"/api/testing/reports/{rid}")
    assert r2.status_code == 200
    assert r2.json()["id"] == rid


def test_get_report_not_found(client):
    r = client.get("/api/testing/reports/99999")
    assert r.status_code == 404


def test_submit_empty_results(client):
    r = client.post("/api/testing/results", json={"test_suite": "Empty", "results": []})
    assert r.status_code == 201
    assert r.json()["results"] == []
