// ЗВІРКА (partner). Рідко — це страхувальна сітка. Женемо здобуте крізь ТОЙ САМИЙ inbox.
async function reconcile() {
  const since = await checkpoint.get("firmware");        // де спинились минулого разу
  const done = await dhApi.listJobs({ status: "done", updatedSince: since });

  for (const job of done) {
    const event = {
      id: `evt_${job.id}`,                 // ТОЙ САМИЙ ключ, що й у вебхука → inbox дедупне
      type: "firmware.updated",
      home: job.home, version: job.version, ok: job.ok,
    };
    await db.tx(async (tx) => {
      const ins = await tx.query(
        "INSERT INTO inbox(event_id) VALUES ($1) ON CONFLICT DO NOTHING", [event.id]);
      if (ins.rowCount === 0) return;      // вебхук уже приніс — нічого не робимо
      await applyFirmwareResult(tx, event); // вебхук проґавив — застосовуємо тут
    });
  }
  await checkpoint.set("firmware", nowIso()); // чекпойнт — лише після успішного проходу
}
setInterval(reconcile, 5 * 60_000);          // раз на кілька хвилин
