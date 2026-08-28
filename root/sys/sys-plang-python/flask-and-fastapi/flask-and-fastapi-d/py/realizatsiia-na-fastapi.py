from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated
import aiosqlite
from fastapi import FastAPI, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

DATABASE_PATH = "telemetry_fastapi.db"

# 1. Pydantic-моделі вхідних даних та відповідей
class TelemetryPayload(BaseModel):
    device_id: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_\-]+$")
    timestamp: datetime
    temperature: float = Field(ge=-50.0, le=85.0, description="Температура сенсора в °C")
    humidity: float = Field(ge=0.0, le=100.0, description="Відносна вологість у %")
    pressure_hpa: float = Field(ge=300.0, le=1200.0, description="Атмосферний тиск у гПа")
    battery_mv: int = Field(ge=0, le=5000, description="Напруга живлення в мВ")

class IngestResponse(BaseModel):
    status: str
    record_id: int
    received_at: datetime

# 2. Керування життєвим циклом додатку (Lifespan Context)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ініціалізація структури бази даних під час старту
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                pressure_hpa REAL NOT NULL,
                battery_mv INTEGER NOT NULL
            )
        """)
        await db.commit()
    yield
    # Очищення ресурсів під час зупинки сервісу

app = FastAPI(
    title="IoT Industrial Telemetry Ingestion API",
    version="1.0.0",
    lifespan=lifespan
)

# 3. Впровадження залежностей (Dependency Injection)
async def verify_auth_token(x_sensor_token: Annotated[str, Header()]) -> str:
    if x_sensor_token != "secret-station-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Sensor-Token header"
        )
    return x_sensor_token

async def get_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        yield db

# 4. Асинхронний ендпоінт прийому телеметрії
@app.post(
    "/api/v1/telemetry",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Прийом вимірювань сенсорної станції"
)
async def ingest_telemetry(
    payload: TelemetryPayload,
    _: Annotated[str, Depends(verify_auth_token)],
    db: Annotated[aiosqlite.Connection, Depends(get_db)]
):
    cursor = await db.execute("""
        INSERT INTO telemetry (device_id, timestamp, temperature, humidity, pressure_hpa, battery_mv)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        payload.device_id,
        payload.timestamp.isoformat(),
        payload.temperature,
        payload.humidity,
        payload.pressure_hpa,
        payload.battery_mv
    ))
    await db.commit()

    return IngestResponse(
        status="success",
        record_id=cursor.lastrowid,
        received_at=datetime.utcnow()
    )
