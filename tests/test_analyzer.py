"""Tests for /api/analyzer router."""


def test_analyze_python_project(client):
    r = client.post("/api/analyzer/analyze", json={
        "file_listing": "requirements.txt\nbackend/main.py\nDockerfile\n.github/workflows/ci.yml",
        "tech_hints": ""
    })
    assert r.status_code == 200
    body = r.json()
    assert "Python" in body["stack_summary"]
    assert "Docker" in body["stack_summary"]
    assert isinstance(body["tool_suggestions"], list)
    assert len(body["tool_suggestions"]) > 0


def test_analyze_node_project(client):
    r = client.post("/api/analyzer/analyze", json={
        "file_listing": "package.json\nsrc/index.js\ntsconfig.json",
        "tech_hints": "uses React"
    })
    assert r.status_code == 200
    body = r.json()
    assert any("Node" in s for s in body["stack_summary"])


def test_analyze_empty_listing(client):
    r = client.post("/api/analyzer/analyze", json={"file_listing": "   ", "tech_hints": ""})
    assert r.status_code == 200
    body = r.json()
    # Should return unknown stack, not crash
    assert isinstance(body["stack_summary"], list)
    assert len(body["stack_summary"]) > 0


def test_analyze_missing_body(client):
    r = client.post("/api/analyzer/analyze", json={})
    assert r.status_code == 422
