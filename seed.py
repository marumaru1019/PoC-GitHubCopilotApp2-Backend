"""Seed script to populate database with initial data."""
import uuid
from datetime import datetime

from app.core.security import get_password_hash
from app.db.base import Base, SessionLocal, engine
from app.models.user import User
from app.models.team import Team
from app.models.category import Category
from app.models.tag import Tag
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.models.knowledge_article import KnowledgeArticle
from app.models.audit_log import AuditLog
from app.models.sla_settings import SLASettings


def seed_database():
    """Seed database with initial data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_admin:
            print("Admin user already exists. Skipping seed.")
            return
        
        print("Seeding database...")
        
        # Create admin user
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@example.com",
            name="管理者",
            role="admin",
            password_hash=get_password_hash("testpass123"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(admin_user)
        
        # Create operator user
        operator_user = User(
            id=str(uuid.uuid4()),
            email="operator@example.com",
            name="オペレーター",
            role="operator",
            password_hash=get_password_hash("testpass123"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(operator_user)
        
        # Create requester user
        requester_user = User(
            id=str(uuid.uuid4()),
            email="user@example.com",
            name="一般ユーザー",
            role="requester",
            password_hash=get_password_hash("testpass123"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(requester_user)
        
        # Create teams
        support_team = Team(
            id=str(uuid.uuid4()),
            name="サポートチーム",
            description="一般的な問い合わせ対応チーム",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(support_team)
        
        tech_team = Team(
            id=str(uuid.uuid4()),
            name="技術チーム",
            description="技術的な問題対応チーム",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(tech_team)
        
        # Create categories
        categories_data = [
            {"name": "システム障害", "type": "BOTH"},
            {"name": "操作方法", "type": "BOTH"},
            {"name": "アカウント", "type": "TICKET"},
            {"name": "トラブルシューティング", "type": "ARTICLE"},
            {"name": "FAQ", "type": "ARTICLE"},
        ]
        
        for cat_data in categories_data:
            category = Category(
                id=str(uuid.uuid4()),
                name=cat_data["name"],
                type=cat_data["type"],
                created_at=datetime.utcnow(),
            )
            db.add(category)
        
        # Create tags
        tags_data = ["緊急", "ネットワーク", "認証", "パフォーマンス", "バグ", "機能要望", "ドキュメント"]
        
        for tag_name in tags_data:
            tag = Tag(
                id=str(uuid.uuid4()),
                name=tag_name,
                created_at=datetime.utcnow(),
            )
            db.add(tag)
        
        # Create SLA settings for all priorities
        sla_configs = [
            {"priority": "LOW", "frt": 480, "resolution": 2880},  # 8h, 48h
            {"priority": "MEDIUM", "frt": 240, "resolution": 1440},  # 4h, 24h
            {"priority": "HIGH", "frt": 120, "resolution": 480},  # 2h, 8h
            {"priority": "URGENT", "frt": 30, "resolution": 240},  # 30min, 4h
        ]
        
        for sla_config in sla_configs:
            sla_settings = SLASettings(
                id=str(uuid.uuid4()),
                priority=sla_config["priority"],
                first_response_target_minutes=sla_config["frt"],
                resolution_target_minutes=sla_config["resolution"],
                pause_on_waiting_customer=True,
                timezone="Asia/Tokyo",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(sla_settings)
        
        db.commit()
        
        print("✅ Database seeded successfully!")
        print("\n初期ユーザー:")
        print("  管理者: admin@example.com / testpass123")
        print("  オペレーター: operator@example.com / testpass123")
        print("  一般ユーザー: user@example.com / testpass123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
