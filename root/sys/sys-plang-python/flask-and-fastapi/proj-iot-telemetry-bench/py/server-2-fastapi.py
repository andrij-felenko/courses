import asyncio
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import FastAPI, Header, HTTPException, status

app = FastAPI()

class TelemetryPayload(BaseModel):
    device_id: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    temperature: float = Field(ge=-50.0, le=150.0)
    humidity: float = Field(ge=0.0, le=100.0)
    battery_mv: int = Field(ge=0, le=5000)

async def verify_token(x_sensor_token: Annotated[str, Header()]) -> str:
    if x_sensor_token != "secret-station-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized sensor"
        )
    return x_sensor_token

@app.post("/api/v1/telemetry", status_code=status.HTTP_200_OK)
async def ingest_telemetry(
    payload: TelemetryPayload,
    _: Annotated[str, Header(alias="X-Sensor-Token")]
):
    # Емуляція неблокувального запису в БД через асинхронний драйвер (15 мс)
    await asyncio.sleep(0.015)

    return {"status": "stored", "device_id": payload.device_id}
