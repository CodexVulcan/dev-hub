"""Tests for /api/teams router."""
import pytest


def test_list_members_empty(client):
    r = client.get("/api/teams/members")
    assert r.status_code == 200
    assert r.json()["members"] == []


def test_add_member_happy(client):
    r = client.post("/api/teams/members", json={"name": "Alice", "email": "alice@test.com", "role": "lead"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Alice"
    assert body["role"] == "lead"
    assert "id" in body


def test_list_members_after_add(client):
    client.post("/api/teams/members", json={"name": "Bob", "email": "bob@test.com", "role": "developer"})
    r = client.get("/api/teams/members")
    names = [m["name"] for m in r.json()["members"]]
    assert "Bob" in names


def test_add_member_duplicate_email(client):
    client.post("/api/teams/members", json={"name": "Carol", "email": "carol@test.com", "role": "tester"})
    r = client.post("/api/teams/members", json={"name": "Carol2", "email": "carol@test.com", "role": "tester"})
    assert r.status_code == 409


def test_update_role_happy(client):
    r = client.post("/api/teams/members", json={"name": "Dave", "email": "dave@test.com", "role": "developer"})
    mid = r.json()["id"]
    r2 = client.patch(f"/api/teams/members/{mid}/role", json={"role": "reviewer"})
    assert r2.status_code == 200
    assert r2.json()["role"] == "reviewer"


def test_update_role_not_found(client):
    r = client.patch("/api/teams/members/99999/role", json={"role": "lead"})
    assert r.status_code == 404


def test_remove_member_happy(client):
    r = client.post("/api/teams/members", json={"name": "Eve", "email": "eve@test.com", "role": "tester"})
    mid = r.json()["id"]
    r2 = client.delete(f"/api/teams/members/{mid}")
    assert r2.status_code == 204


def test_remove_member_not_found(client):
    r = client.delete("/api/teams/members/99999")
    assert r.status_code == 404
