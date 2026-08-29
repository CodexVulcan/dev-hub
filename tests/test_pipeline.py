"""Tests for /api/pipeline router."""


def test_list_projects_empty(client):
    r = client.get("/api/pipeline/projects")
    assert r.status_code == 200
    # Other tests may have created projects already (shared DB); just verify shape
    assert isinstance(r.json()["projects"], list)


def test_add_project_happy(client):
    r = client.post("/api/pipeline/projects", json={"name": "proj-alpha", "description": "Test project"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "proj-alpha"
    # All 3 default stages created
    stages = {s["stage"]: s["status"] for s in body["stages"]}
    assert set(stages.keys()) == {"build", "test", "deploy"}
    assert all(s == "pending" for s in stages.values())


def test_add_project_duplicate(client):
    client.post("/api/pipeline/projects", json={"name": "proj-dup"})
    r = client.post("/api/pipeline/projects", json={"name": "proj-dup"})
    assert r.status_code == 409


def test_update_stage_happy(client):
    r = client.post("/api/pipeline/projects", json={"name": "proj-stage-test"})
    pid = r.json()["id"]
    r2 = client.patch(f"/api/pipeline/projects/{pid}/stage", json={"stage": "build", "status": "passing"})
    assert r2.status_code == 200
    stages = {s["stage"]: s["status"] for s in r2.json()["stages"]}
    assert stages["build"] == "passing"


def test_update_stage_project_not_found(client):
    r = client.patch("/api/pipeline/projects/99999/stage", json={"stage": "build", "status": "passing"})
    assert r.status_code == 404


def test_github_sync_missing_owner_repo(client):
    r = client.post("/api/pipeline/projects", json={"name": "proj-nosync"})
    pid = r.json()["id"]
    r2 = client.get(f"/api/pipeline/projects/{pid}/github-sync")
    assert r2.status_code == 200
    assert r2.json()["reason"] == "owner_or_repo_missing"


def test_github_sync_project_not_found(client):
    r = client.get("/api/pipeline/projects/99999/github-sync")
    assert r.status_code == 404
