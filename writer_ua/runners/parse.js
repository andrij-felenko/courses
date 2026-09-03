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
  const re = /<([А-ЯA-Z][^<>\n]*?)>([\s\S]*?)<\/\1>/g;
  let m;
  while ((m = re.exec(String(text || "")))) {
    const tag = m[1].trim(), body = m[2].trim();
    out[tag] = out[tag] === undefined ? body : out[tag] + "\n" + body;
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
  return !t || t === "—" || t === "-" || t === "н/д" || t === "порожньо" || t === "нічого" || t === "немає";
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
  return lines(s).map((l) => (l.match(/\d+/g) || []).map(Number)).filter((g) => g.length);
}

/** `тип 2 | proj | розділ 5 | про що` → {kind, insert, section, about} */
function inserts(s) {
  return lines(s).map((l) => {
    /* Ім'я НЕобов'язкове в розборі, хоч і просять його завжди: без нього рядок усе одно
       читається, а вставка дістає ім'я за темою. Вимагати його тут означало б викинути
       весь каркас через одну колонку. */
    const m = /^тип\s*(\d)\s*\|\s*([a-z]+)\s*\|\s*(?:([a-z0-9][a-z0-9-]*)\s*\|\s*)?(?:розділ\s*)?([\d—-]+)\s*\|\s*([\s\S]+)$/i.exec(l);
    if (!m) return null;
    const sec = /^\d+$/.test(m[4]) ? Number(m[4]) : null;
    return {
      kind: Number(m[1]), insert: m[2].toLowerCase(),
      name: (m[3] || "").toLowerCase(), section: sec, about: m[5].trim(),
    };
  }).filter(Boolean);
}

/** `розділ 5 | Python | що реалізує` → {section, lang, what} */
function code(s) {
  return lines(s).map((l) => {
    const m = /^(?:розділ\s*)?(\d+)\s*\|\s*([^|]+)\|\s*([\s\S]+)$/i.exec(l);
    return m ? { section: Number(m[1]), lang: m[2].trim(), what: m[3].trim() } : null;
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
    const m = /^\s*([1-5])\s*[|.)–—-]\s*([\s\S]+)$/.exec(l);
    return m ? { level: Number(m[1]), what: m[2].trim() } : { level: 1, what: l.trim() };
  }).filter((x) => x.what && !empty(x.what)).sort((a, b) => b.level - a.level);
}

/** `абзац 3 :: що не так` → {where, why} */
function defects(s) {
  return lines(s).map((l) => {
    const m = /^(.+?)\s*::\s*([\s\S]+)$/.exec(l);
    return m ? { where: m[1].trim(), why: m[2].trim() } : { where: "", why: l };
  });
}

module.exports = { blocks, repeated, files, want, lines, empty, yes, sections, groups, inserts, code, additions, defects };
