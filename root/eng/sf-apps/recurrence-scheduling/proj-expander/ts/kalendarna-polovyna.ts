// Розгортання рекурентного правила: календарна половина.
type Freq = "DAILY" | "WEEKLY" | "MONTHLY" | "YEARLY";
type WeekendShift = "NONE" | "FORWARD" | "BACKWARD";

interface Rule {
  freq: Freq;
  interval?: number;
  byMonth?: number[];                    // 1..12
  byMonthDay?: number[];                 // 1..31 і -1..-31 (рахує з кінця місяця)
  byDay?: [number | null, number][];     // «-1FR» → [-1, 4]; 0 = понеділок
  bySetPos?: number[];                   // відбір у межах ОДНОГО періоду
  count?: number;
  until?: number;                        // мить в UTC, мс, включно
  exdates?: Set<number>;                 // миті-винятки в UTC
  workdayOnly?: boolean;                 // лише понеділок-п'ятниця
  shiftWeekend?: WeekendShift;           // зсув вихідних днів
}

const DAY = 86_400_000;
// Календарну дату кодуємо як опівніч UTC: це НЕ мить, а координата в сітці.
const civil = (y: number, m: number, d: number) => Date.UTC(y, m - 1, d);
const dow = (c: number) => (new Date(c).getUTCDay() + 6) % 7;   // 0 = понеділок
const daysIn = (y: number, m: number) => new Date(Date.UTC(y, m, 0)).getUTCDate();
const dayOf = (wall: number) => { const d = new Date(wall);
  return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()); };
const monthDates = (y: number, m: number) =>
  Array.from({ length: daysIn(y, m) }, (_, j) => civil(y, m, j + 1));

function shiftWeekendDay(c: number, mode: WeekendShift): number {
  const w = dow(c);
  if (w === 5) { // Субота
    if (mode === "FORWARD") return c + 2 * DAY;
    if (mode === "BACKWARD") return c - 1 * DAY;
  } else if (w === 6) { // Неділя
    if (mode === "FORWARD") return c + 1 * DAY;
    if (mode === "BACKWARD") return c - 2 * DAY;
  }
  return c;
}

// i рахується від періоду ПОЧАТКУ, а не від останнього спрацювання —
// саме це тримає крок INTERVAL на місці, коли період випадає.
function periodDates(r: Rule, start: number, i: number): number[] {
  const k = i * (r.interval ?? 1);
  const s = new Date(start);
  switch (r.freq) {
    case "DAILY":
      return [dayOf(start) + k * DAY];
    case "WEEKLY": {
      const mon = dayOf(start) - dow(dayOf(start)) * DAY + k * 7 * DAY;
      return Array.from({ length: 7 }, (_, j) => mon + j * DAY);
    }
    case "MONTHLY": {
      const t = s.getUTCFullYear() * 12 + s.getUTCMonth() + k;
      return monthDates(Math.floor(t / 12), (t % 12) + 1);
    }
    case "YEARLY": {
      // звужуємо ще на породженні: перебирати 366 дат, щоб лишити 28, — марно
      const y = s.getUTCFullYear() + k;
      const months = r.byMonth ?? Array.from({ length: 12 }, (_, j) => j + 1);
      return [...months].sort((a, b) => a - b).flatMap((m) => monthDates(y, m));
    }
  }
}

/** Чи справджують уточнення саме цю дату. dates — увесь період:
 *  без нього не порахувати «остання п'ятниця». */
function matches(r: Rule, c: number, dates: number[]): boolean {
  const d = new Date(c);
  const [y, m, day] = [d.getUTCFullYear(), d.getUTCMonth() + 1, d.getUTCDate()];
  if (r.byMonth && !r.byMonth.includes(m)) return false;
  if (r.byMonthDay) {
    const last = daysIn(y, m);
    if (!r.byMonthDay.some((v) => day === (v > 0 ? v : last + 1 + v))) return false;
  }
  if (r.byDay) {
    const same = dates.filter((x) => dow(x) === dow(c));
    return r.byDay.some(([ord, wd]) => {
      if (wd !== dow(c)) return false;
      if (ord === null) return true;
      const at = same.indexOf(c);
      return (ord > 0 ? at + 1 : at - same.length) === ord;
    });
  }
  return true;
}

/** Упорядкований набір настінних міток i-го періоду після всіх уточнень. */
function candidates(r: Rule, start: number, i: number): [number, number[]] {
  const dates = periodDates(r, start, i);
  let kept = dates.filter((c) => matches(r, c, dates));
  if (r.bySetPos) {                        // відбір бачить УВЕСЬ набір періоду
    const n = kept.length;
    const idx = [...new Set(r.bySetPos.map((p) => (p > 0 ? p - 1 : n + p)))]
      .sort((a, b) => a - b);
    kept = idx.filter((j) => j >= 0 && j < n).map((j) => kept[j]);
  }

  if (r.shiftWeekend && r.shiftWeekend !== "NONE") {
    kept = kept.map((c) => shiftWeekendDay(c, r.shiftWeekend!));
  } else if (r.workdayOnly) {
    kept = kept.filter((c) => dow(c) < 5);
  }

  const tod = start - dayOf(start);
  return [dates[0], kept.map((c) => c + tod)];
}
