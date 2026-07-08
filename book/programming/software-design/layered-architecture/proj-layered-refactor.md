# ⚙️ Розтягуємо злиплений контролер на шари

Є один обробник запиту, у якому зійшлося все. Він читає HTTP-тіло, рахує суму замовлення зі знижкою, відкриває з'єднання з базою, вписує рядки й повертає JSON. Двадцять рядків, які працюють — і за які тебе не похвалять, коли доведеться щось у них змінити. Спробуй перевірити правило знижки тестом: доведеться підняти справжню базу, зімітувати HTTP-запит і виколупати число з відповіді. Спробуй перейти з Postgres на іншу базу: правило знижки написане просто над відкритим курсором, тож зачепиш і його.

Тут ми не переказуватимемо, **чому** шари корисні — ми візьмемо саме такий обробник і крок за кроком розтягнемо його на домен, застосунок та інфраструктуру, щоразу дивлячись, що конкретно ця дія купує. Наприкінці правило знижки перевірятиметься тестом за мілісекунди без жодної бази, а сама база стане деталлю, яку можна вийняти й замінити. Уся магія — в одному: **куди дивиться стрілка залежності**.

## Пацієнт: обробник, де все зрослося

Ось із чого починаємо. Один ендпойнт «оформити замовлення»: перевірити наявність товару, порахувати суму зі знижкою за промокодом, записати замовлення й зменшити залишок. Усе в одному тілі.

:::tabs
```python
# app.py — усе в одному обробнику: HTTP + правило + SQL
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.post("/orders")
def place_order():
    body = request.get_json()
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()

    total = 0.0
    for line in body["items"]:
        row = cur.execute(
            "SELECT price, stock FROM products WHERE sku = ?",
            (line["sku"],)).fetchone()
        if row is None:
            return jsonify(error=f"немає товару {line['sku']}"), 404
        price, stock = row
        if stock < line["qty"]:
            return jsonify(error=f"замало {line['sku']}"), 409
        total += price * line["qty"]

    # знижка за промокодом — правило бізнесу, вписане просто тут
    code = body.get("promo")
    if code == "SPRING":
        total *= 0.9
    elif code == "VIP":
        total *= 0.8

    order_id = cur.execute(
        "INSERT INTO orders(total) VALUES (?)", (total,)).lastrowid
    for line in body["items"]:
        cur.execute("UPDATE products SET stock = stock - ? WHERE sku = ?",
                    (line["qty"], line["sku"]))
    conn.commit()
    return jsonify(order_id=order_id, total=total), 201
```
```ts
// server.ts — усе в одному обробнику: HTTP + правило + SQL
import express from "express";
import Database from "better-sqlite3";

const app = express();
app.use(express.json());
const db = new Database("shop.db");

app.post("/orders", (req, res) => {
  const body = req.body as {
    items: { sku: string; qty: number }[];
    promo?: string;
  };

  let total = 0;
  for (const line of body.items) {
    const row = db.prepare(
      "SELECT price, stock FROM products WHERE sku = ?").get(line.sku) as
      { price: number; stock: number } | undefined;
    if (!row) return res.status(404).json({ error: `немає товару ${line.sku}` });
    if (row.stock < line.qty)
      return res.status(409).json({ error: `замало ${line.sku}` });
    total += row.price * line.qty;
  }

  // знижка за промокодом — правило бізнесу, вписане просто тут
  if (body.promo === "SPRING") total *= 0.9;
  else if (body.promo === "VIP") total *= 0.8;

  const info = db.prepare("INSERT INTO orders(total) VALUES (?)").run(total);
  const orderId = info.lastInsertRowid;
  for (const line of body.items)
    db.prepare("UPDATE products SET stock = stock - ? WHERE sku = ?")
      .run(line.qty, line.sku);

  res.status(201).json({ orderId, total });
});
```
:::

Придивись, що тут стряслося. Правило «SPRING дає 10%, VIP — 20%» — це серце бізнесу, найцінніший рядок у файлі. А стоїть він затиснутий між `cur.execute(...)` і `INSERT`, приклеєний до конкретного драйвера бази й конкретного формату HTTP-тіла. Щоб дізнатися, чи правильно рахується знижка, немає способу коротшого, ніж підняти всю цю машину. Три різні життя — екран, правило, база — злиплися в одну грудку, і кожне тягне за собою два інші.

![Ліворуч контролер, де HTTP, правило суми й SQL злиплися в одну грудку зі стрілкою прямо в Postgres; праворуч три шари, де стрілки залежності дивляться вниз до домену](/book/programming/software-design/layered-architecture/img/arrow-flip.svg)
*Ліва картина — те, з чого ми починаємо. Права — куди йдемо: правило переїжджає в домен, а база опиняється на кінці стрілки, куди й належить.*

Мета — дійти від лівої картини до правої. Робитимемо це не одним стрибком, а маленькими кроками, після кожного з яких код лишається робочим.

## Крок 1. Виколупати правило в домен

Перше, що треба врятувати, — правило. Воно не повинно знати ні про HTTP, ні про SQL; воно має оперувати числами й поняттями бізнесу. Витягуємо `Order` як окрему сутність, яка вміє порахувати власну суму, і промокод як окреме поняття.

Ключове тут — **жодного імпорту бази чи вебфреймворку** в цьому файлі. Якщо він з'явиться, ми провалили крок.

:::tabs
```python
# domain/order.py — правила предметної області, і більш нічого
from dataclasses import dataclass
from enum import Enum

class Promo(Enum):
    NONE = 1.0
    SPRING = 0.9
    VIP = 0.8

@dataclass(frozen=True)
class Line:
    sku: str
    qty: int
    price: float          # ціну домен отримує ззовні, сам її не шукає

@dataclass
class Order:
    lines: list[Line]
    promo: Promo = Promo.NONE

    def total(self) -> float:
        raw = sum(l.price * l.qty for l in self.lines)
        return round(raw * self.promo.value, 2)
```
```ts
// domain/order.ts — правила предметної області, і більш нічого
export enum Promo { None = 1.0, Spring = 0.9, Vip = 0.8 }

export interface Line {
  readonly sku: string;
  readonly qty: number;
  readonly price: number;   // ціну домен отримує ззовні, сам її не шукає
}

export class Order {
  constructor(
    readonly lines: Line[],
    readonly promo: Promo = Promo.None,
  ) {}

  total(): number {
    const raw = this.lines.reduce((s, l) => s + l.price * l.qty, 0);
    return Math.round(raw * this.promo * 100) / 100;
  }
}
```
:::

Одразу видно виграш. Правило знижки тепер живе в місці, куди не дотягується ні база, ні мережа, і його можна перевірити прямим тестом — без Flask, без sqlite, без нічого:

:::tabs
```python
# tests/test_order.py — правило перевіряється за мілісекунди
from domain.order import Order, Line, Promo

def test_vip_discount():
    order = Order([Line("A", 2, 100.0)], promo=Promo.VIP)
    assert order.total() == 160.0     # 200 · 0.8

def test_no_promo():
    order = Order([Line("A", 1, 33.3), Line("B", 3, 10.0)], Promo.NONE)
    assert order.total() == 63.3
```
```ts
// order.test.ts — правило перевіряється за мілісекунди
import { Order, Promo } from "../domain/order";

test("vip discount", () => {
  const order = new Order([{ sku: "A", qty: 2, price: 100 }], Promo.Vip);
  expect(order.total()).toBe(160);   // 200 · 0.8
});

test("no promo", () => {
  const order = new Order(
    [{ sku: "A", qty: 1, price: 33.3 }, { sku: "B", qty: 3, price: 10 }]);
  expect(order.total()).toBe(63.3);
});
```
:::

Зверни увагу на одну свідому відмову: `Line` несе `price` у собі, домен ціну **не шукає**. Це не дрібниця. Якби `total()` сам ходив у базу по ціну, ми б протягли базу назад у домен через чорний хід і зіпсували все, що щойно зробили. Домен рахує з тих чисел, які йому дали; звідки взялися числа — не його клопіт. Це та сама межа, тільки видна зблизька.

## Крок 2. Винести обіцянку сховища — інтерфейс у домені

Правило врятоване, але замовлення ще треба десь зберігати й десь брати ціни та залишки. Спокуса — дати домену клас `Database`. Це і є та пастка, через яку шари протікають вниз: щойно домен назве конкретну базу на ім'я, він від неї залежить, і замінити її вже не можна.

Прийом, який усе рятує, — **інверсія залежності**. Домен не називає базу; він оголошує **інтерфейс** — обіцянку «хтось уміє знайти товар і зберегти замовлення», не кажучи хто. Це називають сховищем, або репозиторієм (від англ. *repository* — сховище): колекцієподібний фасад над збереженням, що ховає, чи там SQL, чи файл, чи мережа.

> 🔧 **Навіщо це.** Інтерфейс сховища — це шов, уздовж якого домен відривається від бази. Поки домен бачить лише обіцянку, а не драйвер, будь-що по той бік обіцянки замінне: жива база в проді, файл у прототипі, фальшивка в тесті. Без цього інтерфейсу база вросла б у правила, і кожен тест волік би її за собою.

Ось де тонкість, на якій багато хто спотикається. Інтерфейс `ProductRepo` **оголошено в домені**, а реалізацію — в інфраструктурі. У коді файл інфраструктури імпортує файл домену (щоб побачити інтерфейс), а не навпаки. Тому стрілка **залежності** дивиться вниз, до абстракції домену, хоча текст реалізації сидить «нижче». Про цей поворот докладніше — стаття [про інверсію залежностей](book:programming/dependency-inversion); тут ми його просто застосовуємо.

:::tabs
```python
# domain/repos.py — обіцянки, які домен вимагає від світу (ще не реалізація)
from typing import Protocol
from domain.order import Order, Line

class ProductRepo(Protocol):
    def find(self, sku: str) -> tuple[float, int] | None:
        """Повернути (ціна, залишок) або None, якщо товару немає."""
        ...

class OrderRepo(Protocol):
    def add(self, order: Order) -> int:
        """Зберегти замовлення, повернути його id."""
        ...
    def reduce_stock(self, sku: str, qty: int) -> None:
        ...
```
```ts
// domain/repos.ts — обіцянки, які домен вимагає від світу (ще не реалізація)
import { Order } from "./order";

export interface ProductRepo {
  // повернути [ціна, залишок] або null, якщо товару немає
  find(sku: string): [price: number, stock: number] | null;
}

export interface OrderRepo {
  add(order: Order): number;              // зберегти, повернути id
  reduceStock(sku: string, qty: number): void;
}
```
:::

Тут варто зупинитися на одному рішенні, яке легко проґавити. Хто **вигадує** цей інтерфейс — домен чи інфраструктура? Відповідь принципова: **домен**, під свою потребу. Інтерфейс формулюють у словах бізнесу («знайти товар», «додати замовлення»), а не в словах бази («виконати SELECT»). Це те, що інколи звуть відокремленим інтерфейсом (англ. *Separated Interface*): абстракцію оголошує той, хто нею **користується**, а не той, хто її **реалізує**. Якби інтерфейс диктувала база, він би просочився деталями бази, і сенс зник би.

## Крок 3. Реалізувати сховище в інфраструктурі

Тепер — конкретика, яку ми стільки відсували. SQL-реалізація сидить в інфраструктурі, імпортує інтерфейси з домену й виконує обіцянку. Уся мова бази замкнена тут; вище цей файл ніхто не імпортує.

:::tabs
```python
# infra/sql_repos.py — тут (і лише тут) живе SQL
from domain.order import Order
from domain.repos import ProductRepo, OrderRepo

class SqlProductRepo:                 # структурно задовольняє ProductRepo
    def __init__(self, conn):
        self.conn = conn
    def find(self, sku: str):
        row = self.conn.execute(
            "SELECT price, stock FROM products WHERE sku = ?", (sku,)).fetchone()
        return (row[0], row[1]) if row else None

class SqlOrderRepo:                    # структурно задовольняє OrderRepo
    def __init__(self, conn):
        self.conn = conn
    def add(self, order: Order) -> int:
        return self.conn.execute(
            "INSERT INTO orders(total) VALUES (?)",
            (order.total(),)).lastrowid
    def reduce_stock(self, sku: str, qty: int) -> None:
        self.conn.execute(
            "UPDATE products SET stock = stock - ? WHERE sku = ?", (qty, sku))
```
```ts
// infra/sqlRepos.ts — тут (і лише тут) живе SQL
import type { Database } from "better-sqlite3";
import { Order } from "../domain/order";
import { ProductRepo, OrderRepo } from "../domain/repos";

export class SqlProductRepo implements ProductRepo {
  constructor(private db: Database) {}
  find(sku: string): [number, number] | null {
    const row = this.db.prepare(
      "SELECT price, stock FROM products WHERE sku = ?").get(sku) as
      { price: number; stock: number } | undefined;
    return row ? [row.price, row.stock] : null;
  }
}

export class SqlOrderRepo implements OrderRepo {
  constructor(private db: Database) {}
  add(order: Order): number {
    return Number(this.db.prepare(
      "INSERT INTO orders(total) VALUES (?)").run(order.total()).lastInsertRowid);
  }
  reduceStock(sku: string, qty: number): void {
    this.db.prepare("UPDATE products SET stock = stock - ? WHERE sku = ?")
      .run(qty, sku);
  }
}
```
:::

Дрібна, але промовиста різниця між мовами. У Python `SqlProductRepo` **ніде не називає** `ProductRepo` — його достатньо, щоб він мав потрібні методи (структурна, «качина» відповідність через `Protocol`). У TypeScript ми пишемо `implements ProductRepo` явно. Обидва підходи дають те саме: конкретний клас задовольняє обіцянку домену. Але напрямок імпорту в обох однаковий — інфраструктура тягне домен, домен про інфраструктуру не чув.

## Крок 4. Диригент у шарі застосунку

Правило в домені, база в інфраструктурі — між ними бракує того, хто веде сценарій: «знайди товари, перевір залишок, порахуй, збережи, зменши». Це не правило (правило — лише сама формула суми) і не техніка бази — це **координація**, і живе вона в шарі застосунку. Дехто зве такий клас службою або варіантом використання (англ. *use case*).

Найважливіше в ньому — він приймає сховища **ззовні**, через конструктор, і бачить їх лише як інтерфейси. Він не знає, що всередині SQL. Саме тут стрілка розвертається остаточно: застосунок залежить від обіцянок домену, а конкретний `SqlOrderRepo` підставлять пізніше й іззовні.

:::tabs
```python
# application/place_order.py — сценарій; бачить лише інтерфейси домену
from domain.order import Order, Line, Promo
from domain.repos import ProductRepo, OrderRepo

class OutOfStock(Exception): ...
class UnknownProduct(Exception): ...

class PlaceOrder:
    def __init__(self, products: ProductRepo, orders: OrderRepo):
        self.products = products      # обіцянки, не драйвери
        self.orders = orders

    def run(self, raw_items: list[dict], promo: str | None) -> dict:
        lines = []
        for it in raw_items:
            found = self.products.find(it["sku"])
            if found is None:
                raise UnknownProduct(it["sku"])
            price, stock = found
            if stock < it["qty"]:
                raise OutOfStock(it["sku"])
            lines.append(Line(it["sku"], it["qty"], price))

        order = Order(lines, Promo[promo] if promo else Promo.NONE)
        order_id = self.orders.add(order)
        for l in lines:
            self.orders.reduce_stock(l.sku, l.qty)
        return {"order_id": order_id, "total": order.total()}
```
```ts
// application/placeOrder.ts — сценарій; бачить лише інтерфейси домену
import { Order, Line, Promo } from "../domain/order";
import { ProductRepo, OrderRepo } from "../domain/repos";

export class OutOfStock extends Error {}
export class UnknownProduct extends Error {}

const promoOf = (s?: string): Promo =>
  s === "SPRING" ? Promo.Spring : s === "VIP" ? Promo.Vip : Promo.None;

export class PlaceOrder {
  constructor(
    private products: ProductRepo,     // обіцянки, не драйвери
    private orders: OrderRepo,
  ) {}

  run(rawItems: { sku: string; qty: number }[], promo?: string) {
    const lines: Line[] = [];
    for (const it of rawItems) {
      const found = this.products.find(it.sku);
      if (!found) throw new UnknownProduct(it.sku);
      const [price, stock] = found;
      if (stock < it.qty) throw new OutOfStock(it.sku);
      lines.push({ sku: it.sku, qty: it.qty, price });
    }

    const order = new Order(lines, promoOf(promo));
    const orderId = this.orders.add(order);
    for (const l of lines) this.orders.reduceStock(l.sku, l.qty);
    return { orderId, total: order.total() };
  }
}
```
:::

Помітив, що обробник HTTP іще ніде не згаданий? І `PlaceOrder`, і `Order` про Flask чи Express не чули. Це навмисно: сценарій оперує звичайними списками й словниками, а переклад HTTP ↔ ці структури — робота найверхнього шару, до якого ми зараз дійдемо.

## Крок 5. Тонкий контролер угорі

Тепер від пацієнта лишається лише шкірка — контролер, чия єдина робота перекласти HTTP-запит у виклик сценарію й відповідь сценарію назад у HTTP. Жодного правила, жодного SQL: розібрав тіло, гукнув, склав відповідь, перетворив помилки домену на коди статусу.

:::tabs
```python
# web/routes.py — лише переклад HTTP ↔ виклик сценарію
from flask import Blueprint, request, jsonify
from application.place_order import PlaceOrder, OutOfStock, UnknownProduct

def make_routes(place: PlaceOrder) -> Blueprint:
    bp = Blueprint("orders", __name__)

    @bp.post("/orders")
    def create():
        body = request.get_json()
        try:
            result = place.run(body["items"], body.get("promo"))
        except UnknownProduct as e:
            return jsonify(error=f"немає товару {e}"), 404
        except OutOfStock as e:
            return jsonify(error=f"замало {e}"), 409
        return jsonify(result), 201

    return bp
```
```ts
// web/routes.ts — лише переклад HTTP ↔ виклик сценарію
import { Router } from "express";
import { PlaceOrder, OutOfStock, UnknownProduct } from "../application/placeOrder";

export function makeRoutes(place: PlaceOrder): Router {
  const r = Router();
  r.post("/orders", (req, res) => {
    try {
      const result = place.run(req.body.items, req.body.promo);
      res.status(201).json(result);
    } catch (e) {
      if (e instanceof UnknownProduct)
        return res.status(404).json({ error: `немає товару ${e.message}` });
      if (e instanceof OutOfStock)
        return res.status(409).json({ error: `замало ${e.message}` });
      throw e;
    }
  });
  return r;
}
```
:::

Тепер увесь код розкладено на чотири зрозумілі теки — `web`, `application`, `domain`, `infra` — і залежності течуть строго вниз. Але лишилося невимовлене питання: **хто ж усіх їх знайомить?** `PlaceOrder` вимагає `ProductRepo`, `SqlProductRepo` вимагає з'єднання — а нікого з них ніхто ще не створює. Ці нитки сходяться в одну точку.

## Крок 6. Збірка на вершечку

Є єдине місце, де конкретні класи можна називати на ім'я безкарно, — **найвища точка входу**, з якої стартує програма. Тут (і лише тут) з'являються слова `SqlOrderRepo`, `connect`, `Express`. Створюємо драйвер, загортаємо його у сховища, віддаємо сценарію, чіпляємо контролер. Цей прийом — «складання на вершечку»; коли деталь **дістають ззовні**, а не творять усередині, це і є впровадження залежностей (стаття [про впровадження залежностей](book:programming/dependency-injection) розбирає його як окремий інструмент).

:::tabs
```python
# main.py — ЄДИНЕ місце, де конкретні класи названо на ім'я
import sqlite3
from flask import Flask
from infra.sql_repos import SqlProductRepo, SqlOrderRepo
from application.place_order import PlaceOrder
from web.routes import make_routes

def build_app() -> Flask:
    conn = sqlite3.connect("shop.db", check_same_thread=False)
    products = SqlProductRepo(conn)          # обіцянку виконує SQL —
    orders = SqlOrderRepo(conn)              #   але знає про це лише тут
    place = PlaceOrder(products, orders)     # сценарію дали готові сховища
    app = Flask(__name__)
    app.register_blueprint(make_routes(place))
    return app

app = build_app()
```
```ts
// main.ts — ЄДИНЕ місце, де конкретні класи названо на ім'я
import express from "express";
import Database from "better-sqlite3";
import { SqlProductRepo, SqlOrderRepo } from "./infra/sqlRepos";
import { PlaceOrder } from "./application/placeOrder";
import { makeRoutes } from "./web/routes";

export function buildApp() {
  const db = new Database("shop.db");
  const products = new SqlProductRepo(db);   // обіцянку виконує SQL —
  const orders = new SqlOrderRepo(db);       //   але знає про це лише тут
  const place = new PlaceOrder(products, orders);
  const app = express();
  app.use(express.json());
  app.use(makeRoutes(place));
  return app;
}

buildApp().listen(3000);
```
:::

Ця точка входу — єдина частина програми, яка знає **всіх** учасників поіменно. Її іноді звуть коренем композиції (англ. *composition root*). Уся решта коду знає лише своїх сусідів через інтерфейси; конкретні імена стягуються в цю одну верхню точку — і саме тому їх так легко підмінити.

## Заради чого все — підміна бази фальшивкою в тесті

Тепер найсолодше, задля чого й крутили стрілку. Оскільки `PlaceOrder` приймає сховища **ззовні** й бачить їх як інтерфейси, у тесті ми даємо йому не SQL, а фальшивку (англ. *fake*) — сховище в пам'яті, що поводиться правдиво, але тримає дані в словнику. Жодної бази, жодного файлу; тест увесь сценарій ганяє за мілісекунди.

Тут корисно назвати речі точно. Загальний термін для будь-якого підставного об'єкта в тесті ввів Джерард Мезарос (Gerard Meszaros) у книзі *xUnit Test Patterns* (2007) — **тест-дублер** (англ. *Test Double*), за прямою аналогією з дублером-каскадером у кіно; Мартін Фаулер саме так це й пояснює: «загальний термін, який він уживає, — Test Double (уяви каскадера-дублера)» *(джерело: bliki Мартіна Фаулера «TestDouble»; усталена термінологія)*. Фальшивка (fake) — один із п'яти його різновидів: на відміну від заглушки, що лише повертає завчене, фальшивка має **робочу**, хоч і спрощену, реалізацію. Наша пам'ятна база — саме фальшивка.

:::tabs
```python
# tests/test_place_order.py — той самий сценарій БЕЗ бази
from application.place_order import PlaceOrder, OutOfStock

class FakeRepo:                       # одна фальшивка на обидві обіцянки
    def __init__(self, catalog):
        self.catalog = dict(catalog)  # sku -> [price, stock]
        self.saved = []
    # ProductRepo
    def find(self, sku):
        row = self.catalog.get(sku)
        return (row[0], row[1]) if row else None
    # OrderRepo
    def add(self, order):
        self.saved.append(order)
        return len(self.saved)        # «id» = порядковий номер
    def reduce_stock(self, sku, qty):
        self.catalog[sku][1] -= qty

def test_places_and_reduces_stock():
    repo = FakeRepo({"A": [100.0, 5]})
    place = PlaceOrder(repo, repo)
    res = place.run([{"sku": "A", "qty": 2}], promo="VIP")

    assert res["total"] == 160.0      # 200 · 0.8
    assert repo.catalog["A"][1] == 3  # залишок зменшився 5 → 3
    assert len(repo.saved) == 1

def test_rejects_when_out_of_stock():
    repo = FakeRepo({"A": [100.0, 1]})
    place = PlaceOrder(repo, repo)
    try:
        place.run([{"sku": "A", "qty": 2}], promo=None)
        assert False, "мало впасти"
    except OutOfStock:
        pass
    assert repo.catalog["A"][1] == 1  # залишок НЕ чіпали
```
```ts
// placeOrder.test.ts — той самий сценарій БЕЗ бази
import { PlaceOrder, OutOfStock } from "../application/placeOrder";
import { Order } from "../domain/order";

class FakeRepo {                      // одна фальшивка на обидві обіцянки
  saved: Order[] = [];
  constructor(private catalog: Record<string, [number, number]>) {}
  find(sku: string): [number, number] | null {
    return this.catalog[sku] ?? null;
  }
  add(order: Order): number {
    this.saved.push(order);
    return this.saved.length;         // «id» = порядковий номер
  }
  reduceStock(sku: string, qty: number): void {
    this.catalog[sku][1] -= qty;
  }
}

test("places and reduces stock", () => {
  const repo = new FakeRepo({ A: [100, 5] });
  const place = new PlaceOrder(repo, repo);
  const res = place.run([{ sku: "A", qty: 2 }], "VIP");

  expect(res.total).toBe(160);        // 200 · 0.8
  expect(repo["catalog"].A[1]).toBe(3); // залишок 5 → 3
  expect(repo.saved).toHaveLength(1);
});

test("rejects when out of stock", () => {
  const repo = new FakeRepo({ A: [100, 1] });
  const place = new PlaceOrder(repo, repo);
  expect(() => place.run([{ sku: "A", qty: 2 }])).toThrow(OutOfStock);
  expect(repo["catalog"].A[1]).toBe(1); // залишок НЕ чіпали
});
```
:::

Ось воно — те, що обіцяла стрілка. Ми перевірили **весь сценарій оформлення** — пошук, перевірку залишку, знижку, запис, списання — не піднявши жодної бази. Тест `test_rejects_when_out_of_stock` навіть ловить тонку річ: коли товару замало, залишок чіпати не можна, і фальшивка це доводить прямою перевіркою словника. У початковому злиплому обробнику така перевірка вимагала б справжньої бази, справжнього HTTP-запиту й виколупування числа з відповіді. Тепер це три рядки й мілісекунди. **Це не побічний бонус чистоти — це і є те, задля чого стрілку розвертали.**

## Складність і пастки

Малюнок гарний, але живий рефакторинг наштовхується на кілька гострих кутів. Пройдімося по тих, що ріжуть найчастіше.

**Транзакція — це не деталь одного сховища.** Наш сценарій пише у дві таблиці: додає замовлення й зменшує залишок. Якщо між ними впаде живлення, замовлення є, а товар не списаний — база розповзлась. Ці дві дії мусять бути **однією транзакцією**: або обидві, або жодної. І тут криється пастка: транзакція охоплює **кілька сховищ**, тож нею не може керувати жодне з них поодинці. Керує той, хто бачить увесь сценарій, — шар застосунку.

![Сценарій PlaceOrder угорі; пунктирна рамка охоплює обидва сховища OrderRepo і StockRepo, підписана «одна транзакція: або всі, або жоден»](/book/programming/software-design/layered-architecture/img/transaction-seam.svg)
*Межу транзакції відкриває застосунок і накриває нею обидва сховища. Домен про транзакції не знає — це технічна межа, а не правило бізнесу.*

Патерн, що загортає групу змін у один атомарний шов, каталогізував Мартін Фаулер (Martin Fowler) у книзі *Patterns of Enterprise Application Architecture* (2002) під іменем **одиниця роботи** (англ. *Unit of Work*) — поряд із самим **репозиторієм** *(джерело: каталог патернів PoEAA; усталена термінологія)*. Ідея проста: об'єкт, що тримає одне з'єднання й один `commit`, а сховища всередині сідають на нього. Ось як це виглядає в збірці — застосунок відкриває шов, обидва сховища працюють на спільному з'єднанні, а `commit` один:

:::tabs
```python
# application/place_order.py — сценарій під однією транзакцією
from contextlib import contextmanager

class SqlUnitOfWork:
    def __init__(self, conn): self.conn = conn
    @contextmanager
    def atomic(self):
        try:
            yield
            self.conn.commit()        # усе вдалось — фіксуємо
        except Exception:
            self.conn.rollback()      # хоч щось впало — відкат
            raise

class PlaceOrder:
    def __init__(self, products, orders, uow: SqlUnitOfWork):
        self.products, self.orders, self.uow = products, orders, uow
    def run(self, raw_items, promo):
        # ... збір lines і перевірки як раніше ...
        with self.uow.atomic():       # межу транзакції відкриває застосунок
            order_id = self.orders.add(order)
            for l in lines:
                self.orders.reduce_stock(l.sku, l.qty)
        return {"order_id": order_id, "total": order.total()}
```
```ts
// application/placeOrder.ts — сценарій під однією транзакцією
export class SqlUnitOfWork {
  constructor(private db: import("better-sqlite3").Database) {}
  atomic<T>(work: () => T): T {
    const tx = this.db.transaction(work); // better-sqlite3: усе або нічого
    return tx();                           // commit/rollback — автоматично
  }
}

export class PlaceOrder {
  constructor(
    private products: ProductRepo,
    private orders: OrderRepo,
    private uow: SqlUnitOfWork,
  ) {}
  run(rawItems, promo) {
    // ... збір lines і перевірки як раніше ...
    return this.uow.atomic(() => {         // межу транзакції відкриває застосунок
      const orderId = this.orders.add(order);
      for (const l of lines) this.orders.reduceStock(l.sku, l.qty);
      return { orderId, total: order.total() };
    });
  }
}
```
:::

Тонкість, яку легко провалити: обидва сховища мусять сидіти на **тому самому** з'єднанні, інакше кожне відкриє свою транзакцію й атомарність зникне. Тому одиниця роботи роздає з'єднання сховищам, а не кожне саме собі його бере. У тесті ж фальшивка транзакцій не потребує зовсім — `atomic` там може просто виконати тіло, бо словник у пам'яті або зміниться весь, або кине виняток до першого запису.

**Не роби шар домену анемічним.** Найпоширеніша хиба після такого поділу — витягти з домену *усі* дані в `dataclass`, а *усю* поведінку зсунути в сценарій. Тоді домен стає мішком геттерів без правил, а вся логіка тече в застосунок — це звуть анемічною моделлю. Лінія проста: якщо метод — це **правило предметної області** (як рахувати суму, чи валідне замовлення), він у домені; якщо це **послідовність кроків** (знайди, перевір, збережи), він у застосунку. Правило `total()` лишилось у `Order` саме тому.

**Не плоди інтерфейс на кожен клас.** Інверсія залежності цінна там, де реалізацію справді підмінюють: база, платіжний шлюз, черга. Огортати інтерфейсом кожен внутрішній клас домену — марна церемонія, що роздуває код без користі. Інтерфейс — це вартість; плати її лише за справжній шов, де по той бік буде більш ніж одна реалізація (жива й тестова — вже дві, і цього досить).

**Repository — не діркою в абстракції.** Спокуса дати сховищу метод на кожен химерний запит («знайти замовлення, старші за 30 днів, зі знижкою VIP, посортовані…») перетворює чисту абстракцію на решето, крізь яке деталі бази протікають назад у домен через сигнатури методів. Тримай інтерфейс сховища у словах бізнесу й вузьким; коли запити стають складними й специфічними для читання, їх часто варто винести окремим шляхом читання (це вже територія розділення команд і запитів, але то інша розмова).

**Крос-процесна транзакція — це вже не та транзакція.** Усе сказане про одиницю роботи тримається, поки сховища сидять в **одній базі** й ділять з'єднання. Щойно одне сховище пише в Postgres, а друге шле повідомлення в чергу, спільного `commit` немає — база й черга не діляться транзакцією. Тоді атомарність доводиться будувати іншими засобами (наприклад, писати намір у ту саму базу й досилати його окремо), і це окрема, серйозна тема. Тут важливо лише не обманюватися: `Unit of Work` рятує в межах одного сховища даних, а не через мережу.

Підсумок усього руху вміщується в одну думку. Ми не додали функцій — обробник як робив замовлення, так і робить. Ми **пересунули стрілки**: правило переїхало в домен, база сховалася за інтерфейс, конкретні імена стеклися в одну верхню точку. І щойно стрілка залежності лягла вниз, домен став тестованим без бази, а база — замінною без страху за правила. Шари — це не спосіб зробити складніше; це спосіб зробити так, щоб **найдорожчі зміни били в один шар і там спинялися**.
