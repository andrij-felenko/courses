import asyncio, random, uuid
import httpx

def full_jitter(attempt, base=0.1, cap=2.0):            # секунди
    return random.uniform(0, min(cap, base * 2 ** attempt))

async def send_command(client: httpx.AsyncClient, device_id: str, action: str) -> bool:
    # Ключ — ОДИН на логічну команду, незмінний крізь усі повтори.
    idempotency_key = str(uuid.uuid4())
    max_tries = 3                                       # єдиний ×k на шляху

    for attempt in range(max_tries):
        if attempt > 0:
            await asyncio.sleep(full_jitter(attempt - 1))
        r = await client.post(
            f"/v1/devices/{device_id}/commands",
            headers={"Idempotency-Key": idempotency_key},   # той самий рядок щоразу
            json={"action": action},
        )
        if r.is_success:
            return True
        if r.status_code < 500 and r.status_code != 429:    # 4xx (крім 429) — не повторюємо
            return False
    return False                                        # спроби вичерпано
