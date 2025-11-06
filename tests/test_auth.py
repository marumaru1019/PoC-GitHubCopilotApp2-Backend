"""Test auth endpoints"""
import pytest


def test_login_success(client, test_user):
    """正常なログインテスト"""
    response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_email(client, test_user):
    """存在しないメールアドレスでのログイン"""
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "testpass123"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_invalid_password(client, test_user):
    """間違ったパスワードでのログイン"""
    response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user(client, auth_headers_user, test_user):
    """現在のユーザー情報取得"""
    response = client.get("/api/auth/me", headers=auth_headers_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["name"] == "Test User"
    assert data["role"] == "requester"


def test_get_current_user_unauthorized(client):
    """認証なしでユーザー情報取得"""
    response = client.get("/api/auth/me")
    # 認証エラーは401または403
    assert response.status_code in [401, 403]


def test_logout(client, auth_headers_user):
    """ログアウトテスト"""
    response = client.post("/api/auth/logout", headers=auth_headers_user)
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"
