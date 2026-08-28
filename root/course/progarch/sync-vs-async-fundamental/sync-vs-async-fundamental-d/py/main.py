# СИНХРОННО — обробник тримає запит відкритим, доки хаб не відповість
@app.post("/homes/{home_id}/lock")
async def lock(home_id: str):
    r = await hub.send(home_id, Cmd.LOCK)   # ← чекаємо ТУТ
    return {"state": r.state}               # лише тепер: 200 OK «зачинено»

# АСИНХРОННО — обробник кладе команду в чергу й одразу відповідає
@app.post("/homes/{home_id}/lock")
async def lock_async(home_id: str):
    cmd_id = await commands.enqueue(home_id, Cmd.LOCK)
    return JSONResponse({"accepted": True, "command_id": cmd_id}, status_code=202)  # «прийнято»

# окремий споживач виконає команду, коли хаб оживе (може прийти двічі — тому LOCK ідемпотентна):
@commands.consumer
async def run(c: Command):
    await hub.send(c.home, c)
