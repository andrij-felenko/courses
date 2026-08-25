# ⚙️ Каркас моноліта DH: дев'ять пакетів, шина, корінь — і сторож, що валить збірку

Мапу ми вже поклали на дошку, а рядок в ADR — у голову. Тепер відкриймо порожній репозиторій і зробімо те, чого не зробить жодна діаграма: **напишімо каркас, який запускається**. Не ще одну картинку зі стрілками, а живий кістяк, у якому дев'ять контекстів дому стали дев'ятьма пакетами, стрілки мапи — правилами імпорту, а «не лазь у чужу базу» — тестом, що падає червоним. Мета вузька й конкретна: щоб наприкінці в руках був не опис, а `git clone`, у якому стіни справжні, і будь-яка спроба їх обійти **валить збірку**, а не рев'ю.

Я писатиму двома мовами водночас — TypeScript і Python, — бо каркас від мови майже не залежить, і саме це видно найкраще, коли той самий кістяк лягає на два різні стеки однаково. Де мови розходяться в дрібницях (як прибити приватність, як провести транзакцію), я на цьому спинюся окремо: у тих дрібницях і ховається чесна відповідь на питання «а що тут насправді тримає стіну».

## Задача: зробити мапу такою, щоб її стерегла машина

Випишімо, що саме має бути в каркасі, щоб він був не декорацією, а хребтом:

- **дев'ять пакетів**, по одному на контекст, і кожен — з єдиними дверима: назовні видно вузький фасад, усе інше сховано так, що чужий модуль його **не бачить за іменем**;
- **внутрішньопроцесна шина**, якою `control` публікує факт `DeviceEvent`, а підписники його ловлять, не знаючи продюсера в обличчя;
- **один корінь склеювання** `buildApp(db, bus)` — єдине місце, де все з'єднано: кожен модуль дістає свою схему бази, потрібні фасади й шину, і тут-таки реєструються підписки;
- **фітнес-функція** — тест архітектури, що падає на трьох речах: заборонене ребро (`billing → control`), цикл у графі залежностей, звертання модуля в чужу схему.

Останній пункт — не прикраса, а те, заради чого весь каркас і має сенс. В одному процесі кожен модуль — на відстані одного `import` від будь-якого іншого. Добра воля таку відстань не втримає й пів року. Тож наш кістяк мусить нести всередині власного сторожа.

## Ідея: тонкі двері, дротова подія, один диригент, один суддя

Уся конструкція тримається на чотирьох простих думках, і кожна відповідає одному шматку каркаса.

Модуль — це **дві сторони**: тонкі двері назовні (фасад: кілька публічних типів і викликів) і закриті нутрощі (класи, SQL, таблиці). Двері — це буквально один файл-бар'єр: `index.ts`, що реекспортує лише дозволене, або `__init__.py` зі списком `__all__`. Що не пройшло крізь бар'єр — для сусіда не існує.

Подія на шині — **дротовий факт**, а не живий об'єкт. Кладемо в шину не `Device` цілком, а плаский `DeviceEvent`: вид, хто, коли, значення. Це той шов, уздовж якого колись — якщо колись — модуль поїде в окремий сервіс, не переписуючи обробників.

Збирає все **один корінь**, бо якби модулі сплітались самі, вони б знову зналися напряму. Корінь — єдине місце, що знає всіх і всі залежності; модулі не знають, звідки їм прийшла їхня схема чи шина.

І над усім — **суддя**: виконуваний тест, що тримає перелік дозволених ребер за єдине джерело правди й валить збірку, щойно код відступив від мапи. Не порада на рев'ю — червона збірка.

## Розкладка: дев'ять пакетів і бар'єр на кожному

Ось увесь кістяк одним поглядом. Кожен контекст — тека верхнього рівня; у кожній рівно один файл-двері, за якими — приватне тіло й власна схема:

```
dh/
├─ ids/                    ← спільне ядро: типи + контракт події + шина
│  ├─ index.ts │ __init__.py     DeviceId, HomeId, DeviceEvent, Bus  (єдине, що ділять усі)
│  ├─ events.ts│ events.py       DeviceEvent — дротовий факт
│  └─ bus.ts   │ bus.py          синхронна внутрішньопроцесна шина
├─ control/               ← керування
│  ├─ index.ts │ __init__.py     ФАСАД: Control, makeControl   (єдині двері)
│  ├─ contract.ts│ contract.py   публічні типи: Command, DeviceView
│  ├─ service.ts│ _service.py    приватна логіка — НЕ експортовано
│  ├─ store.ts │ _store.py       приватний доступ ЛИШЕ до схеми control
│  └─ schema.sql                 DDL: schema control (device, room)
├─ twin/           …             фасад Twin (currentState)
├─ telemetry/      …             фасад Telemetry (record, lastReading)
├─ automations/    …             фасад Automations (evaluate, onEvent)
├─ video/          …
├─ notifications/  …
├─ identity/       …             фасад Identity (authorize)
├─ billing/        …             фасад Billing (onEvent)
├─ app.ts │ app.py               ← КОРІНЬ: buildApp(db, bus)
└─ arch.test.ts │ arch_test.py   ← СТОРОЖ: фітнес-функція, валить збірку
```

Дві речі варто прочитати з цього дерева одразу. Перша: `ids` — крихітний і **ні від кого не залежить**; це спільний словник, який усі свідомо ділять, і саме тому в ньому не може бути нічиєї бізнес-логіки, лише типи, контракт події й шина. Друга: у кожному контексті файли з підкресленням (`_service`, `_store`) і некспортовані класи — це тіло, яке двері назовні не пускають. Двері — тонкі навмисне.

## Спільне ядро: подія-факт і синхронна шина

Почнімо з осердя, бо від нього залежить усе решта. У `ids` живуть три речі: спільні типи, контракт події й шина. Типи — це навіть не класи, а «марковані» рядки: `DeviceId` — це `str`, але окремого сорту, щоб компілятор не дав переплутати його з `HomeId`. Подія — плаский незмінний запис. А шина — і є та тонкість, заради якої крок затіяно.

:::tabs
```ts
// ids/types.ts — спільний словник: марковані примітиви, щоб не сплутати ідентифікатори
export type DeviceId = string & { readonly __brand: "DeviceId" };
export type HomeId   = string & { readonly __brand: "HomeId" };

// ids/events.ts — ДРОТОВИЙ факт: ані живих агрегатів, ані вендорських типів
import type { DeviceId, HomeId } from "./types";
export interface DeviceEvent {
  kind: "state" | "added" | "removed";
  deviceId: DeviceId;
  homeId: HomeId;
  at: number;      // epoch-мілісекунди — примітив, не Date якоїсь бібліотеки
  value: number;
}

// ids/bus.ts — внутрішньопроцесна шина: СИНХРОННА диспетчеризація в тій самій транзакції
import type { DeviceEvent } from "./events";
export type Subscriber = (e: DeviceEvent) => void;

export class Bus {
  private subs: Subscriber[] = [];
  subscribe(handler: Subscriber): void { this.subs.push(handler); }
  publish(event: DeviceEvent): void {
    for (const handler of this.subs) handler(event);   // по черзі, ТУТ-ТАКИ, у tx продюсера
  }                                                    // виняток підписника ЛЕТИТЬ УГОРУ
}

// ids/index.ts — БАР'ЄР спільного ядра
export type { DeviceId, HomeId } from "./types";
export type { DeviceEvent } from "./events";
export { Bus } from "./bus";
export type { Subscriber } from "./bus";
```
```py
# ids/types.py — спільний словник: окремі типи поверх str, щоб не сплутати ідентифікатори
from typing import NewType
DeviceId = NewType("DeviceId", str)
HomeId   = NewType("HomeId", str)

# ids/events.py — ДРОТОВИЙ факт: ані живих агрегатів, ані вендорських типів
from dataclasses import dataclass
from typing import Literal
from .types import DeviceId, HomeId

@dataclass(frozen=True)
class DeviceEvent:
    kind: Literal["state", "added", "removed"]
    device_id: DeviceId
    home_id: HomeId
    at: int            # epoch-мілісекунди — примітив, не datetime якоїсь бібліотеки
    value: float

# ids/bus.py — внутрішньопроцесна шина: СИНХРОННА диспетчеризація в тій самій транзакції
from typing import Callable
Subscriber = Callable[[DeviceEvent], None]

class Bus:
    def __init__(self) -> None:
        self._subs: list[Subscriber] = []
    def subscribe(self, handler: Subscriber) -> None:
        self._subs.append(handler)
    def publish(self, event: DeviceEvent) -> None:
        for handler in self._subs:      # по черзі, ТУТ-ТАКИ, у tx продюсера
            handler(event)              # виняток підписника ЛЕТИТЬ УГОРУ

# ids/__init__.py — БАР'ЄР спільного ядра
from .types import DeviceId, HomeId
from .events import DeviceEvent
from .bus import Bus, Subscriber
__all__ = ["DeviceId", "HomeId", "DeviceEvent", "Bus", "Subscriber"]
```
:::

Придивімося до `publish` — уся шина в ньому вміщається в один цикл, і кожне слово тут навмисне. Сьогодні DH — один процес, тож «опублікувати подію» означає буквально **покликати всіх підписників по черзі, тут-таки, у тому самому стеку й у тій самій транзакції**, що й продюсер. Жодного «поклав у чергу й пішов», жодної мережі. Наносекунди. І — головне — якщо котрийсь підписник кине виняток, `publish` не проковтне його: виняток полетить угору, до того, хто викликав `publish`. Це не недогляд. Це [навмисне зчеплення через подію, а не пряме ребро](root:sf-apps/event-driven-architecture): продюсер не знає підписників, підписники не знають продюсера, обидва знають лише контракт `DeviceEvent`. А те, що виняток летить угору, — свідома семантика, у якій за мить виявиться і сила, і найгостріша пастка всього каркаса.

## Один модуль до дна: телеметрія

Дев'ять модулів однакові за формою, тож розберімо один до самого дна — телеметрію, — і решту вже читатимемо як його копії. Модуль має чотири шматки: публічний контракт, приватний доступ до **своєї** схеми, реалізацію фасаду й бар'єр, що впускає назовні лише перше й третє.

:::tabs
```ts
// telemetry/contract.ts — ПУБЛІЧНЕ: те, що бачать сусіди
import type { DeviceId } from "../ids";
export interface Reading { deviceId: DeviceId; value: number; at: number; }

// telemetry/store.ts — ПРИВАТНЕ: лише цей модуль торкається схеми telemetry
import type { DeviceId } from "../ids";
import type { Reading } from "./contract";
import type { Schema } from "../ids/db";          // дескриптор ЛИШЕ однієї схеми
export class ReadingStore {                        // з index не реекспортовано → зовні не існує
  constructor(private readonly s: Schema) {
    s.exec(`CREATE TABLE IF NOT EXISTS telemetry.reading(
              device_id TEXT, value DOUBLE PRECISION, at BIGINT)`);
  }
  put(r: Reading): void {
    this.s.exec(`INSERT INTO telemetry.reading(device_id, value, at) VALUES ($1,$2,$3)`,
                [r.deviceId, r.value, r.at]);
  }
  last(id: DeviceId): Reading | null {
    const row = this.s.queryOne(
      `SELECT value, at FROM telemetry.reading WHERE device_id=$1 ORDER BY at DESC LIMIT 1`, [id]);
    return row ? { deviceId: id, value: row.value, at: row.at } : null;
  }
}

// telemetry/service.ts — реалізація фасаду (клас приватний; назовні йде лише інтерфейс)
import type { DeviceId, DeviceEvent } from "../ids";
import type { Reading } from "./contract";
import type { Schema } from "../ids/db";
import { ReadingStore } from "./store";
export interface Telemetry {                        // ← ФАСАД: усе, що бачать сусіди
  record(e: DeviceEvent): void;                     // підписник шини
  lastReading(id: DeviceId): Reading | null;
}
class TelemetryService implements Telemetry {
  constructor(private readonly store: ReadingStore) {}
  record(e: DeviceEvent): void {
    if (e.kind === "state") this.store.put({ deviceId: e.deviceId, value: e.value, at: e.at });
  }
  lastReading(id: DeviceId): Reading | null { return this.store.last(id); }
}
export function makeTelemetry(schema: Schema): Telemetry {  // фабрика в'яже приватний стор зі схемою
  return new TelemetryService(new ReadingStore(schema));
}

// telemetry/index.ts — БАР'ЄР: єдині двері модуля
export type { Reading } from "./contract";
export type { Telemetry } from "./service";
export { makeTelemetry } from "./service";
// ReadingStore, TelemetryService, схема — НЕ реекспортовано: для сусідів їх нема
```
```py
# telemetry/contract.py — ПУБЛІЧНЕ: те, що бачать сусіди
from dataclasses import dataclass
from ids import DeviceId
@dataclass(frozen=True)
class Reading:
    device_id: DeviceId
    value: float
    at: int

# telemetry/_store.py — ПРИВАТНЕ (під підкресленням): лише цей модуль торкається схеми telemetry
from ids import DeviceId
from .contract import Reading
class _ReadingStore:
    def __init__(self, schema):                    # schema = дескриптор ЛИШЕ схеми telemetry
        self._s = schema
        schema.execute("""CREATE TABLE IF NOT EXISTS telemetry.reading(
                            device_id TEXT, value DOUBLE PRECISION, at BIGINT)""")
    def put(self, r: Reading) -> None:
        self._s.execute("INSERT INTO telemetry.reading(device_id, value, at) VALUES (%s,%s,%s)",
                        (r.device_id, r.value, r.at))
    def last(self, device_id: DeviceId) -> Reading | None:
        row = self._s.query_one("SELECT value, at FROM telemetry.reading "
                                "WHERE device_id=%s ORDER BY at DESC LIMIT 1", (device_id,))
        return Reading(device_id, row.value, row.at) if row else None

# telemetry/_service.py — реалізація фасаду (клас доступний, фабрика — офіційні двері)
from ids import DeviceId, DeviceEvent
from .contract import Reading
from ._store import _ReadingStore
class Telemetry:                                    # ← ФАСАД
    def __init__(self, store: _ReadingStore):
        self._store = store
    def record(self, e: DeviceEvent) -> None:       # підписник шини
        if e.kind == "state":
            self._store.put(Reading(e.device_id, e.value, e.at))
    def last_reading(self, device_id: DeviceId) -> Reading | None:
        return self._store.last(device_id)
def make_telemetry(schema) -> Telemetry:            # фабрика в'яже приватний стор зі схемою
    return Telemetry(_ReadingStore(schema))

# telemetry/__init__.py — БАР'ЄР: назовні видно лише фасад, фабрику й публічний контракт
from ._service import Telemetry, make_telemetry
from .contract import Reading
__all__ = ["Telemetry", "make_telemetry", "Reading"]
```
:::

Тут — уся анатомія модуля, [точно за означенням модульного моноліта](root:sf-apps/modular-monolith): контракт публічний, стор приватний і **єдиний**, хто знає слово `telemetry.reading`, сервіс реалізує фасад, а фабрика `makeTelemetry(schema)` в'яже приватний стор із виданою йому схемою. Сусід, що має посилання на `Telemetry`, може написати `lastReading(id)` — і не може дотягтися до `ReadingStore` чи до таблиці: їх бар'єр назовні не випустив.

І ось перша чесна тонкість, яку легко проґавити й яка все змінює. У Java-модулях чи в Rust приватність — це **закон мови**: недоступне ти фізично не скомпілюєш. А в TypeScript і Python двері — радше **дуже переконлива домовленість**, ніж стіна з бетону. У Python підкреслення нікого не зупиняє: `from telemetry._store import _ReadingStore` імпортується, якщо дуже захотіти. У TS `index.ts` — головні двері, але глибокий шлях `import { ReadingStore } from "telemetry/store"` теж піде, бо файл фізично там. Мова допомагає — зробити правильне легким, а неправильне помітним, — але сама по собі стіну до кінця не тримає. Ось чому цей каркас **не може** покластися на самі двері. Те, що остаточно робить стіну стіною, — суддя наприкінці, який на будь-який обхід дверей відповідає червоною збіркою. Тримаймо цю думку: вона повернеться в кожній пастці.

## Публікація в транзакції продюсера

Тепер зшиймо шину з роботою. Коли `control` виконує команду, він у **одній транзакції** пише зміну в свою таблицю й публікує факт. А що `publish`, як ми щойно бачили, кличе підписників синхронно, тут-таки, — вони всі відпрацьовують **усередині тієї самої транзакції**:

:::tabs
```ts
// control/service.ts — команда й розсилка події в ОДНІЙ транзакції
import type { Bus } from "../ids";
export class Control {
  constructor(private readonly repo: DeviceRepo, private readonly bus: Bus) {}
  apply(cmd: Command): void {
    this.repo.tx((tx) => {                          // ← одна транзакція на всю операцію
      const device = this.repo.apply(cmd, tx);      // приватна нутрощі: пише в схему control
      this.bus.publish({                            // підписники біжать ТУТ-ТАКИ, у цій tx
        kind: "state", deviceId: device.id, homeId: device.homeId,
        at: Date.now(), value: device.state,
      });
    });   // коллбек завершився без винятку → COMMIT; кинув будь-хто всередині → ROLLBACK усього
  }
}
export function makeControl(schema: Schema, bus: Bus): Control {
  return new Control(new DeviceRepo(schema), bus);
}
```
```py
# control/_service.py — команда й розсилка події в ОДНІЙ транзакції
from time import time
from ids import Bus, DeviceEvent
from ._store import _DeviceRepo
from .contract import Command
class Control:
    def __init__(self, repo: _DeviceRepo, bus: Bus):
        self._repo, self._bus = repo, bus
    def apply(self, cmd: Command) -> None:
        with self._repo.tx() as tx:                 # ← одна транзакція на всю операцію
            device = self._repo.apply(cmd, tx)      # приватна нутрощі: пише в схему control
            self._bus.publish(DeviceEvent(          # підписники біжать ТУТ-ТАКИ, у цій tx
                kind="state", device_id=device.id, home_id=device.home_id,
                at=int(time() * 1000), value=device.state))
        # нормальний вихід із with = COMMIT; будь-який виняток усередині = ROLLBACK усього
def make_control(schema, bus: Bus) -> Control:
    return Control(_DeviceRepo(schema), bus)
```
:::

Це і є вся сила синхронної шини в одному процесі: команда й усі її наслідки — телеметрія записала вимір, автоматизації зважили правила — стають **однією атомарною операцією**. Або все, або нічого; ніякого «пристрій змінився, але вимір загубився, бо мережа кліпнула посеред». За таку атомарність у моноліті не треба платити ані розподіленими транзакціями, ані сагами — її дає звичайна транзакція бази, що накрила все.

Але та сама синхронність має вістря, і його треба назвати вголос: якщо підписник усередині `publish` кине виняток, він розкрутить стек назад — крізь `publish`, крізь `apply` — і **відкотить транзакцію продюсера разом із його власним записом**. Ось ця подвійність, лице й спід одного механізму:

![Дві панелі. Ліворуч «щасливий шлях»: рамка транзакції охоплює control.apply → repo.apply (запис device) → bus.publish, а від publish віялом униз чотири підписники (telemetry, automations, notifications, billing); унизу зелений напис COMMIT. Праворуч «підписник кинув виняток»: та сама схема, але підписник notifications червоний із хрестом і підписом «кидає виняток», червона стрілка розкручується від нього вгору через publish, уся рамка транзакції червона, унизу великий напис ROLLBACK — запис device відкочено через збій сповіщення.](img/bus-tx-dispatch.svg)

*Одна й та сама синхронна диспетчеризація дає й атомарність (ліворуч: усе комітиться разом), і пастку (праворуч: виняток некритичного підписника розкручується вгору й відкочує запис продюсера). Місце для рішення «а що робити зі збоєм підписника» — тут, і воно назване.*

Це рішення ми свідомо **лишаємо на видноті**, а не ховаємо: для критичних наслідків, які мусять статися разом із записом, синхронний відкат — це правильно; для некритичного віяла (спробувати надіслати пуш) розсилку варто винести за коміт. Повний розбір цього вибору — після коміту чи через outbox — належить [розмові про те, як різати систему й пересилати між частинами](root:progarch/when-to-split); тут досить, що каркас **дає для цього рішення чітке місце**, а не тихо ковтає його. До самої пастки повернемося наприкінці — вона того варта.

## Корінь, що збирає дім

Хто вставляє репозиторій і шину в `control`, а фасад твіна — в автоматизації? Не самі модулі — інакше вони знову зналися б напряму. Це робить **одне** місце, [корінь склеювання, де абстрактні залежності зустрічають конкретні реалізації](root:sf-apps/dependency-inversion):

:::tabs
```ts
// app.ts — КОРІНЬ: конструює всі модулі, роздає схеми й шину, реєструє підписки
import { Bus } from "./ids";
import { makeControl } from "./control";
import { makeTwin } from "./twin";
import { makeTelemetry } from "./telemetry";
import { makeAutomations } from "./automations";
import { makeNotifications } from "./notifications";
import { makeIdentity } from "./identity";
import { makeBilling } from "./billing";
import { makeVideo } from "./video";

export function buildApp(db: Db, bus: Bus) {
  // 1) кожен модуль дістає ЛИШЕ свою схему (і шину, якщо публікує)
  const identity      = makeIdentity(db.schema("identity"));
  const twin          = makeTwin(db.schema("twin"));
  const telemetry     = makeTelemetry(db.schema("telemetry"));
  const billing       = makeBilling(db.schema("billing"));
  const notifications = makeNotifications(db.schema("notifications"));
  const video         = makeVideo(db.schema("video"));
  const control       = makeControl(db.schema("control"), bus);   // ← публікує у шину
  const automations   = makeAutomations(twin);                    // ← кличе фасад твіна
  // 2) підписки на DeviceEvent — теж лише тут, в одному видимому місці
  bus.subscribe(telemetry.record);          // вимір у ряд
  bus.subscribe(automations.onEvent);       // зважити правила
  bus.subscribe(notifications.onEvent);     // чи будити власника
  bus.subscribe(billing.onEvent);           // пристрій додано/знято
  return { identity, twin, telemetry, billing, notifications, video, control, automations };
}
```
```py
# app.py — КОРІНЬ: конструює всі модулі, роздає схеми й шину, реєструє підписки
from ids import Bus
from control import make_control
from twin import make_twin
from telemetry import make_telemetry
from automations import make_automations
from notifications import make_notifications
from identity import make_identity
from billing import make_billing
from video import make_video

def build_app(db, bus: Bus):
    # 1) кожен модуль дістає ЛИШЕ свою схему (і шину, якщо публікує)
    identity      = make_identity(db.schema("identity"))
    twin          = make_twin(db.schema("twin"))
    telemetry     = make_telemetry(db.schema("telemetry"))
    billing       = make_billing(db.schema("billing"))
    notifications = make_notifications(db.schema("notifications"))
    video         = make_video(db.schema("video"))
    control       = make_control(db.schema("control"), bus)   # ← публікує у шину
    automations   = make_automations(twin)                    # ← кличе фасад твіна
    # 2) підписки на DeviceEvent — теж лише тут, в одному видимому місці
    bus.subscribe(telemetry.record)          # вимір у ряд
    bus.subscribe(automations.on_event)      # зважити правила
    bus.subscribe(notifications.on_event)    # чи будити власника
    bus.subscribe(billing.on_event)          # пристрій додано/знято
    return dict(identity=identity, twin=twin, telemetry=telemetry, billing=billing,
                notifications=notifications, video=video, control=control, automations=automations)
```
:::

Уся топологія системи зібрана в одному місці, яке читається згори вниз за десять секунд. Кожен модуль дістає рівно те, від чого залежить — свою схему (`db.schema("telemetry")` віддає дескриптор **тільки** схеми `telemetry`, і жодного іншого), потрібний фасад, шину, — і ані краплі більше. Хто кого знає, які підписки живуть у системі — усе тут, а не розсипане по конструкторах десятка класів. Це і робить корінь єдиним джерелом правди про форму системи: змінив залежність — змінив рівно один рядок, на очах.

## Сторож, що валить збірку

І тепер — суддя, без якого весь каркас лишається побажанням. Ми вже визнали чесно: у TS і Python двері не бетонні. Значить, стіну має стерегти [фітнес-функція](root:sf-apps/fitness-functions) — виконуваний тест, що падає на порушенні правила так само гучно, як падає тест на зламаній логіці. Він робить три перевірки, і кожна ловить свій різновид зради межі.

Спершу треба здобути **справжній** граф залежностей — не той, що на дошці, а той, що в коді. Для Python його чисто дає розбір синтаксису: пройди кожен файл, глянь, який верхній пакет він імпортує:

```py
# arch/graph.py — СПРАВЖНІЙ граф імпортів пакета dh через розбір AST (без евристик і регулярок)
import ast, pathlib
MODULES = {"ids", "control", "twin", "telemetry", "automations",
           "video", "notifications", "identity", "billing"}

def import_graph(root="dh") -> dict[str, set[str]]:
    graph = {m: set() for m in MODULES}
    for path in pathlib.Path(root).rglob("*.py"):
        owner = path.relative_to(root).parts[0]         # верхній пакет = модуль-власник файлу
        if owner not in MODULES:                        # app.py, arch/* — не модулі, пропускаємо
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            top = None
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                top = node.module.split(".")[0]         # from control._store import … → "control"
            elif isinstance(node, ast.Import):
                top = node.names[0].name.split(".")[0]
            if top in MODULES and top != owner:
                graph[owner].add(top)                   # ребро owner → top
    return graph
```

Тепер три перевірки над цим графом. Перша — **дозволені ребра**: тримаємо єдиний список того, хто кого сміє знати, і все поза списком — порушення.

```py
# arch/rules.py — єдине джерело правди: дозволені РЕБРА графа
ALLOWED = {
    "control":       {"ids", "identity"},
    "twin":          {"ids", "identity"},
    "telemetry":     {"ids", "identity"},        # control знають лише через подію, не імпортом
    "automations":   {"ids", "identity", "twin"},
    "notifications": {"ids", "identity"},
    "billing":       {"ids", "identity"},        # НЕ control!
    "video":         {"ids", "identity"},
    "identity":      {"ids"},
    "ids":           set(),                       # ядро не залежить ні від кого
}
def forbidden_edges(graph):
    return [(mod, d) for mod, deps in graph.items() for d in deps - ALLOWED[mod]]
```

Друга — **ациклічність**. Граф залежностей мусить бути без циклів: якщо `A` знає `B`, а `B` знає `A`, дві кімнати злиплися в одну, і жодну вже не вийняти окремо. Це не «перевір кілька пар» — це загальна властивість графа, і ловить її класичний обхід у глибину з трьома кольорами: сірий вузол — той, що зараз на стеку рекурсії; наткнутися на сірого — значить знайти ребро назад, тобто цикл.

```py
# arch/cycles.py — знайти цикл (обхід у глибину, три кольори); повернути сам ланцюг для звіту
def find_cycle(graph):
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {n: WHITE for n in graph}
    stack = []
    def visit(n):
        colour[n] = GREY; stack.append(n)           # сірий = на поточному стеку рекурсії
        for m in graph.get(n, ()):
            if colour.get(m, WHITE) == GREY:         # ребро в сірого = ребро назад = ЦИКЛ
                return stack[stack.index(m):] + [m]  # замкнений ланцюг для повідомлення
            if colour.get(m, WHITE) == WHITE:
                found = visit(m)
                if found: return found
        stack.pop(); colour[n] = BLACK               # відходимо — вузол пройдено повністю
        return None
    for n in graph:
        if colour[n] == WHITE:
            found = visit(n)
            if found: return found
    return None
```

Третя — **ізоляція схем**, і вона ловить найтихіше порушення з усіх. Модуль не сміє називати чужу схему у своєму SQL. Це окрема перевірка, бо, як побачимо, її **не видно в графі імпортів узагалі**: зовнішній ключ телеметрії на `control.device` не додає жодного `import` — він живе в DDL. Скануємо саме SQL — DDL-файли й видобуті рядки-запити, — а не весь код навмисне: якби ми шукали `twin.` будь-де, легітимний виклик фасаду `twin.currentState()` з автоматизацій дав би хибне спрацювання. Зрада межі на рівні даних живе в SQL — там її й ловимо.

```py
# arch/schema_rule.py — жоден модуль не сміє називати чужу схему у своєму SQL
import re, pathlib
from .graph import MODULES
SCHEMAS = MODULES - {"ids"}                          # у кожного модуля однойменна схема; в ids схеми нема

def cross_schema(root="dh"):
    bad, pat = [], re.compile(r"\b(" + "|".join(SCHEMAS) + r")\.[a-z_]+")
    for path in pathlib.Path(root).rglob("*.sql"):   # звужуємо до SQL (DDL + видобуті запити), не весь код
        owner = path.relative_to(root).parts[0]
        if owner not in SCHEMAS:
            continue
        for schema in pat.findall(path.read_text(encoding="utf-8")):
            if schema != owner:
                bad.append((owner, schema, path.name))
    return bad
```

І сам тест, що звинчує три перевірки в одну фітнес-функцію. Він біжить у CI при кожному пуші; будь-яка з трьох умов — і збірка червона:

```py
# arch_test.py — ФІТНЕС-ФУНКЦІЯ: три червоні умови валять збірку
from arch.graph import import_graph
from arch.rules import forbidden_edges
from arch.cycles import find_cycle
from arch.schema_rule import cross_schema

def test_no_forbidden_import():
    bad = forbidden_edges(import_graph())
    assert not bad, f"заборонені ребра імпорту: {bad}"        # напр. [('billing', 'control')]

def test_graph_is_acyclic():
    cycle = find_cycle(import_graph())
    assert cycle is None, f"цикл у графі залежностей: {' → '.join(cycle)}"

def test_schema_isolation():
    bad = cross_schema()
    assert not bad, f"звертання в чужу схему: {bad}"          # напр. [('telemetry','control','schema.sql')]
```

Це — хребет сторожа, написаний руками навмисне: обхід у глибину з трьома кольорами варто **побачити**, бо це і є те, що роблять під капотом зрілі інструменти. А в проді граф зазвичай не збираєш сам — його дає готовий інструмент, і ти лиш декларуєш ті самі три правила. Ось той самий сторож двома мовами стеку, декларативно:

:::tabs
```ini
# .importlinter (Python) — import-linter: контракти як конфіг
[importlinter]
root_package = dh

[importlinter:contract:billing-not-control]
name = білінг не сміє знати control (лише подія)
type = forbidden
source_modules = dh.billing
forbidden_modules = dh.control

[importlinter:contract:peers-independent]
name = служби не знають одна одну — ні в який бік (отже й без циклів між ними)
type = independence
modules =
    dh.control
    dh.twin
    dh.telemetry
    dh.billing
    dh.notifications
    dh.video
```
```js
// .dependency-cruiser.cjs (TypeScript) — dependency-cruiser: forbidden + no-circular
module.exports = {
  forbidden: [
    { name: "billing-not-control", severity: "error",
      comment: "білінг не сміє знати control — лише подія",
      from: { path: "^src/billing" }, to: { path: "^src/control" } },
    { name: "no-circular", severity: "error",
      comment: "жодних циклів у графі модулів",
      from: {}, to: { circular: true } },              // ← ациклічність однією умовою
    { name: "cross-module-only-via-index", severity: "error",
      comment: "у чужий модуль — лише через його index-бар'єр, не в нутрощі",
      from: { path: "^src/([^/]+)/" },              // $1 = модуль-власник файлу
      to:   { path: "^src/[^/]+/[^/]+",             // глибокий шлях у якийсь модуль…
              pathNot: ["^src/[^/]+/index\\.ts$",   // …дозволено лише через index…
                        "^src/$1/"] } },            // …або якщо це той самий модуль ($1)
  ],
};
```
:::

Обидва інструменти [названо ще в самій статті](root:sf-apps/fitness-functions): `import-linter` для Python, `dependency-cruiser` для TypeScript, `ArchUnit` для Java, `Packwerk` для Ruby — усі роблять те саме, лише зрілим кодом і швидко. Різниця з нашим ручним хребтом лише в тому, що вони надійніше будують граф; три правила — ті самі. А ось як ця фітнес-функція виглядає збоку, коли працює:

![Зліва вузол «джерело: dh/** (9 модулів) + SQL» веде до вузла «побудувати граф імпортів (AST) + прочитати іменування схем». Від нього три стрілки до трьох перевірок-гейтів: «1 · заборонене ребро: billing → control», «2 · цикл у графі: automations ⇄ twin», «3 · чужа схема: telemetry → control.device». Кожен гейт позначено червоним хрестом, і всі три стрілками сходяться в червоний вузол «ЗБІРКА ЧЕРВОНА, exit 1, merge заблоковано». Нижче зелена лінія з написом «жодного ✗ → ЗБІРКА ЗЕЛЕНА».](img/arch-gate.svg)

*Сторож збирає справжній граф із коду й пропускає його крізь три перевірки. Спрацювала бодай одна — збірка червона, merge заблоковано. Стіна тепер не побажання рев'ю, а умова зеленого CI.*

## Складність і пастки

Каркас стоїть: дев'ять модулів, шина, корінь, суддя. Лишилося пройтися по місцях, де він усе ще ріже руки, — і кожне з них найкраще видно як **конкретний обхід межі**, який ловить (або, підступно, не ловить) наш сторож.

**Пастка 1 — тимчасовий «імпорт на разок».** Під дедлайн хтось у білінгу вирішує дістати стан пристрою навпростець, а не гидати про подію:

```py
# billing/_service.py — «лише на цей реліз, потім приберемо»
from control._store import _DeviceRepo      # ← проліз повз фасад, у приватне тіло control
```

Воно компілюється й працює — ми ж визнали: у Python підкреслення нікого не спиняє. На рев'ю о шостій вечора один такий рядок легко проходить. Але `test_no_forbidden_import` бачить у графі нове ребро `billing → control`, якого нема в `ALLOWED[billing]`, і валить збірку рядком `[('billing', 'control')]`. Ось де окупається чесність про «двері не бетонні»: саме тому, що мова не спинила, мусить спинити суддя. «На разок» не доживає до моноліта-клубка, бо не доживає навіть до merge.

**Пастка 2 — спільна таблиця повз фасад.** Ця підступніша, бо обходить не двері, а **базу**, і не лишає в графі імпортів жодного сліду. Телеметрії треба намертво прив'язати вимір до пристрою — і замість того, щоб тримати самий рядок-`device_id` й питати `control` через фасад, вона в своїй DDL ставить зовнішній ключ у чужу таблицю:

```py
# telemetry/schema.sql — «зручно»: прив'язати вимір до пристрою зовнішнім ключем у ЧУЖУ схему
CREATE TABLE telemetry.reading (
    device_id  TEXT REFERENCES control.device(id),   -- ← FK у схему control, крізь стіну
    value      DOUBLE PRECISION,
    at         BIGINT
);
```

Придивися: тут **немає жодного `import`** — DDL це не код, і граф імпортів чистий, `test_no_forbidden_import` мовчить. А проте цей один `REFERENCES` зшив схему телеметрії зі схемою `control` намертво: відтепер жодну з них не посунеш, не зачепивши другу, — рівно те, що ми й заборонили правилом «жодного зовнішнього ключа через стіну». Ловить це лише `test_schema_isolation`: у DDL телеметрії з'явилося слово `control.` — `[('telemetry', 'control', 'schema.sql')]`, збірка червона. Той самий різновид зради буває й у рантаймі — `JOIN control.room` усередині запиту телеметрії; той самий сторож ловить і його, коли дивиться на видобуті рядки-запити. Мораль проста: **межа в коді, яку зраджує база, — фікція**, тож стерегти треба обидва рівні, бо зчеплення через дані невидиме на рівні імпортів.

**Пастка 3 — синхронний підписник, що відкочує транзакцію продюсера.** Найтонша, бо це не поганий імпорт і не чужа таблиця — тут усі стіни цілі, а біда в **семантиці шини**, яку ми самі й обрали. Сповіщення на подію «пристрій додано» синхронно дзвонять у зовнішній пуш-сервіс просто в обробнику:

```py
# notifications/_service.py — підписник, що синхронно дзвонить у зовнішній світ
def on_event(self, e: DeviceEvent) -> None:
    if e.kind == "added":
        push_api.send(e.home_id, "Новий пристрій у домі")   # мережевий виклик У ТРАНЗАКЦІЇ control
```

Пригадаймо, що `publish` синхронний і біжить усередині транзакції `control`. Пуш-сервіс тайм-аутнув і кинув — виняток розкрутився вгору: крізь `on_event`, крізь `publish`, крізь `control.apply` — і `with tx` **відкотив усе**. Наслідок абсурдний і точний: додавання пристрою, яке цілком удалося, скасовано, **бо не долетіло сповіщення**. Некритичне віяло відмінило основний запис. Це те саме вістря синхронної шини, яке ми лишили пунктиром при діаграмі транзакції, — тепер воно вкусило.

Ліки бувають двох сортів, і вибір між ними — це чесне рішення, а не дефолт. Якщо наслідок **критичний** (мусить статися разом із записом або не статися зовсім) — синхронний відкат правильний, лишаємо як є. Якщо наслідок **некритичний** (спроба надіслати пуш) — його не можна пускати в транзакцію продюсера: або розсилаємо після коміту, або через outbox, коли подія мусить пережити збій. Внутрішньопроцесна шина може ще й **ізолювати** такі збої — обгорнути кожного некритичного підписника в лові винятків, щоб його падіння не валило продюсера, — але це свідома політика на підписника, а не мовчазний дефолт. Ключ у тім, що каркас **дає для цього місце й назву**; повний розбір after-commit проти outbox належить [дальшій розмові про розкрій системи й пересилання між частинами](root:progarch/when-to-split).

**І наскрізна пастка — сторож, якого відклали «на потім».** У всіх трьох випадках вище стіну втримала не мова й не добра воля рев'ю, а червона збірка. Прибери суддю — і кожна з пасток проходить у main тихо, а мапа починає брехати рівно з того дня. Тому фітнес-функцію ставлять поряд із самими модулями **з першого коміту**, а не колись, коли «стабілізуємось»: у сервісів стіну стереже фізика дорогого мережевого виклику, а в одному процесі цієї природної перепони нема — її роль грає тест. Каркас без сторожа — це дев'ять кімнат, у яких вибили двері й забули, що вони колись були.

Ось що в руках наприкінці: не діаграма, а `git clone`, де дев'ять контекстів — дев'ять огороджених пакетів; де стрілки мапи — правила імпорту в ациклічному графі; де одна база, але схема на модуль; де шина вже говорить дротовим фактом, готовим колись стати мережевим; де корінь збирає весь дім на очах; і де кожен обхід стіни — забороненим імпортом, спільною таблицею чи роздертою транзакцією — впирається в машину, що каже «ні» червоним. Кістяк, який тримає код, а не пильність.
