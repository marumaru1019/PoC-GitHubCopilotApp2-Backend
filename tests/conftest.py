import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.core.deps import get_db
from app.models.user import User
from app.models.team import Team
from app.models.category import Category
from app.models.tag import Tag
from app.models.sla_settings import SLASettings
from app.core.security import get_password_hash

# テスト用インメモリSQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """各テスト関数ごとに新しいDBセッションを作成"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """テストクライアントを提供"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_team(db_session):
    """テスト用チーム"""
    import uuid
    team = Team(
        id=str(uuid.uuid4()),
        name="Test Team",
        description="Team for testing"
    )
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    return team


@pytest.fixture(scope="function")
def test_user(db_session, test_team):
    """テスト用一般ユーザー"""
    import uuid
    user = User(
        id=str(uuid.uuid4()),
        email="user@example.com",
        name="Test User",
        password_hash=get_password_hash("testpass123"),
        role="requester",
        team_id=test_team.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_operator(db_session, test_team):
    """テスト用オペレーター"""
    import uuid
    operator = User(
        id=str(uuid.uuid4()),
        email="operator@example.com",
        name="Test Operator",
        password_hash=get_password_hash("testpass123"),
        role="operator",
        team_id=test_team.id
    )
    db_session.add(operator)
    db_session.commit()
    db_session.refresh(operator)
    return operator


@pytest.fixture(scope="function")
def test_admin(db_session, test_team):
    """テスト用管理者"""
    import uuid
    admin = User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        name="Test Admin",
        password_hash=get_password_hash("testpass123"),
        role="admin",
        team_id=test_team.id
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def auth_headers_user(client, test_user):
    """一般ユーザーの認証ヘッダー"""
    response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_operator(client, test_operator):
    """オペレーターの認証ヘッダー"""
    response = client.post(
        "/api/auth/login",
        json={"email": "operator@example.com", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin(client, test_admin):
    """管理者の認証ヘッダー"""
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_category(db_session):
    """テスト用カテゴリ"""
    import uuid
    category = Category(
        id=str(uuid.uuid4()),
        name="Test Category",
        description="Category for testing",
        type="BOTH"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture(scope="function")
def test_tag(db_session):
    """テスト用タグ"""
    import uuid
    tag = Tag(
        id=str(uuid.uuid4()),
        name="test-tag"
    )
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


@pytest.fixture(scope="function")
def test_sla_settings(db_session):
    """テスト用SLA設定"""
    import uuid
    sla_settings = [
        SLASettings(id=str(uuid.uuid4()), priority="LOW", first_response_target_minutes=480, resolution_target_minutes=2880),
        SLASettings(id=str(uuid.uuid4()), priority="MEDIUM", first_response_target_minutes=240, resolution_target_minutes=1440),
        SLASettings(id=str(uuid.uuid4()), priority="HIGH", first_response_target_minutes=60, resolution_target_minutes=480),
        SLASettings(id=str(uuid.uuid4()), priority="URGENT", first_response_target_minutes=15, resolution_target_minutes=240),
    ]
    for sla in sla_settings:
        db_session.add(sla)
    db_session.commit()
    return sla_settings
