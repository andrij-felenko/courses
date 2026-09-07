#!/usr/bin/env node
/* ============================================================================
   ask-file.js — АДАПТЕР «ПОШТОВА СКРИНЬКА». Агента кличе не конвеєр, а той, хто
   його веде.

   ЧОМУ ВІН Є. Пісочниця воркфлоу не має ні `require`, ні диска — отже наш
   оркестратор у ній не живе: і промпти, і маніфест, і лічильники читають файли.
   Із node ж агента не викликати: `agent()` існує лише всередині воркфлоу, а CLI
   в системі немає. Два світи не сходяться напряму, і місток між ними — файл.

   ЯК ЦЕ ПРАЦЮЄ. Конвеєр кладе завдання й чекає на відповідь:

     inwork/<хеш>/<одиниця>/NN-<мітка>.ask.txt    ← поклав конвеєр, чекає
     inwork/<хеш>/<одиниця>/NN-<мітка>.ans.txt    ← поклав ведучий, конвеєр іде далі

   Ведучий — людина, головна сесія чи будь-що інше: адаптер про це не знає.
   Він лише дивиться, чи з'явився файл відповіді, і віддає його вміст.

   ⚠️ ЧЕКАЄ ДОВГО, І ЦЕ НАВМИСНО. Стеля очікування береться з `--wait` (типово
   година): відповідь пише жива істота або агент, і десятихвилинна межа
   оркестратора вбивала б одиницю посеред роботи. Запускати цей адаптер варто з
   тим самим `--wait`, переданим у `callTimeout`.

   Ужиток:
     node writer_ua/runners/start.js --book … --topic … --ask writer_ua/runners/ask-file.js
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const WAIT = Number(process.env.ASK_WAIT_MS) || 60 * 60 * 1000;
const POLL = Number(process.env.ASK_POLL_MS) || 1500;
const STABLE = Number(process.env.ASK_STABLE_MS) || 120 * 1000;

/**
 * ⛔ ВІДПОВІДЬ ГОТОВА ⟺ ЗАКРИТО КОЖЕН БЛОК, ЯКИЙ ПРОСИТЬ КОНТРАКТ. Непорожнього файла
 * замало, і одного закритого блоку — теж: той, хто відповідає, пише великий текст
 * частинами з паузами в хвилину й більше, і між частинами на диску лежить половина.
 * «Хоч один закритий блок» проковтнув таку половину дванадцять разів за один батч: стан
 * одиниці з «у відповіді немає ТЕКСТ» записано на 75 секунд раніше, ніж файл добіг кінця.
 *
 * Тому теги беремо з `<ПОВЕРНИ>` самого завдання — конвеєр і адаптер дивляться на один
 * контракт. Контракт із кількох кроків («Крок 1:», «Крок 2:») читаємо за рядком
 * «крок: N» у шапці завдання. Запасний вихід — коли відповідач не написав необов'язковий
 * порожній блок: перший блок контракту закрито, і файл не мінявся довше, ніж триває
 * пауза між частинами.
 */
const TAG = /<([А-ЯІЇЄҐA-Z][^<>\n/]*?)>/g;
/* Закритий блок — і `<ТЕГ>…</ТЕГ>` (ім'я може бути з пробілами: «ЩО ЗЖАТИ»), і форма з
   атрибутом `<ФАЙЛ path="…">…</ФАЙЛ>`, якою відповідач віддає код: парсер її читає, тож і
   чекати треба саме на неї, інакше одиниця коду висить до стелі очікування. */
const closedTags = (txt) => {
  const s = String(txt || "");
  const out = new Set();
  for (const m of s.matchAll(/<([А-ЯІЇЄҐA-Z][^<>\n]*)>[\s\S]*?<\/\1>/g)) out.add(m[1].trim());
  for (const m of s.matchAll(/<([А-ЯІЇЄҐA-Z][^<>\s]*)\s[^<>\n]*=[^<>\n]*>[\s\S]*?<\/\1>/g)) out.add(m[1].trim());
  return out;
};

/** Теги контракту завдання — для його кроку, якщо кроків кілька. */
function expected(prompt) {
  const m = /<ПОВЕРНИ>([\s\S]*?)<\/ПОВЕРНИ>/.exec(String(prompt || ""));
  if (!m) return [];
  const step = (/^крок: (\d+)\s*$/m.exec(prompt) || [])[1];
  const chunks = [];
  let cur = { step: null, text: "" };
  for (const line of m[1].split("\n")) {
    const s = /^Крок (\d+):/.exec(line);
    if (s) { chunks.push(cur); cur = { step: s[1], text: "" }; } else cur.text += line + "\n";
  }
  chunks.push(cur);
  const mine = step ? chunks.filter((c) => c.step === step) : [];
  const tags = [];
  for (const c of mine.length ? mine : chunks)
    for (const t of c.text.matchAll(TAG)) if (!tags.includes(t[1].trim())) tags.push(t[1].trim());
  return tags;
}

/** Готово: усі теги контракту закрито; або перший закрито й файл давно не мінявся. */
function ready(txt, tags, stableFor = Infinity) {
  const closed = closedTags(txt);
  if (!tags || !tags.length) return closed.size > 0;
  if (tags.every((t) => closed.has(t))) return true;
  return closed.has(tags[0]) && stableFor >= STABLE;
}

/** Ім'я файла з мітки: кирилиця лишається, ламається лише те, що ламає файлову систему. */
const safe = (s) => String(s).replace(/[^\p{L}\p{N}._-]+/gu, "-").slice(0, 60);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * ⚠️ АДАПТЕР — ФАБРИКА, А НЕ ГОЛА ФУНКЦІЯ. Тека в кожної одиниці своя, а в пулі їх
 * кілька воднораз; один спільний стан (чи змінна середовища) звів би завдання двох
 * різних одиниць в одну теку й переплутав би нумерацію.
 */
module.exports.make = function make(dir) {
  fs.mkdirSync(dir, { recursive: true });

  return async function ask(prompt, label) {
    /* ⚠️ ІМ'Я ФАЙЛА — ЗА МІТКОЮ, А НЕ ЗА ЛІЧИЛЬНИКОМ ВИКЛИКІВ. Мітка одиниці унікальна
       («каркас», «письмо 1,2», «викладка 3»), а лічильник щоразу починається з одиниці:
       піднятий батч пропускає вже пройдені етапи, тож перший його запит діставав номер
       01 і повз збережену відповідь із номером 05 — і все, на що вже відповіли, питали б
       наново. */
    const base = path.join(dir, safe(label));
    const askFile = `${base}.ask.txt`;
    const ansFile = `${base}.ans.txt`;

    const tags = expected(prompt);

    /* Відповідь із минулого прогону беремо як є: саме так підіймається обірваний
       батч, не перепитуючи те, на що вже відповіли. Файл, що лежить давно, — стабільний. */
    if (fs.existsSync(ansFile)) {
      const txt = fs.readFileSync(ansFile, "utf8");
      if (ready(txt, tags, Date.now() - fs.statSync(ansFile).mtimeMs)) return txt;
    }

    fs.writeFileSync(askFile, prompt, "utf8");
    process.stdout.write(`\n[ЗАПИТ] ${label}\n[ФАЙЛ]  ${askFile}\n[ЧЕКАЮ] ${ansFile}\n`);

    const until = Date.now() + WAIT;
    let last = null, since = 0;
    while (Date.now() < until) {
      if (fs.existsSync(ansFile)) {
        const txt = fs.readFileSync(ansFile, "utf8");
        /* Порожній чи напівзаписаний файл — це «ще пишуть», а не відповідь: інакше
           перший же дотик до файла зарахувався б за готову й конвеєр пішов би далі з
           половиною тексту. Читаємо один раз і віддаємо саме прочитане. */
        if (txt !== last) { last = txt; since = Date.now(); }
        if (ready(txt, tags, Date.now() - since)) { process.stdout.write(`[ВІДПОВІДЬ] ${label} — ${txt.length} симв.\n`); return txt; }
      }
      await sleep(POLL);
    }
    throw new Error(`ніхто не відповів на «${label}» за ${Math.round(WAIT / 60000)} хв`);
  };
};

module.exports.expected = expected;
module.exports.ready = ready;
