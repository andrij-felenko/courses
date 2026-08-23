# ⚙️ Повний DH v2: одна правда на двоє дверей, і тест, що це доводить

Кістяк показав форму — три кільця, стрілки всередину, двоє дверей у спільний сервіс. Але кістяк тим і підступний, що на ньому все гладко, доки його не спробуєш запустити. `decide` у ньому мав раптом три аргументи, узяті ніби нізвідки; порти стояли самими назвами без жодної реалізації; `build` кликав `OneWireThermometer` і `FakeSensor`, яких ми ще ні рядком не написали; а головна обіцянка модуля — «обидві двері звіряються з однією правдою» — лишалася словом, бо не було тесту, що притиснув би її до стіни. Цей розбір добудовує все, чого бракувало: кожне кільце заповнене справжнім кодом, ядро зведене з тим, що виточили попередні кроки, обидві двері справді живуть разом в одному процесі, а наприкінці — тест, який зеленим доводить головний зиск.

## Задача — зібрати робоче, а не намалювати гарне

Випишімо ціль точно. Один файл, що кладеться на диск і запускається. У ньому — усі три кільця живим кодом: **ядро** (`Reading`, `Config`, `Device`, чисте `decide`), **три драйвовані порти** (`Sensor`, `Heater`, `DeviceRepository`), кожен у двох виданнях (справжній адаптер і підробка), **застосунок** `HubService` з усіма чотирма сценаріями, **двоє дверей** — автономний цикл у фоновому потоці й обробник CLI поруч, — **точка збірки** `build(env)`, що зводить абстрактне з конкретним, і **тест**, який ганяє сервіс самими підробками.

Від тесту хочемо двох доказів, не одного. Перший: цикл і CLI справді ділять **одну** правду — те, що записала одна двер, наступне читання іншої вже бачить. Другий, тонший: дописати завтра HTTP — це **не** зачепити ядра, третій тонкий дзвонар стає збоку, і жоден рядок домену не здригається. Обидва докази мусять бути зеленими без грама заліза, без секунди `sleep` і без живої бази — інакше вся форма лишається малюнком.

І одне залізне обмеження, яке робить збірку чесною: **ядро мусить зійтися** з тим, що ми вже написали. `decide` тут не новий — це те саме правило, що [гартувалося смугою гістерезису на порті пристрою](root:progarch/hexagon-when-overkill/proj-dh-device-port.md) і говорило `Reading`-ами [ще з v1](root:progarch/dh-v1-modules). Якщо в зібраному домі воно раптом рахує інакше — гріш ціна всій формі. Тож почнімо саме з ядра й зведімо його руками.

## Ідея: усі кроки модуля сходяться в одне `decide`

Уся хитрість збірки — в одному місці, і воно в центрі. За модуль ми виточили правило «коли гріти» **двічі, різними гранями**, і тепер їх треба стулити в одну функцію без шва.

[v1 дав рішенню тіло значення](root:progarch/dh-v1-modules): `decide` брало `Reading` (число в °C плюс прапорець `ok`, «чи вірити») і повертало команду. Але v1-ше правило було **безпам'ятне** — воно дивилося лише на поточне число й поріг, тож коло самого порога, де шум гойдає вимір, реле клацало щотакту. [Крок про порт пристрою це вилікував гістерезисом](root:progarch/hexagon-when-overkill/proj-dh-device-port.md): чесне правило тримає не крапку, а **смугу** — вмикається, коли впало під поріг, і не гасить, доки не перегрілося на пів градуса вище. А щоб знати, у якому кінці смуги ти зараз, правилу потрібен **попередній стан** `heating`, і — це принципово — цей стан правило приймає **ззовні**, а не ховає в собі, бо чиста функція станів не тримає.

Зведення обох граней дає рівно одну сигнатуру: `decide(reading, cfg, heating) → heating`. На вхід — число з v1 (`Reading`), поріг з v1 (`Config`) і попередній стан із кроку про порт; на вихід — **новий** стан гріння. Правило лишається чистим островом: ті самі входи дають той самий вихід, стан лежить не в ньому, а на краю ядра, у `HubService`. Ось воно, зведене:

:::tabs
```py
from dataclasses import dataclass, replace
from typing import Protocol

HYSTERESIS = 0.5                     # °C — ширина смуги понад поріг (з кроку про порт)

@dataclass(frozen=True)
class Reading:                       # значення давача з v1: одиниця й статус — у типі
    celsius: float                   # ЗАВЖДИ °C
    ok: bool = True                  # чи це справжнє свіже число

@dataclass(frozen=True)
class Config:
    threshold: float = 20.0          # поріг — вхід рішення, а не його нутрощі

@dataclass(frozen=True)
class Device:                        # доменний пристрій із реєстру
    kind: str                        # "lock", "lamp", "thermostat"…
    room: str
    state: str = "unknown"

def decide(r: Reading, cfg: Config, heating: bool) -> bool:
    if not r.ok:                     # давач мовчить → безпечний спокій (як вирішив v1)
        return False
    if heating:                      # вже гріємо — тримаємо, доки не перескочили верх смуги
        return r.celsius < cfg.threshold + HYSTERESIS
    return r.celsius < cfg.threshold # ще ні — вмикаємо, тільки-но впало під поріг
```
```ts
const HYSTERESIS = 0.5;              // °C — ширина смуги понад поріг (з кроку про порт)

interface Reading { readonly celsius: number; readonly ok: boolean; }  // з v1
interface Config  { readonly threshold: number; }
interface Device  { readonly kind: string; readonly room: string; readonly state: string; }

function decide(r: Reading, cfg: Config, heating: boolean): boolean {
  if (!r.ok) return false;                                    // давач мовчить → спокій (як v1)
  if (heating) return r.celsius < cfg.threshold + HYSTERESIS; // гріємо — тримаємо смугу
  return r.celsius < cfg.threshold;                           // ще ні — вмикаємо під порогом
}
```
:::

Придивіться, де тут пам'ять і де її **немає**. Пам'ять — у смузі: візьміть 20.3 °C. Якщо ми вже гріли, `decide` каже «так» (20.3 ще не перескочило верх смуги 20.5); якщо не гріли — «ні» (20.3 вже над порогом 20.0). Одна температура, дві відповіді, залежно від того, що робили мить тому — оце й глушить клацання. А от у **самій функції** пам'яті немає ані краплі: стан їй передають параметром і забирають результатом. Це те, на чому стоятиме тест, — правило без прихованого стану можна тицяти в будь-яку точку смуги за мілісекунду.

І один рядок вартий окремої зупинки — `if not r.ok: return False`. Це успадкована з v1 постанова: коли давач замовк (таймаут, `CRC=NO`), числу вірити не можна, тож безпечніше **не гріти наосліп**, ніж гріти за брехнею. Ми свідомо тягнемо цю поведінку в зведене ядро незмінною — саме тому воно й «зведене», а не «переписане».

> 🔧 **Навіщо це.** Три аргументи `decide`, що в кістяку виглядали свавіллям, — насправді підпис під двома попередніми кроками. `Reading` прийшов від v1 (одиниця й «вірю/не вірю» живуть у типі, не в чиїйсь голові), смуга `HYSTERESIS` — від порту пристрою, а те, що `heating` **передають ззовні**, а не ховають усередину, — це умова чистоти, без якої тест став би залежним від порядку й крихким. Зведене ядро не додає нового правила; воно бере два вже доведені й стуляє їх без шва — і рівно тому зібраний дім рахує так само, як рахували його частини.

## Порти й обидва видання адаптерів

Ядро чисте — тепер дамо йому очі й руки, але через **обіцянки**, не через залізо. Три драйвовані порти оголошують, що застосунок уміє питати у світу, а конкретні класи цю обіцянку сповняють — кожен двічі: справжнім залізом для проду й пам'яттю для тесту.

:::tabs
```py
# ── Порти: застосунок залежить від них, а не від марки заліза ──
class Sensor(Protocol):
    def read(self) -> Reading: ...

class Heater(Protocol):
    def on(self) -> None: ...        # ідемпотентно
    def off(self) -> None: ...

class DeviceRepository(Protocol):
    def save(self, d: Device) -> None: ...
    def all(self) -> list[Device]: ...

# ── Справжні адаптери: єдині, хто говорить мовою заліза ──
class OneWireThermometer:            # реалізує Sensor: DS18B20 по 1-Wire
    def __init__(self, w1_id: str):
        self._path = f"/sys/bus/w1/devices/{w1_id}/w1_slave"
    def read(self) -> Reading:
        try:
            text = open(self._path).read()          # "...crc=.. YES\n.. t=20125"
            milli = int(text.split("t=")[-1])       # DS18B20 віддає мілі-градуси
            return Reading(celsius=milli / 1000, ok=True)   # переклад одиниць ТУТ, на краю
        except (OSError, ValueError):
            return Reading(celsius=float("nan"), ok=False)  # німий давач → «не вірю»

class SmartPlug:                     # реалізує Heater: Wi-Fi розетка (напр. Shelly)
    def __init__(self, url: str):
        self._url, self._on = url, False
    def on(self) -> None:
        if not self._on: self._toggle("on");  self._on = True
    def off(self) -> None:
        if self._on:     self._toggle("off"); self._on = False
    def _toggle(self, turn: str) -> None:
        import urllib.request
        urllib.request.urlopen(f"{self._url}/relay/0?turn={turn}", timeout=3)

# ── Підробки: кожен порт має свою, дім живе в пам'яті ──
class FakeSensor:                    # реалізує Sensor: віддає задану температуру
    def __init__(self, celsius: float = 18.0):
        self.celsius, self.ok = celsius, True   # тест крутить ці поля, граючи сценарій
    def read(self) -> Reading:
        return Reading(self.celsius, self.ok)

class FakeHeater:                    # реалізує Heater: журнал перемикань, без реле
    def __init__(self):
        self._on = False
        self.log: list[bool] = []
    def on(self) -> None:
        if not self._on: self._on = True;  self.log.append(True)   # лише реальні зміни
    def off(self) -> None:
        if self._on:     self._on = False; self.log.append(False)

class InMemoryDeviceRepository:      # реалізує DeviceRepository: реєстр у пам'яті
    def __init__(self):
        self._items: list[Device] = []
    def save(self, d: Device) -> None:
        self._items.append(d)
    def all(self) -> list[Device]:
        return list(self._items)
```
```ts
// ── Порти: застосунок залежить від них, а не від марки заліза ──
interface Sensor { read(): Reading; }
interface Heater { on(): void; off(): void; }          // on/off — ідемпотентні
interface DeviceRepository { save(d: Device): void; all(): Device[]; }

// ── Справжні адаптери: єдині, хто говорить мовою заліза ──
import { readFileSync } from "node:fs";

class OneWireThermometer implements Sensor {           // DS18B20 по 1-Wire
  constructor(private w1Id: string) {}
  read(): Reading {
    try {
      const text = readFileSync(`/sys/bus/w1/devices/${this.w1Id}/w1_slave`, "utf8");
      const milli = parseInt(text.split("t=").pop()!, 10);   // мілі-градуси
      return { celsius: milli / 1000, ok: true };            // переклад ТУТ, на краю
    } catch {
      return { celsius: NaN, ok: false };                    // німий давач → «не вірю»
    }
  }
}

class SmartPlug implements Heater {                    // Wi-Fi розетка (Shelly)
  private on_ = false;
  constructor(private url: string) {}
  on():  void { if (!this.on_) { this.toggle("on");  this.on_ = true;  } }
  off(): void { if (this.on_)  { this.toggle("off"); this.on_ = false; } }
  private toggle(turn: string): void { void fetch(`${this.url}/relay/0?turn=${turn}`); }
}

// ── Підробки: кожен порт має свою, дім живе в пам'яті ──
class FakeSensor implements Sensor {                   // віддає задану температуру
  celsius = 18.0;
  ok = true;
  constructor(celsius = 18.0) { this.celsius = celsius; }   // тест крутить поля, граючи сценарій
  read(): Reading { return { celsius: this.celsius, ok: this.ok }; }
}

class FakeHeater implements Heater {                   // журнал перемикань, без реле
  private on_ = false;
  readonly log: boolean[] = [];
  on():  void { if (!this.on_) { this.on_ = true;  this.log.push(true);  } }   // лише реальні зміни
  off(): void { if (this.on_)  { this.on_ = false; this.log.push(false); } }
}

class InMemoryDeviceRepository implements DeviceRepository {   // реєстр у пам'яті
  private items: Device[] = [];
  save(d: Device): void { this.items.push(d); }
  all(): Device[] { return [...this.items]; }
}
```
:::

Порахуймо порти чесно, бо форма легко зсувається в рефлекс «обгортай усе». Драйвованих портів **три**, і кожен заробив своє окремим болем модуля: `Sensor` і `Heater` [заслужили шов на кроці про надмір](root:progarch/hexagon-when-overkill) — два різні годинники й тест без заліза; `DeviceRepository` [заробив своє на розвилці доступу до даних](root:progarch/data-access-choice) — зворотний вибір сховища й тест без бази. Жодного четвертого порту «про запас» ми не завели.

Затримаймося на одному рядку `OneWireThermometer`, бо в ньому весь сенс порту. Давач DS18B20 віддає не градуси, а **ціле число мілі-градусів** — `t=20125` означає 20.125 °C, так його показує ядро Linux у файлі `w1_slave`. Ділення на 1000 живе **тут, в адаптері, на самій межі** — і жоден мілі-градус не просочується в ядро. Це той самий діалект заліза, що [тихо зламав v0](root:progarch/dh-v1-modules), коли `18000` мовчки порівнювалося з `20.0`; тепер він помирає на краю, і `decide` бачить самі чисті °C. Підробки ж навмисне **чемніші**: `FakeSensor` віддає рівно те, що йому задали, `FakeHeater` пише журнал замість того, щоб клацати реле, а `InMemoryDeviceRepository` тримає реєстр списком. Про ціну цієї чемності — під кінець; поки що вона нам друг, бо робить тест керованим.

Одне зауваження про репозиторій: тут `InMemoryDeviceRepository` стоїть і за підробку в тесті, і за «бойову» реалізацію в збірці — реєстр поки живе в пам'яті. Це чесно: [сховище, що переживе рестарт](root:progarch/data-access-choice), — окремий тікет, і коли він прийде, SQLite стане за **той самий** порт `DeviceRepository`, не зачепивши ні сервіса, ні ядра.

## Застосунок: `HubService` з усіма сценаріями

Тепер серединне кільце — місце, куди сходяться обидві двері. `HubService` не робить вводу-виводу власними руками й не тримає жодного правила; він **диригує**, спираючись на порти, і тримає той єдиний стан, якому нема місця в чистому ядрі:

:::tabs
```py
@dataclass(frozen=True)
class HomeSnapshot:                  # DTO: плаский знімок назовні, а не живий об'єкт
    heating: bool
    devices: list[Device]

class HubService:
    def __init__(self, sensor: Sensor, heater: Heater,
                 devices: DeviceRepository, cfg: Config):
        self._sensor, self._heater = sensor, heater     # драйвовані порти — інтерфейси
        self._devices, self._cfg = devices, cfg
        self._heating = False                           # стан живе ТУТ, на краю ядра

    def tick(self) -> None:                             # сценарій дверей 1 (цикл)
        reading = self._sensor.read()
        self._heating = decide(reading, self._cfg, self._heating)   # те саме чисте ядро
        self._heater.on() if self._heating else self._heater.off()

    def add_device(self, d: Device) -> None:            # сценарій дверей 2 (CLI/HTTP)
        self._devices.save(d)

    def state(self) -> HomeSnapshot:                    # сценарій дверей 2
        return HomeSnapshot(self._heating, self._devices.all())

    def set_threshold(self, celsius: float) -> None:    # сценарій дверей 2
        self._cfg = replace(self._cfg, threshold=celsius)
```
```ts
interface HomeSnapshot { readonly heating: boolean; readonly devices: Device[]; }

class HubService {
  private heating = false;           // стан живе ТУТ, на краю ядра
  constructor(
    private sensor: Sensor,          // драйвовані порти — інтерфейси, не класи
    private heater: Heater,
    private devices: DeviceRepository,
    private cfg: Config,
  ) {}

  tick(): void {                                        // сценарій дверей 1 (цикл)
    const reading = this.sensor.read();
    this.heating = decide(reading, this.cfg, this.heating);  // те саме чисте ядро
    this.heating ? this.heater.on() : this.heater.off();
  }
  addDevice(d: Device): void { this.devices.save(d); }  // сценарій дверей 2
  state(): HomeSnapshot { return { heating: this.heating, devices: this.devices.all() }; }
  setThreshold(celsius: number): void { this.cfg = { ...this.cfg, threshold: celsius }; }
}
```
:::

Три деталі тут несуть усю вагу. По-перше, **де сидить стан**: `_heating` — поле сервіса, не глобальна змінна й не нутрощі `decide`. Це рівно той «край ядра», про який ішлося: правило чисте, а пам'ять про те, гріємо ми зараз чи ні, лежить на один крок назовні, у застосунку. `tick` бере цей стан, віддає чистому `decide` й **новим** значенням записує назад — коло замикається в сервісі, а не в правилі.

По-друге, `state` віддає не живий об'єкт, а `HomeSnapshot` — **плаский DTO**. Це не косметика: [минулий крок домовився не робити з дому балакучого розподіленого об'єкта](root:progarch/distributed-objects-trap), а перетинати межі грубо — знімком. `state()` і є той знімок: одне число `heating` і список пристроїв, зліплені в одну структуру, яку можна віддати назовні цілком, без ниток назад у сервіс. Коли завтра прийде HTTP, він серіалізує саме цей знімок, а не потягне клієнта смикати `HubService` по полю.

По-третє, `set_threshold` не мутує `Config` на місці, а робить **новий** через `replace` — бо `Config` незмінний. Стара конфігурація ніде не псується під ногами; сервіс просто починає з наступного тіку дивитися на нову. Це та сама дисципліна незмінності, що робить `decide` чистим, піднята на рівень застосунку.

## Двоє дверей і точка збірки

Тепер найтонше — впустити в дім **обидві** двері так, щоб вони жили разом і не побилися за стан. Автономний цикл мусить дихати сам, а обробник команд — чекати на людину; і крутитися вони мусять **одночасно**, звіряючись з одним `hub`.

:::tabs
```py
def run_loop(hub: HubService) -> None:      # двері 1: автономний цикл
    from time import sleep
    while True:
        hub.tick()
        sleep(30)

def run_cli(hub: HubService) -> None:       # двері 2: читаємо команди, поки дім живе
    import sys
    for line in sys.stdin:                  # головний потік блокується на вводі…
        match line.split():
            case ["state"]:
                s = hub.state()
                print(f"heating={s.heating}, пристроїв={len(s.devices)}")
            case ["set-threshold", c]:
                hub.set_threshold(float(c)); print(f"поріг → {c} °C")
            case ["add", kind, room]:
                hub.add_device(Device(kind, room)); print(f"додано {kind} у {room}")
            case ["quit"]:
                break
            case _:
                print("вживай: state | set-threshold <°C> | add <kind> <room> | quit")

def build(env: str) -> HubService:          # ТОЧКА ЗБІРКИ — єдине місце з конкретними іменами
    if env == "prod":
        sensor: Sensor = OneWireThermometer("28-0119a1b2c3d4")   # справжнє залізо
        heater: Heater = SmartPlug("http://192.168.1.50")
    else:
        sensor, heater = FakeSensor(), FakeHeater()              # підробки для тесту й розробки
    devices = InMemoryDeviceRepository()        # SQLite стане сюди в модулі про сховище
    return HubService(sensor, heater, devices, Config(threshold=20.0))

if __name__ == "__main__":
    import os
    from threading import Thread
    hub = build(os.getenv("DH_ENV", "dev"))
    Thread(target=run_loop, args=(hub,), daemon=True).start()   # двері 1 — фоновий потік
    run_cli(hub)                                                # двері 2 — головний потік
```
```ts
import { createInterface } from "node:readline";

function runLoop(hub: HubService): NodeJS.Timeout {   // двері 1: тік на таймері подієвого циклу
  return setInterval(() => hub.tick(), 30_000);       // не OS-потік — сам подієвий цикл
}

function runCli(hub: HubService): void {              // двері 2: читаємо рядки, не блокуючи цикл
  const rl = createInterface({ input: process.stdin });
  rl.on("line", (line) => {
    const [cmd, ...rest] = line.trim().split(/\s+/);
    if (cmd === "state") {
      const s = hub.state();
      console.log(`heating=${s.heating}, пристроїв=${s.devices.length}`);
    } else if (cmd === "set-threshold") {
      hub.setThreshold(Number(rest[0])); console.log(`поріг → ${rest[0]} °C`);
    } else if (cmd === "add") {
      hub.addDevice({ kind: rest[0], room: rest[1], state: "unknown" });
      console.log(`додано ${rest[0]} у ${rest[1]}`);
    } else if (cmd === "quit") rl.close();
  });
}

function build(env: string): HubService {            // ТОЧКА ЗБІРКИ — єдине місце з конкретними іменами
  const [sensor, heater]: [Sensor, Heater] = env === "prod"
    ? [new OneWireThermometer("28-0119a1b2c3d4"), new SmartPlug("http://192.168.1.50")]  // залізо
    : [new FakeSensor(), new FakeHeater()];          // підробки
  const devices = new InMemoryDeviceRepository();    // SQLite стане сюди пізніше
  return new HubService(sensor, heater, devices, { threshold: 20.0 });
}

const hub = build(process.env.DH_ENV ?? "dev");
runLoop(hub);   // цокає у фоні подієвого циклу
runCli(hub);    // а ми читаємо команди — обидві двері, один hub
```
:::

`build` — це [точка збірки (composition root)](book:programming/di-container): єдиний вузол на весь застосунок, що знає конкретні імена. У проді змінна оточення підставляє справжнє залізо, у тесті — підробки; усе інше бачить самі порти. Це той самий `build`, що ми зростили на порті пристрою, тільки підрослий: додав репозиторій і запускає **двоє** дверей замість одного циклу.

А от запуск дверей у двох мовах виглядає по-різному — і різниця не випадкова, вона про модель одночасності кожного стека. У Python читання з `stdin` **блокує** потік: доки `run_cli` висить на рядку вводу, ніщо в тому ж потоці не виконається. Тому цикл мусить дихати в **окремому потоці** — `Thread(daemon=True)`. Прапорець `daemon` означає «цей потік не тримає програму живою»: коли головний потік вийде (людина набрала `quit`), фоновий цикл згасне сам, без ручного гасіння. Обидва потоки смикають **той самий** `hub` — і в цьому вся сіль.

![Часова вісь у дві смуги: угорі синя лінія фонового daemon-потоку з тіками кожні 30 секунд (на 0, 30, 60, 90 с), унизу штрихова лінія головного потоку, що блокується на stdin; на 42-й секунді червона подія «CLI: set-threshold 25», від якої стрілка веде вгору до тіку на 60 с із підписом «наступний тік уже бачить поріг 25»](/root/course/progarch/dh-v2-hexagon/img/concurrency.svg)
*Фоновий цикл цокає щотридцять секунд, поки головний потік спить на вводі. Команда CLI прилітає між тіками, о 42-й секунді, — і наступний тік, о 60-й, уже рахує з новим порогом, бо стан у них спільний.*

У Node ж окремий потік **не потрібен** зовсім: він однопотоковий, а `setInterval` кладе тік у чергу **подієвого циклу**, і той сам вплітає його між асинхронними подіями рядків від `readline`. Жодного `Thread` — сам рушій виконання по черзі бере то тік, то команду. Обидва підходи дають те саме: дві двері живуть одночасно, ділячи один `hub`; просто Python платить за це справжнім потоком, бо його ввід-вивід блокує, а Node — ні. Це різні реалізації однієї форми, і корисно бачити, що форма від стека не залежить, а спосіб її втілити — залежить.

## Одна правда — і тест, що її доводить

Тепер найголовніше — притиснути обіцянку до стіни. Тест ганяє **той самий** `HubService` підробками й доводить обидва наші заявлені зиски. Жодного потоку в тесті ми не крутимо навмисне: замість того, щоб сподіватися на збіг у часі, ми **вручну чергуємо** виклики обох дверей — тік циклу, тоді команду CLI, тоді знову тік — і дивимося, чи справді друга двер побачила те, що записала перша.

![Центральний зелений прямокутник «HubService — одна правда» з трьома полями стану (heating, cfg.threshold, devices); згори до нього ведуть дві сині стрілки від «Двері 1 — Автономний цикл» (пише heating) і «Двері 2 — CLI» (пише cfg); знизу сіра стрілка від «Двері 3 — HTTP (завтра)», що лише читає GET /state](/root/course/progarch/dh-v2-hexagon/img/one-truth.svg)
*Двоє дверей (завтра троє) тримаються за один стан. Цикл пише heating, CLI пише cfg, майбутній HTTP лише читає — і що записала одна, наступне читання іншої вже бачить, бо hub один на всіх.*

:::tabs
```py
# test_hub.py — ганяємо сервіс підробками: без заліза, без бази, без sleep

def test_core_holds_the_band():          # ДОКАЗ 0: зведене ядро тримає смугу
    cfg = Config(threshold=20.0)
    assert decide(Reading(19.9), cfg, heating=False)          # холодно — вмикаємо
    assert decide(Reading(20.3), cfg, heating=True)           # у смузі й гріли — тримаємо
    assert not decide(Reading(20.6), cfg, heating=True)       # перескочили верх — гасимо
    assert not decide(Reading(20.3), cfg, heating=False)      # та сама 20.3, вимкнено — НЕ вмикаємо
    assert not decide(Reading(float("nan"), ok=False), cfg, heating=True)  # німий давач → спокій

def test_both_doors_share_one_truth():   # ДОКАЗ 1 і 2: одна правда + HTTP задарма
    sensor, heater = FakeSensor(celsius=21.0), FakeHeater()   # 21 °C — тепліше за поріг 20
    hub = HubService(sensor, heater, InMemoryDeviceRepository(), Config(threshold=20.0))

    hub.tick()                                    # двері 1: тік — 21 над порогом, не гріємо
    assert hub.state().heating is False
    assert heater.log == []                       # реле жодного разу не смикнулось

    hub.set_threshold(25.0)                        # двері 2: та сама мить — CLI підняв поріг
    hub.add_device(Device("lock", "спальня"))      # двері 2: CLI додав пристрій

    hub.tick()                                     # двері 1: наступний тік БАЧИТЬ нову правду
    snap = hub.state()
    assert snap.heating is True                    # 21 < 25 → цикл тепер гріє
    assert heater.log == [True]                    # і реле ввімкнулось рівно раз
    assert any(d.room == "спальня" for d in snap.devices)   # CLI-пристрій видно циклу

    def http_get_state(h: HubService) -> HomeSnapshot:   # двері 3 — HTTP, завтра
        return h.state()                                 # той самий виклик, нуль правок ядра
    assert http_get_state(hub).heating is True
```
```ts
// test_hub.ts — ганяємо сервіс підробками: без заліза, без бази, без sleep
import assert from "node:assert";

// ДОКАЗ 0: зведене ядро тримає смугу
{
  const cfg = { threshold: 20.0 };
  assert(decide({ celsius: 19.9, ok: true }, cfg, false));    // холодно — вмикаємо
  assert(decide({ celsius: 20.3, ok: true }, cfg, true));     // у смузі й гріли — тримаємо
  assert(!decide({ celsius: 20.6, ok: true }, cfg, true));    // перескочили верх — гасимо
  assert(!decide({ celsius: 20.3, ok: true }, cfg, false));   // та сама 20.3, вимкнено — НЕ вмикаємо
  assert(!decide({ celsius: NaN, ok: false }, cfg, true));    // німий давач → спокій
}

// ДОКАЗ 1 і 2: одна правда + HTTP задарма
{
  const sensor = new FakeSensor(21.0), heater = new FakeHeater();   // 21 °C > поріг 20
  const hub = new HubService(sensor, heater, new InMemoryDeviceRepository(), { threshold: 20.0 });

  hub.tick();                                    // двері 1: 21 над порогом — не гріємо
  assert.strictEqual(hub.state().heating, false);
  assert.deepStrictEqual(heater.log, []);

  hub.setThreshold(25.0);                         // двері 2: CLI підняв поріг
  hub.addDevice({ kind: "lock", room: "спальня", state: "unknown" });

  hub.tick();                                     // двері 1: наступний тік бачить нову правду
  const snap = hub.state();
  assert.strictEqual(snap.heating, true);         // 21 < 25 → цикл тепер гріє
  assert.deepStrictEqual(heater.log, [true]);     // реле ввімкнулось рівно раз
  assert(snap.devices.some((d) => d.room === "спальня"));   // CLI-пристрій видно циклу

  const httpGetState = (h: HubService): HomeSnapshot => h.state();  // двері 3 — HTTP
  assert.strictEqual(httpGetState(hub).heating, true);             // нуль правок ядра
}
```
:::

Розберімо, що саме доводить кожен рядок, бо тут — уся розписка за форму.

**Доказ 0** тицяє зведене ядро в чотири межі смуги плюс німий давач — і зеленим стверджує, що збірка не зіпсувала правила: 19.9 вмикає, 20.3 у стані «гріємо» тримає, 20.6 гасить, та сама 20.3 у стані «не гріємо» лишає вимкненим, а `ok=false` дає спокій. Це буквально ті самі перевірки, [що проходило правило на кроці про порт](root:progarch/hexagon-when-overkill/proj-dh-device-port.md), — тільки тепер із третім аргументом. Ядро зійшлося.

**Доказ 1** — серце. Перший тік: 21 °C над порогом 20, не гріли — `decide` каже «ні», реле мовчить, `heater.log` порожній. Тоді **інша двер** (CLI) піднімає поріг до 25 і додає пристрій у спальню. Наступний тік циклу — і `heating` уже `True`, бо 21 < 25. Зверніть увагу, **звідки** взялося 25: цикл ніде не питав CLI, він просто прочитав `self._cfg`, а там уже стоїть те, що записала команда, — бо `_cfg` **один** на обидві двері. Так само `add_device` від CLI видно в `snap.devices`, який зібрав тік циклу. Дві двері, один стан: що записала одна, наступне читання іншої бачить. Обіцянка модуля тепер не слово, а зелений рядок.

**Доказ 2** ховається в останніх трьох рядках і коштує уваги, хоч виглядає дрібницею. `http_get_state` — це **макет третьої двері**: тонка функція, що на запит просто кличе `hub.state()`, точнісінько як завтра зробить HTTP-обробник на `GET /state`. Вона стала збоку — і **жоден** рядок ядра, застосунку чи портів не змінився, щоб її прийняти. Оце й є доказ, що форма тримає напоготові: новий вхід — це новий тонкий дзвонар на спільний сервіс, а не операція на серці системи.

> 🔧 **Навіщо це.** Уся цінність v2 вміщується в те, що **цей тест зелений і не тягне нічого**. Проти зліпленого дому його не можна було б навіть почати: не було б `HubService`, який обидві двері гукають, тож «спільну правду» не було б де перевірити; не було б портів, тож замість `FakeSensor` довелося б гріти кімнату; не було б знімка `state()`, тож третю двер не підчепиш без хірургії. Форма не зробила код гарнішим на діаграмі — вона зробила **можливими** два докази, яких без неї не існувало. За це — і лише за це — платять непрямотою трьох портів і одного сервісного шару.

## Складність і пастки

**Спільний стан двох потоків просить замка.** Тест зелений саме тому, що ми чергували двері **вручну**, в одному потоці. У проді ж `run_loop` крутиться у своєму потоці, а `run_cli` — у головному, і обидва пишуть у `hub` одночасно. У CPython глобальний замок (GIL) робить окремі операції майже атомарними, тож катастрофи не буде, але гарантій порядку немає: тік може прочитати `_cfg` за мить до того, як CLI його підмінить, і один-єдиний такт відпрацює за старим порогом (наступний уже виправиться — правило самокоригувальне). Це терпимо для опалення, але не для грошей. Чесна відповідь у справжньому домі — **замок** навколо доступу до стану **або**, ще чистіше, зробити цикл єдиним власником стану, а CLI хай **кладе команди в чергу**, яку цикл вибирає між тіками. Тоді пишучий потік один, і гонки нема зовсім. Ми лишили це поза кістяком свідомо: одночасність — окремий тікет, і платити за неї варто тоді, коли межа справді проступить, а не «про всяк випадок».

**`ok=false → False` гасить на одному кліпанні.** Постанова «німий давач → спокій» безпечна, але має зуб: якщо давач кліпнув **однократно** посеред гріння, цей такт віддасть `False`, реле згасне, а наступний свіжий вимір знову ввімкне — те саме клацання, від якого ми боронилися гістерезисом, тільки збоку. Для рідкісного збою це дрібниця; для давача, що кліпає щотретій раз, — ні. Ліки вже намацані [на кроці про порт — вартовий свіжості за тим самим портом `Sensor`](root:progarch/hexagon-when-overkill/proj-dh-device-port.md): обгортка, що тримає останній добрий стан крізь кілька поганих читань, перш ніж визнати давач мертвим. Важливо, що вкласти її **є куди** — у порт, не чіпаючи `decide`; але поки жоден давач не кліпає в полі, це передчасна складність.

**`decide` звузилося з команди до булі — і колись розшириться назад.** [У v1 `decide` повертало `Command`](root:progarch/dh-v1-modules) — `HEAT`/`IDLE`, а потім і `ALERT`. Тут воно повертає голе `bool`, бо гістерезис зробив рішення двостанним: гріємо чи ні, залежно від попереднього стану. Це не втрата — це відповідність поточній потребі: третього виходу v2 не має. Але щойно повернеться вимога **сповіщати замість гріти** («у спальні не вмикай, а напиши мені»), буля стане тісною, і `Command` повернеться — не як реванш абстракції, а тому, що з'явиться третє «тому». Знати, коли форму **звузити**, так само важливо, як коли розширити.

**Підробки чемніші за залізо.** `FakeSensor` ніколи не зволікає, `FakeHeater` вмикається вмить, `InMemoryDeviceRepository` не губить рядків. Справжній дім грубіший: розетка через Wi-Fi відпаде на пів хвилини, давач застигне на правдоподібному числі, кімната має теплову масу й проскакує поріг за інерцією. Зелений тест на підробках — необхідна, але не достатня умова; він доводить **логіку**, не витривалість. Окремо чигає тихий дрейф: `InMemoryDeviceRepository` — фейк, і ніщо не змушує його поводитися як майбутній `SqliteDeviceRepository`; день у день вони розійдуться, і зелений тест почне брехати. Прив'язь від цього одна — [ганяти обидві реалізації спільним контрактним набором](root:progarch/test-doubles-when/proj-verified-fake.md), щоб підробка не старіла нишком.

**Дім і досі в одному процесі — і це чеснота, не борг.** Двоє дверей, три порти, сервіс — усе це шви **в пам'яті**, а не межі мережі. Ми [не розподілили `HubService`](root:progarch/distributed-objects-trap) на мікросервіси й не пустили `Device` по дроту. Коли прийде хмара, лінія дім↔хмара стане **ще одним адаптером**, що перетинає її грубо — тим самим знімком `HomeSnapshot`, — а не балакучим об'єктом, до якого клієнт тягнеться по полю. І `sleep(30)` у циклі, що блокує потік, — це той-таки [super-loop, чиї межі проступлять, коли роботи стане більше, ніж один цикл встигає вчасно](root:embedded/super-loop-limits); ми не чіпали його, бо жодна вимога паралельності ще не тицьнула. v2 виправив рівно те, на що вказали реальні болі, заповнив кожну виточену комірку справжнім кодом — і зупинився. Оце й є форма на дотик: не діаграма, а те, що кожна майбутня зміна вже знає, у яке кільце їй лягати, і тест, який зеленим це стверджує.
