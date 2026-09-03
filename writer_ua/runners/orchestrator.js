#!/usr/bin/env node
/* ============================================================================
   orchestrator.js — ЗОВНІШНІЙ РІВЕНЬ: черга, ліміт активних, стан, маніфест.

   Межа з внутрішнім алгоритмом чиста й навмисна:

     ОРКЕСТРАТОР              ВНУТРІШНІЙ АЛГОРИТМ
     тримає чергу             десять етапів
     заводить прогони         працює з ОДНІЄЮ одиницею
     чекає                    пише ОДИН файл
     тримає стан
     пише маніфест — раз у кінці

   ⛔ ОРКЕСТРАТОР НІЧОГО НЕ СУДИТЬ. Він не читає текст і не вирішує, що добре: тільки
   черга, запуск, очікування, стан і один запис. Усе судження — всередині алгоритму.
   Тому сам алгоритм сюди ПЕРЕДАЄТЬСЯ функцією: оркестратор не знає ні про правила, ні
   про зміст етапів, і його можна ганяти з підробним алгоритмом, не витративши й токена.

   СТАН — ЦЕ ОБ'ЄКТ ІЗ ПОЛЯМИ, А НЕ СТРІЧКА ЗАПИСІВ. Поле заповнене — етап пройдено; де
   воно зупинилось — це останнє заповнене поле. Так було не завжди: спершу тут лежав
   журнал дописуванням, і з нього виросли три різні вади. Ім'я стадії від алгоритму не
   відрізнялося від службового, тож `log("finish")` оголошував одиницю завершеною й ховав
   її від маніфесту. Обірваний посеред запису рядок з'їдав наступний, і разом із ним гинув
   справжній `finish` — одиниця йшла на перепис при кожному піднятті. А щоб відповісти «на
   якому воно етапі», доводилося розбирати стрічку назад.

   Файл стану пишеться ЦІЛКОМ і АТОМАРНО — тимчасовий плюс перейменування, як у
   писар маніфесту. Або старий стан, або новий; напівзаписаного не буває.

   ЧЕРГА РОСТЕ ПІД ЧАС ПРОГОНУ. Батч заводять на 10 тем, але каркас кожної назве свої
   вставки, код і, можливо, базову — і всі вони стануть у ту саму чергу. Тому
   `ctx.enqueue()` доступний у будь-який момент, а цикл триває, доки є що робити, а не
   «доки не скінчиться початковий список». Стеля `maxUnits` існує не проти росту, а проти
   НЕСКІНЧЕННОГО: кожна одиниця в бою це агент і токени.

   ⛔ ТЕКУ БАТЧУ НЕ ПРИБИРАЄМО НІКОЛИ. У станах не самий лише слід для підняття, а й усе
   поодиничне: скільки спроб з'їла викладка, яка була ціль і рівень, що саме написано.
   Прибирає це людина, коли подивилася. `inwork/` у `.gitignore`.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const MF = require("../lib/manifest.js");

/* Усе робоче — в одному місці: `<корінь репо>/inwork/<хеш>/`. Батч дістає власний
   випадковий хеш із 10 символів, і той хеш є і його ім'ям, і іменем його теки. */
const INWORK = path.join(MF.ROOT, "inwork");
const CONTROL = "control.json";
const ID_RE = /^[a-z0-9]{10}$/;
const newId = () => crypto.randomBytes(8).toString("hex").slice(0, 10);

const DEFAULTS = {
  active: 4, stagger: 2000, maxUnits: 200,
  limitPause: 5 * 60 * 1000,
  callTimeout: 10 * 60 * 1000,   // скільки чекати ОДНУ відповідь агента
  tick: 3000,                    // як часто перечитувати пульт, поки нічого не завершилось
};

function whole(v, name, min) {
  if (!Number.isInteger(v) || v < min)
    throw new Error(`${name} має бути цілим числом ≥ ${min}, а не «${v}»`);
  return v;
}

const slug = (s) => String(s).replace(/[^\w.-]+/g, "_");
const msgOf = (e) => String((e && e.message) || e);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/* ── стан одиниці ──────────────────────────────────────────────────────────── */

/**
 * ПОЛЯ ЕТАПІВ — сталий перелік, у порядку конвеєра. Алгоритм заповнює їх через
 * `ctx.set(поле, значення)`; вигадати нове поле він не може, і саме тому службове більше
 * не підробиш. Порядок важить: «де воно зупинилось» — це останнє заповнене.
 */
const STAGES = [
  "prep",       //  1 підготовка: згадки, абзаци довкола
  "goal",       //  2 ціль (текст) і рівень
  "karkas",     //  3 питання з важливістю, групування, опори, вставки й код
  "sections",   //  4 розділи: текст, тези, чи глибше, чи повно, що додати, нові теми
  "size",       //  5 розмір і скільки бракує
  "layout",     //  6 викладка проти цілей: ок або чому ні, скільки спроб
  "formulas",   //  7 формули: стара → нова
  "code",       //  7 код: чи можна C, чи можна C++
  "deferred",   //  8 відкладене: нові теми, лінки, чи треба базова
  "figures",    //  9 фігури: що полагоджено
  "ops",        // 10 що піде в маніфест
];

class UnitState {
  /**
   * Ім'я файла — санітований id ПЛЮС короткий хеш сирого. Сама санітація схлопує різне в
   * одне (`sf-apps/cache` і `sf-apps:cache` дають той самий рядок, а суцільна кирилиця —
   * рядок самих підкреслень), і дві різні одиниці ділили б один стан.
   */
  constructor(dir, unit) {
    this.dir = dir;
    this.unit = unit;
    this.path = path.join(dir, (slug(unit.id).slice(0, 48) || "unit") + "-" +
      crypto.createHash("sha1").update(String(unit.id), "utf8").digest("hex").slice(0, 8) + ".json");
    this.data = {
      id: unit.id, book: unit.book || null, type: unit.type || null,
      unit,                       // повне тіло: підняття відновлює чергу саме звідси
      done: false,
      enqueued: [],               // повні тіла докладених — їх у вхідному списку немає
      error: null,
      calls: 0,                   // скільки запитів до агента вже зроблено
    };
    for (const s of STAGES) this.data[s] = null;
  }

  load() {
    if (!fs.existsSync(this.path)) return false;
    try { Object.assign(this.data, JSON.parse(fs.readFileSync(this.path, "utf8"))); return true; }
    catch { return false; }      // побитий стан — вважаємо, що його немає, і робимо наново
  }

  /** Атомарно: або старий файл, або новий. Дописування тут не буває взагалі. */
  save() {
    const tmp = this.path + ".tmp";
    let text;
    try { text = JSON.stringify(this.data, null, 1); }
    catch (e) {
      /* Несеріалізовний вантаж — не привід ховати те, що вже пройдено: зберігаємо стан
         без нього, а сам факт лишаємо в полі помилки. */
      this.data.error = `стан не серіалізується: ${msgOf(e)}`;
      const safe = { ...this.data };
      for (const s of STAGES) { try { JSON.stringify(safe[s]); } catch { safe[s] = "«не серіалізується»"; } }
      try { JSON.stringify(safe.unit); } catch { safe.unit = { id: this.data.id }; }
      safe.enqueued = [];
      text = JSON.stringify(safe, null, 1);
    }
    fs.writeFileSync(tmp, text + "\n", "utf8");
    fs.renameSync(tmp, this.path);
  }

  set(field, value) {
    if (!STAGES.includes(field)) throw new Error(`немає етапу «${field}» — є: ${STAGES.join(" ")}`);
    this.data[field] = value === undefined ? null : value;
    this.save();
    return this;
  }

  get(field) { return this.data[field]; }

  /** Останнє заповнене поле — і є відповідь на «на якому воно етапі». */
  get stage() {
    let last = null;
    for (const s of STAGES) if (this.data[s] !== null) last = s;
    return last;
  }
  get done() { return this.data.done === true; }
  finish() { this.data.done = true; this.save(); }
  fail(e, limit) { this.data.error = { message: msgOf(e), limit: !!limit }; this.save(); }
  addEnqueued(units) { this.data.enqueued.push(...units); this.save(); }
}

/** Усі стани теки батчу — для підняття й для сухого прогону. */
function readStates(dir) {
  if (!fs.existsSync(dir)) return [];
  let files = [];
  try { files = fs.readdirSync(dir); } catch { return []; }
  const out = [];
  for (const f of files) {
    if (!f.endsWith(".json") || f === CONTROL) continue;
    try { out.push(JSON.parse(fs.readFileSync(path.join(dir, f), "utf8"))); } catch { }
  }
  return out;
}

/**
 * Черга зі станів. Беремо і докладені тіла, і тіла самих одиниць: докладених у вхідному
 * списку немає взагалі, і без цього підняття їх би загубило.
 */
function restoreUnits(dir) {
  const out = new Map();
  for (const st of readStates(dir)) {
    for (const u of st.enqueued || []) if (u && u.id && !out.has(u.id)) out.set(u.id, u);
    if (st.unit && st.unit.id && !out.has(st.unit.id)) out.set(st.unit.id, st.unit);
  }
  return [...out.values()];
}

/* ── стіна ліміту ──────────────────────────────────────────────────────────── */

/**
 * Що САМЕ вважати стіною. Будь-яке «429» чи «quota» в тексті не годиться: «порт 429
 * зайнятий» і «disk quota» стіною не є, а ціна помилки — зупинений прогін.
 */
const LIMIT_RE = [
  /\brate[ _-]?limit/i, /\busage limit/i, /\blimit reached\b/i, /\btoo many requests\b/i,
  /\bquota (?:exceeded|reached)\b/i, /\bexceeded (?:your |the )?(?:\w+ )?quota\b/i,
  /\bout of quota\b/i, /\boverloaded(?:_error)?\b/i,
  /\b(?:status|code|http|error)\W{0,4}429\b/i, /\b429\W{0,3}too many\b/i,
];
const isLimit = (e) => {
  if (!e) return false;
  if (e.limit === true) return true;
  return LIMIT_RE.some((re) => re.test(msgOf(e)));
};

/* ── черга ─────────────────────────────────────────────────────────────────── */

class Queue {
  constructor({ active = DEFAULTS.active, stagger = DEFAULTS.stagger, maxUnits = DEFAULTS.maxUnits } = {}) {
    this.limit = whole(active, "active", 1);
    this.stagger = whole(stagger, "stagger", 0);
    this.max = whole(maxUnits, "maxUnits", 1);
    this.pending = [];
    this.running = new Map();
    this.seen = new Set();
    this.fresh = 0;                // скільки НОВИХ одиниць завів цей прогін
    this.refused = [];
    this.wall = false;
  }
  /**
   * Стеля рахує лише НОВІ одиниці цього прогону. Інакше прогін, що вперся в неї, після
   * підняття відкидав би геть усе, що каркаси доназвали, — а підняття це рівно той
   * момент, коли вони це й роблять.
   */
  push(units, { restored = false } = {}) {
    const added = [], refused = [];
    for (const u of [].concat(units || [])) {
      if (!u || !u.id) throw new Error("одиниця без id — її нічим адресувати");
      if (this.seen.has(u.id)) continue;
      if (!restored && this.fresh >= this.max) { refused.push(u); continue; }
      this.seen.add(u.id);
      if (!restored) this.fresh++;
      this.pending.push(u); added.push(u);
    }
    if (refused.length) this.refused.push(...refused.map((u) => u.id));
    return { added, refused };
  }
  /** Повернути в чергу одиницю, що стояла на паузі: вона вже «бачена», стелі не займає. */
  requeue(u) { this.pending.push(u); }
}

/* ── прогін ────────────────────────────────────────────────────────────────── */

/**
 * @param {object}   o
 * @param {string}   [o.id]          хеш батчу; без нього — новий. Той самий хеш піднімає обірваний
 * @param {Array}    o.units         одиниці: {id, book, …будь-що для алгоритму}
 * @param {Function} [o.algorithm]   async (unit, ctx) → результат. У сухому прогоні НЕ кличеться
 * @param {Function} [o.toOps]       стан → операції писаря маніфесту; типово `state.get("ops")`
 * @param {boolean}  [o.dry]         прокрутити чергу й показати стан; жодного агента, жодного запису
 * @param {number}   [o.active]      скільки одиниць одночасно (пульт міняє на ходу)
 * @param {number}   [o.stagger]     пауза між стартами, мс
 * @param {number}   [o.maxUnits]    стеля НОВИХ одиниць прогону
 * @param {number}   [o.callTimeout] скільки чекати ОДНУ відповідь агента
 * @param {number}   [o.limitPause]  контрольна пауза перед вироком «стіна»
 * @param {Function} [o.onEvent]     сповіщення для людини
 */
async function run(o) {
  const dry = !!o.dry;
  const say = o.onEvent || (() => { });
  /* `null` — операцій не дали, це сирота; `[]` — їх немає НАВМИСНО (код реєструє
     посилання в прозі, у маніфест він не йде). Розрізняти треба, інакше кожна одиниця
     коду звітувалась би як помилка. */
  const toOps = o.toOps || ((st) => st.get("ops"));

  /* Числа — ПЕРШИМИ, до створення теки: `active: NaN` крутив головний цикл синхронно й
     вішав процес на 100% CPU без жодного рядка діагностики. */
  const q = new Queue({ active: o.active, stagger: o.stagger, maxUnits: o.maxUnits });
  const limitPause = whole(o.limitPause === undefined ? DEFAULTS.limitPause : o.limitPause, "limitPause", 0);
  const callTimeout = whole(o.callTimeout === undefined ? DEFAULTS.callTimeout : o.callTimeout, "callTimeout", 0);
  const tick = whole(o.tick === undefined ? DEFAULTS.tick : o.tick, "tick", 100);
  if (!dry && typeof o.algorithm !== "function") throw new Error("немає algorithm — оркестратор сам нічого не робить");

  const id = o.id === undefined ? newId() : String(o.id);
  if (!ID_RE.test(id)) throw new Error(`id батчу — це 10 символів [a-z0-9] (хеш), а не «${id}»`);
  const dir = path.join(INWORK, id);

  /* Спершу черга зі станів, аж тоді вхідний список: докладене минулим прогоном не гине, а
     `o.units` просто не дублюються. Відновлене стелі не займає. */
  const restored = q.push(restoreUnits(dir), { restored: true });
  if (restored.added.length) say({ ev: "restore", n: restored.added.length });
  q.push(o.units || []);
  if (!q.pending.length) throw new Error("черга порожня — нічого заводити");

  /* ── сухий прогін: жодного агента, жодного запису ──
     Він саме «нічого не робить, тільки дивиться»: показує чергу й на якому етапі кожна
     одиниця стоїть за своїм станом. Доти `dry` кликав алгоритм по-справжньому — тобто
     коштував повну ціну, писав статті й не писав маніфест. Це було гірше за обидва. */
  if (dry) {
    const known = new Map(readStates(dir).map((s) => [s.id, s]));
    const rows = q.pending.map((u) => {
      const s = known.get(u.id);
      const last = s ? (STAGES.filter((f) => s[f] !== null && s[f] !== undefined).pop() || null) : null;
      return { id: u.id, book: u.book || null, done: !!(s && s.done), stage: last, error: (s && s.error) || null };
    });
    return {
      id, dir, dry: true, queue: rows.length,
      done: rows.filter((r) => r.done).length,
      todo: rows.filter((r) => !r.done).length,
      restored: restored.added.length, units: rows,
    };
  }

  fs.mkdirSync(dir, { recursive: true });

  const done = [], failed = [], skipped = [], notes = [];

  /* ── пауза ─────────────────────────────────────────────────────────────────
     Одиниця, якій бракує чужого результату (проза чекає на код), не провалюється й
     не тримає місця в пулі: вона стає в `waiting`, а щойно всі, кого вона чекає,
     завершаться — повертається в чергу. Завершені — у `finished`, разом із тими, що
     завершились у минулих прогонах: підняття інакше змусило б чекати вже написане. */
  const waiting = [];
  const finished = new Set(readStates(dir).filter((s) => s && s.done && s.id).map((s) => s.id));
  const release = () => {
    for (let i = waiting.length - 1; i >= 0; i--) {
      const w = waiting[i];
      if (!w.for.every((id) => finished.has(id))) continue;
      waiting.splice(i, 1);
      q.requeue(w.unit);
      try { say({ ev: "resume", unit: w.unit.id }); } catch { }
    }
  };

  /* Протокол стіни (CLAUDE.md): перша підозра на ліміт це ще НЕ стіна — одна контрольна
     пауза й ОДНА повторна спроба; мовчить удруге — WALL. Пауза одна на прогін. */
  let probe = null, probeOver = false;
  const controlPause = (unit) => {
    if (!probe) { say({ ev: "limit-probe", unit, pause: limitPause }); probe = sleep(limitPause).then(() => { probeOver = true; }); }
    return probe;
  };

  const start = (unit) => {
    const st = new UnitState(dir, unit);
    st.load();
    if (st.done) { skipped.push(unit.id); done.push({ unit, state: st }); finished.add(unit.id); say({ ev: "skip", unit: unit.id }); return null; }
    st.save();
    say({ ev: "start", unit: unit.id, from: st.stage, active: q.running.size + 1, pending: q.pending.length });

    const ctx = {
      unit, state: st, run: { id, dir },
      /** Заповнити поле етапу. Поле заповнене — етап пройдено, і це видно одразу. */
      set: (field, value) => { st.set(field, value); say({ ev: "stage", unit: unit.id, stage: field }); return ctx; },
      get: (field) => st.get(field),
      /** Чи завершена інша одиниця — у цьому прогоні або в минулих. */
      isDone: (id) => finished.has(id),
      /**
       * ОДИН запит до агента — з межею очікування. Зависає завжди окремий виклик, а не
       * одиниця цілком: одиниця це десятки запитів і година-дві роботи. Не дочекались —
       * це помилка кроку, і алгоритм вирішує, повторювати чи писати в дефект.
       */
      call: (label, fn) => {
        st.data.calls++;
        let timer;
        return Promise.race([
          Promise.resolve().then(fn),
          new Promise((_, rej) => { timer = setTimeout(() => rej(new Error(`агент мовчить понад ${callTimeout >= 1000 ? Math.round(callTimeout / 1000) + "с" : callTimeout + "мс"}: ${label}`)), callTimeout); }),
        ]).finally(() => clearTimeout(timer));
      },
      enqueue: (more) => {
        const r = q.push(more);
        if (r.added.length) { st.addEnqueued(r.added); say({ ev: "enqueue", unit: unit.id, n: r.added.length }); }
        if (r.refused.length) { notes.push(`${unit.id}: стеля maxUnits=${q.max}, відмовлено ${r.refused.length}`); say({ ev: "refused", unit: unit.id, n: r.refused.length }); }
        return r.added.length;
      },
    };

    const attempt = () => Promise.resolve().then(() => o.algorithm(unit, ctx));
    let ok = false;

    return attempt()
      .catch((e) => {
        /* Перший ліміт — ще не вирок: одна пауза, одна повторна спроба. */
        if (!isLimit(e) || probeOver) throw e;
        return controlPause(unit.id).then(attempt);
      })
      .then(() => {
        ok = true;
        st.finish(); done.push({ unit, state: st });
        finished.add(unit.id); release();
        /* `say` — чужий код, і його виняток не має перетворювати зроблену одиницю на
           провалену: доти вона потрапляла і в `done`, і в `failed` одночасно. */
        try { say({ ev: "done", unit: unit.id }); } catch (e) { notes.push(`onEvent впав: ${msgOf(e)}`); }
      })
      .catch((e) => {
        if (ok) { notes.push(`після завершення ${unit.id}: ${msgOf(e)}`); return; }
        if (e && e.pause && Array.isArray(e.waitFor)) {
          st.data.waiting = e.waitFor; st.save();
          waiting.push({ unit, for: e.waitFor });
          try { say({ ev: "pause", unit: unit.id, for: e.waitFor }); } catch { }
          return;
        }
        const limit = isLimit(e);
        st.fail(e, limit);
        failed.push({ unit: unit.id, error: msgOf(e), limit });
        try { say({ ev: "fail", unit: unit.id, limit, message: msgOf(e) }); } catch { }
        if (limit) q.wall = true;
      });
  };

  /**
   * ПУЛЬТ БАТЧУ, ЩО ВЖЕ ЙДЕ — `inwork/<хеш>/control.json` із `{"active": 6}`. Читається і
   * перед кожним стартом, і раз на `tick`, поки нічого не завершується: інакше пульт
   * оживав би лише в мить, коли якась одиниця дописалась, тобто раз на десятки хвилин.
   */
  const control = () => {
    let raw;
    try { raw = fs.readFileSync(path.join(dir, CONTROL), "utf8"); } catch { return; }
    let v; try { v = JSON.parse(raw); } catch { say({ ev: "control-bad", why: "не JSON" }); return; }
    if (v && v.active !== undefined) {
      if (Number.isInteger(v.active) && v.active >= 1) {
        if (v.active !== q.limit) { say({ ev: "control", active: v.active, was: q.limit }); q.limit = v.active; }
      } else say({ ev: "control-bad", why: `active «${v.active}» — треба ціле ≥ 1` });
    }
  };

  while (q.pending.length || q.running.size) {
    control();
    while (!q.wall && q.running.size < q.limit && q.pending.length) {
      const unit = q.pending.shift();
      const p = start(unit);
      if (!p) continue;
      const key = unit.id;
      q.running.set(key, p.finally(() => q.running.delete(key)));
      if (q.stagger && q.pending.length) await sleep(q.stagger);
      control();
    }
    if (q.running.size) await Promise.race([...q.running.values(), sleep(tick)]);
    else if (q.wall) break;
  }

  const aborted = q.wall;
  if (aborted) say({ ev: "wall", pending: q.pending.length });

  /* ── маніфест: один раз, зі станів ── */
  const byBook = new Map(), orphans = [];
  let routed = 0;
  for (const { unit, state } of done) {
    let ops = null;
    try { ops = toOps(state, unit); }
    catch (e) { notes.push(`${unit.id}: toOps впав — ${msgOf(e)}`); }
    if (ops == null) { orphans.push({ unit: unit.id, why: "нема операцій" }); continue; }
    if (!ops.length) continue;
    if (!unit.book) { orphans.push({ unit: unit.id, why: "немає book" }); continue; }
    if (!byBook.has(unit.book)) byBook.set(unit.book, []);
    byBook.get(unit.book).push(...ops.map((op) => ({ op, unit: unit.id })));
    routed++;
  }

  const report = {
    id, dir, logs: dir, done: done.length, failed: failed.length, skipped: skipped.length,
    restored: restored.added.length, routed, aborted, pending: q.pending.length,
    refused: q.refused, orphans, notes, errors: failed, books: {},
    /* Лишились на паузі — ті, кого вони чекали, не завершились. Стан на диску є;
       той самий хеш підніме їх, щойно з'явиться те, чого бракує. */
    paused: waiting.map((w) => ({ unit: w.unit.id, for: w.for })),
    ids: { done: done.map((d) => d.unit.id), failed: failed.map((f) => f.unit) },
  };
  if (waiting.length) say({ ev: "paused-left", n: waiting.length });

  /* Стіна тимчасова — маніфесту не пишемо взагалі: половина черги ще не пройдена, і запис
     зафіксував би півстан як завершений. Той самий хеш підніме прогін. */
  if (aborted) {
    report.manifest = "не писали — стіна ліміту; той самий хеш піднімає прогін";
    return report;
  }

  let bookErrors = 0;
  for (const [book, tagged] of byBook) {
    /* КНИГА Є ⟺ Є `manifest.json`, а не «є тека». Писар книги не заводить і сам, але
       сказати про це виразним рядком у звіті дешевше, ніж читати його `errors`. */
    const dirBook = MF.bookDirOf(book);
    const units = [...new Set(tagged.map((t) => t.unit))];
    if (!dirBook || !MF.loadBook(dirBook)) { report.books[book] = { missing: "manifest.json не знайдено", units }; bookErrors++; continue; }
    try {
      const rep = MF.applyOps(dirBook, tagged.map((t) => t.op));
      report.books[book] = { changed: rep.changed, skipped: rep.skipped, errors: rep.errors, units };
      if (rep.errors.length) bookErrors++;
    } catch (e) {
      /* `applyOps` пише файли й кидає при будь-якій заваді — повний диск, антивірус на
         `.tmp`, відкритий редактором маніфест. Без цього перехоплення виняток забирав і
         звіт, і книги, до яких черга не дійшла, лишаючи корпус напівзаписаним. */
      report.books[book] = { crashed: msgOf(e), units };
      bookErrors++;
    }
  }

  const flag = [];
  if (failed.length) flag.push(`провалених: ${failed.length}`);
  if (orphans.length) flag.push(`без операцій або без книги: ${orphans.length}`);
  if (q.refused.length) flag.push(`відмовила стеля: ${q.refused.length}`);
  if (bookErrors) flag.push(`книг із помилками: ${bookErrors}`);
  if (!routed && done.length) flag.push("ЖОДНОЇ операції не записано — перевір toOps і формат результату");

  report.manifest = `записано за завершеними (${routed} з ${done.length})` + (flag.length ? `; ${flag.join("; ")}` : "");
  return report;
}

module.exports = { run, Queue, UnitState, STAGES, readStates, restoreUnits, isLimit, newId, INWORK, DEFAULTS };
