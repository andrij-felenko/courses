import hmac, hashlib, time, json

def parse_sig(h: str) -> dict:
    return dict(p.split("=", 1) for p in h.split(",") if "=" in p)  # "t=..,v1=.." → {t, v1}

@app.post("/dh/webhook")
async def receive(request: Request):
    raw = await request.body()                      # сирі байти ДО .json() — інакше підпис не зійдеться
    sig = parse_sig(request.headers.get("dh-signature", ""))
    t, v1 = sig.get("t", "0"), sig.get("v1", "")

    # 1 · ДОВІРА: HMAC над тими самими `t.body`, звірка у СТАЛИЙ час.
    expected = hmac.new(HOOK_SECRET.encode(), f"{t}.".encode() + raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(v1, expected):
        raise HTTPException(401, "bad signature")   # не від DH

    # 2 · СВІЖІСТЬ: вікно 5 хв проти переграння, як у Stripe.
    if abs(time.time() - int(t)) > 300:
        raise HTTPException(400, "stale timestamp")

    event = json.loads(raw)                         # тепер тілу можна вірити

    # 3 · ДЕДУП + ЗАСТОСУВАННЯ РАЗ — в ОДНІЙ транзакції.
    async with db.transaction() as tx:
        ins = await tx.execute(
            "INSERT INTO inbox(event_id) VALUES ($1) ON CONFLICT DO NOTHING", event["id"])
        if ins.rowcount == 0:
            return {"ok": True}                     # вже застосовано — проковтнули повтор
        await apply_firmware_result(tx, event)      # ефект застосовано рівно раз
    return {"ok": True}                             # ACK після коміту
