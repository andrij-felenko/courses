import os, hmac, hashlib, time, json
from fastapi import FastAPI, Request, Response
import asyncpg

SECRET = os.environ["ACME_WEBHOOK_SECRET"].encode()

def verify(raw: bytes, header: str) -> bool:
    parts = dict(kv.split("=", 1) for kv in header.split(","))
    t = int(parts.get("t", 0))
    if not t or abs(time.time() - t) > 300:                # застарілий → повтор, геть
        return False
    signed = f"{t}.".encode() + raw                        # t + СИРІ байти
    expected = hmac.new(SECRET, signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, parts.get("v1", ""))   # звірка за СТАЛИЙ час

# Ядро роуту — чиста корутина над (сирі байти, заголовок, пул). Легко кликати з тесту.
async def handle_webhook(raw: bytes, sig_header: str, pool) -> int:
    if not verify(raw, sig_header):                        # хто ти? не той підпис — двері зачинені
        return 400
    event = json.loads(raw)
    try:
        async with pool.acquire() as cx:
            async with cx.transaction():                   # inbox і черга — В ОДНІЙ транзакції
                row = await cx.fetchrow(
                    "INSERT INTO inbox(event_id) VALUES ($1) "
                    "ON CONFLICT DO NOTHING RETURNING event_id", event["id"])
                if row is not None:                        # id новий → у чергу
                    await cx.execute("INSERT INTO jobs(event_id, payload) VALUES ($1, $2)",
                                     event["id"], json.dumps(event))
    except Exception:
        return 500        # транзакція відкотилась сама; нічого не позначено — повтор безпечний
    return 200                                             # ACK за десятки мс

app = FastAPI()

@app.post("/hooks/acme-lock")
async def receive(req: Request):
    code = await handle_webhook(await req.body(),
                                req.headers.get("x-acme-signature", ""),
                                req.app.state.pool)
    return Response(status_code=code)
