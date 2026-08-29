"""Tests for /api/pulse router (Team Health Score)."""


def test_pulse_score_empty_db(client):
    r = client.get("/api/pulse/score")
    assert r.status_code == 200
    body = r.json()
    assert "overall" in body
    assert "grade" in body
    assert "dimensions" in body
    assert 0 <= body["overall"] <= 100
    assert body["grade"] in ("A", "B", "C", "D", "F")


def test_pulse_all_dimensions_present(client):
    r = client.get("/api/pulse/score")
    dims = r.json()["dimensions"]
    assert set(dims.keys()) == {"pipeline", "quality", "team", "maintenance", "activity"}


def test_pulse_feed_empty(client):
    r = client.get("/api/pulse/feed")
    assert r.status_code == 200
    assert "events" in r.json()


def test_pulse_combined_endpoint(client):
    r = client.get("/api/pulse")
    assert r.status_code == 200
    body = r.json()
    assert "overall" in body
    assert "feed" in body


def test_pulse_score_improves_with_passing_pipeline(client):
    score_before = client.get("/api/pulse/score").json()["overall"]
    # Add a project with all passing stages
    r = client.post("/api/pipeline/projects", json={"name": "pulse-green-proj"})
    pid = r.json()["id"]
    for stage in ["build", "test", "deploy"]:
        client.patch(f"/api/pipeline/projects/{pid}/stage",
                     json={"stage": stage, "status": "passing"})
    score_after = client.get("/api/pulse/score").json()["overall"]
    assert score_after >= score_before


def test_pulse_feed_shows_pipeline_events(client):
    client.post("/api/pipeline/projects", json={"name": "pulse-feed-proj"})
    r = client.get("/api/pulse/feed")
    events = r.json()["events"]
    types = [e["type"] for e in events]
    assert "pipeline" in types
