import os

os.environ["DATABASE_URL"] = "sqlite:///./test_knowledge_hub.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import User, UserRole
from sqlalchemy import select


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


def test_user_can_upload_and_delete_an_allowed_attachment():
    headers = register_and_login()
    created = client.post("/api/notes", headers=headers, json={"title": "Attachments", "content": "notes"})
    note_id = created.json()["id"]

    uploaded = client.post(
        f"/api/notes/{note_id}/files",
        headers=headers,
        files={"file": ("diagram.png", b"fake-png-content", "image/png")},
    )
    assert uploaded.status_code == 201
    attachment = uploaded.json()
    assert attachment["filename"] == "diagram.png"
    assert attachment["file_size"] == len(b"fake-png-content")

    listed = client.get(f"/api/notes/{note_id}/files", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = client.delete(f"/api/notes/{note_id}/files/{attachment['id']}", headers=headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/notes/{note_id}/files", headers=headers).json() == []


def test_upload_rejects_disallowed_file_extensions():
    headers = register_and_login()
    created = client.post("/api/notes", headers=headers, json={"title": "Attachments"})
    response = client.post(
        f"/api/notes/{created.json()['id']}/files",
        headers=headers,
        files={"file": ("payload.exe", b"not allowed", "application/octet-stream")},
    )
    assert response.status_code == 415


def promote_current_user_to_admin(username: str) -> None:
    db = SessionLocal()
    user = db.scalar(select(User).where(User.username == username))
    assert user is not None
    user.role = UserRole.ADMIN
    db.commit()
    db.close()


def test_public_note_comments_require_moderation_and_admin_can_approve():
    owner_headers = register_and_login()
    created = client.post("/api/notes", headers=owner_headers, json={"title": "Public RAG", "content": "RAG notes"})
    note_id = created.json()["id"]
    published = client.patch(f"/api/notes/{note_id}", headers=owner_headers, json={"is_public": True})
    assert published.status_code == 200

    public_note = client.get(f"/api/public/notes/{note_id}")
    assert public_note.status_code == 200
    assert public_note.json()["views"] == 1

    comment = client.post(
        f"/api/public/notes/{note_id}/comments",
        json={"nickname": "Guest", "email": "guest@example.com", "content": "很有帮助"},
    )
    assert comment.status_code == 201
    assert comment.json()["status"] == "pending"

    client.post("/api/auth/register", json={"username": "admin", "email": "admin@example.com", "password": "password123"})
    login = client.post("/api/auth/login", data={"username": "admin", "password": "password123"})
    admin_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    promote_current_user_to_admin("admin")
    moderated = client.patch(f"/api/admin/comments/{comment.json()['id']}", headers=admin_headers, json={"status": "approved"})
    assert moderated.status_code == 200
    assert moderated.json()["status"] == "approved"


def test_user_can_toggle_favorite_and_non_admin_cannot_moderate():
    headers = register_and_login()
    created = client.post("/api/notes", headers=headers, json={"title": "Favorite"})
    note_id = created.json()["id"]
    favorited = client.post(f"/api/notes/{note_id}/favorite", headers=headers)
    assert favorited.status_code == 201
    assert client.get("/api/favorites", headers=headers).json()[0]["id"] == note_id
    assert client.delete(f"/api/notes/{note_id}/favorite", headers=headers).status_code == 204
    assert client.get("/api/favorites", headers=headers).json() == []
    assert client.patch("/api/admin/comments/1", headers=headers, json={"status": "approved"}).status_code == 403
