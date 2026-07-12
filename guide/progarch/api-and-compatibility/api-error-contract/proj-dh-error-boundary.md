# ⚙️ Харнес межі помилок DH: одна таблиця, з якої родиться і відповідь, і тест

Крок лишив на столі повний обробник — з конвертом Problem Details, кореляційним id, `Retry-After` і **контрактним тестом, що пришпилює форму помилки**. Начерк у статті вже показав кістяк: ланцюжок `if err instanceof …`, дві доменні помилки, гілка «усе інше» під сірий `500`. Для двох класів той ланцюжок бездоганний. Але справжній API дому має їх більше — `DeviceNotFound`, `DeviceUnavailable`, `InvalidCommand`, `RateLimited`, — і кожен новий `if` — це ще одне місце, де хтось колись змінить статус чи перейменує `code`, а тест про це не дізнається. Зберімо харнес так, щоб цього статися **не могло**.

Головний хід — один, і він визначає все решта: **зробити каталог помилок даними, а не кодом.** Один рядок таблиці на клас збою — статус, стабільний `code`, заголовок, ознака повторюваності. Тоді обробник стає **пошуком** у цій таблиці, контрактний тест **обходить ту саму таблицю**, а публічний каталог кодів із неї ж і генерується. «Одне місце перекладу», яким тіштся стаття, стає буквальним: рядок таблиці — єдине джерело, а рантайм, тест і документація — три його читачі, які фізично не можуть розійтися.

Одразу вмовмося, чого тут не буде, щоб не переказувати вже пройдене. Теорії Problem Details, різниці `code` проти `detail`, трьох рішень клієнта й правил еволюції кодів — усе це в статті й у книзі; тут я на них лише **спираюся**. Буде рівно харнес: таблиця, обробник, під'єднання до фреймворку, безпечне додавання коду й контрактний тест, який тримає форму.

## Задача: чотири класи збою, один конверт, і тест, що не дасть формі поїхати

Ось що харнес мусить робити. Знизу, крізь шари, підіймаються **чотири** доменні помилки — рівно ті, що вже жили у внутрішньому коді дому. На межі API кожна мусить стати конвертом [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) з правильним статусом, стабільним машинним `code`, людським `detail`, а де доречно — ознакою `retryable`, заголовком `Retry-After` і, для кривої команди, вказівкою на поле-винуватця. І кожна несе `requestId` — той самий кореляційний id, що ляже в журнал.

| Доменна помилка | Статус | `code` | Що ще в конверті |
|---|---|---|---|
| `DeviceNotFound` | `404` | `device_not_found` | — (не повторювати) |
| `DeviceUnavailable` | `503` | `device_unavailable` | `retryable`, `Retry-After` |
| `InvalidCommand` | `400` | `invalid_command` | `field` — яке поле не так |
| `RateLimited` | `429` | `rate_limited` | `retryable`, `Retry-After` |
| *усе інше* | `500` | `internal` | непрозоро, лише `requestId` |

П'ятий рядок — не помилка домену, а **баг у нашому коді**: те, чого ми не передбачили. З ним на межі чинять протилежно до внутрішнього «впасти голосно» — назовні непрозорий `500`, а весь стек лишається вдома.

І поверх усього — **контрактний тест**, що для кожного класу пришпилює `статус + code + форму конверта`, аби CI червонів на будь-яку ненавмисну зміну. Ось тут і криється справжня складність, яку начерк оминув: якщо обробник і тест — це **два окремі рукописні переліки** очікуваних форм, вони неминуче розійдуться. Хтось поправить статус у обробнику й забуде тест; або поправить тест під баг і замаскує поломку. Дві правди про одну форму гниють нарізно. Щоб тест справді сторожив контракт, він мусить читати **те саме джерело**, що й обробник. Звідси й уся конструкція.

## Ідея: каталог помилок як єдине джерело правди

Начерків `if err instanceof DeviceNotFound … if err instanceof DeviceUnavailable …` — це таблиця, перевдягнена в код. Кожна гілка каже одне: «цей клас → цей статус, цей `code`, отака форма». Ланцюжок `if`-ів розсипає цю таблицю по тілу функції, де її не можна ні обійти циклом, ні звірити цілком. Тож зберімо її назад **у дані** — масив рядків, по одному на клас:

```text
DeviceNotFound     →  404 · device_not_found
DeviceUnavailable  →  503 · device_unavailable · retryable · Retry-After
InvalidCommand     →  400 · invalid_command · + поле-винуватець
RateLimited        →  429 · rate_limited · retryable · Retry-After
```

Щойно контракт став таблицею, обробник худне до трьох рухів: **знайди** рядок за класом помилки; якщо знайшовся — **збудуй** конверт із рядка плюс тих дрібниць, що залежать від конкретного випадку; якщо ні — це баг, іди в гілку редакції. А головне — та сама таблиця тепер годує трьох різних читачів, і в цьому вся сила задуму.

![Реєстр помилок у центрі як таблиця-дані, з якої три стрілки ведуть до трьох читачів: handler toProblem у рантаймі будує з неї конверт application/problem+json; контрактний тест обходить її ж і робить golden-знімок, що червоніє на зміну форми; публічний каталог кодів і type-URL теж походить із неї](/guide/progarch/api-and-compatibility/api-error-contract/img/one-table.svg)
*Реєстр — єдине джерело правди про форму помилок. Рантайм будує з нього відповідь, контрактний тест знімає з нього еталон, документація його ж і публікує. Три читачі однієї таблиці не можуть розійтися, бо таблиця одна.*

> 🔧 **Навіщо це.** Поки контракт помилки живе кодом, «додати клас» і «звірити форму» — дві незалежні дії над двома різними місцями, і між ними завжди щілина, куди провалюється поломка. Коли контракт — це дані, «додати клас» стає **рядком у таблиці**, а «звірити форму» — **обходом тієї самої таблиці**. Тест не має власного уявлення про те, які помилки існують: він питає реєстр. Тому клас, доданий у рантайм, не може лишитися неперевіреним — він одразу потрапляє в цикл тесту.

Одне лишається **поза** таблицею — і навмисно. Кореляційний `requestId` не є властивістю класу помилки; він народжується на кожен запит окремо й мусить бути **той самий** у трьох місцях: у рядку журналу, у заголовку відповіді й у тілі конверта. Це той місток від єдиного запису в лозі до людини з екраном, який стаття назвала суттю дієвої помилки; тут ми його просто протягнемо крізь код. Це рівно та [спостережність, наведена на межу](guide:progarch/observability-as-testability): один запит — один id — один слід, який видно і зсередини, і ззовні.

## Робочий код

Домен тут — звичайний бекенд-ендпоінт: помилка, статус, JSON-тіло, заголовки. Основна валюта модуля — TypeScript на Node поряд із Python, тож даю обидві; там, де логіка чиста й переноситься дослівно, тримаю їх вкладками.

### Каталог як дані плюс доменні помилки

Спершу — самі помилки (ті самі, що підіймалися крізь шари) і **реєстр**: рядок на клас. Зверни увагу, чого в рядку **нема**: людського `detail`, значення `Retry-After` для ліміту й поля-винуватця — усе це залежить від конкретного випадку, не від класу, тож живе в самому винятку, а не в таблиці.

:::tabs
```ts
// доменні помилки — ті самі, що впираються в межу HTTP знизу
abstract class DomainError extends Error {}
class DeviceNotFound    extends DomainError { constructor(public id: string) { super("device not found"); } }
class DeviceUnavailable extends DomainError { constructor(public id: string) { super("device offline"); } }
class InvalidCommand    extends DomainError { constructor(public field: string, public reason: string) { super("invalid command"); } }
class RateLimited       extends DomainError { constructor(public retryAfterS: number) { super("rate limited"); } }

// рядок каталогу = контракт ОДНОГО класу, як дані
interface Row {
  status: number;      // HTTP-статус
  code: string;        // стабільний машинний ярлик — НЕ міняється ніколи
  title: string;       // короткий людський заголовок (RFC 9457 title)
  retryable?: boolean; // чи має сенс повторювати
  retryAfterS?: number;// фіксована пауза, коли вона стала для класу
}

// КЛЮЧ — сам клас (посилання на конструктор), а не рядок-назва:
// стійке до мініфікації, яка перейменувала б err.name.
const CATALOG = new Map<Function, Row>([
  [DeviceNotFound,    { status: 404, code: "device_not_found"   , title: "Пристрій не знайдено" }],
  [DeviceUnavailable, { status: 503, code: "device_unavailable" , title: "Пристрій тимчасово недоступний", retryable: true, retryAfterS: 5 }],
  [InvalidCommand,    { status: 400, code: "invalid_command"    , title: "Некоректна команда" }],
  [RateLimited,       { status: 429, code: "rate_limited"       , title: "Забагато запитів", retryable: true }],
]);
```
```py
from dataclasses import dataclass

# доменні помилки — ті самі, що впираються в межу HTTP знизу
class DomainError(Exception): ...
class DeviceNotFound(DomainError):
    def __init__(self, id): self.id = id
class DeviceUnavailable(DomainError):
    def __init__(self, id): self.id = id
class InvalidCommand(DomainError):
    def __init__(self, field, reason): self.field, self.reason = field, reason
class RateLimited(DomainError):
    def __init__(self, retry_after_s): self.retry_after_s = retry_after_s

@dataclass(frozen=True)
class Row:                      # контракт ОДНОГО класу, як дані
    status: int
    code: str                   # стабільний машинний ярлик — НЕ міняється ніколи
    title: str
    retryable: bool = False
    retry_after_s: int | None = None

# КЛЮЧ — сам клас (тип), а не рядок-назва
CATALOG: dict[type, Row] = {
    DeviceNotFound:    Row(404, "device_not_found",   "Пристрій не знайдено"),
    DeviceUnavailable: Row(503, "device_unavailable", "Пристрій тимчасово недоступний", retryable=True, retry_after_s=5),
    InvalidCommand:    Row(400, "invalid_command",    "Некоректна команда"),
    RateLimited:       Row(429, "rate_limited",       "Забагато запитів", retryable=True),
}
```
:::

### Одне місце перекладу: `toProblem`

Тепер серце харнесу. Знайшли рядок — будуємо конверт: `type` (URL, виведений із `code`), `title`, `status`, `code`, авторський `detail`, `requestId`, а далі домальовуємо повторюваність і випадкові дрібниці. Не знайшли — гілка редакції: **лог раз, тут**, зі стеком, а назовні непрозорий `500`.

:::tabs
```ts
const BASE = "https://api.dh.io/errors";
const CT = "application/problem+json";

interface Problem { status: number; headers: Record<string, string>; body: Record<string, unknown>; }

// detail — АВТОРСЬКИЙ текст на випадок, ніколи не String(err):
// сире err.message могло б винести назовні нутрощі нижнього шару.
function detailFor(err: DomainError): string {
  if (err instanceof DeviceNotFound)    return `Пристрою ${err.id} немає або він не ваш.`;
  if (err instanceof DeviceUnavailable) return "Давач не відповідає, спробуйте за кілька секунд.";
  if (err instanceof InvalidCommand)    return `Поле «${err.field}»: ${err.reason}.`;
  if (err instanceof RateLimited)       return "Забагато запитів, зачекайте перед повтором.";
  return "Помилка.";
}

function toProblem(err: unknown, reqId: string, opts = { exposeInternals: false }): Problem {
  const row = err instanceof Error ? CATALOG.get(err.constructor) : undefined;

  if (row && err instanceof DomainError) {
    const headers: Record<string, string> = { "Content-Type": CT };
    const body: Record<string, unknown> = {
      type: `${BASE}/${row.code.replace(/_/g, "-")}`,   // device_not_found → …/device-not-found
      title: row.title,
      status: row.status,
      code: row.code,                                   // машинний ярлик
      detail: detailFor(err),                           // людський текст
      requestId: reqId,                                 // кореляційний id — той самий, що в журналі
    };
    if (row.retryable) {
      body.retryable = true;
      // фіксована пауза — з рядка; динамічна (ліміт) — із самого винятку
      const ra = err instanceof RateLimited ? err.retryAfterS : row.retryAfterS;
      if (ra !== undefined) headers["Retry-After"] = String(ra);
    }
    if (err instanceof InvalidCommand) body.field = err.field; // яке поле не так
    return { status: row.status, headers, body };
  }

  // ── гілка «усе інше»: це БАГ, а не факт світу ──
  log.error({ reqId, err });                            // лог РАЗ, саме тут, зі стеком — ВДОМА
  const body: Record<string, unknown> = {
    type: "about:blank",                                // «нічого понад статус» (RFC 9457 §4.2.1)
    title: "Внутрішня помилка",
    status: 500,
    code: "internal",
    detail: "Сталася непередбачена помилка.",
    requestId: reqId,
  };
  if (opts.exposeInternals) body.debug = String(err instanceof Error ? err.stack : err); // ЛИШЕ dev
  return { status: 500, headers: { "Content-Type": CT }, body };
}
```
```py
BASE = "https://api.dh.io/errors"
CT = "application/problem+json"

def _detail(err: DomainError) -> str:
    # АВТОРСЬКИЙ текст, ніколи не str(err): сире повідомлення винесло б нутрощі назовні
    if isinstance(err, DeviceNotFound):    return f"Пристрою {err.id} немає або він не ваш."
    if isinstance(err, DeviceUnavailable): return "Давач не відповідає, спробуйте за кілька секунд."
    if isinstance(err, InvalidCommand):    return f"Поле «{err.field}»: {err.reason}."
    if isinstance(err, RateLimited):       return "Забагато запитів, зачекайте перед повтором."
    return "Помилка."

def to_problem(err, req_id, expose_internals=False):
    row = CATALOG.get(type(err))                          # точний тип; чужий підклас впаде в default

    if row is not None and isinstance(err, DomainError):
        headers = {"Content-Type": CT}
        body = {
            "type": f"{BASE}/{row.code.replace('_', '-')}",
            "title": row.title,
            "status": row.status,
            "code": row.code,
            "detail": _detail(err),
            "requestId": req_id,                          # той самий id, що в журналі
        }
        if row.retryable:
            body["retryable"] = True
            ra = err.retry_after_s if isinstance(err, RateLimited) else row.retry_after_s
            if ra is not None:
                headers["Retry-After"] = str(ra)
        if isinstance(err, InvalidCommand):
            body["field"] = err.field
        return row.status, headers, body

    # ── гілка «усе інше»: БАГ, не факт світу ──
    log.error("unhandled", extra={"req_id": req_id}, exc_info=err)   # лог РАЗ, тут, зі стеком
    body = {
        "type": "about:blank",                            # «нічого понад статус» (RFC 9457 §4.2.1)
        "title": "Внутрішня помилка",
        "status": 500,
        "code": "internal",
        "detail": "Сталася непередбачена помилка.",
        "requestId": req_id,
    }
    if expose_internals:
        import traceback
        body["debug"] = "".join(traceback.format_exception(err))     # ЛИШЕ dev
    return 500, {"Content-Type": CT}, body
```
:::

Дві чесні дрібниці варті слова, бо вони показують межу самої ідеї «все в таблицю». `Retry-After` для `RateLimited` і поле для `InvalidCommand` **не** в реєстрі — і не тому, що я полінувався, а тому, що вони залежать від конкретного випадку, не від класу: ліміт скидається через різний час, криве поле щоразу інше. Статичний рядок таблиці описує те, що спільне для класу; те, що народжується з конкретного винятку, лишається у винятку. Реєстр — джерело **форми**, а не кожного байта відповіді.

А тепер — гілка редакції, серце всієї безпеки. Подивімося, що вона робить, на двох дротяних відповідях поряд. Чесний доменний збій:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/problem+json
Retry-After: 5

{"type":"https://api.dh.io/errors/device-unavailable","title":"Пристрій тимчасово недоступний",
 "status":503,"code":"device_unavailable","detail":"Давач не відповідає, спробуйте за кілька секунд.",
 "requestId":"a1b2c3","retryable":true}
```

І непередбачений баг — той самий конверт формою, але **порожній усередині**:

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/problem+json

{"type":"about:blank","title":"Внутрішня помилка","status":500,
 "code":"internal","detail":"Сталася непередбачена помилка.","requestId":"a1b2c3"}
```

Уся редакція — в тому, чого в другій відповіді **нема**: ні назви винятку, ні тексту помилки бази, ні шляху до файлу, ні рядка стека. Усе це пішло в журнал під тим самим `a1b2c3` — вдома, де його прочитає розробник, і нікуди більше.

![Неочікуваний виняток зі стеком і текстом SQL заходить у гілку default обробника; звідти вниз усе нутро — стек, SQL, назва винятку, reqId — іде в журнал вдома одним записом, а назовні крізь пунктирну стіну редакції проходить лише непрозорий конверт 500 з code:internal, загальним detail і requestId — і нічим більше](/guide/progarch/api-and-compatibility/api-error-contract/img/redaction-wall.svg)
*Гілка «усе інше» — це стіна редакції. Униз, у журнал, іде все: стек, SQL, назва винятку — під кореляційним id. Назовні проходить лише непрозорий `500` з тим самим id. Внутрішня деталь, що [просочилася б назовні](book:programming/coupling-cohesion), — це і подарунок атакувальнику, і, за законом Гайрама, [випадковий контракт, якого ти не хотів](guide:progarch/what-makes-irreversible/math-hyrum-law.md): пропустиш раз `NullPointerException: user.tier is null` — знайдеться клієнт, що зачепиться за цей рядок.*

### Під'єднання: один обробник на краю

Реєстр і `toProblem` — чисті функції, їх легко тестувати. Лишається пришити їх до фреймворку так, щоб **жоден** маршрут не проскочив повз межу зі своїм сирим `500`. У Express це обробник помилок (чотири аргументи), у FastAPI — глобальний `exception_handler`. Обидва роблять те саме: беруть кореляційний id, кличуть `toProblem`, віддають конверт і луною повертають id у заголовку.

:::tabs
```ts
import { randomUUID } from "node:crypto";
import type { Request, Response, NextFunction } from "express";

function errorBoundary(opts: { exposeInternals: boolean }) {
  return (err: unknown, req: Request, res: Response, _next: NextFunction) => {
    // id призначає ранній middleware на вході; тут лише читаємо той самий,
    // що вже стоїть на КОЖНОМУ рядку журналу цього запиту.
    const reqId = res.locals.reqId ?? req.header("X-Request-Id") ?? randomUUID();
    const { status, headers, body } = toProblem(err, reqId, opts);
    res.set(headers);
    res.set("X-Request-Id", reqId);          // той самий id — і в заголовку, і в тілі, і в лозі
    res.status(status).json(body);
  };
}

// у проді нутрощі закриті; лишити exposeInternals увімкненим у проді — пастка №1
app.use(errorBoundary({ exposeInternals: process.env.NODE_ENV !== "production" }));
```
```py
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

def install_error_boundary(app: FastAPI, expose_internals: bool) -> None:
    @app.exception_handler(Exception)            # ловить УСЕ, що долетіло до краю
    async def _boundary(request: Request, err: Exception):
        req_id = getattr(request.state, "req_id", None) \
            or request.headers.get("X-Request-Id") or str(uuid.uuid4())
        status, headers, body = to_problem(err, req_id, expose_internals)
        headers.pop("Content-Type", None)        # media_type виставить його сам
        headers["X-Request-Id"] = req_id
        return JSONResponse(status_code=status, content=body,
                            media_type="application/problem+json", headers=headers)

# install_error_boundary(app, expose_internals=settings.env != "production")
```
:::

### Додати новий код — безпечно

Продукт вводить новий стан: пристрій оновлює прошивку й на команду має відповідати новим `device_updating`. У таблично-даному харнесі це **один рядок**, і більше нічого в обробнику не міняється:

```ts
class DeviceUpdating extends DomainError { constructor(public id: string) { super("updating"); } }

// + один рядок у CATALOG — і все:
[DeviceUpdating, { status: 409, code: "device_updating", title: "Пристрій оновлюється",
                   retryable: true, retryAfterS: 10 }],
```

Обробник не чіпаємо: `retryable`+`retryAfterS` уже вміє загальна гілка, `detailFor` дописуємо одним рядком. А тепер — дзеркальна умова на боці клієнта, без якої «безпечно» не працює. Панель мусить читати множину кодів як **відкриту** — мати гілку `default` на будь-який незнаний код:

```js
// клієнт (панель) розбирає конверт помилки — перелік кодів ВІДКРИТИЙ
switch (problem.code) {
  case "device_unavailable":
  case "rate_limited":
    scheduleRetry(retryAfterSeconds(res));   // повторюване — назад через Retry-After
    break;
  case "device_not_found":
    forgetDevice();
    break;
  case "invalid_command":
    highlightField(problem.field);           // сервер сказав, ЯКЕ поле
    break;
  default:                                    // ← рятує від БУДЬ-ЯКОГО нового коду
    showGenericError(problem.detail);        // detail — для ока, не для гілок
}
```

Клієнт із цим `default` переживе твій `device_updating`: покаже загальне повідомлення й піде далі. Це не наша примха — це те, що [RFC 9457 §3.2 прямо вимагає](https://www.rfc-editor.org/rfc/rfc9457.html): «клієнти... **MUST ignore** будь-які розширення, яких не впізнають» — саме щоб типи помилок могли рости. Відкритий перелік кодів — стандартна обіцянка, і клієнт, що зробив вичерпний `switch` без `default`, порушує її **на своєму** боці.

І ось де окупається таблиця: додавши рядок, ти автоматично поповнив і те, що бачить **контрактний тест**. Його golden-знімок тепер має на один запис більше — і рев'юер у діфі бачить рівно нову форму, що їде на дріт. Додати код помилки стало **рецензованою зміною даних**, а не тихою правкою в надрах обробника.

### Контрактний тест, що пришпилює форму

Це те, заради чого будувалася вся конструкція. Тест робить три речі, і кожна ловить свій рід поломки.

**(а) Інваріанти конверта над усім каталогом.** Обходимо `CATALOG` — ту саму таблицю, що й рантайм, — і на кожен клас перевіряємо, що конверт валідний: статус у тілі дорівнює HTTP-статусу, `code` присутній і збігається з рядком, `requestId` відлунено, тип вмісту правильний, а повторюваний клас несе `Retry-After`. Цей цикл фізично покриває **кожен** зареєстрований клас — забудеш додати зразок для нового коду, і тест червоніє сам.

**(б) Golden-знімок форми.** На кожен клас — точний конверт, заморожений у файлі-еталоні (з нормалізованим `requestId`). Будь-яке перейменування `code`, зміна статусу, доданий чи прибраний ключ — і знімок розходиться, тест червоніє, а людина мусить **свідомо** благословити нову форму. Це буквально «пришпилити»: жодна дрібниця конверта не поїде мовчки.

**(в) Тест редакції.** Кидаємо сирий баг із соковитим нутром — текстом SQL, паролем, стеком — і вимагаємо, щоб назовні не просочилося **нічого** з цього, лише непрозорий конверт, і в прод-режимі — жодного поля `debug`.

:::tabs
```ts
import { describe, it, expect } from "vitest";

const FIXED = "req-TEST";  // кореляційний id нормалізуємо, щоб знімок був стабільний

// по одному зразку на клас; ключ — той самий code, що й у каталозі
const SAMPLES: Record<string, () => DomainError> = {
  device_not_found:   () => new DeviceNotFound("42"),
  device_unavailable: () => new DeviceUnavailable("42"),
  invalid_command:    () => new InvalidCommand("mode", "невідоме значення"),
  rate_limited:       () => new RateLimited(30),
};

describe("контракт помилок DH", () => {
  // (а) інваріанти — над УСІМА класами каталогу, не над рукописним списком
  it("кожен зареєстрований клас дає валідний конверт RFC 9457", () => {
    for (const row of CATALOG.values()) {
      const make = SAMPLES[row.code];
      expect(make, `нема зразка для ${row.code} — додай його`).toBeDefined();
      const p = toProblem(make(), FIXED);
      expect(p.status).toBe(row.status);
      expect(p.body.status).toBe(row.status);              // статус у тілі === HTTP-статус
      expect(p.body.code).toBe(row.code);                  // стабільний ярлик присутній
      expect(p.body.requestId).toBe(FIXED);                // кореляційний id відлунено
      expect(typeof p.body.detail).toBe("string");         // текст Є, але його ЗМІСТ не пришпилюємо
      expect(p.headers["Content-Type"]).toBe("application/problem+json");
      if (row.retryable) expect(p.headers["Retry-After"]).toBeDefined();
    }
  });

  // (б) golden-знімок — точна форма кожного класу; будь-яка зміна червонить CI
  it.each(Object.entries(SAMPLES))("форма %s пришпилена", (_code, make) => {
    expect(toProblem(make(), FIXED)).toMatchSnapshot();
  });

  // (в) редакція: сирий баг НЕ виносить нутрощів назовні
  it("непередбачений виняток → непрозорий 500 без нутрощів", () => {
    const boom = new Error("SQL: SELECT password FROM users WHERE id=1");
    boom.stack = "at db.query (secret.ts:42)\n" + (boom.stack ?? "");
    const p = toProblem(boom, FIXED);                      // прод-режим: expose off
    expect(p.status).toBe(500);
    expect(p.body.code).toBe("internal");
    expect(p.body.requestId).toBe(FIXED);
    expect(p.body).not.toHaveProperty("debug");            // у проді жодного стека
    expect(JSON.stringify(p)).not.toMatch(/SQL|password|secret\.ts|SELECT/);
  });
});
```
```py
import json, pytest

FIXED = "req-TEST"

SAMPLES = {
    "device_not_found":   lambda: DeviceNotFound("42"),
    "device_unavailable": lambda: DeviceUnavailable("42"),
    "invalid_command":    lambda: InvalidCommand("mode", "невідоме значення"),
    "rate_limited":       lambda: RateLimited(30),
}

# (а) інваріанти — над УСІМА класами каталогу
@pytest.mark.parametrize("row", list(CATALOG.values()), ids=lambda r: r.code)
def test_envelope_invariants(row):
    make = SAMPLES.get(row.code)
    assert make, f"нема зразка для {row.code} — додай його"
    status, headers, body = to_problem(make(), FIXED)
    assert status == row.status
    assert body["status"] == row.status            # статус у тілі === HTTP-статус
    assert body["code"] == row.code                # стабільний ярлик присутній
    assert body["requestId"] == FIXED              # кореляційний id відлунено
    assert isinstance(body["detail"], str)         # текст Є; його ЗМІСТ не пришпилюємо
    assert headers["Content-Type"] == "application/problem+json"
    if row.retryable:
        assert "Retry-After" in headers

# (б) golden-знімок точної форми (syrupy: assert == snapshot)
@pytest.mark.parametrize("code", list(SAMPLES), ids=list(SAMPLES))
def test_shape_pinned(code, snapshot):
    status, headers, body = to_problem(SAMPLES[code](), FIXED)
    assert {"status": status, "headers": headers, "body": body} == snapshot

# (в) редакція
def test_opaque_500_redacts():
    boom = RuntimeError("SQL: SELECT password FROM users WHERE id=1")
    status, headers, body = to_problem(boom, FIXED, expose_internals=False)
    assert status == 500
    assert body["code"] == "internal"
    assert body["requestId"] == FIXED
    assert "debug" not in body                     # у проді жодного стека
    wire = json.dumps({"h": headers, "b": body})
    for leak in ("SQL", "password", "SELECT"):
        assert leak not in wire
```
:::

Придивися до інваріантного циклу (а): він ітерує `CATALOG.values()`, тобто **ту саму таблицю**, з якої рантайм будує відповідь. Це і є вся хитрість. Тест не тримає власного переліку «які помилки бувають» — він питає реєстр. Тому додати клас у рантайм, забувши тест, **неможливо**: новий рядок одразу опиниться в циклі, і якщо для нього нема зразка `SAMPLES`, тест впаде з чесним «додай його». Дві правди, що гнили б нарізно, стали однією, а тест — її сторожем.

І ще тонкість, навмисна: у (а) ми перевіряємо, що `detail` — рядок, але **не** пришпилюємо його **зміст**. Це принципово. Людське повідомлення має лишатися вільним — його перекладають, переписують, роблять лагіднішим; якби тест зафіксував його текст, ми б самі собі зв'язали руки й перетворили змінне повідомлення на застиглий контракт. Пришпилюємо `code` і форму; текст лишаємо диханню. Тест кодує рівно ту межу, що її провів крок: машинне — камінь, людське — вода.

## Складність і пастки

Харнес стрункий, а обійти його захист легко — і майже завжди на одному з кількох знайомих місць.

**Стек у проді.** Найдорожча, бо це діра в безпеці. Два шляхи, якими нутрощі течуть назовні. Перший — лишити `exposeInternals`/`expose_internals` увімкненим у проді: тоді поле `debug` зі стеком їде кожному клієнтові. Тест редакції (в) стереже саме це — він ганяє `toProblem` у прод-режимі й вимагає відсутності `debug` і будь-яких внутрішніх рядків. Другий, підступніший — маршрут, що **проскочив повз** межу: незловлений виняток у місці, куди обробник помилок не дотягся, і фреймворк віддає **свій** дефолтний `500` зі стеком. Тому межа має бути одна на весь застосунок і ловити геть усе, а не стояти в кількох хендлерах вибірково. Правило з модуля меж тут лише твердне: [сире слово нижнього шару не сміє пройти назовні](book:programming/coupling-cohesion) — ні в даних, ні в помилці.

**Клієнт парсить людський `detail`.** Хтось на тому боці, кому забракло `code`, чіпляється регуляркою за текст `detail` — і тепер твоє «спробуйте за кілька секунд» не можна ні перекласти, ні переписати, не зламавши його. Свого боку ти цього не спиниш; але харнес робить максимум правильного: дає стабільний `code` й `field`, щоб машині **не було потреби** лізти в текст, і навмисно **не** пришпилює зміст `detail` у власному тесті, лишаючи його вільним. Golden-знімок при цьому чесно документує, що саме стабільне (`code`, `status`, форма), а що — ні (текст). Найбільше, що можна зробити для чужого коду, — не давати йому приводу спиратися на людське слово.

**Вичерпний `switch` без `default`.** Дзеркало попередньої, тільки на клієнті, і рівно та пастка, що ламає історію «додати код безпечно». Клієнт, який розібрав усі відомі коди й **не** поклав `default`, провалиться повз усі гілки на першому ж новому `device_updating`. Сервер цього не полагодить, але мусить: оголосити відкритість переліку в каталозі кодів (це буквально мова RFC 9457) і викочувати нові коди поступово. Відкритий перелік на вході — та сама поблажливість читача, що веде весь модуль сумісності: [нові коди можуть з'являтися — будь готовий до незнаних](guide:progarch/errors-through-layers).

**`detail`, що відлунює недовірений вхід.** Спокуса зробити повідомлення «кориснішим», вклавши в нього сирий рядок від користувача чи `str(err)`, — це і канал витоку нутрощів, і вектор ін'єкції в чужий UI. Тому `detailFor` збирає текст **сам**, з авторських шаблонів, а поле `field` для `InvalidCommand` береться не з довільного вводу, а з [перевіреного на межі](book:programming/defensive-programming) переліку відомих полів команди. У конверт іде лише те, що ти написав або звірив, — ніколи не те, що просто прилетіло.

**Дві правди, що розходяться.** Метапастка, задля якої й затівався таблично-даний дизайн. Щойно обробник кодує форму в `if`-ах, а тест — окремим рукописним списком очікувань, вони починають жити різним життям: одна правка тут, друга там, і золотий знімок «зелений», бо описує вже не те, що віддає рантайм. Ліки — структурні, а не дисциплінарні: **один реєстр, який читають обидва**. Не «не забувай синхронізувати тест із кодом», а «нема чого синхронізувати — джерело одне».

## Що дає цей харнес

Ми взяли начерк із трьох `if`-ів і зробили один структурний хід: винесли контракт помилки з коду **в дані**. Далі все стало на місця саме собою. Реєстр — рядок на клас — виявився єдиним джерелом, з якого рантайм будує конверт, контрактний тест знімає еталон, а публічний каталог кодів походить сам. `toProblem` схуднув до пошуку плюс редакції. Кореляційний `requestId` протягся крізь журнал, заголовок і тіло одним і тим самим числом — місток від запису в лозі до людини з екраном. А гілка «усе інше» стала стіною редакції: усе нутро — вдома, назовні непрозорий `500`.

І головне — те, чого начерк не міг дати. Додати код помилки стало **рецензованою зміною одного рядка даних**, чий ефект видно в діфі золотого знімка. Зламати форму стало **червоним CI**, бо тест обходить ту саму таблицю, що й обробник, і не має власної, застарілої правди про неї. Контракт помилки перестав бути тим, що випадково випало зі стека, і став тим, на що можна показати пальцем: ось таблиця, ось відповідь, ось тест, що не дасть їм розійтися. Саме про це й був увесь крок — тільки тепер це не принцип, а код, який червоніє, коли принцип порушено.
