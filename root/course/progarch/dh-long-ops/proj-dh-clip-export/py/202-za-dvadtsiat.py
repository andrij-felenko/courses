# POST /cameras/{camera_id}/clips — прийняти, дедуплікувати за ключем, віддати 202 + Location.
@app.post("/cameras/{camera_id}/clips", status_code=202)
async def create_clip(camera_id: str, body: ClipRequest, req: Request, resp: Response):
    key = req.headers.get("Idempotency-Key")
    if not key:
        raise HTTPException(400, "missing_idempotency_key")

    request = {"cameraId": camera_id, "from": body.from_, "to": body.to}
    op_id = "op-" + new_id()

    # ОДНА вставка = і операція, і задача в черзі. UNIQUE(idempotency_key) розсудить гонку.
    row = await db.fetchrow(
        """INSERT INTO operations (id, idempotency_key, status, request, user_id, expires_at)
           VALUES ($1, $2, 'queued', $3, $4, now() + interval '30 days')
           ON CONFLICT (idempotency_key) DO NOTHING
           RETURNING id""",
        op_id, key, request, req.state.user_id)

    if row is not None:                          # ми ВИГРАЛИ гонку: рядок наш, рендер у черзі
        resp.headers["Location"] = f"/operations/{op_id}"
        return {"id": op_id, "status": "queued"}

    # 0 рядків → нас випередили тим самим ключем. Читаємо ЇХНЮ операцію.
    op = await db.fetchrow(
        "SELECT id, request FROM operations WHERE idempotency_key = $1", key)
    if not same_request(op["request"], request):  # той самий ключ, інші параметри — помилка клієнта
        raise HTTPException(422, "idempotency_key_reused")

    resp.headers["Location"] = f"/operations/{op['id']}"
    return {"id": op["id"], "status": "queued"}    # ТА САМА операція
