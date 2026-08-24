# ⚙️ Охорона й кеш поверх сервісу — один заступник, нуль правок оригіналу

Візьмімо сервіс, який справді хочеться поставити під нагляд, — `OrderService`, доступ до замовлень. У нього три методи, і кожен цінний по-своєму:

:::tabs
```ts
interface OrderService {
  getOrder(id: string): Order;           // читання: часте, безпечне, добре кешується
  placeOrder(order: Order): string;      // запис: створює замовлення, треба право
  cancelOrder(id: string): void;         // запис: скасовує, треба право (та ще й вище)
}

// Справжній сервіс: ходить у базу, нічого не знає про права й кеш.
class RealOrderService implements OrderService {
  getOrder(id: string): Order {
    return db.query("SELECT ... WHERE id = ?", id);   // дорогий похід у базу
  }
  placeOrder(order: Order): string {
    return db.insert(order);
  }
  cancelOrder(id: string): void {
    db.update("UPDATE orders SET state='cancelled' WHERE id = ?", id);
  }
}
```
```py
from typing import Protocol

class OrderService(Protocol):
    def get_order(self, id: str) -> "Order": ...        # читання: часте, безпечне, кешується
    def place_order(self, order: "Order") -> str: ...   # запис: треба право
    def cancel_order(self, id: str) -> None: ...        # запис: треба право (вище)

# Справжній сервіс: ходить у базу, нічого не знає про права й кеш.
class RealOrderService:
    def get_order(self, id: str) -> "Order":
        return db.query("SELECT ... WHERE id = ?", id)   # дорогий похід у базу

    def place_order(self, order: "Order") -> str:
        return db.insert(order)

    def cancel_order(self, id: str) -> None:
        db.update("UPDATE orders SET state='cancelled' WHERE id = ?", id)
```
```java
interface OrderService {
    Order getOrder(String id);            // читання: часте, безпечне, кешується
    String placeOrder(Order order);       // запис: треба право
    void cancelOrder(String id);          // запис: треба право (вище)
}

// Справжній сервіс: ходить у базу, нічого не знає про права й кеш.
class RealOrderService implements OrderService {
    public Order getOrder(String id) {
        return db.query("SELECT ... WHERE id = ?", id);   // дорогий похід у базу
    }
    public String placeOrder(Order order) {
        return db.insert(order);
    }
    public void cancelOrder(String id) {
        db.update("UPDATE orders SET state='cancelled' WHERE id = ?", id);
    }
}
```
:::

Цей сервіс має бути **тупим і чистим**: узяв запит — сходив у базу — віддав. Ніякого «а чи можна цьому користувачеві», ніякого «а може, ми це вже питали хвилину тому». Домішати сюди перевірку прав означало б, що логіка замовлень і логіка безпеки зрослися в одному класі: правиш охорону — ризикуєш зачепити роботу з базою, і навпаки. А кеш усередині сервісу — це вже третя, зовсім чужа турбота в тому самому місці. Три різні відповідальності в одному класі — рецепт коду, який ніхто не наважується чіпати.

Хочеться додати і охорону, і облік — **не торкнувшись жодного рядка** `RealOrderService`. Саме це дає проксі: заступник із тим самим інтерфейсом `OrderService`, який клієнт отримує замість справжнього сервісу й навіть не здогадується про підміну. Складемо два таких заступники — захисний і розумне посилання, — покажемо, як їх ставлять один на одного, а тоді знімемо головний біль обох через динамічний проксі.

## Захисний проксі: право питаємо на кожен виклик

Задача захисного проксі проста на словах: **перед тим як пустити виклик до справжнього сервісу, спитати, чи має поточний користувач право на цю дію; немає права — кинути відмову, справжнього виклику не відбудеться взагалі.** Ідея — вставити цю перевірку в одну точку, спільну для всіх методів, а сам сервіс лишити недоторканим.

Заведімо мінімум інфраструктури: хто зараз діє (`currentUser`) і яке право потрібне для кожної дії. Читати замовлення може будь-хто залогінений; створювати — той, у кого є право `orders:write`; скасовувати — лише той, у кого `orders:cancel` (це небезпечніше, ніж просто створити).

:::tabs
```ts
class AccessDenied extends Error {}   // окремий тип, щоб клієнт міг його впіймати

class ProtectedOrderService implements OrderService {
  constructor(
    private real: OrderService,        // кого захищаємо (делегат)
    private user: User,                // від чийого імені йдуть виклики
  ) {}

  private require(permission: string): void {
    if (!this.user.can(permission)) {  // одна точка перевірки для всіх методів
      throw new AccessDenied(`${this.user.name}: немає права ${permission}`);
    }
  }

  getOrder(id: string): Order {
    this.require("orders:read");        // спершу право...
    return this.real.getOrder(id);      // ...тоді делегуємо
  }
  placeOrder(order: Order): string {
    this.require("orders:write");
    return this.real.placeOrder(order);
  }
  cancelOrder(id: string): void {
    this.require("orders:cancel");
    this.real.cancelOrder(id);
  }
}
```
```py
class AccessDenied(Exception):        # окремий тип, щоб клієнт міг його впіймати
    pass

class ProtectedOrderService:
    def __init__(self, real: OrderService, user: "User") -> None:
        self._real = real              # кого захищаємо (делегат)
        self._user = user              # від чийого імені йдуть виклики

    def _require(self, permission: str) -> None:
        if not self._user.can(permission):   # одна точка перевірки для всіх методів
            raise AccessDenied(f"{self._user.name}: немає права {permission}")

    def get_order(self, id: str) -> "Order":
        self._require("orders:read")    # спершу право...
        return self._real.get_order(id) # ...тоді делегуємо

    def place_order(self, order: "Order") -> str:
        self._require("orders:write")
        return self._real.place_order(order)

    def cancel_order(self, id: str) -> None:
        self._require("orders:cancel")
        self._real.cancel_order(id)
```
```java
class AccessDeniedException extends RuntimeException {   // щоб клієнт міг упіймати
    AccessDeniedException(String msg) { super(msg); }
}

class ProtectedOrderService implements OrderService {
    private final OrderService real;    // кого захищаємо (делегат)
    private final User user;            // від чийого імені йдуть виклики
    ProtectedOrderService(OrderService real, User user) {
        this.real = real; this.user = user;
    }

    private void require(String permission) {
        if (!user.can(permission)) {    // одна точка перевірки для всіх методів
            throw new AccessDeniedException(user.name() + ": немає права " + permission);
        }
    }

    public Order getOrder(String id) {
        require("orders:read");         // спершу право...
        return real.getOrder(id);       // ...тоді делегуємо
    }
    public String placeOrder(Order order) {
        require("orders:write");
        return real.placeOrder(order);
    }
    public void cancelOrder(String id) {
        require("orders:cancel");
        real.cancelOrder(id);
    }
}
```
:::

Подивімося, що тут насправді сталося. Клієнт більше не отримує `RealOrderService` — йому дають `ProtectedOrderService`, і тип у нього той самий `OrderService`, тож клієнт нічого не помічає. Але тепер кожен виклик спершу заходить у `require`, і якщо права немає — метод справжнього сервісу **навіть не викликається**: виняток летить раніше, база не чіпається. Охорона стоїть перед дверима, а не всередині кімнати.

> 🔧 **Навіщо це.** Уся перевага в тому, що `RealOrderService` лишився **нульового відношення до безпеки**. Це та сама вигода, що й у [єдиної відповідальності](book:programming/single-responsibility): один клас робить одну справу. Завтра правила прав зміняться — правитимеш `ProtectedOrderService` і жодного разу не відкриєш файл із роботою бази. А ще заступник **вмикається вибірково**: усередині системи, у фоновому обробнику без користувача, можна працювати зі справжнім сервісом напряму, без охорони; на межі, куди приходить зовнішній запит, — обгорнути в захисний проксі. Одна й та сама логіка замовлень, різний рівень нагляду — залежно від того, хто по неї прийшов.

Перевіримо на прикладі. Хай є двоє: `alice` з правами `read` + `write`, і `bob` лише з `read`.

**Умова:** обидва отримали `ProtectedOrderService` поверх спільного `RealOrderService`; `alice` створює замовлення, потім `bob` пробує скасувати чуже.

```
alice.placeOrder({...})    → require("orders:write") → alice.can("write") == true
                           → делегуємо → RealOrderService.placeOrder → "ord-42"   ✅
bob.getOrder("ord-42")     → require("orders:read")  → bob.can("read")  == true
                           → делегуємо → повертає замовлення                       ✅
bob.cancelOrder("ord-42")  → require("orders:cancel")→ bob.can("cancel")== false
                           → throw AccessDenied("bob: немає права orders:cancel")  ⛔
                           → RealOrderService.cancelOrder НЕ викликано, база ціла
```

Скасування `bob`-ом обірвалося на порозі: перевірка впала, делегування не сталося, база лишилася незмінною. Справжній сервіс так і не дізнався, що хтось намагався скасувати чуже замовлення, — уся драма розігралася в заступнику.

## Розумне посилання: кеш повторів і лог кожного дотику

Тепер друга турбота — **облік довкола доступу**. Читання `getOrder` часте й безпечне, але кожен виклик — похід у базу; якщо те саме замовлення просять двічі поспіль, другий похід зайвий. І окремо хочеться **бачити кожен виклик у лозі** — коли, який метод, чим завершився. Обидві дрібниці — не робота сервісу, а бухгалтерія навколо нього; це і є **розумне посилання**.

Складемо його як окремий заступник. Кеш тримає вже прочитані замовлення за `id`; лог пише перед і після делегування. Тонкий момент, який видно одразу: **кешувати можна лише читання**. `getOrder` — чистий запит, його відповідь можна запам'ятати. А `placeOrder` і `cancelOrder` **міняють стан**, і саме вони роблять кеш застарілим: скасував замовлення — те, що лежить у кеші, більше не відповідає базі. Тому запис не лише не кешується — він **скидає кеш**.

:::tabs
```ts
class LoggingCachingOrderService implements OrderService {
  private cache = new Map<string, Order>();   // id → вже прочитане замовлення
  constructor(private real: OrderService) {}

  getOrder(id: string): Order {
    const hit = this.cache.get(id);
    if (hit !== undefined) {
      log(`getOrder(${id}) — з кешу`);
      return hit;                              // база не чіпається взагалі
    }
    log(`getOrder(${id}) — промах, іду в базу`);
    const order = this.real.getOrder(id);
    this.cache.set(id, order);                 // запам'ятали на майбутнє
    return order;
  }

  placeOrder(order: Order): string {
    log(`placeOrder(...)`);
    const id = this.real.placeOrder(order);
    this.cache.set(id, order);                 // свіже замовлення одразу відоме
    return id;
  }

  cancelOrder(id: string): void {
    log(`cancelOrder(${id})`);
    this.real.cancelOrder(id);
    this.cache.delete(id);   // ← ІНВАЛІДАЦІЯ: кеш більше не відповідає базі
  }
}
```
```py
class LoggingCachingOrderService:
    def __init__(self, real: OrderService) -> None:
        self._real = real
        self._cache: dict[str, "Order"] = {}   # id → вже прочитане замовлення

    def get_order(self, id: str) -> "Order":
        if id in self._cache:
            log(f"get_order({id}) — з кешу")
            return self._cache[id]             # база не чіпається взагалі
        log(f"get_order({id}) — промах, іду в базу")
        order = self._real.get_order(id)
        self._cache[id] = order                # запам'ятали на майбутнє
        return order

    def place_order(self, order: "Order") -> str:
        log("place_order(...)")
        id = self._real.place_order(order)
        self._cache[id] = order                # свіже замовлення одразу відоме
        return id

    def cancel_order(self, id: str) -> None:
        log(f"cancel_order({id})")
        self._real.cancel_order(id)
        self._cache.pop(id, None)   # ← ІНВАЛІДАЦІЯ: кеш більше не відповідає базі
```
```java
class LoggingCachingOrderService implements OrderService {
    private final Map<String, Order> cache = new HashMap<>();   // id → замовлення
    private final OrderService real;
    LoggingCachingOrderService(OrderService real) { this.real = real; }

    public Order getOrder(String id) {
        Order hit = cache.get(id);
        if (hit != null) {
            log("getOrder(" + id + ") — з кешу");
            return hit;                         // база не чіпається взагалі
        }
        log("getOrder(" + id + ") — промах, іду в базу");
        Order order = real.getOrder(id);
        cache.put(id, order);                   // запам'ятали на майбутнє
        return order;
    }

    public String placeOrder(Order order) {
        log("placeOrder(...)");
        String id = real.placeOrder(order);
        cache.put(id, order);                   // свіже замовлення одразу відоме
        return id;
    }

    public void cancelOrder(String id) {
        log("cancelOrder(" + id + ")");
        real.cancelOrder(id);
        cache.remove(id);   // ← ІНВАЛІДАЦІЯ: кеш більше не відповідає базі
    }
}
```
:::

Одна деталь у `cancelOrder` варта того, щоб на ній спинитися: без рядка інвалідації весь заступник тихо стає **джерелом брехні**. Уяви, що ми його забули. Хтось читає замовлення — воно лягає в кеш зі станом «активне». Потім те саме замовлення скасовують — база оновлюється, а в кеші лишається стара копія «активне». Наступний `getOrder` радісно віддає з кешу скасоване замовлення як активне, і жодна помилка ніде не спливе — просто система показує неправду. Тому кеш живе за законом: **усе, що міняє дані, мусить прибрати з кешу застарілий запис**; це той самий обовʼязок, що й тримати [інваріанти узгодженими](book:programming/invariants) — правило «кеш відповідає базі» має виконуватися після кожної операції, не лише після читання.

Тепер найцінніше: **заступники складаються один на одного**, бо кожен має інтерфейс `OrderService` і всередині тримає теж `OrderService` — йому байдуже, справжній це сервіс чи ще один проксі. Складімо ланцюжок так, щоб зовні стояла охорона, за нею облік, а в глибині — база:

:::tabs
```ts
const real = new RealOrderService();
const cached = new LoggingCachingOrderService(real);     // облік поверх бази
const guarded = new ProtectedOrderService(cached, bob);  // охорона поверх обліку

// bob працює через один тип OrderService і не бачить ні охорони, ні кешу, ні бази:
guarded.getOrder("ord-42");
// → перевірка права read (ок) → лог → промах кешу → база → у кеш
guarded.getOrder("ord-42");
// → перевірка права read (ок) → лог → влучення в кеш → база НЕ чіпається
guarded.cancelOrder("ord-42");
// → перевірка права cancel → у bob його немає → AccessDenied, кеш і база цілі
```
```py
real = RealOrderService()
cached = LoggingCachingOrderService(real)       # облік поверх бази
guarded = ProtectedOrderService(cached, bob)    # охорона поверх обліку

# bob працює через один тип OrderService і не бачить ні охорони, ні кешу, ні бази:
guarded.get_order("ord-42")
# → перевірка права read (ок) → лог → промах кешу → база → у кеш
guarded.get_order("ord-42")
# → перевірка права read (ок) → лог → влучення в кеш → база НЕ чіпається
guarded.cancel_order("ord-42")
# → перевірка права cancel → у bob його немає → AccessDenied, кеш і база цілі
```
```java
OrderService real = new RealOrderService();
OrderService cached = new LoggingCachingOrderService(real);      // облік поверх бази
OrderService guarded = new ProtectedOrderService(cached, bob);   // охорона поверх обліку

// bob працює через один тип OrderService і не бачить ні охорони, ні кешу, ні бази:
guarded.getOrder("ord-42");
// → перевірка права read (ок) → лог → промах кешу → база → у кеш
guarded.getOrder("ord-42");
// → перевірка права read (ок) → лог → влучення в кеш → база НЕ чіпається
guarded.cancelOrder("ord-42");
// → перевірка права cancel → у bob його немає → AccessDenied, кеш і база цілі
```
:::

Порядок у ланцюжку не випадковий, і його варто прочитати вголос: **охорона зовні — щоб відмова спрацьовувала першою**, ще до того, як облік узагалі задумається про кеш. Якби ми поставили кеш зовні, а охорону всередині, то читання без права спершу влучило б у кеш і повернуло дані — а вже потім (запізно) охорона сказала б «не можна». Заступники — не просто набір обгорток, а **впорядкований конвеєр**, і місце кожного в ньому визначає, що станеться раніше.

![Клієнт ліворуч тримає тип OrderService. Праворуч від нього три коробки-заступники в ряд, вкладені зліва направо: «Захисний: право?», за ним «Розумне посилання: кеш + лог», за ним у глибині «RealOrderService: база». Наскрізна стрілка getOrder іде від клієнта в першу коробку й далі вглиб. Дві відгалужені стрілки показують, де виклик може обірватися раніше: від «Захисний» червона стрілка «немає права → відмова» повертається до клієнта; від «Розумне посилання» зелена стрілка «влучення в кеш → відповідь» повертається, не доходячи до бази. Підпис унизу: кожен шар вирішує сам, пускати виклик глибше чи обірвати](img/access-proxy-chain.svg)

*Три заступники з тим самим інтерфейсом, вкладені один в одного. Виклик іде ззовні всередину й може обірватися на будь-якому шарі: охорона відмовить без права, кеш віддасть повтор, не турбуючи базу. Порядок шарів визначає, що перевіриться раніше.*

## Біль дублювання: динамічний проксі

Обидва заступники працюють, але в них ховається неприємність, яку добре видно, коли інтерфейс росте. Наш `OrderService` має три методи. Кожен заступник **вручну повторив усі три**: три методи в захисному, три в розумному посиланні. А тепер уяви сервіс на двадцять методів. Захисний проксі — це двадцять майже однакових методів, де відрізняється лише рядок перевірки. Розумне посилання — двадцять методів обгортки логу. І найгірше: **додав до сервісу двадцять перший метод — мусиш не забути дописати його в кожен проксі**. Забув — проксі відстав від оригіналу, і новий метод пролетить повз охорону або повз лог, ніхто й не помітить, аж поки не станеться біда.

Корінь болю — у тому, що заступник **дублює інтерфейс механічно**: сама обгортка кожного методу однакова, змінюється тільки крихітна вставка. Хочеться сказати мові один раз: «перехопи **будь-який** виклик, зроби довкола нього ось це, а тоді делегуй далі» — не перелічуючи методи поіменно. Саме це дає **динамічний проксі**: заступник, який ловить усі виклики **однією точкою**, збудований засобами мови на ходу, без ручного повторення інтерфейсу.

Механізм у кожної мови свій, і в кожній він ідіоматичний по-своєму — тож розберімо всі три окремо. Задачу візьмемо ту саму, найпростішу для показу: **розумне посилання, що логує кожен виклик і делегує далі**, але тепер — для будь-якого методу автоматично.

:::tabs
```py
# Python: __getattr__ спрацьовує на доступ до атрибута, якого В САМОМУ проксі немає.
# Повертаємо загорнуту функцію — одна точка на всі методи делегата.
class LoggingProxy:
    def __init__(self, real: object) -> None:
        object.__setattr__(self, "_real", real)   # обходимо власний __getattr__

    def __getattr__(self, name: str):
        attr = getattr(self._real, name)          # дістали справжній метод/поле
        if not callable(attr):
            return attr                            # поле — віддаємо як є
        def wrapper(*args, **kwargs):              # ← ЄДИНА точка для всіх методів
            log(f"→ {name}{args}")
            result = attr(*args, **kwargs)         # делегуємо справжньому
            log(f"← {name} = {result!r}")
            return result
        return wrapper

# Один проксі накриває ВЕСЬ інтерфейс, скільки б методів у ньому не було:
service: OrderService = LoggingProxy(RealOrderService())   # type: ignore[assignment]
service.get_order("ord-42")   # __getattr__("get_order") → wrapper → лог + делегування
service.place_order(order)    # той самий шлях, ані рядка окремо під нього не писали
```
```ts
// JavaScript/TypeScript: об'єкт Proxy з пастками (trap) get + apply.
// get віддає загорнутий метод; тонкість — прив'язати this до РЕАЛЬНОГО об'єкта.
function loggingProxy<T extends object>(real: T): T {
  return new Proxy(real, {
    get(target, prop, receiver) {
      const value = Reflect.get(target, prop, receiver);
      if (typeof value !== "function") return value;   // поле — як є
      return function (this: unknown, ...args: unknown[]) {   // ← єдина точка
        log(`→ ${String(prop)}(${args})`);
        const result = Reflect.apply(value, target, args);    // this = target, НЕ проксі!
        log(`← ${String(prop)} = ${result}`);
        return result;
      };
    },
  });
}

// Один проксі накриває весь інтерфейс:
const service: OrderService = loggingProxy(new RealOrderService());
service.getOrder("ord-42");   // trap get("getOrder") → обгортка → лог + делегування
service.placeOrder(order);    // той самий шлях, окремого коду під метод немає
```
```java
// Java: java.lang.reflect.Proxy будує клас на льоту, усі виклики йдуть в invoke().
import java.lang.reflect.*;

class LoggingHandler implements InvocationHandler {
    private final Object real;
    LoggingHandler(Object real) { this.real = real; }

    // ← ЄДИНА точка: сюди приходить БУДЬ-ЯКИЙ виклик будь-якого методу інтерфейсу
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        log("→ " + method.getName() + Arrays.toString(args));
        Object result = method.invoke(real, args);   // делегуємо справжньому
        log("← " + method.getName() + " = " + result);
        return result;
    }
}

@SuppressWarnings("unchecked")
static <T> T loggingProxy(Class<T> iface, T real) {
    return (T) Proxy.newProxyInstance(
        iface.getClassLoader(),
        new Class<?>[]{ iface },          // ← лише ІНТЕРФЕЙСИ, не конкретні класи
        new LoggingHandler(real));
}

// Один проксі накриває весь інтерфейс:
OrderService service = loggingProxy(OrderService.class, new RealOrderService());
service.getOrder("ord-42");   // → invoke(method=getOrder) → лог + делегування
service.placeOrder(order);    // той самий invoke, окремого коду під метод немає
```
:::

Прочитаймо, що спільного в трьох таких різних на вигляд шматках. У кожному є **рівно одна точка**, крізь яку проходять **усі** виклики: у Python це `wrapper` усередині `__getattr__`, у JS — функція, яку повертає пастка `get`, у Java — метод `invoke`. Двадцять методів чи двісті — код заступника не росте ні на рядок. Додав сервісу новий метод — динамічний проксі підхопить його **сам**, бо він не перелічує методи, а ловить звертання як факт. Ось чому в мовах із широким інтерфейсом ручну обгортку так часто замінюють на динамічну: пишеш поведінку заступника один раз замість того, щоб дублювати її по методу.

Захисний проксі динамічно робиться так само — лише замість логу в тій єдиній точці стоїть перевірка права. Ось Java-варіант, щоб побачити, що змінюється тільки нутро `invoke`, а весь каркас той самий:

```java
class ProtectionHandler implements InvocationHandler {
    private final Object real;
    private final User user;
    // мапа: назва методу → потрібне право
    private static final Map<String, String> NEED = Map.of(
        "getOrder",    "orders:read",
        "placeOrder",  "orders:write",
        "cancelOrder", "orders:cancel");

    ProtectionHandler(Object real, User user) { this.real = real; this.user = user; }

    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        String need = NEED.get(method.getName());
        if (need != null && !user.can(need)) {          // одна точка охорони
            throw new AccessDeniedException(user.name() + ": немає права " + need);
        }
        return method.invoke(real, args);               // право є (або не потрібне) → делегуємо
    }
}
```

Одна точка, мапа «метод → право» замість трьох майже однакових ручних методів. Двадцять методів у сервісі — мапа на двадцять рядків, а не двадцять обгорток. Дублювання інтерфейсу зникло.

## Чим за це платять: прозорість, типи, ціна рефлексії

Динамічний проксі спокусливий, і саме тому варто твердо знати його межі. Він не безкоштовний, і кожна з трьох цін здатна дорого коштувати, якщо про неї забути.

**Проксі мусить лишатися прозорим — не ламати identity й типи.** Найтонша пастка ховається в JS-варіанті, і ми її вже обійшли рядком `Reflect.apply(value, target, args)`. Річ ось у чому: коли метод читають крізь пастку `get`, всередині нього `this` за замовчуванням став би **самим проксі**, а не справжнім об'єктом. Якщо метод усередині лазить у приватне поле через `this.#field`, то виклик крізь наївний проксі впаде або поведеться дивно — бо `this` уже не той об'єкт, у якого те поле є. Тому метод прив'язують до **реального** target. Це загальне правило будь-якого заступника: він має бути **невідрізнимим**. Порушив прозорість — і код, який працював зі справжнім об'єктом, ламається на проксі не там, де його читаєш, а десь усередині чужого методу, і шукати причину доведеться довго.

> 🔧 **Навіщо це.** Прозорість — не педантизм, а умова, за якої проксі взагалі можна підставляти непомітно. Щойно заступник починає відрізнятися від оригіналу — іншим `this`, іншим типом, іншою поведінкою на `===` — уся вигода «клієнт не помічає підміни» зникає, бо клієнт **починає** помічати, і то в найгіршому місці: у чужому коді, який проксі не писав. Тому строге правило: заступник додає поведінку **навколо** виклику, але сам виклик і його оточення лишає такими, ніби проксі немає.

**Динамічний проксі втрачає перевірку типів на компіляції.** Статичний проксі, який ми писали руками, компілятор перевіряв: `ProtectedOrderService implements OrderService` — і якщо ти проґавив метод або переплутав тип аргументу, збірка впаде ще до запуску. Динамічний проксі цю мережу безпеки прибирає. У Java `Proxy.newProxyInstance` повертає `Object`, який ти **сам** кастуєш до `OrderService`, обіцяючи компілятору те, чого він не перевіряв; помилка в мапі прав або в імені методу виявиться аж у рантаймі. У Python `__getattr__` узагалі ловить будь-яке ім'я — одрук у `service.get_ordr("...")` не буде помилкою компіляції, `__getattr__` слухняно піде шукати `get_ordr` у делегаті й впаде вже там. Ти виграв на дублюванні, але заплатив тим, що клас помилок, які раніше ловилися до запуску, тепер чекають на тебе в проді.

**Рефлексія коштує — і в гарячому циклі це відчутно.** Динамічний проксі працює не прямим викликом, а через механізм мови: Java йде через `Method.invoke` (рефлексія), JS — через пастки й `Reflect`, Python — через `__getattr__` і побудову обгортки на кожен доступ. Один такий виклик — дрібниця. Але постав динамічний проксі на метод, який смикають мільйон разів на секунду в гарячому циклі, — і накладні рефлексії стануть помітною часткою часу. Обмежд: Java-варіант ще й **створює нову функцію-обгортку** (JS) чи проходить пошук атрибута (Python) на кожен виклик, якщо не подбати про кеш самих обгорток. Тут доречно згадати правило [не оптимізувати передчасно](book:programming/premature-optimization): для рідкісних викликів (налаштування, адмінка, раз-на-запит) ціна рефлексії невидима й динамічний проксі — чистий виграш; для гарячого шляху краще або статичний проксі руками, або взагалі інший підхід. Міряй, де цей проксі стоїть, перш ніж ставити його на критичний шлях.

І ще одна суто Java-межа, про яку легко перечепитися: `Proxy.newProxyInstance` уміє загорнути **лише інтерфейси** — у масив передають `Class<?>`, що є інтерфейсами, і спроба підсунути конкретний клас кине `IllegalArgumentException` (це підтверджує документація `java.lang.reflect.Proxy`). Тому весь наш приклад і тримається на тому, що `OrderService` — інтерфейс. Хочеш динамічно проксувати клас без інтерфейсу — стандартної бібліотеки не досить, потрібні окремі засоби, що генерують байткод-нащадка (CGLIB, Byte Buddy). У JS і Python цього обмеження немає — там проксі накриває будь-який об'єкт, — але й типобезпеки там менше з самого початку.

Підсумок для рук. Починай зі **статичного проксі руками**: він прозорий, компілятор його перевіряє, він швидкий — і для сервісу на три-п'ять методів ручна обгортка чесніша за будь-яку магію. Тягнися до **динамічного проксі**, коли інтерфейс широкий і ручне дублювання стає джерелом помилок «забув метод», — але свідомо прийми плату: пильнуй прозорість (`this`, типи, identity), пам'ятай, що частину перевірок ти переніс із компіляції в рантайм, і не став рефлексію на гарячий цикл, не помірявши. Проксі — чи то руками, чи то динамічний — виграє рівно там, де охорона, кеш чи облік справді є окрема турбота, яку варто винести із сервісу; там, де це одна перевірка на один метод, окремий заступник буде дорожчим за просто вписаний у метод рядок.
