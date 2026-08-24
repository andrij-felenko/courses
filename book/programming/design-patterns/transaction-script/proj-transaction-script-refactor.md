# ⚙️ Один сценарій, три копії — і хто, зрештою, володіє правилом

Візьмімо серверну частину крамниці й напишімо її саме так, як радять писати прості речі: сценаріями транзакцій. Не абстрактно — на живому коді, який компілюється й працює. Почнемо з однієї чистої процедури, доростимо її до трьох, і на очах побачимо тріщину, про яку зазвичай розповідають словами: як знання «що таке правильне замовлення» тихо розповзається копіями й ще тихіше розходиться. А тоді — два кроки рятунку, від дешевого до серйозного, і чіткий критерій, який каже, коли робити другий.

Таблиць рівно три: `products(id, price, stock)`, `orders(id, customer_id, total, status)`, `order_lines(order_id, product_id, qty, price)`. Плюс `customers`, звідки нам знадобиться регіон. Помічники для бази — тонкі: `db.begin()` відкриває транзакцію, далі `get`/`run`/`all` (чи `execute`/`fetchone` у Python), а `commit`/`rollback` закривають. За ними — звичайний SQL; сценарію байдуже, що саме там усередині.

## Один чистий сценарій

Ось `placeOrder` цілком. Читається згори вниз, як рецепт: перевір товар, порахуй суму зі знижкою, запиши замовлення й рядок, спиши залишок, закрий транзакцію. Спільний шматок — знижку — одразу винесено в підпроцедуру `loyaltyDiscount`: це перша, найдешевша лінія оборони проти повторів, і поки правило коротке, її вистачає.

:::tabs
```ts
// одна ділова операція — одна процедура, згори вниз
async function placeOrder(customerId: string, productId: number, qty: number): Promise<number> {
  const tx = await db.begin();                          // ── МЕЖА ТРАНЗАКЦІЇ: тут вона відкрита
  try {
    const product = await tx.get(
      "SELECT price, stock FROM products WHERE id = ?", productId);
    if (!product) throw new Error("немає такого товару");
    if (product.stock < qty) throw new Error("недостатньо на складі");

    const discount = await loyaltyDiscount(tx, customerId);   // спільна підпроцедура
    const total = product.price * qty * (1 - discount);       // ← ПРАВИЛО ціни живе тут

    const { lastID: orderId } = await tx.run(
      "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, 'new')",
      customerId, total);
    await tx.run(
      "INSERT INTO order_lines (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
      orderId, productId, qty, product.price);
    await tx.run(
      "UPDATE products SET stock = stock - ? WHERE id = ?", qty, productId);

    await tx.commit();                                  // ── усі чотири зміни доїхали разом
    return orderId;
  } catch (e) {
    await tx.rollback();                                // будь-яка невдача — відкат усього
    throw e;
  }
}
```
```py
def place_order(customer_id: str, product_id: int, qty: int) -> int:
    tx = db.begin()                                     # ── МЕЖА ТРАНЗАКЦІЇ: тут вона відкрита
    try:
        product = tx.execute(
            "SELECT price, stock FROM products WHERE id = ?", (product_id,)).fetchone()
        if product is None:
            raise ValueError("немає такого товару")
        if product.stock < qty:
            raise ValueError("недостатньо на складі")

        discount = loyalty_discount(tx, customer_id)    # спільна підпроцедура
        total = product.price * qty * (1 - discount)    # ← ПРАВИЛО ціни живе тут

        cur = tx.execute(
            "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, 'new')",
            (customer_id, total))
        order_id = cur.lastrowid
        tx.execute(
            "INSERT INTO order_lines (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
            (order_id, product_id, qty, product.price))
        tx.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?", (qty, product_id))

        tx.commit()                                     # ── усі чотири зміни доїхали разом
        return order_id
    except Exception:
        tx.rollback()                                   # будь-яка невдача — відкат усього
        raise
```
:::

Дві речі варто зафіксувати, бо на них триматиметься вся дальша історія. Перша: **межа транзакції** — це `begin` угорі й `commit`/`rollback` унизу, і вона обіймає всю процедуру. Або доїжджають усі чотири зміни (замовлення, рядок, залишок), або жодна; проміжного стану, де замовлення є, а залишок не списаний, база не покаже. Друга: рядок, позначений «ПРАВИЛО ціни живе тут», — це і є знання «скільки коштує правильне замовлення». Зараз воно вміщається в один вираз, і здається, що турбуватися нема про що.

## Другий і третій

Тепер додамо братів. `changeQty` дозволяє покупцеві змінити кількість у вже створеному, ще не оплаченому замовленні — а отже, мусить **перерахувати підсумок за тим самим правилом**. `reorder` повторює старе замовлення новим — і теж рахує підсумок наново, бо ціни й знижка могли змінитися. Кожен — свій самодостатній сценарій зі своєю межею транзакції; наводжу лише те місце, де живе ціна:

:::tabs
```ts
async function changeQty(orderId: number, newQty: number): Promise<void> {
  const tx = await db.begin();
  try {
    const line = await tx.get(
      "SELECT product_id, price FROM order_lines WHERE order_id = ?", orderId);
    const order = await tx.get(
      "SELECT customer_id FROM orders WHERE id = ?", orderId);

    const discount = await loyaltyDiscount(tx, order.customer_id);
    const total = line.price * newQty * (1 - discount);     // ← та сама формула, друга копія

    await tx.run("UPDATE order_lines SET qty = ? WHERE order_id = ?", newQty, orderId);
    await tx.run("UPDATE orders SET total = ? WHERE id = ?", total, orderId);
    await tx.commit();
  } catch (e) { await tx.rollback(); throw e; }
}
```
```py
def change_qty(order_id: int, new_qty: int) -> None:
    tx = db.begin()
    try:
        line = tx.execute(
            "SELECT product_id, price FROM order_lines WHERE order_id = ?", (order_id,)).fetchone()
        order = tx.execute(
            "SELECT customer_id FROM orders WHERE id = ?", (order_id,)).fetchone()

        discount = loyalty_discount(tx, order.customer_id)
        total = line.price * new_qty * (1 - discount)         # ← та сама формула, друга копія

        tx.execute("UPDATE order_lines SET qty = ? WHERE order_id = ?", (new_qty, order_id))
        tx.execute("UPDATE orders SET total = ? WHERE id = ?", (total, order_id))
        tx.commit()
    except Exception:
        tx.rollback(); raise
```
:::

`reorder` виглядає так само по суті: читає рядки старого замовлення, бере свіжу знижку й пише `total = price · qty · (1 − discount)` втретє. Три сценарії — три однакові вирази ціни. Поки правило — рівно один рядок, це навіть не боляче: очі бачать, що формула та сама, і мозок відмовляється вважати три однакові рядки проблемою. Саме ця відмова нас і підставить.

## Правило росте — і копії розходяться

Бізнес рідко лишає ціну однорядковою. Приходить бухгалтерія: додаємо **регіональний податок** (ставка залежить від регіону покупця) і **поріг** — чиста сума після знижки не має падати нижче мінімальної суми для регіону, тож якщо знижка проштовхнула б замовлення під поріг, знижку підрізаємо до порогу. Тепер «правильна ціна» — не вираз, а маленький алгоритм із гілкою:

```
subtotal = price · qty
net      = subtotal · (1 − discount)
поріг    = floor(region)
якщо net < поріг:  net = поріг          ← знижка не опускає нижче порогу
total    = net · (1 + tax(region))
```

І тут стається те, заради чого ми все це писали. Цей алгоритм **не складається в один охайний виклик** — податок бере регіон, поріг бере регіон і чисту суму, гілка зчіпляє знижку із сумою. Винести його цілим у підпроцедуру можна, але спершу ніхто цього не робить: правило дописують просто там, де воно знадобилося першим, — у `placeOrder`. А тоді той самий шматок треба руками перенести у двох братів. І ось три копії, які починали однаковими, розходяться — бо переносив їх людина, поспіхом, у різні дні:

:::tabs
```ts
// placeOrder — сюди правило додали першим, повністю
let net = product.price * qty * (1 - discount);
if (net < regionFloor(region)) net = regionFloor(region);   // поріг: є
const total = net * (1 + regionTax(region));                // податок: є

// changeQty — переносили другим, поріг ЗАБУЛИ
let net2 = line.price * newQty * (1 - discount);
const total2 = net2 * (1 + regionTax(region));              // податок: є, поріг: НЕМАЄ

// reorder — руки не дійшли: стара формула, БЕЗ податку й порогу
const total3 = line.price * qty * (1 - discount);           // ані податку, ані порогу
```
```py
# place_order — сюди правило додали першим, повністю
net = product.price * qty * (1 - discount)
if net < region_floor(region): net = region_floor(region)   # поріг: є
total = net * (1 + region_tax(region))                      # податок: є

# change_qty — переносили другим, поріг ЗАБУЛИ
net2 = line.price * new_qty * (1 - discount)
total2 = net2 * (1 + region_tax(region))                    # податок: є, поріг: НЕМАЄ

# reorder — руки не дійшли: стара формула, БЕЗ податку й порогу
total3 = line.price * qty * (1 - discount)                  # ані податку, ані порогу
```
:::

Придивіться, у чому саме підступ. **Жоден із трьох сценаріїв не зламаний.** Кожен читається згори вниз, кожен внутрішньо послідовний, кожен закриває свою транзакцію бездоганно — `commit` доводить усі зміси до бази атомарно. Але одне й те саме замовлення, проведене крізь троє дверей, дає **три різні підсумки**: створив на 100 — податок і поріг враховано; змінив кількість — податок є, поріг зник, знижка раптом проходить під мінімум; повторив замовлення — рахунок як торік, без податку зовсім. Клієнт бачить, що зміна кількості на ту саму цифру «магічно» здешевлює замовлення, і має рацію.

Ось точка, яку найважче побачити самому: **транзакція захищає запис, а не правило.** Гарантія «усе або ніщо» ([що саме вона обіцяє](book:programming/transactions-acid) — атомарність, узгодженість, ізольованість, тривкість) стежить, щоб на диск не потрапив половинчастий стан. Вона нічого не знає про те, що три ваші сценарії розуміють «правильну ціну» по-різному. Кожен із них чесно й атомарно записує **свою** версію істини. Баг не в межі транзакції — вона ідеальна; баг у тому, що істин стало три. Це рівно те [дублювання, яке розходиться нечутно](book:programming/dry-kiss-yagni): копії правила ніхто не тримає синхронними, і кожна забута гілка — тихий баг, який спливе рахунком клієнта, а не падінням тесту.

## Рятунок перший: винести правило у власну підпроцедуру

Найдешевший хід очевидний і правильний: якщо алгоритм ціни повторюється — витягнути його в одну функцію, а три сценарії хай кличуть її. Знижку ми так уже зробили; тепер те саме для всього правила.

:::tabs
```ts
type Priced = { total: number; discount: number };

// чиста функція: жодної бази, лише правило ціни в одному місці
function priceOrder(unitPrice: number, qty: number, discount: number, region: string): Priced {
  const subtotal = unitPrice * qty;
  let net = subtotal * (1 - discount);
  const floor = regionFloor(region);
  if (net < floor) {                        // поріг тепер існує РІВНО ТУТ
    net = floor;
    discount = subtotal > 0 ? 1 - floor / subtotal : 0;   // підрізана знижка
  }
  const total = net * (1 + regionTax(region));
  return { total, discount };
}

// усі три сценарії тепер кличуть одне:
const { total } = priceOrder(product.price, qty, await loyaltyDiscount(tx, customerId), region);
```
```py
from dataclasses import dataclass

@dataclass
class Priced:
    total: float
    discount: float

# чиста функція: жодної бази, лише правило ціни в одному місці
def price_order(unit_price: float, qty: int, discount: float, region: str) -> Priced:
    subtotal = unit_price * qty
    net = subtotal * (1 - discount)
    floor = region_floor(region)
    if net < floor:                         # поріг тепер існує РІВНО ТУТ
        net = floor
        discount = 1 - floor / subtotal if subtotal > 0 else 0.0  # підрізана знижка
    total = net * (1 + region_tax(region))
    return Priced(total=total, discount=discount)

# усі три сценарії тепер кличуть одне:
priced = price_order(product.price, qty, loyalty_discount(tx, customer_id), region)
```
:::

Розходження зачинено: гілку з порогом фізично неможливо «забути в одному зі сценаріїв», бо гілка одна на всіх. Для величезної частки випадків на цьому й слід зупинитися — не кожне повторюване правило заслуговує на об'єкт, і витягнута функція розв'язує проблему тут і зараз, коштуючи один рядок сигнатури.

Але придивімося, де ця функція починає рипіти, бо саме рип підкаже наступний крок. По-перше, **сигнатура обростає хвостом**. Додався купон — `priceOrder(price, qty, discount, region, coupon)`. Перше замовлення дає бонус — ще параметр. Валюта, ваучер, оптова знижка від кількості — і от у виклику вже сім аргументів, половина з яких у більшості сценаріїв `null`, а порядок їх ніхто не пам'ятає. По-друге, тонше: функція **радить** правило, але не може його **нав'язати**. Ніщо не заважає комусь у четвертому сценарії — у `refund`, який писатимуть за півроку, — знову набрати руками `price * qty * (1 - discount)`, бо «тут же просто, навіщо тягнути функцію». Чиста функція — це доступна порада, а не сторож. Вона тримає правило в одному місці рівно доти, доки всі добровільно ходять через неї.

## Рятунок другий: дати правилу власника

Коли обидва рипи чути одночасно — параметрів забагато, а нав'язати правило нічим, — настає момент перенести його з функції в **об'єкт, який ним володіє**. Не в порожню торбину полів, а в об'єкт, що приймає сирі дані, **сам перевіряє їх у конструкторі** й далі просто **є** правильним замовленням або не будується взагалі. Це перший, найменший крок до [предметної моделі](book:programming/domain-model): один об'єкт, у якому дані й правило зрослися, — і те саме, що принцип [«кажи, не питай»](book:programming/tell-dont-ask) велить робити завжди, класти поведінку туди, де живуть її дані.

:::tabs
```ts
interface OrderInput {
  productId: number; qty: number; unitPrice: number; stock: number;
  discount: number; region: string;
}

class Order {
  readonly total: number;
  readonly discount: number;
  readonly lines: { productId: number; qty: number; price: number }[];

  constructor(i: OrderInput) {
    // інваріанти перевіряються ОДИН раз — у мить народження об'єкта
    if (i.qty < 1) throw new Error("кількість має бути ≥ 1");
    if (i.stock < i.qty) throw new Error("недостатньо на складі");

    const subtotal = i.unitPrice * i.qty;
    let net = subtotal * (1 - i.discount);
    const floor = regionFloor(i.region);
    // інваріант, що ЗЧІПЛЯЄ поля: чиста сума ніколи не нижча за поріг регіону
    this.discount = net < floor ? (subtotal > 0 ? 1 - floor / subtotal : 0) : i.discount;
    net = Math.max(net, floor);
    this.total = net * (1 + regionTax(i.region));
    this.lines = [{ productId: i.productId, qty: i.qty, price: i.unitPrice }];
  }
}
```
```py
from dataclasses import dataclass, field

@dataclass
class OrderInput:
    product_id: int; qty: int; unit_price: float; stock: int
    discount: float; region: str

class Order:
    def __init__(self, i: OrderInput):
        # інваріанти перевіряються ОДИН раз — у мить народження об'єкта
        if i.qty < 1:
            raise ValueError("кількість має бути ≥ 1")
        if i.stock < i.qty:
            raise ValueError("недостатньо на складі")

        subtotal = i.unit_price * i.qty
        net = subtotal * (1 - i.discount)
        floor = region_floor(i.region)
        # інваріант, що ЗЧІПЛЯЄ поля: чиста сума ніколи не нижча за поріг регіону
        self.discount = (1 - floor / subtotal if subtotal > 0 else 0) if net < floor else i.discount
        net = max(net, floor)
        self.total = net * (1 + region_tax(i.region))
        self.lines = [{"product_id": i.product_id, "qty": i.qty, "price": i.unit_price}]
```
:::

Тепер сценарій змінюється до невпізнанності — і водночас лишається сценарієм транзакції. Він далі читає рядки, далі володіє межею транзакції, далі пише й комітить; але **рахунок і перевірки віддано об'єкту**. Ось `placeOrder` у новому вигляді:

:::tabs
```ts
async function placeOrder(customerId: string, productId: number, qty: number): Promise<number> {
  const tx = await db.begin();                          // ── МЕЖА ТРАНЗАКЦІЇ лишилась у сценарії
  try {
    const product = await tx.get("SELECT price, stock FROM products WHERE id = ?", productId);
    if (!product) throw new Error("немає такого товару");
    const customer = await tx.get("SELECT region FROM customers WHERE id = ?", customerId);
    const discount = await loyaltyDiscount(tx, customerId);

    const order = new Order({                            // об'єкт рахує й перевіряє — БЕЗ бази
      productId, qty, unitPrice: product.price, stock: product.stock,
      discount, region: customer.region,
    });

    const { lastID: orderId } = await tx.run(
      "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, 'new')",
      customerId, order.total);
    for (const l of order.lines)
      await tx.run("INSERT INTO order_lines (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
        orderId, l.productId, l.qty, l.price);
    await tx.run("UPDATE products SET stock = stock - ? WHERE id = ?", qty, productId);

    await tx.commit();                                  // ── межа закривається тут-таки
    return orderId;
  } catch (e) { await tx.rollback(); throw e; }
}
```
```py
def place_order(customer_id: str, product_id: int, qty: int) -> int:
    tx = db.begin()                                     # ── МЕЖА ТРАНЗАКЦІЇ лишилась у сценарії
    try:
        product = tx.execute(
            "SELECT price, stock FROM products WHERE id = ?", (product_id,)).fetchone()
        if product is None:
            raise ValueError("немає такого товару")
        customer = tx.execute(
            "SELECT region FROM customers WHERE id = ?", (customer_id,)).fetchone()
        discount = loyalty_discount(tx, customer_id)

        order = Order(OrderInput(                        # об'єкт рахує й перевіряє — БЕЗ бази
            product_id=product_id, qty=qty, unit_price=product.price,
            stock=product.stock, discount=discount, region=customer.region))

        cur = tx.execute(
            "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, 'new')",
            (customer_id, order.total))
        order_id = cur.lastrowid
        for l in order.lines:
            tx.execute(
                "INSERT INTO order_lines (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
                (order_id, l["product_id"], l["qty"], l["price"]))
        tx.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, product_id))

        tx.commit()                                     # ── межа закривається тут-таки
        return order_id
    except Exception:
        tx.rollback(); raise
```
:::

`changeQty` і `reorder` тепер теж будують `Order` зі своїх рядків і читають `order.total`. І тут — ключова перевага над чистою функцією: об'єкт **нав'язує** [інваріант](book:programming/invariants), а не радить його. Немає способу отримати `Order`, у якого чиста сума впала під поріг або кількість менша за одиницю: конструктор або збудує коректний об'єкт, або кине виняток. Правило перестало бути порадою, до якої ходять добровільно, — воно стало умовою існування об'єкта. Той майбутній `refund`, автор якого захотів би зрізати кут, більше не може набрати формулу руками повз правило: щоб отримати підсумок, він мусить збудувати `Order`, а `Order` рахує правильно за визначенням.

![Три стадії однієї логіки. Стадія 0: три сценарії placeOrder, changeQty, reorder, у кожному своя копія правила, і копії розходяться. Стадія 1: три сценарії кличуть одну спільну функцію priceOrder — копії зійшлися, але функція обростає параметрами й лише радить правило. Стадія 2: три сценарії будують один об'єкт Order, що володіє правилом і нав'язує інваріант у конструкторі](img/rescue-ladder.svg)

*Та сама логіка ціни на трьох стадіях зрілості. Ліворуч — копії, що розходяться: одна зміна правила означає три правки, одну з яких забувають. Посередині — спільна функція: копії зійшлися в одне місце, але сигнатура обростає хвостом, а правило можна оминути. Праворуч — власник: правило й дані зрослися в об'єкт, інваріант перевіряється раз у конструкторі, і оминути його вже нічим.*

## Коли саме розбирати сценарій в об'єкт

Спокуса, побачивши цей фінал, — розбирати в об'єкти геть усе й одразу. Не треба: кожна з трьох стадій — правильна відповідь для свого рівня складності, і перескакувати через дешеву стадію на дорогу — це наперед сплачена ціна ні за що, рівно та [передчасність, від якої застерігає YAGNI](book:programming/dry-kiss-yagni). Ось три сигнали, кожен із яких зчитується з коду, а не з календаря, і які кажуть, коли переходити далі.

**Порахуй, скільки сценаріїв доведеться відкрити, коли зміниться одне правило.** Один сценарій на правило — тримайся сценарію, жодного об'єкта. Кілька копій того самого виразу, які поки що однакові, — витягни функцію (стадія 1). Але коли зміна ставки податку означає редагувати `placeOrder`, `changeQty`, `reorder` і ще пів десятка, а частина з них уже встигла розійтися в деталях, — копіювати нема сенсу, треба спільний дім.

**Подивись, чи має правило інваріант, що зчіпляє кілька полів.** Якщо «правильність» — це просто формула, яку рахують в одному напрямку, її вистачить тримати чистою функцією. Але щойно з'являється умова виду «це поле не може суперечити тому» — знижка не нижча за поріг, сума рядків дорівнює підсумку, статус і оплата узгоджені, — цю умову хтось мусить **стерегти в одному місці й на вході**, інакше кожен сценарій стереже її по-своєму або не стереже зовсім. Стерегти інваріанти — робота об'єкта, не функції.

**Послухай, чи росте хвіст параметрів.** Коли спільна функція починає брати сьомий аргумент, половина з яких `null`, це сигнатура кричить, що в неї запхали стан, який просився бути полями об'єкта. Згрупуй ці аргументи в об'єкт-вхід — і правило природно переїде в конструктор.

Коли жоден сигнал не дзвонить — не розбирай. Сценарій транзакції з винесеними підпроцедурами покриває більшість внутрішніх сервісів і адмінок так, що краще не буває: просто, читомо, дешево. Розбирати варто рівно тоді, коли **сама логіка** — розходження копій, інваріант між полями, роздутий хвіст — тобі про це скаже.

## Складність і пастки

**Межа транзакції лишається у сценарії — завжди.** Найспокусливіша помилка після народження `Order` — засунути в нього `commit`, а то й самі `INSERT`. Не роби цього. Об'єкт правила не має знати про базу: він приймає числа, повертає числа, кидає винятки — і все. Транзакцією, читанням і записом володіє сценарій. Щойно об'єкт починає сам ходити в базу, ти втрачаєш і легкість тесту (правило вже не перевірити без бази), і чисту межу транзакції, і саме розділення, заради якого все затівалося.

**Половинчаста міграція — гірша за жодну.** Якщо завести класи `Order`, `Customer`, `Product`, але лишити всі правила у сценаріях, вийде [анемічна модель](book:programming/anemic-domain-model): усі витрати об'єктів (класи, мапінг) і жодного зиску (логіка все одно зовні). Переносиш правило в об'єкт — переноси його **разом з інваріантом і перевірками**, щоб об'єкт справді ним володів. Порожня торба полів — не крок до предметної моделі, а гроші на вітер.

**Не тягни в об'єкт того, що ним не володіє.** `Order` рахує ціну й стереже свої інваріанти — але списання залишку (`UPDATE products SET stock = stock - ?`) і гонки навколо нього лишаються транзакційною роботою сценарію, бо це вже не про «правильне замовлення», а про узгодженість двох рядків у базі. Проведи межу чесно: об'єктові — правило й інваріанти сутності, сценарію — послідовність кроків, читання-запис і транзакцію.

**Пам'ятай, що назад дорога довша.** Розібрати сценарій в об'єкт помітно легше, ніж потім збирати назад: коли логіка вже розповзлася десятком сценаріїв і розійшлася в деталях, зшити її в модель — важча робота, ніж було б винести правило вчасно. Тому, відчувши перший із трьох сигналів, не відкладай другий крок надовго — рип чистої функції легко перерости, а розхід копій наздоганяє тихо й дорого.

Уся ця драбина — не про те, що сценарій транзакції «поганий», а об'єкт «хороший». Одна чиста процедура — правильний початок; винесена підпроцедура — правильний наступний крок; об'єкт-власник — правильний крок після нього. Помилка не в тому, щоб узяти сценарій, а в тому, щоб лишитися на стадії, яку логіка вже переросла, — і платити за це трьома підсумками на одне замовлення.
