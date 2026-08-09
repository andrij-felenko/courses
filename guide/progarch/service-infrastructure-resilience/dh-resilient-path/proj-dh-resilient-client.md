# ⚙️ Стійкий клієнт DH: один стос на кожен шов і сторож, що не пускає повз нього

П'ять рядків стійкості на один виклик ми вже склали й прочитали згори вниз: слот перебірки, перевірка запобіжника, стеля часу, а всередині — виклик із повтором. Легко написати їх раз. Небезпека не в першому шві, а в **шостому** — тому, що хтось під дедлайн допише «швиденько, напряму», забувши обгортку. Наївний клієнт лишає стійкість на пам'ять автора; а пам'ять автора о шостій вечора коротка.

Тож не лишаймо. Зберімо той стос **один раз** — у спільному клієнті міжсервісних викликів, крізь який ходить **кожен** похід у сусідній сервіс. Клієнт резолвить адресу через [реєстр виявлення](book:programming/service-discovery) і поверх того резолву накладає всю політику: перебірку, запобіжник, таймаут, повтор. Хто хоче покликати телеметрію чи ядро — бере клієнт і дістає стійкість **за побудовою**, а не тому, що згадав. А щоб «сирий» шлях в обхід був не просто небажаним, а **неможливим у зеленій збірці**, поставимо поруч фітнес-тест, який валить CI на будь-якому міжсервісному HTTP повз клієнт. І наприкінці задушимо телеметрію штучною затримкою й доведемо на працюючому коді, що головний екран деградує до «пристрій без виміру», а список пристроїв і команди течуть окремим пулом, наче нічого не сталося.

## Задача: що саме має вміти клієнт

Випишімо вимоги так, щоб кожну можна було потім тицьнути пальцем у код:

- **резолв адреси через реєстр** — клієнт не знає IP сусіда напам'ять; він питає реєстр виявлення про **готовий** екземпляр (той, що вже прогрівся й сказав «беріть трафік») і лише тоді стукає;
- **стос політики в правильному порядку** — перебірка зовні, запобіжник усередині неї, таймаут на спробу, повтор у ядрі; **порядок не косметика** — переплутаєш шари, і стійкість тихо потече;
- **окремий стос на кожну залежність** — телеметрія дістає свій пул і свій запобіжник, ядро — свої; біда однієї не займає ресурс іншої;
- **фолбек — рішення каллера, не клієнта** — клієнт однаково обгортає **будь-який** виклик, але вирішувати «чим замінити відповідь, якої нема» мусить той, хто кличе: читанню виміру — риска «—», команді «зачинити» — **нічого**, чесна відмова;
- **сторож проти обходу** — фітнес-тест, що валить збірку на сирому `fetch`/HTTP у сусідній сервіс повз клієнт;
- **доказ на живому** — тест, що душить телеметрію й показує числами: екран деградував, ядро й команди — течуть.

Остання пара вимог — про те, чого сам клієнт гарантувати не може. Клієнт — це **можливість** робити правильно; сторож — це те, що робить правильне **єдиним** способом пройти збірку; а тест — це те, що доводить: можливість справді працює під навантаженням, а не лише на папері.

## Ідея: політика — властивість шва, зібрана раз

Головний зсув у голові простий. Наївно ми думаємо про стійкість як про **дію викличника**: «не забудь обгорнути свій виклик». Клієнт міняє це на **властивість шва**: перебірка й запобіжник — не те, що ти робиш, а те, чим цей шов **є**. Телеметричний шов *має* пул на десять і запобіжник на п'ять відмов — так само незмінно, як він має адресу. Ти не «додаєш» їх, ти просто ходиш крізь шов, а вони вже там.

Звідси й конструкція: **один екземпляр клієнта на залежність**, і цей екземпляр **володіє** своїм пулом та своїм запобіжником. Це і є фізичний слід ізоляції з [основної статті](book:programming/bulkhead-isolation): окремий пул — це буквально окреме поле в окремому об'єкті `ServiceClient("telemetry")`, якого об'єкт `ServiceClient("core")` не бачить і не може вичерпати. Спільним лишається тільки **код** стосу; **стан** — пул, лічильник відмов, стан запобіжника — у кожної залежності свій.

І один рядок, який відрізняє чесний клієнт від фальшивого: **фолбек живе не в клієнті**. Клієнт віддає стійкість (не завис, швидка відповідь) і **помилку**, коли не дотягнувся; а що з тією помилкою робити — підмінити рискою чи чесно віддати нагору — вирішує каллер. Інакше клієнт мусив би «знати», що телеметрію можна підмінити, а замок — ні, тобто тягнути в себе доменний сенс кожного виклику. Ми цього не хочемо: клієнт — інфраструктура, а «чим це замінити» — доменне рішення.

## Перебірка на семафорі: fail-fast і обмежене очікування

Почнімо з найнижчої цеглинки — перебірки. Механічно це **семафор**: лічильник дозволених одночасних викликів. Але тут ховається перше проєктне рішення, і воно різне для різних швів: що робити, коли слотів немає — **відмовити одразу** чи **трохи почекати** у черзі?

Для телеметрії відповідь — відмовити одразу (fail-fast): краще миттєва риска «—», ніж черга, у якій запит на прикрасу стоїть і тримає ресурс. Для ядра — навпаки: список пристроїв критичний, тож коротка **обмежена** черга доречна — хай зачекає мілісекунди на вільний слот, ніж дістане відмову. Тому семафор клієнта вміє обидва режими: `черга 0` — це fail-fast, `черга > 0` — обмежене очікування зі **своєю** стелею (черга без стелі — прихована яма затримки, туди ще повернемось).

:::tabs
```ts
// Перебірка = семафор: ≤ limit одночасних; при переповненні або миттєва
// відмова (fail-fast, maxQueue = 0), або коротке очікування в обмеженій черзі.
class BulkheadFull extends Error { readonly retryable = false; }

class Bulkhead {
  private inFlight = 0;
  private readonly q: Array<{ ok: () => void; timer: ReturnType<typeof setTimeout> }> = [];

  constructor(
    private readonly limit: number,
    private readonly maxQueue = 0,     // 0 → fail-fast
    private readonly maxWait = 0,      // стеля очікування в черзі, мс
  ) {}

  async run<T>(fn: () => Promise<T>): Promise<T> {
    await this.acquire();
    try { return await fn(); }
    finally { this.release(); }
  }

  private acquire(): Promise<void> {
    if (this.inFlight < this.limit) { this.inFlight++; return Promise.resolve(); }
    if (this.q.length >= this.maxQueue) return Promise.reject(new BulkheadFull());
    return new Promise<void>((resolve, reject) => {          // паркуємось у черзі — але не назавжди
      const timer = setTimeout(() => {
        const i = this.q.findIndex((w) => w.timer === timer);
        if (i >= 0) { this.q.splice(i, 1); reject(new BulkheadFull()); }
      }, this.maxWait);
      this.q.push({ ok: resolve, timer });
    });
  }

  private release(): void {
    const w = this.q.shift();
    if (w) { clearTimeout(w.timer); w.ok(); }   // слот ПЕРЕХОДИТЬ наступному — лічильник не чіпаємо
    else this.inFlight--;                        // охочих нема — звільняємо слот
  }
}
```
```py
# Перебірка = семафор: ≤ limit одночасних; при переповненні або миттєва
# відмова (fail-fast, max_queue = 0), або коротке очікування в обмеженій черзі.
import asyncio
from collections import deque


class BulkheadFull(Exception):
    retryable = False


class Bulkhead:
    def __init__(self, limit, max_queue=0, max_wait=0.0):
        self._limit = limit
        self._max_queue = max_queue       # 0 → fail-fast
        self._max_wait = max_wait         # стеля очікування в черзі, с
        self._in_flight = 0
        self._waiters: deque[asyncio.Future] = deque()

    async def run(self, fn):
        await self._acquire()
        try:
            return await fn()
        finally:
            self._release()

    async def _acquire(self):
        if self._in_flight < self._limit:
            self._in_flight += 1
            return
        if len(self._waiters) >= self._max_queue:
            raise BulkheadFull()
        fut = asyncio.get_running_loop().create_future()
        self._waiters.append(fut)
        try:
            await asyncio.wait_for(fut, self._max_wait)   # паркуємось, але не назавжди
        except asyncio.TimeoutError:
            if fut in self._waiters:
                self._waiters.remove(fut)
            raise BulkheadFull()
        # слот передано нам напряму — лічильник уже враховує його

    def _release(self):
        while self._waiters:
            fut = self._waiters.popleft()
            if not fut.done():
                fut.set_result(None)     # слот ПЕРЕХОДИТЬ наступному — лічильник не чіпаємо
                return
        self._in_flight -= 1              # охочих нема — звільняємо слот
```
:::

Зверніть увагу на дрібницю в `release`, від якої залежить коректність: коли є хтось у черзі, ми **не** зменшуємо `inFlight`, а передаємо слот далі — він просто змінює власника. Зменшуємо лічильник тільки тоді, коли черга порожня. Інакше слот «протік» би: звільнили й одразу віддали, порахувавши двічі.

## Запобіжник із трьома станами й однією пробою

Друга цеглинка — [запобіжник](book:programming/circuit-breaker-pattern), той самий автомат на три стани, що ми вже розібрали: закритий кличе й лічить відмови, відкритий не кличе взагалі й одразу віддає відмову, напіввідкритий пропускає **рівно одну** пробу. Уся тонкість реалізації — в отому «рівно одну»: у бою запобіжник кличуть з багатьох викликів водночас, і коли кулдаун щойно минув, легко пропустити **натовп** проб на ледь оживлений сервіс замість однієї.

Ключ до «рівно одної» — те, що рішення «пускати чи ні» ухвалюється **синхронно**, без жодного `await` усередині. У однопотоковій моделі (і JS, і `asyncio`) код між двома `await` виконується атомарно: поки триває синхронна перевірка `allow()`, ніхто інший у неї не влізе. Тож прапорця «проба в польоті» досить — перший виклик у напіввідкритому стані ставить його й проходить, решта бачать прапорець і одразу коротять.

:::tabs
```ts
// Запобіжник: closed → open → half. Рішення "пускати?" СИНХРОННЕ (без await),
// тому в однопотоковому рушії проба гарантовано одна.
class CircuitOpen extends Error { readonly retryable = false; }
type BState = "closed" | "open" | "half";
const now = () => performance.now();     // МОНОТОННИЙ годинник, не Date.now()

class CircuitBreaker {
  private state: BState = "closed";
  private fails = 0;
  private openedAt = 0;
  private probeInFlight = false;

  constructor(private readonly o: { failsToOpen: number; cooldown: number }) {}

  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (!this.allow()) throw new CircuitOpen();   // відкритий → НЕ кличемо, миттєво нагору
    try {
      const r = await fn();
      this.onSuccess();
      return r;
    } catch (e) {
      this.onFailure();                            // рахуємо ЦЕЙ виклик як відмову
      throw e;
    }
  }

  private allow(): boolean {
    if (this.state === "closed") return true;
    if (this.state === "open") {
      if (now() - this.openedAt < this.o.cooldown) return false;   // ще холонемо
      this.state = "half"; this.probeInFlight = true; return true; // ця спроба — і є проба
    }
    if (this.probeInFlight) return false;          // half: пробу вже взяли — решту коротимо
    this.probeInFlight = true; return true;
  }

  private onSuccess() { this.state = "closed"; this.fails = 0; this.probeInFlight = false; }

  private onFailure() {
    if (this.state === "half") return this.open();          // проба впала — знову відкрито
    if (++this.fails >= this.o.failsToOpen) this.open();
  }

  private open() { this.state = "open"; this.openedAt = now(); this.fails = 0; this.probeInFlight = false; }
}
```
```py
# Запобіжник: closed → open → half. Рішення "пускати?" СИНХРОННЕ (без await),
# тому в однопотоковому asyncio проба гарантовано одна.
from time import monotonic     # МОНОТОННИЙ годинник, не time.time()


class CircuitOpen(Exception):
    retryable = False


class CircuitBreaker:
    def __init__(self, fails_to_open, cooldown):
        self._fails_to_open = fails_to_open
        self._cooldown = cooldown
        self._state = "closed"
        self._fails = 0
        self._opened_at = 0.0
        self._probe = False

    async def call(self, fn):
        if not self._allow():                 # відкритий → НЕ кличемо, миттєво нагору
            raise CircuitOpen()
        try:
            r = await fn()
        except Exception:
            self._on_failure()                # рахуємо ЦЕЙ виклик як відмову
            raise
        self._on_success()
        return r

    def _allow(self):
        if self._state == "closed":
            return True
        if self._state == "open":
            if monotonic() - self._opened_at < self._cooldown:
                return False                  # ще холонемо
            self._state, self._probe = "half", True   # ця спроба — і є проба
            return True
        if self._probe:                       # half: пробу вже взяли
            return False
        self._probe = True
        return True

    def _on_success(self):
        self._state, self._fails, self._probe = "closed", 0, False

    def _on_failure(self):
        if self._state == "half":             # проба впала — знову відкрито
            return self._open()
        self._fails += 1
        if self._fails >= self._fails_to_open:
            self._open()

    def _open(self):
        self._state, self._opened_at, self._fails, self._probe = "open", monotonic(), 0, False
```
:::

Одну властивість тут варто назвати вголос, бо вона визначить порядок стосу: **запобіжник лічить запити, а не спроби**. Він бачить рівно один результат на кожен `call` — успіх або кінцеву відмову. Тому його треба поставити **зовні** повтору: тоді повтор крутить свої спроби всередині, а запобіжникові віддає лише підсумок. Якби повтор стояв зовні запобіжника, він гамселив би відкрите коло раз за разом і ховав відмови від лічильника — саме та пастка, від якої застерігала основна стаття.

## Таймаут зі скасуванням, повтор усередині, сигнал угору

Лишилися дві обгортки — таймаут і повтор — і спільна для всього мова помилок. Кожна помилка несе прапорець `retryable` — той самий **сигнал, що тече вгору** з [нашого стенда ланцюга](guide:progarch/resilient-call-chain): минущий збій (таймаут, «сервіс перевантажений» — 5xx) варто повторити, відповідь по суті (4xx — «поганий запит», «заборонено») і «коло відкрите» — ні.

Таймаут мусить не просто **облишити** повільний виклик, а **скасувати** його — інакше покинутий запит доганяє відповідь уже нікому не потрібним, тримаючи справжнє з'єднання донизу (і, як побачимо в тесті, слот перебірки). У TS це `AbortController`, у Python — `asyncio.wait_for`, який скасовує внутрішню корутину.

:::tabs
```ts
// Спільна мова помилок: прапорець retryable тече ВГОРУ по стосу.
class TimeoutError_ extends Error { readonly retryable = true; }
class Upstream5xx extends Error { readonly retryable = true;  constructor(readonly status: number) { super(`5xx ${status}`); } }
class Upstream4xx extends Error { readonly retryable = false; constructor(readonly status: number) { super(`4xx ${status}`); } }
const isRetryable = (e: unknown): boolean => !!(e as { retryable?: boolean })?.retryable;

// ТАЙМАУТ: скасовує виклик (abort), а не просто кидає його напризволяще.
function withTimeout<T>(ms: number, fn: (signal: AbortSignal) => Promise<T>): Promise<T> {
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), ms);
  return fn(ac.signal)
    .catch((e) => { throw ac.signal.aborted ? new TimeoutError_() : e; })
    .finally(() => clearTimeout(timer));
}

// ПОВТОР: до tries спроб, поки помилка ВАРТА повтору. Останню відмову — кидає далі
// (не ковтає!), тож її бачить запобіжник, що стоїть зовні.
async function withRetry<T>(tries: number, fn: () => Promise<T>): Promise<T> {
  let last: unknown;
  for (let i = 0; i < tries; i++) {
    try { return await fn(); }
    catch (e) { last = e; if (!isRetryable(e) || i === tries - 1) throw e; }
  }
  throw last;
}
```
```py
# Спільна мова помилок: прапорець retryable тече ВГОРУ по стосу.
import asyncio


class TimeoutErr(Exception):
    retryable = True


class Upstream5xx(Exception):
    retryable = True
    def __init__(self, status): super().__init__(f"5xx {status}"); self.status = status


class Upstream4xx(Exception):
    retryable = False
    def __init__(self, status): super().__init__(f"4xx {status}"); self.status = status


def is_retryable(e) -> bool:
    return getattr(e, "retryable", False)


# ТАЙМАУТ: wait_for скасовує внутрішню корутину, а не кидає її напризволяще.
async def with_timeout(seconds, fn):
    try:
        return await asyncio.wait_for(fn(), seconds)
    except asyncio.TimeoutError:
        raise TimeoutErr()


# ПОВТОР: до tries спроб, поки помилка ВАРТА повтору. Останню відмову — кидає далі
# (не ковтає!), тож її бачить запобіжник, що стоїть зовні.
async def with_retry(tries, fn):
    last = None
    for i in range(tries):
        try:
            return await fn()
        except Exception as e:
            last = e
            if not is_retryable(e) or i == tries - 1:
                raise
    raise last
```
:::

## Клієнт: стос у правильному порядку

Тепер зберімо все. `ServiceClient` — один на залежність — володіє своєю перебіркою й своїм запобіжником, а в `call` складає стос **ззовні всередину** рівно так, як ми вивели: перебірка (слот) → запобіжник (відкритий? — миттєво нагору) → повтор → таймаут на спробу → резолв адреси й сам HTTP. Мережу від резолву відділимо в `transport` — тонкий шов, який тест підмінить фейком, а прод під'єднає до реального `fetch`.

:::tabs
```ts
type Res = { status: number; body: unknown };
type Resolve = (dep: string) => Promise<string>;                          // реєстр виявлення
type Transport = (addr: string, path: string, body: unknown, s: AbortSignal) => Promise<Res>;

interface Limits { pool: number; queue: number; wait: number; timeout: number;
                   tries: number; failsToOpen: number; cooldown: number; }

class ServiceClient {
  private readonly bulkhead: Bulkhead;
  private readonly breaker: CircuitBreaker;
  constructor(
    private readonly dep: string,
    private readonly resolve: Resolve,
    private readonly transport: Transport,
    private readonly lim: Limits,
  ) {
    this.bulkhead = new Bulkhead(lim.pool, lim.queue, lim.wait);          // СВІЙ пул
    this.breaker  = new CircuitBreaker({ failsToOpen: lim.failsToOpen, cooldown: lim.cooldown }); // СВІЙ запобіжник
  }

  // Уся політика в ОДНОМУ стосі, ззовні всередину. Порядок — не косметика.
  call<T>(path: string, body: unknown): Promise<T> {
    return this.bulkhead.run(() =>                       // 1. слот із пулу цієї залежності / BulkheadFull
      this.breaker.call(() =>                            // 2. відкритий? → CircuitOpen, БЕЗ виклику
        withRetry(this.lim.tries, () =>                  // 3. повтор УСЕРЕДИНІ — відмови лічить запобіжник
          withTimeout(this.lim.timeout, (signal) =>      //   4. стеля на СПРОБУ + скасування
            this.send<T>(path, body, signal)))));        //     резолв адреси + HTTP
  }

  private async send<T>(path: string, body: unknown, signal: AbortSignal): Promise<T> {
    const addr = await this.resolve(this.dep);           // готовий екземпляр з реєстру
    const res = await this.transport(addr, path, body, signal);
    if (res.status >= 500) throw new Upstream5xx(res.status);   // минуще → повтор + лічба запобіжника
    if (res.status >= 400) throw new Upstream4xx(res.status);   // по суті → не повторюємо
    return res.body as T;
  }
}
```
```py
# transport(addr, path, body) -> {"status": int, "body": ...};  resolve(dep) -> адреса
class ServiceClient:
    def __init__(self, dep, resolve, transport, lim):
        self._dep = dep
        self._resolve = resolve
        self._transport = transport
        self._lim = lim
        self._bulkhead = Bulkhead(lim["pool"], lim["queue"], lim["wait"])          # СВІЙ пул
        self._breaker = CircuitBreaker(lim["fails_to_open"], lim["cooldown"])       # СВІЙ запобіжник

    # Уся політика в ОДНОМУ стосі, ззовні всередину. Порядок — не косметика.
    async def call(self, path, body):
        async def attempt():
            return await with_timeout(self._lim["timeout"],                  # 4. стеля на СПРОБУ + скасування
                                      lambda: self._send(path, body))
        async def retried():
            return await with_retry(self._lim["tries"], attempt)             # 3. повтор УСЕРЕДИНІ
        return await self._bulkhead.run(                                     # 1. слот / BulkheadFull
            lambda: self._breaker.call(retried))                             # 2. відкритий? → CircuitOpen

    async def _send(self, path, body):
        addr = await self._resolve(self._dep)            # готовий екземпляр з реєстру
        res = await self._transport(addr, path, body)
        if res["status"] >= 500:
            raise Upstream5xx(res["status"])             # минуще → повтор + лічба запобіжника
        if res["status"] >= 400:
            raise Upstream4xx(res["status"])             # по суті → не повторюємо
        return res["body"]
```
:::

Тепер — два клієнти з **різними** ручками й два каллери, у яких вся різниця стійкості вкладається в одне: є `.catch` чи нема. Телеметрія дістає малий пул, fail-fast і терплячий таймаут; ядро — більший пул із короткою чергою й тугіший таймаут. Головний екран кличе **обидва**, але телеметрію обгортає чесним фолбеком; команда «зачинити» йде тим самим клієнтом ядра — і **без** фолбека.

:::tabs
```ts
const telemetry = new ServiceClient("telemetry", resolve, http,
  { pool: 10, queue: 0,  wait: 0,   timeout: 3000, tries: 2, failsToOpen: 5,  cooldown: 2000 }); // fail-fast
const core = new ServiceClient("core", resolve, http,
  { pool: 40, queue: 40, wait: 200, timeout: 1000, tries: 2, failsToOpen: 10, cooldown: 1000 }); // коротка черга

// ЧИТАННЯ: телеметрія — прикраса, тож у неї є ЧЕСНИЙ фолбек. Список пристроїв критичний — фолбека нема.
async function mainScreen(userId: string) {
  const [devices, readings] = await Promise.all([
    core.call<Device[]>("/listDevices", { userId }),                 // свій пул; впаде — екран чесно не збереться
    telemetry.call<Reading[]>("/lastReadings", { userId })
      .catch(() => [] as Reading[]),                                 // ← фолбек: без виміру
  ]);
  const byId = new Map(readings.map((r) => [r.deviceId, r]));
  return devices.map((d) => ({ device: d, reading: byId.get(d.id) ?? null })); // null → плитка «—»
}

// КОМАНДА: той самий стос стійкості — але БЕЗ .catch. Не дотягнулись — помилка летить нагору,
// UI покаже «не вдалося, спробуйте ще», а не збреше «зачинено». Повтор безпечний, бо команда ідемпотентна.
async function lockDoor(deviceId: string): Promise<LockResult> {
  return core.call<LockResult>("/command", { deviceId, op: "lock" });
}
```
```py
telemetry = ServiceClient("telemetry", resolve, http,
    {"pool": 10, "queue": 0,  "wait": 0.0, "timeout": 3.0, "tries": 2, "fails_to_open": 5,  "cooldown": 2.0})
core = ServiceClient("core", resolve, http,
    {"pool": 40, "queue": 40, "wait": 0.2, "timeout": 1.0, "tries": 2, "fails_to_open": 10, "cooldown": 1.0})


# ЧИТАННЯ: телеметрія — прикраса, тож у неї є ЧЕСНИЙ фолбек. Список пристроїв критичний — фолбека нема.
async def main_screen(user_id):
    async def readings_or_empty():
        try:
            return await telemetry.call("/lastReadings", {"userId": user_id})
        except Exception:
            return []                                   # ← фолбек: без виміру
    devices, readings = await asyncio.gather(
        core.call("/listDevices", {"userId": user_id}),  # свій пул; впаде — екран чесно не збереться
        readings_or_empty(),
    )
    by_id = {r["deviceId"]: r for r in readings}
    return [{"device": d, "reading": by_id.get(d["id"])} for d in devices]  # None → плитка «—»


# КОМАНДА: той самий стос — але БЕЗ except-фолбека. Не дотягнулись — помилка нагору.
# Повтор безпечний, бо команду ми зробили ідемпотентною ще на межі з домом.
async def lock_door(device_id):
    return await core.call("/command", {"deviceId": device_id, "op": "lock"})
```
:::

Ось де вся конструкція окупається одним поглядом: `mainScreen` і `lockDoor` ходять крізь **той самий** клієнт із **тим самим** стосом, а різниця стійкості — рівно в наявності `.catch`. Клієнт не знає й не мусить знати, що телеметрію можна підмінити, а замок — ні; він дає стійкість, а сенс «чим замінити» лишає каллеру. І повтор на команді безпечний не випадково: ми зробили команди [ідемпотентними ще на межі з домом](guide:progarch/dh-bad-network), тож дві однакові спроби «зачинити» не зачиняють двічі.

![Три каллери ліворуч (читання виміру, список пристроїв, команда «зачинити») ведуть до клієнтів у центрі: ServiceClient «telemetry» зі своїм пулом 10 fail-fast і ServiceClient «core» зі своїм пулом 40 та чергою; праворуч виходи — від телеметрії зелений фолбек «—» без виміру, від ядра для списку звичайний вихід, а для команди бурштиновий «БЕЗ фолбека: чесна відмова». Підпис: той самий клієнт на кожен шов, окремий пул — окремий радіус ураження, фолбек у каллера](/guide/progarch/service-infrastructure-resilience/dh-resilient-path/img/client-stack.svg)

*Один клієнт, стос на кожну залежність. Телеметрія й ядро мають окремі пули — окремі радіуси ураження; а фолбек не в клієнті, а в каллера, тому читання деградує до «—», а команда «зачинити» дістає чесну відмову, не фальшиве «зачинено».*

> 🔧 **Навіщо це.** Спільний клієнт перетворює стійкість із **звички** на **властивість шва**. У наївному коді кожен новий виклик — це нове запрошення забути обгортку; у клієнта забути її нема як, бо єдиний спосіб покликати сусіда — це `call`, а `call` уже несе перебірку, запобіжник і таймаут. Політику зібрано раз, у правильному порядку, і вона тримається на шостому шві так само, як на першому.

## Сторож: збірка червона на сирому HTTP

Клієнт дає правильний шлях, але сам по собі не забороняє **обхідний**. Хтось під дедлайн допише `await fetch("http://telemetry/lastReadings")` прямо в BFF — «лише сьогодні, потім винесу», — і той рядок тихо повертає весь каскад: сирий виклик без пулу, без запобіжника, без таймаута знову здатен вичерпати робітників і покласти екран. Юніт-тести зелені, рев'ю о шостій проґавило.

Тому поставимо сторожа — прямий рідний брат [сторожа топології](guide:progarch/dh-service-boundaries-final/proj-dh-final-topology.md), що вже валить збірку на ребрі поза мапою. Правило одне: **сирий міжсервісний HTTP дозволено рівно в одному місці — у модулі клієнта**. Сканер дає список усіх викликів `fetch`/`http`/`axios` у коді з файлом, рядком і хостом; суддя лишає ті, що ведуть у відомий сервіс **повз** файл клієнта.

:::tabs
```ts
// arch/no-raw-cross-service.ts — фітнес-тест: сирий міжсервісний HTTP дозволено ЛИШЕ в клієнті.
const CLIENT = "infra/service-client.ts";                  // єдине легальне місце
const SERVICES = new Set(["telemetry", "core", "video", "hub", "payments", "push"]);

// Сканер дав кожен вихідний HTTP-виклик: файл, рядок, хост (якщо статичний), текст.
type RawCall = { file: string; line: number; host: string; text: string };

export function violations(calls: RawCall[]): string[] {
  return calls
    .filter((c) => c.file !== CLIENT && SERVICES.has(c.host))   // йде в сусідній сервіс повз клієнт
    .map((c) => `${c.file}:${c.line} — сирий HTTP у «${c.host}» повз ServiceClient: ${c.text.trim()}`);
}

export function main(calls: RawCall[]): number {
  const bad = violations(calls);
  if (bad.length === 0) { console.log("усі міжсервісні виклики йдуть крізь клієнт"); return 0; }
  console.error("ЗРАДА КЛІЄНТА DH:");
  for (const b of bad) console.error("  " + b);
  return 1;                       // exit 1 → CI червоний → merge заблоковано
}
```
```py
# arch/no_raw_cross_service.py — фітнес-тест: сирий міжсервісний HTTP дозволено ЛИШЕ в клієнті.
CLIENT = "infra/service_client.py"                          # єдине легальне місце
SERVICES = {"telemetry", "core", "video", "hub", "payments", "push"}


def violations(calls):     # calls: [{"file","line","host","text"}] від сканера
    bad = []
    for c in calls:
        if c["file"] != CLIENT and c["host"] in SERVICES:      # йде в сусідній сервіс повз клієнт
            bad.append(f'{c["file"]}:{c["line"]} — сирий HTTP у «{c["host"]}» повз ServiceClient: {c["text"].strip()}')
    return bad


def main(calls):
    bad = violations(calls)
    if not bad:
        print("усі міжсервісні виклики йдуть крізь клієнт")
        return 0
    print("ЗРАДА КЛІЄНТА DH:")
    for b in bad:
        print("  " + b)
    return 1                        # exit 1 → CI червоний → merge заблоковано
```
:::

Той злощасний рядок у BFF сканер бачить як `fetch` у хост `telemetry` з файлу, що не є клієнтом, — і збірка червоніє:

```
ЗРАДА КЛІЄНТА DH:
  bff/main-screen.ts:42 — сирий HTTP у «telemetry» повз ServiceClient: await fetch(`http://telemetry/lastReadings`, …)
```

exit 1 — merge заблоковано. Прибираєш сирий `fetch`, кличеш `telemetry.call("/lastReadings", …)` — і та сама перевірка каже `усі міжсервісні виклики йдуть крізь клієнт` з кодом 0. Тепер стійкість не тримається на дисципліні автора: обхід просто не збирається.

## Довести на живому: задушити телеметрію

Лишилось найцікавіше — **показати** числами, що клієнт робить те, що обіцяє. Зберімо крихітну фейкову мережу, яка рахує **одночасні** виклики на кожен сервіс і вміє душити телеметрію: у режимі `slow` вона висить п'ять секунд (довше за таймаут — тож таймаут скасує), у `fail` — швидко віддає 503. Клієнт справжній, підмінили лише `transport`.

:::tabs
```ts
// Фейкова мережа: лічить ОДНОЧАСНІ виклики на сервіс і душить телеметрію.
const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

class FakeNet {
  maxConc: Record<string, number> = {};
  private live: Record<string, number> = {};
  telemetryMode: "healthy" | "slow" | "fail" = "healthy";

  transportFor(dep: string): Transport {
    return async (_addr, _path, _body, signal) => {
      this.live[dep] = (this.live[dep] ?? 0) + 1;
      this.maxConc[dep] = Math.max(this.maxConc[dep] ?? 0, this.live[dep]);
      try {
        if (dep === "telemetry" && this.telemetryMode === "slow") {
          await abortable(5000, signal);                       // висить 5 с; таймаут скасує на 3-й
          return { status: 200, body: [] };
        }
        if (dep === "telemetry" && this.telemetryMode === "fail") {
          await delay(20); return { status: 503, body: null }; // швидко падає
        }
        await delay(20); return { status: 200, body: sample(dep) };
      } finally { this.live[dep]--; }
    };
  }
}
// abortable: чекає ms, але прокидається помилкою, щойно таймаут викликав abort (скасування).
function abortable(ms: number, signal: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const t = setTimeout(resolve, ms);
    signal.addEventListener("abort", () => { clearTimeout(t); reject(new Error("aborted")); });
  });
}

async function testDegradeAndIsolate() {
  const net = new FakeNet();
  net.telemetryMode = "slow";                                 // ← душимо телеметрію
  // 50 головних екранів + 10 команд «зачинити», усі водночас.
  const screens = Array.from({ length: 50 }, (_, i) => timed(() => mainScreen(`u${i}`)));
  const cmds = Array.from({ length: 10 }, (_, i) => lockDoor(`d${i}`));
  const [tiles, cmdRes] = await Promise.all([Promise.all(screens), Promise.allSettled(cmds)]);

  // 1. Екран ДЕГРАДУВАВ, а не завис: кожна плитка має пристрій, але reading = null.
  assert(tiles.every((t) => t.value.every((x) => x.device && x.reading === null)));
  // 2. Телеметрія НЕ з'їла більше за свій пул; ядро качало вільно.
  assert(net.maxConc.telemetry <= 10);
  assert(net.maxConc.core >= 40);
  // 3. БІЛЬШІСТЬ екранів повернулись швидко (миттєвий «відсік повний» → фолбек).
  assert(tiles.filter((t) => t.ms < 100).length >= 40);
  // 4. Усі команди пройшли своїм пулом — жодної брехні «зачинено».
  assert(cmdRes.every((c) => c.status === "fulfilled"));
  console.log("деградація й ізоляція: OK", net.maxConc);
}
```
```py
import asyncio


class FakeNet:
    def __init__(self):
        self.max_conc = {}
        self._live = {}
        self.telemetry_mode = "healthy"

    def transport_for(self, dep):
        async def transport(_addr, _path, _body):
            self._live[dep] = self._live.get(dep, 0) + 1
            self.max_conc[dep] = max(self.max_conc.get(dep, 0), self._live[dep])
            try:
                if dep == "telemetry" and self.telemetry_mode == "slow":
                    await asyncio.sleep(5.0)                    # висить 5 с; wait_for скасує на 3-й
                    return {"status": 200, "body": []}
                if dep == "telemetry" and self.telemetry_mode == "fail":
                    await asyncio.sleep(0.02); return {"status": 503, "body": None}
                await asyncio.sleep(0.02); return {"status": 200, "body": sample(dep)}
            finally:
                self._live[dep] -= 1
        return transport


async def test_degrade_and_isolate():
    net = FakeNet()
    net.telemetry_mode = "slow"                                # ← душимо телеметрію
    screens = [timed(main_screen(f"u{i}")) for i in range(50)]
    cmds = [lock_door(f"d{i}") for i in range(10)]
    tiles, cmd_res = await asyncio.gather(
        asyncio.gather(*screens),
        asyncio.gather(*cmds, return_exceptions=True),
    )
    # 1. Екран ДЕГРАДУВАВ, а не завис: пристрій є, reading = None.
    assert all(all(x["device"] and x["reading"] is None for x in t.value) for t in tiles)
    # 2. Телеметрія НЕ з'їла більше за свій пул; ядро качало вільно.
    assert net.max_conc["telemetry"] <= 10
    assert net.max_conc["core"] >= 40
    # 3. БІЛЬШІСТЬ екранів повернулись швидко (миттєвий «відсік повний» → фолбек).
    assert sum(1 for t in tiles if t.ms < 0.1) >= 40
    # 4. Усі команди пройшли — жодної брехні «зачинено».
    assert all(not isinstance(c, Exception) for c in cmd_res)
    print("деградація й ізоляція: OK", net.max_conc)
```
:::

Прочитаймо, що саме доводить кожне твердження — і хто його забезпечив.

**Твердження 2 — це перебірка.** П'ятдесят екранів кинулись у телеметрію, але одночасних викликів у ній ніколи не більше **десяти**: одинадцятий і далі дістають `BulkheadFull` синхронно, тобто миттєво. Сорок запитів навіть не торкнулись задушеного сервісу. А `maxConc.core ≥ 40` каже, що ядро тим часом качало на повну — його пул телеметрія не бачить і вичерпати не може.

**Твердження 3 — це чому екран не завис.** Ті сорок, що дістали `BulkheadFull`, повернулись за мілісекунди (домінує швидкий виклик ядра), підмінивши вимір рискою. Завис лише невеликий перший вал — десять, що встигли схопити слоти до того, як пул забився; вони чекають таймаут (три секунди, не п'ять — скасування!), тоді фолбек. Перебірка обмежує **скільки** запитів заплатять; запобіжник, розімкнувшись за п'ять відмов, обмежує, як **довго** триває інцидент: далі вже всі миттєві.

**Твердження 4 — це окремий пул ядра.** Десять команд «зачинити» пройшли, бо йшли **своїм** пулом крізь здорове ядро; задушена телеметрія до них не дотяглася. І — головне — жодна не збрехала: команда, що не дійшла б, віддала б помилку нагору, а не фальшиве «зачинено».

![Тест на двох панелях. Ліворуч задушена телеметрія: пул на десять слотів увесь зайнятий (висять до таймаута 3 с), 40 викликів дістають миттєвий «відсік повний» і фолбек «—», запобіжник після 5 відмов відкривається; підсумок — усі 50 екранів показують пристрій із рискою, жоден не завис. Праворуч здорове ядро зі своїм пулом на 40: 50 списків і 10 команд проходять усі, жодної брехні «зачинено». Унизу стрічка тверджень тесту](/guide/progarch/service-infrastructure-resilience/dh-resilient-path/img/burst-test.svg)

*Задушену телеметрію тримає її власний пул — потоп лишається в одному відсіку. Головний екран деградує до «пристрій без виміру», а список пристроїв і команди течуть незалежним пулом ядра. Числа, а не обіцянка: одночасних викликів у телеметрії ≤ 10, ядро качає на повну, усі команди чесні.*

## Складність і пастки

Клієнт вище — робочий, але між «працює на демо» й «на нього можна покластися вночі» лежить кілька місць, де легко тихо помилитися.

**Розмір пулу — це trade-off, а не «що більше, то краще».** Замалий пул душить у нормі: дай телеметрії десять слотів — і чесний пік у одинадцять паралельних читань упреться в стіну, хоча ресурс у системи є. Завеликий не рятує в біду: пул на сто, коли робітників у BFF двадцять, ніколи не спрацює як огорожа — телеметрія забере всіх двадцять раніше, ніж наблизиться до своєї сотні. Здоровий орієнтир — пул трохи більший за нормальну одночасність цієї залежності, але помітно **менший** за загальний ресурс сервера; точку вибирають вимірюванням, а не смаком, і [де саме її ставити — окреме рішення](guide:progarch/resilience-placement-choice).

**Fail-fast чи черга — залежить від того, чи є фолбек.** Телеметрія (є фолбек) — fail-fast: нема слота, віддай рису й не тримай ресурс. Ядро (фолбека нема) — коротка **обмежена** черга: хай запит зачекає мілісекунди, ніж дістане відмову. Але черга без стелі — прихована яма: під навантаженням у ній назбирується хвіст, і затримка, якої ти уникав таймаутом, повертається як час у черзі. Тому в семафорі є `maxWait` — черга теж мусить здаватися. Черга без стелі — це відкладена каскадна відмова.

**Поріг і кулдаун — теж пара з trade-off.** Поріг замалий (розмикатись від однієї-двох відмов) — і випадковий збій вимикає живий сервіс; завеликий — і запобіжник спізнюється, пропустивши сотні марних викликів у явно мертвий бік. Кулдаун закороткий — і напіввідкрита проба б'є в сервіс, який ще не встав, знову його валить; задовгий — і ти тримаєш коло розімкненим довго по тому, як сусід одужав. Розумний початок — поріг у кілька відмов **поспіль** (не «N із M за вікно» — це складніше й пізніше), кулдаун у секунди; далі підправляють за реальними інцидентами.

**Запобіжник мусить лічити правильні відмови.** Таймаут і 5xx — «сервіс захворів», їх рахуємо (тому таймаут і стоїть **усередині** запобіжника, щоб той його бачив). А 4xx — «поганий запит» — це **не** хвороба сервісу; рахувати його як відмову означало б розмикати коло від власних помилок каллера. У `send` ми навмисне ділимо: 5xx кидає `Upstream5xx` (retryable, лічиться), 4xx — `Upstream4xx` (не retryable). І `CircuitOpen` сам собі не додається в лічильник, бо кидається **до** `try`.

**Таймаут без скасування — фальшивий таймаут.** Якби `withTimeout` просто кидав помилку, не скасовуючи виклик, покинутий запит доганяв би відповідь, тримаючи справжнє з'єднання донизу й **слот перебірки** — той самий десятий слот, який мав звільнитися. У тесті це видно: сон на п'ять секунд у режимі `slow` уривається на третій, бо `abort`/`wait_for` справді скасовує роботу. Без скасування пул телеметрії тік би не за таймаутом, а за повною довжиною залипання.

**Напіввідкритий стан у справжній конкурентності.** Наш прапорець «проба в польоті» тримається на тому, що `allow()` синхронний, а рушій однопотоковий — між `await` ніхто не влізе. У Go чи Java з реальними потоками цієї гарантії немає: там та сама перевірка потребує м'ютекса (як `Breaker.mu` у [стенді ланцюга](guide:progarch/resilient-call-chain)), інакше натовп проб проскочить одночасно й повалить ледь оживлений сервіс. Однопотоковість — не завжди наявна розкіш.

**Ізоляція справжня, лише поки стан справді окремий.** Уся конструкція тримається на тому, що `telemetry` і `core` — **різні** екземпляри `ServiceClient`, кожен зі своїм пулом і запобіжником. Один спокусливий рефакторинг — «винесімо запобіжник у синглтон, щоб не плодити» — і ти нишком повернув спільний ресурс: тепер відмови телеметрії відкривають коло, крізь яке ходить і ядро. Окремий стан на залежність — не деталь реалізації, а сам сенс перебірки; спільний пул чи спільний запобіжник знищує ізоляцію тихо, без жодної помилки компіляції.

**Ретрай на прикрасі варто зважити.** Ми лишили телеметрії `tries: 2`, щоб код був симетричний, — але фолбек у неї **дешевий** (риска «—»), а два таймаути по три секунди тримають слот **удвічі** довше. Тверезий вибір для читання з дешевим фолбеком — часто `tries: 1`: не дочекався з першого разу — не мучся, віддай рису. Повтор беззастережно доречний там, де фолбека нема й відповідь варта боротьби, — на **команді**, і лише тому, що вона ідемпотентна. Повтор — не безкоштовний рефлекс; він коштує утримання слота.

**Сторож бачить лише те, що може назвати.** Статичний сканер ловить `fetch("http://telemetry/…")` зі **сталим** хостом. Виклик, де адресу зібрано з рядка (`fetch(base + path)`), він не впізнає — той самий сліпий бік, що й у сторожа топології. Дірку прикривають з іншого боку: лінт-правило, що забороняє **сам глобальний** `fetch` (чи імпорт `axios`/`undici`/`requests`) деінде, крім модуля клієнта, — тоді обхід не збереться, навіть якщо хост динамічний. Сканер хостів і заборона глобала стережуть **одне** з двох боків.

**Клієнт мусить бути одним опублікованим артефактом.** Сервіси DH — окремі репозиторії з окремими конвеєрами. Якщо клієнт скопіювати в кожен, копії розповзуться: один сервіс уже з новим кулдауном, інший зі старим, і «спільна політика» стає міфом. Клієнт (і сторож при ньому) — **один** пакет, який тягнуть **усі** пайплайни; редагується він в одному місці, а не форкається під дедлайн. Одне джерело політики — багато споживачів.

## Що лишається в руках

Ми зібрали те, що основна стаття лише пообіцяла п'ятьма рядками: робочий спільний клієнт, у якому перебірка на семафорі, запобіжник на три стани з однією пробою, таймаут зі скасуванням і повтор під сигналом «варто/не варто» складені **в один стос у правильному порядку** — слот, запобіжник, повтор, таймаут, виклик — поверх резолву адреси через реєстр. Кожна залежність дістає **свій** стос, тож біда однієї лишається в її відсіку; фолбек винесено до каллера, тож читання деградує до «—», а команда «зачинити» дістає чесну відмову, не фальшиве «зачинено». Сторож валить збірку на сирому HTTP повз клієнт, а тест на задушеній телеметрії довів числами: одночасних викликів у ній ≤ 10, ядро й команди течуть окремим пулом, екран деградує однією плиткою, а не всією системою.

І ось межа, до якої цей клієнт довів нас чесно — і за яку він не заходить. Він питав реєстр «чи готовий сервіс», ставив таймаут, лічив відмови — але жодного разу не спитав, **чи можна цьому запитові** те, що він просить. Клієнт тримає шлях відкритим і швидким; він нічого не каже про те, **кому** той шлях відкритий. Стійкість — це «встигну чи ні»; наступний критичний вузол — «пущу чи ні», і саме він, на відміну від виміру телеметрії, не має права на жоден фолбек.
