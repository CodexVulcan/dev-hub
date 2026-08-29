"""Tests for /api/maintenance router."""
from datetime import date, timedelta


def test_list_tasks_empty(client):
    r = client.get("/api/maintenance/tasks")
    assert r.status_code == 200
    assert r.json()["tasks"] == []


def test_create_task_happy(client):
    future = (date.today() + timedelta(days=30)).isoformat()
    r = client.post("/api/maintenance/tasks", json={
        "title": "Update deps", "category": "dependency_update",
        "due_date": future, "recurrence": "monthly"
    })
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Update deps"
    assert body["overdue"] is False


def test_overdue_flag(client):
    past = (date.today() - timedelta(days=5)).isoformat()
    r = client.post("/api/maintenance/tasks", json={
        "title": "Overdue task", "category": "security_patch",
        "due_date": past, "recurrence": "none"
    })
    assert r.json()["overdue"] is True


def test_complete_task(client):
    future = (date.today() + timedelta(days=10)).isoformat()
    r = client.post("/api/maintenance/tasks", json={
        "title": "Complete me", "category": "other",
        "due_date": future, "recurrence": "none"
    })
    tid = r.json()["id"]
    r2 = client.patch(f"/api/maintenance/tasks/{tid}", json={"status": "completed"})
    assert r2.status_code == 200
    assert r2.json()["status"] == "completed"
    assert r2.json()["overdue"] is False


def test_update_task_not_found(client):
    r = client.patch("/api/maintenance/tasks/99999", json={"status": "completed"})
    assert r.status_code == 404


def test_delete_task_happy(client):
    future = (date.today() + timedelta(days=7)).isoformat()
    r = client.post("/api/maintenance/tasks", json={
        "title": "Delete me", "category": "other",
        "due_date": future, "recurrence": "none"
    })
    tid = r.json()["id"]
    r2 = client.delete(f"/api/maintenance/tasks/{tid}")
    assert r2.status_code == 204


def test_delete_task_not_found(client):
    r = client.delete("/api/maintenance/tasks/99999")
    assert r.status_code == 404
