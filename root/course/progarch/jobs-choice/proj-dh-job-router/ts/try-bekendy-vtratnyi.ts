type JobClass =
  | "cacheWarm" | "transcode" | "notify" | "report" | "fleetRollout" | "telemetry";

type Job = {
  cls: JobClass;
  payload: Record<string, unknown>;
  key: string;                        // ключ ідемпотентності — щоб дубль не наробив шкоди
};

// Усі субстрати — під одним інтерфейсом.  tx присутній ⇒ транзакційний бекенд enlist-иться в нього.
interface Substrate { put(job: Job, tx?: Tx): void; }

// ── БЕКЕНД 1 — черга в памʼяті.  Суть: нуль довговічності; гине на рестарті. ──
class MemoryQueue implements Substrate {
  private buf: Job[] = [];
  put(job: Job): void { this.buf.push(job); }        // tx ігноруємо: втратне не транзакційне
  drain(handle: (j: Job) => void): void {
    let j: Job | undefined;
    while ((j = this.buf.shift()) !== undefined) handle(j);
  }
  get depth(): number { return this.buf.length; }
}

// ── БЕКЕНД 2 — черга в БАЗІ (ДЕФОЛТ).  Суть: INSERT задачі йде в ТУ САМУ
// транзакцію, що й бізнес-запис → постановка атомарна із записом-джерелом. ──
class DbQueue implements Substrate {
  constructor(private db: Db) {}
  put(job: Job, tx?: Tx): void {
    const row = { key: job.key, cls: job.cls, payload: job.payload, state: "ready" };
    if (tx) { tx.insert("jobs", row); return; }      // enlist у транзакцію викликача
    const own = this.db.begin();                     // джерела нема (cron) — своя транзакція
    own.insert("jobs", row); own.commit();
  }
  // Воркер тягне пачку готових задач.  У проді це рівно SQL нижче; тут — його чесна
  // модель: claim атомарний, двом воркерам той самий рядок не дістанеться.
  claimBatch(limit: number): Row[] {
    const ready = this.db.table("jobs").filter(r => r.state === "ready");
    const batch = ready.slice(0, limit);
    for (const r of batch) r.state = "running";      // «зайняв» — конкурентний claim ці пропустить
    return batch;
  }
}

// ── БЕКЕНД 3 — брокер.  Суть: пропускна здатність + фічі (теми, DLQ),
// АЛЕ постановка НЕ транзакційна з базою. ──
class Broker implements Substrate {
  private topics = new Map<JobClass, Job[]>();
  readonly dlq: Job[] = [];
  put(job: Job): void { this.topic(job.cls).push(job); }   // tx ігноруємо: брокер поза транзакцією БД
  private topic(name: JobClass): Job[] {
    if (!this.topics.has(name)) this.topics.set(name, []);
    return this.topics.get(name)!;
  }
  // at-least-once: обробник може впасти → повертаємо в чергу; N спроб і марно → DLQ.
  deliver(cls: JobClass, handle: (j: Job) => void, maxTries = 3): void {
    const q = this.topic(cls);
    let job: Job | undefined;
    while ((job = q.shift()) !== undefined) {
      let ok = false;
      for (let attempt = 1; attempt <= maxTries && !ok; attempt++) {
        try { handle(job); ok = true; }
        catch { if (attempt === maxTries) this.dlq.push(job); }   // отруйне → мертва черга
      }
    }
  }
  depth(cls: JobClass): number { return this.topic(cls).length; }
}
