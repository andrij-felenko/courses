// Порт — єдина річ, від якої залежить домен.
export interface TelemetryStore {
  write(r: Reading): Promise<void>;
  query(home: HomeId, from: Date, to: Date): Promise<Series>;
}

// Адаптер #1 — Postgres. Домен його ніколи не бачить.
export class PostgresStore implements TelemetryStore {
  constructor(private db: PgPool) {}

  async write(r: Reading): Promise<void> {
    await this.db.query(
      "insert into readings(home, ts, metric, value) values ($1,$2,$3,$4)",
      [r.home, r.ts, r.metric, r.value],
    );
  }

  async query(home: HomeId, from: Date, to: Date): Promise<Series> {
    const rows = await this.db.query(
      "select ts, value from readings where home=$1 and ts between $2 and $3 order by ts",
      [home, from, to],
    );
    return rows.map((x) => ({ ts: x.ts, value: x.value }));
  }
}

// Домен бере будь-який store — і не знає, який саме.
export class EnergyPanel {
  constructor(private store: TelemetryStore) {}

  daily(home: HomeId, day: Date): Promise<Series> {
    return this.store.query(home, startOfDay(day), endOfDay(day));
  }
}
