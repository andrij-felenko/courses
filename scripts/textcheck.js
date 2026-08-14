#!/usr/bin/env node
/* ============================================================================
   textcheck.js — локальний гейт ТЕКСТУ (доповнює wordcount/svgcheck/linkcheck).
   Ловить те, що ті три пропускають, а читач бачить одразу:

     (1) ГОМОГЛІФИ   — латинська літера всередині кириличного слова (`вибiр`, `ідea`).
                       Ламає пошук по сайту. ЄДИНИЙ клас, що виправляється --apply.
     (2) LaTeX       — сирий $…$, \(…\), \frac{}, \mathbb{} у прозі. Канон §5: лише Unicode.
     (3) МОВА        — русизми й склейки кирилиці з латиницею. Лише звіт: рішення контекстне.
     (4) ФІГУРИ      — осиротілі SVG, биті посилання, тека з img/ але без figs.py.
     (5) ОБСЯГ       — слова РАЗОМ ІЗ КОДОМ (навмисно інакше, ніж wordcount.js, який
                       рахує саму прозу). Лише список на перевірку.

   Запуск:  node scripts/textcheck.js <тека> [--apply] [--only 1,3] [--json] [--quiet]
            node scripts/textcheck.js book/algorithms
            node scripts/textcheck.js . --only 1 --apply

   Код виходу: 1, якщо є класи (1) або (2) — це тверді дефекти. Інакше 0.

   ЧОМУ САМЕ ТАК (уроки на граблях):
   • Словник шукає по МЕЖАХ СЛІВ. Підрядковий пошук «получ» дав 869 хибних спрацювань
     на «сполучення / паросполучення / словосполучення» — і сигнал потонув у шумі.
   • $…$ пропускає ВАЛЮТУ: «$795 проти ~$15» — це не формула. Без цього 12 із 12 хибні.
   • Гомогліфи не чіпають РЯДКИ-ПРИКЛАДИ ДАНИХ (`ААААААААBBBBCC` у статті про стиснення):
     автозаміна там нищить сам предмет прикладу.
   • Код, інлайн-код, URL і цілі markdown-лінків МАСКУЮТЬСЯ пробілами тієї ж довжини —
     так зміщення рядків лишаються чинними, а всередині коду ми нічого не судимо.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

/* ── аргументи ─────────────────────────────────────────────────────────────── */
const argv = process.argv.slice(2);
const ROOT = argv.find((a) => !a.startsWith("--")) || ".";
const APPLY = argv.includes("--apply");
const JSON_OUT = argv.includes("--json");
const QUIET = argv.includes("--quiet");
const onlyArg = argv.indexOf("--only");
const ONLY = onlyArg >= 0 && argv[onlyArg + 1]
  ? new Set(argv[onlyArg + 1].split(",").map((s) => s.trim()))
  : null;
/* Клас 6 (описки за частотою) — ЛИШЕ на явний запит: українська флективна, і відстань 2
   постійно влучає в сусідню словоформу («поводимося» → «поводиться»). Перевірено на
   документній частоті — не розрізняє: жива рідкісна форма теж сидить в одному файлі. */
const OPT_IN = new Set(["6"]);
const want = (n) => (ONLY ? ONLY.has(String(n)) : !OPT_IN.has(String(n)));

if (!fs.existsSync(ROOT)) { console.error(`нема теки: ${ROOT}`); process.exit(2); }

/* ── маскування: код, інлайн-код, URL, цілі лінків, шляхи до зображень ──────
   Замінюємо на пробіли ТІЄЇ Ж ДОВЖИНИ — рядки й колонки лишаються правильними. */
const blank = (m) => m.replace(/[^\n]/g, " ");
function mask(src) {
  return src
    .replace(/```[\s\S]*?```/g, blank)        // код-блоки
    .replace(/~~~[\s\S]*?~~~/g, blank)        // альтернативні код-блоки
    .replace(/`[^`\n]*`/g, blank)             // інлайн-код
    .replace(/<preknowlist>[\s\S]*?<\/preknowlist>/g, (m) =>
      m.replace(/\]\([^)\n]*\)/g, blank))     // у передумовах маскуємо лише цілі лінків
    .replace(/\]\([^)\n]*\)/g, blank)         // цілі markdown-лінків і зображень
    .replace(/https?:\/\/\S+/g, blank)        // голі URL
    .replace(/<[^>\n]{1,120}>/g, blank);      // html-теги й атрибути
}

/* ── (1) гомогліфи ─────────────────────────────────────────────────────────── */
const HOMO = { a:"а", c:"с", e:"е", i:"і", o:"о", p:"р", x:"х", y:"у",
               A:"А", B:"В", C:"С", E:"Е", H:"Н", I:"І", K:"К", M:"М", O:"О", P:"Р", T:"Т", X:"Х" };
const CYR = /[а-яіїєґА-ЯІЇЄҐ]/;
const TOKEN = /[A-Za-zА-Яа-яІЇЄҐіїєґ]{2,}/g;

/** Токен лагодимо, лише якщо КОЖНА латинська літера має кириличний відповідник.
    Інакше це вклеєне справжнє слово (closed, worked, pythonic) — його калічити не можна. */
function fixToken(tok) {
  if (!CYR.test(tok)) return null;                       // суто латинське — не наше
  const lat = tok.match(/[A-Za-z]/g);
  if (!lat) return null;                                 // суто кирилиця — усе гаразд
  if (!lat.every((ch) => HOMO[ch])) return null;         // є літера без відповідника
  const cyr = tok.match(/[а-яіїєґА-ЯІЇЄҐ]/g) || [];
  if (cyr.length < 2) return null;                       // одна кирилична — надто хитко
  if (/^[A-ZА-ЯІЇЄҐ]{6,}$/.test(tok)) return null;       // ВЕЛИКИМИ й довге — приклад даних
  return tok.replace(/[A-Za-z]/g, (ch) => HOMO[ch]);
}

/* ── (2) LaTeX ─────────────────────────────────────────────────────────────── */
const TEX_CMD = /\\(?:text|frac|sqrt|mathbb|mathcal|mathrm|bmod|le\b|ge\b|in\b|cdot|log_|sum|prod|infty|alpha|beta|lambda|theta)|\\\(|\\\)|\\\[|\\\]|\$\$/g;
const D = "$";
/** $…$ рахуємо формулою, лише якщо вміст СХОЖИЙ на математику:
    є зворотний слеш, ^/_ з фігурними дужками, або це коротке позначення (N, O(1), V=100).
    Валюту ($795, $15 млрд, 0.07 $/год) відкидаємо: там одразу за $ іде цифра/пробіл+цифра. */
function texInline(line) {
  const out = [];
  const re = new RegExp("\\" + D + "([^" + "\\" + D + "\n]{1,80})\\" + D, "g");
  let m;
  while ((m = re.exec(line))) {
    const body = m[1];
    if (/^\s*[\d.,]/.test(body)) continue;                 // $795 … — валюта
    if (/^\s*\/?\s*(год|міс|рік|шт|users?|мд)\b/i.test(body)) continue;  // $/год
    const mathy = /\\/.test(body) || /[\^_]\{/.test(body) ||
                  /^[A-Za-zΑ-Ωα-ω](\s*[=<>]\s*\S+)?$/.test(body.trim()) ||
                  /^O\(|^Θ\(|^Ω\(/.test(body.trim());
    if (mathy) out.push(m[0]);
  }
  return out;
}

/* ── (3) мова ──────────────────────────────────────────────────────────────── */
/* Кожен запис — корінь; шукаємо ЛИШЕ з початку слова. */
const RUS = [
  ["получ", "отримати / здобути"], ["розпреділ", "розподіл"], ["преємник", "наступник"],
  ["учбов", "навчальн"], ["наглядн", "наочн"], ["співпада", "збіга"],
  ["міроприємств", "захід"], ["обраховув", "обчислюв"], ["вияснит", "з'ясувати"],
  ["слідуюч", "наступн"], ["співставл", "зіставл"], ["на протязі", "протягом"],
  ["прийшлось", "довелося"], ["по крайній мірі", "принаймні"], ["в кінці кінців", "зрештою"],
  ["в залежності", "залежно"], ["кольц", "кільц"], ["дешежч", "дешевш"],
  ["багатаяд", "багатояд"], ["реаллок", "реалок"], ["у очікуванні", "в очікуванні"],
  ["приймаючий", "той, що приймає"], ["керуючий", "керівний / той, що керує"],
  ["виконуючий", "той, що виконує"], ["наступаюч", "той, що настає"],
];
const RUS_RE = new RegExp(
  "(^|[^А-Яа-яІЇЄҐіїєґ'’-])(" + RUS.map(([w]) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")",
  "gi");
const RUS_HINT = Object.fromEntries(RUS);

/* Склейки: кирилиця впритул до латиниці в одному токені.
   Свідомі гібриди технічного тексту не рахуємо. */
const GLUE_OK = /^(не|анти|anti|пост|псевдо|квазі|мікро|макро|де|ре)/i;
const GLUE = /[А-Яа-яІЇЄҐіїєґ]{2,}[A-Za-z]{3,}|[A-Za-z]{3,}[А-Яа-яІЇЄҐіїєґ]{2,}/g;

/* ── обхід ─────────────────────────────────────────────────────────────────── */
const SKIP_DIR = /^(\.git|node_modules|\.claude|img|scratch)$/;
function walk(dir, out) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.isDirectory()) { if (!SKIP_DIR.test(e.name)) walk(path.join(dir, e.name), out); }
    else if (e.name.endsWith(".md")) out.push(path.join(dir, e.name));
  }
  return out;
}

const files = walk(ROOT, []);
const R = { homo: [], tex: [], lang: [], svg: [], size: [], typo: [], svgText: [] };
let fixedFiles = 0, fixedTokens = 0;

/* ── (6) ОПИСКИ: слово трапилось у корпусі раз-два, а поряд є частий сусід ────
   Описка майже завжди hapax legomenon і має правильну форму на відстані 1–2 правок:
   «лічильниця» → «лічильник» (4715 ×), «дешежчою» → «дешевою» (171 ×).
   Русизми так НЕ ловляться (правильна форма далі за дві правки) — їх бере словник.
   Частоти будуємо по ВСЬОМУ корпусу, навіть коли перевіряємо одну теку:
   інакше рідкісний правильний термін теки виглядав би опискою. */
const CORPUS = (() => {                       // корінь репо — там, де лежить AUTHORING.md
  let d = path.resolve(ROOT);
  for (let i = 0; i < 6; i++) {
    if (fs.existsSync(path.join(d, "AUTHORING.md"))) return d;
    const up = path.dirname(d); if (up === d) break; d = up;
  }
  return path.resolve(ROOT);
})();
/* ── частотний словник корпусу: будуємо РАЗ, далі беремо з кешу ────────────────
   Словник потрібен лише для пошуку описок: рідкісне слово проти «надійного».
   Раніше він будувався на кожному запуску — обхід усього корпусу (8686 файлів,
   227 МБ) коштував ~8 секунд чистого CPU. Перевірка 02 кличе textcheck пʼять разів,
   отже одна тема коштувала ~1 ГБ читання і ~40 секунд ядра; кілька агентів
   паралельно — і машина стоїть, нічого не виробляючи.

   Кеш дійсний, доки збігається підпис корпусу: кількість .md, сумарний розмір і
   найсвіжіший mtime. Будь-яка написана, дописана чи прибрана стаття підпис міняє,
   і словник перебудовується сам. У кеш кладемо лише слова, що трапились ТРИ рази
   й більше: усе, чого там немає, і так рідкісне (RARE_MAX = 2), тож семантика
   лишається та сама, а файл виходить у рази менший.                              */
const FREQ_CACHE = path.join(CORPUS, "scripts", "_finish", "_freq-cache.json");

function corpusSignature(dir) {
  let n = 0, bytes = 0, newest = 0;
  (function walkSig(d) {
    let ents; try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch (e) { return; }
    for (const e of ents) {
      const q = path.join(d, e.name);
      if (e.isDirectory()) { if (!SKIP_DIR.test(e.name)) walkSig(q); continue; }
      if (!e.name.endsWith(".md")) continue;
      let st; try { st = fs.statSync(q); } catch (e) { continue; }
      n++; bytes += st.size; if (st.mtimeMs > newest) newest = st.mtimeMs;
    }
  })(dir);
  return n + ":" + bytes + ":" + Math.round(newest);
}

function buildFreqMap(dir) {
  const m = new Map();
  (function walkFreq(d) {
    let ents; try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch (e) { return; }
    for (const e of ents) {
      const q = path.join(d, e.name);
      if (e.isDirectory()) { if (!SKIP_DIR.test(e.name)) walkFreq(q); continue; }
      if (!e.name.endsWith(".md")) continue;
      const txt = mask(fs.readFileSync(q, "utf8"));
      for (const w of txt.match(/[а-яіїєґА-ЯІЇЄҐ'’]{4,}/g) || []) {
        const k = w.toLowerCase(); m.set(k, (m.get(k) || 0) + 1);
      }
    }
  })(dir);
  return m;
}

const FREQ = (() => {
  const sig = corpusSignature(CORPUS);
  try {
    const c = JSON.parse(fs.readFileSync(FREQ_CACHE, "utf8"));
    if (c.sig === sig) return new Map(Object.entries(c.freq));
  } catch (e) { /* немає кешу або він побитий — будуємо */ }
  const m = buildFreqMap(CORPUS);
  const keep = {};
  for (const [w, n] of m) if (n >= 3) keep[w] = n;
  try {
    fs.mkdirSync(path.dirname(FREQ_CACHE), { recursive: true });
    fs.writeFileSync(FREQ_CACHE, JSON.stringify({ sig, freq: keep }), "utf8");
  } catch (e) { /* кеш не записався — не біда, просто буде повільніше */ }
  return m;
})();
const VOCAB = [...FREQ.entries()].filter(([, n]) => n >= 8).map(([w]) => w);   // «надійні» слова
const RARE_MAX = 2;        // трапилось стільки разів або менше — кандидат в описки
function editDist(a, b, cap) {
  const m = a.length, n = b.length;
  if (Math.abs(m - n) > cap) return cap + 1;
  let prev = Array.from({ length: n + 1 }, (_, j) => j), cur = new Array(n + 1);
  for (let i = 1; i <= m; i++) {
    cur[0] = i; let best = i;
    for (let j = 1; j <= n; j++) {
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      if (cur[j] < best) best = cur[j];
    }
    if (best > cap) return cap + 1;                       // рання відсічка — інакше повільно
    [prev, cur] = [cur, prev];
  }
  return prev[n];
}
const typoCache = new Map();
function typoOf(w) {
  if (typoCache.has(w)) return typoCache.get(w);
  let res = null;
  if ((FREQ.get(w) || 0) <= RARE_MAX && w.length >= 5) {
    let best = null, bf = 0;
    for (const v of VOCAB) {
      if (Math.abs(v.length - w.length) > 2) continue;
      if (v[0] !== w[0]) continue;                        // описка рідко в першій літері — і це різко пришвидшує
      const f = FREQ.get(v);
      if (f <= bf) continue;
      if (editDist(w, v, 2) <= 2) { best = v; bf = f; }
    }
    if (best && bf >= 8) res = { to: best, freq: bf };
  }
  typoCache.set(w, res);
  return res;
}

/* ── текст усередині SVG ──────────────────────────────────────────────────────
   Підписи у фігурах не гейтить НІЩО: wordcount читає лише .md, svgcheck судить
   геометрію. Саме так у корпус зайшла «одна лічильниця незавершених записів». */
function svgTexts(file) {
  const s = fs.readFileSync(file, "utf8");
  const out = [];
  const re = /<(?:text|tspan)\b[^>]*>([^<]*)<\/(?:text|tspan)>/g;
  let m, idx = 0;
  while ((m = re.exec(s))) {
    const t = m[1].replace(/&[a-z]+;/g, " ").trim();
    if (t) out.push({ text: t, n: ++idx });
  }
  return out;
}
function collectSvg(dir, out) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { if (!/^(\.git|node_modules|\.claude|scratch)$/.test(e.name)) collectSvg(p, out); }
    else if (e.name.endsWith(".svg")) out.push(p);
  }
  return out;
}

/* ── (5) пороги обсягу (слова РАЗОМ із кодом) ──────────────────────────────── */
const TOL = 0.10;
function sizeRule(base, dir) {
  if (base === dir) return { kind: "basic", lo: 500 };
  if (base === dir + "-d") return { kind: "detailed", lo: 1000 };
  if (/^(hist|comp|math|proj|api)-/.test(base)) return { kind: "insert", lo: 400 };
  return null;
}

for (const f of files) {
  const src = fs.readFileSync(f, "utf8");
  const masked = mask(src);
  const lines = masked.split(/\r?\n/);
  const rel = path.relative(ROOT, f) || path.basename(f);
  const dir = path.basename(path.dirname(f));
  const base = path.basename(f, ".md");

  /* (1) гомогліфи */
  if (want(1)) {
    let out = src, dirty = false;
    lines.forEach((ln, i) => {
      let m;
      const re = new RegExp(TOKEN.source, "g");
      while ((m = re.exec(ln))) {
        const fix = fixToken(m[0]);
        if (!fix) continue;
        R.homo.push({ file: rel, line: i + 1, from: m[0], to: fix });
        if (APPLY) {
          const rx = new RegExp("(?<![A-Za-zА-Яа-яІЇЄҐіїєґ])" + m[0].replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "(?![A-Za-zА-Яа-яІЇЄҐіїєґ])", "g");
          const nw = out.replace(rx, fix);
          if (nw !== out) { out = nw; dirty = true; fixedTokens++; }
        }
      }
    });
    if (APPLY && dirty) { fs.writeFileSync(f, out); fixedFiles++; }
  }

  /* (2) LaTeX */
  if (want(2)) {
    lines.forEach((ln, i) => {
      const cmds = ln.match(TEX_CMD) || [];
      const inl = texInline(ln);
      if (cmds.length || inl.length)
        R.tex.push({ file: rel, line: i + 1, hits: [...new Set([...cmds, ...inl])].slice(0, 4) });
    });
  }

  /* (3) мова */
  if (want(3)) {
    lines.forEach((ln, i) => {
      let m;
      RUS_RE.lastIndex = 0;
      while ((m = RUS_RE.exec(ln))) {
        const w = m[2].toLowerCase();
        R.lang.push({ file: rel, line: i + 1, kind: "русизм", word: m[2],
                      hint: RUS_HINT[w] || RUS_HINT[Object.keys(RUS_HINT).find((k) => w.startsWith(k))] || "",
                      ctx: ln.slice(Math.max(0, m.index - 30), m.index + 45).trim() });
      }
      const g = ln.match(GLUE) || [];
      for (const tok of new Set(g)) {
        if (GLUE_OK.test(tok)) continue;
        R.lang.push({ file: rel, line: i + 1, kind: "склейка", word: tok, hint: "", ctx: "" });
      }
    });
  }

  /* (6) описки */
  if (want(6)) {
    const seen = new Set();
    lines.forEach((ln, i) => {
      for (const w of ln.match(/[а-яіїєґА-ЯІЇЄҐ'’]{5,}/g) || []) {
        const k = w.toLowerCase();
        if (seen.has(k)) continue;
        const t = typoOf(k);
        if (t) { seen.add(k); R.typo.push({ file: rel, line: i + 1, word: w, to: t.to, freq: t.freq }); }
      }
    });
  }

  /* (5) обсяг — усі слова, включно з кодом */
  if (want(5)) {
    const rule = sizeRule(base, dir);
    if (rule) {
      const w = (src.match(/[\p{L}\p{N}’'\-]+/gu) || []).length;
      if (w < rule.lo) R.size.push({ file: rel, words: w, lo: rule.lo, kind: rule.kind, soft: w >= rule.lo * (1 - TOL) });
    }
  }
}

/* ── (7) ТЕКСТ УСЕРЕДИНІ SVG — ті самі три класи, застосовані до підписів ──── */
if (want(7)) {
  for (const sf of collectSvg(ROOT, [])) {
    const rel = path.relative(ROOT, sf) || path.basename(sf);
    let out = null, dirty = false;
    for (const { text, n } of svgTexts(sf)) {
      for (const tok of text.match(TOKEN) || []) {
        const fix = fixToken(tok);
        if (fix) {
          R.svgText.push({ file: rel, n, kind: "гомогліф", word: tok, to: fix });
          if (APPLY) { out = (out === null ? fs.readFileSync(sf, "utf8") : out); const nw = out.split(tok).join(fix); if (nw !== out) { out = nw; dirty = true; } }
        }
      }
      RUS_RE.lastIndex = 0; let m;
      while ((m = RUS_RE.exec(text)))
        R.svgText.push({ file: rel, n, kind: "русизм", word: m[2], to: RUS_HINT[m[2].toLowerCase()] || "", ctx: text });
      /* Описки у фігурах НЕ шукаємо частотним детектором: він не розрізняє живу рідкісну
         словоформу («наповнилась») від справжньої описки — українська флективна, і відстань
         2 постійно влучає в сусідню форму. Лишаються гомогліфи й словник русизмів. */
    }
    if (APPLY && dirty) { fs.writeFileSync(sf, out); fixedFiles++; }
  }
}

/* ── (4) фігури — по теках, а не по файлах ─────────────────────────────────── */
if (want(4)) {
  const dirs = new Set(files.map((f) => path.dirname(f)));
  for (const d of dirs) {
    const imgDir = path.join(d, "img");
    if (!fs.existsSync(imgDir)) continue;                       // нема фігур — нема питань
    const svgs = fs.readdirSync(imgDir).filter((x) => x.endsWith(".svg"));
    if (!svgs.length) continue;
    const md = fs.readdirSync(d).filter((x) => x.endsWith(".md"))
      .map((x) => fs.readFileSync(path.join(d, x), "utf8")).join("\n");
    const rel = path.relative(ROOT, d) || ".";
    const orphan = svgs.filter((s) => !md.includes(s));
    const linked = [...new Set((md.match(/img\/[A-Za-z0-9._-]+\.svg/g) || []).map((s) => s.slice(4)))];
    const broken = linked.filter((s) => !svgs.includes(s));
    const noFigs = !fs.existsSync(path.join(d, "figs.py"));
    if (orphan.length || broken.length || noFigs)
      R.svg.push({ dir: rel, orphan, broken, noFigs });
  }
}

/* ── звіт ──────────────────────────────────────────────────────────────────── */
if (JSON_OUT) { console.log(JSON.stringify(R, null, 2)); process.exit(R.homo.length || R.tex.length ? 1 : 0); }

const N = (a) => String(a).padStart(4);
console.log(`\n== textcheck: ${ROOT} ==  файлів .md: ${files.length}`);

if (want(1)) {
  console.log(`\n--- (1) ГОМОГЛІФИ: ${R.homo.length}${APPLY ? `  → виправлено ${fixedTokens} у ${fixedFiles} файлах` : ""} ---`);
  const by = {};
  R.homo.forEach((h) => (by[h.from + " → " + h.to] = (by[h.from + " → " + h.to] || 0) + 1));
  Object.entries(by).sort((a, b) => b[1] - a[1]).slice(0, QUIET ? 8 : 40)
    .forEach(([k, v]) => console.log(`  ${N(v)} × ${k}`));
  if (!APPLY && R.homo.length) console.log(`       (виправити: --only 1 --apply)`);
}

if (want(2)) {
  console.log(`\n--- (2) LaTeX у прозі: ${R.tex.length} рядків ---`);
  R.tex.slice(0, QUIET ? 5 : 30).forEach((t) => console.log(`  ${t.file}:${t.line}  ${t.hits.join("  ")}`));
  if (R.tex.length > 30 && !QUIET) console.log(`  … ще ${R.tex.length - 30}`);
}

if (want(3)) {
  const rus = R.lang.filter((l) => l.kind === "русизм");
  const glue = R.lang.filter((l) => l.kind === "склейка");
  console.log(`\n--- (3) МОВА: русизмів ${rus.length} · склейок ${glue.length} ---`);
  rus.slice(0, QUIET ? 5 : 25).forEach((l) =>
    console.log(`  ${l.file}:${l.line}  «${l.word}»${l.hint ? " → " + l.hint : ""}\n       …${l.ctx}…`));
  glue.slice(0, QUIET ? 5 : 25).forEach((l) => console.log(`  ${l.file}:${l.line}  склейка «${l.word}»`));
}

if (want(4)) {
  const orph = R.svg.reduce((s, x) => s + x.orphan.length, 0);
  const brok = R.svg.reduce((s, x) => s + x.broken.length, 0);
  const nofg = R.svg.filter((x) => x.noFigs).length;
  console.log(`\n--- (4) ФІГУРИ: осиротілих ${orph} · битих ${brok} · з img/ але без figs.py ${nofg} ---`);
  R.svg.filter((x) => x.orphan.length || x.broken.length).slice(0, QUIET ? 5 : 25).forEach((x) =>
    console.log(`  ${x.dir}${x.orphan.length ? "  осиротілі: " + x.orphan.join(", ") : ""}${x.broken.length ? "  ✖ БИТІ: " + x.broken.join(", ") : ""}`));
}

if (want(5)) {
  console.log(`\n--- (5) ОБСЯГ (слова РАЗОМ із кодом; лише список) : ${R.size.length} ---`);
  R.size.sort((a, b) => a.words - b.words).slice(0, QUIET ? 8 : 40).forEach((s) =>
    console.log(`  ${s.soft ? "~" : "✖"} ${N(s.words)}w / поріг ${s.lo} (${s.kind})  ${s.file}`));
}

if (want(6)) {
  console.log(`\n--- (6) ОПИСКИ (рідке слово + частий сусід): ${R.typo.length} ---`);
  R.typo.slice(0, QUIET ? 8 : 30).forEach((t) =>
    console.log(`  ${t.file}:${t.line}  «${t.word}» → «${t.to}» (${t.freq} × у корпусі)`));
}

if (want(7)) {
  const byKind = {};
  R.svgText.forEach((s) => (byKind[s.kind] = (byKind[s.kind] || 0) + 1));
  console.log(`\n--- (7) ТЕКСТ У ФІГУРАХ: ${R.svgText.length} ---  ${Object.entries(byKind).map(([k, v]) => k + " " + v).join(" · ") || "чисто"}`);
  R.svgText.slice(0, QUIET ? 6 : 25).forEach((s) =>
    console.log(`  ${s.file}  [${s.kind}] «${s.word}»${s.to ? " → «" + s.to + "»" : ""}${s.ctx ? "\n       …" + s.ctx.slice(0, 70) + "…" : ""}`));
}

const hard = R.homo.length + R.tex.length;
console.log(`\n== Підсумок ==  гомогліфи ${R.homo.length} · LaTeX ${R.tex.length} · русизми ${R.lang.filter((l) => l.kind === "русизм").length} · склейки ${R.lang.filter((l) => l.kind === "склейка").length} · фігури ${R.svg.length} тек · обсяг ${R.size.length}`);
console.log(hard && !APPLY ? "   тверді дефекти (1)(2) є — код виходу 1\n" : "   тверді дефекти (1)(2): 0\n");
process.exit(hard && !APPLY ? 1 : 0);
