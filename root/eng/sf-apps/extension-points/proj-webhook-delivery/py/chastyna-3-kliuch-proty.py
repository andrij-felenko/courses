import uuid
from dataclasses import dataclass, field

@dataclass
class DeliveryJob:
    url: str
    payload: dict
    # Ключ народжується РАЗ, при створенні, і НЕ змінюється на повторах.
    delivery_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attempt: int = 0

# ── Бік ОДЕРЖУВАЧА: атомарний claim ключа перед роботою ──
async def handle_incoming(key: str, body: str, db) -> int:
    # Атомарно: вставити ключ. Уже був → 0 рядків → це ДУБЛІКАТ.
    inserted = await db.execute(
        "INSERT INTO processed_webhooks(key) VALUES ($1) "
        "ON CONFLICT (key) DO NOTHING",
        key,
    )
    if inserted.rowcount == 0:
        return 200               # вже бачили → нічого не робимо, кажемо OK
    do_the_work(body)            # побічний ефект — РІВНО раз
    return 200
