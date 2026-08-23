/* collect-candidates.js — збирає кандидатів у НОВІ теми з усіх пропозицій scripts/migrate/toc/.
   Секції з заголовком, що містить «НОВ» (НОВІ ТЕМИ / НОВІ КРОКИ / …), беруться цілком.
   На виході scripts/migrate/candidates-<курс>.md: кожен кандидат + скільки з 5 агентів його назвали. */
const fs = require("fs"), path = require("path");
const NL = String.fromCharCode(10);
const dir = path.join(__dirname, "toc");
const courses = ["embedded", "progarch", "unix"];

function norm(s) {
  return s.toLowerCase()
    .replace(/[«»"'`\u2019\u02bc()]/g, " ")
    .replace(/[^a-zа-яіїєґ0-9 ]/gi, " ")
    .replace(/\s+/g, " ").trim();
}
/* із рядка-кандидата дістаємо саму назву теми: перше, що в лапках, або текст до « → » / « · » */
function titleOf(line) {
  const q = line.match(/[«"]([^»"]{3,90})[»"]/);
  if (q) return q[1].trim();
  let s = line.replace(/^[-*\d.\s]+/, "");
  s = s.split(" → ")[0].split(" · ")[0].split(" — ")[0];
  return s.trim().slice(0, 90);
}

for (const c of courses) {
  const seen = {};
  let files = 0;
  for (let i = 1; i <= 5; i++) {
    const f = path.join(dir, c + "-" + i + ".md");
    if (!fs.existsSync(f)) continue;
    files++;
    const lines = fs.readFileSync(f, "utf8").split(NL);
    /* секція «НОВІ …» триває, доки не почнеться заголовок ТОГО САМОГО або вищого рівня.
       Підзаголовки всередині неї (напр. «## Том I — 3») її НЕ закривають. */
    let inNew = false, openLvl = 0;
    for (const L of lines) {
      const h = L.match(/^(#{1,6})\s+(.*)$/);
      if (h) {
        const lvl = h[1].length, txt = h[2];
        if (/НОВ[АІЕ]/i.test(txt)) { inNew = true; openLvl = lvl; }
        else if (inNew && lvl <= openLvl) inNew = false;
        continue;
      }
      if (!inNew) continue;
      const isBullet = /^\s*[-*]\s+\S/.test(L);
      const isRow = /^\s*\|/.test(L) && L.indexOf("---") < 0;
      if (!isBullet && !isRow) continue;
      const t = titleOf(isRow ? L.split("|").filter(x => x.trim()).join(" · ") : L);
      if (t.length < 4) continue;
      const k = norm(t);
      if (!k) continue;
      if (!seen[k]) seen[k] = { title: t, n: 0, from: new Set(), sample: L.trim().slice(0, 200) };
      seen[k].n++; seen[k].from.add(i);
    }
  }
  const rows = Object.values(seen).map(x => ({ title: x.title, votes: x.from.size, sample: x.sample }))
    .sort((a, b) => b.votes - a.votes || a.title.localeCompare(b.title));
  const out = [];
  out.push("# Кандидати в нові теми — курс «" + c + "»", "");
  out.push("Зібрано з " + files + " незалежних пропозицій. Число в дужках — скільки агентів із " + files +
    " назвали цю тему самостійно. Це **кандидати, а не рішення**: бери те, що справді потрібне твоїй структурі,");
  out.push("відкидай зайве, додавай своє. Формулювання чужі — можеш переназвати.", "");
  const strong = rows.filter(r => r.votes >= 2), weak = rows.filter(r => r.votes === 1);
  out.push("## Назвали кілька агентів незалежно (" + strong.length + ")", "");
  strong.forEach(r => out.push("- (" + r.votes + "/" + files + ") " + r.sample));
  out.push("", "## Назвав один агент (" + weak.length + ")", "");
  weak.forEach(r => out.push("- " + r.sample));
  const dst = path.join(__dirname, "candidates-" + c + ".md");
  fs.writeFileSync(dst, out.join(NL) + NL, "utf8");
  console.log("candidates-" + c + ".md   кандидатів " + rows.length + "  (кількома названо " + strong.length + ", одним " + weak.length + ")");
}
