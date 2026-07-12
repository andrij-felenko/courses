# ⚙️ Приймач вебхуків DH цілком: роут, робітник, звірка — і тест, що це доводить

## Задача

Ми вже знаємо всі чотири рефлекси приймача поокремо: перевір підпис, підтверди швидко, дедуп за id, звір із джерелом. Тепер зберімо їх у **один робочий вузол** — такий, що витримає рівно ту ніч, коли двері Соколів стояли навстіж, а застосунок казав «зачинено». І, головне, напишімо **тест, який це доводить**: програємо йому дубль тієї самої події, переставлені події й **загублену** подію під час простою — і побачимо на очах, що дедуп відкидає повтори, а звірка ловить пропущене.

Вузол складається з чотирьох деталей, і кожна відповідає за свою обіцянку:

- **Тонкий роут** — приймає POST, звіряє HMAC над сирими байтами, атомарно кладе подію в inbox і чергу, віддає `200` за десятки мілісекунд.
- **Робітник** — тягне чергу у своєму темпі, ідемпотентно оновлює твін, шле сповіщення, а отруйну подію відправляє в мертву чергу.
- **Звірка** — раз на кілька хвилин опитує API партнера й стягує твін до джерела правди, коли пуш пропав.
- **Тест-гарнес** — жене крізь вузол дублі, переставлені й загублені події й перевіряє, що ефект настає **рівно один раз**, а дрейф виправляється.

Мова тут — бекенд, тож приклади подаємо однаково на **TypeScript** (Node + Express + `pg`) і **Python** (FastAPI + `asyncpg`); база — PostgreSQL, бо саме її транзакції й `ON CONFLICT` роблять дедуп атомарним майже задарма.

## Ідея: одна транзакція на вході, ідемпотентність усередині

Уся конструкція тримається на одному непомітному рішенні: **позначка «цю подію бачено» і запис її в чергу мусять народитися разом — в одній транзакції.** Якщо їх розчепити (спершу позначити inbox, потім штовхнути в чергу), між двома записами є щілина, і якщо процес впаде саме там, подія лишиться **позначеною як бачена, але ніколи не обробленою** — а дедуп відтепер чесно ховатиме її повтори. Тиха вічна втрата, точнісінько того ґатунку, що осліпив застосунок Соколів. Тому inbox і черга — це один `BEGIN … COMMIT`.

Далі все нижче за течією зроблено **ідемпотентним**, тобто безпечним до повторення: робітник може взяти ту саму задачу двічі, звірка може прибути одночасно з пушем — і жодне з цього не подвоїть ефект, бо оновлення твіна захищене версією події. Ідемпотентність — не прикраса, а те, що дає нам право спокійно повторювати будь-що, коли ми не певні, чи дійшло.

![Зібраний вузол зліва направо: підписаний POST входить у тонкий роут, де inbox (INSERT … ON CONFLICT DO NOTHING) і запис у чергу jobs лежать усередині однієї транзакції — обидва записи або жоден, — і одразу летить ACK 200 за десятки мілісекунд. Робітник окремо тягне чергу під FOR UPDATE SKIP LOCKED, оновлює твін через upsert лише коли новіший seq, шле сповіщення тільки якщо твін справді змінився, а отруйну подію після N спроб зсуває в мертву чергу](/guide/progarch/nodes-webhooks-notifications/dh-webhook-consumer/img/pipeline.svg)

*Тонкий роут комітить inbox і чергу разом і зникає; робітник живе окремим темпом і подвоєння не боїться, бо кожен його крок ідемпотентний. Мертва черга ловить те, що не піддається обробці, щоб одна погана подія не спинила решту.*

## Схема: чотири маленькі таблиці

Почнімо з даних, бо на них тримається вся логіка. Чотири таблиці, кожна з однією роботою.

```sql
-- inbox: журнал уже прийнятих подій. PRIMARY KEY робить дедуп атомарним.
CREATE TABLE inbox (
  event_id    text PRIMARY KEY,
  received_at timestamptz NOT NULL DEFAULT now()
);

-- jobs: черга. Робітник бере рядок під FOR UPDATE SKIP LOCKED.
CREATE TABLE jobs (
  id        bigserial   PRIMARY KEY,
  event_id  text        NOT NULL,
  payload   jsonb       NOT NULL,
  attempts  int         NOT NULL DEFAULT 0,
  run_after timestamptz NOT NULL DEFAULT now()   -- коли задача знову «дозріє» після невдачі
);
CREATE INDEX jobs_ready ON jobs (run_after, id);

-- twin: остання відома правда про пристрій. seq — версія від джерела (проти переупорядкування).
CREATE TABLE twin (
  device_id  text        PRIMARY KEY,
  state      text        NOT NULL,
  seq        bigint      NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- dead_letter: подія, що не піддалась після N спроб. Лежить тут для очей людини.
CREATE TABLE dead_letter (
  id        bigserial   PRIMARY KEY,
  event_id  text        NOT NULL,
  payload   jsonb       NOT NULL,
  error     text        NOT NULL,
  failed_at timestamptz NOT NULL DEFAULT now()
);
```

Дві деталі схеми несуть увесь сенс. `event_id text PRIMARY KEY` в **inbox** — це наш дедуп: спроба вставити той самий id вдруге впирається в первинний ключ, і `ON CONFLICT DO NOTHING` тихо її ковтає (це і є [вхідна скринька](book:programming/inbox-pattern) — журнал бачених id, який робить приймач [ідемпотентним споживачем](book:programming/idempotent-consumers-deep)). А `seq bigint` у **twin** — версія події від джерела; саме вона дозволить пізнішій, але старішій за номером події не затерти новішу.

## Роут: сирі байти, підпис, і атомарний inbox + черга

Роут робить рівно три речі — і жодної зайвої. Перевіряє підпис над **точними отриманими байтами**. Розбирає тіло. І в **одній транзакції** позначає inbox та кладе в чергу. Усе — за десятки мілісекунд, задовго до провайдерського таймауту.

Чому саме сирі байти, а не зручний розібраний об'єкт — найкраще видно на числах. Порахуймо HMAC двічі: над байтами, як їх підписав партнер, і над тим самим об'єктом, який ми мовби розібрали й зібрали назад.

**Умова:** секрет `whsec_dh_acme_7Kq2p9`, позначка часу `t = 1752266580`, тіло — рівно 83 байти, як прийшли по дроту.

```
підписаний рядок = "1752266580." + <точні 83 байти тіла>
тіло = {"id":"evt_9f2a","type":"lock.state","device_id":"lock-42","state":"open","seq":41}
HMAC-SHA256(секрет, підписаний) =
  42f6be4ab9ed24ae5f65c55bb11417f6311a715e9e0147835548c8aff1e9c0d6

той самий об'єкт, розібраний і зібраний назад (пробіли після «:», ключі за абеткою):
{"device_id": "lock-42", "id": "evt_9f2a", "seq": 41, "state": "open", "type": "lock.state"}
HMAC-SHA256(секрет, "1752266580." + це) =
  4563c0c12efe8a57a5b5108c35574a9c234f57e31dba16a2fe411e5fb686e650
```

**Висновок:** той самий факт, той самий секрет — **два різні підписи**. Провайдер підписав перший рядок; якби ми звіряли з другого, чесний POST не пройшов би перевірку, і замок Соколів мовчав би не через зловмисника, а через наш власний `JSON.parse` → `stringify`. Тому verify() бере `rawBody` до будь-якого розбору, а веб-фреймворк ми змушуємо віддати нам саме байти (`express.raw` / `await req.body()`), а не готовий об'єкт.

:::tabs
```ts
import express from "express";
import { Pool } from "pg";
import { createHmac, timingSafeEqual } from "node:crypto";

const pool = new Pool();
const SECRET = process.env.ACME_WEBHOOK_SECRET!;

function verify(raw: Buffer, header: string): boolean {
  const parts = Object.fromEntries(header.split(",").map(kv => kv.split("=", 2)));
  const t = Number(parts.t);
  if (!t || Math.abs(Date.now() / 1000 - t) > 300) return false;   // застарілий → повтор, геть
  const signed = Buffer.concat([Buffer.from(`${t}.`), raw]);        // t + СИРІ байти
  const expected = createHmac("sha256", SECRET).update(signed).digest("hex");
  const a = Buffer.from(expected), b = Buffer.from(parts.v1 ?? "");
  return a.length === b.length && timingSafeEqual(a, b);            // звірка за СТАЛИЙ час
}

// Ядро роуту — чиста функція над (сирі байти, заголовок). Легко кликати з тесту.
export async function handleWebhook(raw: Buffer, sigHeader: string): Promise<number> {
  if (!verify(raw, sigHeader)) return 400;                 // хто ти? не той підпис — двері зачинені
  const event = JSON.parse(raw.toString());

  const cx = await pool.connect();
  try {
    await cx.query("BEGIN");                               // inbox і черга — В ОДНІЙ транзакції
    const ins = await cx.query(
      "INSERT INTO inbox(event_id) VALUES ($1) ON CONFLICT DO NOTHING", [event.id]);
    if (ins.rowCount === 1)                                // id новий → у чергу
      await cx.query("INSERT INTO jobs(event_id, payload) VALUES ($1, $2)",
        [event.id, event]);
    await cx.query("COMMIT");                              // позначка й задача народжуються разом
  } catch (e) {
    await cx.query("ROLLBACK");                            // нічого не позначено баченим
    return 500;                                            // провайдер повторить — це безпечно
  } finally {
    cx.release();
  }
  return 200;                                              // ACK за десятки мс
}

const app = express();
// HTTP-обгортка тонка — увесь сенс у handleWebhook, тому його й тестуємо.
app.post("/hooks/acme-lock", express.raw({ type: "*/*" }), async (req, res) =>
  res.sendStatus(await handleWebhook(req.body, req.header("X-Acme-Signature") ?? "")));
```
```py
import os, hmac, hashlib, time, json
from fastapi import FastAPI, Request, Response
import asyncpg

SECRET = os.environ["ACME_WEBHOOK_SECRET"].encode()

def verify(raw: bytes, header: str) -> bool:
    parts = dict(kv.split("=", 1) for kv in header.split(","))
    t = int(parts.get("t", 0))
    if not t or abs(time.time() - t) > 300:                # застарілий → повтор, геть
        return False
    signed = f"{t}.".encode() + raw                        # t + СИРІ байти
    expected = hmac.new(SECRET, signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, parts.get("v1", ""))   # звірка за СТАЛИЙ час

# Ядро роуту — чиста корутина над (сирі байти, заголовок, пул). Легко кликати з тесту.
async def handle_webhook(raw: bytes, sig_header: str, pool) -> int:
    if not verify(raw, sig_header):                        # хто ти? не той підпис — двері зачинені
        return 400
    event = json.loads(raw)
    try:
        async with pool.acquire() as cx:
            async with cx.transaction():                   # inbox і черга — В ОДНІЙ транзакції
                row = await cx.fetchrow(
                    "INSERT INTO inbox(event_id) VALUES ($1) "
                    "ON CONFLICT DO NOTHING RETURNING event_id", event["id"])
                if row is not None:                        # id новий → у чергу
                    await cx.execute("INSERT INTO jobs(event_id, payload) VALUES ($1, $2)",
                                     event["id"], json.dumps(event))
    except Exception:
        return 500        # транзакція відкотилась сама; нічого не позначено — повтор безпечний
    return 200                                             # ACK за десятки мс

app = FastAPI()

@app.post("/hooks/acme-lock")
async def receive(req: Request):
    code = await handle_webhook(await req.body(),
                                req.headers.get("x-acme-signature", ""),
                                req.app.state.pool)
    return Response(status_code=code)
```
:::

Тепер придивімося, як ця одна транзакція гасить одразу дві різні біди. Перша — **загублений `200`**: ми обробили POST, записали inbox і чергу, закомітили, але відповідь не доїхала до провайдера. Він не відрізнить це від невдачі й пришле той самий POST знову. Другого разу `INSERT … ON CONFLICT DO NOTHING` дає `rowCount = 0` — id уже в inbox, — ми **не** кладемо в чергу вдруге й спокійно відповідаємо `200`. Дубль поглинуто. Друга біда підступніша й показує, навіщо взагалі транзакція.

![Дві доріжки. Угорі «два окремі записи»: крок 1 позначає inbox «бачене», між кроками процес падає (CRASH до запису в чергу), крок 2 «створити задачу» не стається — на повтор inbox дає CONFLICT і подію пропущено; банер: подія позначена бачена, але ніколи не оброблена, дедуп тепер її ховає, втрата назавжди. Унизу «одна транзакція»: BEGIN inbox + jobs COMMIT — крах до COMMIT відкочує обидва й повтор безпечно робить обидва; крах після COMMIT лишає обидва, ACK згублено, повтор дає CONFLICT без дублю](/guide/progarch/nodes-webhooks-notifications/dh-webhook-consumer/img/atomic-inbox.svg)

*Розчепити позначку «бачене» і запис у чергу — значить лишити щілину, в яку подія провалюється назавжди: дедуп потім чесно ховає її повтори. Одна транзакція зшиває обидва записи так, що між ними немає куди впасти.* Це та сама причина, з якої запис у чергу [кладуть в одну транзакцію з бізнес-зміною](book:programming/outbox-pattern) — тільки дзеркально, на вході.

## Робітник: ідемпотентно, з версією проти переупорядкування

Роут поклав подію в чергу й зник. Тепер окремий робітник тягне чергу [фонових задач](book:programming/background-jobs) у власному темпі. Його серце — один SQL-запит на видачу задачі:

```sql
SELECT id, event_id, payload, attempts FROM jobs
 WHERE run_after <= now() ORDER BY id
   FOR UPDATE SKIP LOCKED LIMIT 1;
```

`FOR UPDATE` бере рядок під замок, щоб інший робітник його не взяв; `SKIP LOCKED` каже «зайняті кимось рядки просто пропускай, не чекай на них». Так десять робітників тягнуть чергу паралельно, не наступаючи один одному на п'яти й не блокуючись на одній повільній задачі. А `run_after <= now()` дає нам безкоштовний відкладений повтор: невдалу задачу ми відсунемо в майбутнє, і поки її час не настав, робітник її навіть не бачить.

Оновлення твіна — окрема тонкість. Події можуть [прийти не по порядку](guide:progarch/duplicates-and-reorder): «відчинено» (seq 5) обжене «зачинено» (seq 4), і якщо застосовувати сліпо за порядком прибуття, старіше «зачинено» затре свіже «відчинено» — знову брехня про двері. Лік — застосовувати подію, **лише якщо її seq новіший за той, що вже в твіні**. Один upsert робить і вставку нового пристрою, і захист від старіших подій, і повертає рядок **тільки якщо твін справді змінився** — а це рівно та умова, за якої варто слати сповіщення.

:::tabs
```ts
const MAX_ATTEMPTS = 5;
const VALID = new Set(["open", "closed"]);
let notify: (ev: any) => Promise<void> = async () => {};   // впорснемо в проді / у тесті
export const setNotifier = (fn: typeof notify) => { notify = fn; };

// Повертає true, ЛИШЕ якщо твін справді змінився (новий пристрій або новіший seq).
async function applyToTwin(cx: any, ev: any): Promise<boolean> {
  const r = await cx.query(
    `INSERT INTO twin(device_id, state, seq) VALUES ($1, $2, $3)
     ON CONFLICT (device_id) DO UPDATE
       SET state = EXCLUDED.state, seq = EXCLUDED.seq, updated_at = now()
       WHERE EXCLUDED.seq > twin.seq                 -- старіша подія НЕ перебиває новішу
     RETURNING device_id`,
    [ev.device_id, ev.state, ev.seq]);
  return r.rowCount === 1;
}

async function handleEvent(cx: any, ev: any): Promise<void> {
  if (!VALID.has(ev.state)) throw new Error(`невідомий стан: ${ev.state}`);  // отрута
  const changed = await applyToTwin(cx, ev);
  if (changed) await notify(ev);      // пуш ЛИШЕ на реальну зміну; notify — зі своїм дедупом
}

export async function processOnce(): Promise<boolean> {
  const cx = await pool.connect();
  let job: any;
  try {
    await cx.query("BEGIN");
    const { rows } = await cx.query(
      `SELECT id, event_id, payload, attempts FROM jobs
        WHERE run_after <= now() ORDER BY id
          FOR UPDATE SKIP LOCKED LIMIT 1`);
    if (rows.length === 0) { await cx.query("COMMIT"); return false; }
    job = rows[0];
    await handleEvent(cx, job.payload);               // твін + пуш
    await cx.query("DELETE FROM jobs WHERE id = $1", [job.id]);
    await cx.query("COMMIT");                          // зміна твіна й зняття з черги — разом
    return true;
  } catch (err) {
    await cx.query("ROLLBACK");                        // відкат УСЬОГО: твін не зачеплено
    await retryOrBury(job, err);                       // облік спроби — окремою транзакцією
    return true;
  } finally {
    cx.release();
  }
}

async function retryOrBury(job: any, err: unknown): Promise<void> {
  if (!job) return;
  const n = job.attempts + 1;
  if (n >= MAX_ATTEMPTS)                               // отрута — у мертву чергу, геть із jobs
    await pool.query(
      `WITH gone AS (DELETE FROM jobs WHERE id = $1 RETURNING event_id, payload)
       INSERT INTO dead_letter(event_id, payload, error)
       SELECT event_id, payload, $2 FROM gone`, [job.id, String(err)]);
  else                                                // ще спробуємо — експоненційний відступ
    await pool.query(
      `UPDATE jobs SET attempts = $1, run_after = now() + make_interval(secs => $2)
        WHERE id = $3`, [n, 2 ** n, job.id]);
}
```
```py
MAX_ATTEMPTS = 5
VALID = {"open", "closed"}
_notify = lambda ev: None            # впорснемо в проді / у тесті
def set_notifier(fn): 
    global _notify; _notify = fn

# Повертає True, ЛИШЕ якщо твін справді змінився (новий пристрій або новіший seq).
async def apply_to_twin(cx, ev) -> bool:
    row = await cx.fetchrow(
        """INSERT INTO twin(device_id, state, seq) VALUES ($1, $2, $3)
           ON CONFLICT (device_id) DO UPDATE
             SET state = EXCLUDED.state, seq = EXCLUDED.seq, updated_at = now()
             WHERE EXCLUDED.seq > twin.seq            -- старіша подія НЕ перебиває новішу
           RETURNING device_id""",
        ev["device_id"], ev["state"], ev["seq"])
    return row is not None

async def handle_event(cx, ev) -> None:
    if ev["state"] not in VALID:
        raise ValueError(f"невідомий стан: {ev['state']}")   # отрута
    changed = await apply_to_twin(cx, ev)
    if changed:
        await _notify(ev)     # пуш ЛИШЕ на реальну зміну; notify — зі своїм дедупом

async def process_once(pool) -> bool:
    async with pool.acquire() as cx:
        tx = cx.transaction(); await tx.start()
        job = None
        try:
            job = await cx.fetchrow(
                """SELECT id, event_id, payload, attempts FROM jobs
                    WHERE run_after <= now() ORDER BY id
                      FOR UPDATE SKIP LOCKED LIMIT 1""")
            if job is None:
                await tx.commit(); return False
            ev = json.loads(job["payload"])
            await handle_event(cx, ev)                # твін + пуш
            await cx.execute("DELETE FROM jobs WHERE id = $1", job["id"])
            await tx.commit()                         # зміна твіна й зняття з черги — разом
            return True
        except Exception as err:
            await tx.rollback()                       # відкат УСЬОГО: твін не зачеплено
            await retry_or_bury(pool, job, err)       # облік спроби — окремою транзакцією
            return True

async def retry_or_bury(pool, job, err) -> None:
    if job is None:
        return
    n = job["attempts"] + 1
    if n >= MAX_ATTEMPTS:                             # отрута — у мертву чергу, геть із jobs
        await pool.execute(
            """WITH gone AS (DELETE FROM jobs WHERE id = $1 RETURNING event_id, payload)
               INSERT INTO dead_letter(event_id, payload, error)
               SELECT event_id, payload, $2 FROM gone""", job["id"], str(err))
    else:                                            # ще спробуємо — експоненційний відступ
        await pool.execute(
            "UPDATE jobs SET attempts = $1, run_after = now() + make_interval(secs => $2) WHERE id = $3",
            n, 2 ** n, job["id"])
```
:::

Зверни увагу на порядок у `catch`: спершу `ROLLBACK`, і **тільки потім** облік спроби — окремим запитом на новому з'єднанні. Це не примха. Коли обробка падає на помилці бази, PostgreSQL позначає всю транзакцію аварійною, і будь-який наступний запит у ній відмовить із «current transaction is aborted». Тому облік невдачі (`attempts++` чи переїзд у мертву чергу) не можна робити в тій самій транзакції, що впала, — його роблять уже після відкату. Задача при цьому нікуди не зникла: `DELETE` теж відкотився, рядок лишився в `jobs`, і `retryOrBury` акуратно його або відсуває, або ховає.

Отруйна (poison) подія — та, що падає **щоразу**: скажімо, стан `"???"`, якого наш `VALID` не знає. Без мертвої черги вона крутилася б у голові черги вічно, з'їдаючи спроби й затримуючи все за собою. З нею — після `MAX_ATTEMPTS` невдач подія переїжджає в [мертву чергу](book:programming/dead-letter-queue) на очі людині, а черга йде далі. `SKIP LOCKED` тим часом гарантує, що навіть поки отруйна задача сидить під замком чужого робітника, здорові задачі за нею **не** блокуються.

> 🔧 **Навіщо це.** Три захисти в робітнику — це три різні «а що, як?». `seq`-версія відповідає на «а що, як події переставляться»; `RETURNING`-умова на зміну — на «а що, як прийде дубль або старіша» (тоді твін не міняється й пуш не летить); мертва черга — на «а що, як подія не піддається взагалі». Прибери будь-який — і знайдеться вхідний потік, що зробить твій твін брехливим або спинить обробку. Зверни ще увагу: `notify` викликається лише на справжню зміну, але робітник може повторити задачу після відкату — тож сам пуш теж мусить мати власний дедуп, інакше родина дістане дубль о третій ночі. Саме цим займається [приборкання сповіщень](guide:progarch/notification-dedup-throttle).

## Звірка: та сама ідемпотентність, тільки джерело — партнер

Тепер найголовніше проти ночі Соколів. Ні підпис, ні дедуп, ні мертва черга не рятують від події, що **не прийшла взагалі**: ендпоінт лежав під час деплою, провайдер вичерпав повтори й викинув «двері відчинено». Проти тиші працює лише **звірка** — періодичний [pull замість очікування на дзвінок](guide:progarch/polling-vs-callback).

Найгарніше тут те, що звірці не потрібен окремий механізм. Вона застосовує до твіна стан, який повертає API партнера, **тим самим** `applyToTwin` із захистом за `seq`. Якщо пуш був загублений і твін відстав — партнерів `seq` виявиться новішим, upsert спрацює, `changed` буде `true`, і ми не лише виправимо твін, а й дізнаємося, що впіймали дрейф. Якщо ж пуш дійшов і твін уже свіжий — партнерів `seq` дорівнює нашому, умова `EXCLUDED.seq > twin.seq` не виконається, нічого не зміниться, сповіщення не полетить. Звірка стає **нульовою дією, коли все добре, і точковим ремонтом, коли пуш пропав** — без жодної окремої гілки «порівняй і виріши».

:::tabs
```ts
// fetchState — pull стану з API партнера. Ін'єкція, щоб тест міг підставити фейк.
export async function reconcileDevice(
  deviceId: string,
  fetchState: (id: string) => Promise<{ state: string; seq: number }>,
): Promise<void> {
  const truth = await fetchState(deviceId);           // джерело правди — партнерів API
  const cx = await pool.connect();
  try {
    const changed = await applyToTwin(cx,
      { device_id: deviceId, state: truth.state, seq: truth.seq });
    if (changed) {                                     // твін відставав → пуш його пропустив
      await notify({ device_id: deviceId, ...truth });
      console.warn(`звірка: дрейф на ${deviceId} виправлено → ${truth.state}`);
    }
  } finally {
    cx.release();
  }
}

// Раз на N хвилин — по всіх пристроях, що DH веде.
setInterval(async () => {
  for (const id of await trackedDevices())
    await reconcileDevice(id, fetchAcmeState).catch(console.error);
}, 5 * 60_000);
```
```py
# fetch_state — pull стану з API партнера. Ін'єкція, щоб тест міг підставити фейк.
async def reconcile_device(pool, device_id, fetch_state) -> None:
    truth = await fetch_state(device_id)              # джерело правди — партнерів API
    async with pool.acquire() as cx:
        changed = await apply_to_twin(cx,
            {"device_id": device_id, "state": truth["state"], "seq": truth["seq"]})
        if changed:                                   # твін відставав → пуш його пропустив
            await _notify({"device_id": device_id, **truth})
            log.warning("звірка: дрейф на %s виправлено → %s", device_id, truth["state"])

# Раз на N хвилин — по всіх пристроях, що DH веде.
async def reconcile_loop(pool, fetch_state, every=300):
    while True:
        for device_id in await tracked_devices(pool):
            try:
                await reconcile_device(pool, device_id, fetch_state)
            except Exception as e:
                log.error("звірка %s: %s", device_id, e)
        await asyncio.sleep(every)
```
:::

Зверни увагу, що `fetchState` ми **впорскуємо** ззовні, а не викликаємо партнерів HTTP прямо в тілі. Це не лише робить звірку тестовною (за мить підставимо фейкового партнера) — це чесна межа: звірка знає *що* робити з правдою, а *звідки* її взяти — деталь, яку легко підмінити.

## Тест-гарнес: показати, що воно тримає

Тепер найцінніше — тест, який **доводить** усі чотири обіцянки, а не просто заспокоює. Гарнес жене крізь ті самі `handleWebhook`, `processOnce`, `reconcileDevice` реальні події проти справжньої (одноразової тестової) бази й перевіряє наслідки в таблицях. Сповіщення ми перехоплюємо шпигуном (`setNotifier`), а партнера в сценарії звірки підставляємо фейком — обидві межі для того й винесені в ін'єкцію.

Чотири сценарії — це чотири «а що, як?», що колись ламали приймачі DH: дубль, переупорядкування, загублена подія, отрута.

:::tabs
```ts
import test from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";

const sent: any[] = [];
setNotifier(async (ev) => { sent.push(ev); });     // шпигун замість справжнього пуша

function sign(body: object) {                        // підписуємо, як це робив би провайдер
  const raw = Buffer.from(JSON.stringify(body));
  const t = Math.floor(Date.now() / 1000);
  const v1 = createHmac("sha256", process.env.ACME_WEBHOOK_SECRET!)
    .update(Buffer.concat([Buffer.from(`${t}.`), raw])).digest("hex");
  return { raw, header: `t=${t},v1=${v1}` };
}
const drain = async () => { while (await processOnce()) {} };

test("дубль того самого id — рівно одна обробка", async () => {
  await resetDb(); sent.length = 0;
  const { raw, header } = sign({ id: "e1", device_id: "lock-42", state: "open", seq: 5 });
  assert.equal(await handleWebhook(raw, header), 200);
  assert.equal(await handleWebhook(raw, header), 200);   // провайдер повторив
  assert.equal(await countRows("jobs"), 1);              // у чергу лягло ОДИН раз
  await drain();
  assert.equal((await getTwin("lock-42")).state, "open");
  assert.equal(sent.length, 1);                          // один пуш, не два
});

test("переставлені події — старіша не затирає новішу", async () => {
  await resetDb(); sent.length = 0;
  const a = sign({ id: "e2", device_id: "lock-42", state: "open",   seq: 5 });
  const b = sign({ id: "e3", device_id: "lock-42", state: "closed", seq: 4 }); // старіша!
  await handleWebhook(a.raw, a.header);
  await handleWebhook(b.raw, b.header);
  await drain();
  const twin = await getTwin("lock-42");
  assert.equal(twin.state, "open");                      // seq 4 не перебив seq 5
  assert.equal(twin.seq, 5);
});

test("загублена подія — звірка виправляє дрейф", async () => {
  await resetDb(); sent.length = 0;
  await seedTwin("lock-42", "closed", 5);                // остання відома правда
  // подія seq=6 «відчинено» НЕ дійшла (ендпоінт лежав) — handleWebhook не викликаний
  await reconcileDevice("lock-42", async () => ({ state: "open", seq: 6 }));
  assert.equal((await getTwin("lock-42")).state, "open"); // звірка стягла до джерела
  assert.equal(sent.at(-1)?.state, "open");              // і сповістила про виправлення
});

test("poison-подія — у мертву чергу, решта черги жива", async () => {
  await resetDb(); sent.length = 0;
  const bad  = sign({ id: "e4", device_id: "lock-42", state: "???",  seq: 7 }); // впаде щоразу
  const good = sign({ id: "e5", device_id: "lock-9",  state: "open", seq: 1 });
  await handleWebhook(bad.raw, bad.header);
  await handleWebhook(good.raw, good.header);
  for (let i = 0; i < MAX_ATTEMPTS; i++) { await forceReady(); await drain(); } // без чекання
  assert.equal(await countRows("dead_letter"), 1);       // отруйна осіла в DLQ
  assert.equal((await getTwin("lock-9")).state, "open"); // здорова пройшла попри отруту поряд
  assert.equal(await countRows("jobs"), 0);              // черга чиста
});
```
```py
import pytest, json, time, hmac, hashlib, os

sent: list = []
set_notifier(lambda ev: sent.append(ev))          # шпигун замість справжнього пуша

def sign(body: dict):                              # підписуємо, як це робив би провайдер
    raw = json.dumps(body).encode()
    t = int(time.time())
    v1 = hmac.new(os.environ["ACME_WEBHOOK_SECRET"].encode(),
                  f"{t}.".encode() + raw, hashlib.sha256).hexdigest()
    return raw, f"t={t},v1={v1}"

async def drain(pool):
    while await process_once(pool):
        pass

@pytest.mark.asyncio
async def test_duplicate_processed_once(pool):
    await reset_db(pool); sent.clear()
    raw, header = sign({"id": "e1", "device_id": "lock-42", "state": "open", "seq": 5})
    assert await handle_webhook(raw, header, pool) == 200
    assert await handle_webhook(raw, header, pool) == 200   # провайдер повторив
    assert await count_rows(pool, "jobs") == 1              # у чергу лягло ОДИН раз
    await drain(pool)
    assert (await get_twin(pool, "lock-42"))["state"] == "open"
    assert len(sent) == 1                                   # один пуш, не два

@pytest.mark.asyncio
async def test_reorder_older_does_not_win(pool):
    await reset_db(pool); sent.clear()
    a = sign({"id": "e2", "device_id": "lock-42", "state": "open",   "seq": 5})
    b = sign({"id": "e3", "device_id": "lock-42", "state": "closed", "seq": 4})  # старіша!
    await handle_webhook(*a, pool); await handle_webhook(*b, pool)
    await drain(pool)
    twin = await get_twin(pool, "lock-42")
    assert twin["state"] == "open" and twin["seq"] == 5     # seq 4 не перебив seq 5

@pytest.mark.asyncio
async def test_lost_event_caught_by_reconcile(pool):
    await reset_db(pool); sent.clear()
    await seed_twin(pool, "lock-42", "closed", 5)          # остання відома правда
    async def partner(_id): return {"state": "open", "seq": 6}   # подія seq=6 НЕ дійшла
    await reconcile_device(pool, "lock-42", partner)
    assert (await get_twin(pool, "lock-42"))["state"] == "open"  # звірка стягла до джерела
    assert sent[-1]["state"] == "open"                     # і сповістила про виправлення

@pytest.mark.asyncio
async def test_poison_goes_to_dead_letter(pool):
    await reset_db(pool); sent.clear()
    bad  = sign({"id": "e4", "device_id": "lock-42", "state": "???",  "seq": 7})  # впаде щоразу
    good = sign({"id": "e5", "device_id": "lock-9",  "state": "open", "seq": 1})
    await handle_webhook(*bad, pool); await handle_webhook(*good, pool)
    for _ in range(MAX_ATTEMPTS):                          # без чекання на backoff
        await force_ready(pool); await drain(pool)
    assert await count_rows(pool, "dead_letter") == 1      # отруйна осіла в DLQ
    assert (await get_twin(pool, "lock-9"))["state"] == "open"  # здорова пройшла
    assert await count_rows(pool, "jobs") == 0             # черга чиста
```
:::

Прочитаймо, що саме доводить кожен тест. **Дубль:** два однакові POST — `jobs` містить один рядок, `sent` має один пуш, твін «відчинено». Дедуп працює, ідемпотентність тримає. **Переупорядкування:** «зачинено» seq 4 прибуло після «відчинено» seq 5 — і твін лишився «відчинено», бо `seq`-захист відкинув старіше. **Загублена подія:** ми **навмисне не викликаємо** `handleWebhook` — імітуємо мертвий ендпоінт, — сіємо твінові стару правду «зачинено» і запускаємо звірку з фейковим партнером, що каже «відчинено» seq 6; твін виправляється, і саме цей прохід урятував би Соколів. **Отрута:** подія зі станом `"???"` падає всі п'ять разів і осідає в `dead_letter`, тоді як здорова подія сусіднього замка проходить, а черга лишається чистою.

Помічники (`resetDb`, `getTwin`, `countRows`, `seedTwin`, `forceReady`) — тонкі обгортки над тестовою базою; `forceReady` просто робить `UPDATE jobs SET run_after = now()`, щоб тест не чекав на реальний експоненційний відступ. Уся суть — у чотирьох `assert`, що читаються як специфікація: ось що приймач **обіцяє**, і ось запуск, який ловить нас за руку, якщо обіцянку зламано.

## Складність і пастки

Зберімо докупи місця, де цей вузол ламається, якщо не бути уважним — кожне з них має рядок коду вище, що його стереже.

- **Сирі байти проти переупакованого JSON.** HMAC рахують над **точними отриманими байтами**. Один `JSON.parse` → `stringify` перед перевіркою — і чесний підпис не збіжиться (ми щойно бачили два різні геші на той самий факт). Тому фреймворк віддає нам `Buffer`/`bytes`, а не готовий об'єкт.
- **Порівняння за сталий час.** `timingSafeEqual` / `compare_digest`, ніколи `==`. Наївне порівняння виходить на першій різній літері, і за часом відповіді підпис можна вгадувати байт за байтом.
- **Атомарність inbox + черга.** Позначка «бачене» і запис у чергу — в одній транзакції. Розчепиш — крах між ними лишить подію позначеною, але не обробленою, і дедуп ховатиме її повтори навіки.
- **Загублений `200`.** Провайдер повторить те, що ми вже зробили; inbox із первинним ключем поглинає повтор, і ми чесно відповідаємо `200`, не подвоюючи роботи.
- **Переупорядкування.** Твін оновлюємо лише на новіший `seq`; старіша, але пізніша подія не має перебити свіжу правду.
- **Пуш лише на реальну зміну.** `RETURNING` з умови `EXCLUDED.seq > twin.seq` дає сигнал «твін справді змінився» — тільки тоді летить сповіщення, тож дублі й старіші події не спамлять родину.
- **Отрута → мертва черга.** Подія, що падає щоразу, після `N` спроб з експоненційним відступом їде в `dead_letter`; `SKIP LOCKED` не дає їй заблокувати здорові задачі.
- **Аварійна транзакція.** Помилка обробки псує всю транзакцію в PostgreSQL — облік невдалої спроби роби **після** `ROLLBACK`, окремим запитом, інакше він теж відмовить.
- **Ціна звірки.** Опитувати партнера коштує запитів і впирається в його ліміти. Частоту став за ціною пропуску: замок і гроші — часто; яскравість лампи — рідко або ніколи. Звірка — сітка безпеки, а не другий гарячий шлях.
- **Свій дедуп у сповіщень.** Робітник може повторити пуш після відкату або звірки; щоб родина не діставала копій, сам канал сповіщень мусить дедуплікувати — це вже [окрема робота](guide:progarch/notification-dedup-throttle).
- **Вікно позначки часу.** П'ять хвилин — компроміс: вужче ловить менше повторів-атак, але страждає від годинникового дрейфу між серверами; ширше — навпаки. Синхронізуй годинники й тримай вікно вузьким, скільки дозволяє реальність.

І один висновок понад список. Жодна з цих деталей не «просунута» сама по собі — просунута лише їхня **сума**: приймач надійний рівно настільки, наскільки кожен рефлекс на місці й у правильному порядку. Тонкий роут без дедупу подвоїть гроші; дедуп без атомарності загубить подію; усе разом без звірки промовчить про те, що не прийшло. Зібраний так, як вище, вузол переживає рівно ту ніч, з якої почалася розмова, — і наступного ж проходу звірки повертає застосунку Соколів чесне «двері відчинено».
