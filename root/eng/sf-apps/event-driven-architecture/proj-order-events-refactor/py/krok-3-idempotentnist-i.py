import uuid
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass(frozen=True)          # frozen — подія незмінна, знімок минулого
class DomainEvent(Generic[T]):
    type: str
    payload: T
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    # унікальний id САМЕ ЦЬОГО оголошення (не order_id!)
