# ТЕЛЕФОН — поллінг ОБМЕЖЕНИЙ бюджетом часу + експоненційний відступ + ПОВНИЙ джитер.
async def poll_job(job_id: str, budget_s: float = 300.0) -> dict:
    deadline = time.monotonic() + budget_s           # 5 хв — далі спінер не має сенсу
    base, cap, attempt = 1.0, 15.0, 0
    while True:
        job = await http_get_json(f"/jobs/{job_id}")
        if job["status"] in ("done", "failed"):
            return job                               # ← єдиний нормальний вихід

        wait = random.uniform(0, min(cap, base * 2 ** attempt))  # повний джитер
        if time.monotonic() + wait > deadline:       # не спати за бюджет — здаємось
            raise TimeoutError("poll budget exhausted")
        await asyncio.sleep(wait)
        attempt += 1
