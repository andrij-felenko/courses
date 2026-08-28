from sqlalchemy import (Table, Column, Integer, String, ForeignKey,
                        MetaData, create_engine, select)
from sqlalchemy.orm import registry, relationship, Session, selectinload

metadata = MetaData()
devices = Table("devices", metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String), Column("room", String),
    Column("state", String), Column("last_seen", Integer))
telemetry = Table("telemetry", metadata,
    Column("id", Integer, primary_key=True),
    Column("device_id", Integer, ForeignKey("devices.id")),
    Column("at", Integer))

mapper = registry()
mapper.map_imperatively(Telemetry, telemetry)
mapper.map_imperatively(Device, devices, properties={
    "telemetry": relationship(Telemetry, backref="device"),   # лінива за замовчуванням
})
