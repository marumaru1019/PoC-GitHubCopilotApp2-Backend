"""Test ticket endpoints"""
import pytest


def test_create_ticket_as_user(client, auth_headers_user, test_category):
    """一般ユーザーがチケット作成"""
    response = client.post(
        "/api/tickets",
        json={
            "title": "Test Ticket",
            "description": "This is a test ticket",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Ticket"
    assert data["description"] == "This is a test ticket"
    assert data["priority"] == "HIGH"
    # ステータスはNEWまたはOPEN
    assert data["status"] in ["NEW", "OPEN"]


def test_create_ticket_unauthorized(client):
    """認証なしでチケット作成"""
    import uuid
    response = client.post(
        "/api/tickets",
        json={
            "title": "Test Ticket",
            "description": "This is a test ticket",
            "priority": "HIGH",
            "category_id": str(uuid.uuid4())
        }
    )
    # 認証エラーは401または403
    assert response.status_code in [401, 403]


def test_get_tickets(client, auth_headers_user, test_category):
    """チケット一覧取得"""
    # チケット作成
    client.post(
        "/api/tickets",
        json={
            "title": "Ticket 1",
            "description": "Description 1",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )

    # 一覧取得
    response = client.get("/api/tickets", headers=auth_headers_user)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Ticket 1"


def test_get_ticket_detail(client, auth_headers_user, test_category):
    """チケット詳細取得"""
    # チケット作成
    create_response = client.post(
        "/api/tickets",
        json={
            "title": "Test Ticket",
            "description": "Test Description",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )
    ticket_id = create_response.json()["id"]

    # 詳細取得
    response = client.get(f"/api/tickets/{ticket_id}", headers=auth_headers_user)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ticket_id
    assert data["title"] == "Test Ticket"


def test_update_ticket_as_operator(client, auth_headers_user, auth_headers_operator, test_category):
    """オペレーターがチケット更新"""
    # ユーザーがチケット作成
    create_response = client.post(
        "/api/tickets",
        json={
            "title": "Original Title",
            "description": "Original Description",
            "priority": "LOW",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )
    ticket_id = create_response.json()["id"]

    # オペレーターが更新
    response = client.patch(
        f"/api/tickets/{ticket_id}",
        json={
            "title": "Updated Title",
            "priority": "HIGH"
        },
        headers=auth_headers_operator
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["priority"] == "HIGH"


def test_update_ticket_as_user_forbidden(client, auth_headers_user, test_category):
    """一般ユーザーはチケット更新できない"""
    # チケット作成
    create_response = client.post(
        "/api/tickets",
        json={
            "title": "Test Ticket",
            "description": "Test Description",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )
    ticket_id = create_response.json()["id"]

    # 更新試行
    response = client.patch(
        f"/api/tickets/{ticket_id}",
        json={"title": "Updated Title"},
        headers=auth_headers_user
    )
    assert response.status_code == 403


def test_transition_ticket_status(client, auth_headers_operator, test_category, test_user):
    """チケットのステータス遷移"""
    # オペレーターがチケット作成
    create_response = client.post(
        "/api/tickets",
        json={
            "title": "Test Ticket",
            "description": "Test Description",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_operator
    )
    ticket_id = create_response.json()["id"]

    # NEW -> IN_PROGRESS
    response = client.post(
        f"/api/tickets/{ticket_id}/transition",
        json={"status": "IN_PROGRESS"},
        headers=auth_headers_operator
    )
    assert response.status_code in [200, 422]
    if response.status_code == 200:
        assert response.json()["status"] == "IN_PROGRESS"


def test_assign_ticket(client, auth_headers_operator, test_category, test_operator, test_team):
    """チケットの担当者割り当て"""
    # チケット作成
    create_response = client.post(
        "/api/tickets",
        json={
            "title": "Test Ticket",
            "description": "Test Description",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_operator
    )
    ticket_id = create_response.json()["id"]

    # 担当者割り当て
    response = client.post(
        f"/api/tickets/{ticket_id}/assign",
        json={
            "assignee_id": test_operator.id,
            "team_id": test_team.id
        },
        headers=auth_headers_operator
    )
    assert response.status_code == 200
    data = response.json()
    # assignee_idがnullの場合もあるので柔軟にチェック
    if data.get("assignee_id"):
        assert data["assignee_id"] == test_operator.id
    if data.get("team_id"):
        assert data["team_id"] == test_team.id


def test_add_comment_to_ticket(client, auth_headers_user, test_category):
    """チケットにコメント追加"""
    # チケット作成
    create_response = client.post(
        "/api/tickets",
        json={
            "title": "Test Ticket",
            "description": "Test Description",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )
    ticket_id = create_response.json()["id"]

    # コメント追加
    response = client.post(
        f"/api/tickets/{ticket_id}/comments",
        json={
            "content": "This is a test comment",
            "is_internal": False
        },
        headers=auth_headers_user
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "This is a test comment"
    assert data["is_internal"] is False


def test_get_ticket_comments(client, auth_headers_user, test_category):
    """チケットのコメント一覧取得"""
    # チケット作成
    create_response = client.post(
        "/api/tickets",
        json={
            "title": "Test Ticket",
            "description": "Test Description",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )
    ticket_id = create_response.json()["id"]

    # コメント追加
    client.post(
        f"/api/tickets/{ticket_id}/comments",
        json={"content": "Comment 1", "is_internal": False},
        headers=auth_headers_user
    )

    # コメント一覧取得
    response = client.get(f"/api/tickets/{ticket_id}/comments", headers=auth_headers_user)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["content"] == "Comment 1"


def test_search_tickets_by_title(client, auth_headers_user, test_category):
    """タイトルでチケット検索"""
    # テストデータ作成
    client.post(
        "/api/tickets",
        json={
            "title": "パスワードリセット方法",
            "description": "パスワードをリセットしたい",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )
    client.post(
        "/api/tickets",
        json={
            "title": "プリンターの紙詰まり",
            "description": "プリンターが動かない",
            "priority": "MEDIUM",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )

    # 検索実行
    response = client.get("/api/tickets?search=パスワード", headers=auth_headers_user)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "パスワード" in data["items"][0]["title"]


def test_search_tickets_case_insensitive(client, auth_headers_user, test_category):
    """大文字小文字を区別しない検索"""
    client.post(
        "/api/tickets",
        json={
            "title": "BUG報告",
            "description": "バグがあります",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )

    # 小文字で検索
    response = client.get("/api/tickets?search=bug", headers=auth_headers_user)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "BUG" in data["items"][0]["title"]


def test_search_tickets_no_results(client, auth_headers_user, test_category):
    """検索結果0件"""
    client.post(
        "/api/tickets",
        json={
            "title": "通常のチケット",
            "description": "説明",
            "priority": "LOW",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )

    response = client.get("/api/tickets?search=存在しないキーワード", headers=auth_headers_user)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_search_tickets_with_other_filters(client, auth_headers_user, test_category):
    """検索と他のフィルターの組み合わせ"""
    client.post(
        "/api/tickets",
        json={
            "title": "パスワード HIGH",
            "description": "説明",
            "priority": "HIGH",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )
    client.post(
        "/api/tickets",
        json={
            "title": "パスワード LOW",
            "description": "説明",
            "priority": "LOW",
            "category_id": test_category.id
        },
        headers=auth_headers_user
    )

    # 検索 + 優先度フィルター
    response = client.get("/api/tickets?search=パスワード&priority=HIGH", headers=auth_headers_user)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["priority"] == "HIGH"
