# GET /operations/{op_id} — чисте читання; клієнт полить із відступом. Кеш заборонено.
@app.get("/operations/{op_id}")
async def get_operation(op_id: str, resp: Response):
    op = await repo.find(op_id)
    if op is None:
        raise HTTPException(404)
    resp.headers["Cache-Control"] = "no-store"
    return {"id": op.id, "status": op.status, "progress": op.progress,
            "result": op.result, "error": op.error}

# POST /operations/{op_id}:cancel — кооперативно: queued гасне одразу, running лишає прапорець.
@app.post("/operations/{op_id}:cancel", status_code=202)
async def cancel_operation(op_id: str):
    await db.execute(
        """UPDATE operations
              SET status = CASE WHEN status = 'queued' THEN 'canceled' ELSE status END,
                  cancel_requested = true
            WHERE id = $1 AND status IN ('queued','running')""", op_id)
    return {"status": "canceling"}                 # «прийнято до скасування», не «скасовано»
