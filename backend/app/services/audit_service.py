from sqlalchemy.orm import Session
from app.models import AuditLog


def record(db: Session, actor_id: int | None, action: str, entity: str | None = None,
           entity_id: int | None = None, detail: dict | None = None, ip: str | None = None):
    """Append an audit row. Caller commits."""
    db.add(AuditLog(actor_id=actor_id, action=action, entity=entity,
                    entity_id=entity_id, detail=detail, ip_address=ip))
