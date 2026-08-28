// Шов: усе, що знає решта коду, — цей контракт.
interface EnergyRollup {
  kwhForDay(home: string, day: string): Promise<number>;
}

// Свідомий борг: наївно скануємо й підсумовуємо сирі рядки на кожен запит.
// Розплата за масштабом реальна — але ОБМЕЖЕНА цим одним класом.
class NaiveRollup implements EnergyRollup {
  constructor(private db: Db) {}
  async kwhForDay(home: string, day: string): Promise<number> {
    const rows = await this.db.query(
      "SELECT power_w FROM telemetry WHERE home=$1 AND day=$2", [home, day]);
    return rows.reduce((kwh, r) => kwh + r.power_w / 1000 / 3600, 0); // груба інтеграція
  }
}

// Панель бачить лише шов — не знає й не хоче знати про наївність під ним.
async function renderPanel(rollup: EnergyRollup, home: string) {
  const today = await rollup.kwhForDay(home, "2026-07-11");
  // ...малюємо число
}
