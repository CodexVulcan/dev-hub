"""Tests for /api/dashboard router."""


def test_list_cards_empty(client):
    r = client.get("/api/dashboard/cards")
    assert r.status_code == 200
    assert r.json()["cards"] == []


def test_create_card_happy(client):
    r = client.post("/api/dashboard/cards", json={
        "title": "Idea 1", "body": "Details", "color": "#fffacd",
        "x": 50, "y": 50, "author": "alice"
    })
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Idea 1"
    assert "id" in body


def test_update_card_position(client):
    r = client.post("/api/dashboard/cards", json={"title": "Move Me", "x": 0, "y": 0, "author": "bob"})
    cid = r.json()["id"]
    r2 = client.patch(f"/api/dashboard/cards/{cid}", json={"x": 200, "y": 300})
    assert r2.status_code == 200
    assert r2.json()["x"] == 200


def test_update_card_not_found(client):
    r = client.patch("/api/dashboard/cards/nonexistent-id", json={"title": "X"})
    assert r.status_code == 404


def test_add_comment_happy(client):
    r = client.post("/api/dashboard/cards", json={"title": "Commentable", "author": "carol"})
    cid = r.json()["id"]
    r2 = client.post(f"/api/dashboard/cards/{cid}/comments", json={"text": "Great idea!", "author": "dave"})
    assert r2.status_code == 201
    assert r2.json()["text"] == "Great idea!"


def test_add_comment_card_not_found(client):
    r = client.post("/api/dashboard/cards/bad-id/comments", json={"text": "Hmm", "author": "eve"})
    assert r.status_code == 404


def test_delete_card_happy(client):
    r = client.post("/api/dashboard/cards", json={"title": "Delete Me", "author": "frank"})
    cid = r.json()["id"]
    r2 = client.delete(f"/api/dashboard/cards/{cid}")
    assert r2.status_code == 204


def test_delete_card_not_found(client):
    r = client.delete("/api/dashboard/cards/ghost-id")
    assert r.status_code == 404
