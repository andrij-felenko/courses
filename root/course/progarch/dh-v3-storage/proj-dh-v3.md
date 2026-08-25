# ⚙️ Повний DH v3: реєстр на диску, агрегат в одній транзакції, і тест, що це доводить

Кістяк у статті показав **рішення** — переселити правду з крихкої памʼяті на тривкий диск, лишивши порт на місці. Але кістяк тим і зручний, що на ньому все гладко: схема стояла двома фрагментами з `( ... )` замість тіла, `SqliteDeviceRepository` мав транзакцію, але не мав `load`, накатник міграцій згадувався одним реченням, порт `TelemetrySink` був названий, та не показаний, а головні три обіцянки версії — «реєстр переживе рестарт», «агрегат ляже весь або ніяк», «тариф не перевищити під конкуренцією» — лишалися **словами**. Цей розбір добудовує все й притискає кожну обіцянку до стіни зеленим тестом.

І одразу відмежуймося від двох сусідів у цьому ж модулі, бо всі троє чіпають SQLite і легко зливаються в одне. [Розбір про тривкий репозиторій](root:progarch/dh-data-persistence/proj-durable-repository.md) довів вужчу річ: що сховище **взагалі** переживає перезапуск — один порт, дві реалізації, доказ через закриття й повторне відкриття над тим самим файлом. [Розбір про гарантії](root:progarch/dh-storage-guarantees/proj-dh-guarantees.md) крутив **чотири важелі** окремо під кожен клас фактів і вчив головного уроку — що `kill` процесу доводить не те саме, що відмова живлення. Тут задача **третя**: не «зробити тривко» й не «виставити важелі», а **зібрати всю v3 докупи** — схему, репозиторій за незрушеним портом, накатник міграцій зі своєю історією, відкладений шов телеметрії — і довести саме **три обіцянки версії** одним набором тестів. Причому вартовий тут інший, ніж у сусіда: не бюджет нагріву, а **слоти пристроїв за тарифом** — `used_slots < device_cap`.

## Задача: один файл, що збирається, накочується й доводить себе

Випишімо ціль без прикрас. Той самий один файл `dh.db` має нести весь реєстр Digital Homes і зібратися в робочий шар сховища, у якому:

- **уся схема** живе трьома таблицями — `home` (корінь із тарифом і лічильником слотів), `device` (пристрій, привʼязаний до дому зовнішнім ключем) і `measurement` (телеметрія, окремим слотом поза межею агрегату);
- **`SqliteDeviceRepository`** стоїть за **тим самим** портом `DeviceRepository`, що [заклали у v2](root:progarch/dh-v2-hexagon), і зберігає та піднімає **весь агрегат** — дім із його пристроями — однією транзакцією;
- **накатник міграцій** веде табличку `schema_version` і накочує пронумеровані кроки по черзі, причому міграція 001 — це і є переїзд реєстру з RAM на диск;
- **порт `TelemetrySink`** стоїть відкладеним швом на місці майбутнього розлому — сьогодні за ним реляційна затичка, завтра стане окреме сховище;
- **тест-набір** зеленим доводить рівно три речі: реєстр переживає рестарт, агрегат лягає атомарно (rollback на збої посеред циклу запису пристроїв), а атомний вартовий не дає перевищити тариф навіть під натовпом писарів.

Кожну обіцянку доводить не наше слово, а тест, який неможливо підробити.

## Ідея: правда переселяється, порт стоїть, схема має історію

Уся збірка тримається на трьох простих думках, і жодна з них не нова — усі виточені попередніми кроками, а тут лише стуляються без шва.

Перша: **правду переселяємо, а не вигадуємо наново.** Реєстр, власники, поріг уже жили у [`InMemoryDeviceRepository`](root:progarch/dh-v2-hexagon); v3 бере той самий вміст і кладе його туди, де рестарт його не зжере. Тому й порт не рухається: [заміна адаптера коштує один рядок у точці збірки](root:progarch/dh-data-persistence), бо форму під неї заклали заздалегідь.

Друга: **межа агрегату стає межею транзакції.** Ми ще в [моделі даних](root:progarch/dh-data-model) домовилися, що дім із пристроями зберігають як [ціле](root:sf-apps/aggregates-consistency). Реляційно він розсипаний на два рядки в двох таблицях, тож обіцянку «весь або ніяк» тримає не схема, а `BEGIN … COMMIT` навколо всього запису.

Третя: **схема не застигає — вона еволюціонує дисципліновано.** Правити бойову базу руками означає рано чи пізно мати дві копії у двох формах і не памʼятати, яка правильна. Тому кожна зміна схеми — [пронумерована міграція](root:sf-data/database-migrations), і саме переїзд «RAM → диск» стає першим записом в її історії.

Далі — код, у якому ці три думки стають рядками.

## Схема: три таблиці, дві природи

Почнімо зі схеми, бо це [найдовговічніший артефакт системи](root:sf-data/relational-model) — код перепишуть тричі, а таблиці лишаться. Три таблиці, і поділені вони рівно так, як поділений домен:

```sql
-- РЕЄСТР: джерело правди дому. Корінь агрегату.
CREATE TABLE home (
    id          TEXT PRIMARY KEY,
    owner_id    TEXT    NOT NULL,
    plan        TEXT    NOT NULL DEFAULT 'free',              -- тариф
    device_cap  INTEGER NOT NULL DEFAULT 5,                   -- скільки слотів дає тариф
    used_slots  INTEGER NOT NULL DEFAULT 0 CHECK (used_slots >= 0),
    threshold   REAL    NOT NULL DEFAULT 20.0,                -- поріг опалення
    CHECK (used_slots <= device_cap)                          -- лічильник НЕ переростає межу
);

-- ПРИСТРІЙ: дитина агрегату. Живе й зберігається разом із коренем.
CREATE TABLE device (
    id         TEXT PRIMARY KEY,                              -- один фізичний давач — один рядок
    home_id    TEXT NOT NULL REFERENCES home(id) ON DELETE CASCADE,   -- сирота неможливий
    kind       TEXT NOT NULL CHECK (kind IN ('lock','thermostat','plug','sensor')),
    room       TEXT NOT NULL,
    state      TEXT NOT NULL,
    paired_at  TEXT NOT NULL
);

-- ТЕЛЕМЕТРІЯ: інша природа запису. ПОЗА агрегатом реєстру.
CREATE TABLE measurement (
    device_id  TEXT NOT NULL,
    ts         REAL NOT NULL,
    value      REAL NOT NULL,
    PRIMARY KEY (device_id, ts)                               -- один показ на давач у мить
);
```

Придивімося, скільки правил дому тут стало **фізично нездоланними**, а не записаними в чиїйсь голові. `REFERENCES home(id)` означає, що пристрій без наявного дому не завести — база сама відмовить. `CHECK (used_slots <= device_cap)` — це другий пояс під тариф: навіть якби наш вартовий колись прогледів, база не запише лічильник понад межу. `CHECK (kind IN …)` не дасть протекти пристрою невідомого роду. Кожне таке обмеження — це «ні», яке база каже **замість нас** і **завжди**, зокрема тому писареві, про існування якого ми ще не знаємо.

І помітьмо головний розкол схеми: `measurement` стоїть **окремо** й **поза** агрегатом. Це не випадковість, а записана в структуру відповідь на питання «що з чим неподільне». Реєстр — точкові транзакційні читання на скромному обсязі; телеметрія — лавина вставок. Дві різні роботи, тож дві різні комірки: агрегат `home`+`device` лягає однією транзакцією, а `measurement` доливається поза нею, за окремим портом. Схема — це не просто «де байти», а карта того, що зобовʼязане бути істинним в одну мить.

> 🔧 **Навіщо це.** `used_slots` на корені — тонка деталь, у якій уся суть кроку про [останній квиток](root:progarch/last-ticket-race). Це **лічильник із межею**, і межу стереже не `if` у застосунку, а атомний вартовий у мить запису. Тому лічильник живе на диску, поруч із `device_cap`, а не в памʼяті сервіса: суддя інваріанта мусить бачити свіже значення там, де воно справді лежить, а не застарілий знімок у чиємусь процесі.

## Накатник міграцій: у схеми зʼявляється історія

Найпідступніша спокуса — вважати схему вироком навіки й правити її руками, коли треба щось додати. Так народжуються дві бази у двох формах. Ліки — вести зміну схеми **пронумерованими міграціями**, кожна з яких сама себе описує, а база памʼятає, до якої вже дійшла. Ця память — окрема таблиця `schema_version`:

:::tabs
```py
import sqlite3, datetime

def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

# Історія схеми: (версія, нотатка, список операторів). Порядок — за версією, залізно.
MIGRATIONS: list[tuple[int, str, list[str]]] = [
    (1, "реєстр DH переїжджає з памʼяті на диск", [
        """CREATE TABLE home (
               id TEXT PRIMARY KEY, owner_id TEXT NOT NULL,
               plan TEXT NOT NULL DEFAULT 'free',
               device_cap INTEGER NOT NULL DEFAULT 5,
               used_slots INTEGER NOT NULL DEFAULT 0 CHECK (used_slots >= 0),
               threshold  REAL NOT NULL DEFAULT 20.0,
               CHECK (used_slots <= device_cap))""",
        """CREATE TABLE device (
               id TEXT PRIMARY KEY,
               home_id TEXT NOT NULL REFERENCES home(id) ON DELETE CASCADE,
               kind TEXT NOT NULL CHECK (kind IN ('lock','thermostat','plug','sensor')),
               room TEXT NOT NULL, state TEXT NOT NULL, paired_at TEXT NOT NULL)""",
    ]),
    (2, "телеметрія дістає власну таблицю (за портом TelemetrySink)", [
        """CREATE TABLE measurement (
               device_id TEXT NOT NULL, ts REAL NOT NULL, value REAL NOT NULL,
               PRIMARY KEY (device_id, ts))""",
    ]),
    # (3, "годинник останньої активності", ["ALTER TABLE device ADD COLUMN last_seen TEXT"]),
]

def run_migrations(conn: sqlite3.Connection) -> int:
    """Накотити всі міграції, яких ще нема на цій базі. Ідемпотентно: повторний виклик — no-op."""
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version ("
                 "  version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL, note TEXT)")
    current = conn.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version").fetchone()[0]
    for version, note, statements in sorted(MIGRATIONS, key=lambda m: m[0]):   # ← ПОРЯДОК
        if version <= current:
            continue                             # уже накатано — пропускаємо
        conn.execute("BEGIN")                    # схема Й відмітка версії — в ОДНІЙ транзакції
        try:
            for sql in statements:
                conn.execute(sql)
            conn.execute("INSERT INTO schema_version(version, applied_at, note) VALUES(?,?,?)",
                         (version, _now(), note))
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")             # напів-накоченої схеми не існує
            raise
    return conn.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version").fetchone()[0]
```
```ts
import { DatabaseSync } from "node:sqlite";       // вбудований у Node ≥ 22.5

const now = () => new Date().toISOString();

// Історія схеми: [версія, нотатка, оператори]. Порядок — за версією, залізно.
const MIGRATIONS: [number, string, string[]][] = [
  [1, "реєстр DH переїжджає з памʼяті на диск", [
    `CREATE TABLE home (
        id TEXT PRIMARY KEY, owner_id TEXT NOT NULL,
        plan TEXT NOT NULL DEFAULT 'free',
        device_cap INTEGER NOT NULL DEFAULT 5,
        used_slots INTEGER NOT NULL DEFAULT 0 CHECK (used_slots >= 0),
        threshold  REAL NOT NULL DEFAULT 20.0,
        CHECK (used_slots <= device_cap))`,
    `CREATE TABLE device (
        id TEXT PRIMARY KEY,
        home_id TEXT NOT NULL REFERENCES home(id) ON DELETE CASCADE,
        kind TEXT NOT NULL CHECK (kind IN ('lock','thermostat','plug','sensor')),
        room TEXT NOT NULL, state TEXT NOT NULL, paired_at TEXT NOT NULL)`,
  ]],
  [2, "телеметрія дістає власну таблицю (за портом TelemetrySink)", [
    `CREATE TABLE measurement (
        device_id TEXT NOT NULL, ts REAL NOT NULL, value REAL NOT NULL,
        PRIMARY KEY (device_id, ts))`,
  ]],
  // [3, "годинник останньої активності", ["ALTER TABLE device ADD COLUMN last_seen TEXT"]],
];

function runMigrations(db: DatabaseSync): number {   // ідемпотентно: повторний виклик — no-op
  db.exec("CREATE TABLE IF NOT EXISTS schema_version ("
        + "  version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL, note TEXT)");
  const current = db.prepare(
    "SELECT COALESCE(MAX(version), 0) AS v FROM schema_version").get() as { v: number };
  const ins = db.prepare("INSERT INTO schema_version(version, applied_at, note) VALUES(?,?,?)");
  for (const [version, note, statements] of [...MIGRATIONS].sort((a, b) => a[0] - b[0])) {
    if (version <= current.v) continue;              // уже накатано — пропускаємо
    db.exec("BEGIN");                                // схема Й відмітка — в ОДНІЙ транзакції
    try {
      for (const sql of statements) db.exec(sql);
      ins.run(version, now(), note);
      db.exec("COMMIT");
    } catch (e) { db.exec("ROLLBACK"); throw e; }    // напів-накоченої схеми не існує
  }
  return (db.prepare("SELECT COALESCE(MAX(version),0) AS v FROM schema_version")
            .get() as { v: number }).v;
}
```
:::

Розберімо, що тут несе вагу, бо кожен рядок — рішення.

**`schema_version` — це память бази про саму себе.** Перед накатом ми читаємо `MAX(version)` — найвищу вже накочену міграцію — і крутимо лише ті, що **вище** за неї. Тому `run_migrations` можна викликати скільки завгодно разів: на свіжій базі він накотить обидві, на вже накоченій — не зробить нічого. Ця **ідемпотентність** (від лат. *idem* — той самий, *potens* — здатний: скільки не повторюй, результат один) — не примха, а те, на чому тримається рестарт: застосунок гукає `run_migrations` на **кожному** старті, і це безпечно.

**Схема й відмітка версії лягають однією транзакцією.** Придивіться: `conn.execute("BEGIN")`, потім самі `CREATE TABLE`, потім `INSERT` у `schema_version`, і аж тоді `COMMIT`. Якби відмітка йшла **окремо** від DDL, краш між ними лишив би базу у стані «таблиці створено, але версію не записано» — і наступний старт спробував би накотити ту саму міграцію знову, наскочивши на `CREATE TABLE … already exists`. Оскільки [DDL у SQLite транзакційний](root:sf-data/transactions-acid), ми звʼязуємо зміну схеми та її відмітку в одне неподільне ціле: або міграція накотилася **і** записалася, або не сталося ні того, ні того.

**Порядок — залізний.** `sorted(…, key=lambda m: m[0])` не декорація: міграції мусять накочуватися рівно за номерами, і на машині розробника, і в проді, інакше копії бази розійдуться у формі. Саме тому переїзд «RAM → диск» — це не разова подія, а **міграція 001**, перший запис в історії; телеметрія — 002; майбутній `last_seen` дочекається свого 003. Історія лінійна й дописується лише з хвоста.

![Горизонтальна стрічка з трьох карток-міграцій зліва направо: 001 «реєстр: RAM → диск (home, device)» зелена накочена, 002 «телеметрія: measurement (порт TelemetrySink)» зелена накочена, 003 «last_seen (майбутня)» помаранчева пунктирна ще не накочена. Під стрічкою таблиця schema_version із двома рядками (версія 1, версія 2) і маркером «current = 2». Збоку блок-пояснення накатника: «run_migrations бере лише version > current; накочені пропускає; повторний запуск — no-op (ідемпотентно); порядок — за номером, залізно». Знизу банер: схема має історію, що дописується лише з хвоста — і на машині розробника, і в проді копії сходяться до однієї форми](img/migration-ladder.svg)
*Схема не застигла камінь, а живий контракт із лінійною історією. Накатник читає `schema_version`, бере тільки ще не накочені кроки за номером і накочує кожен зі своєю відміткою в одній транзакції. Повторний запуск нічого не ламає — саме тому застосунок безпечно гукає його на кожному старті.*

## Порт не зрушив: `SqliteDeviceRepository`

Тепер найприємніше — підвести під схему код, не зачепивши ядра. Реєстр [сховано за портом `DeviceRepository`](root:progarch/dh-v2-hexagon), і v3 просто ставить на місце тимчасової затички справжню реалізацію на SQL — за **тим самим** портом. Тільки-но домен уклав дім і пристрої в [агрегат](root:sf-apps/aggregates-consistency), порт заговорив мовою агрегату: не «збережи один пристрій», а **`save_home` / `load`** — зберегти й підняти дім **як ціле**.

:::tabs
```py
from dataclasses import dataclass, field
from typing import Protocol

@dataclass(frozen=True)
class Device:                         # дитина агрегату (значення на межі сховища)
    id: str; kind: str; room: str; state: str; paired_at: str

@dataclass
class Home:                           # корінь агрегату
    id: str; owner_id: str; plan: str; device_cap: int; threshold: float
    used_slots: int = 0              # лічильник READ-ONLY для застосунку: пише його лише вартовий
    devices: list[Device] = field(default_factory=list)

class DeviceRepository(Protocol):     # ТОЙ САМИЙ порт із v2, тепер зернистістю агрегату
    def save_home(self, home: Home) -> None: ...
    def load(self, home_id: str) -> Home | None: ...
    def add_device(self, home_id: str, d: Device) -> bool: ...   # повертає False, якщо тариф вичерпано


class SqliteDeviceRepository:         # реалізація за портом DeviceRepository
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def save_home(self, home: Home) -> None:
        """Увесь агрегат — в ОДНІЙ транзакції: дім і його пристрої або разом, або ніяк."""
        self._conn.execute("BEGIN IMMEDIATE")            # межа агрегату = межа транзакції
        try:
            self._conn.execute(
                "INSERT INTO home(id, owner_id, plan, device_cap, used_slots, threshold) "
                "VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET "         # поклади АБО онови…
                "  plan = excluded.plan, threshold = excluded.threshold",   # …та used_slots НЕ чіпай
                (home.id, home.owner_id, home.plan, home.device_cap, len(home.devices), home.threshold))
            for d in home.devices:                        # ← збій на будь-якому витку відкотить УСЕ
                self._conn.execute(
                    "INSERT INTO device(id, home_id, kind, room, state, paired_at) "
                    "VALUES(?,?,?,?,?,?) "
                    "ON CONFLICT(id) DO UPDATE SET room = excluded.room, state = excluded.state",
                    (d.id, home.id, d.kind, d.room, d.state, d.paired_at))
            self._conn.execute("COMMIT")                  # ОДНА мить, у яку весь дім стає видимим
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

    def load(self, home_id: str) -> "Home | None":
        row = self._conn.execute(
            "SELECT owner_id, plan, device_cap, used_slots, threshold FROM home WHERE id=?",
            (home_id,)).fetchone()
        if row is None:
            return None
        devs = [Device(r[0], r[1], r[2], r[3], r[4]) for r in self._conn.execute(
            "SELECT id, kind, room, state, paired_at FROM device WHERE home_id=?", (home_id,))]
        return Home(id=home_id, owner_id=row[0], plan=row[1], device_cap=row[2],
                    used_slots=row[3], threshold=row[4], devices=devs)

    def add_device(self, home_id: str, d: Device) -> bool:
        """Займає слот тарифу Й вписує пристрій — атомарно. False → тариф вичерпано."""
        self._conn.execute("BEGIN IMMEDIATE")            # замок писаря одразу — без гонки на підвищенні
        try:
            cur = self._conn.execute(
                "UPDATE home SET used_slots = used_slots + 1 "
                "WHERE id = ? AND used_slots < device_cap",   # ← вартовий: не перевищити тариф
                (home_id,))
            if cur.rowcount != 1:                         # 0 змінено → межу вже досягнуто
                self._conn.execute("ROLLBACK")
                return False
            self._conn.execute(
                "INSERT INTO device(id, home_id, kind, room, state, paired_at) VALUES(?,?,?,?,?,?)",
                (d.id, home_id, d.kind, d.room, d.state, d.paired_at))
            self._conn.execute("COMMIT")                  # слот і пристрій стають видимі РАЗОМ
            return True
        except Exception:
            self._conn.execute("ROLLBACK")
            raise
```
```ts
interface Device { id: string; kind: string; room: string; state: string; pairedAt: string; }
interface Home {
  id: string; ownerId: string; plan: string; deviceCap: number;
  threshold: number; usedSlots: number;   // лічильник READ-ONLY для застосунку
  devices: Device[];
}

interface DeviceRepository {              // ТОЙ САМИЙ порт із v2, тепер зернистістю агрегату
  saveHome(home: Home): void;
  load(homeId: string): Home | null;
  addDevice(homeId: string, d: Device): boolean;   // False, якщо тариф вичерпано
}

class SqliteDeviceRepository implements DeviceRepository {
  constructor(private db: DatabaseSync) {}

  saveHome(home: Home): void {           // увесь агрегат — в ОДНІЙ транзакції
    this.db.exec("BEGIN IMMEDIATE");     // межа агрегату = межа транзакції
    try {
      this.db.prepare(
        "INSERT INTO home(id, owner_id, plan, device_cap, used_slots, threshold) " +
        "VALUES(?,?,?,?,?,?) " +
        "ON CONFLICT(id) DO UPDATE SET " +           // поклади АБО онови…
        "  plan = excluded.plan, threshold = excluded.threshold"   // …а used_slots НЕ чіпай
      ).run(home.id, home.ownerId, home.plan, home.deviceCap, home.devices.length, home.threshold);
      const insDev = this.db.prepare(
        "INSERT INTO device(id, home_id, kind, room, state, paired_at) VALUES(?,?,?,?,?,?) " +
        "ON CONFLICT(id) DO UPDATE SET room = excluded.room, state = excluded.state");
      for (const d of home.devices)                  // ← збій на будь-якому витку відкотить УСЕ
        insDev.run(d.id, home.id, d.kind, d.room, d.state, d.pairedAt);
      this.db.exec("COMMIT");
    } catch (e) { this.db.exec("ROLLBACK"); throw e; }
  }

  load(homeId: string): Home | null {
    const row = this.db.prepare(
      "SELECT owner_id, plan, device_cap, used_slots, threshold FROM home WHERE id=?"
    ).get(homeId) as any;
    if (!row) return null;
    const devices = this.db.prepare(
      "SELECT id, kind, room, state, paired_at FROM device WHERE home_id=?"
    ).all(homeId).map((r: any) => (
      { id: r.id, kind: r.kind, room: r.room, state: r.state, pairedAt: r.paired_at }));
    return { id: homeId, ownerId: row.owner_id, plan: row.plan, deviceCap: row.device_cap,
             threshold: row.threshold, usedSlots: row.used_slots, devices };
  }

  addDevice(homeId: string, d: Device): boolean {     // слот Й пристрій — атомарно
    this.db.exec("BEGIN IMMEDIATE");                   // замок писаря одразу
    try {
      const bumped = this.db.prepare(
        "UPDATE home SET used_slots = used_slots + 1 " +
        "WHERE id = ? AND used_slots < device_cap"     // ← вартовий: не перевищити тариф
      ).run(homeId);
      if (bumped.changes !== 1) { this.db.exec("ROLLBACK"); return false; }   // 0 → тариф вичерпано
      this.db.prepare(
        "INSERT INTO device(id, home_id, kind, room, state, paired_at) VALUES(?,?,?,?,?,?)"
      ).run(d.id, homeId, d.kind, d.room, d.state, d.pairedAt);
      this.db.exec("COMMIT");                           // слот і пристрій видимі РАЗОМ
      return true;
    } catch (e) { this.db.exec("ROLLBACK"); throw e; }
  }
}
```
:::

Тут три рішення варті окремої зупинки.

**`save_home` — це буквальна межа агрегату.** `BEGIN IMMEDIATE`, потім упис кореня, потім цикл по пристроях, і аж тоді `COMMIT`. Упади процес посеред циклу `for` — і транзакція **відкотиться цілком**, лишивши на диску той стан, що був до неї. Обіцянка «дім лягає весь або ніяк», яку домен дав словом, тут виконана **механізмом**. Це і є вся суть: не «постараємось не лишити піврозібраний дім», а «піврозібраного дому не існує в принципі».

**`used_slots` живе своїм життям — і `save_home` його не чіпає.** Гляньте на `ON CONFLICT(id) DO UPDATE SET plan=…, threshold=…`: при **оновленні** дому лічильник слотів не переписується. Це не забудькуватість, а точний захист. Лічильник рухає **лише** атомний вартовий у `add_device`; якби `save_home` копіював у нього застаріле число з обʼєкта в памʼяті, він би одним махом стер роботу вартового й розбив тариф. Тому `used_slots` для застосунку — **читабельний, але не записуваний**: `load` його дістає, а пише його тільки суддя в мить запису. Це та сама дисципліна «лічильник судить сховище, не застосунок», що вела [задачу останнього квитка](root:progarch/last-ticket-race).

**`add_device` звʼязує слот і пристрій в одну неподільну дію.** Вартовий `used_slots < device_cap` і `INSERT` пристрою — в одній транзакції: або слот зайнято **й** пристрій вписано, або не сталося нічого. Розірви ти їх — і краш між ними лишив би зайнятий слот без пристрою (лічильник бреше вгору) або пристрій без слота (тариф протік). Разом — вони чесні. Саме `add_device` налетить під натовп писарів у третьому тесті.

## `TelemetrySink`: шов, за яким поки нікого

Стаття прийняла одне свідоме архітектурне рішення: телеметрію поки тримати в тому ж реляційному сховищі, але **відгородити її портом**, щоб окреме письмо-оптимізоване сховище прийшло [останнього відповідального моменту](root:sf-apps/last-responsible-moment), а не сьогодні. Порт `TelemetrySink` і є той відкладений шов — навмисне тонкий:

:::tabs
```py
class TelemetrySink(Protocol):        # ВІДКЛАДЕНИЙ ШОВ на місці майбутнього розлому
    def append(self, device_id: str, ts: float, value: float) -> None: ...

class SqliteTelemetrySink:            # реалізація ЗАРАЗ: та сама реляційна база, послаблена тривкість
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn             # відкрито з synchronous=NORMAL (див. точку збірки)
    def append(self, device_id: str, ts: float, value: float) -> None:
        self._conn.execute("INSERT INTO measurement(device_id, ts, value) VALUES(?,?,?)",
                           (device_id, ts, value))     # autocommit: один короткий долив

# коли масштаб телеметрії справді зросте, СЮДИ стане інша реалізація — за ТИМ САМИМ портом:
# class LsmTelemetrySink:  def append(self, ...): ...   # окреме сховище, реєстру не чіпає
```
```ts
interface TelemetrySink {             // ВІДКЛАДЕНИЙ ШОВ на місці майбутнього розлому
  append(deviceId: string, ts: number, value: number): void;
}

class SqliteTelemetrySink implements TelemetrySink {   // реалізація ЗАРАЗ, тривкість послаблена
  constructor(private db: DatabaseSync) {}             // відкрито з synchronous=NORMAL
  append(deviceId: string, ts: number, value: number): void {
    this.db.prepare("INSERT INTO measurement(device_id, ts, value) VALUES(?,?,?)")
      .run(deviceId, ts, value);
  }
}

// коли масштаб зросте, СЮДИ стане LsmTelemetrySink за ТИМ САМИМ портом — реєстру не чіпаючи
```
:::

Уся цінність цього порту — саме в тому, що він **тонкий і сьогодні майже порожній**. Він не робить нічого хитрого: приймає показ і доливає його в `measurement`. Але він стоїть **рівно на лінії розлому**: коли потік вимірів розбухне й реляційна таблиця перестане його тягнути, друге, письмо-оптимізоване сховище стане за `TelemetrySink`, не зачепивши ні `DeviceRepository`, ні `HubService`, ні ядра. Дешевий порт сьогодні купує право не платити за [поліглот-персистентність](root:sf-data/polyglot-persistence) завтра — доки вона справді не знадобиться. Це шов, за який поки нікого, і саме тому він коштує майже нічого.

## Точка збірки: один рядок, що переселив реєстр

Тепер зведімо все в [точці збірки](root:sf-apps/di-container) — єдиному місці, що знає конкретні імена. Тут і живе той славнозвісний «один рядок», яким реєстр переїхав із памʼяті на диск:

:::tabs
```py
def connect(path: str, synchronous: str = "FULL") -> sqlite3.Connection:
    c = sqlite3.connect(path, isolation_level=None)   # ми САМІ керуємо BEGIN/COMMIT
    c.execute("PRAGMA journal_mode = WAL")            # властивість файлу — досить раз на базу
    c.execute(f"PRAGMA synchronous = {synchronous}")  # FULL для реєстру, NORMAL для телеметрії
    c.execute("PRAGMA foreign_keys = ON")             # SQLite інакше НЕ стежить за FK!
    c.execute("PRAGMA busy_timeout = 5000")           # писар ЧЕКАЄ замок, а не падає з BUSY
    return c

def build(path: str) -> HubService:                   # ТОЧКА ЗБІРКИ
    reg = connect(path, "FULL")                       # реєстр: тривкість по максимуму
    run_migrations(reg)                               # схема доганяє код: 001 переселив реєстр на диск
    devices = SqliteDeviceRepository(reg)             # ← ОДИН РЯДОК: SQLite стала за DeviceRepository
    #   було: devices = InMemoryDeviceRepository()    #   (v2 — тимчасова затичка в памʼяті)
    telemetry = SqliteTelemetrySink(connect(path, "NORMAL"))   # той самий файл, відпущена тривкість
    return HubService(sensor=OneWireThermometer(...), heater=SmartPlug(...),
                      devices=devices, telemetry=telemetry, cfg=Config(threshold=20.0))
```
```ts
function connect(path: string, synchronous = "FULL"): DatabaseSync {
  const db = new DatabaseSync(path);
  db.exec("PRAGMA journal_mode = WAL");
  db.exec(`PRAGMA synchronous = ${synchronous}`);     // FULL для реєстру, NORMAL для телеметрії
  db.exec("PRAGMA foreign_keys = ON");                // SQLite інакше НЕ стежить за FK!
  db.exec("PRAGMA busy_timeout = 5000");
  return db;
}

function build(path: string): HubService {            // ТОЧКА ЗБІРКИ
  const reg = connect(path, "FULL");
  runMigrations(reg);                                 // 001 переселив реєстр на диск
  const devices = new SqliteDeviceRepository(reg);    // ← ОДИН РЯДОК: SQLite за DeviceRepository
  //   було: const devices = new InMemoryDeviceRepository();   // v2 — затичка в памʼяті
  const telemetry = new SqliteTelemetrySink(connect(path, "NORMAL"));
  return new HubService(new OneWireThermometer(/*…*/), new SmartPlug(/*…*/),
                        devices, telemetry, { threshold: 20.0 });
}
```
:::

Уся заміна масштабу «даємо системі память, що переживе будь-що» вмістилася в **один рядок** підміни адаптера плюс два рядки на відкриття зʼєднань і накат міграцій. `HubService` не змінився ні на літеру — він як тримав у руках обіцянку `DeviceRepository`, так і тримає. Ядро домену не дізналося, що під ним зʼявився SQL. Це не везіння, а виплата за шов, [закладений заздалегідь](root:progarch/dh-v2-hexagon): дорога зміна коштує дешево рівно тоді, коли для неї наперед лишили місце.

![Схема збірки v3 згори вниз. Угорі зелений широкий блок «HubService — не змінився ні на літеру» зі стрілками залежності донизу до двох портів. Ліворуч порт DeviceRepository: під ним дві картки-адаптери — «InMemoryDeviceRepository (v2)» сіра, перекреслена, і «SqliteDeviceRepository (v3)» зелена активна; підпис «заміна адаптера — один рядок у build». Праворуч порт TelemetrySink: під ним «SqliteTelemetrySink (реляційно, зараз)» зелена активна й «LSM-сховище (пізніше)» помаранчева пунктирна; підпис «шов на місці розлому — реєстру не чіпає». Унизу блок build(path): connect(FULL) → run_migrations(001, 002) → зібрати. Стрілка від build угору до обох портів «підставляє конкретні адаптери»](img/v3-wiring.svg)
*Форма з v2 прийняла сховище в наготовану комірку. Порт `DeviceRepository` не зрушив — SQLite стала за нього на місце тимчасової затички одним рядком, а `HubService` над ним спить незворушно. Порт `TelemetrySink` стоїть відкладеним швом: сьогодні за ним реляційна затичка, місце під окреме сховище позначене й порожнє.*

## Три докази зібраного v3

Тепер найголовніше — притиснути до стіни три обіцянки версії. Тест ганяє **справжній** зібраний шар сховища над тимчасовим файлом; жодного мока бази, бо доводимо ми саме поведінку бази.

![Карта трьох доказів: три рядки, у кожному — обіцянка, метод і що саме доведено. Рядок 1, зелений: «Реєстр переживає рестарт» — метод save_home → close → reopen над тим самим файлом → load — доведено: пристрої на місці після смерті процесу, а run_migrations на другому старті ідемпотентний (no-op). Рядок 2, зелений: «Агрегат лягає атомарно» — метод save_home із пристроєм, що ламає CHECK(kind) посеред циклу — доведено: rollback усього, конфіг дому незмінний, жодного пристрою напівзаписаного. Рядок 3, зелений: «Тариф не перевищити під конкуренцією» — метод 8 процесів навперейми add_device на device_cap=5 — доведено: used_slots == device_cap рівно, ніколи більше, вартовий used_slots < device_cap судить у мить запису. Унизу банер: доказ — зелений тест на зібраній системі, а не рядок у статті](img/three-proofs.svg)
*Три обіцянки — три різні докази. Реєстр перевіряємо на переживання рестарту, агрегат — на атомарність під збоєм посеред циклу, тариф — на конкурентність під натовпом писарів. Спільне в них одне: доказ — це те, що лишилось на диску й повернулось із бази, а не рядок у статті.*

### Доказ 1: реєстр переживає рестарт

Пишемо дім із двома пристроями, **закриваємо** зʼєднання (процес «помер», память стерто) — і відкриваємо базу **наново** над тим самим файлом. Якщо реєстр переселився по-справжньому, друге відкриття підніме все ціле:

:::tabs
```py
def test_registry_survives_restart(tmp_path):
    path = str(tmp_path / "dh.db")

    reg1 = connect(path, "FULL")                 # ── перший «запуск» ──
    run_migrations(reg1)
    SqliteDeviceRepository(reg1).save_home(Home(
        id="h1", owner_id="ada", plan="free", device_cap=5, threshold=21.0,
        devices=[Device("lock-1", "lock", "двері", "Locked", "2026-07-01T10:00"),
                 Device("plug-2", "plug", "кухня", "On",     "2026-07-01T10:05")]))
    reg1.close()                                 # ← процес помер: у памʼяті НІЧОГО не лишилось

    reg2 = connect(path, "FULL")                 # ── другий «запуск» над тим самим файлом ──
    assert run_migrations(reg2) == 2             # ідемпотентно: current=2, накочувати нема чого
    home = SqliteDeviceRepository(reg2).load("h1")

    assert home is not None                      # дім знайдено
    assert home.threshold == 21.0                # конфіг цілий
    assert {d.id for d in home.devices} == {"lock-1", "plug-2"}   # ← реєстр пережив рестарт
```
```ts
{ // Доказ 1: реєстр переживає рестарт
  const path = tmpFile();
  const reg1 = connect(path, "FULL");            // перший «запуск»
  runMigrations(reg1);
  new SqliteDeviceRepository(reg1).saveHome({
    id: "h1", ownerId: "ada", plan: "free", deviceCap: 5, threshold: 21.0, usedSlots: 0,
    devices: [{ id: "lock-1", kind: "lock", room: "двері", state: "Locked", pairedAt: "…" },
              { id: "plug-2", kind: "plug", room: "кухня", state: "On",     pairedAt: "…" }],
  });
  reg1.close();                                  // ← процес помер

  const reg2 = connect(path, "FULL");            // другий «запуск» над тим самим файлом
  assert.strictEqual(runMigrations(reg2), 2);    // ідемпотентно: накочувати нема чого
  const home = new SqliteDeviceRepository(reg2).load("h1")!;
  assert.strictEqual(home.threshold, 21.0);
  assert.deepStrictEqual(new Set(home.devices.map(d => d.id)), new Set(["lock-1", "plug-2"]));
}
```
:::

Це рівно та відмінність від [v2-шого фейка в памʼяті](root:progarch/dh-v2-hexagon), заради якої й затівалася версія: закрий процес над `InMemoryDeviceRepository` — і реєстр щез; закрий над `SqliteDeviceRepository` — і він на місці. Заразом тест доводить **другу** річ безкоштовно: `run_migrations` на другому старті повертає `2`, не накотивши нічого, — тобто ідемпотентний, і застосунок може безпечно гукати його на кожному піднятті. Чесно назвімо межу доказу: `close()` — це **ввічлива** смерть, вона доводить переживання перезапуску застосунку, але не відмови живлення; справжнє вбивство процесу `kill`-ом і межа між ним і висмикнутим шнуром — [у сусідньому розборі про гарантії](root:progarch/dh-storage-guarantees/proj-dh-guarantees.md).

### Доказ 2: агрегат лягає атомарно

Тепер найтонше. Пишемо дім, тоді пробуємо перезаписати його новим станом, де **один із пристроїв посеред циклу ламає правило схеми** — `kind`, якого нема в дозволеному переліку. Транзакція мусить відкотити **все**: і новий поріг, і вже вписаний перед поганим пристрій:

:::tabs
```py
def test_aggregate_lands_all_or_nothing(tmp_path):
    path = str(tmp_path / "dh.db")
    reg = connect(path, "FULL"); run_migrations(reg)
    repo = SqliteDeviceRepository(reg)

    repo.save_home(Home("h1", "ada", "free", 5, threshold=21.0,      # вихідний дім: поріг 21,
                        devices=[Device("lock-1", "lock", "двері", "Locked", "t0")]))  # один замок

    poisoned = Home("h1", "ada", "free", 5, threshold=24.0, devices=[  # намір: поріг 24 + два пристрої
        Device("plug-2", "plug", "кухня", "On", "t1"),                 # добрий — ляже перший…
        Device("bad-3", "???",  "гараж", "On", "t2")])                 # …а цей ЛАМАЄ CHECK(kind)

    with pytest.raises(sqlite3.IntegrityError):     # поганий пристрій підриває транзакцію
        repo.save_home(poisoned)

    survivor = repo.load("h1")                        # читаємо, ЩО лишилось на диску
    assert survivor.threshold == 21.0                 # ← поріг НЕ змінився: відкотилось усе
    assert {d.id for d in survivor.devices} == {"lock-1"}   # ← plug-2 теж зник, хоч ліг ДО поганого
```
```ts
{ // Доказ 2: агрегат лягає весь або ніяк
  const path = tmpFile();
  const reg = connect(path, "FULL"); runMigrations(reg);
  const repo = new SqliteDeviceRepository(reg);

  repo.saveHome({ id: "h1", ownerId: "ada", plan: "free", deviceCap: 5, threshold: 21.0,
    usedSlots: 0, devices: [{ id: "lock-1", kind: "lock", room: "двері", state: "Locked", pairedAt: "t0" }] });

  const poisoned = { id: "h1", ownerId: "ada", plan: "free", deviceCap: 5, threshold: 24.0, usedSlots: 0,
    devices: [{ id: "plug-2", kind: "plug", room: "кухня", state: "On", pairedAt: "t1" },   // добрий
              { id: "bad-3", kind: "???", room: "гараж", state: "On", pairedAt: "t2" }] };   // ЛАМАЄ CHECK

  assert.throws(() => repo.saveHome(poisoned));      // поганий пристрій підриває транзакцію

  const survivor = repo.load("h1")!;
  assert.strictEqual(survivor.threshold, 21.0);      // ← поріг НЕ змінився
  assert.deepStrictEqual(new Set(survivor.devices.map(d => d.id)), new Set(["lock-1"]));  // plug-2 зник
}
```
:::

Ось де «весь або ніяк» перестає бути гаслом. Усередині `save_home` уже виконалися **два** записи — оновлення порога на 24 й вставка `plug-2`, — коли третій, `bad-3`, наскочив на `CHECK(kind IN …)` і підняв помилку. Оскільки все це в одній транзакції, `ROLLBACK` стер **обидва** попередні записи разом із наміром: на диску лишився вихідний дім, цілий до останнього поля — поріг 21, самотній `lock-1`. Напівоновленого дому — нового порога зі старим набором пристроїв, половини пристроїв, будь-якої суміші двох версій — просто **не існує як стану**. Це буквальне виконання [агрегатної обіцянки](root:progarch/dh-data-model): межа домену стала межею транзакції, і всередині неї немає «наполовину».

### Доказ 3: тариф не перевищити під конкуренцією

Останній доказ — не про смерть, а про **натовп**. Вісім окремих процесів (не потоків: справжня паралельність, кожен зі своїм зʼєднанням) навперейми бʼють `add_device` на домі, чий тариф дає рівно пʼять слотів. Разом вони пробують заявити куди більше, ніж пʼять:

:::tabs
```py
import multiprocessing as mp

def _hammer_add(path, home_id, worker, tries):    # МУСИТЬ бути на верхньому рівні (spawn на Windows)
    repo = SqliteDeviceRepository(connect(path, "FULL"))   # свій конекшн у кожного процеса
    for i in range(tries):
        try:
            repo.add_device(home_id, Device(f"{worker}-{i}", "plug", "кімната", "On", "t"))
        except sqlite3.IntegrityError:
            pass                                   # рідкісний збіг id — не наша ціль тут

def test_tariff_never_exceeded_under_concurrency(tmp_path):
    path = str(tmp_path / "dh.db")
    boot = connect(path, "FULL"); run_migrations(boot)
    SqliteDeviceRepository(boot).save_home(
        Home("h1", "ada", "free", device_cap=5, threshold=20.0, devices=[]))   # 5 слотів, 0 зайнято
    boot.close()

    procs = [mp.Process(target=_hammer_add, args=(path, "h1", w, 20)) for w in range(8)]
    for p in procs: p.start()                      # 8×20 = 160 спроб на тариф у 5 слотів
    for p in procs: p.join()

    reg = connect(path, "FULL")
    used = reg.execute("SELECT used_slots FROM home WHERE id='h1'").fetchone()[0]
    rows = reg.execute("SELECT COUNT(*) FROM device WHERE home_id='h1'").fetchone()[0]
    assert used == 5                               # ← рівно тариф зайнято, ні слотом більше
    assert rows == 5                               # ← і рівно 5 пристроїв на диску: лічильник = реальність
```
```ts
// (Node: 8 воркерів через worker_threads/child_process, кожен зі своїм connect(path))
// Суть та сама — наводимо перевірку результату після того, як усі воркери відпрацювали:
{
  const reg = connect(path, "FULL");
  const used = (reg.prepare("SELECT used_slots AS u FROM home WHERE id='h1'").get() as any).u;
  const rows = (reg.prepare("SELECT COUNT(*) AS n FROM device WHERE home_id='h1'").get() as any).n;
  assert.strictEqual(used, 5);   // ← рівно тариф зайнято, ні слотом більше
  assert.strictEqual(rows, 5);   // ← і рівно 5 пристроїв: лічильник дорівнює реальності
}
```
:::

160 спроб налітають на пʼять слотів — і рівно пʼять мають пройти, а 155 наткнутися на вартового `used_slots < device_cap` і змінити нуль рядків. Чому попри вісім конкурентних процесів `used_slots` не проскакує за пʼять? Бо SQLite впускає до запису **одного** писаря за раз: вісім операторів `UPDATE` серіалізуються замком бази, кожен перечитує `used_slots` **свіжим** у мить свого запису, і щойно значення сягне пʼяти, вартовий у всіх решти виявиться хибним — `add_device` поверне `False`, `ROLLBACK` відпустить і слот, і невставлений пристрій. Це буквально [атомний вартовий із задачі квитка](root:progarch/last-ticket-race), тепер доведений під **справжньою** паралельністю, а не в думках, і не на бюджеті нагріву, як у сусіда, а на слотах тарифу. А оскільки слот і пристрій лягають однією транзакцією, `used_slots == COUNT(device)` завжди: лічильник дорівнює реальності, не бреше ні вгору, ні вниз.

## Складність і пастки

**`ON CONFLICT`-upsert додає й оновлює, але не видаляє.** Наш `save_home` робить `INSERT … ON CONFLICT DO UPDATE`: кладе новий пристрій або освіжає наявний. Але пристрій, якого в `home.devices` **не стало**, на диску **лишиться** — upsert його не чіпає. Для v3 це свідомо гаразд (пристрої вибувають окремим шляхом), але якщо `save_home` колись стане повним перезаписом набору, знадобиться або `DELETE FROM device WHERE home_id=?` перед циклом (повна заміна, як у [сусідньому розборі гарантій](root:progarch/dh-storage-guarantees/proj-dh-guarantees.md)), або явний облік вибулих. Плутати «оновив» із «замінив увесь набір» — тихий баг, що проступає лише коли щось видаляють.

**`excluded` і вибір стовпців для `DO UPDATE` — не дрібниця.** Ключове слово `excluded` — це рядок, який **не вдалося** вставити (той, що конфліктнув); `DO UPDATE SET plan = excluded.plan` бере значення з нього. Небезпека — механічно виписати `SET` для **всіх** стовпців. Зроби так із `used_slots` — і кожен `save_home` затре живий лічильник застарілим числом з обʼєкта, розбивши тариф. Тому в `DO UPDATE` ми свідомо лишаємо `used_slots` **осторонь**: його пише лише вартовий. Правило просте — у `DO UPDATE` онови рівно ті стовпці, що справді належать застосунку, і жодного, за який відповідає сховище.

**Порядок міграцій залізний, а накочене — заморожене.** Міграції накочуються строго за номером, тож `sorted` не косметика. І накочену міграцію **не редагують** ніколи: 001 заморожена тієї миті, як пішла в проду. Треба змінити форму — додають **нову** міграцію з наступним номером, а не правлять стару, бо на машинах, де стара вже накотилася, правка просто не виконається (`schema_version` каже «цю вже маємо»). Звідси й типова колізія в команді: двоє в різних гілках завели «міграцію 003» — при злитті номери зіштовхуються, і одну доводиться перенумерувати. Історія схеми дописується лише з хвоста й лише вперед.

**`fsync` і тривкість: цей тест доводить менше, ніж здається.** Реєстр ми відкриваємо з `synchronous=FULL`, тобто `fsync` на кожен коміт — саме він рятує закомічений реєстр навіть на відмові живлення. Але наш `close()`-рестарт цієї гарантії **не бачить**: він доводить переживання перезапуску застосунку, а `FULL` від `NORMAL` різниться лише на висмикнутому шнурі. Не роби з зеленого тесту висновку «`FULL` тут зайвий» — це та сама пастка «зелений тест доводить не те», яку [сусідній розбір](root:progarch/dh-storage-guarantees/proj-dh-guarantees.md) розбирає окремо. Знати межу власного доказу важливіше за сам зелений колір.

**`BEGIN IMMEDIATE`, `busy_timeout`, `foreign_keys` — три рядки, без яких конкурентність бреше.** Ми відкриваємо зʼєднання з `isolation_level=None` навмисне: щоб самим сказати `BEGIN IMMEDIATE` і взяти замок писаря **одразу**. Якби писар стартував відкладену транзакцію (`DEFERRED`), два таких, обидва спершу взявши замок читача, застрягли б на спробі підняти його до писаря — [взаємне блокування](root:sf-tasks/deadlock) на порожньому місці. `busy_timeout = 5000` перетворює зіткнення на **чергу**: писар чекає замок до пʼяти секунд, а не падає з `SQLITE_BUSY` на першій же зайнятості (без нього третій тест губив би спроби, а не «перевитрачав»). А `PRAGMA foreign_keys = ON` треба на **кожному** зʼєднанні окремо — SQLite історично стежить за зовнішніми ключами лише коли її про це попросили; забудеш рядок — і `REFERENCES` мовчки декоративний, сироти пролазять.

**`load` піднімає агрегат двома запитами — і це нормально для одного дому.** Корінь `home` і його `device` ми читаємо окремими `SELECT`. Для одного дому це два дешевих запити. Але якби застосунок піднімав **сотні** домів у циклі, по два запити на кожен, — це класична пастка N+1 (один запит на список плюс по одному на кожен елемент), і тоді дітей тягнуть одним `SELECT … WHERE home_id IN (…)`. Для агрегата, який за визначенням піднімають **поштучно й цілком**, двох запитів досить; масовим читанням тут не місце — і це ще один доказ, що [межу агрегату провели правильно](root:progarch/dh-data-model).

Отут вправа й замикається — зібраним, а не намальованим. Схема стоїть трьома таблицями, поділеними за природою запису; реєстр переселився на диск одним рядком у точці збірки, не зачепивши ядра; схема дістала історію, що дописується дисципліновано; телеметрія — відкладений шов на місці майбутнього розлому. А три обіцянки версії більше не слова: реєстр переживає рестарт, агрегат лягає весь або ніяк, тариф не перевищити під натовпом писарів — і кожну з них стверджує зелений тест на **справжній** зібраній системі. Оце й є «сховище як рішення», доведене до кінця: не «додали базу», а зробили свідомий вибір про правду системи — і притиснули його до стіни доказом.
