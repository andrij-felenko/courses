#!/usr/bin/env node
/* Перевірка 09 — ТЕРМІНИ: один термін на поняття, термін після механізму.
   Ужиток: node scripts/checks/09-terms.js <тека теми>

   Що беремо:
     (1) пари синонімів, ужиті обидві в одній темі (каталог/директорія…);
     (2) поняття, означене ДВІЧІ — два різні визначення того самого жирного терміна;
     (3) базова вводить термін, якого немає в детальній (версії розійшлися).

   Чого НЕ беремо: частоту жирного тексту. Вона ловила «так» і «Навіщо це» —
   тобто канонний підзаголовок — і давала спрацювання на кожній статті. */
"use strict";
const fs = require("fs");
const L = require("./_lib.js");

const DIR = L.resolveDir(process.argv[2]);
if (!DIR) { console.error("Вкажи теку теми (шлях від кореня репо або абсолютний)"); process.exit(L.USAGE); }
const T = L.readTopic(DIR);
L.head("09", "один термін на поняття", DIR);
if (!T.prose.length) L.pass("у темі немає прози");

/* корені, а не слова: українська флективна, тому шукаємо по кореню з межею зліва */
const PAIRS = [
  ["каталог", "директорі"], ["тека", "папк"], ["ядро", "кернел"], ["вставк", "інсерт"],
  ["налагодж", "дебаг"], ["потік", "тред"], ["пристрій", "девайс"], ["сховищ", "сторедж"],
  ["запит", "реквест"], ["відповід", "респонс"], ["оновленн", "апдейт"], ["вимкн", "дисейбл"],
  ["позначк", "флаг"], ["звертанн", "колбек"],
];
const all = T.files.map((f) => L.strip(f.text)).join("\n");
const count = (root) => (all.match(new RegExp(`(?<![\\p{L}])${root}[\\p{L}']*`, "giu")) || []).length;

const items = [];
PAIRS.forEach(([a, b]) => {
  const na = count(a), nb = count(b);
  if (na && nb) items.push({ file: "(уся тема)", text: `вжито обидва варіанти: «${a}…» ×${na} і «${b}…» ×${nb} — за §4 лишається ОДИН на поняття` });
});

/* поняття, означене двічі: **термін** із маркером визначення поруч */
const DEFN = /\*\*([^*\n]{3,42})\*\*\s*(?:—|–|-|це\b|:)/g;
const defs = new Map();
T.prose.forEach((f) => {
  for (const m of f.text.matchAll(DEFN)) {
    const term = m[1].trim().toLowerCase().replace(/[.,:;]$/, "");
    if (term.split(/\s+/).length > 5) continue;
    if (!defs.has(term)) defs.set(term, []);
    defs.get(term).push({ file: f.file, at: f.text.slice(m.index, m.index + 150).replace(/\s+/g, " ") });
  }
});
defs.forEach((places, term) => {
  if (places.length < 2) return;
  items.push({
    file: places.map((p) => p.file).join(" + "),
    text: `«${term}» означено ${places.length} рази: ${places.map((p) => "…" + p.at.slice(0, 90)).join("   ||   ")}`,
  });
});

/* базова вводить своє: жирні терміни базової, яких немає в детальній */
if (T.basic && T.detailed) {
  const dText = T.detailed.text.toLowerCase();
  const bTerms = [...new Set([...T.basic.text.matchAll(/\*\*([^*\n]{3,42})\*\*/g)].map((m) => m[1].trim().toLowerCase()))];
  const orphan = bTerms.filter((t) => !dText.includes(t));
  if (orphan.length)
    items.push({ file: T.basic.file, kind: "basic", text: `базова вводить терміни, яких немає в детальній: ${orphan.slice(0, 8).join(" · ")} — базова простіша мовою, але поняття ті самі` });
}

if (!items.length) L.pass("синонімів на одне поняття й подвійних означень не знайдено");

L.adjudicate(DIR, items,
  "по кожному пункту: це справді два імені одного поняття (тоді лишити одне по всій темі й звірити з корпусом: grep по книзі) " +
  "чи два різні поняття, які просто звучать схоже? " +
  "Окремо перечитай статтю підряд і, якщо побачиш термін, ужитий РАНІШЕ, ніж пояснений механізм, — це дефект §4: спершу що відбувається, потім як це звуть. " +
  "Доказ — цитати обох місць із номерами рядків.");
