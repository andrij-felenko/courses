import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from dataclasses import dataclass
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse

app = FastAPI(title="IoT Service API Gateway")

# Конфігурація життєвого циклу версій API
@dataclass
class VersionMeta:
    deprecated: bool
    sunset_date: Optional[str] = None  # HTTP-date формат RFC 8594
    migration_url: Optional[str] = None

VERSION_REGISTRY: Dict[str, VersionMeta] = {
    "v1": VersionMeta(
        deprecated=True,
        sunset_date="Sun, 15 Nov 2026 00:00:00 GMT",
        migration_url="https://api.iot-corp.com/docs/v1-to-v2"
    ),
    "v2": VersionMeta(
        deprecated=False
    )
}

# Внутрішнє сховище метрик звернень за версіями та пристроями
metrics_request_counter: Dict[str, int] = {}

@app.middleware("http")
async def versioning_and_deprecation_middleware(request: Request, call_next):
    path = request.url.path
    api_version = None

    # 1. Визначення версії: спочатку з URL, якщо немає — із заголовка
    if path.startswith("/v1/"):
        api_version = "v1"
    elif path.startswith("/v2/"):
        api_version = "v2"
    else:
        api_version = request.headers.get("X-API-Version", "v2")

    # Збір метрики звернення
    user_agent = request.headers.get("User-Agent", "Unknown-Device")
    metric_key = f"{api_version}:{request.method}:{path}:{user_agent}"
    metrics_request_counter[metric_key] = metrics_request_counter.get(metric_key, 0) + 1

    # Виконання запиту обробником
    response: Response = await call_next(request)

    # 2. Інжекція стандартних заголовків депрекації за стандартом RFC 8594
    v_meta = VERSION_REGISTRY.get(api_version)
    if v_meta and v_meta.deprecated:
        response.headers["Deprecation"] = "true"
        if v_meta.sunset_date:
            response.headers["Sunset"] = v_meta.sunset_date
        if v_meta.migration_url:
            response.headers["Link"] = f'<{v_meta.migration_url}>; rel="deprecation"; type="text/html"'

    return response

# База даних стану пристроїв та черги команд (імітація)
device_storage: Dict[str, Dict[str, Any]] = {
    "dev-101": {"id": "dev-101", "type": "energy_meter", "firmware": "1.0.4", "status": "online"}
}
command_queue: Dict[str, Dict[str, Any]] = {}

# v1 Телеметрія (Застарілий контракт зі скороченими полями)
@app.get("/v1/devices/{device_id}/telemetry")
async def get_telemetry_v1(device_id: str):
    if device_id not in device_storage:
        raise HTTPException(status_code=404, detail="Device not found")
    # v1 формат: скорочені імена
    return {"id": device_id, "v": 230.2, "a": 5.1, "ts": int(time.time())}

# v2 Телеметрія (Сучасний стандартизований контракт)
@app.get("/v2/devices/{device_id}/telemetry")
async def get_telemetry_v2(device_id: str):
    if device_id not in device_storage:
        raise HTTPException(status_code=404, detail="Device not found")
    # v2 формат: точні інженерні одиниці в мілівольтах та міліамперах
    return {
        "device_id": device_id,
        "metrics": {
            "voltage_mv": 230200,
            "current_ma": 5100
        },
        "timestamp_iso": datetime.now(timezone.utc).isoformat()
    }

# Асинхронне створення команди (єдине для v1 та v2)
@app.post("/v2/devices/{device_id}/commands", status_code=status.HTTP_202_ACCEPTED)
async def create_command(device_id: str, payload: Dict[str, Any], response: Response):
    if device_id not in device_storage:
        raise HTTPException(status_code=404, detail="Device not found")

    cmd_id = f"cmd_{int(time.time() * 1000)}"
    command_record = {
        "id": cmd_id,
        "device_id": device_id,
        "action": payload.get("action", "NOOP"),
        "params": payload.get("params", {}),
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    command_queue[cmd_id] = command_record

    # Встановлення обов'язкового заголовка Location на створений ресурс
    location_url = f"/v2/devices/{device_id}/commands/{cmd_id}"
    response.headers["Location"] = location_url
    return command_record

# Опитування статусу команди
@app.get("/v2/devices/{device_id}/commands/{cmd_id}")
async def get_command_status(device_id: str, cmd_id: str):
    cmd = command_queue.get(cmd_id)
    if not cmd or cmd["device_id"] != device_id:
        raise HTTPException(status_code=404, detail="Command not found")
    return cmd
