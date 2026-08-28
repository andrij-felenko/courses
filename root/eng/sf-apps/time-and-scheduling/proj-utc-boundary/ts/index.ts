// Межа: настінний час ↔ мить. Тільки стандартний Intl, без залежностей.
type Wall = { y: number; mo: number; d: number; h: number; mi: number };
type Kind = "exact" | "gap" | "ambiguous";
type Resolved = { instant: number; kind: Kind };   // instant — мілісекунди епохи

const MINUTE = 60_000;
const DAY = 24 * 60 * MINUTE;

// Побудова форматувальника коштує на порядок дорожче за саме форматування — кешуємо.
const fmtCache = new Map<string, Intl.DateTimeFormat>();
function cachedFmt(key: string, make: () => Intl.DateTimeFormat): Intl.DateTimeFormat {
  let f = fmtCache.get(key);
  if (!f) { f = make(); fmtCache.set(key, f); }
  return f;
}

/** Зсув зони для КОНКРЕТНОЇ миті: читаємо мить у зоні й дивимось,
 *  наскільки цей напис розійшовся з написом у UTC. */
function zoneOffset(instant: number, zone: string): number {
  const p = cachedFmt("parts|" + zone, () => new Intl.DateTimeFormat("en-GB", {
    timeZone: zone, hourCycle: "h23",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit",
  })).formatToParts(new Date(instant));
  const g = (t: string) => Number(p.find((x) => x.type === t)!.value);
  const asUTC = Date.UTC(g("year"), g("month") - 1, g("day"),
                         g("hour"), g("minute"), g("second"));
  return asUTC - Math.floor(instant / 1000) * 1000;
}

/** Настінний час + зона → мить. Каже, скільки відповідей насправді було. */
function resolveLocal(w: Wall, zone: string): Resolved {
  const asIfUTC = Date.UTC(w.y, w.mo - 1, w.d, w.h, w.mi);
  // єдині два зсуви, які тут узагалі можуть діяти
  const before = zoneOffset(asIfUTC - DAY, zone);
  const after = zoneOffset(asIfUTC + DAY, zone);

  const valid: number[] = [];
  for (const off of before === after ? [before] : [before, after]) {
    const t = asIfUTC - off;
    if (zoneOffset(t, zone) === off) valid.push(t);   // напис повернувся сам у себе
  }
  if (valid.length === 1) return { instant: valid[0], kind: "exact" };
  if (valid.length === 2) return { instant: Math.min(...valid), kind: "ambiguous" };
  return { instant: asIfUTC - Math.min(before, after), kind: "gap" };
}

/** Мить → напис у зоні читача: «2026-10-25 03:30 GMT+03:00». */
function formatInZone(instant: number, zone: string): string {
  return cachedFmt("out|" + zone, () => new Intl.DateTimeFormat("sv-SE", {
    timeZone: zone, hourCycle: "h23",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", timeZoneName: "longOffset",
  })).format(new Date(instant));
}

/** Півзакритий проміжок [від, до) — доба користувача на осі митей. */
function dayBounds(y: number, mo: number, d: number, zone: string): [number, number] {
  const next = new Date(Date.UTC(y, mo - 1, d + 1));   // межу місяця й року перескочить саме
  return [
    resolveLocal({ y, mo, d, h: 0, mi: 0 }, zone).instant,
    resolveLocal({ y: next.getUTCFullYear(), mo: next.getUTCMonth() + 1,
                   d: next.getUTCDate(), h: 0, mi: 0 }, zone).instant,
  ];
}
