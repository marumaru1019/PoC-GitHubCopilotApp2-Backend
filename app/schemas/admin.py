from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    type: str  # TICKET, ARTICLE, BOTH
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SLASettingsBase(BaseModel):
    priority: str  # LOW, MEDIUM, HIGH, URGENT
    first_response_target_minutes: int
    resolution_target_minutes: int
    pause_on_waiting_customer: bool = True
    timezone: str = "Asia/Tokyo"


class SLASettingsCreate(SLASettingsBase):
    pass


class SLASettingsUpdate(BaseModel):
    first_response_target_minutes: Optional[int] = None
    resolution_target_minutes: Optional[int] = None
    pause_on_waiting_customer: Optional[bool] = None
    timezone: Optional[str] = None


class SLASettingsResponse(SLASettingsBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    meta_data: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
