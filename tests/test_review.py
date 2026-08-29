"""Tests for /api/review router."""


def test_summarize_happy(client):
    r = client.post("/api/review/summarize", json={
        "changes_text": "security: patch CVE-2024-1234\nfix: null pointer in auth\ndocs: update README"
    })
    assert r.status_code == 201
    body = r.json()
    assert "items" in body
    assert len(body["items"]) == 3
    priorities = [i["priority"] for i in body["items"]]
    # security line should be high
    assert "high" in priorities


def test_summarize_priority_order(client):
    r = client.post("/api/review/summarize", json={
        "changes_text": "docs: cleanup\nfix: crash on startup\nsecurity: auth bypass vulnerability"
    })
    items = r.json()["items"]
    # Items sorted high -> medium -> low
    order = {"high": 0, "medium": 1, "low": 2}
    orders = [order[i["priority"]] for i in items]
    assert orders == sorted(orders)


def test_summarize_empty_text(client):
    r = client.post("/api/review/summarize", json={"changes_text": "   "})
    assert r.status_code == 422


def test_history_after_summarize(client):
    client.post("/api/review/summarize", json={"changes_text": "feat: add new endpoint"})
    r = client.get("/api/review/history")
    assert r.status_code == 200
    assert len(r.json()["history"]) >= 1


def test_summarize_category_detection(client):
    r = client.post("/api/review/summarize", json={
        "changes_text": "feat: implement user dashboard"
    })
    items = r.json()["items"]
    assert any(i["category"] == "feature" for i in items)
