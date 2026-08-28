from dataclasses import dataclass

# ЗАПИС ЗАДАЧІ — річ першого класу, а не «викликав і забув»
@dataclass
class Job:
    id: str
    key: str            # ключ ідемпотентності: f"{hub_id}:{version}"
    state: str          # queued | running | done | dead
    attempts: int
    run_after: float    # монотонний дедлайн: «не чіпати раніше»

# ВЕБ-БІК: обробник лише ставить задачі в чергу й одразу відповідає 202
@app.post("/homes/{home_id}/firmware/{version}")
async def rollout(home_id: str, version: str):
    hubs = await hubs_of(home_id)
    jobs = [{"key": f"{h}:{version}"} for h in hubs]
    batch_id = await queue.enqueue_all(jobs, run_after=next_night_window())
    return JSONResponse({"batchId": batch_id, "total": len(jobs)}, status_code=202)

# ВОРКЕР-БІК: тягне задачу, дедупить за ключем, повторює або складає в мертву чергу
@queue.consumer
async def apply(job: Job):
    if await already_applied(job.key):        # ідемпотентність: повтор — no-op
        return ok(job)
    try:
        await hub.flash(job.key)
        await mark_done(job.key)              # стан → done, поступ видно родині
    except Exception:
        if job.attempts >= 10:
            return dead_letter(job)           # здалися → людина розбере
        return retry_with_backoff(job)        # ще спроба, з відступом
