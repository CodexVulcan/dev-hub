"""Tests for /api/mindmap router."""


def test_get_empty_mindmap(client):
    r = client.get("/api/mindmap")
    assert r.status_code == 200
    body = r.json()
    assert body["nodes"] == []
    assert body["edges"] == []


def test_add_node_happy(client):
    r = client.post("/api/mindmap/nodes", json={"id": "n1", "label": "Auth", "type": "service", "x": 100, "y": 100})
    assert r.status_code == 201
    assert r.json()["id"] == "n1"


def test_add_node_duplicate_id(client):
    client.post("/api/mindmap/nodes", json={"id": "dup-node", "label": "A", "type": "module", "x": 0, "y": 0})
    r = client.post("/api/mindmap/nodes", json={"id": "dup-node", "label": "B", "type": "module", "x": 0, "y": 0})
    assert r.status_code == 409


def test_add_edge_happy(client):
    client.post("/api/mindmap/nodes", json={"id": "e-src", "label": "Src", "type": "service", "x": 0, "y": 0})
    client.post("/api/mindmap/nodes", json={"id": "e-tgt", "label": "Tgt", "type": "database", "x": 100, "y": 0})
    r = client.post("/api/mindmap/edges", json={"source": "e-src", "target": "e-tgt", "label": "calls"})
    assert r.status_code == 201
    assert r.json()["source"] == "e-src"


def test_add_edge_missing_source(client):
    client.post("/api/mindmap/nodes", json={"id": "only-tgt", "label": "T", "type": "module", "x": 0, "y": 0})
    r = client.post("/api/mindmap/edges", json={"source": "nonexistent", "target": "only-tgt", "label": ""})
    assert r.status_code == 404


def test_update_node_position(client):
    client.post("/api/mindmap/nodes", json={"id": "move-me", "label": "M", "type": "component", "x": 10, "y": 10})
    r = client.patch("/api/mindmap/nodes/move-me?x=250.0&y=300.0")
    assert r.status_code == 200
    body = r.json()
    assert body["x"] == 250.0
    assert body["y"] == 300.0


def test_delete_node_happy(client):
    client.post("/api/mindmap/nodes", json={"id": "del-me", "label": "D", "type": "external", "x": 0, "y": 0})
    r = client.delete("/api/mindmap/nodes/del-me")
    assert r.status_code == 204


def test_delete_node_not_found(client):
    r = client.delete("/api/mindmap/nodes/ghost-node")
    assert r.status_code == 404
