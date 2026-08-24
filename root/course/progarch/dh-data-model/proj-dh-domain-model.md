# ⚙️ Повна робоча доменна модель DH

У статті ми розкладали дім на зерна: показали `LockState` окремо, `Lock` окремо, `Home` окремо, а сценарій «нікого немає» лише описали словами. Кожне зерно на своєму місці правдиве, але зерна — це ще не рослина. Тут ми зводимо їх в **одну робочу модель** і, головне, **проганяємо** її: будуємо дім із десятьма дверима, кажемо «йдемо», один замок лишаємо офлайн — і дивимося на власні очі, як процес доганяє бажане до справжнього і чесно звітує «дев'ять замкнено, гараж офлайн».

Домовимося, що означає «робоча». Не «компілюється» — компілюється й купа мертвого коду. Робоча — це коли на сценарії з **реальним офлайн-замком** модель не бреше: не вдає, що все замкнено, не падає з відчаю, а лишає чесний розрив і **зводить його на наступному проході**. Саме цей прогін і є доказ, що межі агрегатів проведені там, де треба.

## Ідея цілого

Форма коду вкладається в один подих. **Значення** — незмінні, замкнені, стережуть себе самі: ідентифікатори, стан замка, режим дому, вимір. Дві **сутності-корені малих агрегатів** — `Lock` і `Home`, кожна зі своїми інваріантами, які нема як порушити ззовні. Зв'язок між агрегатами — **тільки за id**, жодна межа не тримає в руках нутрощі іншої. І окремо від них — **цикл зведення** (reconciler): не транзакція, а процес, що читає бажаний режим дому, розсилає замкам команду й доганяє справжній стан до бажаного, повторюючи для тих, хто не відповів.

Далі — чотири блоки коду в тому самому порядку: значення, сутності, порт зі зведенням, прогін. Кожен наступний спирається на попередній, як і має бути в живій моделі.

## Значення: незмінні й замкнені

Почнімо з найтвердішого шару — з того, що не має тотожності й повністю визначене власним вмістом. Ідентифікатори, стан, режим, вимір, поріг, локація. Усі вони [незмінні](book:programming/immutability) — раз створене значення ніхто по дорозі не перепише, тож зникає цілий клас багів «хтось потай підмінив». `LockState` і `HomeMode` — **замкнені переліки**: стану поза списком просто нема як записати, і `Unknown` тут не діра, а чесно поіменований стан «хаб іще не чув від замка».

:::tabs
```ts
// ── 1. Об'єкти-значення: незмінні, рівність за вмістом, стережуть себе ──
class DomainError extends Error {}

class DeviceId {
  constructor(readonly value: string) {
    if (!value) throw new DomainError("порожній DeviceId — ідентифікатор мусить бути");
  }
  equals(o: DeviceId): boolean { return this.value === o.value; }
  toString(): string { return this.value; }
}
class HomeId { constructor(readonly value: string) {} toString() { return this.value; } }
class RoomId { constructor(readonly value: string) {} toString() { return this.value; } }
class UserId { constructor(readonly value: string) {} toString() { return this.value; } }

// Замкнені переліки — інших значень не буває. Unknown/невизначеність — чесний стан, не null.
type LockState = "Locked" | "Unlocked" | "Jammed" | "Unknown";
type HomeMode  = "Home" | "Away" | "Night";

class Threshold { constructor(readonly celsius: number) {} }

// Вимір — значення: незмінний, два однакові взаємозамінні.
class Reading {
  constructor(readonly celsius: number, readonly at: Date) {}
  hotterThan(t: Threshold): boolean { return this.celsius > t.celsius; }
}

// Локація — де саме стоїть пристрій (кімната + місце); теж значення.
class Location {
  constructor(readonly roomId: RoomId, readonly spot: string) {}
}
```
```py
# ── 1. Об'єкти-значення: незмінні, рівність за вмістом, стережуть себе ──
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DomainError(Exception):
    pass


@dataclass(frozen=True)                 # frozen → незмінний + рівність за вмістом задарма
class DeviceId:
    value: str
    def __post_init__(self):
        if not self.value:
            raise DomainError("порожній DeviceId — ідентифікатор мусить бути")
    def __str__(self): return self.value

@dataclass(frozen=True)
class HomeId:
    value: str

@dataclass(frozen=True)
class RoomId:
    value: str

@dataclass(frozen=True)
class UserId:
    value: str

class LockState(Enum):                  # замкнений перелік: інших станів не буває
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    JAMMED = "jammed"
    UNKNOWN = "unknown"                 # чесний «не чули від замка», не None і не діра

class HomeMode(Enum):
    HOME = "home"
    AWAY = "away"
    NIGHT = "night"

@dataclass(frozen=True)
class Threshold:
    celsius: float

@dataclass(frozen=True)
class Reading:                          # незмінний вимір — два однакові взаємозамінні
    celsius: float
    at: datetime
    def hotter_than(self, t: Threshold) -> bool:
        return self.celsius > t.celsius

@dataclass(frozen=True)
class Location:
    room_id: RoomId
    spot: str
```
:::

Помітьте, що `DeviceId` уже стереже одне правило: порожнього ідентифікатора не буває — конструктор не дасть його народити. Це та сама думка, що й з інваріантами замка, лише в найдрібнішому масштабі: **некоректне значення не має як існувати**. І ще одне, майже непомітне: `equals` порівнює `DeviceId` за вмістом, бо для значення інакше й безглуздо — «схожість» тут ні до чого, два однакові рядки-id — це один і той самий id.

## Сутності: корені, що стережуть себе

Тепер зі значень збираємо дві сутності з поведінкою. Кожна — корінь **свого** агрегата, тобто зони, всередині якої все узгоджено завжди. `Lock` тримає два інваріанти: **не буває нічий** (власника вимагає конструктор — замок без дому не народиться) і **завжди має визначений стан** (про це вже подбав замкнений тип). `Home` тримає лише **своє** спільне — режим, кімнати, членів родини — і посилається на пристрої **тільки за id**, а не живими об'єктами.

Тут з'являється тонка, але вагома пара методів, яку варто розрізняти чітко. `lock()`/`unlock()` — це **локальний намір**: власник тисне кнопку в застосунку, і цифровий двійник замка оптимістично стає `Locked`, але заклинений замок командою не рушиш (інваріант ловить це). А `reportFromDevice()` — це **правда з поля**: фізичний замок доповів свій справжній стан, і ми приймаємо його як є, навіть якщо це `Jammed`. Плутати їх — значить плутати «я хочу» з «так воно є», а на цій різниці стоїть увесь наступний прогін.

:::tabs
```ts
// ── 2. Сутності-корені малих агрегатів ──
class Lock {                                   // СУТНІСТЬ + корінь свого агрегата
  private state: LockState = "Unknown";        // завжди визначений (інваріант 2)

  constructor(
    readonly id: DeviceId,
    readonly homeId: HomeId,                    // ← власника вимагає конструктор:
    readonly location: Location,                //    інваріант 1 «не буває нічий»
  ) {}

  // Локальний НАМІР (кнопка в застосунку). Заклинений — командою не чіпаємо.
  lock(): void {
    if (this.state === "Jammed")
      throw new DomainError(`замок ${this.id} заклинило — командою не замкнути, спершу ремонт`);
    this.state = "Locked";
  }
  unlock(): void {
    if (this.state === "Jammed")
      throw new DomainError(`замок ${this.id} заклинило — командою не відчинити`);
    this.state = "Unlocked";
  }

  // ПРАВДА з поля: фізика доповіла — приймаємо як є (навіть Jammed).
  reportFromDevice(s: LockState): void { this.state = s; }

  isLocked(): boolean { return this.state === "Locked"; }
  get current(): LockState { return this.state; }
}

class Home {                                   // окремий МАЛИЙ агрегат
  private mode: HomeMode = "Home";
  private readonly roomIds: RoomId[] = [];
  private readonly memberIds: UserId[] = [];
  private readonly lockIds: DeviceId[] = [];   // ← лише id, НЕ живі об'єкти замків

  constructor(readonly id: HomeId, readonly ownerId: UserId) {}  // дім не буває без власника

  setMode(m: HomeMode): void { this.mode = m; } // міняє СВІЙ стан — і тільки
  get currentMode(): HomeMode { return this.mode; }

  addRoom(r: RoomId): void { this.roomIds.push(r); }
  admit(u: UserId): void { this.memberIds.push(u); }
  attachLock(d: DeviceId): void { this.lockIds.push(d); }
  get locks(): readonly DeviceId[] { return this.lockIds; }
}
```
```py
# ── 2. Сутності-корені малих агрегатів ──
class Lock:                                     # СУТНІСТЬ + корінь свого агрегата
    def __init__(self, id: DeviceId, home_id: HomeId, location: Location):
        self.id = id
        self.home_id = home_id                  # ← власника вимагає конструктор:
        self.location = location                #    інваріант 1 «не буває нічий»
        self._state = LockState.UNKNOWN         # завжди визначений (інваріант 2)

    # Локальний НАМІР (кнопка в застосунку). Заклинений — командою не чіпаємо.
    def lock(self) -> None:
        if self._state is LockState.JAMMED:
            raise DomainError(f"замок {self.id} заклинило — командою не замкнути, спершу ремонт")
        self._state = LockState.LOCKED

    def unlock(self) -> None:
        if self._state is LockState.JAMMED:
            raise DomainError(f"замок {self.id} заклинило — командою не відчинити")
        self._state = LockState.UNLOCKED

    # ПРАВДА з поля: фізика доповіла — приймаємо як є (навіть Jammed).
    def report_from_device(self, s: LockState) -> None:
        self._state = s

    def is_locked(self) -> bool:
        return self._state is LockState.LOCKED

    @property
    def current(self) -> LockState:
        return self._state


class Home:                                     # окремий МАЛИЙ агрегат
    def __init__(self, id: HomeId, owner_id: UserId):
        self.id = id
        self.owner_id = owner_id                # дім не буває без власника
        self._mode = HomeMode.HOME
        self._room_ids: list[RoomId] = []
        self._member_ids: list[UserId] = []
        self._lock_ids: list[DeviceId] = []     # ← лише id, НЕ живі об'єкти замків

    def set_mode(self, m: HomeMode) -> None:
        self._mode = m                          # міняє СВІЙ стан — і тільки

    @property
    def mode(self) -> HomeMode:
        return self._mode

    def add_room(self, r: RoomId) -> None: self._room_ids.append(r)
    def admit(self, u: UserId) -> None: self._member_ids.append(u)
    def attach_lock(self, d: DeviceId) -> None: self._lock_ids.append(d)

    @property
    def locks(self) -> list[DeviceId]:
        return list(self._lock_ids)
```
:::

Дивіться, чого стало неможливо. Замок без дому й локації не сконструюється — конструктор їх вимагає. Стан у порожнечі не поставиш — поле закрите, єдиний шлях усередину названий і лишає замок у визначеному стані. А `Home` **не тримає замки в руках** — лише їхні id, тож підняти дім з бази й не тягнути за собою всі пристрої тепер можливо в принципі. Це і є [багата модель проти мішка полів](root:progarch/invariants-and-validation): правила живуть **усередині** тих речей, яких стосуються, а не розсипані перевірками по викликах.

## Порт у фізичний світ і цикл зведення

Ось де DH показує суть, якої немає в банківській задачі. Замок — не рядок у базі, а **залізяка на дверях** за кілометри від сервера. Домен не має знати, чи це Wi-Fi, чи Zigbee, чи макет у тесті — тож між ним і залізом кладемо один **порт** `DeviceGateway`. Через нього йде команда «замкнись», і назад приходить одна з небагатьох чесних відповідей: замок відповів (і ось його справжній стан) — або він **офлайн**, і правди ми не знаємо.

А `AwayReconciler` — це і є [узгодженість із часом](book:programming/aggregates-consistency) у коді. Він не транзакція. Він **прохід циклу**: читає бажаний режим дому, для кожного замка шле команду в залізо, приймає правду з поля через `reportFromDevice` і складає **чесний звіт** — скільки замкнено, хто офлайн, хто заклинив. Кожен замок оновлюється **окремо** (у справжній системі — своя транзакція на свій агрегат), а `Home` не чіпається взагалі: його режим уже виставлено раніше, теж окремою транзакцією.

> 🔧 **Навіщо це.** Такий самий цикл зведення — серце промислових систем: контролери Kubernetes нескінченно порівнюють **бажаний** стан кластера зі **справжнім** і підганяють другий до першого, збігаючись за багато проходів, а не однією операцією (це задокументована архітектура їхнього рівневого reconcile-циклу). DH робить те саме з дверима. Спільна причина одна: коли по той бік команди — фізичний світ, що падає, глючить і відповідає із запізненням, єдина чесна модель — не «зроби атомарно», а «оголоси бажане й терпляче доганяй».

:::tabs
```ts
// ── 3. Порт у фізичний світ + зведення бажаного до справжнього ──

// Що може відповісти фізичний замок на команду «замкнись».
type LockOutcome =
  | { kind: "acked"; state: LockState }   // відповів — і ось його справжній стан
  | { kind: "offline" };                  // не на зв'язку — правди не знаємо

// Порт: єдиний місток до заліза. Домен не знає, що там за протокол.
interface DeviceGateway {
  sendLock(id: DeviceId): LockOutcome;
}

// Чесний звіт про ОДИН прохід — об'єкт-значення (лише знімок, нічого не міняє).
class ReconcileReport {
  constructor(
    readonly desired: HomeMode,
    readonly locked: DeviceId[],
    readonly offline: DeviceId[],         // не підтвердили замкнення цього проходу
    readonly jammed: DeviceId[],          // потрібна людина
  ) {}
  get settled(): boolean { return this.offline.length === 0 && this.jammed.length === 0; }
  toString(): string {
    const off = this.offline.map(String).join(", ") || "—";
    const jam = this.jammed.length ? ` · заклинило: ${this.jammed.map(String).join(", ")}` : "";
    return `[${this.desired}] ${this.locked.length} замкнено · офлайн: ${off}${jam}`;
  }
}

// Зводить БАЖАНЕ (режим дому) до СПРАВЖНЬОГО (стан кожного замка).
// Це НЕ транзакція — це один прохід циклу, що доганяє.
class AwayReconciler {
  constructor(private readonly gateway: DeviceGateway) {}

  sweep(home: Home, locks: Map<string, Lock>): ReconcileReport {
    const wantsLocked = home.currentMode === "Away" || home.currentMode === "Night";
    const locked: DeviceId[] = [], offline: DeviceId[] = [], jammed: DeviceId[] = [];
    if (!wantsLocked) return new ReconcileReport(home.currentMode, locked, offline, jammed);

    for (const id of home.locks) {
      const lock = locks.get(id.value);
      if (!lock) continue;
      const out = this.gateway.sendLock(id);       // команда пішла в залізо
      if (out.kind === "offline") {
        offline.push(id);                          // лишаємо останнє відоме, повторимо
        continue;
      }
      lock.reportFromDevice(out.state);            // правда з поля
      if (out.state === "Locked") locked.push(id);
      else if (out.state === "Jammed") jammed.push(id);
      else offline.push(id);                       // відповів, але не замкнувся — у чергу на повтор
    }
    return new ReconcileReport(home.currentMode, locked, offline, jammed);
  }
}
```
```py
# ── 3. Порт у фізичний світ + зведення бажаного до справжнього ──
from dataclasses import field
from typing import Protocol


@dataclass(frozen=True)
class Acked:                            # замок відповів — і ось його справжній стан
    state: LockState

@dataclass(frozen=True)
class Offline:                          # не на зв'язку — правди не знаємо
    pass

LockOutcome = Acked | Offline           # розмічене об'єднання (3.10+)


class DeviceGateway(Protocol):          # порт: єдиний місток до заліза
    def send_lock(self, id: DeviceId) -> LockOutcome: ...


@dataclass(frozen=True)
class ReconcileReport:                  # чесний знімок ОДНОГО проходу — значення
    desired: HomeMode
    locked: list[DeviceId]
    offline: list[DeviceId]             # не підтвердили замкнення цього проходу
    jammed: list[DeviceId]              # потрібна людина

    @property
    def settled(self) -> bool:
        return not self.offline and not self.jammed

    def __str__(self) -> str:
        off = ", ".join(map(str, self.offline)) or "—"
        jam = f" · заклинило: {', '.join(map(str, self.jammed))}" if self.jammed else ""
        return f"[{self.desired.value}] {len(self.locked)} замкнено · офлайн: {off}{jam}"


class AwayReconciler:
    def __init__(self, gateway: DeviceGateway):
        self._gateway = gateway

    # Зводить БАЖАНЕ (режим дому) до СПРАВЖНЬОГО (стан кожного замка).
    # Це НЕ транзакція — це один прохід циклу, що доганяє.
    def sweep(self, home: Home, locks: dict[str, Lock]) -> ReconcileReport:
        locked: list[DeviceId] = []
        offline: list[DeviceId] = []
        jammed: list[DeviceId] = []
        if home.mode not in (HomeMode.AWAY, HomeMode.NIGHT):
            return ReconcileReport(home.mode, locked, offline, jammed)

        for id in home.locks:
            lock = locks.get(id.value)
            if lock is None:
                continue
            match self._gateway.send_lock(id):          # команда пішла в залізо
                case Offline():
                    offline.append(id)                  # лишаємо останнє відоме, повторимо
                case Acked(state=LockState.LOCKED):
                    lock.report_from_device(LockState.LOCKED)
                    locked.append(id)
                case Acked(state=LockState.JAMMED):
                    lock.report_from_device(LockState.JAMMED)
                    jammed.append(id)
                case Acked(state=other):
                    lock.report_from_device(other)      # відповів, але не замкнувся
                    offline.append(id)                  # у чергу на повтор
        return ReconcileReport(home.mode, locked, offline, jammed)
```
:::

Три речі варто прочитати в цьому коді уважно. По-перше, `ReconcileReport` — сам **об'єкт-значення**: він нічого не міняє, це знімок одного проходу, і два однакові звіти — те саме. По-друге, один поганий замок **не зриває весь прохід**: заклинений потрапляє у свій кошик і цикл іде далі — часткове чесне просування краще за «все або нічого». По-третє, `settled` — це і є та мить, коли бажане нарешті збіглося зі справжнім: жодного офлайн, жодного заклиненого, усі двері замкнені насправді.

## Прогін: «нікого немає» з офлайн-гаражем

І ось кульмінація — заради неї ми все й будували. Дім із десятьма дверима, власник тисне «йдемо», гараж саме зараз офлайн (сів акумулятор). Дивимося на два проходи.

:::tabs
```ts
// ── 4. Прогін: «нікого немає» з одним офлайн-замком ──

// Макет заліза: знає, хто на зв'язку. Online — замкнеться; offline — мовчить.
// (У житті тут Wi-Fi, черга команд, таймаути, повторні спроби.)
class FakeGateway implements DeviceGateway {
  constructor(private online: Set<string>) {}
  bringOnline(id: string): void { this.online.add(id); }
  sendLock(id: DeviceId): LockOutcome {
    if (!this.online.has(id.value)) return { kind: "offline" };
    return { kind: "acked", state: "Locked" };
  }
}

// Будуємо дім із десятьма дверима.
const homeId = new HomeId("h-1");
const home = new Home(homeId, new UserId("u-owner"));
const hall = new RoomId("hall");
home.addRoom(hall);

const doorNames = ["front","back","garage","balcony","cellar","gate","patio","side","roof","shed"];
const locks = new Map<string, Lock>();
for (const name of doorNames) {
  const id = new DeviceId(name);
  home.attachLock(id);
  locks.set(name, new Lock(id, homeId, new Location(hall, name)));
}

// Гараж — офлайн. Решта дев'ять — на зв'язку.
const gateway = new FakeGateway(new Set(doorNames.filter(n => n !== "garage")));
const reconciler = new AwayReconciler(gateway);

// Власник тисне «йдемо»: дім ставить БАЖАНИЙ режим — і тільки. Це одна транзакція.
home.setMode("Away");

// Прохід 1: дев'ять замкнулися, гараж мовчить.
const r1 = reconciler.sweep(home, locks);
console.log("прохід 1:", r1.toString(), "· зведено:", r1.settled);
console.log("гараж зараз:", locks.get("garage")!.current);

// ...згодом гараж повертається на зв'язок. Повторюємо — доганяємо решту.
gateway.bringOnline("garage");
const r2 = reconciler.sweep(home, locks);
console.log("прохід 2:", r2.toString(), "· зведено:", r2.settled);
console.log("гараж зараз:", locks.get("garage")!.current);
```
```py
# ── 4. Прогін: «нікого немає» з одним офлайн-замком ──

class FakeGateway:                      # макет заліза: знає, хто на зв'язку
    def __init__(self, online: set[str]):
        self._online = online
    def bring_online(self, id: str) -> None:
        self._online.add(id)
    def send_lock(self, id: DeviceId) -> LockOutcome:
        if id.value not in self._online:
            return Offline()            # у житті тут таймаут Wi-Fi, черга команд
        return Acked(LockState.LOCKED)


home_id = HomeId("h-1")
home = Home(home_id, UserId("u-owner"))
hall = RoomId("hall")
home.add_room(hall)

door_names = ["front","back","garage","balcony","cellar","gate","patio","side","roof","shed"]
locks: dict[str, Lock] = {}
for name in door_names:
    dev = DeviceId(name)
    home.attach_lock(dev)
    locks[name] = Lock(dev, home_id, Location(hall, name))

# Гараж — офлайн. Решта дев'ять — на зв'язку.
gateway = FakeGateway({n for n in door_names if n != "garage"})
reconciler = AwayReconciler(gateway)

# Власник тисне «йдемо»: дім ставить БАЖАНИЙ режим — і тільки. Це одна транзакція.
home.set_mode(HomeMode.AWAY)

# Прохід 1: дев'ять замкнулися, гараж мовчить.
r1 = reconciler.sweep(home, locks)
print("прохід 1:", r1, "· зведено:", r1.settled)
print("гараж зараз:", locks["garage"].current.value)

# ...згодом гараж повертається на зв'язок. Повторюємо — доганяємо решту.
gateway.bring_online("garage")
r2 = reconciler.sweep(home, locks)
print("прохід 2:", r2, "· зведено:", r2.settled)
print("гараж зараз:", locks["garage"].current.value)
```
:::

Що це друкує (Python; TS — те саме з великими назвами станів):

```
прохід 1: [away] 9 замкнено · офлайн: garage · зведено: False
гараж зараз: unknown
прохід 2: [away] 10 замкнено · офлайн: — · зведено: True
гараж зараз: locked
```

Прочитаймо цей вивід повільно, бо в ньому вся суть кроку. Після першого проходу дім **бажає** `Away`, дев'ять замків **насправді** `Locked`, а гараж лишається `Unknown` — не `Locked` (це була б брехня) і не `Unlocked` (це теж припущення), а чесне «не чули». Розрив між «хочу» і «є» видно як на долоні: `зведено: False`. Ніяка транзакція його не сховала — бо офлайн-замок фізично не можна замкнути атомарно з рештою. Аж коли гараж повернувся, **той самий цикл** без жодної нової логіки догнав останні двері, і аж тоді `settled` став `True`. Дім не «замкнувся однією командою» — він **збігся за два проходи**, і кожен проміжний стан чесний.

![Цикл зведення: дім оголошує бажаний режим, хаб шле кожному замку команду, приймає правду з поля, складає звіт і повторює для офлайн. Нижче два проходи в часі: спершу дев'ять із десяти замкнено й гараж офлайн, після повернення гаража — усі десять; розрив тане проходами, а не зникає транзакцією](img/reconcile-loop.svg)
*Бажане й справжнє — різні речі, які зводить не одна операція, а цикл, що доганяє. Перший прохід лишає чесний розрив (гараж офлайн), другий — закриває його. Кожен замок оновлюється окремо, кожна зміна локальна.*

Тут-таки видно, чому цикл безпечно **повторювати**. Команда «замкнись» **ідемпотентна**: замкнути вже замкнений замок — нічого не станеться, стан лишиться `Locked`. Тож повтор для тих, хто минулого разу мовчав, не ламає тих, хто вже замкнувся, а запізніла відповідь від колись-офлайн замка нічого не псує. Це класична пара «доставка щонайменше раз + ідемпотентна операція»: не намагаємося зробити рівно один ідеальний виклик, а робимо стільки проходів, скільки треба, знаючи, що зайвий не шкодить.

## Складність і пастки

Робочий код показує, як **треба**; щоб оцінити рішення, гляньмо на три способи зробити **не так** — усі троє компілюються й усі троє дорого коштують.

**Пастка 1: гігантський `Home`, що тримає живі замки.** Найспокусливіша межа — зробити дім одним великим агрегатом:

:::tabs
```ts
// ✗ АНТИ-МОДЕЛЬ: Home ковтає живі замки й замикає все «однією транзакцією»
class FatHome {
  private locks: Lock[] = [];          // ← живі об'єкти, а не id
  lockAll(): void {                    // виглядає атомарно — але це брехня
    for (const l of this.locks) l.lock();
  }
}
```
```py
# ✗ АНТИ-МОДЕЛЬ: Home ковтає живі замки й замикає все «однією транзакцією»
class FatHome:
    def __init__(self):
        self.locks: list[Lock] = []    # ← живі об'єкти, а не id
    def lock_all(self) -> None:        # виглядає атомарно — але це брехня
        for l in self.locks:
            l.lock()
```
:::

Три біди зразу. Щоб замкнути **один** замок, доводиться підняти з бази **весь** дім — усі кімнати, усі пристрої. Двоє в родині одночасно (одне замикає гараж, друге гасить світло) б'ються за **той самий** об'єкт `FatHome`, і одна зміна перезаписує іншу. А головне — `lockAll()` лише **вдає** атомарність: `l.lock()` міняє цифровий двійник у пам'яті, але фізичні двері за кілометри від сервера так не замикаються, і офлайн-замок цей цикл просто прогавить, повіривши, що «все гаразд». Правильна межа — кожен замок сам собі корінь, а `Home` тримає лише id — рятує від усіх трьох одразу.

**Пастка 2: стан замка як сутність.** Друга спокуса — дати станові власний рядок у таблиці:

:::tabs
```ts
// ✗ АНТИ-МОДЕЛЬ: стан як сутність з id — і рівність ламається
class LockStateEntity {
  constructor(readonly id: string, readonly value: string) {}
}
// два «замкнено» тепер РІЗНІ, бо в них різні id:
new LockStateEntity("s-1", "Locked") === new LockStateEntity("s-2", "Locked"); // false
// код тоне в питанні, якого не мало б бути: «а це та сама замкненість?»
```
```py
# ✗ АНТИ-МОДЕЛЬ: стан як сутність з id — і рівність ламається
@dataclass
class LockStateEntity:
    id: str
    value: str
# два «замкнено» тепер РІЗНІ, бо в них різні id:
LockStateEntity("s-1", "Locked") == LockStateEntity("s-2", "Locked")  # False
# код тоне в питанні, якого не мало б бути: «а це та сама замкненість?»
```
:::

«Замкнено» — це «замкнено»; за ним нема чого стежити крізь час і нема примірників, які треба розрізняти. Давши йому тотожність, ми породжуємо безглузде питання «чи це той самий стан?» і ламаємо просте порівняння. Замкнений перелік-значення `LockState` прибирає це конструктивно — саме тому в робочій моделі стан **значення**, а не сутність. Це прямий наслідок [типів, що не дають записати неможливе](book:programming/type-driven-design): менше представлень некоректного — менше багів, які нема де сховати.

**Пастка 3: вимагати миттєвої узгодженості дому й замків.** Найпідступніша, бо здається «правильною». Якщо наполягати, що «нікого немає ⇒ усі замкнені» — інваріант **однієї миті**, то команда «йдемо» мусить **упасти**, щойно бодай один замок офлайн:

:::tabs
```ts
// ✗ АНТИ-МОДЕЛЬ: «усі або ніхто» — і власник лишає дім відчиненим
function goAwayStrict(home: Home, locks: Map<string, Lock>, gw: DeviceGateway): void {
  for (const id of home.locks) {
    const out = gw.sendLock(id);
    if (out.kind !== "acked" || out.state !== "Locked")
      throw new DomainError("не всі замки замкнулися — режим «нікого немає» скасовано");
  }                                    // ← гараж офлайн → виняток → дім НЕ замкнено ВЗАГАЛІ
}
```
```py
# ✗ АНТИ-МОДЕЛЬ: «усі або ніхто» — і власник лишає дім відчиненим
def go_away_strict(home: Home, locks: dict[str, Lock], gw: DeviceGateway) -> None:
    for id in home.locks:
        out = gw.send_lock(id)
        match out:
            case Acked(state=LockState.LOCKED):
                pass
            case _:
                raise DomainError("не всі замки замкнулися — режим «нікого немає» скасовано")
    # ← гараж офлайн → виняток → дім НЕ замкнено ВЗАГАЛІ
```
:::

Наслідок абсурдний: через один офлайн-гараж система відмовляється замкнути **дев'ять справних дверей** і лишає дім навстіж, бо не змогла пообіцяти неможливе. Реальний дім так не працює — і саме тому `AwayReconciler` **не** такий. Він приймає бажане, робить усе, що може **зараз**, чесно каже, чого не зміг, і доганяє решту згодом. Різниця між цим і суворим «усі або ніхто» — не стильова: вона вирішує, чи витримає платформа перший же розряджений акумулятор.

## Що тепер у руках

Зерна зі статті склалися в модель, яку можна **запустити** й побачити її чесність на очі. У ній `Home`, `Room`, `Lock`, `LockState`, `HomeMode` — ті самі слова, якими про дім говорять власники, тож монтажник вичитав би `home.setMode("Away")` і кивнув. Значення незмінні й стережуть себе, сутності багаті й самозахисні, зв'язок між агрегатами — тонкі стрілки за id, а розрив між «хочу, щоб усі були замкнені» і «гараж іще офлайн» модель не ховає під фальшивою транзакцією, а чесно доганяє циклом. Три анти-моделі поряд показують ціну кожної хибної межі — і чому проведені саме так варті того, щоб на них спиратися далі.
