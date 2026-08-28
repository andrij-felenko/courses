from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import registry

mapper_registry = registry()

orders = Table(
    "orders", mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("placed_at", String),
    Column("total_cents", Integer),
    Column("currency", String(3)),
    Column("status", String(16)),
)

# Order — той самий звичайний клас, що й вище: без спадкування,
# без декораторів, без жодного рядка про базу у власному коді.
mapper_registry.map_imperatively(Order, orders)
