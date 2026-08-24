import os

os.environ["DATABASE_URL"] = "sqlite:///./test_knowledge_hub.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def register_and_login():
    register = client.post(
        "/api/auth/register",
        json={"username": "holmes", "email": "holmes@example.com", "password": "password123"},
    )
    assert register.status_code == 201
    login = client.post(
        "/api/auth/login",
        data={"username": "holmes", "password": "password123"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_login_and_get_current_user():
    headers = register_and_login()
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "holmes"
    assert response.json()["role"] == "user"


def test_user_can_create_update_search_and_change_learning_status():
    headers = register_and_login()
    created = client.post(
        "/api/notes",
        headers=headers,
        json={
            "title": "Python 入门",
            "summary": "我的 Python 学习笔记",
            "content": "变量、函数和 Python 数据结构",
            "tags": ["Python", "计算机"],
        },
    )
    assert created.status_code == 201
    note = created.json()
    assert note["status"] == "unlearned"
    assert {tag["name"] for tag in note["tags"]} == {"Python", "计算机"}

    updated = client.patch(
        f"/api/notes/{note['id']}",
        headers=headers,
        json={"status": "completed", "content": "函数、数据结构和异常处理"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "completed"

    searched = client.get("/api/notes", headers=headers, params={"q": "异常处理"})
    assert searched.status_code == 200
    assert searched.json()["total"] == 1


def test_user_cannot_read_another_users_private_note():
    owner_headers = register_and_login()
    created = client.post(
        "/api/notes",
        headers=owner_headers,
        json={"title": "Private", "content": "secret"},
    )
    assert created.status_code == 201

    client.post(
        "/api/auth/register",
        json={"username": "other", "email": "other@example.com", "password": "password123"},
    )
    login = client.post("/api/auth/login", data={"username": "other", "password": "password123"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.get(f"/api/notes/{created.json()['id']}", headers=other_headers)
    assert response.status_code == 404
