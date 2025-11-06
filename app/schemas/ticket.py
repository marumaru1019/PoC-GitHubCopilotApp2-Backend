from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class TicketBase(BaseModel):
    title: str
    description: str
    priority: str  # LOW, MEDIUM, HIGH, URGENT
    category_id: Optional[str] = None


class TicketCreate(TicketBase):
    tags: Optional[List[str]] = []


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category_id: Optional[str] = None
    assignee_id: Optional[str] = None
    assigned_team_id: Optional[str] = None
    tags: Optional[List[str]] = None


class TicketStatusTransition(BaseModel):
    status: str  # OPEN, IN_PROGRESS, WAITING_CUSTOMER, RESOLVED, CLOSED, CANCELED


class TagResponse(BaseModel):
    id: str
    name: str
    
    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: str
    name: str
    type: str
    
    class Config:
        from_attributes = True


class UserBasicResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    
    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    id: str
    ticket_number: str
    title: str
    description: str
    status: str
    priority: str
    category_id: Optional[str] = None
    category: Optional[CategoryResponse] = None
    requester_id: str
    requester: UserBasicResponse
    assignee_id: Optional[str] = None
    assignee: Optional[UserBasicResponse] = None
    assigned_team_id: Optional[str] = None
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    waiting_customer_started_at: Optional[datetime] = None
    total_waiting_customer_duration: int = 0
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str
    is_internal: bool = False


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: str
    ticket_id: str
    author_id: str
    author: Optional[UserBasicResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaginatedTicketResponse(BaseModel):
    items: List[TicketResponse]
    total: int
    skip: int
    limit: int
