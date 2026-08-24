# ⚙️ Підробка, якій можна вірити: репозиторій у пам'яті

## Задача

Правило, яке треба перевірити, звучить так: **клієнт постійний, якщо три його останні оплачені замовлення — кожне понад 500**. Речення коротке, а пасток у ньому щонайменше шість, і кожна вартує окремого тесту:

1. три останні оплачені, всі понад 500 → постійний;
2. оплачених лише два → ще ні;
3. серед трьох є рівно 500 → ні, бо сказано «понад», а не «від»;
4. оплачених чотири, найстаріше — дешеве → **так**, бо дивимось лише три останні;
5. неоплачене замовлення не рахується, хай яке дороге;
6. замовлення іншого клієнта не рахуються.

Четвертий випадок — найцікавіший: саме він відрізняє «три **останні** оплачені» від «всі оплачені». Щоб він щось означав, замовлення мусять прийти впорядкованими за часом. Запам'ятай це — далі воно стане віссю всієї роботи.

Тепер порахуймо, у що обійдеться перевірка цих шести випадків, якщо ганяти їх по живій базі:

```
один випадок на живій базі:
  взяти з'єднання з пулу        ≈ 1 мс
  TRUNCATE orders (чистка)      ≈ 5 мс
  4 × INSERT                    ≈ 2 мс
  SELECT правила                ≈ 1 мс
  ──────────────────────────────────
  разом                         ≈ 9 мс   — і це в найкращому разі:
                                  база на тій самій машині, схема вже накочена

6 випадків × 9 мс ≈ 54 мс      — начебто дрібниця
але правил у застосунку не одне, а, скажімо, 300:
300 × 6 × 9 мс ≈ 16 с          — на кожне збереження файлу вже не поганяєш
```

І шістнадцять секунд — навіть не найгірше. Гірше — те, чого в арифметиці не видно: щоб ці тести взагалі запустилися, потрібен піднятий Postgres і накочена схема; а щоб вони не псували одне одному дані, їх не можна ганяти паралельно на спільних таблицях — доводиться шикувати в чергу. Тест перестає бути тим, що ти запускаєш не думаючи, і стає подією.

Мета — інша: **шість випадків, жодної бази, прогін на кожне натискання «зберегти»**. Розберімо, як така перевірка робиться насправді — і чому найкоротший спосіб її зробити тихо бреше.

## Найкоротша підробка — і де вона бреше

Найочевидніша реалізація контракту `OrderRepository` над пам'яттю — покласти доменні об'єкти в мапу за їхнім ідентифікатором:

:::tabs
```ts
class InMemoryOrderRepository implements OrderRepository {
  private store = new Map<OrderId, Order>();

  async byId(id: OrderId) { return this.store.get(id) ?? null; }
  async save(o: Order)    { this.store.set(o.id, o); }
  async remove(o: Order)  { this.store.delete(o.id); }
}
```
```py
class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._store: dict[OrderId, Order] = {}

    def by_id(self, id):  return self._store.get(id)
    def save(self, o):    self._store[o.id] = o
    def remove(self, o):  self._store.pop(o.id, None)
```
:::

Шість рядків, і воно працює. Точніше — воно працює доти, доки перевіряєш тільки читання. Ось код, на якому підробка починає брехати, — і зверни увагу, що це не вигаданий, а один із найчастіших справжніх багів:

:::tabs
```ts
class PaymentService {
  constructor(
    private readonly orders: OrderRepository,
    private readonly gateway: PaymentGateway,
  ) {}

  async pay(orderId: OrderId): Promise<void> {
    const order = await this.orders.byId(orderId);
    if (!order) throw new Error(`немає замовлення ${orderId}`);
    await this.gateway.charge(order.total);
    order.markPaid();
    // ← і тут забули: await this.orders.save(order);
  }
}
```
```py
class PaymentService:
    def __init__(self, orders: OrderRepository, gateway: PaymentGateway) -> None:
        self._orders, self._gateway = orders, gateway

    def pay(self, order_id: OrderId) -> None:
        order = self._orders.by_id(order_id)
        if order is None:
            raise LookupError(f"немає замовлення {order_id}")
        self._gateway.charge(order.total)
        order.mark_paid()
        # ← і тут забули: self._orders.save(order)
```
:::

Загублений `save` — банальність, яку кожен писав. Тепер напиши на цей код чесний тест: оплатити замовлення, а тоді дістати його з репозиторію й перевірити, що воно оплачене.

Тест **зеленіє**. І він бреше.

Бреше він тому, що `byId` віддав не копію, а **той самий об'єкт, який лежить у мапі**. Виклик `markPaid()` змінив його на місці — і мапа тепер тримає оплачене замовлення. Не тому, що хтось його зберіг, а тому, що зберігати було нічого: об'єкт у мапі й об'єкт у руках сервісу — одна й та сама річ у пам'яті.

Справжній репозиторій так не вміє. Він поклав у таблицю **рядок** — плаский знімок об'єкта на момент `save`. Мутація доменного об'єкта після цього рядка не торкається: `markPaid()` міняє річ у пам'яті процесу, а в базі лежить `status = 'new'`, і лежатиме, доки хтось не виконає `UPDATE`. Наступний `byId` прочитає той рядок і **зліпить із нього новий об'єкт** — зі статусом `new`.

![Три кроки в двох колонках. Крок 1: repo.save(order) зі статусом «new» — у справжнього репозиторію в таблицю пішов рядок id=41 status='new', у наївної підробки в Map лягло посилання на той самий об'єкт. Крок 2: order.markPaid() без повторного save — у базі рядок не змінився, status у рядку лишився 'new'; у підробки об'єкт у Map той самий і він уже paid. Крок 3: repo.byId(41).isPaid() — справжній репозиторій зліпив новий Order із рядка й дав false, підробка віддала той самий об'єкт і дала true. Унизу два підсумки: «false — так буде в продакшні» проти «true — так буде в тесті», між ними червоний знак нерівності](img/proj-fake-aliasing.svg)

*Той самий крок — і дві різні відповіді. Підробка тримає посилання на об'єкт, база тримає його плаский знімок. Тому загублений `save` для підробки невидимий, а в продакшні коштує грошей клієнта.*

Ціна цієї розбіжності — рівно та, з якої почалася задача. Клієнту списали кошти, замовлення лишилося «нове», а тест увесь цей час був зелений. Підробка не просто помилилася — вона **сховала** баг, який мала знайти.

## Ідея: підробка мусить тримати те саме, що тримає база

З двох колонок на малюнку читається й діагноз, і ліки. Уся розбіжність береться з одного місця: **база зберігає рядок, а підробка зберігає посилання**. Виправляти це доклеюванням копій («не забудь склонувати об'єкт на вході й на виході») — марно: обов'язок пам'ятати про клон рано чи пізно забудеться, як забувся `save`.

Ліки надійніші й простіші. Хай підробка зберігає **рядок** — той самий плаский запис, який лягає в таблицю. Тоді копіювання не треба нікому доручати: воно виходить саме собою, бо рядок — це не об'єкт. Щоб зробити з `Order` рядок, треба його прочитати й скласти нову структуру; щоб зробити з рядка `Order` — треба збудувати новий об'єкт. Обидва напрямки фізично не можуть віддати посилання на те, що тобі й так належить.

Більше того — переклад `Order ⇄ рядок` уже написаний. Його виконує [відображувач об'єкт↔рядок](book:programming/data-mapper): окремий шматок коду, що знає, у яку колонку лягає яке поле, і нічого не знає ні про колекції, ні про запити. Справжній `SqlOrderRepository` кличе саме його. Хай підробка кличе **той самий** — і тоді дві реалізації почнуть різнитися рівно в одному: **де лежать рядки**. У Postgres на диску — чи в мапі в пам'яті. Усе інше в них спільне буквально, тим самим кодом.

> 🔧 **Навіщо це.** Різниця між «підробка тримає об'єкти» і «підробка тримає рядки» здається косметичною, а насправді це різниця між двома реалізаціями, які **розходяться по семантиці**, і двома, які розходяться лише **місцем зберігання**. У першому разі кожна відмінність бази від пам'яті — жива тріщина, крізь яку в продакшн проходять баги на кшталт загубленого `save`, і ти не знаєш, скільки тих тріщин. У другому — тріщина одна й відома: диск проти мапи. Усе, що вище рядка (переклад полів, тотожність, видимість змін), в обох реалізаціях однакове, бо це буквально один і той самий код. Підробка перестає бути «схожою» на базу й починає бути базою, у якої відібрали диск.

## Робочий код: домен, рядок, мапер, контракт

Почнімо з доменного об'єкта. Головне в ньому для нашої історії — те, що він **змінюваний**: статус міняється методом, а не переприсвоєнням поля, і зміна має правило.

:::tabs
```ts
type OrderId = string;
type CustomerId = string;
type OrderStatus = "new" | "paid" | "shipped";

class Order {
  private _status: OrderStatus;

  constructor(
    readonly id: OrderId,
    readonly customerId: CustomerId,
    readonly total: number,
    readonly createdAt: Date,
    status: OrderStatus = "new",
  ) {
    this._status = status;
  }

  get status(): OrderStatus { return this._status; }
  isPaid(): boolean { return this._status === "paid"; }

  markPaid(): void {
    if (this._status !== "new") {
      throw new Error(`оплатити можна лише нове замовлення, а це «${this._status}»`);
    }
    this._status = "paid";
  }
}
```
```py
from __future__ import annotations
from datetime import datetime

OrderId = str
CustomerId = str


class Order:
    def __init__(self, id: OrderId, customer_id: CustomerId, total: int,
                 created_at: datetime, status: str = "new") -> None:
        self.id = id
        self.customer_id = customer_id
        self.total = total
        self.created_at = created_at
        self._status = status

    @property
    def status(self) -> str:
        return self._status

    def is_paid(self) -> bool:
        return self._status == "paid"

    def mark_paid(self) -> None:
        if self._status != "new":
            raise ValueError(f"оплатити можна лише нове замовлення, а це «{self._status}»")
        self._status = "paid"
```
:::

Далі — **рядок і мапер**. Рядок навмисно виглядає як колонки таблиці, а не як домен: імена в змійці, час — рядком ISO-8601, статус — просто текстом. Це і є та плоска правда, яку вміє зберігати база.

:::tabs
```ts
type OrderRow = {
  id: string;
  customer_id: string;
  total: number;
  status: string;
  created_at: string;   // ISO-8601 у UTC — як у колонці timestamptz
};

// той самий мапер, яким користується SqlOrderRepository
const toRow = (o: Order): OrderRow => ({
  id: o.id,
  customer_id: o.customerId,
  total: o.total,
  status: o.status,
  created_at: o.createdAt.toISOString(),
});

const toDomain = (r: OrderRow): Order =>
  new Order(r.id, r.customer_id, r.total, new Date(r.created_at), r.status as OrderStatus);
```
```py
from dataclasses import dataclass
from datetime import timezone


@dataclass(frozen=True)
class OrderRow:
    id: str
    customer_id: str
    total: int
    status: str
    created_at: str          # ISO-8601 у UTC — як у колонці timestamptz


# той самий мапер, яким користується SqlOrderRepository
def to_row(o: Order) -> OrderRow:
    return OrderRow(o.id, o.customer_id, o.total, o.status,
                    o.created_at.astimezone(timezone.utc).isoformat())


def to_domain(r: OrderRow) -> Order:
    return Order(r.id, r.customer_id, r.total,
                 datetime.fromisoformat(r.created_at), r.status)
```
:::

Тепер **контракт**. Тут ховається рішення, від якого залежить усе інше: правило про «три останні» вимагає порядку, і порядок мусить бути **записаний у контракті**, а не додуманий реалізацією. Тому в інтерфейсі не безликий `forCustomer`, а доменно названий пошук, чия назва сама каже, що він обіцяє:

:::tabs
```ts
interface OrderRepository {
  byId(id: OrderId): Promise<Order | null>;

  /** Оплачені замовлення клієнта: найновіші перші, не більше за limit.
   *  За однакового часу — старшим вважається більший id. */
  recentPaidOrders(customerId: CustomerId, limit: number): Promise<Order[]>;

  save(order: Order): Promise<void>;
  remove(order: Order): Promise<void>;
}

class LoyaltyService {
  constructor(private readonly orders: OrderRepository) {}

  async isLoyal(customerId: CustomerId): Promise<boolean> {
    const recent = await this.orders.recentPaidOrders(customerId, 3);
    return recent.length === 3 && recent.every(o => o.total > 500);
  }
}
```
```py
from typing import Optional, Protocol


class OrderRepository(Protocol):
    def by_id(self, id: OrderId) -> Optional[Order]: ...

    def recent_paid_orders(self, customer_id: CustomerId, limit: int) -> list[Order]:
        """Оплачені замовлення клієнта: найновіші перші, не більше за limit.
        За однакового часу — старшим вважається більший id."""
        ...

    def save(self, order: Order) -> None: ...
    def remove(self, order: Order) -> None: ...


class LoyaltyService:
    def __init__(self, orders: OrderRepository) -> None:
        self._orders = orders

    def is_loyal(self, customer_id: CustomerId) -> bool:
        recent = self._orders.recent_paid_orders(customer_id, 3)
        return len(recent) == 3 and all(o.total > 500 for o in recent)
```
:::

Два рядки коментаря над `recentPaidOrders` — не ввічливість, а найважливіше речення в усьому файлі. Вони кажуть: порядок — частина обіцянки, і навіть нічия за часом розв'язується визначено. Без цього другого речення дві реалізації розходяться на рівному місці — розберемо, де саме, коли дійде до детермінованості.

## Робочий код: підробка

:::tabs
```ts
class InMemoryOrderRepository implements OrderRepository {
  private readonly rows = new Map<OrderId, OrderRow>();   // РЯДКИ, не Order

  async byId(id: OrderId): Promise<Order | null> {
    const row = this.rows.get(id);
    return row ? toDomain(row) : null;                     // щоразу новий об'єкт
  }

  async recentPaidOrders(customerId: CustomerId, limit: number): Promise<Order[]> {
    const cmp = (x: string, y: string) => (x < y ? -1 : x > y ? 1 : 0);
    return [...this.rows.values()]
      .filter(r => r.customer_id === customerId && r.status === "paid")   // WHERE
      .sort((a, b) => cmp(b.created_at, a.created_at) || cmp(b.id, a.id)) // ORDER BY … DESC
      .slice(0, limit)                                                    // LIMIT
      .map(toDomain);
  }

  async save(order: Order): Promise<void> {
    this.rows.set(order.id, toRow(order));                 // знімок, не посилання
  }

  async remove(order: Order): Promise<void> {
    this.rows.delete(order.id);
  }
}
```
```py
class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._rows: dict[OrderId, OrderRow] = {}           # РЯДКИ, не Order

    def by_id(self, id: OrderId) -> Optional[Order]:
        row = self._rows.get(id)
        return to_domain(row) if row is not None else None  # щоразу новий об'єкт

    def recent_paid_orders(self, customer_id: CustomerId, limit: int) -> list[Order]:
        rows = [r for r in self._rows.values()                        # WHERE
                if r.customer_id == customer_id and r.status == "paid"]
        rows.sort(key=lambda r: (datetime.fromisoformat(r.created_at), r.id),
                  reverse=True)                                       # ORDER BY … DESC
        return [to_domain(r) for r in rows[:limit]]                   # LIMIT

    def save(self, order: Order) -> None:
        self._rows[order.id] = to_row(order)               # знімок, не посилання

    def remove(self, order: Order) -> None:
        self._rows.pop(order.id, None)
```
:::

Двадцять рядків — і кожен має свого двійника в SQL, який виконує `SqlOrderRepository`: `filter` — це `WHERE`, `sort` — це `ORDER BY created_at DESC, id DESC`, `slice`/зріз — це `LIMIT`. Підробка не «схожа» на запит, вона **розписує той самий запит руками**.

У TypeScript-версії порівняння `created_at` іде по самому рядку, а не по розібраній даті — і це не лінощі: `toISOString()` завжди дає UTC однакової ширини (`2026-03-01T10:00:00.000Z`), а такий формат впорядковується за абеткою точно так само, як за часом. У Python `isoformat()` ширину не гарантує (мікросекунди то є, то нема), тому там ключ сортування розбирає дату явно. Дрібниця — але з тих, на яких дві реалізації тихо розходяться.

Найважливіше в цьому класі — те, чого в ньому **нема**. Нема годинника: жоден метод не питає, котра зараз година. Нема генератора ключів: `save` бере той `id`, що вже є в об'єкті. Нема глобального стану: усе живе в полі екземпляра. Кожна з цих відсутностей — окремий канал недетермінованості, який ми зараз перекриємо.

## Тест, що наповнює підробку

Спершу — дані. Замовлення для тесту будуються **явно**: свій ідентифікатор, свій час, і жодного `new Date()` без аргументів.

:::tabs
```ts
const T0 = new Date("2026-03-01T10:00:00.000Z");
const day = (n: number) => new Date(T0.getTime() + n * 86_400_000);

function paidOrder(id: string, customerId: string, total: number, d: number): Order {
  const o = new Order(id, customerId, total, day(d));
  o.markPaid();
  return o;
}
```
```py
from datetime import timedelta

T0 = datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc)


def day(n: int) -> datetime:
    return T0 + timedelta(days=n)


def paid_order(id: str, customer_id: str, total: int, d: int) -> Order:
    o = Order(id, customer_id, total, day(d))
    o.mark_paid()
    return o
```
:::

А тепер — шість випадків із задачі, слово в слово:

:::tabs
```ts
describe("LoyaltyService.isLoyal", () => {
  let orders: InMemoryOrderRepository;
  let loyalty: LoyaltyService;

  beforeEach(() => {
    orders = new InMemoryOrderRepository();   // ← свіжий на КОЖЕН тест
    loyalty = new LoyaltyService(orders);
  });

  it("три останні оплачені понад 500 — постійний", async () => {
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 700, 2));
    await orders.save(paidOrder("o-3", "c-19", 800, 3));
    expect(await loyalty.isLoyal("c-19")).toBe(true);
  });

  it("оплачених лише два — ще не постійний", async () => {
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 700, 2));
    expect(await loyalty.isLoyal("c-19")).toBe(false);
  });

  it("рівно 500 — це не «понад 500»", async () => {
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 500, 2));   // ← межа
    await orders.save(paidOrder("o-3", "c-19", 700, 3));
    expect(await loyalty.isLoyal("c-19")).toBe(false);
  });

  it("старе дешеве не тягне вниз — дивимось лише три останні", async () => {
    await orders.save(paidOrder("o-0", "c-19", 10, 0));    // ← найстаріше й дешеве
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 700, 2));
    await orders.save(paidOrder("o-3", "c-19", 800, 3));
    expect(await loyalty.isLoyal("c-19")).toBe(true);
  });

  it("неоплачене не рахується, хай яке дороге", async () => {
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 700, 2));
    await orders.save(new Order("o-3", "c-19", 9000, day(3)));   // ← лишилось «new»
    expect(await loyalty.isLoyal("c-19")).toBe(false);
  });

  it("чужі замовлення не рахуються", async () => {
    await orders.save(paidOrder("o-1", "c-19", 600, 1));
    await orders.save(paidOrder("o-2", "c-19", 700, 2));
    await orders.save(paidOrder("x-1", "c-77", 800, 3));         // ← інший клієнт
    expect(await loyalty.isLoyal("c-19")).toBe(false);
  });
});
```
```py
import pytest


@pytest.fixture
def orders() -> InMemoryOrderRepository:
    return InMemoryOrderRepository()          # ← свіжий на КОЖЕН тест


@pytest.fixture
def loyalty(orders) -> LoyaltyService:
    return LoyaltyService(orders)


def test_three_recent_paid_over_500(orders, loyalty):
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 700, 2))
    orders.save(paid_order("o-3", "c-19", 800, 3))
    assert loyalty.is_loyal("c-19") is True


def test_only_two_paid(orders, loyalty):
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 700, 2))
    assert loyalty.is_loyal("c-19") is False


def test_exactly_500_is_not_over_500(orders, loyalty):
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 500, 2))    # ← межа
    orders.save(paid_order("o-3", "c-19", 700, 3))
    assert loyalty.is_loyal("c-19") is False


def test_old_cheap_order_is_out_of_the_window(orders, loyalty):
    orders.save(paid_order("o-0", "c-19", 10, 0))     # ← найстаріше й дешеве
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 700, 2))
    orders.save(paid_order("o-3", "c-19", 800, 3))
    assert loyalty.is_loyal("c-19") is True


def test_unpaid_does_not_count(orders, loyalty):
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 700, 2))
    orders.save(Order("o-3", "c-19", 9000, day(3)))   # ← лишилось «new»
    assert loyalty.is_loyal("c-19") is False


def test_other_customers_orders_do_not_count(orders, loyalty):
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 700, 2))
    orders.save(paid_order("x-1", "c-77", 800, 3))    # ← інший клієнт
    assert loyalty.is_loyal("c-19") is False
```
:::

Прочитай четвертий тест ще раз. Він єдиний, у якому порядок несе вагу: якщо `recentPaidOrders` віддасть **будь-які** три з чотирьох замовлень, а не три найновіші, у вибірку може потрапити десятка — і тест почервоніє. Тобто цей тест перевіряє не лише правило постійності, а й **обіцянку контракту про порядок**. Саме такий тест на живій базі без `ORDER BY` перетворюється на монетку.

Що ж до підстановки: `new LoyaltyService(orders)` — це та сама [ін'єкція залежності](book:programming/dependency-injection), що й у продакшні, тільки в конструктор летить інший об'єкт. Сервіс не має жодного перемикача «я в тесті»; він і не здогадується, що сьогодні за контрактом стоїть мапа. Якби здогадувався — тест перевіряв би вже не той код, що працює в продакшні.

## Звідки береться детермінованість

«Тест детермінований» означає: **та сама відповідь на кожному прогоні** — байдуже, які тести бігли перед ним, у якому порядку їх запустив прогонник, скільки їх бігло паралельно, котра година й хто ще сидить на цій машині. Слово легко сказати, тож розберімо його на канали: недетермінованість не приходить «взагалі», вона протікає **конкретними шляхами**, і кожен треба перекрити окремо.

![Таблиця з чотирьох рядків і трьох колонок: канал недетермінованості, тест на живій базі, тест на свіжій підробці. Рядок «Залишок від попереднього тесту, спільна база, порядок запуску»: на базі тече, чужі рядки лишаються; на підробці закрито — новий екземпляр на кожен тест. Рядок «Порядок рядків без ORDER BY»: на базі тече, порядок не обіцяний; на підробці оманливо тихо — dict тримає порядок вставляння, тест не побачить баг. Рядок «Годинник: NOW(), Date.now()»: на базі тече, час іде; на підробці тече теж — треба вколоти годинник ззовні. Рядок «Ключі: autoincrement, UUID»: на базі тече, ключ щоразу інший; на підробці тече теж — треба вколоти генератор ключів. Унизу підсумок: свіжий екземпляр знімає спільний стан і тільки його; годинник і ключі детермінованими не стають, їх треба подати ззовні](img/proj-determinism-channels.svg)

*Підробка не роздає детермінованість автоматично. Свіжий екземпляр перекриває спільний стан; порядок вона перекриває оманливо; годинник і ключі не перекриває взагалі.*

**Канал перший — залишок від попередніх тестів.** Це той, заради якого підробку й заводять. База одна на весь прогін: рядки, що їх лишив сусідній тест, нікуди не діваються, і тест починає залежати від того, хто біг перед ним. Звідси класика — «поодинці все зелене, разом падає». Ліки в підробці не в тому, що вона в пам'яті, а в тому, що вона **дешева**: `new InMemoryOrderRepository()` у `beforeEach` коштує наносекунди, тому кожен тест дістає власне порожнє сховище й фізично не має чужих рядків. Не мапа робить тест детермінованим, а **свіжість**: якби TRUNCATE коштував наносекунди, база була б не гіршою.

**Канал другий — порядок.** Ось де підробка небезпечніша за базу. SQL не обіцяє порядку без `ORDER BY` — документація PostgreSQL каже про це прямо: без сортування рядки повертаються в невизначеному порядку, який залежить від плану й розкладки на диску, і покладатися на нього не можна (усталений факт). А підробка? `Map` у JavaScript обходиться **в порядку вставляння** — це гарантія специфікації ECMAScript. Словник у Python — так само: у 3.6 це був побічний ефект реалізації CPython, а з 3.7 збереження порядку вставляння записане в саму мову (усталений факт).

І ось наслідок, який варто побачити нарізно: **підробка впорядкована сильніше, ніж база**. Забудь `ORDER BY` у `SqlOrderRepository` — і підробка все одно чемно віддасть замовлення в порядку вставляння, тест позеленіє, а в продакшні той самий запит поверне що завгодно. Тиша тут гірша за падіння: тест не просто не знайшов баг, він **видав його за норму**.

Тому порядок і винесено в контракт — і в назву методу, і в коментар над ним. Обидві реалізації мусять сортувати явно: `.sort(...)` у підробці, `ORDER BY created_at DESC, id DESC` у SQL. Другий ключ, `id`, — не прикраса. За однакового `created_at` (а це трапляється легко: імпорт, пакетне створення, груба точність колонки) SQL віддасть нічию в довільному порядку, тоді як `Array.prototype.sort` і `sorted` у Python **стабільні** й розв'яжуть її порядком вставляння. Дві реалізації розійдуться на рівному місці — і саме на тому вході, який ти в тест не додумався покласти. Нічия, розв'язана в контракті, знімає питання: обидві сторони рахують однаково.

**Канал третій — годинник.** Тут підробка не допомагає **ніяк**, і це треба сказати вголос. Якби `Order` брав час у конструкторі з `new Date()`, тест «три останні» залежав би від того, коли його запустили; правило з вікном «за останні 30 днів» червоніло б рівно раз на місяць. Мапа від цього не рятує — час іде однаково і в пам'яті, і в базі. Рятує те, що час **подають ззовні**: у нашому коді всі дати ростуть із `T0`, а `T0` — константа у файлі тесту. У продакшні на її місці стоїть справжній годинник, який теж подають ззовні — таким самим конструктором, як і репозиторій.

**Канал четвертий — ключі.** Так само. Якби `id` роздавала база через `autoincrement`, кожен прогін давав би інші числа, і тест не міг би написати `byId("o-1")`. Якби їх роздавав `randomUUID()` — те саме, тільки гірше. Тому в нашому тесті ключі називає сам тест: `"o-1"`, `"o-2"`, `"x-1"`. Ключ став **частиною умови задачі**, а не побічним ефектом сховища — а заразом і читабельним: у `paidOrder("x-1", "c-77", …)` видно, що це чуже замовлення, без жодного коментаря.

Ось звідки береться детермінованість насправді: не з мапи, а з **чотирьох перекритих каналів**. Мапа сама по собі закриває один із них (та й то тому, що дешева), другий закриває оманливо, а третій і четвертий не закриває зовсім — їх закриває дисципліна подавати годинник і ключі ззовні. Підробка — не заклинання, а один із чотирьох ходів.

## Контракт-набір: підробка вартує стільки, скільки її перевірка

Лишилося головне питання, і ставити його треба чесно. У нас тепер **дві** реалізації одного контракту, і всі швидкі тести спираються на ту, яка в продакшні не працює жодної секунди. Звідки віра, що вона не бреше?

Із самої підробки — нізвідки. Але задачу можна перевернути. Ми маємо контракт; обидві реалізації обіцяють його виконувати; отже, перевіряти треба **не реалізацію, а контракт** — одним набором тестів, який ганяють проти обох.

![Угорі зелений блок «Контракт-набір проти OrderRepository» з чотирма перевірками: save(o) → byId(o.id) дає рівний o; мутація після save НЕ видима без save; recentPaidOrders — свіжі перші, чужих нема; remove(o) → byId(o.id) дає null. Від нього дві стрілки вниз до двох реалізацій: ліворуч InMemoryOrderRepository — на кожен коміт, близько 8 мс, без бази й диску, зелений означає що підробка не бреше; праворуч SqlOrderRepository — у CI, піднімає базу, секунди замість мілісекунд, червоний означає що контракт змінився. Унизу підсумок: обидві колонки зелені — підробка й база відповідають однаково; аж тоді сотні швидких тестів над підробкою можна читати як правду про продакшн](img/proj-contract-test.svg)

*Один набір тестів, дві реалізації. Швидкі доменні тести над підробкою чогось варті рівно доти, доки контракт-набір зелений на обох.*

Технічно це просто: набір параметризують фабрикою репозиторію.

:::tabs
```ts
function orderRepositoryContract(
  name: string,
  make: () => Promise<{ repo: OrderRepository; dispose: () => Promise<void> }>,
) {
  describe(`OrderRepository · контракт · ${name}`, () => {
    let repo: OrderRepository;
    let dispose: () => Promise<void>;

    beforeEach(async () => {
      const made = await make();
      repo = made.repo;
      dispose = made.dispose;
    });
    afterEach(() => dispose());

    it("збережене дістається рівним", async () => {
      const o = paidOrder("o-1", "c-19", 600, 1);
      await repo.save(o);
      const got = await repo.byId("o-1");
      expect(got).not.toBeNull();
      expect(got!.total).toBe(600);
      expect(got!.isPaid()).toBe(true);
      expect(got!.createdAt.toISOString()).toBe(o.createdAt.toISOString());
    });

    it("мутація ПІСЛЯ save не видима без повторного save", async () => {
      const o = new Order("o-1", "c-19", 600, day(1));   // «new»
      await repo.save(o);
      o.markPaid();                                      // ← без save
      expect((await repo.byId("o-1"))!.isPaid()).toBe(false);
    });

    it("recentPaidOrders: найновіші перші, не більше за limit", async () => {
      await repo.save(paidOrder("o-1", "c-19", 100, 1));
      await repo.save(paidOrder("o-3", "c-19", 300, 3));
      await repo.save(paidOrder("o-2", "c-19", 200, 2));   // навмисно не по черзі
      const got = await repo.recentPaidOrders("c-19", 2);
      expect(got.map(o => o.id)).toEqual(["o-3", "o-2"]);
    });

    it("recentPaidOrders: нічию за часом розв'язує більший id", async () => {
      await repo.save(paidOrder("o-1", "c-19", 100, 5));
      await repo.save(paidOrder("o-9", "c-19", 200, 5));   // той самий час
      const got = await repo.recentPaidOrders("c-19", 1);
      expect(got.map(o => o.id)).toEqual(["o-9"]);
    });

    it("recentPaidOrders: чужих і неоплачених нема", async () => {
      await repo.save(paidOrder("x-1", "c-77", 100, 1));
      await repo.save(new Order("o-2", "c-19", 200, day(2)));
      expect(await repo.recentPaidOrders("c-19", 10)).toEqual([]);
    });

    it("після remove byId дає null", async () => {
      const o = paidOrder("o-1", "c-19", 600, 1);
      await repo.save(o);
      await repo.remove(o);
      expect(await repo.byId("o-1")).toBeNull();
    });
  });
}

// швидка колонка — на кожен коміт
orderRepositoryContract("InMemory", async () => ({
  repo: new InMemoryOrderRepository(),
  dispose: async () => {},
}));

// повільна колонка — той САМИЙ набір, але вже проти живої бази; у CI
orderRepositoryContract("Postgres", async () => {
  const db = await openTestDb();
  await db.exec("TRUNCATE orders");
  return { repo: new SqlOrderRepository(db, mapper), dispose: () => db.close() };
});
```
```py
import pytest


@pytest.fixture(params=["in-memory", "postgres"])
def repo(request):
    if request.param == "in-memory":
        yield InMemoryOrderRepository()
    else:
        db = open_test_db()
        db.execute("TRUNCATE orders")
        yield SqlOrderRepository(db, mapper)
        db.close()


def test_saved_comes_back_equal(repo):
    o = paid_order("o-1", "c-19", 600, 1)
    repo.save(o)
    got = repo.by_id("o-1")
    assert got is not None
    assert got.total == 600
    assert got.is_paid() is True
    assert got.created_at == o.created_at


def test_mutation_after_save_is_invisible(repo):
    o = Order("o-1", "c-19", 600, day(1))          # «new»
    repo.save(o)
    o.mark_paid()                                  # ← без save
    assert repo.by_id("o-1").is_paid() is False


def test_recent_paid_orders_newest_first(repo):
    repo.save(paid_order("o-1", "c-19", 100, 1))
    repo.save(paid_order("o-3", "c-19", 300, 3))
    repo.save(paid_order("o-2", "c-19", 200, 2))   # навмисно не по черзі
    assert [o.id for o in repo.recent_paid_orders("c-19", 2)] == ["o-3", "o-2"]


def test_recent_paid_orders_breaks_tie_by_id(repo):
    repo.save(paid_order("o-1", "c-19", 100, 5))
    repo.save(paid_order("o-9", "c-19", 200, 5))   # той самий час
    assert [o.id for o in repo.recent_paid_orders("c-19", 1)] == ["o-9"]


def test_recent_paid_orders_skips_others_and_unpaid(repo):
    repo.save(paid_order("x-1", "c-77", 100, 1))
    repo.save(Order("o-2", "c-19", 200, day(2)))
    assert repo.recent_paid_orders("c-19", 10) == []


def test_by_id_is_none_after_remove(repo):
    o = paid_order("o-1", "c-19", 600, 1)
    repo.save(o)
    repo.remove(o)
    assert repo.by_id("o-1") is None
```
:::

У Python це виходить майже задарма: `params` на фікстурі — і кожен тест у файлі відпрацює двічі, проти обох реалізацій. У TypeScript набір загортають у функцію й кличуть двічі. Форма різна, суть одна.

Другий тест у наборі — той самий, на якому впала наївна підробка. Тепер він стоїть у наборі назавжди: **обидві** реалізації зобов'язані показати, що мутація після `save` невидима. Наївна мапа цього не переживе, наша — переживе, бо тримає рядок. Так пастка з початку перетворилася на правило контракту.

Повільну колонку тримають окремо — `-m "not slow"` у pytest, свій проєкт у Vitest — і ганяють у CI, а не на кожне збереження файлу. Але ганяють **обов'язково**: щойно вона червоніє, це не «база примхлива», це підробка розійшлася з реальністю, і швидким тестам більше вірити не можна, доки розбіжність не закрита.

Ідея не нова й має ім'я. У каталозі тестових дублерів Ґерарда Мезароса (xUnit Test Patterns, 2007) наш клас — це **підробка** (Fake Object): реалізація, що виконує ту саму роботу, тільки значно простішим способом, і канонічний приклад там саме такий — база, замінена на хеш-таблиці в пам'яті (усталений факт). А перевірку дублера тим самим набором, що й справжню службу, Мартін Фаулер описав як [контрактний тест](book:programming/contract-testing) у нотатці «Contract Test» (12 січня 2011): перевіряємо, що звертання до дублера повертають те саме, що повернуло б звертання до справжнього (усталений факт).

> 🔧 **Навіщо це.** Без контракт-набору підробка — це друга реалізація, яку ніхто не перевіряє, і вона неминуче поповзе: хтось допише в `SqlOrderRepository` `WHERE deleted_at IS NULL`, у підробку не допише, і сотні швидких тестів почнуть упевнено брехати всі одразу. Контракт-набір робить із двох реалізацій **одну обіцянку з двома виконавцями**. І коли він зелений на обох, кожен швидкий доменний тест над підробкою можна читати як твердження про продакшн — а це і є та валюта, заради якої репозиторій узагалі заводили. Підробка без контракт-набору дає швидкість; підробка з контракт-набором дає швидкість **і** правду.

## Що підробка не покаже ніколи

Тепер про межі — бо чесна межа корисніша за десять переваг.

**Швидкість.** Підробка сканує все, що має, і сортує вручну. Порахуймо:

```
підробка:  T(n) ≈ n (фільтр по всіх рядках) + k·log k (сортування вцілілих)
база:      T(n) ≈ log n (спуск індексом (customer_id, status, created_at)) + limit

n = 8 (тест):            8 кроків проти ≈ 3 — різниці нема, мікросекунди
n = 1 000 000 (продакшн): 10⁶ кроків проти log₂(10⁶) ≈ 20 — у 50 000 разів
```

У тесті ця різниця не існує: вісім рядків — це вісім рядків. Але звідси й межа: **підробка ніколи не скаже, що ти забув індекс**. Вона зеленітиме на `recentPaidOrders` і тоді, коли в продакшні цей самий виклик влаштує повне сканування мільйона рядків. Підробка доводить, що правило **правильне**; що запит **швидкий**, доводить лише справжня база на справжніх обсягах — і це робота іншого типу перевірок.

**Обмеження, які тримає база.** `UNIQUE`, `NOT NULL`, зовнішні ключі — усе це база боронить сама, а мапа не боронить нічого. Зберегти двічі той самий `id`? Підробка мовчки перезапише, `INSERT` у базу впаде на порушенні унікальності. Зберегти замовлення неіснуючого клієнта? Підробка прийме, база відкине по зовнішньому ключу. Правило тут те саме, що з порядком: якщо домен на це обмеження **спирається**, воно мусить стати рядком у контракті й тестом у наборі — а тоді підробці доведеться його виконати (перевірити ключ у `save` і кинути ту саму помилку). Якщо не спирається — не вигадуй його підробці.

**Транзакції.** Зберегти два замовлення, і хай друге впаде: підробка лишить перше в мапі, а справжній репозиторій усередині транзакції відкотить обидва. Розбіжність справжня, але лікувати її на рівні репозиторію не варто: зводити зміни в одну транзакцію — робота [Unit of Work](book:programming/unit-of-work), і підробляти треба саме його. Підробити його, до речі, легко: `begin()` знімає копію мапи рядків, `rollback()` повертає її на місце. Знову виграє те, що підробка тримає **рядки**: знімок плаского словника — це справді знімок, а не купа посилань на живі об'єкти.

**Змагання за дані.** Два процеси читають те саме замовлення, обидва міняють, обидва зберігають — один запис губиться. База ловить це версією рядка й [оптимістичним блокуванням](book:programming/optimistic-locking); підробка, яка живе в одному потоці тесту, не покаже втраченого оновлення ніколи. Як і скрізь: спирається домен на версію — версія йде в контракт, у набір і в підробку; не спирається — не вигадуй.

**Типи колонок.** Найтихіша з усіх розбіжностей. Підробка зберігає рівно те, що ти їй дав; база зберігає те, що влізе в колонку. `NUMERIC(10,2)` округлить копійки, яких `number` у JavaScript і не думав округлювати; `timestamptz` тримає мікросекунди, а `Date` у JavaScript — лише мілісекунди, тож час, що пройшов крізь базу й повернувся, може не збігтися з тим, що ти зберігав. Підробка про це не знає й знати не може. Ліки — ті самі: у контракт-набір кладуть **незручні** значення (гроші з копійками, час із мікросекундами, довгий текст, юнікод), і повільна колонка сама покаже, де база округлила.

Бачиш повторення? Кожна межа лікується однаково: **назви обіцянку в контракті, перевір її набором проти обох**. Підробка не мусить бути схожою на базу в усьому — вона мусить бути схожою рівно в тому, на що спирається домен. Решта — не її справа.

## Останнє: підробка як гейт дизайну

І висновок, якого на початку не було видно. Ми щойно написали підробку на двадцять рядків. Це вийшло не тому, що ми молодці, а тому, що контракт складався з чотирьох доменно названих операцій.

Спробуй тепер написати підробку для контракту, який віддає назовні `IQueryable<Order>` чи `QuerySet`. Клієнт зможе побудувати **будь-який** запит — з довільними умовами, з'єднаннями, групуванням. Отже, підробка мусить уміти виконати будь-який запит. Отже, підробка мусить бути **рушієм запитів**. Отже, підробки не буде — буде або жива база в кожному тесті, або дублер, що виконує півдесятка знайомих випадків і бреше на решті.

Ось у цьому й уся діагностика: **«скільки рядків займе підробка» — це і є міра того, чи справді контракт щось ховає**. Двадцять рядків — контракт вузький, домен просить у сховища небагато й конкретно, підробка чесна майже задарма. Не пишеться взагалі — контракт нічого не абстрагував: він просто перейменував базу й пропустив її крізь себе, а домен, як і раніше, вміє все, що вміє SQL. І тоді порожньою обгорткою [антипатерна](book:programming/anti-patterns) виявляється не підробка. Виявляється сам репозиторій.

Тому підробку варто писати першою — ще до `SqlOrderRepository`. Не заради тестів. Заради питання, на яке вона відповідає негайно й безжально: чи є тут узагалі межа — чи ми її лише намалювали.
