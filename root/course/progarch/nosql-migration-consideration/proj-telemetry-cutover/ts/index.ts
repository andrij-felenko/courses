async writeReading(r: Reading): Promise<void> {
  // Старе — джерело правди: помилка тут справжня, летить далі.
  await this.old.insert(r);
  try {
    await this.new.upsert(r);            // нове — «як вийде»
  } catch (err) {
    this.divergence.inc();               // безперервний лічильник розбіжності
    log.warn(`new-store write failed: device=${r.deviceId} ts=${r.ts} err=${err}`);
    // навмисно не кидаємо далі: нове ще не джерело правди
  }
}
