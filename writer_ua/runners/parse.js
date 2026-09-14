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

/**
 * ⛔ ОБГОРТКА <ПОВЕРНИ> — НЕ БЛОК ВІДПОВІДІ. Контракт завдання перелічує блоки всередині
 * `<ПОВЕРНИ>…</ПОВЕРНИ>`, і відповідач часом віддає їх у тій самій обгортці: 56 відповідей
 * за один батч (09.09), доти — жодної. Лінивий розбір брав обгортку як єдиний блок і не
 * бачив жодного внутрішнього — «немає ТЕКСТ», «не повернув жодного розділу», «немає
 * ОЦІНКА»: 28 зламаних одиниць із 31. Обгортку знімаємо до розбору; блоків це не торкається.
 */
const unwrap = (s) => String(s || "").replace(/\r\n?/g, "\n").replace(/<\/?ПОВЕРНИ>/g, "");

/* Обгортка буває й з іншим ім'ям — за назвою етапу: <АНАЛІЗ>…</АНАЛІЗ>, <ФІГУРА>…</ФІГУРА>
   (по три на батч, «немає ОЦІНКА», «немає SVG»). Ознака — один-єдиний блок, а всередині
   закриті блоки. Блоки, що самі є вмістом, усередину не розбираємо. */
const CONTENT_TAGS = new Set(["ТЕКСТ", "ФАЙЛ", "SVG", "ЦІЛЬ"]);
const NESTED = /<([А-ЯІЇЄҐA-Z][^<>\n]*?)>[\s\S]*?<\/\1>/;

/** Усі блоки відповіді як {ТЕГ: текст}. Однакові теги склеюються рядками. */
function blocks(text) {
  const out = rawBlocks(unwrap(text));
  const k = Object.keys(out);
  if (k.length === 1 && !CONTENT_TAGS.has(k[0]) && NESTED.test(out[k[0]])) return blocks(out[k[0]]);
  return out;
}

function rawBlocks(s) {
  const out = {};
  const re = /<([А-ЯІЇЄҐA-Z][^<>\n]*?)>([\s\S]*?)<\/\1>/g;
  let m;
  while ((m = re.exec(s))) {
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
  const s = unwrap(text);
  let m;
  while ((m = re.exec(s))) out.push(m[1].trim());
  return out;
}

/**
 * `<ФАЙЛ>шлях :: що робить\nвміст</ФАЙЛ>` → [{path, about, body}].
 *
 * ⛔ ШЛЯХ В АТРИБУТІ — ТЕЖ ШЛЯХ. Контракт просить його першим рядком, а агент відповідає
 * й `<ФАЙЛ path="quadrature_decoder.h">`: на живому — сім файлів із семи в C і чотири з
 * чотирьох у C++, і всі губились: обидві одиниці коду падали «немає жодного блоку <ФАЙЛ>»,
 * а проєкт лишався на паузі назавжди. Це не здогад — шлях названо явно, лише в іншому
 * місці; здогадом було б брати ім'я з коментаря у вмісті, і цього тут немає.
 */
function files(text) {
  const out = [];
  const re = /<ФАЙЛ(?:\s+[^<>]*?(?:path|file|шлях|файл)\s*=\s*["']([^"']+)["'][^<>]*)?>([\s\S]*?)<\/ФАЙЛ>/g;
  const s = unwrap(text);
  let m;
  while ((m = re.exec(s))) {
    const attr = m[1] ? m[1].trim() : "";
    const b = m[2].trim();
    const nl = b.indexOf("\n");
    const head = nl < 0 ? b : b.slice(0, nl);
    const h = /^(\S+)\s*(?:::\s*(.*))?$/.exec(head.trim());
    if (attr) {
      /* Перший рядок повторює шлях з атрибута — це шапка, не код; інакше все — вміст. */
      const cap = h && h[1] === attr;
      out.push({ path: attr, about: cap ? (h[2] || "").trim() : "", body: cap ? (nl < 0 ? "" : b.slice(nl + 1).replace(/^\n+/, "")) : b });
    } else if (h) {
      out.push({ path: h[1], about: (h[2] || "").trim(), body: nl < 0 ? "" : b.slice(nl + 1).replace(/^\n+/, "") });
    }
  }
  return out;
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

/**
 * ⛔ `\b` ІЗ КИРИЛИЦЕЮ НЕ ПРАЦЮЄ — межа слова знає лише `[A-Za-z0-9_]`, і після «к» у «так»
 * її НЕМА. `/^(так)\b/` не збігалося з «так» ЖОДНОГО разу, тобто `<БАЗОВА>так</БАЗОВА>`
 * етапу 2 не читалося взагалі: базову заводив лише поріг обсягу. Тут — заперечний погляд
 * уперед на будь-яку літеру чи цифру: він мовою не обмежений.
 */
const yes = (s) => /^\s*(так|yes|ок|ok)(?!\p{L}|\p{N})/iu.test(String(s || ""));

/**
 * `1 | важливість: висока | питання…` → {n, importance, text}.
 *
 * ⛔ СЛОВО «важливість:» — НЕОБОВ'ЯЗКОВЕ. Контракт його показує, а агент часто пише лише
 * значення: `1 | висока | …`. Парсер, що вимагав ярлик, дав «каркас: не повернув жодного
 * розділу» на трьох вставках одного батчу, хоч розділи в відповіді були всі. Значення
 * в другій колонці однозначне й без ярлика.
 */
function sections(s) {
  const out = [];
  const IMP = /^(?:важливість\s*:\s*)?(висока|середня|низька)$/i;
  for (const l of lines(s)) {
    const p = l.split("|").map((x) => x.trim());
    const n = p.length >= 3 ? secNo(p[0]) : null;
    const at = n == null ? -1 : p.findIndex((c, i) => i > 0 && IMP.test(c));
    if (at > 0) {
      /* `номер | назва | важливість | ціль` (автор, 14.09: назва окремо від цілі розділу —
         заголовком ставало речення плану на 8–25 слів) або стара `номер | важливість | опис`.
         Колонку важливості знаходимо за словом, а не за місцем: агент ставить її і другою,
         і третьою. */
      const rest = p.filter((_, i) => i > 0 && i !== at);
      const title = rest.length >= 2 ? rest[0] : "";
      out.push({ n, title, importance: IMP.exec(p[at])[1].toLowerCase(), text: (rest.length >= 2 ? rest.slice(1) : rest).join(" | ") });
    }
    /* Рядок без номера після розділу — продовження його опису («На вході: …», «На виході:
       …»): 44 таких рядки за батч губились, і план розділу ставав коротшим за задуманий. */
    else if (out.length && !/^<\//.test(l)) out[out.length - 1].text += " " + l;
  }
  return out;
}

/**
 * `hist-birth | коротка | 2` → {key, mode: "short"|"full", section}. Форма вставок з каркаса
 * (автор, 14.09): коротка — абзац у тексті названого розділу, повна — окремий файл і
 * одиниця. Рядок без вердикту — повна: так було завжди, і це безпечніший бік.
 */
function insertForms(s) {
  return lines(s).map((l) => {
    const p = l.split("|").map((x) => x.trim());
    const m = /^(hist|comp|math|proj|api)-([a-z0-9][a-z0-9-]*)/i.exec(p[0] || "");
    if (!m) return null;
    const short = p.slice(1).some((c) => /^коротк/i.test(c));
    const full = p.slice(1).some((c) => /^повн/i.test(c));
    const secCol = p.slice(1).find((c) => secNo(c) != null);
    return { key: `${m[1].toLowerCase()}-${m[2].toLowerCase()}`, mode: short && !full ? "short" : "full", section: secCol ? secNo(secCol) : null };
  }).filter(Boolean);
}

/** `1, 2, 3` по рядку → [[1,2,3], …] */
function groups(s) {
  const seen = new Set();
  /* ⛔ ОДНАКОВІ ГРУПИ ЗГОРТАЄМО. Кожна група — це окремий виклик письма, і два однакові
     рядки давали два однакові виклики, чиї тексти потім склеювались у файл підряд. Той
     самий дослівний повтор, тільки з іншого боку. */
  return lines(s).map((l) => [...new Set((l.match(/\d+/g) || []).map(Number))]).filter((g) => {
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
    if (m) {
      /* `тип-ім'я | назва | що там` — назва вставки з етапу 2 стає її заголовком (автор, 14.09);
         `тип-ім'я | що там` — стара форма, без назви. */
      const rest = m[3].split("|").map((x) => x.trim()).filter(Boolean);
      const title = rest.length >= 2 ? rest[0] : "";
      return { insert: m[1].toLowerCase(), name: m[2].toLowerCase(), title, about: (rest.length >= 2 ? rest.slice(1) : rest).join(" | ") };
    }
    m = /^(?:тип\s*\d\s*\|\s*)?(hist|comp|math|proj|api)\s*\|\s*(?:([a-z0-9][a-z0-9-]*)\s*\|\s*)?(?:[^\d|]*?\s*)?(?:[\d—-]+)\s*\|\s*([\s\S]+)$/i.exec(l);
    return m ? { insert: m[1].toLowerCase(), name: (m[2] || "").toLowerCase(), about: m[3].trim() } : null;
  }).filter(Boolean);
}

/**
 * `3 | що можна стиснути` → {section, text}; рядок без номера — section null.
 *
 * ⛔ РОЗДІЛ НАЗВАНО ЗАГОЛОВКОМ — ТЕЖ РОЗДІЛ. Контракт каже `{розділ}`, і писар ставить туди
 * заголовок H2, не номер: 923 із 2 312 рядків «ЩО ДОДАТИ» і 411 із 898 «ЩО ЗЖАТИ» за три батчі.
 * Доти такий рядок ішов у перший розділ порції, а рівень 5 ставав 1. Тут — {section: null,
 * title}; номер за заголовком знаходить алгоритм, бо текст порції є лише в нього.
 */
function bySection(s) {
  return lines(s).map((l) => {
    const p = l.split("|").map((x) => x.trim());
    if (p.length < 2) return { section: null, text: l.trim() };
    const n = secNo(p[0]);
    const base = n == null ? { section: null, title: p[0] } : { section: n };
    /* `розділ | як | що` — «де дописати» з абзацом (автор, 14.09). */
    const how = p.length >= 3 ? howOf(p[1]) : null;
    return how ? { ...base, kind: how.kind, anchor: how.anchor, text: p.slice(2).join(" | ") } : { ...base, text: p.slice(1).join(" | ") };
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

/**
 * `нитка | 2 | чому` → {name, score, why}. Бали аналізу за критеріями (автор, 14.09): бал
 * нараховується, не знімається; перша колонка — ім'я критерію, не номери розділів.
 */
function points(s) {
  return lines(s).map((l) => {
    const p = l.split("|").map((x) => x.trim());
    if (p.length < 2) return null;
    const score = Number((p[1].match(/\d+(?:[.,]\d+)?/) || [""])[0].replace(",", "."));
    if (!Number.isFinite(score)) return null;
    return { name: p[0], score, why: p.slice(2).join(" | ") };
  }).filter(Boolean);
}

/** `перші слова | точне|неточне|невідомо | джерело` → {head, verdict, source}. Перевірка фактів. */
function verdicts(s) {
  return lines(s).map((l) => {
    const p = l.split("|").map((x) => x.trim());
    if (p.length < 2) return null;
    const v = p[1].toLowerCase();
    const verdict = /^точн/.test(v) ? "точне" : /^неточн|^хибн/.test(v) ? "неточне" : /^невідом|^не перевір/.test(v) ? "невідомо" : null;
    return verdict ? { head: p[0], verdict, source: p.slice(2).join(" | ") } : null;
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
    /* Роздільник — тире, як у контракті, або вертикальна риска, як усюди: писар плутає. */
    const m = /^(.+?)\s*[—|-]\s*(root:[a-z0-9][a-z0-9-]*\/[a-z0-9][a-z0-9-]*)\s*(?:[—|-]\s*([\s\S]+))?$/i.exec(l);
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
  /* Ім'я писар дає і з `img/`, і з `.svg` (254 із 494 рядків «НОВІ SVG» за три батчі губились
     саме на цьому) — зрізаємо обидва: ім'я — лише за тим, що зображено. */
  const clean = (n) => String(n || "").trim().replace(/^img\//i, "").replace(/\.svg$/i, "").toLowerCase();
  return lines(str).map((l) => {
    /* Друга колонка — ім'я латиницею за тим, що зображено; без неї — лише опис. */
    let m = /^(?:[^\d|]*?\s*)?(\d+)\s*\|\s*(?:(?:img\/)?([a-z0-9][a-z0-9-]*)(?:\.svg)?\s*\|\s*)?([\s\S]+)$/i.exec(l);
    if (m) return { section: Number(m[1]), name: clean(m[2]), what: m[3].trim() };
    /* Розділ названо заголовком: тоді ім'я обов'язкове — інакше не відрізнити від опису. */
    m = /^\s*([^|]+?)\s*\|\s*(?:img\/)?([a-z0-9][a-z0-9-]*)(?:\.svg)?\s*\|\s*([\s\S]+)$/i.exec(l);
    return m ? { section: null, title: m[1].trim(), name: clean(m[2]), what: m[3].trim() } : null;
  }).filter(Boolean);
}

/** `слуг | Назва | scope одним реченням` → {slug, title, scope}. Нова група чи розділ. */
function place(s) {
  const p = String(s || "").split("|").map((x) => x.trim());
  if (p.length < 2 || !/^[a-z0-9][a-z0-9-]*$/i.test(p[0]) || !p[1]) return null;
  return { slug: p[0].toLowerCase(), title: p[1], scope: p.slice(2).join(" | ") };
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
/** Рядки з колонками через `|`, обрізані; порожні й «пустота» — геть. */
const cols = (s) => lines(s).filter((l) => !empty(l)).map((l) => l.split("|").map((x) => x.trim()));

/** `поглибити «перші слова абзацу»` / `новий після «перші слова абзацу»` → {kind, anchor}. */
function howOf(s) {
  const t = String(s || "").trim();
  const q = (x) => String(x || "").replace(/^[«"“'`\s]+|[»"”'`.\s]+$/g, "").trim();
  let m = /^поглиб\S*\s*(?:абзац\S*\s*)?(.*)$/i.exec(t);
  if (m) return { kind: "deepen", anchor: q(m[1]) };
  m = /^нов\S*\s*(?:абзац\S*\s*)?(?:після\s*)?(.*)$/i.exec(t);
  if (m) return { kind: "new", anchor: q(m[1]) };
  return null;
}

const secNo = (x) => { const m = /^(?:[^\d|]*?\s*)?(\d+)\s*$/.exec(String(x || "")); return m ? Number(m[1]) : null; };
const levelNo = (x) => (/^[1-5]$/.test(String(x || "").trim()) ? Number(x) : null);

/**
 * `розділ | рівень | як | що` → {section, level, kind, anchor, what}; коротші форми —
 * `розділ | рівень | що`, `рівень | що`, голий рядок. Розділ буває й заголовком (title).
 * «Як» — поглибити названий абзац або новий після названого (автор, 14.09).
 */
function additions(s) {
  return lines(s).map((l) => {
    const p = l.split("|").map((x) => x.trim());
    const base = (secCol) => { const n = secNo(secCol); return n == null ? { section: null, title: secCol } : { section: n }; };
    if (p.length >= 4 && levelNo(p[1]) != null) {
      const how = howOf(p[2]);
      return how ? { ...base(p[0]), level: levelNo(p[1]), kind: how.kind, anchor: how.anchor, what: p.slice(3).join(" | ") }
        : { ...base(p[0]), level: levelNo(p[1]), what: p.slice(2).join(" | ") };
    }
    if (p.length === 3 && levelNo(p[1]) != null) return { ...base(p[0]), level: levelNo(p[1]), what: p[2] };
    if (p.length >= 2 && levelNo(p[0]) != null) return { section: null, level: levelNo(p[0]), what: p.slice(1).join(" | ") };
    const m = /^\s*([1-5])\s*[.)–—-]\s*([\s\S]+)$/.exec(l);
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
    /* Слуг із префіксом книги — `progarch_cqrs`, `progarch/cqrs` (18 рядків за батч) — це слуг
       і книга разом; книгу вирішує етап 8, префікс зрізаємо. */
    if (p[0]) p[0] = p[0].replace(/^[a-z0-9-]+[_/](?=[a-z0-9])/i, "");
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
  unwrap, blocks, repeated, files, want, lines, cols, empty, yes, howOf, sections, groups, inserts, code, figures,
  preknow, topics, additions, defects, bySection, scores, points, insertForms, replacements, verdicts, verdict, names, place,
};
