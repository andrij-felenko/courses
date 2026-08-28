interface ReadCounter {
  hit(field: string, cohort: string): void;
  perCohort(field: string, windowMs: number): Map<string, number>;
}

class WindowedReadCounter implements ReadCounter {
  // (поле|когорта) → (epoch-день → лічильник)
  private buckets = new Map<string, Map<number, number>>();
  private day(ts = Date.now()): number { return Math.floor(ts / 86_400_000); }

  hit(field: string, cohort: string): void {
    const key = `${field}|${cohort}`;
    const b = this.buckets.get(key) ?? new Map<number, number>();
    b.set(this.day(), (b.get(this.day()) ?? 0) + 1);
    this.buckets.set(key, b);
  }

  perCohort(field: string, windowMs: number): Map<string, number> {
    const since = this.day(Date.now() - windowMs);
    const out = new Map<string, number>();
    for (const [key, b] of this.buckets) {
      const [f, cohort] = key.split("|");
      if (f !== field) continue;
      let n = 0;
      for (const [d, c] of b) if (d >= since) n += c;
      if (n > 0) out.set(cohort, n);   // у вікні читали → когорта в грі
    }
    return out;
  }
}

interface GateResult {
  field: string;
  green: boolean;
  windowDays: number;
  stillReading: Record<string, number>;   // когорта → читань за вікно (лише >0)
}

function canContract(field: string, counter: ReadCounter, windowMs: number): GateResult {
  const perCohort = counter.perCohort(field, windowMs);   // когорти — із телеметрії!
  const stillReading = Object.fromEntries(perCohort);
  return {
    field,
    windowDays: windowMs / 86_400_000,
    green: perCohort.size === 0,          // зелено ⟺ НУЛЬ у КОЖНІЙ когорті
    stillReading,
  };
}
