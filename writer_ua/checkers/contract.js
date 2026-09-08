#!/usr/bin/env node
/* ============================================================================
   contract.js — ЧИ РОЗБЕРЕ ПАРСЕР ТЕ, ЩО ПРОСИТЬ КОНТРАКТ.

   Правила диктують агентові формат відповіді, а `parse.js` цей формат читає. Двоє
   пишуться окремо й розходяться мовчки: `<ФІГУРИ>подія {n}` просять у трьох типів, а
   парсер знає саме «розділ» — і фігури в історії, виведенні й проєкті не виникали ЖОДНОЇ,
   без сліду в лозі. Агент відповів рівно як просили, розбір дав нуль рядків, крок пішов
   далі. Заміряно: 3 типи з 7.

   Тут із шаблона в контракті будують зразок відповіді й проганяють крізь той самий
   парсер, яким читатиме конвеєр. Порожньо на виході — розбіжність, і вона видна ДО того,
   як за неї заплатять токенами.

   ⛔ ЦЕ НЕ ПЕРЕВІРКА ТЕКСТУ ПРАВИЛ. Тут не питають, чи правило добре; питають лише, чи
   доїде відповідь на нього назад.
   ========================================================================== */
"use strict";

const fs = require("fs");
const path = require("path");
const R = require("../runners/parse.js");

const RULES = path.join(__dirname, "..", "rules");

/** Тег → чим його читає алгоритм. Теги вільного тексту сюди не входять: там нема формату. */
const READER = {
  "РОЗДІЛИ": R.sections, "КРОКИ": R.sections, "ПОДІЇ": R.sections,
  "ГРУПИ": R.groups, "ФІГУРИ": R.figures, "НОВІ SVG": R.figures,
  "ВСТАВКИ": R.inserts, "НОВІ ТЕМИ": R.topics, "ОКРЕМА ТЕМА": R.topics,
  "ЧИ Є ІСТОРІЯ": R.inserts, "ЧИ Є МАТЕМАТИКА": R.inserts, "ЧИ Є ПРОЄКТ": R.inserts,
  "ЧИ Є КОМПОНЕНТ": R.inserts, "ЧИ Є API": R.inserts,
  /* «КЛАСИ», «ФАЙЛИ», «СТРУКТУРА», «ГЛИБИНА», «ВЕРДИКТ» алгоритм читає як текст — там
     формату нема, і питати тут нема про що. */
  "КОД": R.code, "ПЕРЕДУМОВИ": R.preknow,
  "ЩО ДОДАТИ": R.additions, "ЩО ЗЖАТИ": R.bySection, "ТЕЗИ": R.bySection,
  "ДЕ ДОПИСАТИ": R.bySection, "ОЦІНКИ": R.scores, "ЗАМІНИ": R.replacements, "НАЗВИ": R.names,
};

/**
 * Шаблон із контракту → правдоподібний рядок відповіді.
 *
 * Агент бачить `{n}`, `{ім'я}`, `{a|b|c}` і підставляє щось своє; ми підставляємо те саме,
 * тільки передбачувано. Хвіст «; порожньо, якщо…» — вказівка агентові, не частина рядка.
 */
function sample(tpl) {
  let s = tpl.replace(/\s*[;·]\s*(порожньо|пусто|нічого)[^]*$/i, "").trim();
  /* Підставляємо за тим, ЩО стоїть перед діркою, а не лише за словом усередині: у
     «важливість: {…}» саме́ слово нічого не каже, а місце каже все. */
  s = s.replace(/([^\s{}]*\s*)\{([^{}]*)\}/g, (_, before, inner) => {
    const alt = inner.split("|").map((x) => x.trim());
    const pick = (v) => before + v;
    if (alt.length > 1 && alt.every((x) => /^[a-zа-яіїєґ0-9 ]+$/i.test(x) && x.length < 12)) return pick(alt[0]);
    if (/важлив/i.test(before) || /важлив/i.test(inner)) return pick("висока");
    /* ⛔ БЕЗ ``: межа слова знає саме [A-Za-z0-9_], і після кирилиці її НЕМА — `/^номер/`
       не збігається з «номер» ніколи. Довший варіант просто стоїть першим. */
    if (/^номери|^група/i.test(inner)) return pick("1, 2");
    if (/^n$/i.test(inner) || /^номер|^розділ$/i.test(inner)) return pick("1");
    if (/0[–-]10/.test(inner)) return pick("8");
    if (/^тип$/i.test(inner)) return pick("hist");
    if (/слуг|ім'я|имя/i.test(inner)) return pick("probe-name");
    if (/мова/i.test(inner)) return pick("python");
    if (/адрес|root:/i.test(inner)) return pick("root:probe-book/probe-topic");
    if (/рівень|1-5|1–5/i.test(inner)) return pick("3");
    return pick("проба тексту");
  });
  /* «розділ {n або —}» лишає по собі «розділ 3 або —» — беремо перше значення. */
  return s.replace(/\s+(або|чи)\s+[—-]/g, "");
}

/**
 * Що не так із розбором — або `null`, якщо все гаразд.
 *
 * ⛔ «НЕПОРОЖНЬО» ЗАМАЛО, і це коштувало окремої вади: `крок 3 | python | обхід` давало
 * рядок, тільки МОВОЮ в ньому стояло «крок 3». Порожнечу видно, з'їхані колонки — ні,
 * тож тут дивляться на самі значення. Ознаки універсальні: розділювач, що лишився
 * всередині поля, і слово-одиниця, яке мало бути з'їдене префіксом.
 */
const SPILL = /^(розділ|крок|подія|подии|варіант|клас|пункт)\s*\d/i;

function verdict(got, tpl) {
  if (!got.length) return "розбір порожній";
  for (const o of got)
    for (const [k, v] of Object.entries(o)) {
      if (typeof v !== "string") continue;
      if (v.includes("|")) return `у полі «${k}» лишився розділювач: колонки з'їхали`;
      if (SPILL.test(v)) return `у поле «${k}» потрапило слово-одиниця: «${v}»`;
    }
  /* Номер просили — номер має бути прочитаний, а не проковтнутий сусіднім полем. */
  const wantsNum = /\{\s*(n|номер|розділ)\s*\}/i.test(tpl.split("|")[0] || "");
  if (wantsNum && got.every((o) => "section" in o && o.section == null))
    return "номер просили, а `section` порожній";
  return null;
}

/* Рядок контракту може стояти в будь-якому файлі правил і будь-де в ньому. */
/* Ім'я тега — кирилиця, але може містити латинське слово («ЧИ Є API»). */
const TAG = /<([А-ЯІЇЄҐA-Z][А-ЯІЇЄҐA-Z' ]*)>([^<>\n]+)<\/\1>/g;

const files = [];
(function walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true }))
    e.isDirectory() ? walk(path.join(d, e.name))
      : e.name.endsWith(".md") && files.push(path.join(d, e.name));
})(RULES);

const bad = [];
let checked = 0;

for (const f of files.sort()) {
  const text = fs.readFileSync(f, "utf8");
  let m;
  while ((m = TAG.exec(text))) {
    const tag = m[1].trim(), tpl = m[2].trim();
    const read = READER[tag];
    if (!read) continue;                       // вільний текст — формату нема
    if (!/[{|]/.test(tpl)) continue;           // не шаблон, а сам текст
    const line = sample(tpl);
    checked++;
    let got = [];
    try { got = read(line) || []; } catch (e) { got = []; }
    const why = verdict(got, tpl);
    if (why) bad.push({ file: path.relative(RULES, f).replace(/\\/g, "/"), tag, tpl, line, why, got });
  }
}

const w = (s, n) => String(s).padEnd(n);
if (bad.length) {
  console.log("⛔ КОНТРАКТ ПРОСИТЬ ТЕ, ЧОГО ПАРСЕР НЕ ЧИТАЄ\n");
  for (const b of bad) {
    console.log(`  ${w(b.file, 24)} <${b.tag}>`);
    console.log(`  ${w("", 24)} просять:  ${b.tpl}`);
    console.log(`  ${w("", 24)} вийшло б: ${b.line}`);
    console.log(`  ${w("", 24)} розбір:   ${b.got.length ? JSON.stringify(b.got[0]) : "порожньо"}`);
    console.log(`  ${w("", 24)} ⛔        ${b.why}\n`);
  }
}
console.log(`перевірено рядків контракту: ${checked} · розбіжностей: ${bad.length}`);
process.exit(bad.length ? 1 : 0);
