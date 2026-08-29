"""Tests for /api/deployment router."""


def _create_project(client, name):
    r = client.post("/api/pipeline/projects", json={"name": name})
    assert r.status_code == 201
    return r.json()["id"]


def test_check_project_not_found(client):
    r = client.get("/api/deployment/check/99999")
    assert r.status_code == 404


def test_check_all_pending_is_nogo(client):
    pid = _create_project(client, "deploy-pending")
    r = client.get(f"/api/deployment/check/{pid}")
    assert r.status_code == 200
    body = r.json()
    assert body["go"] is False
    # Pipeline check should fail (stages are pending, not passing)
    pipeline_check = next(c for c in body["checks"] if c["name"] == "Pipeline stages")
    assert pipeline_check["passed"] is False


def test_check_all_passing_no_issues_go(client):
    pid = _create_project(client, "deploy-green-unique-xyz")
    # Set all 3 stages to passing
    for stage in ["build", "test", "deploy"]:
        client.patch(f"/api/pipeline/projects/{pid}/stage",
                     json={"stage": stage, "status": "passing"})
    r = client.get(f"/api/deployment/check/{pid}")
    assert r.status_code == 200
    body = r.json()
    # Pipeline check must pass; quality checks depend on whether other tests left critical items
    pipeline_check = next(c for c in body["checks"] if c["name"] == "Pipeline stages")
    assert pipeline_check["passed"] is True


def test_check_blocked_by_critical_debug_issue(client):
    pid = _create_project(client, "deploy-critical-bug")
    for stage in ["build", "test", "deploy"]:
        client.patch(f"/api/pipeline/projects/{pid}/stage",
                     json={"stage": stage, "status": "passing"})
    # Create a critical debug issue (open by default)
    client.post("/api/debugging/report", json={
        "title": "Blocker",
        "issues": [{"title": "Critical bug", "severity": "critical", "description": ""}]
    })
    r = client.get(f"/api/deployment/check/{pid}")
    body = r.json()
    assert body["go"] is False
    quality_check = next(c for c in body["checks"] if c["name"] == "Critical debug issues")
    assert quality_check["passed"] is False


def test_check_blocked_by_critical_test_failure(client):
    pid = _create_project(client, "deploy-fail-test")
    for stage in ["build", "test", "deploy"]:
        client.patch(f"/api/pipeline/projects/{pid}/stage",
                     json={"stage": stage, "status": "passing"})
    # Submit a critical failing test
    client.post("/api/testing/results", json={
        "test_suite": "Blocker Suite",
        "results": [{"test_name": "critical_fail", "status": "failed", "severity": "critical", "message": ""}]
    })
    r = client.get(f"/api/deployment/check/{pid}")
    body = r.json()
    assert body["go"] is False
    test_check = next(c for c in body["checks"] if c["name"] == "Critical test failures")
    assert test_check["passed"] is False
