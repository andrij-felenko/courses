async def handle_charge(request):
    key = request.headers.get("Idempotency-Key")
    if not key or not KEY_RE.match(key):
        return json_resp({"error": "потрібен коректний Idempotency-Key"}, 400)

    user_id = request["user_id"]
    path = request.path
    raw = await request.read()                         # ТОЧНІ байти, як прийшли
    req_hash = fingerprint(request.method, path, raw)
    expires_at = datetime.now(timezone.utc) + KEY_TTL

    async with pool.acquire() as conn:
        won, row = await claim(conn, key, user_id, path, req_hash, expires_at)

        if not won:
            if bytes(row["request_hash"]) != req_hash:            # ключ той, тіло інше
                return json_resp({"error": "Idempotency-Key уже вжито з іншим тілом"}, 422)
            if row["state"] == "in_progress":                     # переможець ще рахує
                return json_resp({"error": "запит із цим ключем ще виконується"},
                                 409, headers={"Retry-After": "1"})
            return send(to_stored(row), replayed=True)            # completed → відтворення

    stored = await run_once(pool, key, user_id, path, json.loads(raw))
    return send(stored, replayed=False)                           # свіжий результат — раз
