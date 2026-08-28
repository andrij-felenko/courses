# СЕРВЕР DH — статус для тих, хто ОПИТУЄ. Дешева: тільки читання стану.
@app.get("/jobs/{job_id}")
async def job_status(job_id: str, response: Response):
    job = await jobs.get(job_id)                     # одне читання за ключем
    if job is None:
        raise HTTPException(404, "unknown job")

    terminal = job.status in ("done", "failed")
    # термінальний стан кешувати можна; проміжний — ні, він ще зміниться
    response.headers["Cache-Control"] = "public, max-age=3600" if terminal else "no-store"
    return {
        "jobId": job.id,
        "status": job.status,                        # queued | running | done | failed
        "result": job.result if terminal else None,  # {version, ok} на done; {code, message} на failed
        "updatedAt": job.updatedAt,                  # точка відліку для клієнта й для звірки
    }
