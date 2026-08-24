# ⚙️ Одиниця роботи, що стежить сама

Наївна одиниця роботи змушує гукати її руками: змінив об'єкт — не забудь `register_dirty`; створив — `register_new`; викинув — `register_removed`. Це чесно й видно, але вада та сама, з якої весь патерн і починався, — треба **не забути**. Забув дописати `register_dirty` після зміни балів — і зміна тихо не збережеться, без жодної помилки.

Справжні інструменти цей клопіт прибирають. У SQLAlchemy ти пишеш `customer.points += 10` — і більше нічого; на фіксації сесія сама помічає, що поле розійшлося з тим, яким його прочитали, і додає рівно один `UPDATE`. Об'єкт мутуєш, як звичайний об'єкт у пам'яті, кличеш `commit` один раз — а вона сама з'ясовує, **що** змінилося, **в якому порядку** це писати, роздає **згенеровані ключі** й **чисто відкочується** на збої.

Зберемо саме таку — за зразком сесії SQLAlchemy. Щоб її побудувати, треба зчепити три речі: [карту тотожності](book:programming/identity-map) (звідки одиниця роботи взагалі знає про завантажені об'єкти), [мапери даних](book:programming/data-mapper) (хто перекладає об'єкт у SQL) і власне механізм звірки зі знімком.

## Ідея: центр, зчеплений із двома сусідами

Одиниця роботи нічого не робить сама — вона диригент. Ноти їй дають два сусіди, і без обох вона глуха.

**Ліворуч — [карта тотожності](book:programming/identity-map).** Це реєстр «один рядок бази ↔ один об'єкт у пам'яті». Кожен об'єкт, який ти читаєш із бази, проходить крізь неї: карта або віддає вже наявний екземпляр цього рядка, або кладе новий. Одиниця роботи чіпляється саме сюди: **в ту саму мить, коли об'єкт завантажується й лягає в карту, вона потайки знімає його стан** — робить знімок полів. Тому «список змінених об'єктів» узагалі має сенс: усі об'єкти, які треба перевірити на зміну, — це і є вміст карти, а знімок дає з чим порівнювати.

**Праворуч — [мапери](book:programming/data-mapper).** Одиниця роботи не пише SQL — вона не знає ні таблиць, ні стовпців. Коли настає час писати, вона для кожного об'єкта бере його мапер і доручає: `insert`, `update`, `delete`. Мапер перекладає об'єкт у рядок і виконує запит. Диригент вирішує **що** й **коли**; музику грають мапери.

Із цього зчеплення випливає весь механізм. **Автовідстеження** — це знімок при завантаженні й звірка при фіксації: збіглося — об'єкт чистий, розійшлося — «брудний», у `UPDATE`. **Упорядкована фіксація** — це топологічне впорядкування об'єктів за зовнішніми ключами, перш ніж кликати мапери. А **злив проти фіксації** — це різниця між «проштовхнути накопичений SQL у відкриту транзакцію» (щоб дістати згенеровані ключі й щоб наступний запит побачив зміни) і «завершити цю транзакцію остаточно».

## Каркас: домен і мапери

Почнімо з того, чого одиниця роботи торкатиметься. Об'єкти домену — звичайні, про базу не знають нічого (це й є суть [Data Mapper](book:programming/data-mapper)); ключ `id` спершу порожній — його призначить база на вставці.

```py
class Entity:
    def __init__(self):
        self.id = None                      # призначить база на INSERT

class Customer(Entity):
    def __init__(self, name, points=0):
        super().__init__()
        self.name, self.points = name, points

class Order(Entity):
    def __init__(self, customer):
        super().__init__()
        self.customer = customer            # посилання на батька
        self.total = 0
```

Мапер знає таблицю, вміє перекласти об'єкт у рядок і назад, виконати три команди — і, що важливо для порядку, **оголошує свої залежності**: на які типи цей вказує зовнішнім ключем. Метод `fields` віддає ті поля, що йдуть у знімок.

```py
class CustomerMapper:
    entity = Customer
    depends_on = ()                                     # ні на кого не вказує

    def load(self, id, cur):
        row = cur.execute("SELECT id, name, points FROM customer WHERE id=?",
                          (id,)).fetchone()
        if row is None: return None
        o = Customer(row[1], row[2]); o.id = row[0]; return o

    def insert(self, o, cur):
        cur.execute("INSERT INTO customer(name, points) VALUES (?, ?)",
                    (o.name, o.points))
        o.id = cur.lastrowid                            # база призначила ключ
    def update(self, o, cur):
        cur.execute("UPDATE customer SET name=?, points=? WHERE id=?",
                    (o.name, o.points, o.id))
    def delete(self, o, cur):
        cur.execute("DELETE FROM customer WHERE id=?", (o.id,))
    def fields(self, o):
        return {"name": o.name, "points": o.points}

class OrderMapper:
    entity = Order
    depends_on = (Customer,)                            # order.customer → потрібен спершу

    def load(self, id, cur):
        row = cur.execute('SELECT id, customer_id, total FROM "order" WHERE id=?',
                          (id,)).fetchone()
        if row is None: return None
        o = Order.__new__(Order); o.id = row[0]
        o.customer = None; o.total = row[2]; return o   # клієнта підтягне окремо
    def insert(self, o, cur):
        cur.execute('INSERT INTO "order"(customer_id, total) VALUES (?, ?)',
                    (o.customer.id, o.total))            # ЧИТАЄ o.customer.id — має вже бути!
        o.id = cur.lastrowid
    def update(self, o, cur):
        cur.execute('UPDATE "order" SET total=? WHERE id=?', (o.total, o.id))
    def delete(self, o, cur):
        cur.execute('DELETE FROM "order" WHERE id=?', (o.id,))
    def fields(self, o):
        return {"customer_id": o.customer.id if o.customer else None, "total": o.total}
```

Затримайся на одному рядку — `o.customer.id` в `OrderMapper.insert`. Замовлення пише в стовпець `customer_id` **ключ свого клієнта**. А ключ у клієнта з'являється лише після того, як його вставили в базу. Ось звідки візьметься весь клопіт із порядком: не можна вставити замовлення, поки клієнт не вставлений і не дістав ключа. Тримай цей рядок в голові — до нього все повернеться.

## Ядро: знімок на завантаженні, звірка на фіксації

Тепер сама одиниця роботи. Вона тримає з'єднання (одне з'єднання = одна транзакція), мапери за типом, карту тотожності `(тип, ключ) → об'єкт`, знімки `об'єкт → поля`, і два явні списки — новостворені й видалені. Чому новий і видалений — явні, а змінений — ні? Бо зміну знімок **вгадає** (поле розійшлося), а от народження й смерть — ні: щойно створеного об'єкта карта ще не бачила, тож нема з чим звіряти, а видалення — це намір, а не зміна поля.

:::tabs
```py
import copy

class UnitOfWork:
    def __init__(self, conn, mappers):
        self._conn = conn
        self._cur = conn.cursor()
        self._mappers = {m.entity: m for m in mappers}
        self._identity = {}        # (тип, ключ) → об'єкт  — карта тотожності
        self._snapshots = {}       # об'єкт → знімок полів
        self._new, self._removed = [], []

    # ── завантаження: тут народжується і карта, і знімок ──
    def read(self, cls, id):
        key = (cls, id)
        if key in self._identity:
            return self._identity[key]                 # той самий об'єкт — Identity Map
        obj = self._mappers[cls].load(id, self._cur)   # Data Mapper дістає рядок
        if obj is None:
            return None
        self._identity[key] = obj
        self._snapshot(obj)                            # запам'ятати стан на мить читання
        return obj

    def _snapshot(self, obj):
        self._snapshots[obj] = copy.deepcopy(self._mappers[type(obj)].fields(obj))

    # ── явна реєстрація для того, чого знімок не вгадає ──
    def register_new(self, obj):
        self._new.append(obj)                          # ключа ще нема — в карту потрапить на зливі
    def register_removed(self, obj):
        if obj in self._new:
            self._new.remove(obj); return              # народжене й убите — базі байдуже
        if obj not in self._removed:
            self._removed.append(obj)

    # ── автовідстеження: хто розійшовся зі своїм знімком ──
    def _dirty(self):
        out = []
        for obj, snap in self._snapshots.items():
            if obj in self._removed:
                continue
            if self._mappers[type(obj)].fields(obj) != snap:   # хоч одне поле інше
                out.append(obj)
        return out

    # ── топосорт за залежностями маперів: батько перед дитиною ──
    def _toposort(self, objs):
        order, seen = [], set()
        def visit(t):
            if t in seen: return
            seen.add(t)
            for parent in self._mappers[t].depends_on:
                visit(parent)
            order.append(t)                            # батьки лягають раніше
        for o in objs:
            visit(type(o))
        rank = {t: i for i, t in enumerate(order)}
        return sorted(objs, key=lambda o: rank[type(o)])

    # ── злив: проштовхнути SQL у транзакцію (ще НЕ завершити її) ──
    def flush(self):
        dirty = self._dirty()                          # порахувати ДО вставок
        for obj in self._toposort(self._new):          # згори вниз: батьки першими
            self._mappers[type(obj)].insert(obj, self._cur)   # призначає obj.id
            self._identity[(type(obj), obj.id)] = obj         # аж тепер має ключ → у карту
            self._snapshot(obj)                               # свіжий базовий знімок
        for obj in dirty:
            self._mappers[type(obj)].update(obj, self._cur)
            self._snapshot(obj)                               # скинути «брудність»
        for obj in reversed(self._toposort(self._removed)):   # знизу вгору: діти першими
            self._mappers[type(obj)].delete(obj, self._cur)
            self._identity.pop((type(obj), obj.id), None)
            self._snapshots.pop(obj, None)
        self._new.clear(); self._removed.clear()

    # ── фіксація: злити, а тоді завершити транзакцію ──
    def commit(self):
        try:
            self.flush()                               # увесь накопичений SQL
            self._conn.commit()                        # і аж тепер — остаточно
        except Exception:
            self._conn.rollback()                      # усе або нічого
            raise
```
```ts
type Ctor<T = object> = new (...a: never[]) => T;

interface Mapper<T = { id: number | null }> {
  entity: Ctor<T>;
  dependsOn: Ctor[];                                    // на які типи вказує ФК
  load(id: number, tx: Tx): Promise<T | null>;
  insert(o: T, tx: Tx): Promise<void>;                  // має заповнити o.id
  update(o: T, tx: Tx): Promise<void>;
  delete(o: T, tx: Tx): Promise<void>;
  fields(o: T): Record<string, unknown>;
}

class UnitOfWork {
  readonly #mappers = new Map<Ctor, Mapper>();
  readonly #identity = new Map<string, { id: number | null }>();   // "Тип#ключ" → об'єкт
  readonly #snapshots = new Map<object, string>();                 // об'єкт → знімок (серіалізований)
  readonly #tracked: object[] = [];                               // порядок обходу знімків
  #new: { id: number | null }[] = [];
  #removed: { id: number | null }[] = [];

  constructor(private readonly tx: Tx, mappers: Mapper[]) {
    for (const m of mappers) this.#mappers.set(m.entity, m);
  }

  // ── завантаження: карта + знімок в одну мить ──
  async read<T extends { id: number | null }>(cls: Ctor<T>, id: number): Promise<T | null> {
    const key = `${cls.name}#${id}`;
    if (this.#identity.has(key)) return this.#identity.get(key) as T;
    const obj = await this.#mappers.get(cls)!.load(id, this.tx) as T | null;
    if (!obj) return null;
    this.#identity.set(key, obj);
    this.#snapshot(obj);
    return obj;
  }

  registerNew(o: { id: number | null }): void { this.#new.push(o); }
  registerRemoved(o: { id: number | null }): void {
    const i = this.#new.indexOf(o);
    if (i >= 0) { this.#new.splice(i, 1); return; }     // народжене й убите — пропустити
    if (!this.#removed.includes(o)) this.#removed.push(o);
  }

  #mapperOf(o: object): Mapper { return this.#mappers.get(o.constructor as Ctor)!; }
  #snapshot(o: object): void {
    this.#snapshots.set(o, JSON.stringify(this.#mapperOf(o).fields(o)));
    if (!this.#tracked.includes(o)) this.#tracked.push(o);
  }

  // ── автовідстеження: хто розійшовся зі знімком ──
  #dirty(): object[] {
    return this.#tracked.filter(o =>
      !this.#removed.includes(o as { id: number | null }) &&
      JSON.stringify(this.#mapperOf(o).fields(o)) !== this.#snapshots.get(o));
  }

  // ── топосорт: батько перед дитиною ──
  #toposort<T extends object>(objs: T[]): T[] {
    const order: Ctor[] = [], seen = new Set<Ctor>();
    const visit = (t: Ctor) => {
      if (seen.has(t)) return;
      seen.add(t);
      for (const p of this.#mappers.get(t)!.dependsOn) visit(p);
      order.push(t);
    };
    for (const o of objs) visit(o.constructor as Ctor);
    const rank = new Map(order.map((t, i) => [t, i] as const));
    return [...objs].sort((a, b) =>
      rank.get(a.constructor as Ctor)! - rank.get(b.constructor as Ctor)!);
  }

  // ── злив: SQL у транзакцію, але транзакція ще жива ──
  async flush(): Promise<void> {
    const dirty = this.#dirty();                        // порахувати ДО вставок
    for (const o of this.#toposort(this.#new)) {        // згори вниз
      await this.#mapperOf(o).insert(o, this.tx);       // призначає o.id
      this.#identity.set(`${o.constructor.name}#${(o as { id: number }).id}`, o as { id: number });
      this.#snapshot(o);
    }
    for (const o of dirty) { await this.#mapperOf(o).update(o, this.tx); this.#snapshot(o); }
    for (const o of this.#toposort(this.#removed).reverse()) {   // знизу вгору
      await this.#mapperOf(o).delete(o, this.tx);
      this.#identity.delete(`${o.constructor.name}#${(o as { id: number }).id}`);
      this.#snapshots.delete(o);
    }
    this.#new = []; this.#removed = [];
  }

  async commit(): Promise<void> {
    try { await this.flush(); await this.tx.commit(); }
    catch (e) { await this.tx.rollback(); throw e; }
  }
}
```
:::

Прочитай `commit` знизу вгору й побачиш увесь патерн у чотири ходи. `_dirty()` звіряє кожен знімок із поточним станом — так автовідстеження знаходить змінених. `_toposort` шикує об'єкти за графом зовнішніх ключів. `flush` виконує вставки (батьки першими), оновлення й видалення (діти першими) через мапери. І лише `commit` завершує транзакцію — або відкочує все на будь-якому збої.

## Як воно біжить

Заведемо базу в пам'яті й проженемо повний цикл.

```py
import sqlite3
conn = sqlite3.connect(":memory:")
conn.executescript('''
  CREATE TABLE customer("id" INTEGER PRIMARY KEY, name TEXT, points INT);
  CREATE TABLE "order"("id" INTEGER PRIMARY KEY, customer_id INT, total INT);
''')
mappers = [CustomerMapper(), OrderMapper()]

# ── операція 1: створити клієнта й замовлення ──
uow = UnitOfWork(conn, mappers)
alice = Customer("Аліса")
order = Order(alice); order.total = 250
uow.register_new(order)                # навмисне В НЕПРАВИЛЬНОМУ порядку:
uow.register_new(alice)                #   спершу замовлення, тоді клієнт
uow.commit()

print(alice.id)                        # → 1  — база призначила ключ клієнтові
print(conn.execute('SELECT customer_id FROM "order"').fetchone())   # → (1,)
```

Ми зареєстрували замовлення **раніше** за клієнта — а база не спіткнулася. Топосорт побачив, що `OrderMapper.depends_on == (Customer,)`, і всупереч порядку реєстрації вставив спершу `alice` (дістала ключ `1`), а тоді `order`, чий `customer_id` у базі вже дорівнює `1`. Той самий рядок `o.customer.id`, що я просив запам'ятати, спрацював без пригод саме тому, що ключ клієнта на той момент уже існував.

Тепер — автовідстеження без жодного `register_dirty`:

```py
# ── операція 2: змінити бали ──
uow2 = UnitOfWork(conn, mappers)
a = uow2.read(Customer, 1)             # у карту + знімок {name:"Аліса", points:0}
a.points += 25                         # просто мутуємо об'єкт
uow2.commit()                          # _dirty() бачить points 0 → 25 → один UPDATE
```

Ми ніде не сказали одиниці роботи, що клієнт змінився. Вона з'ясувала це сама: на читанні зняла знімок `{points: 0}`, на фіксації побачила `{points: 25}` і з розбіжності вивела рівно один `UPDATE`. Якби ми написали `a.points += 25`, а потім `a.points -= 25`, знімок і поточний стан збіглися б — і фіксація не породила б **жодного** SQL. Звірка полів — це не тільки виявлення змін, а й глушник зайвих записів.

## Злив — не фіксація

У коді `commit` кличе `flush`, а вже потім `conn.commit()`. Ці двоє — різні речі, і плутанина між ними коштує найдорожче.

**Злив (англ. *flush* — «проштовхнути») виконує накопичений SQL усередині відкритої [транзакції](book:programming/transactions-acid).** Після зливу база вже знає про твої вставки — і, головне, вже **призначила згенеровані ключі**: `alice.id` став `1` саме на зливі, до жодної фіксації. Але зміни ще не остаточні: інше з'єднання їх не бачить, а `rollback` досі може стерти все начисто.

**Фіксація (commit) завершує саму транзакцію** — робить зміни остаточними й видимими всім. `commit` завжди спершу зливає (інакше не було б чого фіксувати), тож `flush` перед `commit` — надлишковий.

Навіщо ж окремий `flush`, якщо `commit` і так зливає? Через **згенеровані ключі**. Згадай `OrderMapper.insert`: щоб вставити замовлення, треба вже мати `alice.id`. Якби клієнт і замовлення були в різних операціях, довелося б **злити** вставку клієнта посеред роботи — дістати його ключ, — і лише тоді будувати замовлення. Топосорт дає **порядок**; злив дає **момент**, коли ключ батька матеріалізується для дитини.

Звідси й **автозлив** серйозних ORM: перед кожним запитом сесія тихо зливає накопичене, щоб запит побачив ще незафіксовані зміни. Зручно — і водночас джерело найпідступнішої з усіх пасток.

![Що діється всередині зливу: вхід — карта тотожності зі знімками плюс списки нових і видалених; далі звірка полів зі знімком відсіює справді змінених; топосорт шикує їх за зовнішніми ключами; виконання кличе мапери — INSERT призначає ключі, UPDATE і DELETE лягають у транзакцію; наприкінці свіжий знімок скидає «брудність». Знизу підпис: commit = злив плюс завершити транзакцію; збій відкочує її й скидає карту та знімки](img/flush-pipeline.svg)

*Злив — це конвеєр, а не сліпий перебір: звірити зі знімком, упорядкувати за ключами, виконати через мапери, переснімкувати. Фіксація лише додає останній крок — завершити транзакцію; відкат замість нього не лишає в базі жодного сліду.*

## Складність і пастки

Робочий каркас вище показує кістяк. Але між ним і промисловою сесією лежить смуга пасток, і кожна колись когось вкусила.

**Знімок мілкий — колекції течуть повз нього.** Наш `_snapshot` рятує `copy.deepcopy`, та початкова спокуса — узяти `dict(fields)`, який копіює **значення** полів. Для чисел і рядків цього досить. Але додай замовленню список позицій `order.lines` і поклади його у знімок мілкою копією — знімок збереже **те саме посилання** на список. Допишеш позицію через `order.lines.append(...)` — посилання не змінилося, звірка каже «збіглося», зміна **невидима**. Тому справжні ORM не покладаються на голий знімок для зв'язків: SQLAlchemy загортає колекції в інструментовані обгортки, і будь-який `append`/`remove` одразу позначає власника зміненим. Знімок добрий для скалярних полів; для колекцій потрібне або глибоке копіювання, або перехоплення.

**Ключ карти до і після вставки — різний.** Карта індексує об'єкт за `(тип, ключ)`. Але щойно створений об'єкт має `id = None` — його нема за чим індексувати, тож він живе окремим списком `_new`. І аж на зливі, коли база призначить ключ, він потрапляє в карту під `(тип, id)`. Пастка: спробуй `read(Order, id)` для замовлення, яке ще висить у `_new` і не злите, — карта його не знайде, мапер завантажить рядок наново, і на один рядок ти дістанеш **два об'єкти**. А це рівно те, що [карта тотожності](book:programming/identity-map) має забороняти. Ліки — автозлив перед запитом (щоб об'єкт устиг дістати ключ і лягти в карту) або окреме індексування нових за тотожністю самого об'єкта.

**Автозлив — тихий постріл у ногу.** Він рятує від попередньої пастки, але заводить свою. Запит **усередині** напівзібраної операції змусить злити ще недороблений об'єкт — і той упреться в обмеження `NOT NULL` чи зовнішнього ключа завчасно, задовго до `commit`. Помилка вилізе далеко від причини: ти лише читав щось геть інше, а впала вставка напівпорожнього об'єкта, який ти ще не встиг доробити. Це класична загадка «звідки тут `IntegrityError`, я ж нічого не зберігав» у SQLAlchemy. Захист — доводь об'єкт до повного стану, перш ніж робити будь-який запит, або вимикай автозлив на такому блоці.

**Цикли ламають топологічний порядок.** Наш топосорт мовчки припускає, що граф залежностей — без циклів. А хай клієнт знає «останнє замовлення» (`customer.last_order_id → order`), а замовлення знає клієнта (`order.customer_id → customer`). Тепер жодного не можна вставити першим: кожному для вставки потрібен ключ іншого. Топологічного порядку **не існує взагалі** — і `visit` у такому графі зациклиться. Промислові ORM розривають цикл окремим ходом: вставляють один бік із зовнішнім ключем `NULL`, а тоді, коли обидва вже мають ключі, доганяють одним `UPDATE` (у SQLAlchemy це `post_update`). Тобто циклічний зв'язок коштує зайвого запису — вставка з діркою плюс оновлення, що її латає.

**Відкат не відмотує пам'ять.** `conn.rollback()` повертає **базу** в стан до операції — але твої об'єкти в пам'яті цього не знають. `alice.points` лишиться `25`, хоч у базі знову `0`; гірше — `alice.id` лишиться `1`, хоч рядок із таким ключем відкотом стерто. Знову скористаєшся тими об'єктами чи тією ж одиницею роботи — і матимеш стан пам'яті, що **суперечить** базі. Тому на відкоті мало відкотити з'єднання: треба ще й **знедійснити карту й знімки** (SQLAlchemy на відкоті «протухає» всі об'єкти сесії, щоб наступне звернення перечитало їх із бази), а призначені ключі вважати недійсними.

**Суперечки доступу владнуються теж на зливі.** Якщо між читанням і записом рядок змінив хтось інший, наш `update` наосліп затре чужу зміну. Місце для запобіжника — рівно тут, у мапері: додати стовпець версії й писати `UPDATE ... WHERE id=? AND version=?`. Нуль зачеплених рядків означає, що версія зрушила під тобою, — і фіксацію треба відхилити. Це [оптимістичне блокування](book:programming/optimistic-locking), і його природний дім — мить зливу, єдина, коли одиниця роботи торкається бази й може звірити версії.

Зведемо в одне. Робоча одиниця роботи — це не три списки й цикл по них, а конвеєр: **знімок при завантаженні** дає базу для звірки, **звірка при зливі** знаходить змінених без нагадувань, **топологічне впорядкування** шикує записи за зовнішніми ключами, **злив** матеріалізує ключі всередині транзакції, а **фіксація** запечатує її — або відкат стирає без сліду. Кожна ланка чіпляється за сусідню, і диригент лишається тонким саме тому, що всю чорну роботу — SQL і тотожність — робить не він, а два його сусіди.
