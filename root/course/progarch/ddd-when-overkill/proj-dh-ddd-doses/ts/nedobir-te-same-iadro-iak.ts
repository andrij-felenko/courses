interface DB {
  query(sql: string, id: string): { heater: number; cooler: number };
  exec(sql: string, id: string): void;
}

// ❌ Недобір: правило безпеки розмазане по коду магічними числами.
function runScenario(roomId: string, scenarioId: number, db: DB): void {
  const room = db.query(`SELECT heater, cooler FROM rooms WHERE id = ?`, roomId);

  if (scenarioId === 3) {                          // 3 — це «ніч»? «ранок»? хто вже згадає
    db.exec(`UPDATE rooms SET heater = 1 WHERE id = ?`, roomId);
    // ...а чи не працює ще кулер — перевірити ТУТ забули
  } else if (scenarioId === 7) {
    if (room.cooler === 0)                         // тут перевірку згадали...
      db.exec(`UPDATE rooms SET heater = 1 WHERE id = ?`, roomId);
  }
  // ...те саме правило живе ще у notifyService і в scheduleService,
  //    і в одному з них перевірку теж загубили
}
