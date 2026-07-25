# ⚙️ Робочий оркестратор передачі: цикл, що переживає власний крах

Кістяк у статті показав головне чесно: рід кроку сам вирішує, куди хилити на невдачі, а порядок у списку несе решту мудрості. Але той кістяк тримає перелік зроблених кроків `done` у **локальній змінній** і мовчки припускає, що кожен `run` якось-то ідемпотентний. Витягни машину з розетки посеред циклу — і `done` випарується разом із оперативною пам'яттю: піднявшись, координатор не знатиме ні на якому він кроці, ні що вже відкочувати. Для процедури, що тягнеться днями й посеред себе чекає на живу людину, це не крайовий випадок — це перше, що з нею станеться в проді.

Тож доберемо кістяк до кінця. Винесемо пам'ять саги у сховище, зробимо кожен крок стійким до повтору, навчимо чекати на людину з витримкою, повторювати після півота з відступом і здавати безнадійно застрягле в мертву чергу. А тоді — доведемо тестом-ін'єкцією збою, що дві невдачі й справді розходяться на дві різні долі, а не просто на словах.

## Задача

Ось що робочий оркестратор мусить уміти понад кістяк.

Перше — **повна таблиця кроків, і в кожного зворотного крок названо його компенсацію**, бо саме компенсації задають, що можна відкотити:

| Крок | Рід | Діло (`run`) | Компенсація | Ключ ідемпотентності |
|---|---|---|---|---|
| `freeze` | зворотний | заморозити дім | `unfreeze` — розморозити | `saga:freeze:<dir>` |
| `revokeAccess` | зворотний | відкликати ключі старих | `restoreOldKeys` — повернути | `saga:revokeAccess:<dir>` |
| `awaitClaim` | зворотний | запросити й чекати нових | `cancelClaim` — відкликати запрошення | `saga:awaitClaim:<dir>` |
| `transferAndWipe` | **півот** | передати власність + стерти | **немає** — незворотно | `saga:transferAndWipe:forward` |
| `rebindDevices` | повторюваний | перевипустити сертифікати | — | `saga:rebindDevices:forward` |
| `openBilling` | повторюваний | переоформити тариф | — | `saga:openBilling:forward` |
| `welcome` | повторюваний | привітати нових | — | `saga:welcome:forward` |

Друге — **пережити власний крах**. Стан «де я на сазі» мусить жити у сховищі, а не на стеку; і, що тонше, просування саги на крок мусить лягати в базу **разом** із подією «крок зроблено» — інакше між двома записами відкривається щілина, куди провалюється або загублена подія, або привид події без просування. Це [транзакційний outbox](book:programming/outbox-pattern), і без нього тривкий цикл — самообман.

Третє — **ключ ідемпотентності на крок**, бо повідомлення про крок доставляється [щонайменше раз](book:programming/idempotent-consumers-deep), і повтор «відкликати ключі» не сміє відкликати їх удвічі.

Четверте — **витримка на людину** в `awaitClaim`: запросити нових власників і чекати не вічно, а до строку; мовчання до строку — це невдача **до** півота, з розворотом.

П'яте — **повтор із відступом** після півота і **мертва черга** для того, що застрягло надовго: [DLQ](book:programming/dead-letter-queue) з сигналом людині.

І нарешті — **тест, що інжектує збій** і доводить дві долі. Збий крок **до** півота — маємо побачити компенсації у зворотному порядку й чисте скасування. Збий крок **після** — жодної компенсації, повтори, а на затятому збої — мертву чергу.

## Ідея: пам'ять саги — у сховищі, а не на стеку

Один структурний хід прибирає найбільший страх: **зробити стан саги рядком у базі**, а сам координатор — не функцією, що біжить від початку до кінця, а машиною, що робить **рівно один крок за такт** і між тактами нічого не тримає в голові. Уся її пам'ять — це персистентний рядок: на якому кроці курсор, куди дивиться (вперед чи назад), скільки разів уже пробувала поточний крок. Крах між тактами тепер безкарний: піднявшись, машина перечитує рядок і тикає далі з того самого місця. Це і є [тривкий процес](book:programming/durable-workflows) — не магія, а перенесена у сховище змінна циклу.

Але одного персистентного курсора мало, і ось чому. Просунути курсор — це наш локальний запис; а «сказати світові, що крок зроблено» — це подія в брокер. Два різні записи у дві різні системи: класична проблема подвійного запису. Впадеш між ними — і або курсор поїхав уперед, а події нема (наступний крок ніколи не поїде), або подію відправлено, а курсор не закомічено (привид). Ліки — не героїзм, а **outbox**: подію кладемо **рядком у ту саму базу, в тій самій транзакції**, що й просування курсора. Коміт дає обидва записи або жодного. А окреме реле згодом вичитує outbox і публікує в брокер; упаде реле — по підйому дочитає незакомічене. Ніякого двофазного коміту, жодного розподіленого замка — лише одна локальна транзакція й один фоновий читач.

![Ліворуч наївний подвійний запис: спершу коміт «посунути стан саги», потім окрема публікація події — і хрест «крах саме тут» у щілині між ними, після якого подія загубилась, а стан уже поїхав уперед. Праворуч outbox: одна транзакція містить три рядки — діло кроку, нову позицію саги й рядок outbox із подією — і комітиться разом; окреме реле потім читає outbox і публікує в брокер, тож крах будь-де безпечний](/guide/progarch/messaging-and-eip/dh-handover-saga/img/outbox-atomic.svg)
*Наївний подвійний запис лишає щілину: крах між просуванням стану й публікацією події губить одне з двох. Outbox замикає стан саги й подію кроку в одну транзакцію — коміт дає обидва, крах не дає напіврезультату, а реле публікує подію вже по факту.*

> 🔧 **Навіщо це.** Outbox і ключ ідемпотентності лікують **різні** половини однієї хвороби, тож потрібні обидва. Outbox стежить, щоб **локально** просування саги й подія про нього ніколи не розійшлися — жодної загубленої чи осиротілої події. Ключ ідемпотентності стежить, щоб **на тому боці** повторна доставка того самого кроку не спрацювала вдруге. Викинь outbox — і крах між записами лишить сагу в стані, якого нема в жодній події; викинь ключ — і повтор кроку двічі відкличе доступ, двічі виставить рахунок. Одна транзакція проти щілини, один ключ проти повтору.

## Робочий код

Домен тут — бекенд-оркестрація: рядок у базі, транзакція, подія, повтор. Основна валюта модуля — TypeScript на Node поряд із Python, тож даю обидві мови вкладками; логіка переноситься майже дослівно.

### Кроки як дані та порти у світ

Спершу — тип саги (це і є вся пам'ять), таблиця кроків із компенсаціями та **порти**: усе, чим координатор торкається світу, схований за цими дужками, щоб серце машини лишалось чистою логікою, яку легко проженути в тесті.

:::tabs
```ts
type Kind = "compensatable" | "pivot" | "retriable";
type Dir  = "forward" | "back";

interface Ctx { homeId: string; idemKey: string }
interface Step {
  name: string; kind: Kind;
  run: (c: Ctx) => Promise<void>;
  compensate?: (c: Ctx) => Promise<void>;   // тільки у зворотних
}

// ВЕСЬ стан саги — персистентний рядок; на стеку не тримаємо нічого.
interface Saga {
  id: string; homeId: string;
  cursor: number;                            // індекс кроку, на якому стоїмо
  dir: Dir;                                  // forward | back
  status: "running" | "waiting" | "aborted" | "done" | "stuck";
  attempts: number;                          // повтори поточного повторюваного кроку
  deadline?: number;                         // строк людського очікування (awaitClaim)
}

interface Tx {}                              // ручка транзакції сховища
interface Ports {                            // усе, що машина пише у світ, — через ці дужки
  load(id: string): Promise<Saga>;
  persist(s: Saga): Promise<void>;           // звичайний тривкий запис стану
  txn<T>(fn: (tx: Tx) => Promise<T>): Promise<T>;   // ОДНА транзакція сховища
  seen(tx: Tx, key: string): Promise<boolean>;      // цей ключ уже застосовували?
  mark(tx: Tx, key: string): Promise<void>;
  saveIn(tx: Tx, s: Saga): Promise<void>;    // записати стан саги В ЦІЙ транзакції
  outbox(tx: Tx, ev: unknown): Promise<void>;// покласти подію в outbox В ЦІЙ транзакції
  alert(s: Saga, step: Step, err: unknown): Promise<void>;  // сигнал людині (DLQ)
}

// Порядок і є суть: усе зворотне ДО півота, усе обов'язкове — ПІСЛЯ.
// freeze, unfreeze, revokeOldKeys … — тонкі клієнти відповідних контекстів.
const STEPS: Step[] = [
  { name: "freeze",          kind: "compensatable", run: freeze,          compensate: unfreeze },
  { name: "revokeAccess",    kind: "compensatable", run: revokeOldKeys,   compensate: restoreOldKeys },
  { name: "awaitClaim",      kind: "compensatable", run: waitForNewOwner, compensate: cancelClaim },
  { name: "transferAndWipe", kind: "pivot",         run: transferAndShred },   // без compensate
  { name: "rebindDevices",   kind: "retriable",     run: reissueCerts },
  { name: "openBilling",     kind: "retriable",     run: switchBilling },
  { name: "welcome",         kind: "retriable",     run: notifyNewOwner },
];
const MAX_ATTEMPTS = 12;
```
```py
from dataclasses import dataclass
from enum import Enum

class Kind(str, Enum):
    COMPENSATABLE = "compensatable"; PIVOT = "pivot"; RETRIABLE = "retriable"

@dataclass
class Step:
    name: str; kind: Kind
    run: object                    # async fn(ctx)
    compensate: object = None      # async fn(ctx) — тільки у зворотних

@dataclass
class Saga:                        # ВЕСЬ стан саги — персистентний рядок
    id: str; home_id: str
    cursor: int = 0                # індекс кроку, на якому стоїмо
    dir: str = "forward"           # "forward" | "back"
    status: str = "running"        # running|waiting|aborted|done|stuck
    attempts: int = 0              # повтори поточного повторюваного кроку
    deadline: float | None = None  # строк людського очікування

# Порти у світ: усе, що машина пише, — через ці методи (у тесті підмінимо).
class Ports:
    async def load(self, i): ...
    async def persist(self, s): ...          # звичайний тривкий запис
    def txn(self): ...                        # async-контекст: ОДНА транзакція
    async def seen(self, tx, key): ...        # ключ уже застосовували?
    async def mark(self, tx, key): ...
    async def save_in(self, tx, s): ...       # стан саги В ЦІЙ транзакції
    async def outbox(self, tx, ev): ...       # подія в outbox В ЦІЙ транзакції
    async def alert(self, s, step, err): ...  # сигнал людині (DLQ)

# freeze, unfreeze, revoke_keys … — тонкі клієнти відповідних контекстів.
STEPS = [
    Step("freeze",          Kind.COMPENSATABLE, freeze,          unfreeze),
    Step("revoke_access",   Kind.COMPENSATABLE, revoke_keys,     restore_keys),
    Step("await_claim",     Kind.COMPENSATABLE, wait_for_owner,  cancel_claim),
    Step("transfer_wipe",   Kind.PIVOT,         transfer_shred),   # без compensate
    Step("rebind_devices",  Kind.RETRIABLE,     reissue_certs),
    Step("open_billing",    Kind.RETRIABLE,     switch_billing),
    Step("welcome",         Kind.RETRIABLE,     notify_owner),
]
MAX_ATTEMPTS = 12
```
:::

### Атомний ідемпотентний крок

Тепер — одиниця, з якої складено все: застосувати крок. Спершу пускаємо **ефект** (він іде в чужий контекст і несе `idemKey`, тож той бік сам відсіє повтор), а тоді в **одній транзакції** позначаємо ключ, зсуваємо курсор і кладемо подію в outbox. Ключова тонкість — перевірка `seen` **всередині** транзакції: якщо цей крок уже застосовано (дубль доставки), уся транзакція стає нічого-не-роблю, і курсор не поповзе вдруге.

:::tabs
```ts
// Ефект + просування саги та подія — атомарно. Напрям вирішує, run це чи compensate.
async function applyStep(p: Ports, saga: Saga, step: Step, dir: Dir): Promise<void> {
  const key = `${saga.id}:${step.name}:${dir}`;           // ключ на крок І напрям
  const action = dir === "forward" ? step.run : step.compensate;
  if (action) await action({ homeId: saga.homeId, idemKey: key });  // ефект; повтор — тихий no-op на тому боці

  await p.txn(async (tx) => {                              // стан + подія — В ОДНІЙ транзакції
    if (await p.seen(tx, key)) return;                     // дубль → уся транзакція нічого не робить
    await p.mark(tx, key);
    saga.cursor += dir === "forward" ? 1 : -1;
    await p.saveIn(tx, saga);
    await p.outbox(tx, { sagaId: saga.id, step: step.name, dir });
  });
}
```
```py
async def apply_step(p, saga, step, direction):
    key = f"{saga.id}:{step.name}:{direction}"             # ключ на крок І напрям
    action = step.run if direction == "forward" else step.compensate
    if action:
        await action({"home_id": saga.home_id, "idem_key": key})   # ефект; повтор — no-op на тому боці

    async with p.txn() as tx:                              # стан + подія — В ОДНІЙ транзакції
        if await p.seen(tx, key):
            return                                         # дубль → транзакція нічого не робить
        await p.mark(tx, key)
        saga.cursor += 1 if direction == "forward" else -1
        await p.save_in(tx, saga)
        await p.outbox(tx, {"saga": saga.id, "step": step.name, "dir": direction})
```
:::

![Дві доставки того самого кроку revokeAccess — «доставка 1» і «доставка 2 (дубль)» — заходять у вартового «бачив ключ (sagaId, revokeAccess)?». Перша: «ні → виконати revokeOldKeys, записати ключ + результат». Друга: «так → повернути збережений результат, 0 ефекту». Унизу підсумок: ефект стався рівно раз попри дві доставки](/guide/progarch/messaging-and-eip/dh-handover-saga/img/idempotency-dedup.svg)
*Доставка «щонайменше раз» неминуче приносить дублі; ключ `(sagaId, крок, напрям)` перетворює другу доставку на тихе повернення вже зробленого. Ефект стається рівно раз — і на боці оркестратора (курсор не поповзе двічі), і на боці контексту (той дедупить за тим самим ключем).*

### Тривкий цикл: розворот до півота, повтор і DLQ після

Серце — один такт `tick`: зроби рівно один крок і запиши стан. Уся асиметрія саги живе тут, у гілці `catch`. Ідемо назад — просто компенсуємо й задкуємо, доки курсор не впаде за початок. Ідемо вперед і крок упав — дивимось, з якого боку півота стоїмо: **після** нього повторюємо з відступом, а вичерпавши спроби, здаємо в мертву чергу; **до** нього розвертаємось і відкочуємо вже зроблене. А `awaitClaim`, що паркується чекати людину, кидає особливий сигнал — то не невдача, а пауза.

Одна тонкість робить цикл крахостійким і **на кінцях**, не лише в середині. Обидва краї курсора — це термінальні стани, і машина вичитує їх **із самого курсора на кожному вході**, а не покладається на те, що встигла дописати статус: курсор упав за початок (`< 0`) — сага `aborted`; курсор переступив останній крок (`≥ довжину`) — сага `done`. Важить це саме на завершенні. `applyStep` зсуває курсор **усередині** своєї транзакції, а `done` лягає **окремим**, пізнішим записом — і крах у щілині між ними лишив би на диску курсор уже за останнім кроком при статусі ще `running`. Без сторожа на вході машина по підйому полізла б по неіснуючий `steps[курсор]`, впала б у `catch` — а що курсор уже правіше півота, прийняла б завершену сагу за застряглий крок після півота: марні повтори й виклик живої людини до дому, який давно й успішно передано. Тому сторож `курсор ≥ довжина → done` **на вході** в гілку «вперед» дзеркалить давній `курсор < 0 → aborted` і закриває цю щілину — термінал відновлюємо з курсора, а не зі статусу.

:::tabs
```ts
const sleep = (_ms: number) => new Promise((r) => setTimeout(r, _ms));
const backoff = (n: number) => fullJitter(n);   // відступ із джитером — деталі в іншому кроці

async function tick(p: Ports, saga: Saga, steps: Step[]): Promise<Saga> {
  if (saga.status !== "running") return saga;
  const pivot = steps.findIndex((s) => s.kind === "pivot");

  if (saga.dir === "back") {                          // ── задкуємо, відкочуючи ──
    if (saga.cursor < 0) { saga.status = "aborted"; await p.persist(saga); return saga; }
    const step = steps[saga.cursor];
    await applyStep(p, saga, step, "back");           // компенсація + cursor-- атомарно
    if (saga.cursor < 0) saga.status = "aborted";     // відкотили все → чисте скасування
    await p.persist(saga);
    return saga;
  }

  // ── ідемо вперед ──
  if (saga.cursor >= steps.length) {                  // курсор ЗА останнім кроком = ЗАВЕРШЕНО (термінал з курсора)
    saga.status = "done"; await p.persist(saga); return saga;   // ідемпотентний сторож: закриває щілину крах-на-терміналі
  }
  const step = steps[saga.cursor];                    // тепер гарантовано в межах
  try {
    await applyStep(p, saga, step, "forward");        // ефект + cursor++ атомарно
    saga.attempts = 0;
    if (saga.cursor >= steps.length) saga.status = "done";      // ступили за останній → done уже цього такту
    await p.persist(saga);
  } catch (err) {
    if (err instanceof WaitingForHuman) {             // awaitClaim паркується — це НЕ невдача
      saga.status = "waiting"; saga.deadline = err.until;
      await p.persist(saga);
    } else if (saga.cursor > pivot) {                 // ПІСЛЯ півота: не скасовуй — повторюй, тоді DLQ
      saga.attempts += 1;
      if (saga.attempts > MAX_ATTEMPTS) {             // затято застрягло → мертва черга
        saga.status = "stuck"; await p.persist(saga); await p.alert(saga, step, err);
      } else {
        await p.persist(saga); await sleep(backoff(saga.attempts));   // той самий cursor — повтор
      }
    } else {                                          // ДО півота: розвертайся й відкочуй зроблене
      saga.dir = "back"; saga.cursor -= 1;            // невдалий крок не завершився — компенсуємо лише DONE
      await p.persist(saga);
    }
  }
  return saga;
}

// Тривкий цикл: пам'ять — у сховищі, тож крах = перезавантажити й тикати далі.
async function drive(p: Ports, id: string, steps: Step[]): Promise<Saga> {
  let saga = await p.load(id);
  while (saga.status === "running") saga = await tick(p, saga, steps);
  return saga;                                        // done | aborted | stuck | waiting
}
```
```py
import asyncio

async def sleep(ms): await asyncio.sleep(ms / 1000)
def backoff(n): return full_jitter(n)     # відступ із джитером — деталі в іншому кроці

async def tick(p, saga, steps):
    if saga.status != "running":
        return saga
    pivot = next(i for i, s in enumerate(steps) if s.kind is Kind.PIVOT)

    if saga.dir == "back":                            # ── задкуємо, відкочуючи ──
        if saga.cursor < 0:
            saga.status = "aborted"; await p.persist(saga); return saga
        step = steps[saga.cursor]
        await apply_step(p, saga, step, "back")       # компенсація + cursor-- атомарно
        if saga.cursor < 0: saga.status = "aborted"   # відкотили все → чисте скасування
        await p.persist(saga); return saga

    # ── ідемо вперед ──
    if saga.cursor >= len(steps):                     # курсор ЗА останнім кроком = ЗАВЕРШЕНО (термінал з курсора)
        saga.status = "done"; await p.persist(saga); return saga   # ідемпотентний сторож: закриває щілину крах-на-терміналі
    step = steps[saga.cursor]                         # тепер гарантовано в межах
    try:
        await apply_step(p, saga, step, "forward")    # ефект + cursor++ атомарно
        saga.attempts = 0
        if saga.cursor >= len(steps): saga.status = "done"   # ступили за останній → done уже цього такту
        await p.persist(saga)
    except WaitingForHuman as w:                      # awaitClaim паркується — не невдача
        saga.status = "waiting"; saga.deadline = w.until; await p.persist(saga)
    except Exception as err:
        if saga.cursor > pivot:                       # ПІСЛЯ півота: повторюй, тоді DLQ
            saga.attempts += 1
            if saga.attempts > MAX_ATTEMPTS:          # затято застрягло → мертва черга
                saga.status = "stuck"; await p.persist(saga); await p.alert(saga, step, err)
            else:
                await p.persist(saga); await sleep(backoff(saga.attempts))
        else:                                         # ДО півота: розворот
            saga.dir = "back"; saga.cursor -= 1; await p.persist(saga)
    return saga

async def drive(p, sid, steps):
    saga = await p.load(sid)
    while saga.status == "running":
        saga = await tick(p, saga, steps)
    return saga
```
:::

Один `backoff` тут — не наш винахід: **повний джитер** із того ж бюджету-й-відступу, що ми вже [збирали руками з монотонним годинником](guide:progarch/concurrency-and-clocks/proj-monotonic-deadline.md); тут ми лише кличемо його між повторами після півота, і `sleep` спить на монотонному таймері рантайму.

### Витримка на людину: `awaitClaim`

Найдовший крок не робить майже нічого — він **чекає**. `waitForNewOwner` шле нових власників запрошення (ідемпотентно, за `idemKey`) і, якщо ще не підтвердили, кидає `WaitingForHuman` — не помилку, а паузу зі строком. Підтвердять — окрема подія `onClaim` будить сагу вперед. Вичерпається строк — `onClaimDeadline` перетворює мовчання на невдачу **до** півота: курсор лишається на `awaitClaim`, бо запрошення **живе** в світі, тож відкликати треба і його (`cancelClaim`), і все раніше зроблене.

:::tabs
```ts
class WaitingForHuman extends Error { constructor(public until: number) { super("waiting"); } }
const DAY = 86_400_000;

async function waitForNewOwner(ctx: Ctx): Promise<void> {
  await postClaimInvite(ctx.homeId, ctx.idemKey);       // запросити нових (ідемпотентно)
  if (await claimAccepted(ctx.homeId)) return;          // уже підтвердили → крок завершено
  throw new WaitingForHuman(Date.now() + 7 * DAY);      // ще ні → паркуємось, не падаємо
}

// нові власники підтвердили → будимо вперед
async function onClaim(p: Ports, id: string, steps: Step[]): Promise<void> {
  const s = await p.load(id);
  if (s.status !== "waiting") return;                   // ідемпотентно: пізній клац — тиша
  s.status = "running"; await p.persist(s); await drive(p, id, steps);
}
// витримку вичерпано → невдача ДО півота: cursor лишається на awaitClaim (запрошення живе)
async function onClaimDeadline(p: Ports, id: string, steps: Step[]): Promise<void> {
  const s = await p.load(id);
  if (s.status !== "waiting" || Date.now() < (s.deadline ?? Infinity)) return;
  s.status = "running"; s.dir = "back";                 // задкуємо, відкликаючи і cancelClaim
  await p.persist(s); await drive(p, id, steps);
}
```
```py
import time
class WaitingForHuman(Exception):
    def __init__(self, until): self.until = until
DAY = 86_400

async def wait_for_owner(ctx):
    await post_claim_invite(ctx["home_id"], ctx["idem_key"])   # запросити (ідемпотентно)
    if await claim_accepted(ctx["home_id"]):
        return                                                 # уже підтвердили → завершено
    raise WaitingForHuman(time.time() + 7 * DAY)               # ще ні → паркуємось

async def on_claim(p, sid, steps):                             # підтвердили → уперед
    s = await p.load(sid)
    if s.status != "waiting": return                           # пізній клац — тиша
    s.status = "running"; await p.persist(s); await drive(p, sid, steps)

async def on_claim_deadline(p, sid, steps):                    # строк вийшов → розворот
    s = await p.load(sid)
    dl = s.deadline if s.deadline is not None else float("inf")   # None ≠ 0: не даємо «or» з'їсти нуль
    if s.status != "waiting" or time.time() < dl: return
    s.dir = "back"; s.status = "running"                       # cursor лишається на awaitClaim
    await p.persist(s); await drive(p, sid, steps)
```
:::

## Тест-ін'єкція: дві долі, доведені

Тепер — те, заради чого будувалося все. Збудуємо фейковий світ: журнал викликів, лічильник спрацювань, інжектор збою (`faults[name]` — скільки перших разів крок падає) і сховище в пам'яті, де «транзакція» атомарна тривіально. Кроки в тесті — ті самі за родом, але їхні дії інструментовані, тож ми **бачимо** і порядок, і кількість.

:::tabs
```ts
import { describe, it, expect } from "vitest";

function makeWorld(faults: Record<string, number>, claimAccepted = true) {
  const log: string[] = [], fired: Record<string, number> = {}, seen = new Set<string>();
  const box = { alerted: null as string | null };

  const act = (name: string) => async (_c: Ctx) => {      // рахує й падає перші faults[name] разів
    fired[name] = (fired[name] ?? 0) + 1;
    if (fired[name] <= (faults[name] ?? 0)) { log.push(name + "✗"); throw new Error("збій " + name); }
    log.push(name);
  };
  const waitOrPark = async (_c: Ctx) => {
    log.push("postInvite");
    if (!claimAccepted) throw new WaitingForHuman(0);      // паркуємось; 0 → одразу «протерміновано»
    log.push("accepted");
  };

  const S: Step[] = [
    { name: "freeze",          kind: "compensatable", run: act("freeze"),        compensate: act("unfreeze") },
    { name: "revokeAccess",    kind: "compensatable", run: act("revokeOldKeys"), compensate: act("restoreOldKeys") },
    { name: "awaitClaim",      kind: "compensatable", run: waitOrPark,           compensate: act("cancelClaim") },
    { name: "transferAndWipe", kind: "pivot",         run: act("transferAndShred") },
    { name: "rebindDevices",   kind: "retriable",     run: act("reissueCerts") },
    { name: "openBilling",     kind: "retriable",     run: act("switchBilling") },
    { name: "welcome",         kind: "retriable",     run: act("notifyNewOwner") },
  ];

  const db = new Map<string, Saga>();
  const clone = (s: Saga) => structuredClone(s);
  const ports: Ports = {
    load:   async (id) => clone(db.get(id)!),
    persist:async (s)  => void db.set(s.id, clone(s)),
    txn:    async (fn) => fn({}),                          // у пам'яті транзакція атомарна тривіально
    seen:   async (_t, k) => seen.has(k),
    mark:   async (_t, k) => void seen.add(k),
    saveIn: async (_t, s) => void db.set(s.id, clone(s)),
    outbox: async () => {},                                // подію ковтаємо — тут перевіряємо стан
    alert:  async (s) => void (box.alerted = s.id),
  };
  db.set("h1", { id: "h1", homeId: "home-1", cursor: 0, dir: "forward", status: "running", attempts: 0 });
  return { S, ports, log, fired, box };
}

const COMPS = ["cancelClaim", "restoreOldKeys", "unfreeze"];

describe("дві невдачі — дві долі", () => {
  it("ДО півота: компенсації у ЗВОРОТНОМУ порядку, чисте скасування, півот не чіпано", async () => {
    const w = makeWorld({}, /*claimAccepted*/ false);
    let saga = await drive(w.ports, "h1", w.S);            // дійде до awaitClaim і запаркується
    expect(saga.status).toBe("waiting");
    await onClaimDeadline(w.ports, "h1", w.S);             // витримка вичерпана

    saga = await w.ports.load("h1");
    expect(saga.status).toBe("aborted");                                  // чисте скасування
    expect(w.log.filter((x) => COMPS.includes(x))).toEqual(COMPS);        // рівно зворотний порядок
    expect(w.fired["transferAndShred"]).toBeUndefined();                  // ПІВОТ так і не настав
  });

  it("ПІСЛЯ півота (минуще): повтори до успіху, ЖОДНОЇ компенсації", async () => {
    const w = makeWorld({ switchBilling: 2 });            // білінг падає двічі, тоді встає
    const saga = await drive(w.ports, "h1", w.S);
    expect(saga.status).toBe("done");
    expect(w.fired["switchBilling"]).toBe(3);             // 2 падіння + 1 успіх
    expect(w.fired["transferAndShred"]).toBe(1);          // півот стався
    expect(w.log.some((x) => COMPS.includes(x))).toBe(false);            // нічого не відкочено
  });

  it("ПІСЛЯ півота (затяте): повтори вичерпано → DLQ і сигнал людині, без відкату", async () => {
    const w = makeWorld({ switchBilling: 999 });          // білінг лежить назавжди
    const saga = await drive(w.ports, "h1", w.S);
    expect(saga.status).toBe("stuck");                    // застрягло → мертва черга
    expect(w.box.alerted).toBe("h1");                     // людину покликано
    expect(w.fired["switchBilling"]).toBe(MAX_ATTEMPTS + 1);
    expect(w.fired["transferAndShred"]).toBe(1);          // передане лишається переданим
    expect(w.log.some((x) => COMPS.includes(x))).toBe(false);           // нічого не відкочено
  });

  it("КРАХ на терміналі: курсор за останнім кроком, статус іще 'running' → підйом завершує в 'done', без DLQ", async () => {
    const w = makeWorld({});
    // Щілина: остання транзакція вже посунула cursor ЗА останній крок (applyStep закомітив),
    // але p.persist(status='done') не встиг — машину смикнули з розетки саме тут.
    await w.ports.persist({ id: "h1", homeId: "home-1", cursor: w.S.length, dir: "forward", status: "running", attempts: 0 });
    const saga = await drive(w.ports, "h1", w.S);
    expect(saga.status).toBe("done");     // підйом дочитав термінал із самого курсора
    expect(w.box.alerted).toBeNull();     // сагу НЕ здано в DLQ — вона таки завершилась
    expect(w.log).toEqual([]);            // жодного кроку не перезапущено
  });
});
```
```py
import copy, pytest

def make_world(faults, claim_accepted=True):
    log, fired, seen, box = [], {}, set(), {"alerted": None}

    def act(name):
        async def _a(_ctx):                               # рахує й падає перші faults[name] разів
            fired[name] = fired.get(name, 0) + 1
            if fired[name] <= faults.get(name, 0):
                log.append(name + "✗"); raise RuntimeError("збій " + name)
            log.append(name)
        return _a

    async def wait_or_park(_ctx):
        log.append("post_invite")
        if not claim_accepted:
            raise WaitingForHuman(0)                       # паркуємось; 0 → одразу «протерміновано»
        log.append("accepted")

    S = [
        Step("freeze",        Kind.COMPENSATABLE, act("freeze"),        act("unfreeze")),
        Step("revoke_access", Kind.COMPENSATABLE, act("revoke_keys"),   act("restore_keys")),
        Step("await_claim",   Kind.COMPENSATABLE, wait_or_park,         act("cancel_claim")),
        Step("transfer_wipe", Kind.PIVOT,         act("transfer_shred")),
        Step("rebind",        Kind.RETRIABLE,     act("reissue_certs")),
        Step("billing",       Kind.RETRIABLE,     act("switch_billing")),
        Step("welcome",       Kind.RETRIABLE,     act("notify")),
    ]

    db = {}
    class Tx: ...
    class C:
        async def __aenter__(self): return Tx()
        async def __aexit__(self, *a): return False
    class P(Ports):
        async def load(self, i): return copy.deepcopy(db[i])
        async def persist(self, s): db[s.id] = copy.deepcopy(s)
        def txn(self): return C()                          # у пам'яті атомарна тривіально
        async def seen(self, _t, k): return k in seen
        async def mark(self, _t, k): seen.add(k)
        async def save_in(self, _t, s): db[s.id] = copy.deepcopy(s)
        async def outbox(self, _t, ev): pass
        async def alert(self, s, *a): box["alerted"] = s.id
    db["h1"] = Saga(id="h1", home_id="home-1")
    return S, P(), log, fired, box

COMPS = ["cancel_claim", "restore_keys", "unfreeze"]

@pytest.mark.asyncio
async def test_before_pivot_clean_abort():
    S, p, log, fired, box = make_world({}, claim_accepted=False)
    saga = await drive(p, "h1", S)                         # дійде до await_claim і запаркується
    assert saga.status == "waiting"
    await on_claim_deadline(p, "h1", S)                    # витримка вичерпана
    saga = await p.load("h1")
    assert saga.status == "aborted"                                       # чисте скасування
    assert [x for x in log if x in COMPS] == COMPS                        # рівно зворотний порядок
    assert "transfer_shred" not in fired                                  # ПІВОТ не настав

@pytest.mark.asyncio
async def test_after_pivot_transient_retries():
    S, p, log, fired, box = make_world({"switch_billing": 2})
    saga = await drive(p, "h1", S)
    assert saga.status == "done"
    assert fired["switch_billing"] == 3                    # 2 падіння + 1 успіх
    assert fired["transfer_shred"] == 1                    # півот стався
    assert not any(x in COMPS for x in log)                # нічого не відкочено

@pytest.mark.asyncio
async def test_after_pivot_stuck_to_dlq():
    S, p, log, fired, box = make_world({"switch_billing": 999})
    saga = await drive(p, "h1", S)
    assert saga.status == "stuck"                          # застрягло → мертва черга
    assert box["alerted"] == "h1"                          # людину покликано
    assert fired["switch_billing"] == MAX_ATTEMPTS + 1
    assert fired["transfer_shred"] == 1                    # передане лишається переданим
    assert not any(x in COMPS for x in log)                # нічого не відкочено

@pytest.mark.asyncio
async def test_crash_at_terminal_resolves_done():
    S, p, log, fired, box = make_world({})
    # Щілина: остання транзакція вже посунула cursor за останній крок,
    # але persist(status="done") не встиг — крах саме тут.
    await p.persist(Saga(id="h1", home_id="home-1", cursor=len(S)))
    saga = await drive(p, "h1", S)
    assert saga.status == "done"      # підйом дочитав термінал із курсора
    assert box["alerted"] is None     # у DLQ не здавали — сага завершилась
    assert log == []                  # жодного кроку не перезапущено
```
:::

Придивись до першого тесту: він не перевіряє «сага скасувалась» абстрактно — він пришпилює **точний порядок** компенсацій `["cancelClaim", "restoreOldKeys", "unfreeze"]`, дзеркальний порядку, в якому кроки робилися. Постав компенсації не так — і рівність упаде. І він вимагає, щоб `transferAndShred` **не спрацював жодного разу**: доки збій ліворуч від півота, дім не переходить із рук у руки навіть на мить. Другий і третій тести стережуть протилежний бік: `transferAndShred` спрацював рівно раз, і після нього **жодна** компенсація не побігла — тільки повтори (`switchBilling` тричі, аж поки встав) або, коли він лежить затято, тихий перехід у `stuck` із сигналом людині. А четвертий тест б'є вже не збоєм кроку, а **крахом**: піднімає сагу рівно в терміналі щілини — курсор уже за останнім кроком, статус іще `running` — і вимагає, щоб вона встала `done`, нікого не смикнувши; так пришпилено крахостійкість самого **завершення**, того шва, що його закриває сторож на вході. Чотири тести — і дві долі саги разом із її кінцем стають не обіцянкою в прозі, а червоним чи зеленим CI.

## Складність і пастки

Оркестратор стрункий, а зламати його легко — і майже завжди на одному з трьох знайомих місць.

**Компенсація, що сама падає.** Найпідступніше. Ти впевнено відкочуєш до півота — і раптом `restoreOldKeys` кидає помилку: контекст ідентичності недоступний. Наївний цикл на цьому просто зупиниться, лишивши сагу напіввідкоченою — гірше за будь-який із двох чесних кінців. Тому компенсація **не привілейована**: вона така сама дія, що доставляється щонайменше раз, тож мусить бути **ідемпотентна** (тому в нас ключ і на напрям `back`) і сама **повторювана**. У нашій машині невдала компенсація не рухає курсор назад — отже, наступний такт спробує ту саму компенсацію знову, з тим самим ключем; а якщо вона застрягла надовго, зворотний бік теж заслуговує на **мертву чергу** й людину. Компенсацію, яку не можна повторити, треба проєктувати так само сторожко, як і незворотний крок.

**Неідемпотентний крок.** Уся конструкція `applyStep` тримається на одній обіцянці: `run` можна пустити двічі без подвоєння ефекту. Забудь про це в `switchBilling` — і повтор після півота виставить **другий** рахунок, а дубль доставки `revokeAccess` двічі відкличе доступ. Ключ ідемпотентності — це половина ліків (він відсіює повтор на нашому боці), але друга половина мусить жити **в контексті**: той бік дедупить за `idemKey`, який ми йому передали. Крок, чий контекст не вміє дедупити, — не «майже ідемпотентний», а **бомба**, і повторювати його наосліп не можна; або зроби його контекст ідемпотентним, або не став його в повторювану зону.

**Півот, поставлений не там.** Найдорожча помилка, бо вона тиха, поки не вдарить. Постав `transferAndShred` **зарано** — скажімо, перед `awaitClaim` — і збій очікування опиниться вже **після** півота: система чесно повторюватиме… стирання персонального, якого не можна ні повторити (воно зроблене), ні відкотити (воно незворотне). Дім завис проданим, хоча ніхто його не приймав. Постав його **запізно** — і тягтимеш ризик відкату там, де він уже безсенсовний. Лінія півота — не механіка, а [найдорожче рішення саги](guide:progarch/what-makes-irreversible): пройди кроки й спитай кожен «це я зможу відкотити?»; перший чесний «ні» — і є твій півот, усе зворотне збери **перед** ним, усе обов'язкове — **після**. Наш `tick` лише виконує це рішення; **прийняти** його — досі твоя, людська, робота.

Отже, кістяк із статті лишився впізнаваним — той самий цикл, той самий рід кроку, що хилить на невдачі. Ми не додали йому розуму, ми додали йому **пам'ять і чесність**: винесли стан у сховище, замкнули просування з подією в одну транзакцію, дали кожному кроку ключ проти повтору, а зоні після півота — відступ і мертву чергу замість наївного відкату. І, найважливіше, ми пришпилили тестом рівно ту асиметрію, довкола якої збудовано всю сагу: до півота — назад до чистого нуля, після — тільки вперед, у крайньому разі руками людини.
