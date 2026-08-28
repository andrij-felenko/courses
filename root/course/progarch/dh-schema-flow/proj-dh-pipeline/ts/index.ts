const STEP_SEC = 3600;   // номінальний крок відліку

type Raw = {
  homeId: string;
  deviceId: string;
  ts: number;            // epoch, секунди
  schema: 1 | 2;         // 1 → value є Вт; 2 → value є Вт·год (лічильник)
  value: number;         // на дроті `w` (schema 1) або `wh` (schema 2) — тут одне число
};
type Override = { deviceId: string; from: number; to: number; schema: 1 | 2 };

const dayOf = (ts: number) => new Date(ts * 1000).toISOString().slice(0, 10);

const effSchema = (r: Raw, ov: Override[]): 1 | 2 =>
  ov.find(o => o.deviceId === r.deviceId && o.from <= r.ts && r.ts < o.to)?.schema
  ?? r.schema;                                    // виправлення тут, не в сирому рядку

function deviceDayWh(rows: Raw[], preMeter: number | null, ov: Override[]): Map<string, number> {
  const sorted = [...rows].sort((a, b) => a.ts - b.ts);
  const out = new Map<string, number>();
  let meter = preMeter;                           // показ лічильника ДО вікна
  sorted.forEach((r, i) => {
    const day = dayOf(r.ts);
    const add = (x: number) => out.set(day, (out.get(day) ?? 0) + x);
    if (effSchema(r, ov) === 2) {                 // лічильник: різниця показів
      if (meter !== null) add(r.value - meter);
      meter = r.value;
    } else {                                      // потужність: інтеграл по dt
      const nxt = i + 1 < sorted.length ? sorted[i + 1].ts : r.ts + STEP_SEC;
      add(r.value * (nxt - r.ts) / 3600);
    }
  });
  return out;
}
