# ⚙️ Робочий шлюз рядка від руки

Скелет шлюзу рядка виглядає так, ніби писати вже нема чого: поля рядка, три дієслова `insert`/`update`/`delete`, поряд окремий шукач, що будує шлюзи з відповіді бази. Та між цим кресленням і кодом, який справді запускається, лежить одна річ, яку схема мовчки пропускає. Коли натиснуто «зберегти», шлюз мусить сам вирішити, що це — **народження** нового рядка чи **правка** наявного: новому потрібен `INSERT` і виданий базою ключ, наявному — `UPDATE ... WHERE id = …`. Той самий метод, та сама кнопка, а SQL два різні. Отже, шлюзові бракує одного факту: **чи цей рядок уже в базі**. Факт цей — булеве значення, і майже вся різниця між робочим шлюзом і діаграмою в тому, щоб тримати його чесним.

Зберемо стенд повністю на SQLite: він лежить у стандартній поставці і Python (`sqlite3`), і Node (`node:sqlite`), тож без жодної зовнішньої залежності видно сам патерн, а не прошарок драйвера. Таблиця — та сама, що й скрізь:

```sql
CREATE TABLE orders (
  id          INTEGER PRIMARY KEY,
  customer_id TEXT NOT NULL,
  total       REAL NOT NULL DEFAULT 0,
  status      TEXT NOT NULL DEFAULT 'new'
);
```

## Прапорець «я вже в базі» — і як save() ним керується

Заведемо в шлюзі поле `persisted` — правда чи брехня на питання «чи існує мій рядок». Уся механіка — в тому, звідки це поле бере кожне своє значення:

- **новий шлюз** (конструктор під нову річ) — `persisted = false`, `id = null`: рядка ще немає;
- **`insert()`** — база вставила рядок і видала ключ; `id` заповнено, `persisted = true`;
- **шукач** — рядок **прийшов із бази**, тобто вже там; збудований із нього шлюз одразу `persisted = true`;
- **`delete()`** — рядок зник; `persisted = false`, `id = null` — шлюз знову «порожній».

Після цього `save()` не питає викликача нічого: `persisted` сам каже йому, `INSERT` це чи `UPDATE`. Задача суто бекендова — розмова з базою, — тож пишемо мовами, що там реально живуть; TypeScript і Python лягають на неї однаково природно.

:::tabs
```ts
import { DatabaseSync } from "node:sqlite";

const db = new DatabaseSync(":memory:");
type Row = { id: number; customer_id: string; total: number; status: string };

// ── ШЛЮЗ: рівно один рядок — його поля, три дієслова й прапорець наявності. ──
class OrderGateway {
  id: number | null;
  persisted: boolean;                        // ← чи мій рядок уже в базі

  constructor(
    public customerId: string,
    public total: number,
    public status = "new",
    init: { id?: number; persisted?: boolean } = {},
  ) {
    this.id = init.id ?? null;
    this.persisted = init.persisted ?? false;
  }

  // єдина точка запису: сам обирає INSERT чи UPDATE за прапорцем
  save(): void {
    if (this.persisted) this.update();
    else this.insert();
  }

  private insert(): void {
    const info = db
      .prepare("INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)")
      .run(this.customerId, this.total, this.status);
    this.id = Number(info.lastInsertRowid);  // база видала ключ
    this.persisted = true;                   // відтепер я в базі
  }                                          // node:sqlite фіксує кожен .run() сам

  private update(): void {
    db.prepare("UPDATE orders SET customer_id = ?, total = ?, status = ? WHERE id = ?")
      .run(this.customerId, this.total, this.status, this.id);
  }

  delete(): void {
    if (!this.persisted) return;
    db.prepare("DELETE FROM orders WHERE id = ?").run(this.id);
    this.id = null;                          // ключа немає
    this.persisted = false;                  // рядка немає
  }
}

// ── ШУКАЧ: окремий клас; виконує SELECT і будує з кожного рядка свій шлюз. ──
class OrderFinder {
  // рядок ПРИЙШОВ із бази → шлюз одразу позначено як наявний
  private static load(r: Row): OrderGateway {
    return new OrderGateway(r.customer_id, r.total, r.status,
                            { id: r.id, persisted: true });
  }

  static find(id: number): OrderGateway | null {
    const r = db.prepare("SELECT * FROM orders WHERE id = ?").get(id) as Row | undefined;
    return r ? OrderFinder.load(r) : null;
  }

  static findByStatus(status: string): OrderGateway[] {
    const rows = db.prepare("SELECT * FROM orders WHERE status = ?").all(status) as Row[];
    return rows.map((r) => OrderFinder.load(r));
  }
}
```
```py
import sqlite3

db = sqlite3.connect(":memory:")
db.row_factory = sqlite3.Row


# ── ШЛЮЗ: рівно один рядок — його поля, три дієслова й прапорець наявності. ──
class OrderGateway:
    def __init__(self, customer_id, total, status="new", *, id=None, persisted=False):
        self.id = id
        self.customer_id = customer_id
        self.total = total
        self.status = status
        self.persisted = persisted          # ← чи мій рядок уже в базі

    # єдина точка запису: сам обирає INSERT чи UPDATE за прапорцем
    def save(self):
        self._update() if self.persisted else self._insert()

    def _insert(self):
        cur = db.execute(
            "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
            (self.customer_id, self.total, self.status),
        )
        self.id = cur.lastrowid             # база видала ключ
        self.persisted = True               # відтепер я в базі
        db.commit()

    def _update(self):
        db.execute(
            "UPDATE orders SET customer_id = ?, total = ?, status = ? WHERE id = ?",
            (self.customer_id, self.total, self.status, self.id),
        )
        db.commit()

    def delete(self):
        if not self.persisted:
            return
        db.execute("DELETE FROM orders WHERE id = ?", (self.id,))
        db.commit()
        self.id = None                      # ключа немає
        self.persisted = False              # рядка немає


# ── ШУКАЧ: окремий клас; виконує SELECT і будує з кожного рядка свій шлюз. ──
class OrderFinder:
    @staticmethod
    def _load(r):
        # рядок ПРИЙШОВ із бази → шлюз одразу позначено як наявний
        return OrderGateway(r["customer_id"], r["total"], r["status"],
                            id=r["id"], persisted=True)

    @staticmethod
    def find(id):
        r = db.execute("SELECT * FROM orders WHERE id = ?", (id,)).fetchone()
        return OrderFinder._load(r) if r else None

    @staticmethod
    def find_by_status(status):
        rows = db.execute("SELECT * FROM orders WHERE status = ?", (status,)).fetchall()
        return [OrderFinder._load(r) for r in rows]
```
:::

Дві речі в цьому коді варто прочитати повільно. Перша — кожне значення передане **окремим параметром** (`?`), а не вклеєне в текст запиту; вся розмова з базою замкнена в цих двох класах, і зробити її стійкою до підставленого лихого вводу треба саме тут, в одному місці, а не в кожному контролері. Друга — конструктор шлюзу й фабрика шукача (`load`) розходяться навмисне: конструктор народжує **новий** рядок (`persisted = false`), а `load` одягає в об'єкт рядок, що **вже є** (`persisted = true`). Один і той самий клас, а два входи — і кожен ставить прапорець за своєю правдою.

## Повний оберт: новий → INSERT → UPDATE → find → delete

Найкраще прапорець видно в дії. Проженемо один рядок крізь усе його життя й подивимося, який SQL шлюз при цьому вимовляє:

```py
gw = OrderGateway("c-19", 1200.0)   # persisted=False, id=None — рядка ще немає
gw.save()                            # persisted False → INSERT
print(gw.id, gw.persisted)           # 1 True

gw.status = "paid"
gw.save()                            # persisted True → UPDATE (а не другий INSERT!)

again = OrderFinder.find(1)          # persisted True одразу — рядок із бази
again.total = 999.0
again.save()                         # UPDATE

gw.delete()                          # DELETE; далі gw.id=None, gw.persisted=False
```

Ось що з цього поїде в базу — не переказ, а рівно ті запити, що їх складає код вище:

```
OrderGateway("c-19", 1200.0)      persisted=False  id=None
  save() → INSERT INTO orders (customer_id, total, status)
           VALUES ('c-19', 1200.0, 'new')
           база видала id=1;  persisted=True

status = "paid";  save()
  save() → UPDATE orders SET customer_id='c-19', total=1200.0, status='paid'
           WHERE id=1

OrderFinder.find(1)               persisted=True   id=1   (рядок ІЗ бази)
total = 999.0;  save()
  save() → UPDATE orders SET customer_id='c-19', total=999.0, status='paid'
           WHERE id=1

  delete() → DELETE FROM orders WHERE id=1
           persisted=False;  id=None
```

Придивись до двох рядків цього виводу — і побачиш весь патерн у роботі. Перший `save()` дав `INSERT`, а другий, третій — `UPDATE`, хоча метод той самий: між ними лише перемкнувся `persisted`. І шлюз, що прийшов від шукача (`again`), пішов одразу в `UPDATE`, ні на мить не сплутавши себе з новим рядком, — бо народився вже наявним. Прапорець — це не оздоба над кодом, а той стрілочник, що переводить `save()` на правильну колію.

![Дві великі рамки-стани. Ліворуч синя рамка «новий · transient»: id = null, persisted = false, підпис рядка в базі ще немає. Праворуч зелена рамка «у базі · persisted»: id = 1, persisted = true, підпис рядок існує, ключ відомий. Від лівої до правої стрілка save() → INSERT. Над правою рамкою петля save() → UPDATE. Від правої назад до лівої стрілка delete() → DELETE. Знизу до правої рамки входить стрілка від рамки OrderFinder._load(row) з підписом одразу persisted = true](/book/programming/design-patterns/row-data-gateway/img/rdg-lifecycle.svg)

*Один прапорець `persisted` вирішує, чим стане `save()`: для нового рядка — `INSERT` і виданий базою ключ, для наявного — `UPDATE`. Шукач ставить прапорець за тебе, бо єдиний бачив рядок у базі; `delete()` вертає шлюз у стан «мене немає».*

## Межа на очах: один додаток відділяє шлюз від Active Record

Тепер — найцікавіше, заради чого стенд і зібрано. Шлюз рядка визначає не те, що в ньому є, а те, чого в ньому свідомо немає: **жодного предметного правила**. Це легко перевірити руками — вставити правило й побачити, як об'єкт міняє породу.

Візьмімо той самий `OrderGateway` і додаймо йому рішення «чи можна скасувати замовлення» разом із дією `cancel`:

:::tabs
```ts
class OrderGateway {
  // ⚠️ додали предметне правило В шлюз — і це вже не шлюз
  canCancel(): boolean {
    return this.status === "new" || this.status === "paid";
  }

  cancel(): void {
    if (!this.canCancel())
      throw new Error(`замовлення в статусі ${this.status} не скасувати`);
    this.status = "cancelled";
    this.save();
  }
}
```
```py
class OrderGateway:
    # ⚠️ додали предметне правило В шлюз — і це вже не шлюз
    def can_cancel(self):
        return self.status in ("new", "paid")

    def cancel(self):
        if not self.can_cancel():
            raise ValueError(f"замовлення в статусі {self.status!r} не скасувати")
        self.status = "cancelled"
        self.save()
```
:::

Поля ті самі, три дієслова ті самі — а об'єкт уже інший. Тепер він **знає предметне правило** (коли замовлення скасовне) і сам його застосовує. Об'єкт, що поєднав у собі рядок бази й правила над ним, має власне ім'я — [Active Record](book:programming/active-record). Ми не перепроєктовували клас, не міняли доступ до бази — лише вклали одне рішення, і межа перейдена.

Тепер зробімо зворотний рух: заберімо правило зі шлюзу назад і покладімо його **окремим сценарієм** над чистим шлюзом:

:::tabs
```ts
// правило живе ТУТ, у сценарії; шлюз лишається порожнім перекладачем рядка
function cancelOrder(orderId: number): void {
  const gw = OrderFinder.find(orderId);
  if (gw === null) throw new Error(`замовлення ${orderId} немає`);
  if (gw.status !== "new" && gw.status !== "paid")
    throw new Error(`замовлення в статусі ${gw.status} не скасувати`);
  gw.status = "cancelled";
  gw.save();                        // шлюз лише переносить рядок назад у базу
}
```
```py
# правило живе ТУТ, у сценарії; шлюз лишається порожнім перекладачем рядка
def cancel_order(order_id):
    gw = OrderFinder.find(order_id)
    if gw is None:
        raise LookupError(f"замовлення {order_id} немає")
    if gw.status not in ("new", "paid"):
        raise ValueError(f"замовлення в статусі {gw.status!r} не скасувати")
    gw.status = "cancelled"
    gw.save()                       # шлюз лише переносить рядок назад у базу
```
:::

Правило те саме до літери, і SQL наприкінці той самий — змінилася лише **адреса**, за якою правило живе. У класі шлюзу воно робить Active Record; у сценарії поверх шлюзу — лишає шлюз шлюзом. Таку організацію логіки, де кожна дія — короткий сценарій, а рядки він чіпає через шлюз, звуть [сценарієм транзакції](book:programming/transaction-script): сценарій вирішує **що** зробити, шлюз знає **як** дістати й покласти рядок. Оце пересування правила туди-сюди і є вся різниця між двома патернами — не структура, не назви класів, а місце, куди сідає одне `if`.

> 🔧 **Навіщо це.** Практична проба, чи перед тобою й досі шлюз: пробіжи очима по його методах і спитай, чи є серед них **бодай один, що ухвалює предметне рішення**. З'явився `canCancel`, `isOverdue`, `applyPromo` — це вже Active Record, можливо, ненавмисний. Тримати межу варто тоді, коли ти **хочеш**, щоб доступ до бази й правила лежали окремо: правила тоді перевіряються без бази, а весь SQL сидить у тонкому передбачуваному шарі, куди легко зазирнути, коли щось гальмує. Немає такої потреби — не бійся Active Record, він дешевший на один клас; є — стережи порожнечу шлюзу свідомо, бо заповнюється вона тихо й сама.

## Складність і пастки

Стенд навмисно малий, і саме тому на ньому видно пастки, які у великому коді ховаються за шарами. Жодна з них — не хиба цієї реалізації; кожна є в будь-якому шлюзі рядка, хоч руками писаному, хоч під фреймворком.

### Прапорець мусить бути чесним — інакше save() вставить дубль

Уся конструкція тримається на тому, що `persisted` каже правду. Порушиш це — і `save()` зробить не те дієслово. Найлегше порушити мовчки: збудувати шлюз для наявного рядка **руками**, повз шукач:

```py
# рядок id=1 УЖЕ в базі, але ми зробили шлюз конструктором — persisted=False
ghost = OrderGateway("c-19", 999.0, "paid", id=1)
ghost.save()        # persisted False → INSERT … → дубль або конфлікт первинного ключа
```

Конструктор народжує **нові** рядки, тож його прапорець — `false`, і `save()` слухняно піде в `INSERT`, хоча рядок уже є. Тому наявний рядок беруть **тільки через шукач**: він єдиний має право поставити `persisted = true`, бо єдиний бачив цей рядок у базі. Прапорець — несуча деталь, а не оздоба.

Тут-таки видно, чому явний прапорець кращий за спокусу вгадувати стан за ключем — `id is None ? INSERT : UPDATE`. Для лічильника-автоінкремента таке вгадування працює: новому рядку ключ дає база, тож до `insert()` він і справді `null`. Але щойно ключі роздаєш ти сам — скажімо, UUID, згенерований **до** вставки, — новий рядок приходить із уже заповненим `id`, і перевірка `id is None` упевнено скаже «наявний» та пошле код в `UPDATE`, якому нема чого оновлювати. Явний `persisted` нічого не вгадує: він каже те, що знає напевно, і від способу видачі ключів не залежить.

### Кожен save() — окрема транзакція

Придивись до робочого шлюзу: кожен запис закінчується фіксацією (Python — явним `db.commit()`, node:sqlite — автоматично по кожному `.run()`). Отже, кожен `save()` — самостійна, вже зафіксована транзакція. Для одного рядка це саме те, що треба. Та замовлення рідко живе саме — збережи його разом із позиціями:

```py
order.save()                        # commit №1 — замовлення вже в базі
for ln in lines:
    ln.save()                       # commit №2, №3, … кожен окремо
```

Якщо на третій позиції впаде помилка, замовлення й перші дві позиції **вже зафіксовані**, а решти немає — у базі осів піврядок замовлення, якого ніхто не просив. Причина проста: шлюз вирішив межу транзакції за тебе, поклавши `commit()` собі всередину.

Ліки — забрати фіксацію зі шлюзу й віддати межу тому, хто керує цілою дією:

```py
db.execute("BEGIN")
try:
    order.save()                    # save() тепер БЕЗ внутрішнього commit()
    for ln in lines:
        ln.save()
    db.commit()                     # усі рядки разом — або жодного
except Exception:
    db.rollback()
    raise
```

Тепер або доїхало все, або відкотилося все. Систематична форма цієї ідеї — накопичити всі зміни й записати одним обігом в одній транзакції — зветься [одиницею роботи](book:programming/unit-of-work); а сама межа «усе або нічого» — це [транзакція](book:programming/transactions-acid), яку шлюз рядка не вміє тримати сам і, поки лишається тонким, тримати не повинен.

### Ручне підвантаження зв'язків через шукач — це N+1

Хай у замовлення є позиції в дочірній таблиці `order_lines(id, order_id, sku, qty)`, а на неї — свій шукач (шлюз `OrderLineGateway` — така сама трійка полів-і-дієслів, тільки над `order_lines`):

```py
class OrderLineFinder:
    @staticmethod
    def find_by_order(order_id):
        rows = db.execute("SELECT * FROM order_lines WHERE order_id = ?",
                          (order_id,)).fetchall()
        return [OrderLineGateway._load(r) for r in rows]
```

І тепер найприродніший на вигляд код показує список замовлень із їхніми позиціями:

```py
orders = OrderFinder.find_by_status("paid")            # 1 запит
for o in orders:
    o.lines = OrderLineFinder.find_by_order(o.id)      # +1 запит на КОЖНЕ замовлення
```

Сто замовлень — сто один запит: один по список і сто по позиції, кожен окремою поїздкою в базу. На десятці рядків у розробника непомітно, на тисячі в проді сторінка лягає. Це — [проблема N+1](book:programming/lazy-loading), тільки написана руками: шукач так само зручний, як ліниве звертання до поля, і так само мовчки множить запити. Лікується вона не відмовою від шукача, а одним питанням до бази замість ста:

```py
from collections import defaultdict

class OrderLineFinder:
    @staticmethod
    def find_by_orders(order_ids):
        marks = ",".join("?" * len(order_ids))         # → WHERE order_id IN (?, ?, …)
        rows = db.execute(
            f"SELECT * FROM order_lines WHERE order_id IN ({marks})", order_ids
        ).fetchall()
        return [OrderLineGateway._load(r) for r in rows]

orders = OrderFinder.find_by_status("paid")            # 1 запит
lines = OrderLineFinder.find_by_orders([o.id for o in orders])   # +1 на ВСІХ
by_order = defaultdict(list)
for ln in lines:
    by_order[ln.order_id].append(ln)                   # групуємо в пам'яті
for o in orders:
    o.lines = by_order[o.id]
```

Два запити замість ста одного, скільки б не було замовлень. Єдиний обережний момент — довжина списку в `IN (…)`: бази мають стелю на кількість параметрів (SQLite історично близько 999), тож на великих вибірках його ріжуть пачками. Як саме ці числа ростуть із розміром вибірки — [розкладено окремо](book:programming/active-record/math-n-plus-one.md); нам досить бачити, що межа між «швидко» і «повзе» — це один зайвий запит, схований у циклі.

### Два шукання — два об'єкти на один рядок

І остання, тихіша пастка. `OrderFinder.find(1)`, покликаний двічі, дає **два різні шлюзи** на той самий рядок. Зміниш один, збережеш другий — правку першого затерто, бо він про сусіда й не знав. Реєстр «один рядок у межах роботи = один об'єкт у пам'яті» зветься [картою тотожності](book:programming/identity-map); у голому шлюзі його немає, і поки об'єкти живуть недовго й у межах одного запиту, це терпимо — але знати про пастку варто заздалегідь, бо баг від неї виходить із тих, що не відтворюються на вимогу.

## Що показав стенд

Робочий шлюз рядка — це тонкий чесний перекладач, що знає рівно дві речі й більше нічого. Перша: **чи існує його рядок** — прапорець `persisted`, який ставить шукач і читає `save()`, обираючи між `INSERT` і `UPDATE`. Друга: що **правил він не тримає**. Тримай прапорець чесним, а об'єкт — порожнім від рішень, і він лишиться шлюзом: службовим шаром під [мапером даних](book:programming/data-mapper) чи постачальником рядків для [сценарію транзакції](book:programming/transaction-script). Додай `canCancel` із `cancel` — і він тихо стане [Active Record](book:programming/active-record); це не помилка, а інший патерн, у якому межу між доступом і логікою стерто навмисно.

А пастки — дубль від збрехавшого прапорця, піврядка замовлення від фіксації всередині `save()`, N+1 від зв'язків, підвантажених руками, — не хиби шлюзу. Це питання, на які мусить відповісти **будь-який** об'єкт, що сам ходить у базу; просто на стенді в сотню рядків їх видно цілими, а не по частинах з-під фреймворку.
