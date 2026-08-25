# ⚙️ Драбина в робочому коді: одна обгортка, метрика на кожен виклик

Щойно в темі ми зробили руками **один** щабель драбини — спробувати живу відповідь, а на збої зійти на кеш у межах бюджету застарілості. Одного щабля мало з двох причин. По-перше, справжній сервіс має не один виклик, а десятки, і кожен терпить **свою** брехню: читання ковтне температуру двохвилинної давнини, а замок відмовиться вірити застарілому «відчинено». По-друге — і це підступніше — коли `try/catch` пишуть окремо під кожен виклик, драбина з шести щаблів тихо осідає до двох: «жива відповідь або виняток». Не тому, що так вирішили, а тому, що під тиском кожен пише найдешевший `catch`, і драбина розсипається саме там, де вона потрібна.

Тому зберемо драбину **один раз** — як обгортку, крізь яку проходить **кожен** виклик, — і віддамо кожному викликові маленьку **політику** (policy), що каже, на яких щаблях цей виклик має право чесно стати. А тоді зробимо те єдине, що відрізняє справжній fallback від сподівання: **навмисне зламаємо залежність** і перевіримо тестом, що обгортка спинилася рівно на очікуваному щаблі — не впала й не збрехала простроченим кешем.

Ідея не нова: іменований «щабель відступу» давно живе в бібліотеках стійкості. У Netflix Hystrix це метод `getFallback()`, який перекривають, щоб дати запасну відповідь; у наступниці resilience4j — параметр `fallbackMethod`. (Сам Hystrix Netflix перевела в режим підтримки ще 2018 року й для нового коду радить resilience4j — але патерн «обгортка з fallback-щаблем» пережив саму бібліотеку.) Нижче ми будуємо той самий патерн явно, щоб було видно кожну гілку — і, головне, додаємо те, чого готова обгортка сама не дає: **метрику щабля на кожен виклик** і **політику на кожен виклик**.

## Задача одним абзацом

Хмара Digital Homes стоїть перед домашнім хабом. Коли хаб замовкає — сплив таймаут, [запобіжник](root:sf-distributed/circuit-breaker-pattern) розімкнувся, обірвалося з'єднання, — два виклики мусять пережити тишу по-різному:

- **`readState(deviceId)`** — прочитати стан пристрою (температуру термостата, положення замка). Терпить застаріле: показати значення двохвилинної давнини не гріх.
- **Ґейт перед командою — `canCommand(user, deviceId, "unlock")`** — інстанція «так/ні»: чи має цей користувач право відчинити цей замок **просто зараз**. Застаріле «дозволено» тут небезпечне; коли до авторизації не достукатися, треба свідомо обрати напрям здогаду — **fail-open** чи **fail-closed** ([залежно від ціни помилки](root:sf-distributed/fail-open-fail-closed)).

Одна тиша — дві протилежні реакції. Спокуса — написати два різні `catch`. Мета — написати **один** механізм, який обидва виклики проходять із різними політиками.

## Ідея: драбина — це дані, а обгортка нею ходить

Замість того щоб зашивати щаблі в кожен виклик, винесемо драбину **в дані**. Обгортка знає лише універсальний алгоритм — «спробуй згори вниз, віддай найвищий щабель, що спрацював». А **які** щаблі ввімкнені для конкретного виклику — каже `Policy`: чи є щабель кешу і який у нього бюджет застарілості, чи є розумний дефолт. Ось тут і ховається перше вагоме спостереження.

**Fail-open/fail-closed — не окремий механізм.** Це той самий **щабель розумного дефолту**, тільки значення в нього — рішення «так/ні». Для ґейта `smartDefault = () => ({ allowed: false })` означає fail-closed, `() => ({ allowed: true })` — fail-open. Вибір напряму — це і є вибір дефолту. Тому в коді не буде окремої гілки «а якщо це ґейт»: буде одна драбина, а fail-closed — просто конкретний дефолт для конкретної політики.

Обгортка завжди повертає не голе значення, а **який щабель його дав** — бо саме цей щабель ми хочемо міряти:

:::tabs
```ts
// Який щабель драбини віддав відповідь — рівно ці чотири.
type Rung = "live" | "cache" | "default" | "unavailable";

// Те, що обгортка ЗАВЖДИ повертає: значення, щабель і чи воно застаріле.
interface Served<T> {
  value: T;
  rung: Rung;
  stale: boolean;
}

interface Entry<T> { value: T; at: number; } // тепла копія з відміткою часу
interface Cache<T> {
  get(key: string): Entry<T> | undefined;
  put(key: string, value: T): void;
}

// Policy — це драбина В ДАНИХ: які щаблі ввімкнені саме для ЦЬОГО виклику.
interface Policy<T> {
  op: string;                      // ім'я для метрик: "readState", "canCommand:unlock"
  cache: Cache<T> | null;          // null → щабель кешу вимкнено (напр., для ґейта)
  staleBudgetMs: number;           // кеш віддаємо, лише поки вік ≤ цього
  smartDefault: (() => T) | null;  // null → дефолту нема; для ґейта це fail-open/closed
}
```
```go
// Який щабель драбини віддав відповідь — рівно ці чотири.
type Rung string

const (
    RungLive        Rung = "live"
    RungCache       Rung = "cache"
    RungDefault     Rung = "default"
    RungUnavailable Rung = "unavailable"
)

// Те, що обгортка ЗАВЖДИ повертає: значення, щабель і чи воно застаріле.
type Served[T any] struct {
    Value T
    Rung  Rung
    Stale bool
}

type entry[T any] struct {
    value T
    at    time.Time
}
type Cache[T any] interface {
    Get(key string) (entry[T], bool)
    Put(key string, v T)
}

// Policy — це драбина В ДАНИХ: які щаблі ввімкнені саме для ЦЬОГО виклику.
type Policy[T any] struct {
    Op           string        // ім'я для метрик
    Cache        Cache[T]      // nil → щабель кешу вимкнено
    StaleBudget  time.Duration // кеш віддаємо, лише поки вік ≤ цього
    SmartDefault func() T      // nil → дефолту нема; для ґейта це fail-open/closed
}
```
:::

## Обгортка

Тепер сам механізм. Він ходить драбиною згори вниз і на кожному **виході** — навіть успішному — карбує метрику щабля. Придивись до чотирьох гілок і до однієї сторожі на самому початку `catch`:

:::tabs
```ts
class Unavailable extends Error {
  constructor(op: string, key: string) {
    super(`${op}(${key}): залежність недоступна, чесного щабля не лишилось`);
  }
}

// Обгортка віддає НАЙВИЩИЙ щабель, що policy тримає чесно.
async function withFallback<T>(
  key: string,
  policy: Policy<T>,
  primary: () => Promise<T>,
): Promise<Served<T>> {
  try {
    // ① Живий щабель. Таймаут і запобіжник — усередині primary().
    const value = await primary();
    policy.cache?.put(key, value);           // тримаємо копію теплою (якщо кеш увімкнено)
    recordRung(policy.op, "live");           // метрика на КОЖНОМУ виході, навіть успішному
    return { value, rung: "live", stale: false };
  } catch (err) {
    // КЛЮЧОВЕ: fallback — лише на «залежність мовчить». Баг/валідація летять далі.
    if (!isDependencyDown(err)) throw err;

    // ② Кеш у межах бюджету застарілості.
    const hit = policy.cache?.get(key);
    if (hit && Date.now() - hit.at <= policy.staleBudgetMs) {
      recordRung(policy.op, "cache", Date.now() - hit.at);
      return { value: hit.value, rung: "cache", stale: true };
    }

    // ③ Розумний дефолт. Для ґейта САМЕ ТУТ живе fail-open/fail-closed.
    if (policy.smartDefault) {
      recordRung(policy.op, "default");
      return { value: policy.smartDefault(), rung: "default", stale: true };
    }

    // ④ Чесна вузька відмова. Не брехня простроченим кешем — прямо «недоступно».
    recordRung(policy.op, "unavailable");
    throw new Unavailable(policy.op, key);
  }
}
```
```go
type Unavailable struct{ Op, Key string }

func (e *Unavailable) Error() string {
    return fmt.Sprintf("%s(%s): залежність недоступна, чесного щабля не лишилось", e.Op, e.Key)
}

// Обгортка віддає НАЙВИЩИЙ щабель, що policy тримає чесно.
func WithFallback[T any](
    key string,
    policy Policy[T],
    primary func() (T, error),
) (Served[T], error) {
    // ① Живий щабель. Таймаут і запобіжник — усередині primary().
    value, err := primary()
    if err == nil {
        if policy.Cache != nil {
            policy.Cache.Put(key, value) // тримаємо копію теплою
        }
        recordRung(policy.Op, RungLive, 0) // метрика на КОЖНОМУ виході, навіть успішному
        return Served[T]{Value: value, Rung: RungLive}, nil
    }

    // КЛЮЧОВЕ: fallback — лише на «залежність мовчить». Баг/валідація летять далі.
    if !isDependencyDown(err) {
        return Served[T]{}, err
    }

    // ② Кеш у межах бюджету застарілості.
    if policy.Cache != nil {
        if hit, ok := policy.Cache.Get(key); ok {
            if age := time.Since(hit.at); age <= policy.StaleBudget {
                recordRung(policy.Op, RungCache, age)
                return Served[T]{Value: hit.value, Rung: RungCache, Stale: true}, nil
            }
        }
    }

    // ③ Розумний дефолт. Для ґейта САМЕ ТУТ живе fail-open/fail-closed.
    if policy.SmartDefault != nil {
        recordRung(policy.Op, RungDefault, 0)
        return Served[T]{Value: policy.SmartDefault(), Rung: RungDefault, Stale: true}, nil
    }

    // ④ Чесна вузька відмова. Не брехня простроченим кешем — прямо «недоступно».
    recordRung(policy.Op, RungUnavailable, 0)
    return Served[T]{}, &Unavailable{Op: policy.Op, Key: key}
}
```
:::

Чотири виходи — чотири щаблі, і на кожному стоїть `recordRung`. Це не косметика: без метрики на **живому** щаблі ти не маєш знаменника. «Сто викликів упало на кеш» нічого не означає, поки не знаєш, зі скількох усього — зі ста тисяч (0.1%, спокійно) чи зі ста двадцяти (кеш витримує систему на плечах, залежність фактично мертва). Тому метрика виходить **завжди**, а вже дашборд рахує частку деградованих — і саме тому деградований шлях без [спостережності](root:progarch/observability-as-testability) сліпий.

Сторожа `isDependencyDown(err)` на початку `catch` — друге серце обгортки. Fallback законний **тільки** тоді, коли залежність мовчить; якщо ж примчала справжня відповідь «так не можна» — помилка валідації, «пристрою нема», відмова прав, — маскувати її кешем означає **брехати про іншу річ**. Тому не-залежницька помилка летить далі як є:

:::tabs
```ts
// «Залежність мовчить» — це минущий збій транспорту, а не змістовна відповідь.
function isDependencyDown(err: unknown): boolean {
  return err instanceof TimeoutError
      || err instanceof CircuitOpenError    // запобіжник розімкнено
      || err instanceof ConnectionError;
  // НЕ сюди: ValidationError, NotFoundError, ForbiddenError — це чесні відповіді,
  // і підмінити їх кешем/дефолтом = замаскувати справжній баг.
}
```
```go
// «Залежність мовчить» — це минущий збій транспорту, а не змістовна відповідь.
func isDependencyDown(err error) bool {
    var to *TimeoutError
    var co *CircuitOpenError // запобіжник розімкнено
    return errors.As(err, &to) || errors.As(err, &co) ||
        errors.Is(err, context.DeadlineExceeded) ||
        errors.Is(err, syscall.ECONNREFUSED)
    // НЕ сюди: ValidationError, NotFound, Forbidden — це чесні відповіді, не тиша.
}
```
:::

А метрика — простий лічильник із мітками `{op, rung}` (стиль Prometheus / OpenTelemetry), оголошений раз:

:::tabs
```ts
// fallback_rung_total{op, rung} — скільки викликів яким щаблем закрилось.
function recordRung(op: string, rung: Rung, ageMs = 0): void {
  rungTotal.labels(op, rung).inc();
  if (rung === "cache") cacheAge.labels(op).observe(ageMs); // вік відданого кешу
}
```
```go
// fallback_rung_total{op, rung} — скільки викликів яким щаблем закрилось.
func recordRung(op string, rung Rung, age time.Duration) {
    rungTotal.WithLabelValues(op, string(rung)).Inc()
    if rung == RungCache {
        cacheAge.WithLabelValues(op).Observe(age.Seconds()) // вік відданого кешу
    }
}
```
:::

![Згори — вхідна рамка «будь-який виклик → withFallback(key, policy, primary())». Під нею вертикальна драбина з чотирьох щаблів, кожен — умова ліворуч і кольоровий бейдж-результат праворуч; між щаблями вниз ідуть стрілки з підписами причини сходження. Щабель ①: «primary() — жива відповідь (таймаут/запобіжник усередині)» → зелений «rung=live · метрика»; стрілка вниз «↓ dependency down (не баг!)». Щабель ②: «кеш свіжіший за staleBudget?» → зелений «rung=cache · stale»; стрілка «↓ кешу нема / прострочений». Щабель ③: «є розумний дефолт?» → бурштиновий «rung=default (для ґейта — fail-open/closed)»; стрілка «↓ дефолту не передбачено». Щабель ④: «чесно зізнатись» → червоний «throw Unavailable · rung=unavailable». Праворуч висока рамка-виноска «policy вмикає щаблі: read → cache+чесна відмова; ґейт → без кешу, дефолт=fail-closed». Унизу банер: «recordRung на КОЖНОМУ виході — навіть live: без знаменника деградацію не побачиш».](img/withfallback-flow.svg)
*Обгортка ходить драбиною згори вниз, а політика вмикає й вимикає щаблі під конкретний виклик. Метрика щабля стоїть на кожному виході — включно з живим, бо частку деградованих без знаменника не порахувати.*

> 🔧 **Навіщо це.** Одна обгортка замість розсипаних `catch` — це не про охайність, а про те, що драбину видно й **виміряно**. Розсипані `catch` завжди деградують до двох щаблів (жива відповідь або виняток), бо кожен пишеться поспіхом. Зведи їх в один прохід — і тоді щабель стає **даними**: його видно в політиці, його карбує метрика, його перевіряє тест. Усе, що нижче, спирається саме на це.

## Дві політики, той самий механізм

Тепер — обіцяне «одна тиша, дві реакції», але вже в коді. Обидва виклики йдуть крізь `withFallback`; різницю задають **тільки** політики.

:::tabs
```ts
// READ: терпить застаріле на 2 хв; коли кеш прострочено — чесна відмова (дефолту НЕМА).
const readPolicy: Policy<Reading> = {
  op: "readState",
  cache: readingCache,
  staleBudgetMs: 120_000,
  smartDefault: null,        // прострочений кеш → Unavailable, а не тихе старе значення
};

function readState(id: string): Promise<Served<Reading>> {
  return withFallback(id, readPolicy, () => device.read(id));
}

// ҐЕЙТ (так/ні): кешу НЕМА (щоб не відтворити застаріле «дозволено»), дефолт = fail-closed.
// Для пейволла було б smartDefault: () => ({ allowed: true }) — fail-open.
const unlockGatePolicy: Policy<Decision> = {
  op: "canCommand:unlock",
  cache: null,
  staleBudgetMs: 0,
  smartDefault: () => ({ allowed: false }),   // не достукались до авторизації → забороняємо
};

async function unlock(user: string, id: string): Promise<void> {
  const gate = await withFallback(`${user}:${id}`, unlockGatePolicy,
    () => authz.canCommand(user, id, "unlock"));

  if (!gate.value.allowed) throw new Forbidden(user, id);  // fail-closed: не впустили — правильно
  await hub.send(id, "unlock");   // саму КОМАНДУ не фолбечимо — вона не ідемпотентна
}
```
```go
// READ: терпить застаріле на 2 хв; коли кеш прострочено — чесна відмова (дефолту НЕМА).
var readPolicy = Policy[Reading]{
    Op:           "readState",
    Cache:        readingCache,
    StaleBudget:  2 * time.Minute,
    SmartDefault: nil, // прострочений кеш → Unavailable, а не тихе старе значення
}

func ReadState(id string) (Served[Reading], error) {
    return WithFallback(id, readPolicy, func() (Reading, error) {
        return device.Read(id) // таймаут/запобіжник — усередині
    })
}

// ҐЕЙТ (так/ні): кешу НЕМА (щоб не відтворити застаріле «дозволено»), дефолт = fail-closed.
// Для пейволла було б SmartDefault: func() Decision { return Decision{Allowed: true} }.
var unlockGatePolicy = Policy[Decision]{
    Op:           "canCommand:unlock",
    Cache:        nil,
    SmartDefault: func() Decision { return Decision{Allowed: false} }, // fail-closed
}

func Unlock(user, id string) error {
    gate, err := WithFallback(user+":"+id, unlockGatePolicy, func() (Decision, error) {
        return authz.CanCommand(user, id, "unlock")
    })
    if err != nil {
        return err // напр., не-залежницька помилка авторизації — пропускаємо як є
    }
    if !gate.Value.Allowed {
        return &Forbidden{User: user, ID: id} // fail-closed: не впустили — правильно
    }
    return hub.Send(id, "unlock") // саму команду не фолбечимо — вона не ідемпотентна
}
```
:::

Придивись, як розходяться шляхи під **однією** тишею. У `readPolicy` є кеш і немає дефолту: жива температура → застаріла в межах двох хвилин → а якщо й кеш протух, обгортка чесно кидає `Unavailable`, бо гірше за «недоступно» лише **тихо-хибне** старе значення. У `unlockGatePolicy` навпаки — кешу немає зовсім, зате є дефолт `{ allowed: false }`. Через відсутній кеш ґейт **не може** відтворити застаріле «дозволено» навіть випадково; через дефолт-заборону він **ніколи** не доходить до `Unavailable` — ґейт завжди видає рішення, бо його контракт саме такий: не «не знаю», а «так/ні», і напрям здогаду обрано заздалегідь.

І ще одна тонкість у `unlock`: коли ґейт сказав `allowed`, ми шлемо команду хабу — але **саму команду** через обгортку fallback не проводимо. Повторити читання безпечно, а повторити «відчинити» — ні, якщо перша спроба насправді дійшла до замка, а загубилась лише відповідь ([чому повтор безпечний лише для ідемпотентних операцій](root:sf-distributed/idempotency)). Fallback — про **відповіді на запити стану**, не про дії над фізичним світом.

## Тест, що навмисне вимикає залежність

Тепер найважливіше. Fallback-код виконується **тільки під час збою** — тобто в спокійні дні не працює ніколи й лишається найменш обкатаним у системі. Раз він не пробується сам, його треба пробувати **навмисне**: підсунути залежність, яку можна вимкнути перемикачем, увімкнути «збій» і **перевірити щабель**, на якому система встояла. Не «не впало» — а саме `rung == cache`, `rung == unavailable`, `rung == default`, залежно від сценарію.

Спершу підробка залежності з перемикачем `down`:

:::tabs
```ts
// Підроблена залежність із перемикачем: down=true → кидає, наче хаб замовк.
class FakeDevice {
  down = false;
  reading: Reading = { temperature: 21.5, stale: false };
  async read(id: string): Promise<Reading> {
    if (this.down) throw new TimeoutError(id); // ← навмисно «вимкнена» залежність
    return { ...this.reading };
  }
}

class MapCache<T> implements Cache<T> {
  private m = new Map<string, Entry<T>>();
  get(key: string) { return this.m.get(key); }
  put(key: string, value: T) { this.m.set(key, { value, at: Date.now() }); }
  seed(key: string, value: T, at: number) { this.m.set(key, { value, at }); } // шов для тесту
}
```
```go
// Підроблена залежність із перемикачем: down=true → кидає, наче хаб замовк.
type fakeDevice struct {
    down    bool
    reading Reading
}

func (d *fakeDevice) Read(id string) (Reading, error) {
    if d.down {
        return Reading{}, &TimeoutError{Key: id} // ← навмисно «вимкнена» залежність
    }
    return d.reading, nil
}

type mapCache[T any] struct{ m map[string]entry[T] }

func newMapCache[T any]() *mapCache[T]           { return &mapCache[T]{m: map[string]entry[T]{}} }
func (c *mapCache[T]) Get(k string) (entry[T], bool) { e, ok := c.m[k]; return e, ok }
func (c *mapCache[T]) Put(k string, v T)         { c.m[k] = entry[T]{value: v, at: time.Now()} }
func (c *mapCache[T]) seed(k string, v T, at time.Time) { c.m[k] = entry[T]{value: v, at: at} }
```
:::

Тепер три сценарії — і в кожному перевіряємо **щабель**, а не лише «встояло»:

:::tabs
```ts
test("read + залежність down + свіжий кеш → щабель cache, не падає й не бреше простроченим", async () => {
  const device = new FakeDevice();
  const policy: Policy<Reading> = { ...readPolicy, cache: new MapCache<Reading>() };

  await withFallback("dev-1", policy, () => device.read("dev-1")); // прогрів: жива → у кеш
  device.down = true;                                              // ← вимикаємо залежність

  const served = await withFallback("dev-1", policy, () => device.read("dev-1"));

  expect(served.rung).toBe("cache");           // встояли на ОЧІКУВАНОМУ щаблі
  expect(served.stale).toBe(true);             // і чесно позначили: це не свіже
  expect(served.value.temperature).toBe(21.5);
});

test("read + залежність down + ПРОСТРОЧЕНИЙ кеш → чесна відмова, а не стара брехня", async () => {
  const device = new FakeDevice();
  const cache = new MapCache<Reading>();
  cache.seed("dev-1", { temperature: 21.5, stale: false }, Date.now() - 5 * 60_000); // кешу 5 хв
  const policy: Policy<Reading> = { ...readPolicy, cache, staleBudgetMs: 60_000 };    // бюджет 1 хв
  device.down = true;

  // КЛЮЧОВЕ: система НЕ віддає прострочене значення — вона чесно падає вузько.
  await expect(withFallback("dev-1", policy, () => device.read("dev-1")))
    .rejects.toBeInstanceOf(Unavailable);
});

test("gate unlock + залежність down + fail-closed → deny, НЕ fail-open, кеш не чіпає", async () => {
  const authzDown = () => Promise.reject(new TimeoutError("authz")); // авторизація мовчить
  const served = await withFallback("u1:dev-1", unlockGatePolicy, authzDown);

  expect(served.rung).toBe("default");         // впав на дефолт-щабель…
  expect(served.value.allowed).toBe(false);    // …а дефолт — ЗАБОРОНА (fail-closed)
});
```
```go
func TestReadFreshCache(t *testing.T) {
    dev := &fakeDevice{reading: Reading{Temperature: 21.5}}
    policy := readPolicy
    policy.Cache = newMapCache[Reading]()

    // прогрів: жива відповідь осідає в кеш
    WithFallback("dev-1", policy, func() (Reading, error) { return dev.Read("dev-1") })
    dev.down = true // ← вимикаємо залежність

    served, err := WithFallback("dev-1", policy,
        func() (Reading, error) { return dev.Read("dev-1") })

    if err != nil {
        t.Fatalf("не мало впасти: %v", err)
    }
    if served.Rung != RungCache {
        t.Errorf("щабель = %q, хотіли cache", served.Rung)
    }
    if !served.Stale {
        t.Error("cache-щабель мусить нести stale=true")
    }
}

func TestReadExpiredCacheFailsHonestly(t *testing.T) {
    dev := &fakeDevice{down: true}
    cache := newMapCache[Reading]()
    cache.seed("dev-1", Reading{Temperature: 21.5}, time.Now().Add(-5*time.Minute)) // кешу 5 хв
    policy := readPolicy
    policy.Cache = cache
    policy.StaleBudget = time.Minute // бюджет 1 хв < вік кешу

    _, err := WithFallback("dev-1", policy,
        func() (Reading, error) { return dev.Read("dev-1") })

    var un *Unavailable
    if !errors.As(err, &un) { // мусить бути ЧЕСНА відмова, а не старе значення
        t.Fatalf("хотіли Unavailable, а не стару брехню; отримали %v", err)
    }
}

func TestGateFailClosed(t *testing.T) {
    served, err := WithFallback("u1:dev-1", unlockGatePolicy,
        func() (Decision, error) { return Decision{}, &TimeoutError{Key: "authz"} })

    if err != nil {
        t.Fatalf("ґейт не мав повернути помилку: %v", err)
    }
    if served.Rung != RungDefault {
        t.Errorf("щабель = %q, хотіли default", served.Rung)
    }
    if served.Value.Allowed { // fail-closed: дефолт мусить бути ЗАБОРОНА
        t.Error("fail-closed зламано: дефолт відчинив замок")
    }
}
```
:::

Кожен тест ловить **свій** клас брехні. Перший стежить, щоб під живою залежністю в кеші, вимкнувши її, ми дістали кеш і **чесну позначку `stale`** — не тихо видали старе за свіже. Другий — найважливіший: коли кеш **старший за бюджет**, система мусить `throw Unavailable`, а не віддати п'ятихвилинну температуру як поточну; сам `rejects.toBeInstanceOf(Unavailable)` (Go: `errors.As` до `*Unavailable`) і є перевіркою «не збрехала простроченим». Третій пильнує ґейт: під тишею авторизації fail-closed мусить дати `allowed == false` — не впав, не відчинив наосліп, кешу не торкнувся.

![Таблиця з чотирьох рядків і чотирьох колонок: «Сценарій», «Впорснутий збій», «Очікуваний щабель», «Що НЕ сталося (баг, який ловимо)». Рядок 1 (зелений щабель): readState · кеш свіжий (≤ бюджет) | залежність down | rung=cache · stale=true | не впав; не віддав прострочене. Рядок 2 (червоний): readState · кеш прострочений (> бюджет) | залежність down | throw Unavailable (rung=unavailable) | НЕ збрехав старим кешем. Рядок 3 (бурштиновий): canCommand:unlock · fail-closed · без кешу | залежність down | allowed=false (rung=default) | НЕ fail-open; кеш не чіпав. Рядок 4 (зелений, контроль): readState · залежність ЖИВА | — | rung=live · кеш прогрітий | видно live у метриці (знаменник).](img/outage-test-matrix.svg)
*Тест не питає «чи впало» — він фіксує ОЧІКУВАНИЙ щабель на кожен навмисний збій. Права колонка називає брехню, яку кожен рядок стереже: обвал, старий кеш, fail-open. Контрольний рядок із живою залежністю дає знаменник для метрики.*

> 🔧 **Навіщо це.** Fallback, який жодного разу не запускали, — це не запасна позиція, а здогад: у дефолті ховається помилка, читання кешу кидає виняток, а найгірше — деградований шлях **тихо бреше** простроченим значенням, і ніхто не бачить, бо тривога не спрацювала. Тест із перемикачем `down` — єдине місце, де цей шлях узагалі виконується поза продом. Перевіряй ним не «встояло/впало», а **точний щабель**: інакше зелений тест може ховати систему, що встояла, збрехавши.

## Складність і пастки

Механізм простий, але кожна його гілка ламається на дрібниці, і кожна дрібниця вже стелила комусь нічну зміну.

**Сторожа `isDependencyDown` — не косметика, а межа брехні.** Спокуса написати голий `catch (err) { …fallback… }` без розбору помилки. Тоді помилка валідації «поле температури поза діапазоном» чи «пристрою не існує» піде на щабель кешу — і ти віддаси старе значення на запит, який насправді був **хибний**. Ти замаскував баг кешем, і тепер він невидимий удвічі. Fallback законний **лише** для минущого збою транспорту; будь-яка змістовна відповідь залежності, навіть негативна, мусить пройти нагору незмінною. Помиляйся в бік `throw`, не в бік мовчазного кешу.

**Кеш для ґейта треба вимикати в політиці, а не «просто не читати».** Легко подумати: «ми ж не звертаємось до кешу на шляху авторизації». Але поки `cache != null`, живий щабель ще й **пише** в нього рішення — і одного дня хтось додасть читання, а тепла копія застарілого «дозволено» вже лежить напоготові. Тому `cache: null` у `unlockGatePolicy` — не оптимізація, а гарантія: рішення нікуди не зберігається, тож відтворити його неможливо навіть помилково. Вимкнений щабель безпечніший за ввімкнений-але-обійдений.

**Метрика на живому щаблі — знаменник, без якого решта сліпа.** Порахувати `recordRung(op, "live")` серед зайвих — часта економія: «навіщо міряти успіх, він і так успіх». Без нього ти бачиш абсолютне число деградацій, але не **частку**, а саме частка каже, чи це фонове тремтіння (0.1%), чи залежність фактично мертва й систему тримає лише кеш. Alert будуй на відношенні `rung!=live / всі` — а для відношення потрібні обидві половини.

**Fail-open — це справжній вибір із справжньою ціною, а не «дефолт за замовчуванням».** Напрям дефолту для ґейта обирають **під кожну інстанцію окремо** за ціною помилки: пейволл радше fail-open (пустити читача, втративши копійки, дешевше, ніж розлютити стіною), а замок, платіж, перевірка прав — тільки fail-closed. Небезпека — скопіювати політику з одного ґейта на інший «бо схоже»: fail-open, доречний для банера, відчинить двері, якщо його наосліп перенести на замок. Кожна нова інстанція «так/ні» — окреме рішення, у який бік помилитися дешевше.

**Бюджет застарілості — обов'язкова частина щабля кешу, не порада.** Кеш без бюджету з часом перетворюється зі рятівника на джерело тихо-хибних відповідей: залежність померла три тижні тому, а система бадьоро віддає температуру тритижневої давнини як поточну. Перевірка `Date.now() - hit.at <= staleBudgetMs` (Go: `time.Since(hit.at) <= StaleBudget`) — саме та межа, за якою чесне «недоступно» стає кращим за старе значення. Тест на прострочений кеш існує рівно для того, щоб ця межа не зникла при рефакторингу.

**Обгортка з дженериками не замінює запобіжник усередині `primary`.** Наша драбина вирішує, **що віддати**, коли залежність мовчить, — але сам факт «мовчить швидко, а не висить хвилинами» забезпечує таймаут і [запобіжник](root:sf-distributed/circuit-breaker-pattern) **всередині** `primary()`. Без них перший щабель не впаде **швидко**: `withFallback` слухняно чекатиме завислого виклику стільки, скільки той висить, і драбина не почне спускатись. «Падай швидко» і «що віддати, впавши» — дві половини однієї відповіді; ця обгортка робить лише другу, і покладається, що першу вже зроблено там, де народжується `primary`.
