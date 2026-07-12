# ⚙️ Сага «завести пристрій» — повний код двома стилями

Зерна обох стилів уже в руках: коротка хореографія з чотирьох обробників і коротка функція-оркестратор зі списком `undo`. На зернах видно головне — де живе знання про процес. Але зерна тихо оминули три речі, а саме в них уся інженерія: **повний ланцюг компенсацій**, коли падає не перший крок; **збій посеред саги**, коли гине не крок, а сам процес; і **тест**, що ловить найпідступнішу ваду хореографії — її розповзання. Зберімо тут усе це так, щоб воно **запускалося**. Візьмімо ту саму маленьку сагу — завести новий пристрій у дім: (1) зарезервувати його в реєстрі, (2) залити конфіг на хаб, (3) увімкнути облік у білінгу — і пройдімо її обома способами до кінця. Сама ідея розбивати ділову дію на локальні транзакції з компенсаціями — це [патерн саги](book:programming/saga-pattern); тут ми не пояснюємо його, а **втілюємо**.

## Світ саги — три сервіси, які можна повалити

Щоб приклад був чесний і запускався як є, змоделюймо три сервіси в пам'яті. Кожен має свою дію та її компенсацію, і в кожного — прапорець `down`, яким ми вмикаємо збій там, де захочемо. У бою за цими методами ховаються мережеві виклики; тут вони — прості множини, бо нас цікавить **координація**, а не нутрощі сервісів.

:::tabs
```ts
// Три сервіси DH. Кожна дія має компенсацію; прапорець down імітує відмову.
class Registry {
  reserved = new Set<string>();
  async reserve(deviceId: string, homeId: string) { this.reserved.add(deviceId); }
  async unreserve(deviceId: string)               { this.reserved.delete(deviceId); }
}
class Hub {
  configured = new Set<string>(); down = false;
  async pushConfig(homeId: string, deviceId: string) {
    if (this.down) throw new Error("хаб недоступний");
    this.configured.add(deviceId);
  }
  async wipeConfig(homeId: string, deviceId: string) { this.configured.delete(deviceId); }
}
class Billing {
  metered = new Set<string>(); down = false;
  async startMeter(homeId: string, deviceId: string) {
    if (this.down) throw new Error("білінг недоступний");
    this.metered.add(deviceId);
  }
  async stopMeter(homeId: string, deviceId: string) { this.metered.delete(deviceId); }
}

type Enroll = { homeId: string; deviceId: string };
```
```py
# Три сервіси DH. Кожна дія має компенсацію; прапорець down імітує відмову.
from dataclasses import dataclass

class Registry:
    def __init__(self): self.reserved = set()
    async def reserve(self, device_id, home_id): self.reserved.add(device_id)
    async def unreserve(self, device_id):        self.reserved.discard(device_id)

class Hub:
    def __init__(self): self.configured = set(); self.down = False
    async def push_config(self, home_id, device_id):
        if self.down: raise RuntimeError("хаб недоступний")
        self.configured.add(device_id)
    async def wipe_config(self, home_id, device_id): self.configured.discard(device_id)

class Billing:
    def __init__(self): self.metered = set(); self.down = False
    async def start_meter(self, home_id, device_id):
        if self.down: raise RuntimeError("білінг недоступний")
        self.metered.add(device_id)
    async def stop_meter(self, home_id, device_id): self.metered.discard(device_id)

@dataclass
class Enroll:
    home_id: str
    device_id: str
```
:::

Три сервіси, шість методів — три дії й три компенсації, дзеркальні до них. Це весь наш світ. Тепер двічі проведемо крізь нього одну сагу, змінивши **тільки координацію**.

## Хореографія повністю — і друга, прихована мережа

У зерні хореографія обірвалася на компенсації першого кроку. Але сага має три кроки, і компенсувати доводиться з **будь-якої** висоти падіння. Ось де відкривається те, про що зерно змовчало: компенсації в хореографії — це **друга мережа підписок**, яка їде **у зворотний бік**, і вона так само ніде не зібрана. Хореографія стоїть на [публікації-підписці — продюсер кидає подію, не знаючи, хто зреагує](book:programming/publish-subscribe); зберімо на ній обидві мережі — пряму й компенсаційну.

:::tabs
```ts
type Handler = (e: Enroll) => Promise<void>;

class Bus {                                  // проста шина подій
  private subs = new Map<string, Handler[]>();
  on(ev: string, fn: Handler) { const a = this.subs.get(ev) ?? []; a.push(fn); this.subs.set(ev, a); }
  async emit(ev: string, e: Enroll) { for (const fn of this.subs.get(ev) ?? []) await fn(e); }
}

function wireChoreography(bus: Bus, registry: Registry, hub: Hub, billing: Billing) {
  // ── ПРЯМА мережа: крок завершив — кинув подію, наступний підхопив ──
  bus.on("DeviceReserveRequested", async e => {
    await registry.reserve(e.deviceId, e.homeId);
    await bus.emit("DeviceReserved", e);                 // хто підхопить — реєстр не знає
  });
  bus.on("DeviceReserved", async e => {
    try { await hub.pushConfig(e.homeId, e.deviceId); await bus.emit("DeviceConfigured", e); }
    catch { await bus.emit("DeviceConfigFailed", e); }   // впав — запускаємо відкіт
  });
  bus.on("DeviceConfigured", async e => {
    try { await billing.startMeter(e.homeId, e.deviceId); }   // останній крок: тиша = «готово»
    catch { await bus.emit("DeviceMeterFailed", e); }
  });

  // ── КОМПЕНСАЦІЙНА мережа: окремі підписки, що їдуть НАЗАД ──
  bus.on("DeviceConfigFailed", async e => {              // упав крок 2 → відкотити крок 1
    await registry.unreserve(e.deviceId);
  });
  bus.on("DeviceMeterFailed", async e => {               // упав крок 3 → відкотити крок 2…
    await hub.wipeConfig(e.homeId, e.deviceId);
    await bus.emit("DeviceConfigCompensated", e);        // …і лише тоді ланцюг іде далі назад
  });
  bus.on("DeviceConfigCompensated", async e => {         // …→ відкотити крок 1
    await registry.unreserve(e.deviceId);
  });
}
```
```py
class Bus:                                   # проста шина подій
    def __init__(self): self.subs = {}
    def on(self, ev, fn): self.subs.setdefault(ev, []).append(fn)
    async def emit(self, ev, e):
        for fn in list(self.subs.get(ev, [])): await fn(e)

def wire_choreography(bus, registry, hub, billing):
    # ── ПРЯМА мережа: крок завершив — кинув подію, наступний підхопив ──
    async def on_requested(e):
        await registry.reserve(e.device_id, e.home_id)
        await bus.emit("DeviceReserved", e)                 # хто підхопить — реєстр не знає
    async def on_reserved(e):
        try:
            await hub.push_config(e.home_id, e.device_id); await bus.emit("DeviceConfigured", e)
        except Exception:
            await bus.emit("DeviceConfigFailed", e)          # впав — запускаємо відкіт
    async def on_configured(e):
        try:
            await billing.start_meter(e.home_id, e.device_id)   # останній крок: тиша = «готово»
        except Exception:
            await bus.emit("DeviceMeterFailed", e)

    # ── КОМПЕНСАЦІЙНА мережа: окремі підписки, що їдуть НАЗАД ──
    async def on_config_failed(e):                          # упав крок 2 → відкотити крок 1
        await registry.unreserve(e.device_id)
    async def on_meter_failed(e):                           # упав крок 3 → відкотити крок 2…
        await hub.wipe_config(e.home_id, e.device_id)
        await bus.emit("DeviceConfigCompensated", e)        # …і лише тоді ланцюг іде далі назад
    async def on_config_compensated(e):                     # …→ відкотити крок 1
        await registry.unreserve(e.device_id)

    bus.on("DeviceReserveRequested", on_requested)
    bus.on("DeviceReserved", on_reserved)
    bus.on("DeviceConfigured", on_configured)
    bus.on("DeviceConfigFailed", on_config_failed)
    bus.on("DeviceMeterFailed", on_meter_failed)
    bus.on("DeviceConfigCompensated", on_config_compensated)
```
:::

Придивися, що тут насправді відбулося. Прямих обробників три, а компенсаційних — теж окрема жменя, і вони **не суміжні** з прямими: щоб відкотити крок 2 після падіння кроку 3, я емітю `DeviceMeterFailed`, той обробник робить `wipeConfig` і **кидає ще одну подію** `DeviceConfigCompensated`, і аж вона відкочує крок 1. Тобто компенсації самі вишикувані в **ланцюг подій**, що повзе назад, — і що глибше впала сага, то довший цей задній хвіст. Ніде в цьому файлі не написано слова «сага». Процес як ціле не зібраний **ніде** — ні пряма нитка, ні зворотна; обидві лише **проступають** із того, хто на що підписаний.

Запустімо збій на кроці 2 — повалимо хаб (`hub.down = true`) — і подивімося на слід:

```
emit DeviceReserveRequested { dev-42 }
  registry.reserve(dev-42) ✓              → emit DeviceReserved
  hub.pushConfig(dev-42) ✗ «хаб недоступний» → emit DeviceConfigFailed
  registry.unreserve(dev-42) ✓             (компенсація кроку 1)
підсумок:  reserved = {}   configured = {}   ← чисто
```

Відкат кроку 1 спрацював — реєстр порожній. Але зверни увагу, **як** ми це дізналися: довелося подумки пройти три прямі обробники, тоді три компенсаційні, і **скласти танець у голові**. Ніхто в системі не міг би відповісти на запит «покажи мені сагу пристрою dev-42» — бо саги як об'єкта не існує.

> 🔧 **Навіщо це.** Дві мережі замість однієї — ось прихована ціна хореографії, якої не видно на щасливому шляху. Поки все проходить, компенсаційні підписки мовчать, і система здається простою. Перша ж реальна відмова вмикає той задній ланцюг — і тепер, щоб зрозуміти, що станеться, треба тримати в голові **обидві** мережі одразу. Додай сюди циклічну підписку (подія-компенсація будить обробник, що емітить ще одну подію) — і отримаєш відкіт, який ніхто не годен простежити очима.

## Оркестрація наївна — весь процес в одній функції

Тепер той самий процес, зібраний в одну функцію. Це той оркестратор, що ми бачили в зерні, лиш випишемо його повністю. Уся сага читається згори вниз, а компенсації складаються в список `undo` й спрацьовують точно у зворотному порядку — останнє зроблене відкочується першим.

:::tabs
```ts
async function enrollDevice(registry: Registry, hub: Hub, billing: Billing,
                            homeId: string, deviceId: string) {
  const undo: Array<() => Promise<void>> = [];
  try {
    await registry.reserve(deviceId, homeId);   undo.push(() => registry.unreserve(deviceId));
    await hub.pushConfig(homeId, deviceId);      undo.push(() => hub.wipeConfig(homeId, deviceId));
    await billing.startMeter(homeId, deviceId);  undo.push(() => billing.stopMeter(homeId, deviceId));
  } catch (err) {
    for (const step of undo.reverse()) await step();   // компенсації — точно у зворотному порядку
    throw err;
  }
}
```
```py
async def enroll_device(registry, hub, billing, home_id, device_id):
    undo = []
    try:
        await registry.reserve(device_id, home_id);    undo.append(lambda: registry.unreserve(device_id))
        await hub.push_config(home_id, device_id);      undo.append(lambda: hub.wipe_config(home_id, device_id))
        await billing.start_meter(home_id, device_id);  undo.append(lambda: billing.stop_meter(home_id, device_id))
    except Exception:
        for step in reversed(undo): await step()        # компенсації — точно у зворотному порядку
        raise
```
:::

Той самий збій на кроці 2 читається тут без жодного стрибка очима:

```
enrollDevice(home-7, dev-42)
  registry.reserve(dev-42) ✓     undo = [ unreserve ]
  hub.pushConfig ✗ «хаб недоступний»
  → catch: undo.reverse() →
  registry.unreserve(dev-42) ✓
кинуто помилку;  reserved = {}   ← чисто
```

Різниця не в кількості коду — рядків тут навіть менше. Різниця в тому, що **порядок кроків і порядок компенсацій зібрані в одному місці**, видимі одним поглядом. Такий оркестратор — це, по суті, [явний автомат станів, як життєвий цикл пристрою, що ми вже малювали](guide:progarch/dh-device-fsm): є стан «зарезервовано», «сконфігуровано», «відкочується».

Але в цьому наївному варіанті сидить діра, і вона глибша за будь-яку відмову сервісу. Список `undo` живе в **пам'яті процесу**. А що, як помре не крок, а сам **процес** — між кроком 1 і кроком 2? Не виняток, який ми зловимо, а SIGKILL, перезапуск контейнера, впав вузол:

```
enrollDevice(home-7, dev-42)
  registry.reserve(dev-42) ✓     undo = [ unreserve ]   ← у пам'яті процесу
  💀 процес помер (SIGKILL) — стек згорнувся, undo зник разом із ним
підсумок:  reserved = { dev-42 }   ← сирота: нема кому відкотити, нема запису «де сага»
```

Пристрій лишився зарезервованим **назавжди**. Ніхто не знає, що сагу почато й не докінчено, бо єдиний, хто це знав, — список `undo` у стеку мертвого процесу. Це не крайовий випадок: процеси вмирають щодня — деплой, автоскейл, OOM. Наївний оркестратор перетворює кожну таку смерть посеред саги на тихого сироту в реєстрі.

![Дві смуги, розділені вертикальною лінією «процес помер тут». Верхня — наївний оркестратор: після reserve стан undo лежить у пам'яті процесу й губиться разом із ним; праворуч від смерті реєстр тримає dev-42 назавжди, відкотити нема кому, статусу нема. Нижня — довговічний рушій: після reserve крок зафіксовано на диску (cursor=1), диск переживає смерть процесу, і новий процес читає диск, доробляє config та meter, сага завершується](/guide/progarch/messaging-and-eip/saga-style-choice/img/crash-mid-saga.svg)
*Той самий збій посеред саги — і вся різниця в тому, де живе стан. У наївного він у пам'яті процесу й помирає разом із ним, лишаючи сироту. У довговічного кожен крок лягає на диск, тож новий процес читає, де сага спинилась, і доводить її до кінця.*

## Довговічний рушій — крок лягає на диск, процес відроджується

Діру видно, і видно ліки: стан саги мусить жити **поза** процесом — на диску, — щоб його пережити. Саме це й роблять [довговічні робочі процеси](book:programming/durable-workflows): кожен завершений крок фіксується в стійкому журналі, і якщо процес гине, новий читає журнал і продовжує рівно з того місця. Зберімо мінімальний такий рушій — саме стільки, щоб побачити механізм у дії. Опишемо сагу як список кроків, у кожного своя дія й компенсація, а «диск» — це сховище `Store`, що живе окремо від процесу саги.

:::tabs
```ts
type Step = { name: string; run: () => Promise<void>; comp: () => Promise<void> };
type SagaState = { cursor: number; status: "running" | "committed" | "compensated" };

class Store {                                 // «диск» — переживає смерть процесу саги
  private db = new Map<string, SagaState>();
  load(id: string) { return this.db.get(id); }
  save(id: string, st: SagaState) { this.db.set(id, { ...st }); }   // копія = «лягло на диск»
}

class ProcessKilled extends Error {}          // імітація жорсткої смерті процесу

async function runSaga(id: string, steps: Step[], store: Store) {
  const st = store.load(id) ?? { cursor: 0, status: "running" as const };
  try {
    while (st.cursor < steps.length) {
      await steps[st.cursor].run();
      st.cursor += 1;
      store.save(id, st);                     // ← крок зафіксовано на диску ПЕРЕД наступним
    }
    st.status = "committed"; store.save(id, st);
  } catch (err) {
    if (err instanceof ProcessKilled) { store.save(id, st); throw err; }  // не відкіт — процес помер, диск лишився
    while (st.cursor > 0) {                    // бізнес-збій → компенсуємо зворотним порядком
      st.cursor -= 1;
      await steps[st.cursor].comp();
      store.save(id, st);                      // прогрес відкоту теж лягає на диск
    }
    st.status = "compensated"; store.save(id, st);
    throw err;
  }
}

const step = (name: string, run: () => Promise<void>, comp: () => Promise<void>): Step =>
  ({ name, run, comp });
```
```py
class Step:
    def __init__(self, name, run, comp): self.name, self.run, self.comp = name, run, comp

class Store:                                  # «диск» — переживає смерть процесу саги
    def __init__(self): self.db = {}
    def load(self, sid):        return self.db.get(sid)
    def save(self, sid, state): self.db[sid] = dict(state)   # копія = «лягло на диск»

class ProcessKilled(Exception):               # імітація жорсткої смерті процесу
    pass

async def run_saga(sid, steps, store):
    st = store.load(sid) or {"cursor": 0, "status": "running"}
    try:
        while st["cursor"] < len(steps):
            await steps[st["cursor"]].run()
            st["cursor"] += 1
            store.save(sid, st)               # ← крок зафіксовано на диску ПЕРЕД наступним
        st["status"] = "committed"; store.save(sid, st)
    except ProcessKilled:                     # не відкіт — процес помер, диск лишився
        store.save(sid, st); raise
    except Exception:                         # бізнес-збій → компенсуємо зворотним порядком
        while st["cursor"] > 0:
            st["cursor"] -= 1
            await steps[st["cursor"]].comp()
            store.save(sid, st)               # прогрес відкоту теж лягає на диск
        st["status"] = "compensated"; store.save(sid, st)
        raise
```
:::

Одна річ тут потребує чесного застереження. Гілка `ProcessKilled` — це **симуляція** жорсткої смерті, щоб демо запускалося в одному процесі; справжній рушій такої гілки не має, бо процес просто зникає — операційна система його вбиває, ніякого винятку не летить. Натомість зовнішній координатор (сервер рушія) помічає, що виконавець перестав звітувати, і **відтворює журнал** на новому виконавці. Наш `cursor` на диску — це мінімальна версія тієї самої ідеї: справжні рушії, як-от Temporal, тримають повну **історію подій** саги й, відтворюючи її, пропускають уже зроблені кроки; хмарні служби на кшталт AWS Step Functions роблять те саме як керований сервіс. Механізм один: **завершений крок — на стійкому носії, процес — відроджуваний із нього.**

Тепер повалимо процес посеред саги — і подивімося, як диск її рятує:

```
процес A:  runSaga("saga-42")
  reserve ✓                → диск: { cursor: 1, running }
  💀 процес помер під час config
диск лишився:  { cursor: 1, running }        ← крок 1 зафіксовано

процес B:  runSaga("saga-42")                ← ВІДРОДЖЕННЯ (новий процес, той самий id)
  читає диск: cursor = 1  → доробляє з кроку 2
  config ✓                 → диск: { cursor: 2 }
  meter  ✓                 → диск: { cursor: 3, committed }
підсумок:  reserved, configured, metered = { dev-42 };  статус: committed
```

Ось де діра затулилася. Перший процес помер, лишивши на диску `cursor = 1`. Другий процес — це може бути перезапущений контейнер за секунду чи за годину — читає той запис і **доводить сагу до кінця**, не переробляючи вже зроблене. Жодного сироти. А коли впаде не процес, а **крок** (той самий хаб недоступний), гілка бізнес-збою відкотить зроблене зворотним порядком і запише `compensated` — і цей відкіт теж фіксується покроково, тож переживе смерть **посеред самого відкоту**.

> 🔧 **Навіщо це.** «Оркестрація» на співбесіді часто звучить як «одна функція з try/catch» — і це наївний варіант, у якому стан живе в пам'яті. Різниця між ним і бойовою оркестрацією — рівно один рядок думки: **де лежить cursor саги.** У наївного — у стеку, тож смерть процесу = сирота; у довговічного — на диску, тож смерть процесу = пауза, яку відродження знімає. Ось чому «оркестрація» сьогодні майже завжди означає «оркестрація на довговічному рушії»: не тому, що так модно, а тому, що без стійкого журналу оркестратор не переживе власної смерті — а він мусить.

## Тест, що ловить розповзання хореографії

Тепер найцінніше — тест, який робить **відчутною** ваду хореографії, що на словах звучить абстрактно: «додати крок важче, а статусу ніде нема». Зробімо це руками. Уяви новий крок: перед білінгом пристрій треба зареєструвати в **податковому** сервісі (регуляторна вимога). Один крок посередині саги. Податковий сервіс — тонкий, як і решта:

:::tabs
```ts
class Tax {
  registered = new Set<string>(); down = false;
  async register(homeId: string, deviceId: string) {
    if (this.down) throw new Error("податкова недоступна");
    this.registered.add(deviceId);
  }
  async unregister(deviceId: string) { this.registered.delete(deviceId); }
}
```
```py
class Tax:
    def __init__(self): self.registered = set(); self.down = False
    async def register(self, home_id, device_id):
        if self.down: raise RuntimeError("податкова недоступна")
        self.registered.add(device_id)
    async def unregister(self, device_id): self.registered.discard(device_id)
```
:::

В **оркестрації** це буквально один рядок — вставити `Step` у список. Компенсація зворотного порядку підхопить його **даром**: тест повного відкоту, який був зелений до змін, лишається зеленим, бо новий крок автоматично опинився в тому самому циклі `undo`.

:::tabs
```ts
import { test, expect } from "vitest";

// той самий рушій runSaga; додаємо КРОК tax між config і meter
function enrollSteps(reg: Registry, hub: Hub, bil: Billing, tax: Tax, home: string, dev: string): Step[] {
  return [
    step("reserve", () => reg.reserve(dev, home),       () => reg.unreserve(dev)),
    step("config",  () => hub.pushConfig(home, dev),     () => hub.wipeConfig(home, dev)),
    step("tax",     () => tax.register(home, dev),       () => tax.unregister(dev)),   // ← ОДИН новий рядок
    step("meter",   () => bil.startMeter(home, dev),     () => bil.stopMeter(home, dev)),
  ];
}

test("оркестрація: новий крок tax відкочується зворотним порядком — ДАРМА", async () => {
  const reg = new Registry(), hub = new Hub(), bil = new Billing(), tax = new Tax();
  bil.down = true;                                    // збій на останньому кроці
  const store = new Store();
  await expect(runSaga("s1", enrollSteps(reg, hub, bil, tax, "home-7", "dev-42"), store))
    .rejects.toThrow();
  expect(reg.reserved.size).toBe(0);                 // reserve відкотився
  expect(hub.configured.size).toBe(0);               // config відкотився
  expect(tax.registered.size).toBe(0);               // ← tax теж — хоч ми компенсацій НЕ дописували
  expect(store.load("s1")!.status).toBe("compensated");   // а статус саги — ось він, однією викличкою
});
```
```py
import pytest

# той самий рушій run_saga; додаємо КРОК tax між config і meter
def enroll_steps(reg, hub, bil, tax, home, dev):
    return [
        Step("reserve", lambda: reg.reserve(dev, home),        lambda: reg.unreserve(dev)),
        Step("config",  lambda: hub.push_config(home, dev),    lambda: hub.wipe_config(home, dev)),
        Step("tax",     lambda: tax.register(home, dev),       lambda: tax.unregister(dev)),   # ← ОДИН новий рядок
        Step("meter",   lambda: bil.start_meter(home, dev),    lambda: bil.stop_meter(home, dev)),
    ]

@pytest.mark.asyncio
async def test_orchestration_rolls_back_new_step_for_free():
    reg, hub, bil, tax = Registry(), Hub(), Billing(), Tax()
    bil.down = True                                    # збій на останньому кроці
    store = Store()
    with pytest.raises(RuntimeError):
        await run_saga("s1", enroll_steps(reg, hub, bil, tax, "home-7", "dev-42"), store)
    assert reg.reserved == set()                       # reserve відкотився
    assert hub.configured == set()                     # config відкотився
    assert tax.registered == set()                     # ← tax теж — хоч ми компенсацій НЕ дописували
    assert store.load("s1")["status"] == "compensated" # а статус саги — ось він, однією викличкою
```
:::

Тепер той самий крок у **хореографії**. Тут одним рядком не обійтися. Прямий шлях треба переплести: новий обробник `on DeviceConfigured → tax.register → emit DeviceTaxed`, а білінг **перевести** слухати вже `DeviceTaxed`, а не `DeviceConfigured`. Це вже дві правки у двох місцях. Але головне попереду: компенсацію tax треба **окремо** вплести в задню мережу — навчити `DeviceMeterFailed` відкочувати ще й податкову. А та мережа — інший файл, інші підписки, і про неї **легко забути**, бо на прямому шляху все зелено. Ось хореографічна версія з дописаним прямим шляхом і **забутою** гілкою компенсації — типова помилка, яку робить жива команда:

:::tabs
```ts
function wireChoreographyWithTax(reg: Registry, hub: Hub, bil: Billing, tax: Tax): Bus {
  const bus = new Bus();
  bus.on("DeviceReserveRequested", async e => { await reg.reserve(e.deviceId, e.homeId); await bus.emit("DeviceReserved", e); });
  bus.on("DeviceReserved", async e => {
    try { await hub.pushConfig(e.homeId, e.deviceId); await bus.emit("DeviceConfigured", e); }
    catch { await bus.emit("DeviceConfigFailed", e); }
  });
  bus.on("DeviceConfigured", async e => { await tax.register(e.homeId, e.deviceId); await bus.emit("DeviceTaxed", e); });  // правка 1
  bus.on("DeviceTaxed", async e => {                                                     // правка 2: білінг слухає вже Taxed
    try { await bil.startMeter(e.homeId, e.deviceId); }
    catch { await bus.emit("DeviceMeterFailed", e); }
  });
  bus.on("DeviceConfigFailed", async e => { await reg.unreserve(e.deviceId); });
  bus.on("DeviceMeterFailed", async e => {                                              // ← гілку відкоту tax ТУТ забули
    await hub.wipeConfig(e.homeId, e.deviceId); await bus.emit("DeviceConfigCompensated", e);
  });
  bus.on("DeviceConfigCompensated", async e => { await reg.unreserve(e.deviceId); });
  return bus;
}

test("хореографія: той самий доданий крок ТЕЧЕ у шві — тест це й ловить", async () => {
  const reg = new Registry(), hub = new Hub(), bil = new Billing(), tax = new Tax();
  bil.down = true;
  const bus = wireChoreographyWithTax(reg, hub, bil, tax);
  await bus.emit("DeviceReserveRequested", { homeId: "home-7", deviceId: "dev-42" });
  expect(reg.reserved.size).toBe(0);            // reserve відкотився
  expect(hub.configured.size).toBe(0);          // config відкотився
  expect(tax.registered.has("dev-42")).toBe(true);   // ← tax ЛИШИВСЯ: гілку компенсації забули
  // а «статус саги»? спитати ніде — об'єкта саги не існує
});
```
```py
def wire_choreography_with_tax(reg, hub, bil, tax):
    bus = Bus()
    async def on_requested(e):  await reg.reserve(e.device_id, e.home_id); await bus.emit("DeviceReserved", e)
    async def on_reserved(e):
        try: await hub.push_config(e.home_id, e.device_id); await bus.emit("DeviceConfigured", e)
        except Exception: await bus.emit("DeviceConfigFailed", e)
    async def on_configured(e):  await tax.register(e.home_id, e.device_id); await bus.emit("DeviceTaxed", e)   # правка 1
    async def on_taxed(e):                                                    # правка 2: білінг слухає вже Taxed
        try: await bil.start_meter(e.home_id, e.device_id)
        except Exception: await bus.emit("DeviceMeterFailed", e)
    async def on_config_failed(e):  await reg.unreserve(e.device_id)
    async def on_meter_failed(e):                                            # ← гілку відкоту tax ТУТ забули
        await hub.wipe_config(e.home_id, e.device_id); await bus.emit("DeviceConfigCompensated", e)
    async def on_config_compensated(e):  await reg.unreserve(e.device_id)
    for ev, fn in [("DeviceReserveRequested", on_requested), ("DeviceReserved", on_reserved),
                   ("DeviceConfigured", on_configured), ("DeviceTaxed", on_taxed),
                   ("DeviceConfigFailed", on_config_failed), ("DeviceMeterFailed", on_meter_failed),
                   ("DeviceConfigCompensated", on_config_compensated)]:
        bus.on(ev, fn)
    return bus

@pytest.mark.asyncio
async def test_choreography_leaks_new_step_in_the_seam():
    reg, hub, bil, tax = Registry(), Hub(), Billing(), Tax()
    bil.down = True
    bus = wire_choreography_with_tax(reg, hub, bil, tax)
    await bus.emit("DeviceReserveRequested", Enroll("home-7", "dev-42"))
    assert reg.reserved == set()                # reserve відкотився
    assert hub.configured == set()              # config відкотився
    assert tax.registered == {"dev-42"}         # ← tax ЛИШИВСЯ: гілку компенсації забули
    # а «статус саги»? спитати ніде — об'єкта саги не існує
```
:::

Ось у чому підступність, і чому цей тест — [характеризаційний: пришпилює наявну поведінку системи як є, щоб мовчазна зміна не зламала її непомітно](guide:progarch/characterization-tests). Він навмисне фіксує тут саме хибу, а не бажаний відкіт. Кожен окремий обробник тут **локально правильний**: `tax.register` реєструє, `on_meter_failed` чесно відкочує хаб і реєстр. Юніт-тест **будь-якого одного сервісу** буде зелений. Помилка живе не в жодному обробнику, а в **шві між ними** — у забутій підписці задньої мережі. Тому наш тест і мусить бути наскрізним: він проганяє всю сагу до падіння й ловить, що `tax` **лишився зареєстрованим**, тимчасом як усе решта відкотилося. Це рівно те «розповзання», якого не видно, поки не спитаєш систему як ціле — а спитати нема кого, бо, як каже останній коментар, **об'єкта саги не існує**. Порівняй із тим самим рядком оркестрації, де `store.load("s1").status` повертає `"compensated"` однією викличкою.

![Ліворуч оркестрація: один блок enrollDevice зі списком кроків, підпис «вставив один крок tax», нижче зелена рамка «компенсація зворотним порядком включає tax дарма, тест повного відкоту лишається зелений», унизу «статус саги — store.status(id)». Праворуч хореографія: три розкидані рамки правок (новий обробник на Configured, білінг слухає тепер DeviceTaxed, on MeterFailed теж має undo tax) плюс окрема компенсаційна мережа, червона рамка «забув гілку компенсації → tax тече, сага рветься у шві», унизу «статусу саги — ніде»](/guide/progarch/messaging-and-eip/saga-style-choice/img/choreo-sprawl.svg)
*Той самий доданий крок — і два різні рахунки за зміну. В оркестрації одна правка, а компенсація й статус ідуть даром. У хореографії правка розповзається по кількох підписках, окрема задня мережа легко лишається недописаною, і напівпройдена сага тече у шві — без жодного місця, де видно, що вона застрягла.*

> 🔧 **Навіщо це.** Цей тест — не про tax і не про DH. Він про те, як **виміряти** розповзання, замість сперечатися про нього словами. Хочеш знати, чи потягне твій процес хореографію на дистанції? Спробуй **додати крок** і напиши наскрізний тест на повний відкіт. В оркестрації він зелений після однорядкової правки. У хореографії ти спершу згадуєш усі підписки, які треба переплести, тоді забуваєш одну із задньої мережі — і тест червоніє саме там, у шві. Червоний тест тут — не поразка, а **діагноз**: він показав ціну зміни ще до того, як вона витекла в бойовий дім.

## Складність і пастки

Три реалізації — три різні набори граблів, і кожні ростуть із того самого кореня, що й перевага стилю.

**Хореографія: усе — у швах.** Ми бачили головне: компенсації — це друга мережа, яка їде назад і ніде не зібрана, тож кожна зміна саги розповзається по підписках, а забута гілка тече мовчки. Поряд — ще двоє сусідів. Перший: **циклічні залежності**. Подія-компенсація будить обробник, той емітить наступну — і легко зробити петлю, де сага відкочується по колу; жодне окреме місце цієї петлі не показує. Другий: **статусу нема за побудовою**. Питання «на якому кроці сага dev-42?» не має відповіді, бо ніхто її не тримає; напівпройдений стан не відрізнити від застряглого. Для процесу на два-три незалежні кроки все це — прийнятна ціна за слабке зчеплення; для процесу, що росте, — накопичувальний борг.

**Наївна оркестрація: стан у пам'яті.** Одна функція гарна доти, доки не помирає процес. `undo` у стеку — це сирота на кожен SIGKILL посеред саги, і жоден `try/catch` цього не ловить, бо ловити нема чого — процес просто зник. Друга грабля тут — **спокуса бога-об'єкта**: раз увесь процес в одній функції, туди тягне й ділову логіку сервісів, аж оркестратор роздувається у «розумну трубу». Ліки від першої — довговічність; від другої — дисципліна тримати в оркестраторі лише **порядок**, а роботу лишати учасникам.

**Довговічна оркестрація: ціна стійкості.** Журнал на диску розв'язує сиріт, але приносить свій оброк. По-перше, **повтори**: якщо процес помер після дії, але **до** запису на диск, відродження виконає крок ще раз — тому кроки й компенсації мусять бути [ідемпотентні: повторний виклик не робить подвійної роботи](book:programming/idempotency). `reserve` двічі має лишати один резерв, `unreserve` неіснуючого — тихо нічого не робити (наш `discard`/`delete` саме такий). По-друге, **компенсація теж може впасти** — `wipeConfig` не достукався до хаба; довговічний рушій це переживає (повторить із того ж cursor), але потрібні межа спроб і сигнал людині, коли відкіт застряг. По-третє, **не все відкочується**: якщо крок надіслав лист чи списав гроші, компенсація — не «стерти», а «надіслати спростування» чи «повернути кошти»; проєктуючи сагу, за кожен крок питай не лише «як зробити», а й «як **чесно** відкотити».

## Що лишається в руках

Ми провели одну маленьку сагу трьома реалізаціями й щоразу міряли одне: **де живе стан процесу.** У хореографії — ніде: ні прямий потік, ні зворотний не зібрані, вони проступають зі швів, і будь-яка зміна чи відмова оголює той шов. У наївній оркестрації — у пам'яті процесу: видно згори вниз, доки процес живий, і сирота, щойно він помер посеред саги. У довговічній — на диску: кожен крок фіксується поза процесом, тож смерть стає паузою, а не катастрофою, і статус саги є задарма, бо він **і є** той запис на диску.

Тест зробив цю різницю відчутною там, де слова її лише називали. Додавши один крок, ми побачили обидві ціни поруч: однорядкову правку з безплатною компенсацією — і розповзання по підписках із дірою у шві, яку не ловить жоден локальний тест. Ось чому вибір стилю — не про красу коду, а про те, **хто зможе відповісти о третій ночі**, де застрягла ця операція. У довговічного оркестратора відповідь — один запит до сховища. У хореографії відповіді немає, бо немає й того, хто мав би її тримати.
