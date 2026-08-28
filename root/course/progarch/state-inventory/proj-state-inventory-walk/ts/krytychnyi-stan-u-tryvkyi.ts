const MAX_RUN_S = 2 * 3600;

function setHeatingSince(ts: number | null): void {   // тривкий запис — переживе рестарт
  db.prepare("INSERT OR REPLACE INTO kv(k, v) VALUES ('heated_since', ?)").run(ts);
}

function heatingSince(): number | null {
  const row = db.prepare("SELECT v FROM kv WHERE k = 'heated_since'").get() as any;
  return row ? row.v : null;
}

function guard(): void {                               // межа рахує від ДИСКА, не від памʼяті
  const since = heatingSince();
  if (relayIsOn() && since && Date.now() / 1000 - since > MAX_RUN_S) {
    relayOff(); setHeatingSince(null);
  }
}
