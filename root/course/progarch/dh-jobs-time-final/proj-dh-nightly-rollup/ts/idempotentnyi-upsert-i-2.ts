async function planner(db: Pool, me: string): Promise<void> {
  const lease = new CronLease(db, "nightly-rollup", me, 60);
  let fence: number | null = null;                         // токен поточної оренди
  for (;;) {
    if (fence === null) {                                  // оренди нема — БЕРЕМО (нове право)
      const held = await lease.acquire();
      if (!held) { await sleep(30_000); continue; }        // живу лізу тримає інший — чекаємо
      fence = held.fence;
    } else if (!(await lease.renew(fence))) {              // не ПРОДОВЖИЛАСЬ → оренду втрачено
      fence = null; continue;                              // на наступному колі спробуємо взяти
    }
    // ми — єдиний планувальник; фенс СТАБІЛЬНИЙ на всю оренду (renew його не міняє)
    for (const h of await loadHomes(db)) {                 // { id, zone, policy, lastDone }
      const days = applyPolicy(dueDays(h.zone, h.lastDone), h.policy);
      for (const day of days) {
        const w = localDayWindow(h.zone, day);
        await enqueue(db, {
          homeId: h.id, zone: h.zone, day: day.toString(),
          fromUtc: w.fromUtc.toString(), toUtc: w.toUtc.toString(),
          fence,                                           // той самий токен їде до писаря
          policy: h.policy,                                // політика їде із задачею — вона вирішує рух mark
        });
      }
    }
    await sleep(30_000);                                   // sleep < TTL, щоб renew устигав
  }
}
