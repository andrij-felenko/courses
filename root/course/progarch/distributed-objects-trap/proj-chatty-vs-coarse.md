# ⚙️ Балакучий проти грубого: порахувати переходи й зібрати знімок з обох боків

Стаття лишила обіцянку — повний робочий розбір, де переходи через межу не рахуєш на пальцях, а **виміряєш**, і де знімок збирається з одного боку та відновлюється з іншого. Виконаймо її. І то так, щоб наприкінці дисципліна «дрібно всередині, грубо на межі» лишилась не гаслом, а кодом, який можна запустити й полічити.

Найпідступніше в цій пастці — те, що перехід через межу **невидимий у коді**: `d.room()` виглядає точнісінько як локальний виклик. Тому першим ділом ми зробимо межу видимою, буквально — навісимо на неї лічильник. Коли кожен перехід стане на облік, «балакучий проти грубого» перестане бути суперечкою смаків і обернеться двома числами, які не брешуть.

## Задача

Випишемо сцену точно. У домі стоїть **хаб** — окремий процес, що тримає реєстр із 30 пристроїв. Кожен пристрій — повноцінний об'єкт `Device` з поведінкою: п'ять полів (`type`, `room`, `state`, `brightness`, `lastSeen`) віддаються геттерами. У **хмарі** крутиться дашборд — інший процес на іншій машині, часто по інший бік океану, — і йому треба намалювати всі 30 пристроїв, по п'ять полів на кожен.

Між хабом і хмарою лежить справжня межа: не та, яку хтось «спроєктував», а та, яку поставив сам світ. Кожен перехід через неї коштує однаково, байдуже, що саме несе: **0.5 мілісекунди**, якщо обидві машини в одному дата-центрі, і **150 мілісекунд**, якщо пакет іде через океан. Ось стала, навколо якої крутиться весь розбір: `c` — ціна одного переходу.

Будуємо чотири речі. Спершу — **лічильник межі**, щоб переходи можна було рахувати, а не вгадувати. Потім — **балакучий** інтерфейс (кожен геттер летить окремо) і **грубий** (один знімок забирає все), обидва проти того самого лічильника. Далі — **збірку** `DeviceDTO` на боці хаба й **відновлення** повноцінних об'єктів на боці хмари. І наприкінці — чотири граблі, на які ця дисципліна наступає, якщо тримати її бездумно: over-fetch, завеликий знімок, N+1, що переїхав усередину, і версії DTO.

## Зробимо межу вимірною

Ідея проста, майже нахабна: якщо перехід невидимий, проженімо **кожен** перехід крізь одну точку, і хай вона їх лічить. Реального дроту в прикладі нема — є чесний облік того, скільки разів ми той дріт торкнули б. А час рахуємо вже потім, помноживши перелік на ціну одного переходу.

:::tabs
```ts
// Перехід через межу невидимий у коді — тому й пастка.
// Зробимо його ВИМІРНИМ: кожен перехід іде крізь Link, і той його лічить.
class Link {
  crossings = 0;
  // один похід туди-й-назад; реального дроту нема — є облік дотиків до нього
  async cross<T>(work: () => T): Promise<T> {
    this.crossings++;
    return work();                 // тут «летіли б байти»; ми лише рахуємо перехід
  }
  costMs(perCrossing: number): number {
    return this.crossings * perCrossing;   // 0.5 — той самий ДЦ; 150 — через океан
  }
}
```
```py
# Перехід через межу невидимий у коді — тому й пастка.
# Зробимо його ВИМІРНИМ: кожен перехід іде крізь Link, і той його лічить.
class Link:
    def __init__(self):
        self.crossings = 0

    async def cross(self, work):            # один похід туди-й-назад
        self.crossings += 1
        return work()                       # «летіли б байти»; ми лише рахуємо перехід

    def cost_ms(self, per_crossing: float) -> float:
        return self.crossings * per_crossing   # 0.5 — той самий ДЦ; 150 — океан
```
:::

Зверни увагу на одну свідому дрібницю: `work` — **синхронна** функція, а `cross` — асинхронна. Так і в житті: сам виклик по той бік дешевий, дорогий саме похід туди-назад, і саме його ми чекаємо через `await`. Лічильник не імітує затримку справжнім сном — навіщо чекати двадцять секунд, аби це довести; він рахує переходи, а секунди дає множення. Тепер два інтерфейси проти цього лічильника.

## Балакучий варіант: сто п'ятдесят переходів

На хабі живуть справжні об'єкти. Їхні геттери локальні, тобто дарові — і всередині хаба дрібнити їх на окремі `type()`, `room()`, `state()` цілком правильно.

:::tabs
```ts
// НА ХАБІ — справжні об'єкти з поведінкою. Геттери локальні, тобто дарові.
class Device {
  constructor(
    readonly id: string,
    private _type: string, private _room: string, private _state: string,
    private _brightness: number, private _lastSeen: number,
  ) {}
  type()       { return this._type; }
  room()       { return this._room; }
  state()      { return this._state; }
  brightness() { return this._brightness; }
  lastSeen()   { return this._lastSeen; }
}

class Hub {
  private devices = new Map<string, Device>();
  register(d: Device) { this.devices.set(d.id, d); }
  get(id: string): Device {
    const d = this.devices.get(id);
    if (!d) throw new Error(`no device ${id}`);
    return d;
  }
  ids(): string[] { return [...this.devices.keys()]; }
}
```
```py
# НА ХАБІ — справжні об'єкти з поведінкою. Геттери локальні, тобто дарові.
class Device:
    def __init__(self, id, type, room, state, brightness, last_seen):
        self.id = id
        self._type, self._room, self._state = type, room, state
        self._brightness, self._last_seen = brightness, last_seen
    def type(self):       return self._type
    def room(self):       return self._room
    def state(self):      return self._state
    def brightness(self): return self._brightness
    def last_seen(self):  return self._last_seen

class Hub:
    def __init__(self):
        self._devices = {}
    def register(self, d): self._devices[d.id] = d
    def get(self, id):     return self._devices[id]
    def ids(self):         return list(self._devices)
```
:::

А тепер — рефлекторна пастка. Хмара хоче ті самі об'єкти в себе, тож ми даємо їй **проксі**: клас, що виглядає як `Device`, але кожен геттер якого крадькома перетинає межу. У коді нічого не кричить «мережа» — і в цьому вся біда.

:::tabs
```ts
function render(..._fields: unknown[]) {}   // малює один рядок дашборда (заглушка)

// НА ХМАРІ — проксі. Виглядає як Device, але КОЖЕН геттер перетинає межу.
class RemoteDevice {
  constructor(private id: string, private hub: Hub, private link: Link) {}
  type()       { return this.link.cross(() => this.hub.get(this.id).type()); }
  room()       { return this.link.cross(() => this.hub.get(this.id).room()); }
  state()      { return this.link.cross(() => this.hub.get(this.id).state()); }
  brightness() { return this.link.cross(() => this.hub.get(this.id).brightness()); }
  lastSeen()   { return this.link.cross(() => this.hub.get(this.id).lastSeen()); }
}

async function renderChatty(ids: string[], hub: Hub, link: Link) {
  for (const id of ids) {                   // 30 пристроїв
    const d = new RemoteDevice(id, hub, link);
    render(await d.type(), await d.room(), await d.state(),
           await d.brightness(), await d.lastSeen());   // 5 переходів на пристрій
  }
}
```
```py
def render(*_fields):                       # малює один рядок дашборда (заглушка)
    pass

# НА ХМАРІ — проксі. Виглядає як Device, але КОЖЕН геттер перетинає межу.
class RemoteDevice:
    def __init__(self, id, hub, link):
        self.id, self.hub, self.link = id, hub, link
    async def type(self):       return await self.link.cross(lambda: self.hub.get(self.id).type())
    async def room(self):       return await self.link.cross(lambda: self.hub.get(self.id).room())
    async def state(self):      return await self.link.cross(lambda: self.hub.get(self.id).state())
    async def brightness(self): return await self.link.cross(lambda: self.hub.get(self.id).brightness())
    async def last_seen(self):  return await self.link.cross(lambda: self.hub.get(self.id).last_seen())

async def render_chatty(ids, hub, link):
    for id in ids:                          # 30 пристроїв
        d = RemoteDevice(id, hub, link)
        render(await d.type(), await d.room(), await d.state(),
               await d.brightness(), await d.last_seen())   # 5 переходів на пристрій
```
:::

Цикл читається як робота з пам'яттю — а лічильник по його завершенні показує **150**. П'ять геттерів на пристрій, тридцять пристроїв. (Строго кажучи, ще один перехід треба на сам список `ids`, але подаруймо балакучому дизайну цю знижку — навіть без неї він програє з розгромом.) Помножмо на ціну переходу:

```
балакучий:  150 переходів
  × 0.5 мс  (той самий ДЦ)  =  75 мс     — уже помітний тормоз
  × 150 мс  (через океан)   =  22 500 мс =  22.5 секунди спінера
```

## Грубий варіант: один знімок туди, об'єкти назад

Лік очевидний, щойно названо хворобу: замість «спитати об'єкт п'ять разів» — «забрати знімок один раз». Хаб дістає **плаский пакунок** — [DTO](topic:sf-apps/dto), структуру самих полів без жодної поведінки, скроєну на те, щоб їхати по дроту одним шматком. Ключове тут — де ця збірка відбувається: **на боці хаба**, де всі геттери локальні й дарові. По межі летить уже готовий пакунок.

:::tabs
```ts
// Плаский пакунок: самі поля, нуль поведінки, версія формату. Скроєний на дріт.
interface DeviceDTO {
  v: 1;                            // версія формату — знадобиться в кінці
  id: string;
  type: string; room: string; state: string;
  brightness: number; lastSeen: number;
}

class Hub {
  // ... register / get / ids — як вище ...

  // ГРУБА межа: один метод збирає ВЕСЬ реєстр у пакунок.
  // Усі геттери тут дарові — Device лежить у тому самому процесі.
  snapshot(): DeviceDTO[] {
    const out: DeviceDTO[] = [];
    for (const d of this.devices.values())
      out.push({ v: 1, id: d.id,
        type: d.type(), room: d.room(), state: d.state(),
        brightness: d.brightness(), lastSeen: d.lastSeen() });
    return out;
  }
}
```
```py
from dataclasses import dataclass

# Плаский пакунок: самі поля, нуль поведінки, версія формату. Скроєний на дріт.
@dataclass
class DeviceDTO:
    v: int
    id: str
    type: str; room: str; state: str
    brightness: int; last_seen: float

class Hub:
    # ... register / get / ids — як вище ...

    # ГРУБА межа: один метод збирає ВЕСЬ реєстр у пакунок.
    # Усі геттери тут дарові — Device лежить у тому самому процесі.
    def snapshot(self):
        return [DeviceDTO(1, d.id, d.type(), d.room(), d.state(),
                          d.brightness(), d.last_seen())
                for d in self._devices.values()]
```
:::

Тепер найтонше місце всієї дисципліни — **бік хмари**. Спокуса тут — лишити прибулі DTO як є й ганяти по коду пласкі пакунки. Це помилка дзеркальна до балакучого інтерфейсу: тоді хмарний код зросте на зчепленні з формою дроту. Тож ми робимо навпаки — з пакунка **відновлюємо повноцінний об'єкт**, у якого своя, потрібна саме хмарі поведінка. DTO живе рівно стільки, скільки летить через межу, і вмирає, щойно перетнув її.

:::tabs
```ts
// НА ХМАРІ пакунок знову стає об'єктом — зі СВОЄЮ поведінкою (локальною, даровою).
class CloudDevice {
  constructor(
    readonly id: string,
    readonly type: string, readonly room: string, readonly state: string,
    readonly brightness: number, readonly lastSeen: number,
  ) {}
  static fromDTO(dto: DeviceDTO): CloudDevice {
    return new CloudDevice(dto.id, dto.type, dto.room, dto.state,
                           dto.brightness, dto.lastSeen);
  }
  isStale(now: number): boolean { return now - this.lastSeen > 60; }
  label(): string { return `${this.room}: ${this.type}`; }
}

async function renderCoarse(hub: Hub, link: Link, now: number) {
  const dtos = await link.cross(() => hub.snapshot());   // 1 перехід — увесь знімок
  const devices = dtos.map(CloudDevice.fromDTO);         // пакунки → об'єкти
  for (const d of devices)
    render(d.label(), d.state, d.brightness, d.isStale(now));   // локально, дарма
}
```
```py
# НА ХМАРІ пакунок знову стає об'єктом — зі СВОЄЮ поведінкою (локальною, даровою).
class CloudDevice:
    def __init__(self, id, type, room, state, brightness, last_seen):
        self.id, self.type, self.room = id, type, room
        self.state, self.brightness, self.last_seen = state, brightness, last_seen

    @classmethod
    def from_dto(cls, dto):
        return cls(dto.id, dto.type, dto.room, dto.state, dto.brightness, dto.last_seen)

    def is_stale(self, now): return now - self.last_seen > 60
    def label(self):         return f"{self.room}: {self.type}"

async def render_coarse(hub, link, now):
    dtos = await link.cross(hub.snapshot)          # 1 перехід — увесь знімок
    devices = [CloudDevice.from_dto(x) for x in dtos]
    for d in devices:
        render(d.label(), d.state, d.brightness, d.is_stale(now))   # локально, дарма
```
:::

Наповнимо хаб тридцятьма пристроями й проженімо обидва інтерфейси проти свіжих лічильників:

:::tabs
```ts
const hub = new Hub();
for (let i = 0; i < 30; i++)
  hub.register(new Device(`d${i}`, "lamp", "hall", "on", 80, 1000));

const chatty = new Link();
await renderChatty(hub.ids(), hub, chatty);
const coarse = new Link();
await renderCoarse(hub, coarse, /* now = */ 1030);

console.log(chatty.crossings, coarse.crossings);      // → 150   1
console.log(chatty.costMs(150), coarse.costMs(150));  // → 22500 150   (мс, океан)
```
```py
hub = Hub()
for i in range(30):
    hub.register(Device(f"d{i}", "lamp", "hall", "on", 80, 1000))

chatty = Link()
await render_chatty(hub.ids(), hub, chatty)
coarse = Link()
await render_coarse(hub, coarse, now=1030)

print(chatty.crossings, coarse.crossings)         # → 150 1
print(chatty.cost_ms(150), coarse.cost_ms(150))   # → 22500 150   (мс, океан)
```
:::

Той самий дашборд, та сама межа — і два числа замість суперечки:

```
              переходи    ДЦ (×0.5 мс)   океан (×150 мс)
балакучий        150         75 мс          22.5 с
грубий             1         0.5 мс         150 мс
```

Сто п'ятдесят переходів стиснулись в один; двадцять дві секунди — у півсекунди за океаном. І це не «швидша машина» — обидва прогони крутили той самий код на тому самому залізі. Різниця вся в тому, **скільки разів ми торкнулись межі**.

## Дрібно всередині, грубо на межі — що саме зробили

Спинімося на мить, бо без цього лік перетворюється на новий забобон. Ми **не викинули** дрібнозернисті об'єкти. На хабі `Device` як був об'єктом із геттерами, так і лишився — там виклики локальні, дарові, і дрібнити їх правильно. На хмарі пакунок знову став об'єктом `CloudDevice` зі своєю поведінкою — і там геттери теж локальні й дарові. Грубим ми зробили **рівно одне — сам перехід через межу**: замість сотні дрібних дотиків один ситий.

![Три колонки, розділені двома пунктирними стінами-межами. Ліва колонка «ХАБ» на зеленому: об'єкти Device з поведінкою, підпис «геттери локальні, дарові». Стрілка крізь першу стіну підписана «збірка → DeviceDTO[]». Середня вузька колонка «ДРІТ»: один пакунок «30 × DeviceDTO», підпис «1 перехід через межу». Стрілка крізь другу стіну підписана «DTO → відновлення». Права колонка «ХМАРА» на зеленому: об'єкти CloudDevice з поведінкою, підпис «геттери знову локальні, дарові». Унизу девіз «DTO живе лише на дроті»](img/wire-pipeline.svg)
*Дрібно на обох берегах, грубо лише на переправі. Об'єкти з поведінкою живуть і на хабі, і в хмарі; пласким пакунком дані стають рівно на той час, поки перетинають межу, — і одразу по той бік знову збираються в об'єкти. Грубизна — властивість переходу, а не домену.*

> 🔧 **Навіщо це.** Плаский DTO — це **формат дроту**, а не твоя модель. Тримай його на межі й не пускай глибше: щойно пакунок перетнув кордон, віддай його справжньому об'єктові й далі працюй з об'єктом. Інакше форма дроту протече в бізнес-логіку, і ти отримаєш те саме зчеплення з мережею, від якого тікав, — лише вивернуте навиворіт.

## Складність і пастки

Грубизна на межі — правило, а не заклинання. Застосована бездумно, вона наступає на чотири окремі граблі, і кожна б'є по-своєму.

### Over-fetch: грубо — не значить «усе підряд»

Перша грабля — перебір у інший бік. `snapshot()` тягне всі п'ять полів на кожен із тридцяти пристроїв — а список на телефоні малює лише кімнату й стан. Виходить, `type`, `brightness` і `lastSeen` летять по дроту, аби бути викинутими одразу по прибутті. На тридцяти пристроях це дрібниця; на п'яти тисячах — реальні кілобайти, за які хтось платить і які хтось розпаковує. Грубо перекачали в «забрати все», а треба — «забрати рівно те, що екран малює».

Лік — кроїти пакунок **під вигляд**. Списковий екран отримує вузький DTO, екран деталей одного пристрою — повний. Переходів так само один; пакунок утричі легший.

:::tabs
```ts
// Грубо — не означає «усе підряд». Список малює лише кімнату й стан.
interface ListItemDTO { v: 1; id: string; room: string; state: string; }

class Hub {
  // ... snapshot() лишається для екрана деталей ...
  listView(): ListItemDTO[] {              // той самий 1 перехід, утричі менший пакунок
    return [...this.devices.values()].map(d =>
      ({ v: 1 as const, id: d.id, room: d.room(), state: d.state() }));
  }
}
```
```py
# Грубо — не означає «усе підряд». Список малює лише кімнату й стан.
@dataclass
class ListItemDTO:
    v: int; id: str; room: str; state: str

class Hub:
    # ... snapshot() лишається для екрана деталей ...
    def list_view(self):                     # той самий 1 перехід, утричі менший пакунок
        return [ListItemDTO(1, d.id, d.room(), d.state())
                for d in self._devices.values()]
```
:::

### Завеликий знімок: грубо, але обмежено

Друга грабля вилазить, коли будинок росте. Тридцять пристроїв у знімку — ніщо. А ось велика будівля на **п'ять тисяч** пристроїв: один `snapshot()` стає багатомегабайтним пакунком, який хаб мусить весь зібрати в пам'яті, проштовхнути одним повідомленням (а в багатьох транспортів є стеля на розмір) і який хмара не покаже, доки не приповзе останній байт. «Один виклик» було правильно; «один **безмежний** виклик» — нова пастка.

Тож грубо, але **обмежено**: не сто дрібних смиків, але й не один валун, а сторінки скінченного розміру з курсором, що веде до наступної.

:::tabs
```ts
interface Page { items: DeviceDTO[]; nextCursor: string | null; }

class Hub {
  // Грубо, але ОБМЕЖЕНО: сторінка по limit; курсор — id, з якого починати далі.
  snapshotPage(cursor: string | null, limit: number): Page {
    const ids = this.ids();
    const start = cursor ? ids.indexOf(cursor) + 1 : 0;
    const items = ids.slice(start, start + limit).map(id => {
      const d = this.get(id);
      return { v: 1 as const, id: d.id, type: d.type(), room: d.room(),
               state: d.state(), brightness: d.brightness(), lastSeen: d.lastSeen() };
    });
    const last = items.length ? items[items.length - 1].id : null;
    return { items, nextCursor: start + limit < ids.length ? last : null };
  }
}

async function pullAll(hub: Hub, link: Link): Promise<DeviceDTO[]> {
  const all: DeviceDTO[] = [];
  let cursor: string | null = null;
  do {
    const page = await link.cross(() => hub.snapshotPage(cursor, 200));  // 1 перехід/сторінка
    all.push(...page.items);
    cursor = page.nextCursor;
  } while (cursor);
  return all;                             // 5000 пристроїв → 25 переходів, не 25000
}
```
```py
@dataclass
class Page:
    items: list
    next_cursor: "str | None"

class Hub:
    # Грубо, але ОБМЕЖЕНО: сторінка по limit; курсор — id, з якого починати далі.
    def snapshot_page(self, cursor, limit):
        ids = self.ids()
        start = ids.index(cursor) + 1 if cursor else 0
        window = ids[start:start + limit]
        items = [DeviceDTO(1, d.id, d.type(), d.room(), d.state(),
                           d.brightness(), d.last_seen())
                 for d in (self.get(i) for i in window)]
        nxt = window[-1] if start + limit < len(ids) else None
        return Page(items, nxt)

async def pull_all(hub, link):
    out, cursor = [], None
    while True:
        page = await link.cross(lambda: hub.snapshot_page(cursor, 200))  # 1 перехід/сторінка
        out += page.items
        cursor = page.next_cursor
        if cursor is None:
            break
    return out                            # 5000 пристроїв → 25 переходів, не 25000
```
:::

П'ять тисяч пристроїв сторінками по двісті — це двадцять п'ять переходів. Проти двадцяти п'яти тисяч у балакучому — усе одно в тисячу разів менше, а кожен перехід тепер обмежений, передбачуваний і піддається потоковому показу. Грубо ловить головний виграш; обмеженість боронить від нового краю.

### N+1, що переїхав усередину межі

Третя грабля — найпідступніша, бо ховається за зеленим лічильником. Хмара бачить один перехід і тішиться. Але що, як `state` — не поле в пам'яті хаба, а **живе показання заліза**, яке хаб читає з фізичного пристрою по радіо? Радіо — це теж межа, друга, схована всередині. І тоді `snapshot()`, грубий назовні, всередині робить тридцять окремих радіо-переходів. N+1 не зник — він **переїхав** за першу межу й затих.

Виявити його можна тим самим прийомом: навісити лічильник і на **другу** межу.

:::tabs
```ts
class Radio {                    // друга межа: синхронний драйвер заліза
  reads = 0;
  read(id: string): string { this.reads++; return "on"; }   // кожне читання — перехід
}

class HubLive {
  private devices = new Map<string, Device>();
  constructor(private radio: Radio) {}
  // ... register / ids ...
  snapshot(): DeviceDTO[] {
    const out: DeviceDTO[] = [];
    for (const d of this.devices.values())
      out.push({ v: 1, id: d.id, type: d.type(), room: d.room(),
                 state: this.radio.read(d.id),          // ← прихований перехід на кожен!
                 brightness: d.brightness(), lastSeen: d.lastSeen() });
    return out;
  }
}
// cloudLink.crossings === 1     ← грубо, як домовлялись
// radio.reads       === 30      ← балакучий N+1, лише сховався всередину
```
```py
class Radio:                     # друга межа: синхронний драйвер заліза
    def __init__(self): self.reads = 0
    def read(self, id):
        self.reads += 1                                  # кожне читання — перехід
        return "on"

class HubLive:
    def __init__(self, radio):
        self._devices, self.radio = {}, radio
    # ... register / ids ...
    def snapshot(self):
        return [DeviceDTO(1, d.id, d.type(), d.room(),
                          self.radio.read(d.id),          # ← прихований перехід на кожен!
                          d.brightness(), d.last_seen())
                for d in self._devices.values()]
# cloud_link.crossings == 1     ← грубо, як домовлялись
# radio.reads          == 30      ← балакучий N+1, лише сховався всередину
```
:::

![Три блоки, розділені двома пунктирними стінами. Ліворуч блок «ХМАРА / дашборд». Від нього одна зелена стрілка «1 перехід» крізь першу стіну («межа 1») до середнього блоку «ХАБ / snapshot() / грубий назовні». Праворуч від хаба — друга стіна, червона й підписана «межа 2 — схована!», а крізь неї віялом ідуть багато червоних стрілок із підписом «× 30» до блоку «фізичні пристрої». Унизу два лічильники: зелений «cloud.crossings = 1» і червоний «radio.reads = 30 — прихований N+1»](img/hidden-n1.svg)
*Хмара бачить один грубий перехід — і лічильник першої межі це підтверджує. Але за хабом ховається друга межа, радіо до заліза, і на ній той самий балакучий N+1: тридцять переходів, яких з боку хмари не видно. Грубий фасад не рятує, якщо нутро балакуче.*

Ліки — не «зробити snapshot асинхронним» (це лише замаскує тридцять походів), а прибрати другу межу з гарячого шляху: хай пристрій **штовхає** свій стан у кеш хаба, коли той міняється, а `snapshot()` читає пам'ять, не радіо. Тоді радіо-переходів на показ дашборда — нуль. Мораль ширша за приклад: лічи переходи на **кожній** межі, а не лише на тій, що на видноті. Грубий фасад над балакучим нутром — та сама пастка, просто на поверх глибша.

### Версії DTO: хаб і хмара котяться нарізно

Четверта грабля росте з того самого факту, що й уся межа: хаб і хмара — різні машини, часто різні команди й **різні темпи розгортання**. Хаб у домі оновиться тоді, коли до нього дійдуть руки; хмара — щотижня. Тож настане день, коли хаб уже шле нове поле (скажімо, `signal` — рівень Wi-Fi), а стара хмара його ще не знає. Пакунок не можна міняти так, наче обидва боки оновлюються в одну мить, — такої миті нема.

Звідси дисципліна дроту. Читач має бути **терплячий**: невідомі поля мовчки ігнорує, відсутні — підставляє за замовчуванням, а не падає. Поле `v` лишаємо на той рідкісний випадок, коли зміниться не склад, а **зміст** поля й доведеться гілкувати свідомо.

:::tabs
```ts
// Хаб і хмара котяться нарізно. Тому читач ТЕРПЛЯЧИЙ:
// невідомі поля ігнорує, відсутні — підставляє за замовчуванням.
function fromWire(raw: any): CloudDevice {
  return new CloudDevice(
    raw.id,
    raw.type      ?? "unknown",
    raw.room      ?? "?",
    raw.state     ?? "unknown",
    raw.brightness ?? 0,
    raw.lastSeen  ?? 0,
    // raw.signal (нове поле v2) старий читач просто НЕ помічає — і не падає
  );
}
```
```py
# Хаб і хмара котяться нарізно. Тому читач ТЕРПЛЯЧИЙ:
# невідомі поля ігнорує, відсутні — підставляє за замовчуванням.
def from_wire(raw: dict) -> CloudDevice:
    return CloudDevice(
        raw["id"],
        raw.get("type", "unknown"),
        raw.get("room", "?"),
        raw.get("state", "unknown"),
        raw.get("brightness", 0),
        raw.get("last_seen", 0),
        # raw.get("signal") (нове поле v2) старий читач просто не чіпає — і не падає
    )
```
:::

Звідси правило дроту в один рядок: **лише додавай, ніколи не прибирай і не перейменовуй мовчки**. Нове поле стара хмара переживе, бо терплячий читач його не помітить; а от вилучене чи перейменоване поле старий читач шукатиме — і спіткнеться. Коли зміна таки не додавальна (поле треба прибрати, перейменувати чи змінити його тип), одним кроком її не проведеш: спершу веди обидві форми паралельно, дай усім бокам оновитися й лише тоді прибери стару. Це той самий танець [розширення-звуження](root:progarch/what-makes-irreversible/proj-expand-contract.md), яким міняють будь-який контракт без спільного дня оновлення — і серіалізований DTO ([що це](topic:com-protocol/data-serialization)) підкоряється йому так само, як схема на диску.

## Що лишається в руках

Ми взяли обіцянку статті й довели її до коду, який лічить. Перше й головне: перехід через межу вдалося зробити **вимірним** — лічильник обернув суперечку смаків на два числа, 150 проти 1, і провалля між ними видно без жодної риторики. Друге: знімок збирається **на боці хаба**, де геттери дарові, летить одним пакунком, а на боці хмари **відновлюється в об'єкт** зі своєю поведінкою — дрібно на обох берегах, грубо лише на переправі. DTO виявився не моделлю, а форматом дроту, що живе рівно поки летить.

І чотири граблі окреслили той самий закон із чотирьох боків. Over-fetch нагадав, що грубо — не «усе підряд», а «рівно під вигляд». Завеликий знімок — що грубо мусить бути обмеженим, сторінкою з курсором, а не валуном. Прихований N+1 — що лічити переходи треба на **кожній** межі, бо балакучість любить переїхати на поверх глибше. А версії DTO — що межу, яку не можна оновити в одну мить, перетинають лише додавальними змінами й терплячим читачем. Скрізь під сподом та сама механіка: ціна межі є ціна межі, тож торкайся її **рідко й ситно** — а щоб знати, чи справді рідко, не гадай, а порахуй.
