"""Диспетчер командного каналу: вхід оператора, поштова скринька для сплячих
вузлів, супервізор таймаутів і трансляція станів у панелі.

Запуск: uvicorn backend:app --reload --port 8000
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Annotated, Any

import jwt
from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from control_plane.hub import Hub
from control_plane.mailbox import Mailbox
from control_plane.models import CommandRecord, CommandRequest, DeviceReport
from control_plane.mqtt_link import MqttLink

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
LOG = logging.getLogger("control-plane")

JWT_SECRET = "stand-secret"   # на стенді ключ один; у полі його видає сховище секретів
JWT_ALGO = "HS256"
EXEC_DEADLINE_SEC = 15.0      # скільки чекаємо на другу фазу після відправки
RETENTION_SEC = 900.0         # скільки тримаємо закриті транзакції для повторних питань

hub = Hub()
mailbox = Mailbox()
mqtt_link: MqttLink | None = None


# --- права доступу --------------------------------------------------------

def _claims(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.PyJWTError as exc:
        raise ValueError(str(exc)) from exc


def operator(authorization: Annotated[str | None, Header()] = None) -> str:
    """Керувати приводом може лише роль operator — перевіряємо ДО черги."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "потрібен заголовок Authorization: Bearer <jwt>"
        )
    try:
        claims = _claims(authorization.split(" ", 1)[1])
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"недійсний токен: {exc}") from exc
    if "operator" not in claims.get("roles", []):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "для керування потрібна роль operator")
    return str(claims.get("sub", "anonymous"))


# --- реакція на звіти заліза ---------------------------------------------

async def on_device_report(report: DeviceReport) -> None:
    record = mailbox.get(report.cmd_id)
    if record is None:
        # Таке буває після перезапуску сервера: залізо ще звітує по команді,
        # якої диспетчер уже не пам'ятає. Мовчки ковтати не можна — це журнал.
        LOG.warning("звіт по невідомій команді %s (%s)", report.cmd_id, report.state)
        return
    if record.apply(report):
        await hub.broadcast({"event": "STATUS_UPDATE", "command": record.snapshot()})


# --- супервізор -----------------------------------------------------------

async def supervisor() -> None:
    """Раз на секунду закриває те, що зависло, і прибирає старе."""
    while True:
        await asyncio.sleep(1.0)
        try:
            now = time.time()
            for record in mailbox.overdue(now, EXEC_DEADLINE_SEC):
                record.mark_timeout()
                LOG.warning("таймаут другої фази: %s", record.cmd_id)
                await hub.broadcast({"event": "STATUS_UPDATE", "command": record.snapshot()})
            for record in mailbox.expire_queued(now):
                LOG.info("наказ %s протух у черзі", record.cmd_id)
                await hub.broadcast({"event": "STATUS_UPDATE", "command": record.snapshot()})
            mailbox.purge(now, RETENTION_SEC)
        except asyncio.CancelledError:
            raise
        except Exception:
            # Супервізор не має права померти: без нього транзакції висять вічно.
            LOG.exception("виток супервізора впав, працюємо далі")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_link
    mqtt_link = MqttLink(asyncio.get_running_loop(), on_device_report)
    mqtt_link.start()
    watcher = asyncio.create_task(supervisor(), name="timeout-supervisor")
    try:
        yield
    finally:
        watcher.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await watcher
        mqtt_link.stop()


app = FastAPI(title="Контур керування приводом", lifespan=lifespan)


# --- вхід оператора -------------------------------------------------------

@app.post("/command", status_code=status.HTTP_202_ACCEPTED)
async def post_command(
    request: CommandRequest, who: Annotated[str, Depends(operator)]
) -> dict[str, Any]:
    if request.idempotency_key:
        twin = mailbox.find_by_key(request.device_id, request.idempotency_key)
        if twin is not None:
            # Повторний клік або ретрай мережі: віддаємо ту саму транзакцію.
            return {"cmd_id": twin.cmd_id, "status": twin.status, "duplicate": True}

    record = CommandRecord(
        cmd_id=str(uuid.uuid4()),
        device_id=request.device_id,
        op=request.op,
        params=request.params,
        ttl_sec=request.ttl_sec,
        operator=who,
        idempotency_key=request.idempotency_key,
    )
    mailbox.enqueue(record)
    LOG.info("%s поставив %s на %s", who, record.op, record.device_id)
    await hub.broadcast({"event": "STATUS_UPDATE", "command": record.snapshot()})

    if mqtt_link is not None and mqtt_link.publish_command(record):
        record.mark_dispatched()
        await hub.broadcast({"event": "STATUS_UPDATE", "command": record.snapshot()})

    return {"cmd_id": record.cmd_id, "status": record.status, "duplicate": False}


# --- вхід пристрою --------------------------------------------------------

@app.get("/devices/{device_id}/mailbox")
async def poll_mailbox(device_id: str) -> Any:
    """Сплячий вузол прокинувся й питає, чи є для нього наказ."""
    now = time.time()
    record, expired = mailbox.take_for(device_id, now)
    for dead in expired:
        LOG.info("наказ %s викинуто з черги за TTL", dead.cmd_id)
        await hub.broadcast({"event": "STATUS_UPDATE", "command": dead.snapshot()})

    if record is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    await hub.broadcast({"event": "STATUS_UPDATE", "command": record.snapshot()})
    return {
        "cmd_id": record.cmd_id,
        "op": record.op,
        "target_pct": record.params.get("target_pct"),
        "issued_at": int(record.issued_at),
        "ttl_sec": record.ttl_sec,
    }


@app.post("/devices/{device_id}/report", status_code=status.HTTP_204_NO_CONTENT)
async def post_report(device_id: str, payload: dict[str, Any]) -> Response:
    """Шлях для вузлів без MQTT: та сама квитанція, тільки поверх HTTP."""
    try:
        report = DeviceReport.from_payload(json.dumps(payload))
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"непридатний звіт: {exc}") from exc
    await on_device_report(report)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- канал у панель -------------------------------------------------------

@app.websocket("/ws/control")
async def ws_control(websocket: WebSocket) -> None:
    try:
        claims = _claims(websocket.query_params.get("token", ""))
    except ValueError:
        await websocket.close(code=4401, reason="недійсний токен")
        return
    roles = set(claims.get("roles", []))
    if not roles & {"operator", "viewer"}:
        await websocket.close(code=4403, reason="немає права дивитися контур")
        return

    await websocket.accept()
    await hub.register(websocket)
    try:
        # Одразу віддаємо зріз: панель могла щойно перепідключитися й не знати
        # про транзакції, що почалися без неї.
        await hub.send(
            websocket,
            {"event": "SYNC_SNAPSHOT", "commands": [r.snapshot() for r in mailbox.active()]},
        )
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                await hub.send(websocket, {"event": "ERROR", "reason": "кадр не JSON"})
                continue

            action = message.get("action") if isinstance(message, dict) else None
            if action == "SYNC_PENDING":
                await hub.send(
                    websocket,
                    {
                        "event": "SYNC_SNAPSHOT",
                        "commands": [r.snapshot() for r in mailbox.active()],
                    },
                )
            elif action == "PING":
                await hub.send(websocket, {"event": "PONG"})
            else:
                await hub.send(
                    websocket, {"event": "ERROR", "reason": f"невідома дія {action!r}"}
                )
    except WebSocketDisconnect:
        pass
    finally:
        await hub.unregister(websocket)
