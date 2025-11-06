from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_current_operator
from app.db.base import get_db
from app.models.user import User
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketStatusTransition,
    CommentCreate,
    CommentResponse,
    PaginatedTicketResponse,
)
from app.services import ticket_service

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new ticket."""
    ticket = ticket_service.create_ticket(
        db=db,
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority,
        requester_id=current_user.id,
        category_id=ticket_data.category_id,
        tag_names=ticket_data.tags,
    )
    return ticket


@router.get("", response_model=PaginatedTicketResponse)
def list_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assignee_id: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of tickets with filters."""
    # Requesters can only see their own tickets
    requester_id = None if current_user.role in ["operator", "admin"] else current_user.id
    
    tickets = ticket_service.get_tickets(
        db=db,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        requester_id=requester_id,
        category_id=category_id,
        skip=skip,
        limit=limit,
    )
    
    # Get total count
    total = ticket_service.count_tickets(
        db=db,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        requester_id=requester_id,
        category_id=category_id,
    )
    
    return {
        "items": tickets,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get ticket by ID."""
    ticket = ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check permission: requesters can only view their own tickets
    if current_user.role == "requester" and ticket.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")
    
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: str,
    ticket_data: TicketUpdate,
    current_user: User = Depends(get_current_operator),
    db: Session = Depends(get_db),
):
    """Update ticket fields (operator/admin only)."""
    ticket = ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Prepare update data
    updates = ticket_data.model_dump(exclude_unset=True)
    
    # Handle tags separately
    if "tags" in updates:
        tag_names = updates.pop("tags")
        # Clear existing tags and add new ones
        ticket.tags.clear()
        if tag_names:
            from app.models.tag import Tag
            import uuid
            from datetime import datetime
            for tag_name in tag_names:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(id=str(uuid.uuid4()), name=tag_name, created_at=datetime.utcnow())
                    db.add(tag)
                ticket.tags.append(tag)
    
    return ticket_service.update_ticket(db, ticket, current_user.id, **updates)


@router.post("/{ticket_id}/transition", response_model=TicketResponse)
def transition_status(
    ticket_id: str,
    transition_data: TicketStatusTransition,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Transition ticket status."""
    ticket = ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check permission
    if current_user.role == "requester":
        # Requesters can only change their own tickets
        if ticket.requester_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to change ticket status")
        
        # Requesters can only perform specific status transitions
        allowed_transitions = {
            "WAITING_CUSTOMER": ["IN_PROGRESS"],  # Customer provides additional info
            "RESOLVED": ["CLOSED"],               # Customer confirms resolution
        }
        
        current_status = ticket.status
        if current_status not in allowed_transitions:
            raise HTTPException(
                status_code=403, 
                detail=f"Cannot change status from {current_status}. Only allowed from WAITING_CUSTOMER or RESOLVED."
            )
        
        if transition_data.status not in allowed_transitions[current_status]:
            raise HTTPException(
                status_code=403,
                detail=f"Cannot transition from {current_status} to {transition_data.status}"
            )
    
    # Validate status transition
    valid_statuses = ["OPEN", "IN_PROGRESS", "WAITING_CUSTOMER", "RESOLVED", "CLOSED", "CANCELED"]
    if transition_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    return ticket_service.transition_ticket_status(
        db, ticket, transition_data.status, current_user.id
    )


@router.post("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: str,
    assignee_id: Optional[str] = None,
    assigned_team_id: Optional[str] = None,
    current_user: User = Depends(get_current_operator),
    db: Session = Depends(get_db),
):
    """Assign ticket to user or team (operator/admin only)."""
    ticket = ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket_service.assign_ticket(db, ticket, assignee_id, assigned_team_id, current_user.id)


@router.post("/{ticket_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    ticket_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a comment to a ticket."""
    ticket = ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check permission for viewing ticket
    if current_user.role == "requester" and ticket.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to comment on this ticket")
    
    # Only operators/admins can create internal comments
    if comment_data.is_internal and current_user.role not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to create internal comments")
    
    comment = ticket_service.create_comment(
        db, ticket, current_user.id, comment_data.content, comment_data.is_internal
    )
    return comment


@router.get("/{ticket_id}/comments", response_model=List[CommentResponse])
def get_comments(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comments for a ticket."""
    ticket = ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check permission for viewing ticket
    if current_user.role == "requester" and ticket.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")
    
    # Include internal comments only for operators/admins
    include_internal = current_user.role in ["operator", "admin"]
    
    comments = ticket_service.get_ticket_comments(db, ticket_id, include_internal)
    return comments
