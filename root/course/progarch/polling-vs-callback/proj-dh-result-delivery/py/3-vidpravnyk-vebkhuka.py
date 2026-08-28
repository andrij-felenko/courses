import hmac, hashlib, json, time, random, asyncio

async def on_firmware_done(job):
    event = {                                       # будуємо РАЗ; id детермінований з задачі
        "id": f"evt_{job['id']}",                   # той самий на кожен повтор і на звірку
        "type": "firmware.updated",
        "home": job["home"], "version": job["version"], "ok": job["ok"],
        "occurred_at": job["finished_at"],
    }
    for url in await hooks.for_home(job["home"]):
        await deliver(url, event)

def sign(body: str, secret: str, ts: int) -> str:
    mac = hmac.new(secret.encode(), f"{ts}.{body}".encode(), hashlib.sha256).hexdigest()
    return f"t={ts},v1={mac}"                        # Stripe-стиль: підпис прикриває й тіло, й час

async def deliver(url: str, event: dict):
    body = json.dumps(event, separators=(",", ":"))  # канонічні байти: й підписуємо, й шлемо саме їх
    ts = int(time.time())
    sig = sign(body, HOOK_SECRET, ts)
    base, cap, max_attempts = 1.0, 60.0, 8

    for attempt in range(max_attempts):
        try:
            r = await http_post(url, data=body, timeout=5.0,
                                headers={"content-type": "application/json", "dh-signature": sig})
            if 200 <= r.status < 300:
                return                               # прийнято
            if 400 <= r.status < 500 and r.status != 429:
                break                                # 4xx (крім 429) — не полагодиться повтором
        except (TimeoutError, ConnectionError):
            pass                                     # мережа — у відступ

        window = min(cap, base * 2 ** attempt)
        await asyncio.sleep(random.uniform(0, window))  # експонента + повний джитер
    await dead_letters.put({"url": url, "body": body, "sig": sig, "failed_at": time.time()})
