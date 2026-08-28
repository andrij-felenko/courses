async def reconcile():
    since = await checkpoint.get("firmware")            # де спинились минулого разу
    done = await dh_api.list_jobs(status="done", updated_since=since)
    for job in done:
        event = {
            "id": f"evt_{job['id']}",       # ТОЙ САМИЙ ключ, що й у вебхука → inbox дедупне
            "type": "firmware.updated",
            "home": job["home"], "version": job["version"], "ok": job["ok"],
        }
        async with db.transaction() as tx:
            ins = await tx.execute(
                "INSERT INTO inbox(event_id) VALUES ($1) ON CONFLICT DO NOTHING", event["id"])
            if ins.rowcount == 0:
                continue                    # вебхук уже приніс
            await apply_firmware_result(tx, event)  # вебхук проґавив — застосовуємо тут
    await checkpoint.set("firmware", now_iso())     # чекпойнт — лише після успішного проходу
# планувальник викликає reconcile() раз на кілька хвилин
