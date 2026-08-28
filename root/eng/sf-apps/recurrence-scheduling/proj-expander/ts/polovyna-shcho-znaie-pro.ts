// Друга половина: локалізація й головний цикл.
const FMT = new Map<string, Intl.DateTimeFormat>();      // побудова форматувача дорога

function offsetMs(tz: string, instant: number): number {
  let f = FMT.get(tz);
  if (!f) {
    f = new Intl.DateTimeFormat("en-US", {
      timeZone: tz, hour12: false, year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    });
    FMT.set(tz, f);
  }
  const p: Record<string, string> = {};
  for (const { type, value } of f.formatToParts(instant)) p[type] = value;
  // «24» замість «00» — відома примха hour12:false у частині рушіїв
  return Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour % 24, +p.minute, +p.second) - instant;
}

/** null, якщо такого місцевого часу не існує (весняний стрибок).
 *  Двозначний час (осінній відкат) → ПЕРШЕ з двох проходжень. */
function toInstant(tz: string, wall: number, disambiguate = "compatible"): number | null {
  const before = offsetMs(tz, wall - 26 * 3600_000);     // завідомо до переходу
  const after = offsetMs(tz, wall + 26 * 3600_000);      // завідомо після
  for (const off of before >= after ? [before, after] : [after, before]) {
    const inst = wall - off;
    if (inst + offsetMs(tz, inst) === wall) return inst; // обертання зійшлося
  }
  if (disambiguate === "compatible" || disambiguate === "forward") {
    // Зсув на 1 годину вперед при потраплянні в прогалину
    const shiftedWall = wall + 3600_000;
    const off = offsetMs(tz, shiftedWall - 3600_000);
    const inst = shiftedWall - off;
    if (inst + offsetMs(tz, inst) === shiftedWall) return inst;
  }
  return null;
}

function expand(r: Rule, startWall: number, tz: string, after: number,
                limit: number, horizonYears = 10, disambiguate = "compatible"): number[] {
  const startUtc = toInstant(tz, startWall, disambiguate) ?? startWall;
  // запобіжник від вічного циклу на правилі, що не справджується ніколи
  const horizon = Date.UTC(new Date(after).getUTCFullYear() + horizonYears, 11, 31);
  const out: number[] = [];
  let seen = 0;
  for (let i = 0; out.length < limit; i++) {
    const [first, marks] = candidates(r, startWall, i);
    if (first > horizon) break;
    for (const wall of marks) {
      const inst = toInstant(tz, wall, disambiguate);
      if (inst === null || inst < startUtc) continue;    // неіснуючі НЕ рахуємо

      // Фільтрація винятків EXDATE
      if (r.exdates && r.exdates.has(inst)) continue;

      if (r.count !== undefined && ++seen > r.count) return out;
      if (r.until !== undefined && inst > r.until) return out;
      if (inst > after) {                                // строго після — не включно
        out.push(inst);
        if (out.length === limit) return out;
      }
    }
  }
  return out;
}

function runDemoSuite(): { lastFridays: number[]; billing: number[]; dstLeap: number[] } {
  // 1. Щомісяця остання п'ятниця
  const ruleLastFri: Rule = { freq: "MONTHLY", byDay: [[-1, 4]], count: 5 };
  const start = Date.UTC(2026, 0, 1, 9, 0);
  const lastFridays = expand(ruleLastFri, start, "Europe/Kyiv", start, 5);
  if (lastFridays.length !== 5) throw new Error("Має бути 5 дат");

  // 2. Зсув вихідних днів до понеділка з винятком EXDATE
  const exDate = Date.UTC(2026, 2, 16, 7, 0); // 16 березня 2026
  const ruleBilling: Rule = {
    freq: "MONTHLY", byMonthDay: [15], shiftWeekend: "FORWARD",
    exdates: new Set([exDate]),
  };
  const billing = expand(ruleBilling, Date.UTC(2026, 0, 15, 9, 0), "Europe/Kyiv", start, 4);
  if (billing.includes(exDate)) throw new Error("EXDATE не відфільтровано");

  // 3. Весняний стрибок через прогалину 03:30
  const ruleDaily: Rule = { freq: "DAILY", count: 5 };
  const dstLeap = expand(ruleDaily, Date.UTC(2026, 2, 27, 3, 30), "Europe/Kyiv", Date.UTC(2026, 2, 27, 0, 0), 5);
  if (dstLeap.length !== 5) throw new Error("Невірна кількість дат при переході");

  return { lastFridays, billing, dstLeap };
}
