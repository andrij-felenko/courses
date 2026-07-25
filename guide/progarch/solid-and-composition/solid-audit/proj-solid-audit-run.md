# ⚙️ DH-тривога: аудит і рефакторинг, доведені до робочого коду

Ми вже провели аудит: навели п'ять лінз на `AlarmDispatcher` хаба Digital Homes і побачили, що вони показують не п'ять різних вад, а **один вузол** — волатильні механізми (оператор, файл, годинник) зрощені зі стабільною політикою тривоги. І накидали розв'язок: витягти ядро, вкорінити деталі через вузькі порти, зшити ззовні. Але накидали — з `/*…*/` замість тіла адаптерів і зі словом «зелено» замість доказу.

Тут ми доводимо це до кінця. Не «ось як могло б виглядати», а маленький проєкт, що збирається й проходить тести — з реальним Twilio, реальним впорскуванням, реальними дублерами. І головне: не просто рефакторимо, а **робимо виграш кожної літери видимим тестом**. Бо рефакторинг завершений не тоді, коли код компілюється, а тоді, коли є перевірка, яка **почервоніє**, щойно ти цей виграш зіпсуєш. «SOLID» без такого тесту — досі смак; з ним — інженерія.

> 🔧 **Навіщо це.** Питання рев'ю «а тут дотримано DIP?» безплідне, поки відповідь — думка. Перетвори кожну літеру на тест, і суперечка закінчується: DIP дотримано ⟺ політику видно судити без мережі й акаунта; OCP ⟺ новий канал не чіпає жодного рядка ядра; LSP ⟺ будь-який дублер, що проходить контракт, підставляється всюди. Далі — рівно ці три тести, доведені до робочого коду.

Мова — TypeScript (де структурна відмінність повчальна, поруч іде Python-вкладка). Увесь код справжній: ніякого псевдокоду, кожен фрагмент — файл, який можна покласти в проєкт.

## Розрослий клас — цілком

Спершу подивімось на пацієнта не скороченим, а таким, як він живе в репозиторії. Ось той самий `AlarmDispatcher`, але з дописаними тілами, які в аудиті ми лишили за трьома крапками:

```ts
// dispatcher.ts — «до». Один клас робить усе одразу.
import twilio from "twilio";
import * as fs from "node:fs";

export class AlarmDispatcher {
  private armed = false;
  arm()    { this.armed = true; }
  disarm() { this.armed = false; }

  handle(ev: SensorEvent): void {
    // 1) політика: чи це взагалі тривога?
    if (ev.type !== "motion" || !this.armed) return;
    if (ev.zone === "pet-safe") return;                    // зона, де бігає кіт

    // 2) як це звучить для людини
    const t = new Date().toLocaleTimeString();
    const text = `Рух у зоні «${ev.zone}» о ${t}`;

    // 3) чим шлемо — Twilio SMS, створений тут-таки з ключами з оточення
    const client = twilio(process.env.TWILIO_SID!, process.env.TWILIO_TOKEN!);
    client.messages.create({
      to: process.env.OWNER_PHONE!, from: process.env.TWILIO_FROM!, body: text,
    });

    // 4) слід — теж прибитий цвяхом, синхронний запис у файл
    fs.appendFileSync("/var/log/alarms.log", text + "\n");
  }
}
```

Тепер зупинись на одному питанні, у якому й ховається весь біль: **як написати тест «кіт у pet-safe не піднімає тривоги»?** Це чиста політика — жодного стосунку до SMS. А спробуй. Щоб інстанціювати `AlarmDispatcher` і викликати `handle`, ти тягнеш `import twilio` і код, що на рядку 3 **створює живого клієнта** з `TWILIO_SID`. Тест «про кота» тепер вимагає Twilio-акаунта, справжніх ключів в оточенні й — якщо кіт раптом *таки* в pet-safe, і гілка не спрацює, добре, але для позитивного випадку — реального SMS власникові щоразу, як ти запускаєш `npm test`. А ще `appendFileSync("/var/log/alarms.log")` впаде на будь-якій машині, де цього шляху нема або нема прав. Політику, найцінніше, що є в класі, **не можна торкнутися без усієї інфраструктури довкола неї**. Ось як DIP-вада відчувається пальцями, а не в теорії: високе прибите до низького — і тягне його за собою в кожен тест.

## Ідея: ядро окремо, деталі — ззовні

Розв'язок ми вже назвали, тепер — точно. Один хід: витягнути **стабільне ядро** (політику) у клас, що не знає ні про Twilio, ні про файл, ні про годинник; а кожну волатильну деталь заховати за **вузьким портом** — інтерфейсом рівно на одну дію — і **подавати ззовні** готовою. Це те, що звуть [впорскуванням залежності](book:programming/dependency-injection): залежність не створюють усередині оператором `new`, а вручають через конструктор.

> 💡 [Впорскування залежності](book:programming/dependency-injection) — замість того щоб об'єкт сам створював те, від чого залежить (`new TwilioClient()` усередині), готову залежність передають йому ззовні (у конструктор). Так той самий об'єкт у проді дістає справжній адаптер, а в тесті — дублер, і його код при цьому не міняється ні на рядок.

Зібрати конкретне з конкретним усе одно колись треба — але **в одному місці**: там, де застосунок стартує. Це місце зветься [композиційний корінь](book:programming/di-container) (термін закріпив Марк Зееман близько 2011 року, *статус: усталений у спільноті DI*): єдина точка, найближча до входу програми, де будують об'єктний граф — і тільки там живе `new` конкретних деталей. Самі порти й адаптери — це словник [гексагональної архітектури](book:programming/hexagonal-architecture): порт (інтерфейс) належить ядру, адаптер (реалізація) втикається в нього ззовні.

> 💡 [Композиційний корінь](book:programming/di-container) — одне місце застосунку (зазвичай коло `main`), де всі слабозв'язані об'єкти зшивають докупи: створюють конкретні адаптери й передають їх у конструктори. Решта коду ніколи не створює свої залежності сама — лише приймає їх. Так «брудні» `new` не розповзаються по проєкту, а сидять в одній купці, яку легко читати й підмінювати.

Ось як виглядає граф залежностей після ходу — і в ньому вся сіль DIP:

![Угорі блок AlarmPolicy — стабільне ядро; від нього дві стрілки вниз у два порти-абстракції Notifier (send) і Clock (now), обведені синім. Знизу адаптери — SmsNotifier, PushNotifier, EmailNotifier — стрілками вгору впираються в порт Notifier; SystemClock і FixedClock — у порт Clock. І ядро згори, і адаптери знизу спрямовані в порт: стрілки залежності сходяться на абстракції.](/guide/progarch/solid-and-composition/solid-audit/img/object-graph.svg)

*Ключ у напрямі стрілок. І високорівнева політика згори, і низькорівневі адаптери знизу залежать від того самого порту посередині — жоден не залежить від іншого напряму. Це і є інверсія: деталь тепер втикається в абстракцію, яку визначає ядро, а не ядро тягнеться по деталь.*

Тепер — по файлах.

## Робочий код

### Контракти: типи й порти

Спочатку — словник. Дані, якими обмінюються, і два порти. Порт навмисно **крихітний**: рівно та поверхня, якої потребує ядро, ні методом ширше (це вже ISP у дії).

:::tabs
```ts
// types.ts — дані, якими обмінюються шари
export type SensorEvent = { type: string; zone: string };
export type Message     = { to: string; body: string };

// ports.ts — вузькі абстракції, які визначає ЯДРО
import type { Message } from "./types";

export interface Notifier { send(msg: Message): Promise<void>; }  // рівно одна дія
export interface Clock    { now(): Date; }
```
```py
# models.py — дані, якими обмінюються шари (не types.py: так зветься модуль стандартної бібліотеки)
from dataclasses import dataclass

@dataclass(frozen=True)
class SensorEvent:
    type: str
    zone: str

@dataclass(frozen=True)
class Message:
    to: str
    body: str

# ports.py — вузькі абстракції, які визначає ЯДРО
from typing import Protocol
from datetime import datetime
from models import Message

class Notifier(Protocol):                       # рівно одна дія
    async def send(self, msg: Message) -> None: ...

class Clock(Protocol):
    def now(self) -> datetime: ...
```
:::

Зверни увагу на одну відмінність, яка згодом стане важливою для LSP. У TypeScript адаптер мусить написати `implements Notifier` — це декларація наміру, яку компілятор звірить. У Python `Protocol` **структурний**: будь-що з методом `send(msg) -> None` уже вважається `Notifier`, без жодного «implements». Це зручно — і водночас пастка: тип нічого не гарантує про **поведінку**, лише про форму. Тримай це в голові.

### Чисте ядро: AlarmPolicy

А ось і серце — політика, і **нічого крім неї**. Ні `import twilio`, ні `fs`, ні `new Date()`. Тільки два порти в конструкторі й одне рішення.

Формування тексту виносимо в окрему **чисту функцію** — не тому, що «так модно», а тому, що це окремий актор (тон спілкування з клієнтом) і окрема потреба: модуль звітності захоче той самий рядок, не надсилаючи нічого. [Чиста функція](book:programming/pure-functions-side-effects) — без побічних ефектів, лише вхід → вихід — тестується без жодного оточення.

:::tabs
```ts
// format.ts — окремий актор (тон), чиста функція. Час беремо ЯВНО, не з Date.now().
export function formatAlarm(zone: string, at: Date): string {
  const hh = String(at.getHours()).padStart(2, "0");
  const mm = String(at.getMinutes()).padStart(2, "0");
  return `Рух у зоні «${zone}» о ${hh}:${mm}`;
}

// policy.ts — стабільне ядро. Залежить ЛИШЕ від портів.
import type { SensorEvent } from "./types";
import type { Notifier, Clock } from "./ports";
import { formatAlarm } from "./format";

export class AlarmPolicy {
  private armed = false;
  constructor(private readonly notifier: Notifier,
              private readonly clock: Clock) {}      // деталі подано ЗЗОВНІ

  arm()    { this.armed = true; }
  disarm() { this.armed = false; }

  async handle(ev: SensorEvent): Promise<void> {
    if (ev.type !== "motion" || !this.armed) return; // політика тривоги…
    if (ev.zone === "pet-safe") return;              // …і тільки вона
    const body = formatAlarm(ev.zone, this.clock.now());
    await this.notifier.send({ to: "owner", body });
  }
}
```
```py
# format.py — окремий актор (тон), чиста функція. Час беремо ЯВНО.
from datetime import datetime

def format_alarm(zone: str, at: datetime) -> str:
    return f"Рух у зоні «{zone}» о {at:%H:%M}"

# policy.py — стабільне ядро. Залежить ЛИШЕ від портів.
from ports import Notifier, Clock
from models import SensorEvent, Message

class AlarmPolicy:
    def __init__(self, notifier: Notifier, clock: Clock) -> None:
        self._notifier, self._clock = notifier, clock   # подано ЗЗОВНІ
        self._armed = False

    def arm(self)    -> None: self._armed = True
    def disarm(self) -> None: self._armed = False

    async def handle(self, ev: SensorEvent) -> None:
        if ev.type != "motion" or not self._armed: return  # політика тривоги…
        if ev.zone == "pet-safe": return                   # …і тільки вона
        body = format_alarm(ev.zone, self._clock.now())
        await self._notifier.send(Message(to="owner", body=body))
```
:::

Помітив, що навіть годинник — залежність? Це не педантизм. `this.clock.now()` замість `new Date()` — саме те, що зробить тест на текст із часом **детермінованим**: у проді стоятиме системний годинник, у тесті — застиглий на `23:05`, і той самий код видасть той самий рядок щоразу. Волатильне — це не лише мережа; поточний час теж «пливе», тож і його ми вкорінили за портом.

### Адаптери: Twilio живе тут

Тепер — волатильні деталі, кожна окремим адаптером. `SmsNotifier` — це те **єдине** місце, де тепер існує Twilio і де живуть номери телефонів. Ядро про них не знає й знати не мусить: воно каже `to: "owner"`, а хто такий «owner» і який у нього номер — клопіт адаптера.

```ts
// adapters/sms.ts — увесь Twilio замкнено ТУТ.
import type { Notifier } from "../ports";
import type { Message } from "../types";

// Мінімальна форма клієнта Twilio, якою ми користуємось. Справжній клієнт її задовольняє,
// а в тесті адаптера можна підставити фейковий HTTP — сам адаптер теж стає тестованим.
export interface TwilioLike {
  messages: { create(o: { to: string; from: string; body: string }): Promise<{ sid: string }> };
}

export class SmsNotifier implements Notifier {
  constructor(private readonly client: TwilioLike,
              private readonly ownerPhone: string,
              private readonly fromPhone: string) {}

  async send(m: Message): Promise<void> {
    // Тут — і тільки тут — логічний «owner» перетворюється на номер, а Message — на SMS.
    await this.client.messages.create({ to: this.ownerPhone, from: this.fromPhone, body: m.body });
  }
}

// adapters/push.ts — інший канал, той самий вузький порт.
import type { Notifier } from "../ports";
import type { Message } from "../types";

export interface PushChannel { push(deviceTag: string, text: string): Promise<void>; }

export class PushNotifier implements Notifier {
  constructor(private readonly channel: PushChannel, private readonly deviceTag: string) {}
  async send(m: Message): Promise<void> { await this.channel.push(this.deviceTag, m.body); }
}

// adapters/clock.ts — системний годинник як адаптер порту Clock.
import type { Clock } from "../ports";
export class SystemClock implements Clock { now(): Date { return new Date(); } }
```

Кожен адаптер — тонка обгортка: перекласти `Message` мовою свого каналу й віддати вендорові. Уся «брудна» специфіка (ключі, номери, формат виклику Twilio) стиснута в ці кілька рядків і не тече нікуди далі.

### Композиційний корінь

І нарешті — місце, де конкретне зустрічається з конкретним. Один файл, найближчий до входу. **Тільки тут** з'являється `new` живих адаптерів і `twilio(...)`; усе інше проєкту лише **приймає** залежності, не створює їх.

```ts
// main.ts — композиційний корінь. Єдине місце збирання графа.
import twilio from "twilio";
import { AlarmPolicy } from "./policy";
import { SmsNotifier } from "./adapters/sms";
import { SystemClock } from "./adapters/clock";
import type { SensorEvent } from "./types";

export function buildPolicy(): AlarmPolicy {
  // Ось тут — і ніде більше — читаємо секрети й будуємо конкретне.
  const client = twilio(process.env.TWILIO_SID!, process.env.TWILIO_TOKEN!);
  const sms    = new SmsNotifier(client, process.env.OWNER_PHONE!, process.env.TWILIO_FROM!);
  const clock  = new SystemClock();

  const policy = new AlarmPolicy(sms, clock);   // деталі впорснуто в ядро
  policy.arm();
  return policy;
}

// десь у старті: підписуємо політику на потік подій із давачів
function wire(bus: { on(ev: "sensor", cb: (e: SensorEvent) => void): void }) {
  const policy = buildPolicy();
  bus.on("sensor", (ev) => { void policy.handle(ev); });
}
```

Порівняй із класом «до»: там `twilio(...)` жив усередині `handle`, тобто відроджувався на **кожній події** і всередині логіки тривоги. Тут він народжується **раз**, у корені, і крізь конструктор потрапляє в політику як абстрактний `Notifier`. Ядро зшите з інфраструктурою, але шов між ними — чіткий і в одному місці.

## Тести, що роблять виграш видимим

А ось те, заради чого все й затівалось. Три тести — по одному на літеру, що найдужче боліла, — і кожен **не пройшов би** над старим класом.

### DIP: політику судять без мережі

Той самий тест «про кота», що над `AlarmDispatcher` вимагав Twilio-акаунта, тепер — чиста пам'ять і мілісекунди. Замість справжнього нотифаєра ставимо `RecordingNotifier` (запам'ятовує, що йому дали), замість системного годинника — `FixedClock`. Жодного `import twilio`, жодного файлу.

```ts
// test/doubles.ts — чесні дублери для тестів
import type { Notifier, Clock } from "../ports";
import type { Message } from "../types";

export class RecordingNotifier implements Notifier {
  readonly sent: Message[] = [];
  async send(m: Message): Promise<void> { this.sent.push(m); }   // записує прийняте
}
export class FixedClock implements Clock {
  constructor(private readonly at: Date) {}
  now(): Date { return this.at; }
}

// test/policy.test.ts — політику видно судити в ізоляції
import { AlarmPolicy } from "../policy";
import { RecordingNotifier, FixedClock } from "./doubles";

const at = new Date(2026, 6, 11, 23, 5);   // застиглий час: 23:05

test("кіт у pet-safe не піднімає тривоги", async () => {
  const spy = new RecordingNotifier();
  const policy = new AlarmPolicy(spy, new FixedClock(at));
  policy.arm();
  await policy.handle({ type: "motion", zone: "pet-safe" });
  expect(spy.sent).toHaveLength(0);        // жодного повідомлення — і жодного SMS
});

test("рух в охоронюваній зоні шле рівно одну тривогу з часом", async () => {
  const spy = new RecordingNotifier();
  const policy = new AlarmPolicy(spy, new FixedClock(at));
  policy.arm();
  await policy.handle({ type: "motion", zone: "hallway" });
  expect(spy.sent).toEqual([{ to: "owner", body: "Рух у зоні «hallway» о 23:05" }]);
});

test("роззброєний дім мовчить", async () => {
  const spy = new RecordingNotifier();
  const policy = new AlarmPolicy(spy, new FixedClock(at));   // arm() не викликаємо
  await policy.handle({ type: "motion", zone: "hallway" });
  expect(spy.sent).toHaveLength(0);
});
```

Ось предметний доказ DIP: політику **судять без світу**. Тест детермінований (застиглий час дає точний рядок `23:05`), швидкий (нема мережі), безпечний (нікому не летить справжнє SMS). Це не бонус до чистоти — це і є те, що інверсія залежності **купує**: можливість перевіряти найцінніше окремо від найбруднішого.

### OCP: новий канал не чіпає політику

Власник хоче дублювати тривогу ще й на email. Над старим класом це означало «розкрий `handle` і додай гілку». Тут — **новий файл**, і жодного дотику до `policy.ts`.

Спершу дрібний композит: `Notifier`, що розсилає в кілька інших. Він сам — теж `Notifier` (той самий вузький порт), тож ядро й не помітить різниці між ним і одинарним адаптером.

```ts
// adapters/fanout.ts — Notifier, що віялом шле в кілька каналів. Сам — теж Notifier.
import type { Notifier } from "../ports";
import type { Message } from "../types";

export class FanoutNotifier implements Notifier {
  constructor(private readonly targets: Notifier[]) {}
  async send(m: Message): Promise<void> {
    await Promise.all(this.targets.map((t) => t.send(m)));
  }
}

// adapters/email.ts — НОВИЙ канал. Новий файл, нова реалізація того ж порту.
import type { Notifier } from "../ports";
import type { Message } from "../types";

export interface Mailer { send(o: { to: string; subject: string; text: string }): Promise<void>; }

export class EmailNotifier implements Notifier {
  constructor(private readonly mailer: Mailer, private readonly to: string) {}
  async send(m: Message): Promise<void> {
    await this.mailer.send({ to: this.to, subject: "Тривога Digital Homes", text: m.body });
  }
}
```

Тепер додати email у прод — це **один рядок** у композиційному корені: обгорнути наявні адаптери у `FanoutNotifier`.

```ts
// main.ts — зміна ЛИШЕ тут: було `new AlarmPolicy(sms, clock)`, стало —
const email  = new EmailNotifier(mailer, process.env.OWNER_EMAIL!);
const policy = new AlarmPolicy(new FanoutNotifier([sms, email]), clock);
```

І от чим OCP стає **видимим**, а не обіцяним. Подивись на `git diff --stat` цієї зміни:

```
 adapters/email.ts  | 12 ++++++++++++   (новий файл)
 adapters/fanout.ts |  9 +++++++++      (новий файл)
 main.ts            |  2 +-             (один рядок зшивання)
 policy.ts          |  0               ← ЯДРА НЕ ТОРКНУЛИСЬ
 format.ts          |  0
```

Нуль рядків у `policy.ts` — це і є «відкрито до розширення, закрито до змін», у формі, під якою можна підписатися на рев'ю. А тест підтверджує, що новий канал справді працює й **та сама** політика його живить:

```ts
// test/ocp.test.ts — той самий AlarmPolicy, новий канал, ані рядка змін у ядрі
import { AlarmPolicy } from "../policy";
import { FanoutNotifier } from "../adapters/fanout";
import { RecordingNotifier, FixedClock } from "./doubles";

test("email додається без правок політики", async () => {
  const sms   = new RecordingNotifier();      // за ними в тесті — будь-які канали
  const email = new RecordingNotifier();
  const policy = new AlarmPolicy(
    new FanoutNotifier([sms, email]), new FixedClock(new Date(2026, 6, 11, 23, 5)),
  );
  policy.arm();
  await policy.handle({ type: "motion", zone: "hallway" });
  expect(sms.sent).toHaveLength(1);
  expect(email.sent).toHaveLength(1);         // новий канал отримав тривогу
});
```

### LSP: чесний дублер проти «мовчазного»

Найтонше — і найважливіше. В аудиті ми назвали спокусу: підклас `TestDispatcher`, що «нічого насправді не шле». Тепер спокуса переїхала на порт — написати `Notifier`, що вдає відправлення. І тут криється пастка, яку **тип не ловить**.

Ось два дублери. Один чесний, другий — та сама пастка:

:::tabs
```ts
// чесний: сток видимий, контракт справді виконано
export class RecordingNotifier implements Notifier {
  readonly sent: Message[] = [];
  async send(m: Message): Promise<void> { this.sent.push(m); }
}

// ПАСТКА: форма правильна, поведінка бреше — «send» нічого не робить
export class SilentNotifier implements Notifier {
  async send(_m: Message): Promise<void> { /* вдає, що надіслав */ }
}
```
```py
# чесний: сток видимий, контракт справді виконано
class RecordingNotifier:
    def __init__(self) -> None: self.sent: list[Message] = []
    async def send(self, msg: Message) -> None: self.sent.append(msg)

# ПАСТКА: у Python навіть «implements» писати не треба — структурний Protocol
# сам вважає це за Notifier. Форма правильна, поведінка бреше.
class SilentNotifier:
    async def send(self, msg: Message) -> None: ...   # вдає, що надіслав
```
:::

Обидва мають метод `send(m) -> Promise<void>`. Обидва проходять компілятор (а в Python — навіть без декларації). За **типом** вони взаємозамінні. І саме тут ховається катастрофа: хтось пише `class NoopNotifier implements Notifier` «щоб вимкнути сповіщення на стейджингу», втикає його в корінь — і система рапортує «власника попереджено», доки насправді ніхто нічого не отримав. Тип змовчав. LSP — про **поведінку**, не про форму: підстановка законна лише тоді, коли нащадок **чесно тримає обіцянку** предка. `SilentNotifier` обіцянку порушує, а `implements` цього не бачить.

Що ж бачить? **Контракт-тест** — виконувана форма обіцянки. Це та сама ідея, що [контрактні тести](book:programming/contract-testing): один набір перевірок, який ганяють проти **кожної** реалізації інтерфейсу, щоб усі вони поводились однаково там, де на них спираються.

> 💡 [Контрактний тест](book:programming/contract-testing) — тест, прив'язаний не до конкретного класу, а до **інтерфейсу**: він параметризований фабрикою реалізації й перевіряє поведінку, яку кожен, хто стоїть за цим інтерфейсом, зобов'язаний дати. Один контракт — багато реалізацій — одна поведінка. Саме він робить LSP перевірюваним замість «на слово».

Питання лише — **що** саме перевіряти. Ось де треба думати чесно. Обіцянка `Notifier.send` не може бути «повідомлення доставлено» — жоден реальний адаптер такого не гарантує (мережа падає). Але вона й не порожня. Чесна обіцянка на правильній висоті: **після того як `send(m)` завершився без помилки, `m` спостережно опинилося у стоці доставки цього нотифаєра**. У `RecordingNotifier` сток — масив у пам'яті; у `SmsNotifier` — «вихідні» Twilio; у справжньому проді — черга оператора. Різні стоки, одна обіцянка. Запишемо її:

:::tabs
```ts
// test/notifier.contract.ts — ОДИН контракт на будь-яку реалізацію Notifier
import type { Notifier } from "../ports";
import type { Message } from "../types";

export function notifierContract(
  name: string,
  make: () => { notifier: Notifier; delivered: () => Message[] },
) {
  test(`${name}: доставляє повідомлення, яке прийняв`, async () => {
    const { notifier, delivered } = make();
    const m: Message = { to: "owner", body: "проба" };
    await notifier.send(m);
    expect(delivered()).toContainEqual(m);   // мусить з'явитися у стоці
  });
}

// чесний дублер: сток — його масив. ПРОХОДИТЬ.
notifierContract("RecordingNotifier", () => {
  const n = new RecordingNotifier();
  return { notifier: n, delivered: () => n.sent };
});

// реальний адаптер: сток — «вихідні» фейкового Twilio. ТЕЖ ПРОХОДИТЬ.
class FakeTwilio {
  readonly out: { to: string; from: string; body: string }[] = [];
  messages = { create: async (o: any) => { this.out.push(o); return { sid: "SM_test" }; } };
}
notifierContract("SmsNotifier", () => {
  const fake = new FakeTwilio();
  const n = new SmsNotifier(fake, "+380000000000", "+380111111111");
  // сток адаптера — його вихідні; перекладаємо назад мовою Message
  return { notifier: n, delivered: () => fake.out.map((o) => ({ to: "owner", body: o.body })) };
});

// «мовчазний»: наповнити сток нема чим — ПАДАЄ. Ось як пастку ловлять.
notifierContract("SilentNotifier (пастка)", () => {
  const n = new SilentNotifier();
  return { notifier: n, delivered: () => [] };
});
```
```py
# один контракт на будь-яку реалізацію Notifier (pytest)
import pytest
from models import Message

def notifier_contract(make):
    async def run() -> None:
        notifier, delivered = make()
        m = Message(to="owner", body="проба")
        await notifier.send(m)
        assert m in delivered()          # мусить з'явитися у стоці
    return run

@pytest.mark.asyncio
async def test_recording():              # чесний — ПРОХОДИТЬ
    n = RecordingNotifier()
    await notifier_contract(lambda: (n, lambda: n.sent))()

@pytest.mark.asyncio
async def test_silent_trap():            # «мовчазний» — ПАДАЄ, і саме так його ловлять
    n = SilentNotifier()
    await notifier_contract(lambda: (n, lambda: []))()
```
:::

Придивись, що сталося з пасткою. Щоб `SilentNotifier` **пройшов** контракт, його `delivered()` мусив би повернути прийняте `m`. Але звідки — він же нічого не зберіг. Єдиний спосіб «пройти» — почати справді записувати, тобто перестати бути мовчазним і стати чесним. Контракт не можна вдовольнити брехнею: він **змушує** реалізацію справді зробити спостережний хід. Ось і весь захист від LSP-порушення — виконуваний, а не на слово.

![Посередині — ворота «Контракт Notifier: після send(m) — m у стоці доставки». Ліворуч у них заходять три кандидати: RecordingNotifier (зелений, сток — масив) і SmsNotifier (сток — вихідні Twilio) проходять праворуч у блок «підставляється всюди, де стоїть Notifier»; SilentNotifier (червоний, вдає) впирається у ворота з написом «сток порожній — контракт не виконано, до Notifier не пускають». Той самий тест женуть на кожну реалізацію.](/guide/progarch/solid-and-composition/solid-audit/img/contract-gate.svg)

*Контракт-тест — ворота на вході в роль `Notifier`. Хто спостережно доставив прийняте, той підставляється будь-де замість справжнього нотифаєра. «Мовчазний» дублер має правильну форму, але не проходить обіцянку — і ворота ловлять його до того, як він потрапить у прод під виглядом справжнього.*

Іменування, до речі, не випадкове. `RecordingNotifier`, що записує виклики для перевірки тестом, у класифікації дублерів Джерарда Мессароса (книга «xUnit Test Patterns», 2007, *статус: усталений канон тестування*) зветься **шпигун** (spy); робоча полегшена реалізація на кшталт in-memory — **фейк** (fake). `SilentNotifier` — це вироджений **заглушка** (stub), що повертає «успіх» без ефекту. Різниця між шпигуном і німою заглушкою — не в типі, а рівно в тому, чи чесно вони тримають контракт. Тому LSP і не ловиться компілятором: він живе на рівні поведінки, і перевіряють його поведінкою.

## Складність і пастки

Розв'язок красивий, але провалити його легко — і майже завжди на одному з кількох місць.

**Мовчазний дублер, що робить тести зеленими, а прод — німим.** Найпідступніше. Ти пишеш «заглушку, щоб вимкнути сповіщення в певному середовищі», вона має правильний тип, компілюється, деплоїться — і система впевнено рапортує «власника попереджено», доки насправді жодна тривога не пішла. Тести при цьому **зелені**, бо вони й перевіряли лише «`handle` не впав». Ліки одні: **контракт-тест на порт**, який ганяють проти всіх реалізацій. Без нього LSP лишається побажанням; з ним німа заглушка червоніє на CI, а не в домі, де спрацював давач.

**Обіцянка не на тій висоті.** Другий бік тієї ж медалі. Спокуса зробити контракт сильним — «після `send` повідомлення **доставлено**». Але тоді жоден реальний адаптер його не виконає: Twilio інколи відмовляє, мережа падає. Контракт, який справжня реалізація не може дотримати, — гірший за жодного: він або бреше, або блокує чесні адаптери. Тому обіцянку кладуть рівно там, де її **тримають усі**: «прийнято до доставки, спостережно у стоці». А що робити з відмовою й повтором — питання адаптера й того, хто його викликає, і воно живе **в адаптері**, не в політиці. Ядро не має знати ні про ретраї Twilio, ні про його коди помилок.

**`new` конкретного, що втік із кореня.** Уся конструкція тримається на тому, що деталі створюють **лише** в композиційному корені. Варто одному `new SmsNotifier(...)` чи `twilio(...)` заповзти назад у політику «на хвилинку» — і DIP тихо зламано, а тест «про кота» знову тягне мережу. Проста сторожа: заборонити `import` вендорських пакетів (`twilio`, `nodemailer`, `fs`) будь-де, крім теки `adapters/` і `main.ts`, — хоч лінтером, хоч `grep` у CI. Дешевий гейт, що не дає інверсії розсипатися з часом.

**Регулятори на максимум.** Протиотрута, про яку ми вже говорили. Порт `Notifier` — **один** метод; не піддавайся спокусі роздути його на `sendSms`/`sendEmail`/`sendPush` — це вбило б і ISP, і всю підставність. І не заводь порт там, де реалізація навіки одна: абстракція з однією реалізацією на весь вік проєкту — податок на непрямість, а не гнучкість. Тут ми ввели `Notifier`, `Clock`, `FanoutNotifier` не тому, що «більше портів — краще», а тому, що по кожному вже тиснула **реальна** зміна: другий канал на порозі, час треба застигати в тестах, каналів стало кілька. Нема тиску — тримай простим.

**Годинник, який забули вкорінити.** Дрібна, але кусюча. Лишиш `new Date()` десь у політиці — і тест на текст із часом стане плавучим: о 23:59 він зелений, о півночі червоний, а на CI в іншому часовому поясі падає завжди. Час — така сама волатильна деталь, як мережа; вкорінюй його за `Clock` і подавай `FixedClock` у тестах. (Тонкощі настінного проти монотонного часу — окрема довга розмова, але правило вкорінення діє вже тут.)

> 🔧 **Навіщо це.** Спільна нитка всіх пасток одна: **структура сама себе не втримає**. Інверсію з'їдає перший `new`, що втік у ядро; LSP — перший німий дублер, що проходить за типом; ISP — перший «зручний» метод, дописаний у порт. Тому виграш кожної літери й закріплюють **тестом або гейтом**, який червоніє на регресі: контракт-тест стереже підстановку, `git diff` по `policy.ts` стереже OCP, ізольований тест ядра стереже DIP, лінт на вендор-імпорти стереже напрям залежностей. Принцип, за яким не стоїть перевірка, тихо вивітрюється за півроку — рівно так, як вивітрився первісний `AlarmDispatcher`.

## Що лишається в руках

Ми взяли `AlarmDispatcher`, у якому політика тривоги, формування тексту, Twilio й файловий лог були сплавлені в один метод, і розклали його на **стабільне ядро** (`AlarmPolicy` + чиста `formatAlarm`), **вузькі порти** (`Notifier`, `Clock`) і **адаптери** (`SmsNotifier`, `PushNotifier`, `EmailNotifier`, `SystemClock`), зшиті в одному композиційному корені. Той самий один хід — витягти незмінне, вкорінити змінне, подати ззовні — і всі п'ять оцінок перекинулись у зелене.

Але справжня різниця не в тому, що код «став чистіший». Вона в тому, що тепер кожну літеру видно **виконуваним доказом**: політику судять без мережі (DIP), новий канал додається з нулем змін у ядрі (OCP), а будь-який дублер, що проходить контракт-ворота, підставляється всюди — тоді як «мовчазний» ловиться до прода (LSP). SRP та ISP при цьому не окремі перевірки, а те, що зробило перші три можливими: один актор на файл і порт на одну дію.

Ось що забрати з рук у наступні кроки: **рефакторинг завершений не тоді, коли компілюється, а тоді, коли на кожен виграш є тест, що почервоніє на регресі**. Аудит показав, де різати; композиція розрізала; а ці три тести — те, що не дасть розрізаному знову зрости докупи.
