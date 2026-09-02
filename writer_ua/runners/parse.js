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
  return !t || t === "—" || t === "-" || t === "н/д" || t === "порожньо" || t === "нічого";
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
    const m = /^тип\s*(\d)\s*\|\s*([a-z]+)\s*\|\s*(?:розділ\s*)?([\d—-]+)\s*\|\s*([\s\S]+)$/i.exec(l);
    if (!m) return null;
    const sec = /^\d+$/.test(m[3]) ? Number(m[3]) : null;
    return { kind: Number(m[1]), insert: m[2].toLowerCase(), section: sec, about: m[4].trim() };
  }).filter(Boolean);
}

/** `розділ 5 | Python | що реалізує` → {section, lang, what} */
function code(s) {
  return lines(s).map((l) => {
    const m = /^(?:розділ\s*)?(\d+)\s*\|\s*([^|]+)\|\s*([\s\S]+)$/i.exec(l);
    return m ? { section: Number(m[1]), lang: m[2].trim(), what: m[3].trim() } : null;
  }).filter(Boolean);
}

/** `абзац 3 :: що не так` → {where, why} */
function defects(s) {
  return lines(s).map((l) => {
    const m = /^(.+?)\s*::\s*([\s\S]+)$/.exec(l);
    return m ? { where: m[1].trim(), why: m[2].trim() } : { where: "", why: l };
  });
}

module.exports = { blocks, want, lines, empty, yes, sections, groups, inserts, code, defects };
