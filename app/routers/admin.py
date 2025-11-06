from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_current_user
from app.core.security import get_password_hash
from app.db.base import get_db
from app.models.user import User
from app.models.team import Team
from app.models.category import Category
from app.models.tag import Tag
from app.models.sla_settings import SLASettings
from app.models.audit_log import AuditLog
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.admin import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    TagCreate,
    TagResponse,
    SLASettingsCreate,
    SLASettingsUpdate,
    SLASettingsResponse,
    AuditLogResponse,
)
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["admin"])


# User Management
@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get list of users (admin only)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a new user (admin only)."""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        name=user_data.name,
        role=user_data.role,
        team_id=user_data.team_id,
        password_hash=get_password_hash(user_data.password),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


# Team Management
@router.get("/teams", response_model=List[TeamResponse])
def list_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of teams."""
    teams = db.query(Team).all()
    return teams


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a new team (admin only)."""
    team = Team(
        id=str(uuid.uuid4()),
        name=team_data.name,
        description=team_data.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.patch("/teams/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: str,
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update team (admin only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    update_data = team_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team, key, value)
    
    team.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(team)
    return team


# Category Management
@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of categories."""
    categories = db.query(Category).all()
    return categories


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a new category (admin only)."""
    category = Category(
        id=str(uuid.uuid4()),
        name=category_data.name,
        type=category_data.type,
        description=category_data.description,
        created_at=datetime.utcnow(),
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# Tag Management
@router.get("/tags", response_model=List[TagResponse])
def list_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of tags."""
    tags = db.query(Tag).all()
    return tags


@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new tag."""
    # Check if tag already exists
    existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
    if existing_tag:
        return existing_tag
    
    tag = Tag(
        id=str(uuid.uuid4()),
        name=tag_data.name,
        created_at=datetime.utcnow(),
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


# SLA Settings Management
@router.get("/sla-settings", response_model=List[SLASettingsResponse])
def list_sla_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of SLA settings."""
    settings = db.query(SLASettings).all()
    return settings


@router.post("/sla-settings", response_model=SLASettingsResponse, status_code=status.HTTP_201_CREATED)
def create_sla_settings(
    sla_data: SLASettingsCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create SLA settings for a priority (admin only)."""
    # Check if settings already exist for this priority
    existing = db.query(SLASettings).filter(SLASettings.priority == sla_data.priority).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"SLA settings for priority '{sla_data.priority}' already exist")
    
    settings = SLASettings(
        id=str(uuid.uuid4()),
        priority=sla_data.priority,
        first_response_target_minutes=sla_data.first_response_target_minutes,
        resolution_target_minutes=sla_data.resolution_target_minutes,
        pause_on_waiting_customer=sla_data.pause_on_waiting_customer,
        timezone=sla_data.timezone,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


@router.patch("/sla-settings/{settings_id}", response_model=SLASettingsResponse)
def update_sla_settings(
    settings_id: str,
    sla_data: SLASettingsUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update SLA settings (admin only)."""
    settings = db.query(SLASettings).filter(SLASettings.id == settings_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="SLA settings not found")
    
    update_data = sla_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
    
    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    return settings


# Audit Log
@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get audit logs (admin only, read-only)."""
    query = db.query(AuditLog)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(AuditLog.action == action)
    
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs
