# ⚙️ Маршрутизатор задач DH: один шов, три субстрати й тест, що ловить розрив транзакції

У статті ми домовились про головне на словах: постановка задачі ходить через **один шов** `enqueue`, а куди фізично ляже робота — вирішує таблиця маршрутів за класом. І тричі обіцяли, що з цього виходить: перекодування лишається атомарним із записом кліпа, викатка на флот іде брокером із корінцем у базі, а «випуск» класу в брокер коштує правки одного рядка. Тут ми перетворимо кожну з трьох обіцянок на **число, яке або тримається, або ламається на очах**. Зберемо справжній маршрутизатор — три бекенди за одним швом, outbox-міст для флоту — а тоді навмисне уроним транзакцію на півдорозі й подивимось, як обидва записи зникають разом; не тому, що ми їх видалили, а тому, що вони й були одним неподільним записом.

Усе запускається як є — TypeScript через `npx tsx dh-jobs.ts`, Python через `python dh_jobs.py`. Ми не піднімаємо ні Postgres, ні брокера: усе в памʼяті, синхронно й **детерміновано**. Але модель бази — **чесна**: рядки, вставлені в межах транзакції, стають видимі лише після `commit()`, а `rollback()` їх справді викидає. І там, де в проді стояв би Postgres, ми покажемо **справжній** запит, яким воркер забирає пачку задач без гонки за рядок, — `FOR UPDATE SKIP LOCKED`. Катастрофа, яку ми ловимо, — не гонка в часі (її руками не відтвориш), а **розірвана транзакція**: величина, яку рахуєш точно, до останньої одиниці, за будь-якого запуску.

## Задача: три обіцянки, три свідки

Випишімо стенд точно, бо кожен його шматок відповідає рядку статті.

- **Один шов `enqueue(job, tx?)`** — єдина точка, крізь яку проходить уся постановка. Другий параметр `tx` — необовʼязкова транзакція викликача; саме він виявиться завісою, на якій тримається вся атомарність.
- **Таблиця маршрутів `клас → субстрат`** — єдине місце, де клас роботи зустрічає свій бекенд. Її правка — і є «випуск» класу.
- **Три бекенди**, кожен — найдрібніша чесна реалізація свого субстрату: **черга в памʼяті** (втратна, гине на рестарті), **черга в базі** (дефолт; постановка ділить транзакцію з бізнес-записом, воркери тягнуть через `SKIP LOCKED`), **брокер** (пропускна здатність фан-ауту, DLQ з коробки, але поза транзакцією бази).
- **Outbox-міст** для класу викатки-на-флот: корінець-кампанія й рядок outbox лягають однією транзакцією, а окремий `relay` уже розсіює лавину per-device задач у брокер.
- **Три свідки** — три сценарії, кожен друкує числа, у яких і сховані обіцянки статті: (а) перекодування атомарне із записом кліпа; (б) фан-аут на флот іде брокером, поки корінець атомарний; (в) випуск класу в брокер не чіпає жодного, хто кличе `enqueue`.

Головне про метод: свідком ми робимо не стан субстрату, а **вміст таблиць і черг після дії** — скільки рядків осіло, скільки повідомлень дійшло. Бо саме кількість осілого й псує розрив транзакції: коли перекодування зривається з базою, у світі лишається кліп без задачі або задача без кліпа — і це видно як число, а не як здогад.

## Ідея: субстрат ховається за швом, транзакція протікає крізь нього

Перш ніж писати, домовмося про два рішення, на яких стоїть увесь стенд.

**Перше — уніфікований субстрат.** Усі три бекенди й outbox-міст ховаються за одним інтерфейсом з єдиним методом `put(job, tx?)`. Тоді таблиця маршрутів — це просто словник «клас → обʼєкт із `put`», а `enqueue` — один рядок: знайти субстрат за класом і покласти. Виклику байдуже, хто там унизу; це і є [шов](root:progarch/seams-and-boundaries) у чистому вигляді — межа, за якою можна міняти реалізацію, не чіпаючи тих, хто по цей бік.

> 🔧 **Навіщо це.** Крос-лінк веде до кроку про шви: **шов** — це вузьке місце, де ти можеш підмінити те, що за ним, не переписуючи код по цей бік. Тут шов — `enqueue`; за ним ховаються субстрати. Прибери шов — і вибір субстрату для класу перестане бути правкою одного рядка й стане розкопуванням усього коду, що ставить задачі.

**Друге, і неочевидне, — транзакція протікає крізь шов.** Ось де вирішується доля атомарності. Коли задача народжується з бізнес-запису («залили кліп → перекодуй»), той, хто кличе `enqueue`, **уже тримає відкриту транзакцію** — ту саму, у якій він щойно вставив рядок про кліп. Він передає цю транзакцію в `enqueue` другим параметром, а бекенд-**база** вставляє рядок задачі **в неї ж**. Один `COMMIT` накриває обидва записи, один `ROLLBACK` викидає обидва. Памʼять і брокер параметр `tx` просто **ігнорують** — вони не транзакційні, і вдавати, ніби вони поділяють атомарність бази, було б брехнею.

А що з класами, які народжуються **не** із запису в тому ж запиті — місячний звіт, що його кладе cron? Той викликач транзакції не тримає, тож кличе `enqueue` без `tx`; а бекенд-база, не діставши чужої транзакції, відкриває **свою** й комітить сама. Один і той самий шов обслуговує обидва шляхи — атомарний-із-записом і самостійний — не роздвоюючись на два API. Ця дрібна деталь, необовʼязковий другий параметр, і несе всю вагу: вона робить клас багів «записали кліп, а перекодувати забули» не **виправленим**, а **невиразним** — його не можна висловити, бо два записи стали одним.

## Чесна модель бази: транзакція, що справді відкочується

Почнімо з фундаменту — крихітної, але правдивої бази. Її суть в одному: рядки, вставлені в межах транзакції, тримаються в **буфері** й стають видимі таблиці лише на `commit()`; `rollback()` цей буфер просто викидає. Без цієї чесності свідок (а) нічого не довів би.

:::tabs
```ts
// dh-jobs.ts — робочий маршрутизатор фонових задач DH.  Запуск: npx tsx dh-jobs.ts

type Row = Record<string, unknown>;

// Мінімальна, але ЧЕСНА модель БД: вставлене в транзакції видно лише після commit().
class Db {
  private tables = new Map<string, Row[]>();
  table(name: string): Row[] {
    if (!this.tables.has(name)) this.tables.set(name, []);
    return this.tables.get(name)!;                 // закомічені рядки цієї таблиці
  }
  begin(): Tx { return new Tx(this); }
}

class Tx {
  private staged: { table: string; row: Row }[] = [];   // буфер: ще НЕ закомічені вставки
  private done = false;
  constructor(private db: Db) {}
  insert(table: string, row: Row): void {
    if (this.done) throw new Error("транзакція вже завершена");
    this.staged.push({ table, row });              // просто складаємо в буфер — у таблицю ще нічого
  }
  commit(): void {
    if (this.done) throw new Error("подвійний commit");
    for (const { table, row } of this.staged)      // одним махом: усе або нічого
      this.db.table(table).push(row);
    this.done = true;
  }
  rollback(): void {
    this.staged = [];                              // викидаємо буфер — жоден рядок не осів
    this.done = true;
  }
}

// Ідіоматична обгортка: коміт на успіх, відкат на будь-який виняток.
function withTransaction(db: Db, body: (tx: Tx) => void): void {
  const tx = db.begin();
  try { body(tx); tx.commit(); }
  catch (e) { tx.rollback(); throw e; }            // впало до commit → нічого не осіло
}
```
```py
# dh_jobs.py — робочий маршрутизатор фонових задач DH.  Запуск: python dh_jobs.py
from contextlib import contextmanager
from dataclasses import dataclass
from types import SimpleNamespace


class Db:
    """Мінімальна, але ЧЕСНА модель БД: вставлене в транзакції видно лише після commit()."""
    def __init__(self):
        self.tables: dict[str, list[dict]] = {}

    def table(self, name: str) -> list[dict]:
        return self.tables.setdefault(name, [])     # закомічені рядки цієї таблиці

    def begin(self) -> "Tx":
        return Tx(self)


class Tx:
    def __init__(self, db: Db):
        self.db = db
        self.staged: list[tuple[str, dict]] = []    # буфер: ще НЕ закомічені вставки
        self.done = False

    def insert(self, table: str, row: dict) -> None:
        if self.done:
            raise RuntimeError("транзакція вже завершена")
        self.staged.append((table, row))            # просто складаємо в буфер — у таблицю ще нічого

    def commit(self) -> None:
        if self.done:
            raise RuntimeError("подвійний commit")
        for table, row in self.staged:              # одним махом: усе або нічого
            self.db.table(table).append(row)
        self.done = True

    def rollback(self) -> None:
        self.staged = []                            # викидаємо буфер — жоден рядок не осів
        self.done = True


@contextmanager
def transaction(db: Db):
    """Ідіоматична обгортка: коміт на успіх, відкат на будь-який виняток."""
    tx = db.begin()
    try:
        yield tx
        tx.commit()
    except Exception:
        tx.rollback()                               # впало до commit → нічого не осіло
        raise
```
:::

Зверніть увагу на симетрію керування транзакцією в двох мовах. У TypeScript це `withTransaction(db, body)` — обгортка навколо тіла: коміт, якщо тіло дійшло до кінця, відкат, якщо кинуло виняток. У Python — той самий візерунок природно лягає в **контекст-менеджер**: `with transaction(db) as tx: …`; `__exit__` комітить на щасливий вихід і відкочує, якщо всередині блока вибухнув виняток. Різні синтаксиси, та сама ідея: **межа транзакції збігається з межею блока коду**, і поза цією межею немає стану «половина записалась».

## Три бекенди: втратний, дефолтний, потужний

Тепер — субстрати. Кожен зводимо до **однієї** відмітної властивості, а решту (диск, мережу, підтвердження) відкидаємо, бо саме та одна властивість і вирішує долю задачі.

**Черга в памʼяті** зашила «нуль довговічності»: `put` штовхає задачу в масив, воркер її забирає, а на рестарті масив зникає разом із процесом. Параметр `tx` вона ігнорує — втратне не буває атомарним.

**Черга в базі** зашила головне — «постановка ділить транзакцію із записом-джерелом». Її `put`, діставши чужий `tx`, вставляє рядок задачі **в нього**; не діставши — відкриває свій. А `claimBatch` моделює те, як воркер забирає роботу: атомарно, так, щоб двом воркерам не дістався той самий рядок.

**Брокер** зашив «пропускну здатність і фічі»: кілька тем-черг, мертва черга для отруйних, доставка з ретраями. Транзакцію бази він не поділяє — і це чесно.

:::tabs
```ts
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
```
```py
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
```
:::

Одна деталь у `DbQueue` заслуговує на окрему увагу, бо в проді вона і є та межа, за якою база каже «досить». Наш `claimBatch` мітить рядки `running` синхронно, тож два воркери не візьмуть той самий. Справжня база робить це так:

```sql
-- Так воркер у проді забирає пачку готових задач БЕЗ гонки за рядок.
-- FOR UPDATE бере рядок під блокування; SKIP LOCKED каже «зайняте іншим — не чекай, пропусти».
UPDATE jobs
   SET state = 'running', locked_by = $worker, locked_at = now()
 WHERE id IN (
     SELECT id FROM jobs
      WHERE state = 'ready' AND run_after <= now()
      ORDER BY id
      FOR UPDATE SKIP LOCKED           -- Postgres 9.5+ (2016): пропустити вже зайняті рядки
      LIMIT $batch
 )
RETURNING id, cls, payload, key;
```

`FOR UPDATE SKIP LOCKED` зʼявився в PostgreSQL 9.5 (2016) саме під цей ужиток: кілька воркерів шлють той самий запит одночасно, і кожен дістає **свою** пачку невзятих задач, нікого не чекаючи й ні з ким не б’ючись за рядок. Без `SKIP LOCKED` воркери або стояли б у черзі за блокуванням (`FOR UPDATE` без пропуску **чекає**), або хапали б ті самі рядки й падали на конфлікті. Це та точка, де черга в базі перестає бути «нудним дефолтом» і стає майже безкоштовним, але справжнім субстратом — рівно доти, доки воркерів не стане так багато, що саме пропускання зайнятих почне коштувати; про цю стелю — у пастках.

## Outbox-міст: атомарний корінець, лавина в брокер

Найтонший субстрат — для викатки на флот. Вона народжується з бізнес-факту (адмін натиснув «оновити»), тож корінець-кампанію треба писати атомарно, як усе в базі. Але **лавину** з тисяч per-device задач гарячій таблиці `jobs` не віддають — її несе брокер. Як поєднати атомарність кореня з брокерним фан-аутом, не розриваючи транзакцію? Ось де вступає [outbox](topic:programming/outbox-pattern) — таблиця-черга в тій самій базі: `put` пише **рядок outbox** у ту саму транзакцію, що й корінець, а окремий `relay` уже читає **закомічені** рядки й розсіює лавину в брокер, мітячи розіслане.

> 🔧 **Навіщо це.** Крос-лінк веде до патерну outbox і **проблеми подвійного запису**: якби ми в транзакції кампанії ще й публікували напряму в брокер, то на збої одне з двох міг би не відбутися — база закомітилась, а публікація впала (або навпаки), і корінець розсинхронізувався б із флотом. Outbox прибирає цей клас: у транзакції ми чіпаємо **лише базу** (корінець + рядок outbox), а брокера торкаємось **після** коміту, з окремого процесу, який завжди може перечитати незіслане й досилати.

:::tabs
```ts
// ── МІСТ для класу «викатка на флот»: корінець-кампанія + рядок outbox
// однією транзакцією (атомарно з базою), а relay уже РОЗСІЮЄ лавину в брокер. ──
class OutboxBridge implements Substrate {
  constructor(private db: Db, private broker: Broker) {}
  put(job: Job, tx?: Tx): void {
    const row = { key: job.key, cls: job.cls, payload: job.payload, sent: false };
    if (tx) { tx.insert("outbox", row); return; }    // у ту саму транзакцію, що й корінець
    const own = this.db.begin(); own.insert("outbox", row); own.commit();
  }
  // Окремий relay: читає ЗАКОМІЧЕНІ невислані рядки, розгортає фан-аут у брокер, мітить sent.
  relay(): number {
    const pending = this.db.table("outbox").filter(r => r.sent === false);
    let fanned = 0;
    for (const r of pending) {
      const p = r.payload as { devices: string[]; image: string };
      for (const dev of p.devices) {                 // один outbox-рядок → задача на КОЖЕН пристрій
        this.broker.put({ cls: "fleetRollout", key: `${r.key}:${dev}`,
                          payload: { device: dev, image: p.image } });
        fanned++;
      }
      r.sent = true;                                  // цей рядок розсіяно — вдруге не візьмемо
    }
    return fanned;
  }
}
```
```py
# ── МІСТ для класу «викатка на флот»: корінець-кампанія + рядок outbox
# однією транзакцією (атомарно з базою), а relay уже РОЗСІЮЄ лавину в брокер. ──
class OutboxBridge:
    def __init__(self, db: Db, broker: Broker):
        self.db = db
        self.broker = broker

    def put(self, job: Job, tx: Tx | None = None) -> None:
        row = {"key": job.key, "cls": job.cls, "payload": job.payload, "sent": False}
        if tx is not None:
            tx.insert("outbox", row)          # у ту саму транзакцію, що й корінець
            return
        own = self.db.begin()
        own.insert("outbox", row)
        own.commit()

    def relay(self) -> int:
        # Окремий relay: читає ЗАКОМІЧЕНІ невислані рядки, розгортає фан-аут у брокер, мітить sent.
        pending = [r for r in self.db.table("outbox") if not r["sent"]]
        fanned = 0
        for r in pending:
            p = r["payload"]
            for dev in p["devices"]:          # один outbox-рядок → задача на КОЖЕН пристрій
                self.broker.put(Job("fleetRollout", {"device": dev, "image": p["image"]},
                                    f'{r["key"]}:{dev}'))
                fanned += 1
            r["sent"] = True                  # цей рядок розсіяно — вдруге не візьмемо
        return fanned
```
:::

Зверніть увагу, що `relay` кличе `broker.put` **напряму**, а не через шов `enqueue`: розгортання лавини — це внутрішня механіка транспорту, а не постановка нового класу роботи, тож повторно маршрутизувати її нема потреби (та й вийшла б петля). Шов лишається для тих, хто **ставить** задачу; relay — для того, хто її **несе далі**.

## Шов і таблиця маршрутів: єдине місце, де клас зустрічає субстрат

Тепер зшиваємо все в один вузол. Ось воно — серце статті в коді: три бекенди й міст створюються раз, таблиця маршрутів привʼязує кожен клас до субстрату, а `enqueue` у два рядки ховає все це від викликача.

:::tabs
```ts
// ── ОДИН ШОВ + таблиця маршрутів (ЄДИНЕ місце, де клас зустрічає субстрат) ──
function makeSystem() {
  const db     = new Db();
  const broker = new Broker();
  const dbQueue = new DbQueue(db);
  const outbox  = new OutboxBridge(db, broker);

  const route: Record<JobClass, Substrate> = {
    cacheWarm:    new MemoryQueue(),  // втратне — хай гине на рестарті
    transcode:    dbQueue,            // народжене із записом кліпа → атомарно в тій же транзакції
    notify:       dbQueue,            // теж із бізнес-запису → дефолт
    report:       dbQueue,            // cron кладе сюди ж (без tx — свій)
    fleetRollout: outbox,             // корінець у базі атомарно, relay розсіює в брокер
    telemetry:    broker,             // потік із пристроїв — не для гарячої таблиці jobs
  };

  const enqueue = (job: Job, tx?: Tx): void => { route[job.cls].put(job, tx); };
  return { db, broker, outbox, route, enqueue };   // виклику байдуже, який субстрат унизу
}
```
```py
# ── ОДИН ШОВ + таблиця маршрутів (ЄДИНЕ місце, де клас зустрічає субстрат) ──
def make_system():
    db = Db()
    broker = Broker()
    db_queue = DbQueue(db)
    outbox = OutboxBridge(db, broker)

    route = {
        "cacheWarm":    MemoryQueue(),  # втратне — хай гине на рестарті
        "transcode":    db_queue,       # народжене із записом кліпа → атомарно в тій же транзакції
        "notify":       db_queue,       # теж із бізнес-запису → дефолт
        "report":       db_queue,       # cron кладе сюди ж (без tx — свій)
        "fleetRollout": outbox,         # корінець у базі атомарно, relay розсіює в брокер
        "telemetry":    broker,         # потік із пристроїв — не для гарячої таблиці jobs
    }

    def enqueue(job: Job, tx: Tx | None = None) -> None:
        route[job.cls].put(job, tx)     # виклику байдуже, який субстрат унизу

    return SimpleNamespace(db=db, broker=broker, outbox=outbox, route=route, enqueue=enqueue)
```
:::

Уся карта з таблиці статті тепер живе в одному словнику `route`. Дві дрібниці — у памʼять, три класи — у базу-дефолт, викатка — в outbox-міст, телеметрія — у брокер. І це **єдине** місце в системі, де клас роботи знає імʼя свого субстрату; усюди інде код кличе просто `enqueue(job)` й нічого про субстрати не відає. Далі три свідки покажуть, що з цього виходить.

## Свідок (а): перекодування живе й гине разом із кліпом

Перший сценарій — найпростіший і найважливіший. Заливаємо кліп: у транзакції вставляємо бізнес-запис про нього й тут же ставимо задачу перекодування — **в ту саму транзакцію**. Раз проганяємо зі збоєм до коміту, раз — до кінця.

:::tabs
```ts
function uploadClip(sys: ReturnType<typeof makeSystem>, clipId: string, crash: boolean): void {
  try {
    withTransaction(sys.db, (tx) => {
      tx.insert("clips", { id: clipId, state: "raw" });                       // бізнес-запис
      sys.enqueue({ cls: "transcode", key: `transcode:${clipId}`,
                    payload: { clipId } }, tx);                               // задача В ТУ САМУ tx
      if (crash) throw new Error("збій перекодувального пайплайна до commit");
    });
  } catch { /* транзакція вже відкотилась у withTransaction */ }
}

const sys = makeSystem();
const count = (t: string) => sys.db.table(t).length;

uploadClip(sys, "clip-A", true);                                             // впало по дорозі
console.log("після ВІДКАТУ →  clips:", count("clips"), " jobs:", count("jobs"));
uploadClip(sys, "clip-B", false);                                           // дійшло до кінця
console.log("після COMMIT  →  clips:", count("clips"), " jobs:", count("jobs"));
```
```py
def upload_clip(sys, clip_id: str, crash: bool) -> None:
    try:
        with transaction(sys.db) as tx:
            tx.insert("clips", {"id": clip_id, "state": "raw"})                 # бізнес-запис
            sys.enqueue(Job("transcode", {"clip_id": clip_id},
                            f"transcode:{clip_id}"), tx)                        # задача В ТУ САМУ tx
            if crash:
                raise RuntimeError("збій перекодувального пайплайна до commit")
    except RuntimeError:
        pass  # транзакція вже відкотилась у контекст-менеджері


sys = make_system()
count = lambda t: len(sys.db.table(t))

upload_clip(sys, "clip-A", True)                                             # впало по дорозі
print("після ВІДКАТУ →  clips:", count("clips"), " jobs:", count("jobs"))
upload_clip(sys, "clip-B", False)                                           # дійшло до кінця
print("після COMMIT  →  clips:", count("clips"), " jobs:", count("jobs"))
```
:::

Запусти будь-яку версію — числа ті самі:

```
після ВІДКАТУ →  clips: 0  jobs: 0
після COMMIT  →  clips: 1  jobs: 1
```

Прочитаймо повільно. Рядок відкату — і є вся суть: пайплайн вибухнув **після** того, як обидва записи лягли в буфер, але **до** коміту, і зникли обидва. Немає осиротілого кліпа, що чекає на перекодування, яке ніколи не прийде; немає задачі, що вказує на кліп, якого нема. Рядок коміту — обидва осіли разом. І — ось де доказ — немає **третього й четвертого** рядка: не буває `clips: 1  jobs: 0` чи `clips: 0  jobs: 1`, бо шов поклав вставку задачі в ту саму транзакцію, що й вставку кліпа, а в транзакції рівно два кінці. Клас багів «записали кліп, а перекодувати забули» тут не полагоджено — його **неможливо висловити**.

## Свідок (б): фан-аут іде брокером, корінець лишається атомарним

Тепер тонше. Запускаємо викатку на п’ять пристроїв: у транзакції — корінець-кампанія й (через шов, отже, в outbox-міст) рядок outbox. Дивимось на брокер до й після relay.

:::tabs
```ts
function launchRollout(sys: ReturnType<typeof makeSystem>, id: string,
                       image: string, devices: string[], crash: boolean): void {
  try {
    withTransaction(sys.db, (tx) => {
      tx.insert("campaigns", { id, image, state: "launched" });               // корінець-кампанія
      sys.enqueue({ cls: "fleetRollout", key: `rollout:${id}`,
                    payload: { devices, image } }, tx);                       // → outbox у ТІЙ ЖЕ tx
      if (crash) throw new Error("збій до commit");
    });
  } catch { /* відкотилось */ }
}

const sys = makeSystem();
const count = (t: string) => sys.db.table(t).length;
const fleet = ["dev-1", "dev-2", "dev-3", "dev-4", "dev-5"];

launchRollout(sys, "camp-X", "fw-2.0", fleet, true);                         // невдала спроба
console.log("ВІДКАТ кампанії → campaigns:", count("campaigns"),
            " outbox:", count("outbox"), " брокер:", sys.broker.depth("fleetRollout"));

launchRollout(sys, "camp-Y", "fw-2.0", fleet, false);                        // успішний запуск
console.log("COMMIT кампанії → campaigns:", count("campaigns"),
            " брокер ДО relay:", sys.broker.depth("fleetRollout"));

const fanned = sys.outbox.relay();                                          // relay розсіює лавину
console.log("після relay    → фан-аут у брокер:", fanned,
            " брокер:", sys.broker.depth("fleetRollout"));
```
```py
def launch_rollout(sys, campaign_id: str, image: str, devices: list[str], crash: bool) -> None:
    try:
        with transaction(sys.db) as tx:
            tx.insert("campaigns", {"id": campaign_id, "image": image, "state": "launched"})  # корінець
            sys.enqueue(Job("fleetRollout", {"devices": devices, "image": image},
                            f"rollout:{campaign_id}"), tx)                    # → outbox у ТІЙ ЖЕ tx
            if crash:
                raise RuntimeError("збій до commit")
    except RuntimeError:
        pass  # відкотилось


sys = make_system()
count = lambda t: len(sys.db.table(t))
fleet = ["dev-1", "dev-2", "dev-3", "dev-4", "dev-5"]

launch_rollout(sys, "camp-X", "fw-2.0", fleet, True)                         # невдала спроба
print("ВІДКАТ кампанії → campaigns:", count("campaigns"),
      " outbox:", count("outbox"), " брокер:", sys.broker.depth("fleetRollout"))

launch_rollout(sys, "camp-Y", "fw-2.0", fleet, False)                        # успішний запуск
print("COMMIT кампанії → campaigns:", count("campaigns"),
      " брокер ДО relay:", sys.broker.depth("fleetRollout"))

fanned = sys.outbox.relay()                                                 # relay розсіює лавину
print("після relay    → фан-аут у брокер:", fanned,
      " брокер:", sys.broker.depth("fleetRollout"))
```
:::

```
ВІДКАТ кампанії → campaigns: 0  outbox: 0  брокер: 0
COMMIT кампанії → campaigns: 1  брокер ДО relay: 0
після relay    → фан-аут у брокер: 5  брокер: 5
```

Три рядки — три сцени. **Відкат**: упала кампанія — і зник не лише корінець, а й рядок outbox; запиту на фан-аут ніби й не було, тож relay нема чого нести, брокер порожній. Атомарність тримає обидва кінці й тут. **Коміт**: корінець осів (`campaigns: 1`) — але брокер **ще порожній**. Це і є суть outbox: фан-аут **не** стався всередині транзакції. Ми не публікували в брокер із-під `COMMIT` бази (це й був би подвійний запис — база закомітилась, а публікація могла б не пройти). Ми атомарно закомітили **один рядок outbox** поруч із корінцем — і по всьому. **Після relay**: окремий процес прочитав той закомічений рядок і розсіяв **пʼять** per-device задач у брокер. Корінець сплатив свою атомарність у базі, де вона важить; лавина сплатила свою пропускну здатність брокеру, де важить вона; жоден не платив за іншого.

![Outbox-міст класу викатки на флот. Ліворуч — зелений контейнер «ОДНА ТРАНЗАКЦІЯ» з двома записами всередині: «campaigns — корінець кампанії» та «outbox — рядок фан-ауту (sent=false)»; під контейнером підпис «COMMIT — обидва разом; ROLLBACK — жодного». Стрілка від транзакції веде праворуч до синього блока «relay — окремий процес» із приміткою «читає ЗАКОМІЧЕНІ невислані рядки, мітить sent=true». Далі стрілка до бурштинового блока «брокер — тема fleetRollout», а від нього віяло стрілок до пʼятьох дрібних блоків dev-1…dev-5 із приміткою «один outbox-рядок → задача на КОЖЕН пристрій». Унизу висновок: корінець атомарний у базі, лавину несе брокер ПІСЛЯ commit — не гаряча таблиця jobs](img/outbox-bridge.svg)
*Чому виходять саме ці числа. Корінець і рядок outbox лежать в одній транзакції — тому на відкоті зникають разом, а на коміті осідають разом (звідси «campaigns: 1, брокер: 0»). І лише окремий relay, уже після коміту, розгортає один рядок outbox у пʼять брокерних задач — звідси «фан-аут: 5». Транзакція чіпає тільки базу; брокера торкається relay, який завжди може перечитати незіслане.*

## Свідок (в): випуск класу в брокер — правка одного рядка

Останній сценарій доводить обіцянку зворотності. Клас `notify` стартував у базі-дефолті. Кладемо одне сповіщення — воно осідає в таблиці `jobs`. Потім потік сповіщень нібито виріс, і ми **випускаємо** клас у брокер: міняємо в маршруті рівно один рядок — і той **самий** виклик `enqueue` тепер лягає в брокер.

:::tabs
```ts
const sys = makeSystem();
const count = (t: string) => sys.db.table(t).length;

// notify ще в базі-дефолті — сповіщення осідає в таблиці jobs:
sys.enqueue({ cls: "notify", key: "notify:smoke-1", payload: { kind: "smoke" } });
console.log("notify ДО випуску   → jobs у базі:", count("jobs"),
            " брокер notify:", sys.broker.depth("notify"));

sys.route.notify = sys.broker;   // ← ЄДИНА правка; жоден виклик enqueue не чіпаємо

// той САМИЙ виклик — тепер їде брокером:
sys.enqueue({ cls: "notify", key: "notify:smoke-2", payload: { kind: "smoke" } });
console.log("notify ПІСЛЯ випуску → jobs у базі:", count("jobs"),
            " брокер notify:", sys.broker.depth("notify"));
```
```py
sys = make_system()
count = lambda t: len(sys.db.table(t))

# notify ще в базі-дефолті — сповіщення осідає в таблиці jobs:
sys.enqueue(Job("notify", {"kind": "smoke"}, "notify:smoke-1"))
print("notify ДО випуску   → jobs у базі:", count("jobs"),
      " брокер notify:", sys.broker.depth("notify"))

sys.route["notify"] = sys.broker   # ← ЄДИНА правка; жоден виклик enqueue не чіпаємо

# той САМИЙ виклик — тепер їде брокером:
sys.enqueue(Job("notify", {"kind": "smoke"}, "notify:smoke-2"))
print("notify ПІСЛЯ випуску → jobs у базі:", count("jobs"),
      " брокер notify:", sys.broker.depth("notify"))
```
:::

```
notify ДО випуску   → jobs у базі: 1  брокер notify: 0
notify ПІСЛЯ випуску → jobs у базі: 1  брокер notify: 1
```

До випуску сповіщення лягло в базу (`jobs: 1`). Ми міняємо **один** рядок — `route.notify = broker` — і кличемо той самий `enqueue({cls:"notify", …})`. Лічильник бази не зрушив (там усе ще та, стара задача), а тема `notify` у брокері тепер тримає нову. **Жоден** виклик `enqueue` не змінився — викликачі ніколи не знали субстрату й далі не знають. Оскільки таблиця маршрутів — єдине місце, де клас зустрічає субстрат, переставити клас — це правка одного рядка, і двобічні двері зі статті справжні: угору в брокер по пропускну здатність, униз назад у базу, якщо профіль навантаження виявився не той, — обидва напрями дешеві.

## Складність і пастки

Стенд чесний рівно доти, доки бачиш, чого він **не** показує. Ось де реальність жорсткіша — і чому кожне спрощення важить.

### At-least-once: обробник мусить витримати повтор

Наш брокер віддає задачу, а якщо обробник кинув — пробує ще, і лише після кількох спроб паркує в DLQ. Але **успішний** обробник у нас викликається рівно раз. У проді це не так: воркер, що вихопив задачу й **упав, не підтвердивши** її, побачить, як задачу віддадуть іншому — і вона виконається **двічі**. Це не аварія брокера, а його гарантія: [«щонайменше раз»](topic:programming/delivery-guarantees) означає, що після збою повідомлення доправлять повторно. Звідси залізне: обробник мусить бути **ідемпотентним** — виконаний двічі, він не має шкодити. Перекодування пише результат у адресований за вмістом шлях і пропускає, якщо той уже є; списання грошей звіряється з ключем ідемпотентності (ось навіщо в `Job` поле `key`) і другий раз не списує.

> 🔧 **Навіщо це.** Різниця «щонайменше раз» проти «фактично раз» — не бюрократія, а те, що вирішує, чи впаде твоя фонова обробка з подвоєним рахунком. Проєктуючи будь-який `enqueue`-шлях DH — перекодування, звіт, розсилку, — став собі одне питання: що станеться, якщо ця задача виконається двічі? «Нічого страшного» — ти вже ідемпотентний; «подвійне списання» — тобі потрібен ключ ідемпотентності, і закласти його краще зараз, а не після першого дубля в проді.

### Отруйне повідомлення: без DLQ воно вклинюється навіки

Що станеться з задачею, яка падає **завжди** — зіпсований payload, неможливий формат? Наївний брокер вертав би її в чергу нескінченно, і вона або крутилась би вічно, зжираючи воркерів, або, ще гірше, вклинилась би в голову черги, спинивши весь клас за собою. Наш `deliver` ловить це: після `maxTries` спроб він паркує задачу в [мертву чергу (DLQ)](topic:programming/dead-letter-queue) й іде далі. Покажемо — чотири задачі, одна з яких отруйна:

:::tabs
```ts
const sys = makeSystem();
for (let i = 0; i < 4; i++)
  sys.broker.put({ cls: "notify", key: `n-${i}`, payload: { i } });

const processed = new Set<string>();
let attempts = 0;
sys.broker.deliver("notify", (job) => {
  attempts++;
  if ((job.payload as { i: number }).i === 2) throw new Error("otruta: несправний payload");
  if (processed.has(job.key)) return;                 // ідемпотентність: дубль — нічого
  processed.add(job.key);
});
console.log("оброблено:", processed.size, " спроб:", attempts, " DLQ:", sys.broker.dlq.length);
```
```py
sys = make_system()
for i in range(4):
    sys.broker.put(Job("notify", {"i": i}, f"n-{i}"))

processed: set[str] = set()
attempts = 0


def handle(job):
    global attempts
    attempts += 1
    if job.payload["i"] == 2:
        raise RuntimeError("otruta: несправний payload")
    if job.key in processed:                          # ідемпотентність: дубль — нічого
        return
    processed.add(job.key)


sys.broker.deliver("notify", handle)
print("оброблено:", len(processed), " спроб:", attempts, " DLQ:", len(sys.broker.dlq))
```
:::

```
оброблено: 3  спроб: 6  DLQ: 1
```

Три здорові задачі оброблено по разу. Отруйну (`i=2`) пробували три рази (звідси `6 = 1+1+3+1` спроб) і після третього провалу відклали в DLQ (`1`), щоб вона перестала блокувати клас. DLQ — не смітник, а **поличка на розгляд**: людина дивиться, чому payload несправний, лагодить причину й за потреби відправляє задачу назад. Без цієї полички один зіпсований запис здатен покласти цілий клас роботи.

### Контенція SKIP LOCKED: сама черга й стає стелею

`SKIP LOCKED` дає воркерам тягти паралельно без гонки за рядок — але не задарма при зростанні числа воркерів. Коли їх десятки, усі скануть **ту саму** голову таблиці `jobs`, і кожен **пропускає** рядки, вже взяті іншими; саме це пропускання коштує сканів, а гаряча таблиця під безперервним `UPDATE … RETURNING` ще й тисне на автовакуум і роздуває мертві версії рядків. До певної межі індекс по `state='ready'` і забір пачками це тримають дешево. Але за нею гарячий обіг `jobs` починає заважати самому Postgres, що обслуговує бізнес, — і це рівно та третя точка зі статті, де клас **переростає базу за пропускною** й проситься в брокер. Іншими словами, наш `DbQueue` — чудовий дефолт саме доти, доки конкретний клас не вперся в цю стелю; коли вперся — його випускають одним рядком маршруту, як `notify` у свідку (в).

### Що ховає стенд

Наша транзакція синхронна й не може «розірватись посеред коміту» — справжня дворядкова вставка комітиться атомарно на рівні бази, але між сервісами атомарності вже нема, і саме тому потрібен outbox. Буфери в нас безмежні — справжній брокер тисне на видавця (backpressure) або накопичує лаг, коли споживач не встигає. Мережі нема — а з нею приходять таймаути, часткові збої й переупорядкування. Числа в нас детерміновані — у проді той самий механізм ховається за шумом, і розірвана транзакція проявляється не чистим `1/0`, а рідкісним «інколи кліп без перекодування», який місяцями списують на будь-що інше. Стенд називає причину до того, як прод покаже симптом; у цьому його цінність, а не в тому, що він «як справжній».

## Що лишається в руках

Ми взяли три обіцянки, що в статті звучали як твердження, і зробили їх вимірюваними. Атомарність перекодування — не віра, а `clips:1 jobs:1` проти `clips:0 jobs:0`, без третього результату. Брокерний фан-аут із атомарним корінцем — не гасло, а `campaigns:1, брокер:0` до relay й `брокер:5` після, де видно рівно, що транзакція чіпає лише базу, а лавину несе окремий процес. Зворотність вибору — не обіцянка «двобічних дверей», а одна змінена стрічка `route.notify = broker`, від якої не здригнувся жоден викликач.

А під трьома свідками — один хід думки, ширший за цей код. Ми жодного разу не питали субстрат, чи він «правильний»; ми питали **систему після дії** — що осіло в таблицях і що дійшло в черги, — бо саме кількість осілого й псує неправильний вибір субстрату. І винесли єдину точку, крізь яку все проходить, — шов `enqueue` із протягнутою крізь нього транзакцією, — так, що атомарність стала невиразним для бага станом, а не заплатою. Будуєш постановку роботи будь-де: спершу постав шов і протягни крізь нього транзакцію тих, хто народжений із запису; тоді вибір субстрату для кожного класу лишиться олівцевим, а найдорожчий клас багів — «зробили половину» — просто не матиме як статися.
