import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI(title="IoT Control Plane Service")

class CommandRequest(BaseModel):
    device_id: str
    op: str
    params: dict
    ttl_sec: int = 300
    idempotency_key: Optional[str] = None

class CommandRecord:
    def __init__(self, cmd_id: str, device_id: str, op: str, params: dict, ttl_sec: int):
        self.cmd_id = cmd_id
        self.device_id = device_id
        self.op = op
        self.params = params
        self.ttl_sec = ttl_sec
        self.issued_at = int(time.time())
        self.status = "QUEUED"
        self.progress_pct = 0
        self.error_code = 0

class MailboxStore:
    """Черга поштової скриньки для асинхронно сплячих пристроїв."""
    def __init__(self):
        self._queues: Dict[str, List[CommandRecord]] = {}
        self._registry: Dict[str, CommandRecord] = {}

    def enqueue(self, record: CommandRecord):
        if record.device_id not in self._queues:
            self._queues[record.device_id] = []
        self._queues[record.device_id].append(record)
        self._registry[record.cmd_id] = record

    def pop_valid_command(self, device_id: str) -> Optional[CommandRecord]:
        now = int(time.time())
        queue = self._queues.get(device_id, [])
        while queue:
            cmd = queue.pop(0)
            if now <= cmd.issued_at + cmd.ttl_sec:
                cmd.status = "DISPATCHED"
                return cmd
            cmd.status = "EXPIRED"
        return None

    def update_status(self, cmd_id: str, status: str, progress: int = 0, err: int = 0):
        if cmd_id in self._registry:
            cmd = self._registry[cmd_id]
            cmd.status = status
            cmd.progress_pct = progress
            cmd.error_code = err

mailbox = MailboxStore()
active_connections: List[WebSocket] = []

@app.websocket("/ws/control")
async def websocket_control_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            action = msg.get("action")

            if action == "SEND_COMMAND":
                cmd_id = str(uuid.uuid4())
                record = CommandRecord(
                    cmd_id=cmd_id,
                    device_id=msg["device_id"],
                    op=msg["op"],
                    params=msg.get("params", {}),
                    ttl_sec=msg.get("ttl_sec", 300)
                )
                mailbox.enqueue(record)
                
                # Миттєве підтвердження клієнту про постановку в чергу
                await websocket.send_json({
                    "event": "COMMAND_ENQUEUED",
                    "cmd_id": cmd_id,
                    "device_id": record.device_id,
                    "status": "QUEUED"
                })

                # Запуск асинхронного відстеження сесії доставки
                asyncio.create_task(simulate_device_exchange(record))

    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_status(cmd_id: str, status: str, progress: int = 0, val: int = 0):
    mailbox.update_status(cmd_id, status, progress)
    payload = {
        "event": "STATUS_UPDATE",
        "cmd_id": cmd_id,
        "status": status,
        "progress_pct": progress,
        "current_value": val
    }
    for ws in list(active_connections):
        try:
            await ws.send_json(payload)
        except Exception:
            pass

async def simulate_device_exchange(cmd: CommandRecord):
    """Емуляція повного життєвого циклу проходження команди через залізо."""
    # Етап 1: Затримка доставки та транспортний ACK
    await asyncio.sleep(0.3)
    await broadcast_status(cmd.cmd_id, "ACK_RECEIVED", progress=0)
    
    # Етап 2: Початок руху приводу
    await asyncio.sleep(0.5)
    await broadcast_status(cmd.cmd_id, "STARTED", progress=0)
    
    # Етап 3: Проміжні звіти прогресу
    for p in range(25, 100, 25):
        await asyncio.sleep(0.8)
        await broadcast_status(cmd.cmd_id, "IN_PROGRESS", progress=p)
        
    # Етап 4: Фінальне підтвердження завершення
    await asyncio.sleep(0.5)
    target_pos = cmd.params.get("target_pct", 100)
    await broadcast_status(cmd.cmd_id, "COMPLETED", progress=100, val=target_pos)
