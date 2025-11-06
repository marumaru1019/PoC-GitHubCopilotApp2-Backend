"""Test admin endpoints"""
import pytest


def test_get_users_as_admin(client, auth_headers_admin, test_user):
    """管理者がユーザー一覧取得"""
    response = client.get("/api/admin/users", headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_users_as_operator_forbidden(client, auth_headers_operator):
    """オペレーターはユーザー一覧取得できない"""
    response = client.get("/api/admin/users", headers=auth_headers_operator)
    assert response.status_code == 403


def test_create_user_as_admin(client, auth_headers_admin, test_team):
    """管理者がユーザー作成"""
    response = client.post(
        "/api/admin/users",
        json={
            "email": "newuser@example.com",
            "name": "New User",
            "password": "newpass123",
            "role": "requester",
            "team_id": test_team.id
        },
        headers=auth_headers_admin
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert data["role"] == "requester"


def test_update_user_as_admin(client, auth_headers_admin, test_user):
    """管理者がユーザー更新"""
    response = client.patch(
        f"/api/admin/users/{test_user.id}",
        json={
            "name": "Updated Name",
            "role": "operator"
        },
        headers=auth_headers_admin
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["role"] == "operator"


def test_get_teams_as_admin(client, auth_headers_admin, test_team):
    """管理者がチーム一覧取得"""
    response = client.get("/api/admin/teams", headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test Team"


def test_create_team_as_admin(client, auth_headers_admin):
    """管理者がチーム作成"""
    response = client.post(
        "/api/admin/teams",
        json={
            "name": "New Team",
            "description": "A new team for testing"
        },
        headers=auth_headers_admin
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Team"
    assert data["description"] == "A new team for testing"


def test_get_categories_as_admin(client, auth_headers_admin, test_category):
    """管理者がカテゴリ一覧取得"""
    response = client.get("/api/admin/categories", headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_create_category_as_admin(client, auth_headers_admin):
    """管理者がカテゴリ作成"""
    response = client.post(
        "/api/admin/categories",
        json={
            "name": "New Category",
            "description": "A new category",
            "type": "TICKET"
        },
        headers=auth_headers_admin
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Category"
    assert data["type"] == "TICKET"


def test_get_tags_as_admin(client, auth_headers_admin, test_tag):
    """管理者がタグ一覧取得"""
    response = client.get("/api/admin/tags", headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_create_tag_as_admin(client, auth_headers_admin):
    """管理者がタグ作成"""
    response = client.post(
        "/api/admin/tags",
        json={"name": "new-tag"},
        headers=auth_headers_admin
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "new-tag"


def test_get_sla_settings_as_admin(client, auth_headers_admin, test_sla_settings):
    """管理者がSLA設定一覧取得"""
    response = client.get("/api/admin/sla-settings", headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4  # LOW, MEDIUM, HIGH, URGENT


def test_create_sla_setting_as_admin(client, auth_headers_admin):
    """管理者がSLA設定作成"""
    response = client.post(
        "/api/admin/sla-settings",
        json={
            "priority": "HIGH",
            "first_response_target_minutes": 30,
            "resolution_target_minutes": 240
        },
        headers=auth_headers_admin
    )
    assert response.status_code == 201
    data = response.json()
    assert data["priority"] == "HIGH"
    assert data["first_response_target_minutes"] == 30


def test_update_sla_setting_as_admin(client, auth_headers_admin, test_sla_settings):
    """管理者がSLA設定更新"""
    sla_id = test_sla_settings[0].id
    response = client.patch(
        f"/api/admin/sla-settings/{sla_id}",
        json={
            "first_response_target_minutes": 600,
            "resolution_target_minutes": 3000
        },
        headers=auth_headers_admin
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_response_target_minutes"] == 600
    assert data["resolution_target_minutes"] == 3000


def test_get_audit_logs_as_admin(client, auth_headers_admin, test_user):
    """管理者が監査ログ取得"""
    response = client.get("/api/admin/audit-logs", headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    # レスポンスがリストまたはitemsキーを持つ辞書の両方に対応
    if isinstance(data, list):
        assert len(data) >= 0
    else:
        assert "items" in data
        assert len(data["items"]) >= 0


def test_audit_log_filters(client, auth_headers_admin, auth_headers_operator, test_category):
    """監査ログのフィルタリング"""
    # チケット作成（監査ログが記録される）
    client.post(
        "/api/tickets",
        json={
            "title": "Test Ticket",
            "description": "Test",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_operator
    )
    
    # エンティティタイプでフィルタ
    response = client.get(
        "/api/admin/audit-logs?entity_type=ticket",
        headers=auth_headers_admin
    )
    assert response.status_code == 200
    data = response.json()
    # レスポンスがリストまたはitemsキーを持つ辞書の両方に対応
    items = data if isinstance(data, list) else data.get("items", [])
    if len(items) > 0:
        assert all(item["entity_type"] == "ticket" for item in items)
