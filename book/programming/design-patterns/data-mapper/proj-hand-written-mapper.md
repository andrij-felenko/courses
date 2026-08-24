# ⚙️ Робочий мапер: транзакція, оновлення, видалення

`findById` та `insert` — легша половина мапера, і легка вона з однієї причини: обидва працюють із чистого аркуша. Один читає рядки, яких ще ніхто не чіпав; другий пише рядки, яких ще нема. Жоден не мусить відповідати на питання «а що там зараз?».

Уся решта мапера тільки з цього питання й складається. `update` мусить знати, чим нинішній стан бази відрізняється від того, що йому щойно принесли. `delete` мусить знати, де саме закінчується замовлення. І обидва мусять знати, у чиїх межах вони працюють, — бо кожен із них це не один запит, а кілька, а між запитами буває всяке.

Доведу `OrderMapper` до стану, у якому його не соромно покласти в сервіс. Три рішення по черзі — межа транзакції, оновлення, видалення, — а потім чотири пастки, кожна з яких комусь коштувала ночі.

## Схема, на якій це бігає

```sql
CREATE TABLE orders (
  id          INTEGER PRIMARY KEY,
  placed_at   TEXT    NOT NULL,
  total_cents INTEGER NOT NULL,
  currency    TEXT    NOT NULL CHECK (length(currency) = 3),
  status      TEXT    NOT NULL CHECK (status IN ('new', 'shipped', 'cancelled'))
);

CREATE TABLE order_lines (
  id          INTEGER PRIMARY KEY,
  order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  position    INTEGER NOT NULL,
  sku         TEXT    NOT NULL,
  qty         INTEGER NOT NULL CHECK (qty > 0),
  price_cents INTEGER NOT NULL,
  UNIQUE (order_id, position)
);
```

Одна колонка тут з'явилася не сама собою, і на неї варто глянути пильно — це `position`. У домені позиції лежать у масиві: `readonly lines: readonly OrderLine[]`. Масив упорядкований, і цей порядок — справжній стан: користувач вводив позиції в певній послідовності й чекає побачити їх у ній же. А реляційна таблиця — це множина рядків, і порядку в ній нема за побудовою. Стандарт SQL каже про це прямо: коли впорядкування не задано через `ORDER BY`, взаємне положення двох рядків залежить від реалізації. Не «зазвичай збігається зі вставкою», а *не визначено*.

Тому спокуса написати `ORDER BY id` і жити далі — це не економія, а відкладена поломка: `id` віддає рушій, і збігатися з порядком у масиві він зобов'язаний рівно доти, доки ти не змінив спосіб запису. Порядок — частина стану домену, отже, мапер мусить його зберігати явно, окремою колонкою. Це той самий розрив у чистому вигляді: в об'єкті властивість є, у базі місця під неї нема — тож місце доводиться зробити.

Решта схеми — звичайні наслідки. `total_cents` і `currency` окремо, бо типу «гроші» в рушія нема. `placed_at` тут `TEXT` (SQLite інакше не вміє); у Postgres на його місці був би `timestamptz`, і разом із ним поїхало б питання часового поясу — `TEXT` зберігає рівно те, що записали, а `timestamp` без пояса тихо загубить, у якому поясі це «14:30». Ще одна колонка, ще одне рішення, яке ухвалює мапер.

`ON DELETE CASCADE` тут стоїть, але не як механізм — про це трохи нижче.

## Хто відкриває транзакцію

Перше рішення напрошується неправильне. `insert` робить кілька записів — голову й позиції, — тож інстинкт каже: хай сам загорне їх у `BEGIN`/`COMMIT`, він же знає, що це одне ціле.

Простеж, що з цього виходить. Сценарій «скасувати замовлення» — це не одна дія: треба змінити `orders.status` і зняти резерв на складі. Два мапери. Якщо кожен сам собі транзакція, то між ними є мить, коли одне вже сталося, а друге ще ні. Процес упав саме там — замовлення скасоване, товар навіки в резерві, і жодної помилки ніде не записано.

![Дві панелі. Ліворуч: сценарій кличе OrderMapper.update, який сам робить BEGIN-UPDATE-COMMIT, потім мав би покликати StockMapper.release із власним BEGIN-DELETE-COMMIT — але між ними процес упав, і друге вже не сталося: замовлення скасоване, товар навіки в резерві. Праворуч: сценарій відкриває одну транзакцію, обидва мапери отримують те саме з'єднання tx і працюють усередині одного BEGIN…COMMIT, тож збій будь-де відкочує обидві дії разом](img/tx-seam.svg)

*Мапер не знає, що робиться навколо нього, — отже, не має права визначати, що є одним цілим. Коли транзакцію відкриває кожен мапер, межа атомарності визначається випадковим набором маперів, які покликав сценарій.*

Звідси правило, і воно коротке: **мапер не відкриває транзакцію — він у ній працює**. Межу задає той, хто знає, що тут одна одиниця роботи. Що саме зобов'язане змінюватися разом і чому це не питання мапера — вирішує [агрегат](book:programming/aggregates-consistency): він і є та одиниця, чиї межі збігаються з межами транзакції.

Технічно це означає одне: мапер приймає ззовні **конкретне з'єднання**, а не пул.

```ts
// ── шов, у який потім стане транзакція ─────────────────────────
interface Executor {
  one<T>(sql: string, args: unknown[]): Promise<T | null>;
  all<T>(sql: string, args: unknown[]): Promise<T[]>;
  run(sql: string, args: unknown[]): Promise<{ rowCount: number }>;
}

interface Pool {
  connect(): Promise<Executor & { release(): void }>;
}

async function withTransaction<T>(pool: Pool, fn: (tx: Executor) => Promise<T>): Promise<T> {
  const conn = await pool.connect();
  try {
    await conn.run("BEGIN", []);
    const out = await fn(conn);
    await conn.run("COMMIT", []);
    return out;
  } catch (err) {
    // з'єднання могло вже вмерти — хай ROLLBACK не затуляє справжню помилку
    await conn.run("ROLLBACK", []).catch(() => {});
    throw err;
  } finally {
    conn.release();
  }
}
```

Різниця між `Executor` і `Pool` — не буквоїдство. Дай маперу пул — і кожен його запит візьме з пулу **довільне вільне з'єднання**. `update` зробить `UPDATE orders` на з'єднанні №1, а `DELETE FROM order_lines` — на з'єднанні №2. Це вже дві незалежні транзакції, і жодне `BEGIN` навколо їх не з'єднає.

Найгидкіше в цій пастці — коли вона себе показує. Під малим навантаженням пул майже завжди віддає те саме з'єднання, тож тести зелені, локально все працює, і код їде в продакшн. Розходитися воно починає рівно тоді, коли з'єднань не вистачає на всіх, — тобто під навантаженням, у пік, на живих грошах. Тип `Executor` замість `Pool` — це п'ять рядків, які роблять таку помилку неможливою на етапі компіляції.

## Оновлення: там, де ховається вся складність

Голову оновити просто — один `UPDATE` по всіх колонках. Позиції — ні, і причина суто патернова: **об'єкт не сказав маперу, що змінилося**. Він і не міг: `Order` про існування мапера не знає. Мапер отримує масив із трьома позиціями і рядок у базі з якимись позиціями, а що між ними сталося — вставили, змінили, викинули, переставили — має вирахувати сам.

Виходів рівно три.

![Угорі два стани: у базі id=11 A×2, id=12 B×1, id=13 D×4; в об'єкті 0: A×2, 1: B×3, 2: C×5. Нижче три колонки-стратегії. Перша, «стерти й вписати наново»: DELETE усіх рядків замовлення і три INSERT, після чого в базі id=14, 15, 16 — усі нові; плюси — найпростіший код і порядок збігається з масивом, мінуси — id щоразу нові, чотири записи там, де змінилось одне, каскад знесе все, що на них посилалося. Друга, «звірити з базою»: SELECT поточних рядків, UPDATE id=12, INSERT C, DELETE id=13, після чого id=11 і id=12 живі; плюси — мінімум записів і живі id, аудит бачить справжню зміну; мінуси — зайве читання перед кожним записом, потрібен стабільний ключ позиції, переставлення ламає UNIQUE. Третя, «знімок при завантаженні»: find кладе поруч копію, порівняння йде зі знімком, а не з базою, ті самі записи і нуль зайвих читань; мінуси — мапер тримає стан між викликами, у нього з'явився час життя, і це вже Unit of Work](img/update-strategies.svg)

*Три способи відповісти на одне питання «що змінилося?»: спитати базу, порівняти зі знімком або не питати взагалі й переписати все. Найдешевший спосіб — третій, і саме він перетворює мапер на щось, що має пам'ять і час життя.*

**Спосіб перший — стерти й вписати наново.** Один `DELETE`, далі `INSERT` на кожну позицію. Виглядає як грубість, але в межах транзакції це цілком коректно, і для агрегата з десятком позицій різниця в швидкості між ним і розумним порівнянням — статистичний шум. Головне ж інше: він **не має стану**. Мапер нічого не пам'ятає, ні про що не питає, і зламатися в ньому нема чому.

Платить він трьома речами. Позиції щоразу отримують нові `id` — і якщо на них хтось посилається (таблиця знижок на позицію, аудит, зовнішня система), то `ON DELETE CASCADE` тихо винесе й ті рядки. Реплікація й тригери бачать не «змінилася кількість в одній позиції», а «зникли три, з'явилися три». І запис іде на всі позиції, навіть якщо змінилася одна.

Коли це годиться — коли позиції справді частина агрегата, ззовні на них ніхто не посилається, і їх десятки, а не тисячі. Тобто в переважній більшості випадків.

**Спосіб другий — звірити з базою.** Прочитати поточні рядки й розкласти на три множини: вставити, оновити, видалити.

```ts
// альтернатива до writeLines: не стирати все, а звести різницю
private async syncLines(orderId: number, lines: readonly OrderLine[]): Promise<void> {
  const current = await this.db.all<LineRow & { id: number; position: number }>(
    `SELECT id, position, sku, qty, price_cents FROM order_lines WHERE order_id = $1`,
    [orderId]);
  const have = new Map(current.map(r => [r.position, r]));

  for (const [i, l] of lines.entries()) {
    const row = have.get(i);
    have.delete(i);                                   // цю позицію розглянули

    if (!row) {
      await this.db.run(
        `INSERT INTO order_lines (order_id, position, sku, qty, price_cents)
         VALUES ($1, $2, $3, $4, $5)`, [orderId, i, l.sku, l.qty, l.price.cents]);
      continue;
    }
    if (row.sku === l.sku && row.qty === l.qty && row.price_cents === l.price.cents)
      continue;                                       // не змінилась — не чіпаємо
    await this.db.run(
      `UPDATE order_lines SET sku = $1, qty = $2, price_cents = $3 WHERE id = $4`,
      [l.sku, l.qty, l.price.cents, row.id]);
  }

  // що лишилось у have — позиції, яких в об'єкті вже нема
  for (const row of have.values())
    await this.db.run(`DELETE FROM order_lines WHERE id = $1`, [row.id]);
}
```

Тут одразу видно, за що платимо: зайве читання перед кожним записом. Але дорожча за нього інша річ — **ключ**. Я звіряю за `position`, бо іншого стабільного ключа нема. `sku`? Той самий товар може стояти в замовленні двічі — з різною ціною, з різного складу. Тоді `sku` не ключ.

А `position` — ключ рівно доти, доки позиції не переставляють. Помінялися місцями A і B — обидві «змінилися», два `UPDATE` замість нуля. Вставили нову позицію на початок — зсунулися всі, і diff виродився в переписування всього, тільки дорожче, бо ще й із читанням. Гірше: `UNIQUE (order_id, position)` перевіряється негайно, порядково, тож проста перестановка двох сусідніх позицій упаде на порушенні обмеження просто посеред циклу (у Postgres це лікують `DEFERRABLE INITIALLY DEFERRED`, у SQLite — ніяк).

Справжній ключ тут — власна тотожність позиції: дати `OrderLine` при створенні свій `id` (скажімо, UUID), і diff запрацює по-справжньому. Але зверни увагу, що щойно сталося: ти змінив домен заради збереження. Поле, якого предметна область не просила, з'явилося в об'єкті, бо так зручніше маперу. Це чесна ціна, її просто треба назвати вголос, а не вдавати, що її нема.

**Спосіб третій — знімок.** Хай `findById` кладе поруч із об'єктом копію стану, а `update` порівнює з нею, а не з базою. Нуль зайвих читань, мінімум записів, ключ теж потрібен — але читання зникло.

І ось тут із мапера виростає те, чим він доти не був. Щоб тримати знімок, мапер мусить пам'ятати, що́ він видавав, — у нього з'явився стан. Стан живе між викликами — у нього з'явився час життя. А раз є час життя, то є й межа, на якій усе накопичене треба записати, — і це вже не мапер, це [Unit of Work](book:programming/unit-of-work). Він приходить не з фреймворку й не з моди: він виростає з `update`, щойно ти вирішуєш не питати базу.

## Видалення: де закінчується замовлення

`delete` виглядає найпростішим, а насправді змушує відповісти на питання, якого решта мапера не ставила: **що входить у «замовлення»?**

У схемі стоїть `ON DELETE CASCADE`, і спокуса очевидна — видалити голову й дати базі прибрати позиції. Не роби так, і причина не в смаку. `CASCADE` — це опис межі агрегата, записаний у DDL. Тепер відповідь на питання «що є одним цілим» живе у двох місцях: у домені та в схемі, — і синхронізувати їх не буде ніхто. Міграція, яку писав не ти, знімає каскад заради швидкості — і мапер починає лишати сиріт, не помітивши цього.

До того ж на SQLite цей каскад за замовчуванням просто не працює. Зовнішні ключі там **вимкнено заради сумісності зі старими базами**: рушій розбирає оголошення `REFERENCES`, але не стежить за ним, доки на кожному з'єднанні окремо не сказано `PRAGMA foreign_keys = ON`. Тобто `DELETE FROM orders` мовчки лишає позиції в таблиці — без помилки, без сліду в журналі. Улюблена комбінація: тести на SQLite, продакшн на Postgres — і поведінка різна там, де її ніхто не думав перевіряти.

Тому мапер видаляє явно, а `CASCADE` лишається страховкою від сиріт, а не механізмом. Одне зайве речення в коді — і межа агрегата описана рівно в одному місці, у домені.

Друге питання `delete` ставить уже не маперу, а тобі: чи взагалі можна видаляти замовлення? Відвантажене замовлення — це фінансовий документ, який мусить пережити всіх. У живих системах `delete` для таких сутностей або не існує, або означає `status = 'archived'`. Мапер тут ні до чого — але саме він робить це питання видимим, бо мусить написати метод.

## Мапер цілком

Усе разом. Це працездатний код, а не начерк: `Executor` замість пулу, явні позиції, перевірка на зниклий рядок, збірка через конструктор і множинна вибірка без `N+1`.

:::tabs
```ts
type Status = "new" | "shipped" | "cancelled";
type HeadRow = { id: number; placed_at: string; currency: string; status: Status };
type LineRow = { sku: string; qty: number; price_cents: number };

class OrderMapper {
  constructor(private readonly db: Executor) {}      // не Pool — конкретне з'єднання

  async findById(id: number): Promise<Order | null> {
    const head = await this.db.one<HeadRow>(
      `SELECT id, placed_at, currency, status FROM orders WHERE id = $1`, [id]);
    if (!head) return null;

    const rows = await this.db.all<LineRow>(
      `SELECT sku, qty, price_cents FROM order_lines
       WHERE order_id = $1 ORDER BY position`, [id]);
    return this.build(head, rows);
  }

  async findByStatus(status: Status): Promise<Order[]> {
    const heads = await this.db.all<HeadRow>(
      `SELECT id, placed_at, currency, status FROM orders WHERE status = $1`, [status]);
    if (heads.length === 0) return [];

    // ОДИН запит на всі позиції — не по запиту на кожне замовлення
    const rows = await this.db.all<LineRow & { order_id: number }>(
      `SELECT order_id, sku, qty, price_cents FROM order_lines
       WHERE order_id = ANY($1) ORDER BY order_id, position`, [heads.map(h => h.id)]);

    const byOrder = new Map<number, LineRow[]>();
    for (const r of rows) {
      const bucket = byOrder.get(r.order_id);
      if (bucket) bucket.push(r); else byOrder.set(r.order_id, [r]);
    }
    return heads.map(h => this.build(h, byOrder.get(h.id) ?? []));
  }

  async insert(order: Order): Promise<Order> {
    const total = order.total();
    const head = await this.db.one<{ id: number }>(
      `INSERT INTO orders (placed_at, total_cents, currency, status)
       VALUES ($1, $2, $3, $4) RETURNING id`,
      [order.placedAt, total.cents, total.currency, order.state]);

    await this.writeLines(head!.id, order.lines);
    // id readonly — вписати його в переданий об'єкт не можна, тож віддаємо новий
    return new Order(head!.id, order.placedAt, order.lines, order.state);
  }

  async update(order: Order): Promise<void> {
    const id = this.identified(order);
    const total = order.total();
    const { rowCount } = await this.db.run(
      `UPDATE orders SET placed_at = $1, total_cents = $2, currency = $3, status = $4
       WHERE id = $5`,
      [order.placedAt, total.cents, total.currency, order.state, id]);

    if (rowCount === 0) throw new Error(`orders#${id}: рядка нема — його встигли видалити?`);

    await this.db.run(`DELETE FROM order_lines WHERE order_id = $1`, [id]);
    await this.writeLines(id, order.lines);
  }

  async delete(order: Order): Promise<void> {
    const id = this.identified(order);
    await this.db.run(`DELETE FROM order_lines WHERE order_id = $1`, [id]);  // явно, не каскадом
    const { rowCount } = await this.db.run(`DELETE FROM orders WHERE id = $1`, [id]);
    if (rowCount === 0) throw new Error(`orders#${id}: видаляти нема чого`);
  }

  // ── внутрішнє ──────────────────────────────────────────────────────────
  private build(head: HeadRow, rows: LineRow[]): Order {
    if (rows.length === 0)
      throw new Error(`orders#${head.id}: голова є, позицій нема — база суперечить домену`);
    const lines = rows.map(r =>
      new OrderLine(r.sku, r.qty, new Money(r.price_cents, head.currency)));
    return new Order(head.id, new Date(head.placed_at), lines, head.status);
  }

  private async writeLines(orderId: number, lines: readonly OrderLine[]): Promise<void> {
    for (const [i, l] of lines.entries())
      await this.db.run(
        `INSERT INTO order_lines (order_id, position, sku, qty, price_cents)
         VALUES ($1, $2, $3, $4, $5)`, [orderId, i, l.sku, l.qty, l.price.cents]);
  }

  private identified(order: Order): number {
    if (order.id === null) throw new Error("об'єкт без id: спершу insert");
    return order.id;
  }
}
```
```py
import sqlite3
from contextlib import contextmanager
from datetime import datetime


def connect(path):
    conn = sqlite3.connect(path, isolation_level=None)   # BEGIN пишемо самі
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")             # інакше REFERENCES — просто напис
    return conn


@contextmanager
def transaction(conn):
    """Межу задає той, хто кличе, — не мапер."""
    conn.execute("BEGIN")
    try:
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


class OrderMapper:
    def __init__(self, conn):                            # конкретне з'єднання, не пул
        self._conn = conn

    def find_by_id(self, order_id):
        head = self._conn.execute(
            "SELECT id, placed_at, currency, status FROM orders WHERE id = ?",
            (order_id,)).fetchone()
        if head is None:
            return None

        rows = self._conn.execute(
            "SELECT sku, qty, price_cents FROM order_lines "
            "WHERE order_id = ? ORDER BY position", (order_id,)).fetchall()
        return self._build(head, rows)

    def find_by_status(self, status):
        heads = self._conn.execute(
            "SELECT id, placed_at, currency, status FROM orders WHERE status = ?",
            (status,)).fetchall()
        if not heads:
            return []

        ids = [h["id"] for h in heads]
        holes = ",".join("?" * len(ids))                  # IN (?,?,?) — за кількістю id
        rows = self._conn.execute(                        # ОДИН запит на всі позиції
            "SELECT order_id, sku, qty, price_cents FROM order_lines "
            f"WHERE order_id IN ({holes}) ORDER BY order_id, position", ids).fetchall()

        by_order = {}
        for r in rows:
            by_order.setdefault(r["order_id"], []).append(r)
        return [self._build(h, by_order.get(h["id"], [])) for h in heads]

    def insert(self, order):
        total = order.total()
        cur = self._conn.execute(
            "INSERT INTO orders (placed_at, total_cents, currency, status) "
            "VALUES (?, ?, ?, ?)",
            (order.placed_at.isoformat(), total.cents, total.currency, order.status))

        order.id = cur.lastrowid          # поле відкрите — мапер вписує тотожність на місці
        self._write_lines(order.id, order.lines)
        return order

    def update(self, order):
        order_id = self._identified(order)
        total = order.total()
        cur = self._conn.execute(
            "UPDATE orders SET placed_at = ?, total_cents = ?, currency = ?, status = ? "
            "WHERE id = ?",
            (order.placed_at.isoformat(), total.cents, total.currency,
             order.status, order_id))

        if cur.rowcount == 0:
            raise LookupError(f"orders#{order_id}: рядка нема — його встигли видалити?")

        self._conn.execute("DELETE FROM order_lines WHERE order_id = ?", (order_id,))
        self._write_lines(order_id, order.lines)

    def delete(self, order):
        order_id = self._identified(order)
        self._conn.execute("DELETE FROM order_lines WHERE order_id = ?",  # явно, не каскадом
                           (order_id,))
        cur = self._conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        if cur.rowcount == 0:
            raise LookupError(f"orders#{order_id}: видаляти нема чого")

    # ── внутрішнє ──────────────────────────────────────────────────────────
    def _build(self, head, rows):
        if not rows:
            raise LookupError(
                f"orders#{head['id']}: голова є, позицій нема — база суперечить домену")
        lines = [OrderLine(r["sku"], r["qty"], Money(r["price_cents"], head["currency"]))
                 for r in rows]
        return Order(head["id"], datetime.fromisoformat(head["placed_at"]),
                     lines, head["status"])

    def _write_lines(self, order_id, lines):
        self._conn.executemany(
            "INSERT INTO order_lines (order_id, position, sku, qty, price_cents) "
            "VALUES (?, ?, ?, ?, ?)",
            [(order_id, i, l.sku, l.qty, l.price.cents) for i, l in enumerate(lines)])

    @staticmethod
    def _identified(order):
        if order.id is None:
            raise ValueError("об'єкт без id: спершу insert")
        return order.id
```
:::

Одна відмінність між вкладками не косметична, і вона показова. У TypeScript `id` оголошено `readonly`, тож `insert` не може вписати його в переданий об'єкт і повертає **новий** `Order`. У Python поле відкрите, тож мапер просто дописує `order.id = cur.lastrowid` у той самий примірник. Мова вирішила за тебе, наскільки глибоко маперу дозволено залізти в домен, — і саме в цю щілину пролізе перша пастка.

А ось сценарій цілком — той самий, що падав на початку:

```py
conn = connect("shop.db")

with transaction(conn):                  # межу відкриває сценарій
    orders = OrderMapper(conn)
    stock = StockMapper(conn)            # той самий conn — та сама транзакція

    order = orders.find_by_id(7)
    if order is None:
        raise LookupError("нема замовлення 7")

    order.cancel()                       # домен вирішує, чи можна
    orders.update(order)
    stock.release(order.lines)
```

`order.cancel()` стоїть посередині й нічого не знає ні про транзакцію, ні про мапер. Якщо замовлення відвантажене — він кине виняток, транзакція відкотиться, і в базу не піде нічого. Правило домену вберегло базу, ні разу про неї не почувши. Це і є те, за що патерн платять.

## Чотири пастки

### Пастка перша: id, якого в об'єкті нема

`insert` віддає новий `Order` з `id`, а той, що ти передав, лишається з `id === null`. Викликач, який цього не помітив і покликав далі `update(order)` на старому примірнику, отримає… нічого. `WHERE id = NULL` не збігається з жодним рядком — у SQL порівняння з `NULL` не істинне ніколи. Нуль оновлених рядків, нуль винятків, нуль слідів. Зміна просто не сталася.

Тому в `update` стоїть чотири рядки, які варті всієї решти:

```ts
const { rowCount } = await this.db.run(`UPDATE orders SET ... WHERE id = $5`, [...]);
if (rowCount === 0) throw new Error(`orders#${id}: рядка нема — його встигли видалити?`);
```

Правило загальне: **мапер ніколи не пише, не перевіривши, скільки рядків він зачепив.** Запит, який мав змінити один рядок і не змінив жодного, — це не «нічого не сталося», це збій, який прикидається успіхом.

І це той самий шов, у який згодом стає версія рядка:

```ts
`UPDATE orders SET ..., version = version + 1 WHERE id = $5 AND version = $6`
```

Перевірка та сама — `rowCount === 0`, — але значень у неї тепер два: або рядка нема, або хтось змінив його раніше за тебе. Це і є [оптимістичне блокування](book:programming/optimistic-locking), і воно вимагає рівно одну колонку та рівно одну умову. Якщо звичка перевіряти `rowCount` вже є — воно приходить майже задарма; якщо нема — його доведеться вкручувати в кожен метод окремо.

### Пастка друга: два джерела правди на одне число

Придивись до `total_cents`. Мапер його **пише** — з `order.total()`. І ніде не **читає**: у `findById` вибрано `placed_at`, `currency`, `status`, а підсумок рахується заново з позицій.

Отже, `orders.total_cents` — не дані. Це кеш, чиє єдине джерело правди — `order_lines`. Поки в нього пише лише мапер, розходження неможливе, і про це можна не думати роками.

Але колонка існує саме для того, щоб її читав **хтось інший** — той нічний звіт, заради якого її й завели. І цей інший бачить не кеш, а число. Одного разу воно виявиться неправильним (міграція, ручне виправлення, стара версія коду), хтось акуратно полагодить його `UPDATE`-ом — і полагоджене проживе до першого `update(order)`, який мовчки затре його сумою з позицій. Мапер навіть не помітить конфлікту: він цю колонку не читає.

Розв'язок — не в коді, а в рішенні, і рішень два. Або `total_cents` оголошено кешем домену: писати в нього має право лише мапер, а хто хоче правди — рахує з `order_lines`. Або навпаки, колонка є джерелом правди — і тоді `findById` мусить її читати, а `total()` із домену зникає.

Чого не можна — лишити питання без відповіді. Дешева страховка на цей випадок — гейт у самому мапері:

```ts
// у SELECT додано total_cents — не щоб ним користуватися, а щоб звірити
private build(head: HeadRow & { total_cents: number }, rows: LineRow[]): Order {
  const order = /* ...як було: збірка позицій і конструктор... */ this.assemble(head, rows);
  if (order.total().cents !== head.total_cents)
    throw new Error(
      `orders#${head.id}: total_cents=${head.total_cents}, а позиції дають ${order.total().cents}`);
  return order;
}
```

Ціна — одна колонка у `SELECT`. Виграш — розходження помітять у мить, коли воно з'явилося, а не у квартальному звіті, коли вже незрозуміло, яке з двох чисел правильне.

### Пастка третя: конструктор проти історії бази

`build` збирає `Order` **звичайним конструктором** — і конструктор виконує свої перевірки. Це велика перевага: з бази не влізе в пам'ять стан, який домен вважає неможливим. Мапер стає останнім фільтром між історією таблиці й твоїми правилами.

Але саме тому він і б'є. У базі **вже є** такий стан: замовлення без позицій із міграції п'ятирічної давнини, статус, якого нинішній `Status` не знає, від'ємна кількість із виправленого позаторік бага. `new Order(...)` кине `замовлення без позицій не буває` — і рядок №7 стане недосяжним для застосунку взагалі. Навіть для того, щоб його полагодити.

Ось чому справжні ORM конструктор **обходять**. SQLAlchemy при завантаженні не кличе `__init__` зовсім: її ORM працює приблизно як `pickle` — викликає низькорівневий `__new__` і тихо відновлює атрибути прямо на примірнику; для післязавантажувальної ініціалізації є окремий гачок `@reconstructor`. JPA заходить з іншого боку: специфікація вимагає від сутності конструктора без аргументів (публічного або захищеного), бо провайдер створює примірник рефлексією, а вже потім заповнює поля.

Обмін тепер видно чітко. ORM обирає **завантажити завжди**, ціною того, що суперечливий рядок безборонно доїде до пам'яті. Твій мапер обирає **не впустити суперечність**, ціною того, що частина бази стане нечитанною. Обидва варіанти захищаються — але лише коли обрано свідомо, а не «так вийшло».

Практична середина дешева: конструктор лишити суворим, а мапер хай ловить його виняток і загортає у свій, дописавши `id` рядка. Тоді посеред звіту впаде не безадресне «замовлення без позицій не буває», а `orders#7 не збирається: ...` — і ти одразу знаєш, який рядок лікувати.

### Пастка четверта: N+1 у власному мапері

`findByStatus` навмисно написаний двома запитами. Наївний варіант коротший на десять рядків:

```ts
// НЕ ТАК: один запит на голови + по запиту на кожну з них
const heads = await this.db.all<HeadRow>(`SELECT id FROM orders WHERE status = $1`, [status]);
return Promise.all(heads.map(h => this.findById(h.id)));   // 1 + N запитів
```

Сто замовлень — двісті один похід у базу замість двох. Це та сама `N+1`, яку прийнято приписувати ORM і [лінивому завантаженню](book:programming/lazy-loading), — тільки написана власноруч, свідомо й без жодного фреймворку поруч.

Іронія тут повчальна. Свій мапер пишуть саме заради контролю над запитами — і втрачають цей контроль у першій же множинній вибірці, бо `findById` уже є й перевикористати його спокусливо. Правило просте: **множинна вибірка — окремий метод із власними запитами, а не цикл по одиничній.** Кількість походів у базу не має залежати від кількості знайдених рядків — ні в ORM, ні у твоєму коді.

## Що з усього цього видно

Поглянь на чотири пастки разом — у них одна форма. Об'єкт не знає про мапера, тож не може підказати йому нічого: ні що змінився, ні що вже отримав `id`, ні що його підсумок розійшовся з колонкою. Щоразу мапер стоїть перед тим самим вибором із трьох: **спитати базу** (зайве читання), **запам'ятати самому** (зайвий стан), **повірити викликачеві** (зайва дисципліна).

Оце і є весь патерн, якщо зняти з нього назви. Реєстр завантажених об'єктів — це «запам'ятати самому» щодо тотожності. Знімок стану — «запам'ятати самому» щодо змін. Заглушка замість посилання — «спитати базу, але потім». Не три можливості фреймворку, а три відповіді на одне питання, яке ставить сама конструкція: знання винесли з об'єкта, і тепер його треба десь тримати.

Тому й чужий мапер найшвидше читається з одного питання: на кожному з цих місць — що він обрав? Якщо відповідь «нічого, воно якось само» — саме там він і зламається.
