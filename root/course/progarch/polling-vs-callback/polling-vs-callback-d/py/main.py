# СЕРВЕР DH: статус для тих, хто ОПИТУЄ (телефон тягне сам)
@app.get("/jobs/{job_id}")
async def job_status(job_id: str):
    j = await jobs.get(job_id)
    return {"status": j.status, "ok": j.ok}          # "processing" → ... → "done"

# СЕРВЕР DH: задача завершилась — ШТОВХАЄМО вебхук тим, хто лишив адресу
async def on_firmware_done(job):
    for url in await hooks.for_home(job.home):
        body = json.dumps({"event": "firmware.updated", "home": job.home, "ok": job.ok})
        await deliver(url, body, sign(body, secret))  # з підписом + повтор при збої (див. проєкт)

# ТЕЛЕФОН: опитування з відступом, поки екран відкритий
async def poll_until_done(job_id: str):
    wait = 1.0
    while True:
        r = await http_get_json(f"/jobs/{job_id}")
        if r["status"] == "done":
            return r                                  # дізналися результат
        await asyncio.sleep(wait)
        wait = min(wait * 2, 15.0)                    # відступ, щоб не бити щосекунди
