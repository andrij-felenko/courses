JobClass = str  # "cacheWarm" | "transcode" | "notify" | "report" | "fleetRollout" | "telemetry"


@dataclass
class Job:
    cls: JobClass
    payload: dict
    key: str                              # ключ ідемпотентності — щоб дубль не наробив шкоди


# ── БЕКЕНД 1 — черга в памʼяті.  Суть: нуль довговічності; гине на рестарті. ──
class MemoryQueue:
    def __init__(self):
        self.buf: list[Job] = []

    def put(self, job: Job, tx: Tx | None = None) -> None:
        self.buf.append(job)              # tx ігноруємо: втратне не транзакційне

    def drain(self, handle) -> None:
        while self.buf:
            handle(self.buf.pop(0))

    @property
    def depth(self) -> int:
        return len(self.buf)


# ── БЕКЕНД 2 — черга в БАЗІ (ДЕФОЛТ).  Суть: INSERT задачі йде в ТУ САМУ
# транзакцію, що й бізнес-запис → постановка атомарна із записом-джерелом. ──
class DbQueue:
    def __init__(self, db: Db):
        self.db = db

    def put(self, job: Job, tx: Tx | None = None) -> None:
        row = {"key": job.key, "cls": job.cls, "payload": job.payload, "state": "ready"}
        if tx is not None:
            tx.insert("jobs", row)        # enlist у транзакцію викликача
            return
        own = self.db.begin()             # джерела нема (cron) — своя транзакція
        own.insert("jobs", row)
        own.commit()

    def claim_batch(self, limit: int) -> list[dict]:
        # У проді це рівно SQL нижче; тут — його чесна модель: claim атомарний,
        # двом воркерам той самий рядок не дістанеться.
        ready = [r for r in self.db.table("jobs") if r["state"] == "ready"]
        batch = ready[:limit]
        for r in batch:
            r["state"] = "running"        # «зайняв» — конкурентний claim ці пропустить
        return batch


# ── БЕКЕНД 3 — брокер.  Суть: пропускна здатність + фічі (теми, DLQ),
# АЛЕ постановка НЕ транзакційна з базою. ──
class Broker:
    def __init__(self):
        self.topics: dict[JobClass, list[Job]] = {}
        self.dlq: list[Job] = []

    def put(self, job: Job, tx: Tx | None = None) -> None:
        self._topic(job.cls).append(job)  # tx ігноруємо: брокер поза транзакцією БД

    def _topic(self, name: JobClass) -> list[Job]:
        return self.topics.setdefault(name, [])

    def deliver(self, cls: JobClass, handle, max_tries: int = 3) -> None:
        # at-least-once: обробник може впасти → повертаємо в чергу; N спроб і марно → DLQ.
        q = self._topic(cls)
        while q:
            job = q.pop(0)
            for attempt in range(1, max_tries + 1):
                try:
                    handle(job)
                    break
                except Exception:
                    if attempt == max_tries:
                        self.dlq.append(job)          # отруйне → мертва черга

    def depth(self, cls: JobClass) -> int:
        return len(self._topic(cls))
