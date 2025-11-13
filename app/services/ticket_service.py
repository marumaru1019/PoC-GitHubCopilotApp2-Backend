import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from app.models.ticket import Ticket
from app.models.comment import Comment
from app.models.tag import Tag
from app.models.audit_log import AuditLog


def generate_ticket_number(db: Session) -> str:
    """Generate unique ticket number in format TKT-00001."""
    last_ticket = db.query(Ticket).order_by(Ticket.created_at.desc()).first()
    if not last_ticket:
        return "TKT-00001"

    # Extract number from last ticket
    last_number = int(last_ticket.ticket_number.split("-")[1])
    new_number = last_number + 1
    return f"TKT-{new_number:05d}"


def create_ticket(
    db: Session,
    title: str,
    description: str,
    priority: str,
    requester_id: str,
    category_id: Optional[str] = None,
    tag_names: Optional[List[str]] = None,
) -> Ticket:
    """Create a new ticket."""
    ticket_id = str(uuid.uuid4())
    ticket_number = generate_ticket_number(db)

    ticket = Ticket(
        id=ticket_id,
        ticket_number=ticket_number,
        title=title,
        description=description,
        status="OPEN",
        priority=priority,
        category_id=category_id,
        requester_id=requester_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Add tags if provided
    if tag_names:
        for tag_name in tag_names:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(id=str(uuid.uuid4()), name=tag_name, created_at=datetime.utcnow())
                db.add(tag)
            ticket.tags.append(tag)

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Reload ticket with relationships
    ticket = get_ticket(db, ticket.id)

    # Create audit log
    create_audit_log(
        db,
        user_id=requester_id,
        action="TICKET_CREATED",
        entity_type="TICKET",
        entity_id=ticket.id,
        metadata={"ticket_number": ticket.ticket_number, "title": title},
    )

    return ticket


def get_ticket(db: Session, ticket_id: str) -> Optional[Ticket]:
    """Get ticket by ID."""
    return (
        db.query(Ticket)
        .options(
            joinedload(Ticket.category),
            joinedload(Ticket.requester),
            joinedload(Ticket.assignee),
            joinedload(Ticket.assigned_team),
            joinedload(Ticket.tags),
        )
        .filter(Ticket.id == ticket_id)
        .first()
    )


def get_tickets(
    db: Session,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[str] = None,
    requester_id: Optional[str] = None,
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 25,
) -> List[Ticket]:
    """Get tickets with filters and search."""
    query = db.query(Ticket).options(
        joinedload(Ticket.category),
        joinedload(Ticket.requester),
        joinedload(Ticket.assignee),
        joinedload(Ticket.assigned_team),
        joinedload(Ticket.tags),
    )

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if assignee_id:
        query = query.filter(Ticket.assignee_id == assignee_id)
    if requester_id:
        query = query.filter(Ticket.requester_id == requester_id)
    if category_id:
        query = query.filter(Ticket.category_id == category_id)
    if search:
        query = query.filter(Ticket.title.ilike(f"%{search}%"))

    return query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
def count_tickets(
    db: Session,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[str] = None,
    requester_id: Optional[str] = None,
    category_id: Optional[str] = None,
    search: Optional[str] = None,
) -> int:
    """Count tickets with filters and search."""
    query = db.query(Ticket)

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if assignee_id:
        query = query.filter(Ticket.assignee_id == assignee_id)
    if requester_id:
        query = query.filter(Ticket.requester_id == requester_id)
    if category_id:
        query = query.filter(Ticket.category_id == category_id)
    if search:
        query = query.filter(Ticket.title.ilike(f"%{search}%"))

    return query.count()
def update_ticket(
    db: Session,
    ticket: Ticket,
    user_id: str,
    **updates,
) -> Ticket:
    """Update ticket fields."""
    old_values = {}

    for key, value in updates.items():
        if value is not None and hasattr(ticket, key):
            old_values[key] = getattr(ticket, key)
            setattr(ticket, key, value)

    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)

    # Create audit log
    if old_values:
        create_audit_log(
            db,
            user_id=user_id,
            action="TICKET_UPDATED",
            entity_type="TICKET",
            entity_id=ticket.id,
            metadata={"old": old_values, "new": updates},
        )

    return ticket


def transition_ticket_status(
    db: Session,
    ticket: Ticket,
    new_status: str,
    user_id: str,
) -> Ticket:
    """Transition ticket status with SLA tracking."""
    old_status = ticket.status

    # Track status transitions for SLA
    if new_status == "WAITING_CUSTOMER" and old_status != "WAITING_CUSTOMER":
        # Start waiting timer
        ticket.waiting_customer_started_at = datetime.utcnow()
    elif old_status == "WAITING_CUSTOMER" and new_status != "WAITING_CUSTOMER":
        # Stop waiting timer and add duration
        if ticket.waiting_customer_started_at:
            duration = (datetime.utcnow() - ticket.waiting_customer_started_at).total_seconds()
            ticket.total_waiting_customer_duration += int(duration)
            ticket.waiting_customer_started_at = None

    if new_status == "RESOLVED" and not ticket.resolved_at:
        ticket.resolved_at = datetime.utcnow()

    if new_status == "CLOSED" and not ticket.closed_at:
        ticket.closed_at = datetime.utcnow()

    ticket.status = new_status
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)

    # Create audit log
    create_audit_log(
        db,
        user_id=user_id,
        action="STATUS_CHANGED",
        entity_type="TICKET",
        entity_id=ticket.id,
        metadata={"old_status": old_status, "new_status": new_status},
    )

    return ticket


def assign_ticket(
    db: Session,
    ticket: Ticket,
    assignee_id: Optional[str],
    assigned_team_id: Optional[str],
    user_id: str,
) -> Ticket:
    """Assign ticket to user or team."""
    old_assignee = ticket.assignee_id
    old_team = ticket.assigned_team_id

    ticket.assignee_id = assignee_id
    ticket.assigned_team_id = assigned_team_id
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)

    # Create audit log
    create_audit_log(
        db,
        user_id=user_id,
        action="TICKET_ASSIGNED",
        entity_type="TICKET",
        entity_id=ticket.id,
        metadata={
            "old_assignee_id": old_assignee,
            "new_assignee_id": assignee_id,
            "old_team_id": old_team,
            "new_team_id": assigned_team_id,
        },
    )

    return ticket


def create_comment(
    db: Session,
    ticket: Ticket,
    author_id: str,
    content: str,
    is_internal: bool = False,
) -> Comment:
    """Create a comment on a ticket."""
    comment = Comment(
        id=str(uuid.uuid4()),
        ticket_id=ticket.id,
        author_id=author_id,
        content=content,
        is_internal=is_internal,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(comment)

    # Track first response time (FRT) - only for public comments by operator/admin
    if not is_internal and not ticket.first_response_at:
        author = db.query(Tag).filter(Tag.id == author_id).first()
        if author and author.role in ["operator", "admin"]:
            ticket.first_response_at = datetime.utcnow()
            ticket.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(comment)

    # Create audit log
    create_audit_log(
        db,
        user_id=author_id,
        action="COMMENT_ADDED",
        entity_type="TICKET",
        entity_id=ticket.id,
        metadata={"comment_id": comment.id, "is_internal": is_internal},
    )

    return comment


def get_ticket_comments(
    db: Session,
    ticket_id: str,
    include_internal: bool = False,
) -> List[Comment]:
    """Get comments for a ticket."""
    query = (
        db.query(Comment)
        .options(joinedload(Comment.author))
        .filter(Comment.ticket_id == ticket_id)
    )

    if not include_internal:
        query = query.filter(Comment.is_internal == False)

    return query.order_by(Comment.created_at.asc()).all()


def create_audit_log(
    db: Session,
    user_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    metadata: Optional[dict] = None,
) -> AuditLog:
    """Create an audit log entry."""
    log = AuditLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        meta_data=metadata,
        created_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    return log
