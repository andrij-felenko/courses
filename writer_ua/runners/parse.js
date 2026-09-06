#!/usr/bin/env node
/* ============================================================================
   parse.js — РОЗБІР ВІДПОВІДІ. Блоки туди, блоки назад.

   Відповідь приходить тими самими блоками, що й запит: `<ТЕКСТ>…</ТЕКСТ>`. Тут її
   розбирають — і на цьому вся робота: якщо блоку немає, це помилка кроку, а не привід
   вгадувати. Доти конвеєри розбирали прозу регулярками, і один промах давав сміття
   наступному кроку за повну ціну.

   ⛔ ЧОГО ТУТ НЕМАЄ: здогадів. Немає блоку — `missing`, і рішення ухвалює алгоритм.
   ========================================================================== */
"use strict";

/** Усі блоки відповіді як {ТЕГ: текст}. Однакові теги склеюються рядками. */
function blocks(text) {
  const out = {};
  const re = /<([А-ЯІЇЄҐA-Z][^<>\n]*?)>([\s\S]*?)<\/\1>/g;
  let m;
  while ((m = re.exec(String(text || "")))) {
    const tag = m[1].trim(), body = m[2].trim();
    /* ⛔ ДОСЛІВНИЙ ПОВТОР НЕ СКЛЕЮЄМО. Агент, що перечитав своє завдання, повторює
       відповідь цілком — і склейка перетворювала це на текст, написаний двічі. Заміряно
       на живому: дев'ять вставок із дев'яти, тіло дослівно × 2, у файлі два H1.
       Різні тіла склеюємо як раніше: це законне продовження довгої відповіді. */
    if (out[tag] === undefined) out[tag] = body;
    else if (out[tag] !== body && !out[tag].endsWith(body)) out[tag] += "\n" + body;
  }
  return out;
}

/**
 * Усі блоки з ОДНИМ тегом — окремо, масивом. `blocks()` склеює однакові теги в один
 * рядок, і для `<ФАЙЛ>` це втратило б межу між файлами.
 */
function repeated(text, tag) {
  const out = [];
  const re = new RegExp(`<${tag}>([\\s\\S]*?)<\\/${tag}>`, "g");
  let m;
  while ((m = re.exec(String(text || "")))) out.push(m[1].trim());
  return out;
}

/** `<ФАЙЛ>шлях :: що робить\nвміст</ФАЙЛ>` → [{path, about, body}] */
function files(text) {
  return repeated(text, "ФАЙЛ").map((b) => {
    const nl = b.indexOf("\n");
    const head = nl < 0 ? b : b.slice(0, nl);
    const m = /^(\S+)\s*(?:::\s*(.*))?$/.exec(head.trim());
    if (!m) return null;
    return { path: m[1], about: (m[2] || "").trim(), body: nl < 0 ? "" : b.slice(nl + 1).replace(/^\n+/, "") };
  }).filter(Boolean);
}

/**
 * Витягти названі блоки. Повертає {дані, missing:[теги]} — і НЕ кидає: провал одного
 * блоку не має валити крок, поки алгоритм не вирішив, що він обов'язковий.
 */
function want(text, tags) {
  const b = blocks(text), data = {}, missing = [];
  for (const t of tags) {
    if (b[t] === undefined) missing.push(t);
    else data[t] = b[t];
  }
  return { data, missing, all: b };
}

/* ── дрібні розбори, спільні для кількох етапів ─────────────────────────────── */

const lines = (s) => String(s || "").split("\n").map((x) => x.trim()).filter(Boolean);

/** Порожньо — це «нема чого додати», а не збій. Так і домовлено. */
const empty = (s) => {
  const t = String(s || "").trim().toLowerCase();
  /* ⛔ «ПУСТОТА» ТУТ ОБОВ'ЯЗКОВА: саме це слово пропонує контракт («немає — поверни
     пустоту»), і без нього відповідь ставала ЗНАЧЕННЯМ — тема на ім'я «пустота» їхала в
     нові теми, а розділ із «пустотою» в «Що зжати» вважався жирним і йшов у стиснення. */
  return !t || t === "—" || t === "-" || t === "н/д" || t === "порожньо"
    || t === "пустота" || t === "нічого" || t === "немає" || t === "жодних";
};

const yes = (s) => /^\s*(так|yes|ок|ok)\b/i.test(String(s || ""));

/** `1 | важливість: висока | питання…` → {n, importance, text} */
function sections(s) {
  return lines(s).map((l) => {
    const m = /^(\d+)\s*\|\s*важливість:\s*([^|]+)\|\s*([\s\S]+)$/i.exec(l);
    return m ? { n: Number(m[1]), importance: m[2].trim(), text: m[3].trim() } : null;
  }).filter(Boolean);
}

/** `1, 2, 3` по рядку → [[1,2,3], …] */
function groups(s) {
  const seen = new Set();
  /* ⛔ ОДНАКОВІ ГРУПИ ЗГОРТАЄМО. Кожна група — це окремий виклик письма, і два однакові
     рядки давали два однакові виклики, чиї тексти потім склеювались у файл підряд. Той
     самий дослівний повтор, тільки з іншого боку. */
  return lines(s).map((l) => (l.match(/\d+/g) || []).map(Number)).filter((g) => {
    if (!g.length) return false;
    const key = [...g].sort((a, b) => a - b).join(",");
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

/**
 * `proj-circuit-breaker | що саме там має бути` → {insert, name, about}.
 *
 * Тип — лише з п'яти, і він частина імені: інше слово перед дефісом — не вставка, і рядок
 * відкидається. Стару форму «тип | ім'я | розділ n | про що» ще читаємо, розділ викидаємо:
 * куди вставку інтегрувати, вирішує письмо.
 */
function inserts(s) {
  return lines(s).map((l) => {
    let m = /^(hist|comp|math|proj|api)-([a-z0-9][a-z0-9-]*)\s*\|\s*([\s\S]+)$/i.exec(l);
    if (m) return { insert: m[1].toLowerCase(), name: m[2].toLowerCase(), about: m[3].trim() };
    m = /^(?:тип\s*\d\s*\|\s*)?(hist|comp|math|proj|api)\s*\|\s*(?:([a-z0-9][a-z0-9-]*)\s*\|\s*)?(?:[^\d|]*?\s*)?(?:[\d—-]+)\s*\|\s*([\s\S]+)$/i.exec(l);
    return m ? { insert: m[1].toLowerCase(), name: (m[2] || "").toLowerCase(), about: m[3].trim() } : null;
  }).filter(Boolean);
}

/** `3 | що можна стиснути` → {section, text}; рядок без номера — section null. */
function bySection(s) {
  return lines(s).map((l) => {
    const m = /^\s*(?:[^\d|]*?\s*)?(\d+)\s*\|\s*([\s\S]+)$/.exec(l);
    return m ? { section: Number(m[1]), text: m[2].trim() } : { section: null, text: l.trim() };
  }).filter((x) => x.text && !empty(x.text));
}

/** `1, 2, 3 | 8 | чому` → {groups:[1,2,3], score, why}. Оцінки етапу аналізу. */
function scores(s) {
  return lines(s).map((l) => {
    const p = l.split("|").map((x) => x.trim());
    if (p.length < 2) return null;
    const score = Number((p[1].match(/\d+/) || [])[0]);
    if (!Number.isFinite(score)) return null;
    return { groups: (p[0].match(/\d+/g) || []).map(Number), score, why: p.slice(2).join(" | ") };
  }).filter(Boolean);
}

/** `старе речення :: нове речення` → {from, to}. */
function replacements(s) {
  return lines(s).map((l) => {
    const m = /^([\s\S]+?)\s*::\s*([\s\S]+)$/.exec(l);
    return m && m[1].trim() && m[2].trim() ? { from: m[1].trim(), to: m[2].trim() } : null;
  }).filter(Boolean);
}

/** `<ВЕРДИКТ>` етапу 8: {kind, slug}. */
function verdict(s) {
  const t = String(s || "").trim().toLowerCase();
  const m = /^є\s*\|\s*([a-z0-9][a-z0-9-]*)/i.exec(t);
  if (m) return { kind: "є", slug: m[1].toLowerCase() };
  if (/^нов/.test(t)) return { kind: "нова", slug: "" };
  if (/^дубл/.test(t)) return { kind: "дубль", slug: "" };
  if (/^різн/.test(t)) return { kind: "різні", slug: "" };
  return { kind: "", slug: "" };
}

/** `слуг | точніша назва` → {slug, title}. */
function names(s) {
  return lines(s).map((l) => {
    const m = /^([a-z0-9][a-z0-9-]*)\s*\|\s*([\s\S]+)$/i.exec(l);
    return m ? { slug: m[1].toLowerCase(), title: m[2].trim() } : null;
  }).filter(Boolean);
}

/**
 * `Назва — root:книга/тема — що саме знати` → {title, addr, why}.
 *
 * ⛔ Рядок без адреси відкидаємо. Передумова без цілі — обіцянка в порожнечу, і саме такі
 * рядки псували корпус, коли адресу дозволяли складати самому.
 */
function preknow(s) {
  return lines(s).map((l) => {
    const m = /^(.+?)\s+[—-]\s+(root:[a-z0-9][a-z0-9-]*\/[a-z0-9][a-z0-9-]*)\s*(?:[—-]\s*([\s\S]+))?$/i.exec(l);
    return m ? { title: m[1].trim(), addr: m[2].trim(), why: (m[3] || "").trim() } : null;
  }).filter(Boolean);
}

/**
 * `розділ 5 | що зображено` → {section, what}.
 *
 * ⛔ СЛОВО ПЕРЕД ЧИСЛОМ — БУДЬ-ЯКЕ. Одиницю каркаса кожен тип зве по-своєму, і контракт
 * так і просить: «розділ» у статті, «подія» в історії, «крок» у виведенні й проєкті.
 * Парсер знав саме «розділ» — отже в трьох типах із семи фігури не виникали ЖОДНОЇ, і
 * мовчки: агент відповідав рівно як просили, розбір давав нуль рядків, крок ішов далі.
 * Перелічувати ті слова тут не можна — назву одиниці вигадує контракт, не розбір.
 */
function figures(str) {
  return lines(str).map((l) => {
    const m = /^(?:[^\d|]*?\s*)?(\d+)\s*\|\s*([\s\S]+)$/i.exec(l);
    return m ? { section: Number(m[1]), what: m[2].trim() } : null;
  }).filter(Boolean);
}

/**
 * `Python | що реалізує` або `розділ 5 | Python | що реалізує` → {section, lang, what}.
 *
 * ⚠️ РОЗДІЛ НЕОБОВ'ЯЗКОВИЙ: код замовляють на запиті «рівень і вставки», де розділів ще
 * немає. Без розділу він прив'язується до всіх груп — шляхи справжні, і письменник
 * цитує їх там, де вони доречні.
 *
 * ⛔ СЛОВО ПЕРЕД ЧИСЛОМ — БУДЬ-ЯКЕ, з тієї ж причини, що й у фігурах: одиницю каркаса
 * кожен тип зве по-своєму. Тут промах коштував дорожче за порожнечу — «крок 3 | python»
 * розбиралося в МОВУ «крок 3», бо необов'язкова група не збігалась, а решту рядка їла
 * колонка мови. Тека коду діставала ім'я «крок 3», і директиви на неї не сходились.
 */
function code(s) {
  return lines(s).map((l) => {
    const m = /^(?:(?:[^\d|]*?\s*)?(\d+)\s*\|)?\s*([^|]+?)\s*\|\s*([\s\S]+)$/i.exec(l);
    return m ? { section: m[1] ? Number(m[1]) : null, lang: m[2].trim(), what: m[3].trim() } : null;
  }).filter(Boolean);
}

/**
 * `4 | що саме додати` → [{level, what}], від найбільшого рівня до найменшого.
 *
 * ⚠️ ПЕРЕЛІК НЕ БУВАЄ ПОРОЖНІМ — так каже завдання, і на це спирається дописування:
 * доти письменникові дозволяли повернути пустоту, і він майже завжди її й повертав,
 * бо це дешевше за думання. Тоді етап розміру не мав НАЗВАНОГО матеріалу, і коротка
 * стаття лишалася короткою. Рядок без рівня не викидаємо — беремо його за одиницю:
 * назване без числа все одно варте більше, ніж не назване.
 */
function additions(s) {
  return lines(s).map((l) => {
    /* Нова форма — з розділом: `3 | 5 | що`. Стара `5 | що` — без розділу. */
    let m = /^\s*(?:[^\d|]*?\s*)?(\d+)\s*\|\s*([1-5])\s*\|\s*([\s\S]+)$/.exec(l);
    if (m) return { section: Number(m[1]), level: Number(m[2]), what: m[3].trim() };
    m = /^\s*([1-5])\s*[|.)–—-]\s*([\s\S]+)$/.exec(l);
    return m ? { section: null, level: Number(m[1]), what: m[2].trim() } : { section: null, level: 1, what: l.trim() };
  }).filter((x) => x.what && !empty(x.what)).sort((a, b) => b.level - a.level);
}

/**
 * `trie-compression | Стиснення вузлів префіксного дерева` → {slug, title}.
 *
 * ⛔ СЛУГ ОБОВ'ЯЗКОВИЙ, і саме тому його просять. Тему, названу самим лише заголовком,
 * завести не можна: слуг довелося б виводити транслітерацією, а корпус іменує теми
 * англійськими термінами, не українськими словами. Без слуга тема лишалась назвою в
 * переліку, стаття не мала на неї адреси й тому не ставила лінка — матеріал зникав.
 */
function topics(s) {
  return lines(s).map((l) => {
    const p = l.split("|").map((x) => x.trim());
    if (p.length < 2 || !/^[a-z0-9][a-z0-9-]{2,}$/i.test(p[0]) || !p[1]) return null;
    return { slug: p[0].toLowerCase(), title: p[1], where: p[2] || "", about: p.slice(3).join(" | ") };
  }).filter(Boolean);
}

/** `абзац 3 :: що не так` → {where, why} */
function defects(s) {
  return lines(s).map((l) => {
    const m = /^(.+?)\s*::\s*([\s\S]+)$/.exec(l);
    return m ? { where: m[1].trim(), why: m[2].trim() } : { where: "", why: l };
  });
}

module.exports = {
  blocks, repeated, files, want, lines, empty, yes, sections, groups, inserts, code, figures,
  preknow, topics, additions, defects, bySection, scores, replacements, verdict, names,
};
