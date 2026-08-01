# ⚙️ Багата модель, зібрана руками: замовлення як розмова об'єктів

Найшвидший спосіб відчути, чим багата предметна модель відрізняється від купки класів із правильними назвами, — зібрати таку модель самому, маленьку, але повну, і провести крізь неї один-єдиний випадок: **оформлення замовлення**. Ми виростимо її знизу вгору — від найдрібнішого [об'єкта-значення](book:programming/entity-value-object) `Money` до сутності `Order`, що стереже власний життєвий цикл, — і побачимо, як операція «оформити» перестає бути процедурою, що читає таблиці, і стає короткою розмовою кількох об'єктів, кожен з яких відповідає лише за своє. А в кінці поставимо модель на найсуворіший іспит: прогонимо всю її ділову логіку **в пам'яті, без бази й без жодного мока**.

Правила візьмемо конкретні. Замовлення складається з позицій; кожна позиція — це товар і кількість. Ціну фіксуємо в мить додавання (товар потім подорожчає — оформлене замовлення це вже не обходить). Постійний клієнт дістає знижку. Товар, доданий у замовлення, резервують на складі. І саме замовлення живе своїм життям: `чернетка → оформлене → відвантажене`, з відгалуженням у `скасоване`, — і не кожен перехід між цими станами дозволений.

Питання, з якого все починається: **де живе кожне з цих правил?** Багата модель відповідає на всі однаково — правило живе в тому об'єкті, чиї дані воно чіпає. Тож зберемо об'єкти й рознесемо правила по їхніх природних власниках. Код тут — звичайна ділова логіка, тож пишемо мовами, якими її й пишуть: C++ показує сильну семантику значень і справжню інкапсуляцію, TypeScript — мейнстрімний ідіом бекенду.

## Гроші — найменший об'єкт, у якого вже є характер

Почнімо з грошей, бо в них немає жодної тотожності — і саме тому вони найкраще показують, що таке об'єкт-значення. Дві п'ятигривневі монети взаємозамінні: немає «цієї конкретної п'ятірки», є просто «п'ять гривень». Значить, і `Money` не має особи: два об'єкти рівні, якщо рівний їхній вміст, і один можна будь-коли підмінити іншим. З цього випливають три його риси, і кожна закриває окремий клас помилок.

Гроші **незмінні**: операція над ними не псує старе значення, а народжує нове. Гроші тримають **ціле число копійок**, а не дріб із плавучою комою — бо `0.1 + 0.2` у двійковому дробі не дорівнює `0.3`, і копійка, розмита похибкою, з часом розсипає баланс. І гроші стережуть **інваріант**: сума не буває від'ємна, а складати різні валюти не можна. Вартовий цих правил стоїть у фабриці, повз яку об'єкт не створити.

:::tabs
```cpp
#include <string>
#include <vector>
#include <optional>
#include <cstdint>
#include <stdexcept>

struct DomainError : std::runtime_error {
    using std::runtime_error::runtime_error;
};

using Cents = std::int64_t;                       // копійки цілим числом, не дріб

class Money {
public:
    // єдині двері всередину — з вартовим: гроші не бувають від'ємні
    static Money of(Cents cents, std::string currency) {
        if (cents < 0) throw DomainError("гроші не бувають від'ємні");
        return Money(cents, std::move(currency));
    }
    static Money zero(std::string currency) { return Money(0, std::move(currency)); }

    Money add(const Money& o) const {
        requireSameCurrency(o);
        return Money(cents_ + o.cents_, currency_);        // новий об'єкт, старі не змінені
    }
    Money times(int qty) const {
        if (qty < 0) throw DomainError("кількість не буває від'ємна");
        return Money(cents_ * qty, currency_);
    }
    Money withDiscountPercent(int pct) const {
        if (pct < 0 || pct > 100) throw DomainError("відсоток поза межами 0..100");
        return Money(cents_ - cents_ * pct / 100, currency_);
    }

    bool operator==(const Money& o) const {                // рівність за ВМІСТОМ — рідна мові
        return cents_ == o.cents_ && currency_ == o.currency_;
    }
    Cents cents() const { return cents_; }
    const std::string& currency() const { return currency_; }

private:
    Money(Cents cents, std::string currency)               // конструктор закритий
        : cents_(cents), currency_(std::move(currency)) {}
    void requireSameCurrency(const Money& o) const {
        if (currency_ != o.currency_) throw DomainError("не можна складати різні валюти");
    }
    Cents cents_;
    std::string currency_;
};
```
```ts
class DomainError extends Error {}

class Money {
  private constructor(
    readonly cents: number,            // копійки цілим числом, не дріб
    readonly currency: string,
  ) {}

  // єдині двері всередину — з вартовим: гроші не бувають від'ємні
  static of(cents: number, currency: string): Money {
    if (!Number.isInteger(cents)) throw new DomainError("копійки мусять бути цілим числом");
    if (cents < 0) throw new DomainError(`гроші не бувають від'ємні: ${cents}`);
    return new Money(cents, currency);
  }
  static zero(currency: string): Money { return new Money(0, currency); }

  add(o: Money): Money {
    this.requireSameCurrency(o);
    return new Money(this.cents + o.cents, this.currency);  // новий об'єкт, старі не змінені
  }
  times(qty: number): Money {
    if (!Number.isInteger(qty) || qty < 0) throw new DomainError("кількість — ціле невід'ємне");
    return new Money(this.cents * qty, this.currency);
  }
  withDiscountPercent(pct: number): Money {
    if (pct < 0 || pct > 100) throw new DomainError("відсоток поза межами 0..100");
    return new Money(this.cents - Math.trunc(this.cents * pct / 100), this.currency);
  }

  equals(o: Money): boolean {              // рівність за ВМІСТОМ — руками, бо оператора нема
    return this.cents === o.cents && this.currency === o.currency;
  }
  private requireSameCurrency(o: Money): void {
    if (this.currency !== o.currency) throw new DomainError("не можна складати різні валюти");
  }
}
```
:::

Одна відмінність між вкладками не косметична, і вона показує, за що тут відповідає мова. У C++ рівність за вмістом — рідна: `operator==` робить `Money` повноцінним значенням, яке можна порівнювати `==`, класти в контейнер, передавати копією майже задарма. У TypeScript оператор перевантажити не можна, тож рівність доводиться писати методом `equals`, а `===` над двома `Money` порівняв би **посилання** — тобто збрехав би, що два однакові гроші різні. Семантику значень C++ дає, TypeScript її дисципліновано вдає — і про цю дисципліну треба пам'ятати щоразу.

> 🔧 **Навіщо це.** Об'єкт-значення здається церемонією над одним числом, а насправді він разом виполює три сімейства багів. Незмінність убиває **розділене посилання**: передав `Money` у три місця — жодне не зіпсує його іншим двом, бо змінити його нема як. Ціла копійка вбиває **похибку дробу** — баланс сходиться до копійки й через рік. Вартовий у фабриці вбиває **від'ємні й різновалютні гроші** в зародку — стан, який деінде довелося б ловити перевірками. А рівність за вмістом робить гроші **тривіально тестованими**: очікуване значення — це просто ще один `Money`, зібраний руками, і звірка проходить одним порівнянням.

## Сутність відрізняється від значення тим, що має особу

`Order` — інша порода об'єкта. Двоє замовлень з тим самим списком позицій — це **не** одне замовлення: у кожного свій номер, своя доля, свій рахунок. Тут тотожність — не за вмістом, а за `id`, і вона переживає будь-яку зміну вмісту: додав позицію, оформив, відвантажив — це те саме замовлення, просто в іншому стані. Об'єкт, чия суть — тривати в часі й міняти стан, зберігаючи особу, звуть **сутністю** (англ. *entity*), на противагу об'єктові-значенню, у якого стану, що тече, немає взагалі.

![Дві панелі. Ліворуч «об'єкт-значення»: два однакові прямокутники Money 5.00 UAH зі знаком рівності між ними й підписом, що рівні за вмістом об'єкти взаємозамінні, незмінні, тотожності не мають. Праворуч «сутність»: два прямокутники Order з однаковим вмістом «1 × ноутбук», але різними номерами #A17 і #B42, між ними знак нерівності й підпис, що однаковий вміст за різних id дає різні замовлення, які мають стан і життєвий цикл](/book/programming/design-patterns/domain-model/img/value-vs-entity.svg)

*Дві природи об'єктів моделі. Значення рівні, коли рівний їхній вміст, — і тоді вони взаємозамінні, а міняти в них нема чого. Сутності рівні лише за тотожністю: два замовлення з однаковим вмістом однаково різні, бо в кожного свій номер і своя течія стану.*

Раз сутність тримає стан, що тече, головне питання про неї — **хто має право цей стан міняти**. Відповідь багатої моделі різка: ніхто ззовні. Поля приватні, сеттерів немає, а єдиний спосіб зрушити стан — покликати **метод-команду**, усередині якого сидить вартовий. Тому привести замовлення в стан, якого не буває в природі — відвантажене без оформлення, оформлене двічі, порожнє оформлене, — ззовні просто нема як: кожен такий хід упирається у виняток раніше, ніж встигне статися.

Складімо `Product`, `Customer` і `OrderLine`, з якими розмовлятиме замовлення. Кожен — маленький, кожен стереже рівно своє.

:::tabs
```cpp
enum class Tier { Regular, Gold };

class Product {                                  // сутність: свій id, свій стан складу
public:
    Product(std::string id, Money unitPrice, int stock)
        : id_(std::move(id)), unitPrice_(std::move(unitPrice)), stock_(stock) {
        if (stock < 0) throw DomainError("залишок не буває від'ємний");
    }
    const Money& price() const { return unitPrice_; }
    int stock() const { return stock_; }
    void reserve(int qty) {                      // метод-команда: товар сам стереже склад
        if (qty <= 0)       throw DomainError("резервувати можна лише додатну кількість");
        if (qty > stock_)   throw DomainError("на складі лише " + std::to_string(stock_));
        stock_ -= qty;
    }
    const std::string& id() const { return id_; }
private:
    std::string id_;
    Money unitPrice_;
    int stock_;
};

class Customer {                                 // сутність: свій рівень лояльності
public:
    Customer(std::string id, Tier tier) : id_(std::move(id)), tier_(tier) {}
    int discountPercent() const { return tier_ == Tier::Gold ? 10 : 0; }  // знає свій відсоток
    const std::string& id() const { return id_; }
private:
    std::string id_;
    Tier tier_;
};

class OrderLine {                                // всередині агрегату замовлення
public:
    OrderLine(std::string productId, Money unitPrice, int qty)
        : productId_(std::move(productId)), unitPrice_(std::move(unitPrice)), qty_(qty) {
        if (qty <= 0) throw DomainError("кількість у позиції має бути додатна");
    }
    Money subtotal() const { return unitPrice_.times(qty_); }   // рахує сам, знімком ціни
    const std::string& productId() const { return productId_; }
private:
    std::string productId_;                      // товар — за id, а не покажчиком
    Money unitPrice_;                            // знімок ціни на мить додавання
    int qty_;
};
```
```ts
type Tier = "regular" | "gold";

class Product {                                  // сутність: свій id, свій стан складу
  constructor(
    readonly id: string,
    private readonly unitPrice: Money,
    private _stock: number,
  ) {
    if (_stock < 0) throw new DomainError("залишок не буває від'ємний");
  }
  price(): Money { return this.unitPrice; }
  stock(): number { return this._stock; }
  reserve(qty: number): void {                   // метод-команда: товар сам стереже склад
    if (qty <= 0)            throw new DomainError("резервувати можна лише додатну кількість");
    if (qty > this._stock)   throw new DomainError(`на складі лише ${this._stock}`);
    this._stock -= qty;
  }
}

class Customer {                                 // сутність: свій рівень лояльності
  constructor(readonly id: string, private readonly tier: Tier) {}
  discountPercent(): number { return this.tier === "gold" ? 10 : 0; }  // знає свій відсоток
}

class OrderLine {                                // всередині агрегату замовлення
  constructor(
    readonly productId: string,                  // товар — за id, а не посиланням
    readonly unitPrice: Money,                   // знімок ціни на мить додавання
    readonly qty: number,
  ) {
    if (qty <= 0) throw new DomainError("кількість у позиції має бути додатна");
  }
  subtotal(): Money { return this.unitPrice.times(this.qty); }  // рахує сам, знімком ціни
}
```
:::

Зверни увагу на два рішення в `OrderLine`, бо вони тихо визначають межу цілого. По-перше, позиція тримає товар **за `productId`, а не покажчиком** на живий `Product` — це вже проведена межа між замовленням і товаром як окремими сутностями. По-друге, позиція тримає **знімок ціни** (`unitPrice`), скопійований у мить додавання, — тож `subtotal()` рахується з тієї ціни, що була тоді, і пізніша переоцінка товару оформленого замовлення не зачепить. Значення скопіювали в момент, коли воно було правдою, — і замкнули всередині.

## Життєвий цикл під вартою

Тепер сам `Order` — корінь, що зшиває позиції в одне ціле й береже свій стан. Його стан — це маленький автомат: `чернетка → оформлене → відвантажене`, з відгалуженням `→ скасоване` з перших двох станів. Кожна стрілка цього автомата — окремий метод-команда, а кожна **відсутня** стрілка — вартовий, що кидає виняток. Тому автомат не намальований у документації, а **вкований у код**: недозволеного переходу нема не тому, що про нього забули, а тому, що метод на нього відповідає відмовою.

![Автомат станів замовлення. Чотири стани: Чернетка, Оформлене, Відвантажене в ряд, Скасоване нижче. Суцільні стрілки — дозволені переходи, підписані методами: place від чернетки до оформленого, ship від оформленого до відвантаженого, cancel від чернетки та від оформленого до скасованого. Дві червоні штрихові стрілки з хрестиком — заборонені переходи: від чернетки прямо до відвантаженого й від відвантаженого до скасованого. Легенда: суцільна — метод-команда виконується; червона штрихова — вартовий усередині методу кидає DomainError](/book/programming/design-patterns/domain-model/img/order-lifecycle.svg)

*Життєвий цикл, вкований у методи-команди. Кожен дозволений перехід — окремий метод; кожен заборонений — вартовий, що відповідає винятком. Стан приватний, тож іншого шляху змінити його, ніж крізь ці двері з вартою, просто немає.*

:::tabs
```cpp
enum class Status { Draft, Placed, Shipped, Cancelled };

class Order {
public:
    Order(std::string id, std::string customerId)
        : id_(std::move(id)), customerId_(std::move(customerId)) {}

    // ── команди: єдиний спосіб зрушити стан, і в кожній — вартовий ──
    void addLine(Product& product, int qty) {
        if (status_ != Status::Draft)
            throw DomainError("позиції можна додавати лише чернетці");
        product.reserve(qty);                            // розмова з Product: хай стереже склад
        lines_.emplace_back(product.id(), product.price(), qty);
    }

    void place(const Customer& customer) {
        if (status_ != Status::Draft)
            throw DomainError("оформити можна лише чернетку");
        if (lines_.empty())
            throw DomainError("порожнє замовлення оформити не можна");

        Money sum = Money::zero(lines_.front().subtotal().currency());
        for (const OrderLine& line : lines_)
            sum = sum.add(line.subtotal());              // OrderLine рахує сам, Money додає сам
        total_ = sum.withDiscountPercent(customer.discountPercent());  // Customer дає свій відсоток
        status_ = Status::Placed;                        // інваріант циклу — під замком самого Order
    }

    void ship() {
        if (status_ != Status::Placed)
            throw DomainError("відвантажити можна лише оформлене замовлення");
        status_ = Status::Shipped;
    }

    void cancel() {
        if (status_ != Status::Draft && status_ != Status::Placed)
            throw DomainError("скасувати можна лише чернетку або оформлене");
        status_ = Status::Cancelled;
    }

    // ── запити ──
    Status status() const { return status_; }
    const Money& total() const {
        if (!total_) throw DomainError("підсумок з'являється лише в оформленого замовлення");
        return *total_;
    }
private:
    std::string id_;
    std::string customerId_;                             // клієнт — за id, а не покажчиком
    Status status_ = Status::Draft;
    std::vector<OrderLine> lines_;
    std::optional<Money> total_;                         // підсумку нема, доки не оформлено
};
```
```ts
type Status = "draft" | "placed" | "shipped" | "cancelled";

class Order {
  private _status: Status = "draft";
  private readonly _lines: OrderLine[] = [];
  private _total: Money | null = null;                   // підсумку нема, доки не оформлено

  constructor(
    readonly id: string,
    readonly customerId: string,                         // клієнт — за id, а не посиланням
  ) {}

  // ── команди: єдиний спосіб зрушити стан, і в кожній — вартовий ──
  addLine(product: Product, qty: number): void {
    if (this._status !== "draft")
      throw new DomainError("позиції можна додавати лише чернетці");
    product.reserve(qty);                                // розмова з Product: хай стереже склад
    this._lines.push(new OrderLine(product.id, product.price(), qty));
  }

  place(customer: Customer): void {
    if (this._status !== "draft")
      throw new DomainError("оформити можна лише чернетку");
    if (this._lines.length === 0)
      throw new DomainError("порожнє замовлення оформити не можна");

    const sum = this._lines
      .map(line => line.subtotal())                              // OrderLine рахує сам
      .reduce((a, b) => a.add(b), Money.zero(this.currency()));  // Money додає сам
    this._total = sum.withDiscountPercent(customer.discountPercent()); // Customer дає свій відсоток
    this._status = "placed";                             // інваріант циклу — під замком самого Order
  }

  ship(): void {
    if (this._status !== "placed")
      throw new DomainError("відвантажити можна лише оформлене замовлення");
    this._status = "shipped";
  }

  cancel(): void {
    if (this._status !== "draft" && this._status !== "placed")
      throw new DomainError("скасувати можна лише чернетку або оформлене");
    this._status = "cancelled";
  }

  // ── запити ──
  get status(): Status { return this._status; }
  total(): Money {
    if (this._total === null)
      throw new DomainError("підсумок з'являється лише в оформленого замовлення");
    return this._total;
  }
  private currency(): string { return this._lines[0].unitPrice.currency; }
}
```
:::

Придивись до `place` — це і є те, заради чого будувалася вся мережа. Замовлення **не рахує нічого саме**. Треба підсумок позиції — питає `OrderLine`, а той питає свій `Money`. Треба скласти суми — просить `Money` додатися до `Money`. Треба знижку — питає `Customer`, який один знає свій відсоток. `Order` лише диригує цією розмовою й наприкінці робить те єдине, що належить йому й нікому більше: перевіряє власний інваріант циклу і, якщо все гаразд, зрушує свій стан у `Placed`.

Прибери цей код — думка лишається цілою: операція розкладена по власниках даних, і кожен крок робить той, хто за дані відповідає. У цьому вся різниця з процедурою [сценарію транзакції](book:programming/transaction-script), яка сама пірнула б до всіх даних і зробила все власноруч. І в цьому ж — уся різниця з [анемічною моделлю](book:programming/anemic-domain-model): якби `Order` лише віддавав назовні `lines` і `status`, а рахував і міняв стан хтось інший, ми дістали б ту саму процедуру, тільки вбрану в об'єктний костюм.

## Шов, за який модель не зазирає

Модель готова, і в ній є прикметна порожнеча: **ніде немає ані слова про базу**. Ні `SELECT`, ні таблиць, ні натяку, що ці об'єкти взагалі десь зберігають. Це не випадковість і не незакінченість — це головна дисципліна патерну, [непроникність для збереження](book:programming/data-mapper) (англ. *persistence ignorance*): об'єкти моделі поводяться так, ніби живуть у пам'яті вічно, і про сховище не знають нічого.

Але дані ж мусять десь лежати між запусками. Раз сама модель про це не дбає, значить, дбає хтось поза нею. Цей хтось входить у модель крізь **шов** — інтерфейс сховища, названий мовою предмета, а не мовою бази. Модель (точніше, сервіс над нею) звертається до цього інтерфейсу як до звичайної колекції об'єктів, а що за ним стоїть — жива база, файл чи мапа в пам'яті — її не обходить.

:::tabs
```cpp
// ── порти: інтерфейси сховища, названі мовою предмета, не мовою SQL ──
struct OrderRepository {
    virtual ~OrderRepository() = default;
    virtual Order* byId(const std::string& id) = 0;      // nullptr, якщо нема
    virtual void   save(const Order& order)   = 0;
};

struct CustomerRepository {
    virtual ~CustomerRepository() = default;
    virtual const Customer* byId(const std::string& id) = 0;
};

// ── сервіс: тонка оркестрація — дістати, сказати одне слово, зберегти ──
class PlaceOrderService {
public:
    PlaceOrderService(OrderRepository& orders, CustomerRepository& customers)
        : orders_(orders), customers_(customers) {}

    void place(const std::string& orderId, const std::string& customerId) {
        Order* order = orders_.byId(orderId);
        if (!order) throw DomainError("немає замовлення " + orderId);
        const Customer* customer = customers_.byId(customerId);
        if (!customer) throw DomainError("немає клієнта " + customerId);

        order->place(*customer);          // домен вирішує все — сервіс лише передав слово
        orders_.save(*order);             // збереження живе ЗЗОВНІ моделі
    }
private:
    OrderRepository&    orders_;
    CustomerRepository& customers_;
};
```
```ts
// ── порти: інтерфейси сховища, названі мовою предмета, не мовою SQL ──
interface OrderRepository {
  byId(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}
interface CustomerRepository {
  byId(id: string): Promise<Customer | null>;
}

// ── сервіс: тонка оркестрація — дістати, сказати одне слово, зберегти ──
class PlaceOrderService {
  constructor(
    private readonly orders: OrderRepository,
    private readonly customers: CustomerRepository,
  ) {}

  async place(orderId: string, customerId: string): Promise<void> {
    const order = await this.orders.byId(orderId);
    if (!order) throw new DomainError(`немає замовлення ${orderId}`);
    const customer = await this.customers.byId(customerId);
    if (!customer) throw new DomainError(`немає клієнта ${customerId}`);

    order.place(customer);              // домен вирішує все — сервіс лише передав слово
    await this.orders.save(order);      // збереження живе ЗЗОВНІ моделі
  }
}
```
:::

Уся суть шва — у напрямі залежностей. `Order` не залежить ні від чого. `PlaceOrderService` залежить від `Order` і від **інтерфейсу** сховища. А конкретна реалізація на SQL залежатиме від того самого інтерфейсу — тобто вказує стрілкою вгору, до моделі, а не навпаки. Модель сидить у центрі й нічого під собою не знає; що саме мостить її до пласких таблиць — [репозиторій](book:programming/repository) поверх [мапера даних](book:programming/data-mapper) — вирішується поза нею, і його можна замінити, не торкнувшись жодного правила. Сервіс же лишається чесною оркестрацією: дістав об'єкт, сказав йому одне слово, зберіг. Уся думка — у слові `place`, а воно живе в самому об'єкті.

## Уся логіка — у пам'яті, без бази й моків

Тепер винагорода за дисципліну. Раз модель не знає про базу, її й перевіряти можна без бази — просто зібравши об'єкти конструкторами, покликавши операцію й звіривши підсумковий стан. Ні Postgres, ні схеми, ні контейнера, ні жодного мока: усе, що є в тесті, — це самі об'єкти предмета.

:::tabs
```cpp
#include <cassert>
#include <functional>
#include <iostream>

static bool throwsDomain(const std::function<void()>& fn) {
    try { fn(); } catch (const DomainError&) { return true; }
    return false;
}

int main() {
    // 1. постійний клієнт дістає знижку, а склад меншає
    {
        Product laptop("SKU-1", Money::of(3'000'000, "UAH"), 5);   // 30 000.00, 5 шт
        Customer gold("C-1", Tier::Gold);

        Order order("O-1", "C-1");
        order.addLine(laptop, 2);
        order.place(gold);

        assert(order.status() == Status::Placed);
        assert(order.total() == Money::of(5'400'000, "UAH"));      // 60 000 − 10%
        assert(laptop.stock() == 3);                               // 5 − 2
    }
    // 2. вартові не пускають неможливий стан
    {
        Customer reg("C-1", Tier::Regular);

        Order empty("O-2", "C-1");
        assert(throwsDomain([&]{ empty.place(reg); }));            // порожнє оформити не можна

        Product p("SKU-1", Money::of(1000, "UAH"), 10);
        Order order("O-3", "C-1");
        order.addLine(p, 1);
        assert(throwsDomain([&]{ order.ship(); }));                // чернетку не відвантажити
        order.place(reg);
        assert(throwsDomain([&]{ order.place(reg); }));            // оформити двічі — не можна
    }
    std::cout << "усі перевірки пройдено — і жодної бази поруч\n";
    return 0;
}
```
```ts
describe("оформлення замовлення — уся логіка в пам'яті", () => {
  it("постійний клієнт дістає знижку, а склад меншає", () => {
    const laptop = new Product("SKU-1", Money.of(3_000_000, "UAH"), 5);  // 30 000.00, 5 шт
    const gold = new Customer("C-1", "gold");

    const order = new Order("O-1", "C-1");
    order.addLine(laptop, 2);
    order.place(gold);

    expect(order.status).toBe("placed");
    expect(order.total().equals(Money.of(5_400_000, "UAH"))).toBe(true);  // 60 000 − 10%
    expect(laptop.stock()).toBe(3);                                       // 5 − 2
  });

  it("вартові не пускають неможливий стан", () => {
    const reg = new Customer("C-1", "regular");

    const empty = new Order("O-2", "C-1");
    expect(() => empty.place(reg)).toThrow(DomainError);        // порожнє оформити не можна

    const order = new Order("O-3", "C-1");
    order.addLine(new Product("SKU-1", Money.of(1000, "UAH"), 10), 1);
    expect(() => order.ship()).toThrow(DomainError);           // чернетку не відвантажити
    order.place(reg);
    expect(() => order.place(reg)).toThrow(DomainError);       // оформити двічі — не можна
  });
});
```
:::

Цей тест не звертається до `PlaceOrderService` й до репозиторіїв узагалі — і не має до них звертатися. Ділова логіка вся сидить у моделі, а модель у пам'яті повна: `addLine`, `place`, `ship`, `cancel`, знижка, резерв, кожен вартовий — усе перевіряється конструкторами й прямими викликами. Перевіряти сам шов збереження — окрема робота, і робиться вона [підробкою-репозиторієм у пам'яті проти контракт-набору](book:programming/repository/proj-in-memory-repository.md), а не моками: реальний репозиторій і його підробка ганяються тим самим набором тестів, тож підробці можна вірити рівно доти, доки набір зелений на обох.

> 🔧 **Навіщо це.** Непроникність для збереження оплачується найдорожчою в розробці валютою — швидкістю тестів. Модель, що не знає про базу, дає перевірити всю ділову логіку **за мілісекунди, без бази й без моків**: зібрав об'єкти, покликав операцію, звірив стан. Тому багатий предмет із сотнями правил можна ганяти тисячами тестів, що пробігають за секунду, — а це саме те, що дозволяє безстрашно міняти складну логіку. Щойно ж у модель протече `SELECT`, кожен тест потягне за собою базу, набір ставатиме хвилинами, і його перестануть ганяти на кожну зміну — а нетестована складна логіка гниє найшвидше. Тому тест, що біжить без бази, — це не зручність, а **доказ**, що модель чиста: не можеш перевірити правило без Postgres — правило вже витекло з моделі.

## Три пастки, у які провалюються найчастіше

**Межі агрегату.** У нашій моделі `Order` разом зі своїми `OrderLine` — це один [агрегат](book:programming/aggregates-consistency): гроно об'єктів, які живуть і вмирають разом і мусять бути узгоджені як ціле, з коренем `Order` за єдині двері всередину. А `Product` і `Customer` — **інші** агрегати, тож `Order` і тримає їх за `id`, а не покажчиком. Але одне місце цю межу порушує, і його треба назвати вголос: `addLine` кличе `product.reserve(qty)` — тобто в одному подиху міняє **два** агрегати, замовлення і товар. Практичне правило радить протилежне: одна транзакція чіпає один агрегат, а зв'язок між агрегатами зводить пізніше, іноді з відкладеною узгодженістю. Для навчального моноліту прямий резерв простий і чесний; у системі, де склад — окрема служба, `reserve` став би окремою операцією над агрегатом товару, а не рядком усередині `addLine`. Пастка не в тому, що ми обрали простіше, а в тому, щоб обрати це, **не помітивши межі**.

**Зісковзування в анемію.** Багату модель тягне назад до анемії безперервно, і рух завжди однаковий. Спершу хтось додає невинний геттер: «мені лише прочитати `lines`». Потім поруч заводиться сервіс, що цим геттером користується — «зручніше порахувати підсумок тут». І ось правило вже живе не в об'єкті, а в сервісі:

```ts
// ЗАПАХ анемії: об'єкт лише віддає поля, а рахує й вирішує хтось інший
class Order { lines: OrderLine[] = []; status = "draft"; }         // самі дані, жодного правила

class OrderService {
  place(order: Order, customer: Customer) {
    if (order.lines.length === 0) throw new Error("порожнє");      // інваріант утік сюди
    order.status = "placed";                                       // і перехід стану — теж
    // ...і підсумок сервіс рахує сам, лізучи в order.lines
  }
}
```

Це знову [сценарій транзакції](book:programming/transaction-script), тільки прикидається об'єктом: усі витрати на класи є, а зиску нема, бо правило розсипане по викликачах і одну його копію рано чи пізно проґавлять. Межа між «завів об'єкти» і «оживив об'єкти» проходить рівно по тому, чи **переселилися правила всередину**. Простий гейт проти сповзання: якщо поле віддається геттером **лише для того, щоб хтось зовні над ним щось вирішив**, — це правило кличе додому, в об'єкт.

**Тримати модель чистою.** Остання спокуса — дозволити збереженню протекти в саму сутність: дописати `Order` метод `save()`, повісити на поля анотації сховища, підмішати в конструктор клієнт бази. `save()` на об'єкті — це вже інший патерн, [активний запис](book:programming/active-record), законний для простої моделі, схожої на таблиці, але згубний для багатої: сутність, що знає про власне збереження, більше не проженеш у пам'яті без бази, і перша ж пастка з цього списку — тест без Postgres — перестане бути можливою. Спосіб тримати межу простий і перевіряється механічно: модель мусить збиратися й працювати, маючи в оточенні лише саму себе — жодного `import` бази, драйвера чи фреймворку. Щойно `new Order(...)` вимагає підключення до сховища, чистота вже втрачена — і разом з нею втрачено все, заради чого багату модель будували.

Отже, живий доказ, що модель багата, а не лише названа правильними іменами, — це не діаграма класів, а той короткий тест, що зібрав `Order`, `Product`, `Money` голими руками, покликав `place` і звірив підсумок, жодного разу не торкнувшись бази. Якщо він пишеться легко — правила справді переселилися в об'єкти. Якщо ні — вони й досі десь зовні, хай навіть класи з правильними назвами вже стоять на місці.
