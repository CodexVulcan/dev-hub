"""Tests for /api/debugging router."""


def test_create_report_happy(client):
    r = client.post("/api/debugging/report", json={
        "title": "Sprint 1 Issues",
        "issues": [
            {"title": "Null pointer in auth", "description": "crashes on login", "severity": "critical"},
            {"title": "Slow query", "description": "timeout on search", "severity": "major"},
            {"title": "Typo in log", "description": "", "severity": "minor"},
        ]
    })
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Sprint 1 Issues"
    assert len(body["issues"]) == 3
    # Sorted by severity: critical first
    assert body["issues"][0]["severity"] == "critical"
    # Fix suggestion populated
    assert len(body["issues"][0]["suggested_fix"]) > 0


def test_create_report_fix_keyword_null(client):
    r = client.post("/api/debugging/report", json={
        "title": "Null Check Report",
        "issues": [{"title": "null pointer exception", "description": "", "severity": "critical"}]
    })
    fix = r.json()["issues"][0]["suggested_fix"]
    assert "null" in fix.lower() or "None" in fix or "guard" in fix.lower()


def test_list_reports(client):
    client.post("/api/debugging/report", json={
        "title": "List Test", "issues": [{"title": "X", "severity": "minor"}]
    })
    r = client.get("/api/debugging/reports")
    assert r.status_code == 200
    assert len(r.json()["reports"]) >= 1


def test_get_report_happy(client):
    r = client.post("/api/debugging/report", json={
        "title": "Get Test", "issues": [{"title": "Y", "severity": "major"}]
    })
    rid = r.json()["id"]
    r2 = client.get(f"/api/debugging/reports/{rid}")
    assert r2.status_code == 200
    assert r2.json()["id"] == rid


def test_get_report_not_found(client):
    r = client.get("/api/debugging/reports/99999")
    assert r.status_code == 404


def test_create_report_empty_issues(client):
    r = client.post("/api/debugging/report", json={"title": "Empty", "issues": []})
    # Should succeed (empty issues list is valid)
    assert r.status_code == 201
    assert r.json()["issues"] == []
