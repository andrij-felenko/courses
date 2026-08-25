# ⚙️ Один граф, три заглушки, лічильник запитів

Про ліниве завантаження легко говорити абстрактно й важко відчути, поки не побачиш ціну очима. Тому зберемо крихітну робочу лабораторію: справжній код, який запускається, крихітний домен `Order → Customer`, фейкове сховище — і **лічильник запитів**, вбудований у це сховище. Лічильник тут головний прилад. Кожен похід у базу штовхає його на одиницю, і невидимі раніше поїздки по дані стають числом, за яким можна стежити. Ми над одним і тим самим графом побудуємо три різні ліниві заглушки, роздивимося, чим вони різняться в поведінці, тоді відтворимо горезвісний N+1 **живцем** — і полікуємо його в три щаблі, дивлячись, як лічильник падає зі 101 до 1.

Мова тут — загальний доступ до даних, тож приклади йдуть у TypeScript і Python: та сама логіка, кожна вкладка ідіоматична своєю мовою.

## Задача: зробити ціну видимою

Уяви екран — список замовлень, у кожному рядку номер, сума й **ім'я покупця**. Даних небагато: сто замовлень, а покупців усього троє (замовлення розкидані між ними по колу). Питання, на яке ми хочемо чесну відповідь у числах: **скільки разів код сходить у базу**, щоб намалювати цей екран? Наївний спосіб «просто прочитати `order.customer.name` у циклі» виглядає невинно, але кожне таке читання може обернутися окремою поїздкою. Поки поїздки невидимі, ніхто їх не рахує — і застосунок тихо повзе. Ми зробимо їх видимими.

## Сховище, що рахує кожен похід

Сховище — це дві «таблиці» в пам'яті (покупці й замовлення) плюс поле `queries`. Домовимося про єдине правило: **кожен метод, що дістає дані, — це один похід у базу, тож він штовхає лічильник**. Так один об'єкт бере на себе роль і бази, і секундоміра.

:::tabs
```py
class Db:
    """Фейкове сховище: дві «таблиці» в пам'яті; кожен похід рахуємо."""
    def __init__(self) -> None:
        self.customers = {
            1: {"id": 1, "name": "Ада",   "city": "Лондон"},
            2: {"id": 2, "name": "Грейс", "city": "Нью-Йорк"},
            3: {"id": 3, "name": "Лінус", "city": "Гельсінкі"},
        }
        # 100 замовлень, розкидані лише на трьох покупців: (i % 3) + 1
        self.orders = {
            i: {"id": i, "customer_id": (i % 3) + 1, "total": 10 * i}
            for i in range(1, 101)
        }
        self.queries = 0                                  # лічильник запитів

    def find_all_orders(self) -> list[dict]:
        self.queries += 1                                 # один SELECT на весь список
        return [dict(r) for r in self.orders.values()]

    def find_customer(self, cid: int) -> dict:
        self.queries += 1                                 # один SELECT на один рядок
        return dict(self.customers[cid])

    def find_customers(self, ids: list[int]) -> dict[int, dict]:
        self.queries += 1                                 # один SELECT ... WHERE id IN (...)
        want = set(ids)
        return {cid: dict(r) for cid, r in self.customers.items() if cid in want}

    def find_orders_join_customer(self) -> list[dict]:
        self.queries += 1                                 # один SELECT ... JOIN — покупець їде в кожному рядку
        out = []
        for r in self.orders.values():
            row = dict(r)
            row["customer"] = dict(self.customers[r["customer_id"]])
            out.append(row)
        return out
```
```ts
type Row = Record<string, any>;

class Db {
  // дві «таблиці» в пам'яті; кожен похід рахуємо
  private customers = new Map<number, Row>([
    [1, { id: 1, name: "Ада",   city: "Лондон" }],
    [2, { id: 2, name: "Грейс", city: "Нью-Йорк" }],
    [3, { id: 3, name: "Лінус", city: "Гельсінкі" }],
  ]);
  private orders = new Map<number, Row>(
    Array.from({ length: 100 }, (_, k): [number, Row] => {
      const i = k + 1;                       // замовлення розкидані на трьох: (i % 3) + 1
      return [i, { id: i, customerId: (i % 3) + 1, total: 10 * i }];
    }),
  );
  queries = 0;                                            // лічильник запитів

  findAllOrders(): Row[] {
    this.queries++;                                       // один SELECT на весь список
    return [...this.orders.values()].map((r) => ({ ...r }));
  }
  findCustomer(id: number): Row {
    this.queries++;                                       // один SELECT на один рядок
    return { ...this.customers.get(id)! };
  }
  findCustomers(ids: number[]): Map<number, Row> {
    this.queries++;                                       // один SELECT ... WHERE id IN (...)
    const want = new Set(ids);
    const out = new Map<number, Row>();
    for (const [id, r] of this.customers) if (want.has(id)) out.set(id, { ...r });
    return out;
  }
  findOrdersJoinCustomer(): Row[] {
    this.queries++;                                       // один SELECT ... JOIN — покупець їде в кожному рядку
    return [...this.orders.values()].map((r) => ({
      ...r,
      customer: { ...this.customers.get(r.customerId)! },
    }));
  }
}
```
:::

Кожен метод повертає **свіжі копії** рядків, а не самі внутрішні об'єкти — так, як робить справжня база: вона матеріалізує нові рядки на кожен запит, і два різні `find_customer(1)` дають два різні об'єкти в пам'яті. Ця дрібниця стане важливою, коли дійде до тотожності.

## Три заглушки над одним покупцем

Тепер побудуємо над цим сховищем трьох різних лінивих посередників до покупця — ліниве поле, віртуальний проксі й привид. Усі троє мають ту саму мету (не ходити в базу, поки по покупця не прийшли), але тримають лінь у різних місцях.

:::tabs
```py
# 1) Ліниве поле: лінь живе в самому Order — порожній слот плюс властивість.
class OrderLazyField:
    def __init__(self, db: Db, row: dict) -> None:
        self._db = db
        self.id = row["id"]
        self.total = row["total"]
        self._customer_id = row["customer_id"]
        self._customer: dict | None = None                # ще не тягли
    @property
    def customer(self) -> dict:
        if self._customer is None:
            self._customer = self._db.find_customer(self._customer_id)
        return self._customer

# 2) Віртуальний проксі: ОКРЕМИЙ об'єкт із тим самим інтерфейсом, що й покупець.
class CustomerProxy:
    def __init__(self, db: Db, cid: int) -> None:
        self._db, self._cid, self._real = db, cid, None
    def _load(self) -> dict:
        if self._real is None:
            self._real = self._db.find_customer(self._cid)  # справжнього створює раз
        return self._real
    @property
    def name(self) -> str: return self._load()["name"]      # кожен метод делегує
    @property
    def city(self) -> str: return self._load()["city"]

# 3) Привид: сам покупець, але створений з одним id і порожніми полями.
class CustomerGhost:
    def __init__(self, db: Db, cid: int) -> None:
        self._db = db
        self.id = cid                                       # тотожність правильна від початку
        self._loaded = False
        self._name = self._city = ""
    def _fill(self) -> None:
        if not self._loaded:
            row = self._db.find_customer(self.id)           # один запит — і ВСІ поля разом
            self._name, self._city = row["name"], row["city"]
            self._loaded = True
    @property
    def name(self) -> str: self._fill(); return self._name
    @property
    def city(self) -> str: self._fill(); return self._city
```
```ts
// 1) Ліниве поле: лінь живе в самому Order — порожній слот плюс геттер.
class OrderLazyField {
  readonly id: number;
  readonly total: number;
  private customerId: number;
  private _customer: Row | null = null;                    // ще не тягли
  constructor(private db: Db, row: Row) {
    this.id = row.id;
    this.total = row.total;
    this.customerId = row.customerId;
  }
  get customer(): Row {
    return (this._customer ??= this.db.findCustomer(this.customerId));
  }
}

// 2) Віртуальний проксі: окремий об'єкт із тим самим інтерфейсом.
interface Customer { readonly name: string; readonly city: string; }

class CustomerProxy implements Customer {
  private real: Row | null = null;
  constructor(private db: Db, private id: number) {}
  private load(): Row { return (this.real ??= this.db.findCustomer(this.id)); }  // справжнього — раз
  get name(): string { return this.load().name; }          // кожен метод делегує
  get city(): string { return this.load().city; }
}

// 3) Привид: сам покупець з одним id і порожніми полями.
class CustomerGhost implements Customer {
  private loaded = false;
  private _name = "";
  private _city = "";
  constructor(private db: Db, readonly id: number) {}       // тотожність правильна від початку
  private fill(): void {
    if (this.loaded) return;
    const row = this.db.findCustomer(this.id);              // один запит — і ВСІ поля разом
    this._name = row.name;
    this._city = row.city;
    this.loaded = true;
  }
  get name(): string { this.fill(); return this._name; }
  get city(): string { this.fill(); return this._city; }
}
```
:::

Тепер підключимо лічильник і поштрикаємо заглушку пальцем, дивлячись на число. Проксі тут — але точнісінько так само поводяться ліниве поле й привид:

:::tabs
```py
db = Db()
c = CustomerProxy(db, 1)
print(db.queries)     # 0  — заглушка ще нічого не тягла
print(c.name)         # Ада      ← перший доступ збігав у базу
print(db.queries)     # 1
print(c.city)         # Лондон   ← рядок уже в руках, бази не чіпаємо
print(db.queries)     # 1  (не 2!)
```
```ts
const db = new Db();
const c = new CustomerProxy(db, 1);
console.log(db.queries);   // 0  — заглушка ще нічого не тягла
console.log(c.name);       // Ада      ← перший доступ збігав у базу
console.log(db.queries);   // 1
console.log(c.city);       // Лондон   ← рядок уже в руках, бази не чіпаємо
console.log(db.queries);   // 1  (не 2!)
```
:::

Число розповідає всю поведінку: `0` до дотику, `1` після першого дотику, і той самий `1` після другого — бо перший доступ витяг **увесь рядок** (усі поля разом), і друге поле вже нікуди не бігає. Так само поводяться всі три заглушки.

А от у чому вони **не** однакові — це тотожність. Проксі — окремий об'єкт, він лише вдає покупця; справжній рядок, який він тримає всередині, — це вже інший об'єкт. Тому `proxy` і будь-який `find_customer(1)`, узятий деінде, — **дві різні речі в пам'яті**, і перевірка на тотожність між ними дасть хибу. Привид натомість — це **сам** покупець, лише напівпорожній: його тотожність правильна від першого рядка. Саме тому проксі майже завжди ходять у парі з реєстром об'єктів, який стежить, щоб один рядок бази давав один об'єкт у пам'яті.

> 🔧 **Навіщо це.** Різниця «окремий заступник проти самого об'єкта» — не педантизм. Щойно в системі два об'єкти вдають один рядок, ламається все, що звіряє сутності за посиланням: кеші, множини відвіданого, порівняння «це той самий покупець?». Проксі вимагає [мапи тотожності](topic:sf-data/identity-map) як страховки; привид цю проблему знімає в зародку — і саме тому справжні [ORM](topic:sf-data/orm) найчастіше повертають зв'язки привидами, а не проксі.

## Рій запитів: N+1 живцем

Заглушки поводяться чудово, поки їх торкаються зрідка. Тепер зробимо те, від чого вони ламаються: поставимо ліниве завантаження за замовчуванням і **пройдемося циклом**. Дістанемо всі замовлення одним запитом, а тоді для кожного намалюємо ім'я покупця — тобто торкнемося лінивого поля сто разів:

:::tabs
```py
db = Db()
orders = [OrderLazyField(db, r) for r in db.find_all_orders()]   # +1 запит
for o in orders:
    _ = o.customer["name"]        # кожен дотик будить лінивого покупця → окремий SELECT
print(db.queries)                 # 101
```
```ts
const db = new Db();
const orders = db.findAllOrders().map((r) => new OrderLazyField(db, r));  // +1 запит
for (const o of orders) {
  void o.customer.name;           // кожен дотик будить лінивого покупця → окремий SELECT
}
console.log(db.queries);          // 101
```
:::

```
1 запит    — find_all_orders()          → 100 замовлень
+ 100      — find_customer(?)  ×100      (по разу на кожен дотик у циклі)
= 101 запит  заради одного екрана
```

Ось він, **N+1** живцем: одна логічна дія («покажи список») розсипалася на 1 + N дрібних поїздок. Але придивись до чисел уважніше, і побачиш ще гіршу подробицю. Покупців у нас **троє**. Отже, зі ста походів по покупця дев'яносто сім — це повторне витягування **тих самих трьох рядків**, знову й знову. Лінь не просто множить запити — вона їх ще й дублює, бо кожне ліниве поле живе в своєму замовленні й не знає, що сусіднє замовлення вже тягло того самого покупця. Докладний розбір того, як ці числа ростуть із розміром вибірки, лежить в [окремому розборі N+1](topic:sf-data/active-record/math-n-plus-one.md); нам зараз досить бачити, що 101 — це діагноз, а не вирок.

## Ліки в три щаблі

Лікувати N+1 відмовою від лінивого завантаження — все одно що лікувати кашель, перестаючи дихати. Лінь на своєму місці корисна: вона не тягне павутину, поки по неї не прийшли. Проблема не в лінощах, а в тому, що на **відомій наперед стежці** (ми точно пройдемося по всіх покупцях) лінь вибрала найгіршу тактику. Полагодимо це трьома дедалі сильнішими ходами.

### Щабель перший: спільна мапа тотожності → 4 запити

Найдешевший хід не чіпає структуру запитів узагалі — він лише прибирає дублі. Заведемо один спільний кеш, ключований за id: перший похід по покупця №2 іде в базу, а всі наступні дотики до №2 віддають той самий уже завантажений об'єкт. Це і є [мапа тотожності](topic:sf-data/identity-map) — реєстр «один id → один об'єкт у пам'яті».

:::tabs
```py
class IdentityMap:
    def __init__(self, db: Db) -> None:
        self._db, self._cache = db, {}
    def customer(self, cid: int) -> dict:
        if cid not in self._cache:                    # у базу — лише на першу зустріч id
            self._cache[cid] = self._db.find_customer(cid)
        return self._cache[cid]                        # далі — той самий об'єкт
```
```ts
class IdentityMap {
  private cache = new Map<number, Row>();
  constructor(private db: Db) {}
  customer(id: number): Row {
    let row = this.cache.get(id);
    if (!row) { row = this.db.findCustomer(id); this.cache.set(id, row); }  // у базу — раз на id
    return row;
  }
}
```
:::

Тепер цикл на сто замовлень чіпає базу рівно стільки разів, скільки є **різних** покупців. Перша зустріч кожного з трьох id — похід у базу; решта дев'яносто сім дотиків обслуговує кеш. `1 + 3 = 4`. Тобто дев'яносто сім зайвих поїздок випарувалися від одного маленького словника, і ми навіть не міняли того, що цикл лінивий.

### Щабель другий: пакетний запит наперед → 2 запити

Мапа тотожності прибрала дублі, але залишила по одному запиту на кожного **різного** покупця. Якщо покупців не троє, а тисяча, це знову тисяча поїздок. Наступний хід — не тягнути їх поодинці зовсім: зібрати всі потрібні id заздалегідь і попросити базу віддати їх **одним** запитом `WHERE id IN (...)`.

:::tabs
```py
db = Db()
rows = db.find_all_orders()                                # +1
customers = db.find_customers([r["customer_id"] for r in rows])   # +1: усі id одним IN-запитом
for r in rows:
    _ = customers[r["customer_id"]]["name"]                # уже в пам'яті — жодного запиту
print(db.queries)                                          # 2
```
```ts
const db = new Db();
const rows = db.findAllOrders();                           // +1
const customers = db.findCustomers(rows.map((r) => r.customerId));  // +1: усі id одним IN-запитом
for (const r of rows) {
  void customers.get(r.customerId)!.name;                  // уже в пам'яті — жодного запиту
}
console.log(db.queries);                                   // 2
```
:::

Тепер незалежно від того, троє покупців чи тисяча, поїздок рівно дві: одна по замовлення, одна по всіх їхніх покупців разом. Цю ідею — «збери ключі за один тік і завантаж їх однією пачкою» — колись оформили в окремий інструмент: **DataLoader**. Він виріс із внутрішнього механізму «Loader», що його Ніколас Шрок збудував у Facebook близько 2010 року в межах системи Ent, а згодом Лі Байрон виніс у публічну бібліотеку; DataLoader сам збирає всі `.load(id)` в межах одного тіку в єдиний пакетний запит і кешує результат на час запиту — тобто робить рівно те, що ми щойно зробили руками, тільки прозоро для коду в циклі. Саме він став стандартними ліками від N+1 у світі GraphQL.

### Щабель третій: жадібне з'єднання → 1 запит

Два запити — це вже майже нічого, але можна й один. Якщо база вміє з'єднувати таблиці (а реляційна база саме для цього й створена), попросимо її повернути замовлення **разом** із покупцем в одному рядку результату — жадібне з'єднання:

:::tabs
```py
db = Db()
rows = db.find_orders_join_customer()      # +1: JOIN тягне покупця в кожному рядку
for row in rows:
    _ = row["customer"]["name"]            # покупець уже приїхав разом із замовленням
print(db.queries)                          # 1
```
```ts
const db = new Db();
const rows = db.findOrdersJoinCustomer();  // +1: JOIN тягне покупця в кожному рядку
for (const row of rows) {
  void (row.customer as Row).name;         // покупець уже приїхав разом із замовленням
}
console.log(db.queries);                   // 1
```
:::

Один похід — і на екрані все. Сто один запит перетворився на один.

## Повний стенд і драбина чисел

Складемо всі чотири стратегії в один стенд і виміряємо їх поряд, кожну на свіжому лічильнику:

:::tabs
```py
def scenario_naive() -> int:
    db = Db()
    orders = [OrderLazyField(db, r) for r in db.find_all_orders()]
    for o in orders: _ = o.customer["name"]
    return db.queries

def scenario_identity_map() -> int:
    db = Db()
    imap = IdentityMap(db)
    for r in db.find_all_orders(): _ = imap.customer(r["customer_id"])["name"]
    return db.queries

def scenario_batch() -> int:
    db = Db()
    rows = db.find_all_orders()
    customers = db.find_customers([r["customer_id"] for r in rows])
    for r in rows: _ = customers[r["customer_id"]]["name"]
    return db.queries

def scenario_join() -> int:
    db = Db()
    for row in db.find_orders_join_customer(): _ = row["customer"]["name"]
    return db.queries

print("запитів  стратегія")
for run, name in [(scenario_naive,        "ліниво в циклі"),
                  (scenario_identity_map, "+ мапа тотожності"),
                  (scenario_batch,        "пакетний IN-запит"),
                  (scenario_join,         "жадібний JOIN")]:
    print(f"{run():>7}  {name}")
```
```ts
function scenarioNaive(): number {
  const db = new Db();
  const orders = db.findAllOrders().map((r) => new OrderLazyField(db, r));
  for (const o of orders) void o.customer.name;
  return db.queries;
}
function scenarioIdentityMap(): number {
  const db = new Db();
  const imap = new IdentityMap(db);
  for (const r of db.findAllOrders()) void imap.customer(r.customerId).name;
  return db.queries;
}
function scenarioBatch(): number {
  const db = new Db();
  const rows = db.findAllOrders();
  const customers = db.findCustomers(rows.map((r) => r.customerId));
  for (const r of rows) void customers.get(r.customerId)!.name;
  return db.queries;
}
function scenarioJoin(): number {
  const db = new Db();
  for (const row of db.findOrdersJoinCustomer()) void (row.customer as Row).name;
  return db.queries;
}

console.log("запитів  стратегія");
for (const [run, name] of [
  [scenarioNaive,        "ліниво в циклі"],
  [scenarioIdentityMap,  "+ мапа тотожності"],
  [scenarioBatch,        "пакетний IN-запит"],
  [scenarioJoin,         "жадібний JOIN"],
] as [() => number, string][]) {
  console.log(`${String(run()).padStart(7)}  ${name}`);
}
```
:::

```
запитів  стратегія
    101  ліниво в циклі
      4  + мапа тотожності
      2  пакетний IN-запит
      1  жадібний JOIN
```

![Горизонтальна драбина: чотири стратегії, довжина стовпчика за логарифмом числа запитів. Найдовший червоний стовпчик — 101 (ліниво в циклі, без спільної мапи); коротший бурштиновий — 4 (ліниво плюс мапа тотожності, 100 дотиків склеєні у 3 покупці); ще коротший синій — 2 (пакетний IN-запит); найкоротший зелений — 1 (жадібне з'єднання JOIN). Внизу підпис: 101 до 4 до 2 до 1](img/query-ladder.svg)

*Той самий екран над тим самим графом коштує від 101 до 1 запиту — залежно не від лінощів, а від того, чи знали ми свій сценарій. Мапа тотожності прибирає дублі, пакетний запит тягне всіх одним махом, з'єднання забирає геть усе однією поїздкою.*

Драбина `101 → 4 → 2 → 1` — це, по суті, вся мораль лінивого завантаження в чотирьох числах. Лінь **сама по собі** не рятує: наївний лінивий цикл дав найгірше число. Рятує **знання свого сценарію** — коли наперед відомо, що зв'язок точно знадобиться, його беруть жадібно.

## Складність і пастки

Числа спокусливо чисті, тож варто одразу назвати місця, де реальність кусається.

**Лінь ховає ціну.** Найпідступніше в `order.customer.name` те, що воно виглядає як звичайне читання поля, а насправді може бути поїздкою на інший бік мережі. Око не бачить різниці між дешевим доступом до пам'яті й дорогим запитом — і саме тому N+1 так легко просочується в код. Лічильник із цього прикладу — не навчальна іграшка: у справжніх системах його варто тримати назавжди. Обгорни тест перевіркою «цей ендпойнт не має робити більше ніж K запитів» — і регресія N+1 впаде на збірці, а не на проді.

**Жадібність теж має ціну — протилежну.** Три щаблі ліків тягнуть **усе** наперед. Це виграш, лише якщо дані справді потрібні. Якщо на екрані показують сотню замовлень, а покупця розкривають натисканням лише в кількох — жадібний JOIN щоразу тягне сто покупців, з яких дивляться на трьох. Тоді ти проміняв N+1 на постійний перетяг зайвого. Правильний хід — не «завжди жадібно», а «жадібно саме на тій стежці, якою точно підеш».

**У пакетного запиту є стеля.** `WHERE id IN (...)` не безрозмірний. Oracle історично не пускав більше ніж 1000 виразів у списку (помилка `ORA-01795`; у версії 23ai стелю підняли до 65535), а SQL Server обмежує один запит 2100 параметрами. Тобто наївне `IN` на десять тисяч id впаде або відмовиться планувати. Лікують це **розбиттям пачки** на шматки по кількасот і кількома запитами — або тимчасовою таблицею чи табличним параметром, у який висипають ключі й з'єднуються з ним. DataLoader робить розбиття за тебе, але саму стелю пам'ятати все одно треба.

**Пакет любить унікальні ключі.** У нас сто замовлень на трьох покупців. Якщо не прибрати дублі перед `IN`, у запит поїде сто id замість трьох — база стерпить, але це марна робота й роздутий план. У прикладі `find_customers` сам згортає список у множину; у справжньому коді це роблять або на боці збирача ключів, або тим самим кешем тотожності, що вже пам'ятає завантажене.

**Тотожність живе лише в межах запиту.** І мапа тотожності, і кеш DataLoader — короткочасні: їх заводять на **один** вебзапит і викидають наприкінці. Тягнути їх між запитами спокусливо (ще менше поїздок!), але тоді два користувачі бачитимуть чужі несвіжі дані, а пам'ять поросте застряглими об'єктами. Дедуплікація в межах однієї дії — правильно; вічний кеш через мапу тотожності — це вже інша, набагато складніша розмова про інвалідацію.

Підсумок стенда простий: ліниве завантаження — це **регулятор за замовчуванням**, а не чеснота. За замовчуванням лінивий, щоб не тягнути павутину даремно; жадібний точково там, де стежка відома. А лічильник запитів — той дешевий прилад, що не дає лінощам тихо перерости в рій.
