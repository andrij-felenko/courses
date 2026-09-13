#!/usr/bin/env node
/* ============================================================================
   local.js — ЛОКАЛЬНІ КРОКИ КОНВЕЄРА. Нуль токенів, нуль здогадів.

   Сюди зібрано все, що агентові робити не треба: підготовка контексту, розмір,
   умови здачі, збирання файла, операції в маніфест. Кожен із цих кроків або дає
   число, або дає текст, який runner підставляє в блок, — і жоден нічого не судить
   про зміст.

   ⛔ ПЕРЕВІРКА ДУБЛЯ ЖИВЕ ТУТ, А НЕ В АГЕНТА. «Стаття існує» — це факт: слуг є в
   маніфесті, файл є на диску. Агент статей не бачить і може судити лише за
   заголовками, тобто дати «схоже», а не «є».
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const cp = require("child_process");
const MF = require("../lib/manifest.js");
const TXT = require("../lib/text.js");
const DUP = require("../lib/dupes.js");
const FRM = require("../checkers/formulas.js");
const DEC = require("../local/decamp.js");

/* ── людський шлях ─────────────────────────────────────────────────────────── */

/**
 * ⚠️ ПОСИЛАННЯ НА СТАТТЮ ЗАВЖДИ НЕСЕ ПОВНИЙ ШЛЯХ МОВОЮ. Сирий шлях на диску нічого
 * не каже тому, хто читає; «книга / група / розділ / тема» каже все одразу.
 */
function humanPath(rel) {
  const seg = rel.split("/");                       // root/<вид>/<книга>/<тема>/<файл>
  const b = MF.loadBook(MF.bookDirOf(seg[2]));
  if (!b) return rel;
  const t = MF.allTopics(b).find((x) => x.slug === seg[3]);
  const title = b.manifest.title || seg[2];
  if (!t) return `${title} / ${seg[3]}`;
  const g = b.groups.get(t.group);
  const gt = (g && g.data.title) || t.group;
  const ct = ((g && (g.data.chapters || []).find((c) => c.slug === t.chapter) || {}).title) || t.chapter;
  return `${title} / ${gt} / ${ct} / ${t.title}`;
}

/**
 * Одиниця з маніфесту в тому вигляді, у якому її бачать запити.
 *
 * ⚠️ ФАЙЛ ВСТАВКИ ЗВЕТЬСЯ ЗА ЇЇ ПРЕДМЕТОМ, А НЕ ЗА СЛУГОМ ТЕМИ: `<тип>-<назва>.md`.
 * Тому ім'я приходить ззовні; виведене з теми, воно дало б `proj-<тема>.md` — одне ім'я
 * на всі вставки того самого типу, тобто другий `proj` затирав би перший. Так само
 * адреса: `книга/тема:proj-circuit-breaker`, а не `книга/тема:proj`.
 */
function unitOf(book, slug, type = "article", version = "ДЕТАЛЬНА", file = "") {
  const b = MF.loadBook(MF.bookDirOf(book));
  if (!b) throw new Error(`книги «${book}» немає (manifest.json не знайдено)`);
  const t = MF.allTopics(b).find((x) => x.own && x.slug === slug);
  if (!t) throw new Error(`теми «${slug}» у книзі «${book}» немає`);
  const g = b.groups.get(t.group);
  const insert = MF.INSERT_TYPES.includes(type);
  const name = file
    ? String(file).replace(/\.md$/, "")
    : insert ? `${type}-${slug}` : type === "basic" ? slug : `${slug}-d`;
  return {
    id: `${book}/${slug}:${insert ? name : type === "article" ? "detailed" : type}`,
    book, slug, type, version, insert,
    /* Вид книги їде з одиницею: курс і книга пишуться по-різному (крок спирається на
       пройдене, стаття — атом), і письменник мусить знати, що саме перед ним. */
    kind: (MF.books().get(book) || {}).kind || b.manifest.kind || "",
    file: `${name}.md`,
    title: t.title,
    bookTitle: b.manifest.title || book,
    groupTitle: (g && g.data.title) || t.group,
    chapterTitle: ((g && (g.data.chapters || []).find((c) => c.slug === t.chapter) || {}).title) || t.chapter,
    bookDir: MF.bookDirOf(book),
    /* Слуги групи й розділу потрібні, щоб покласти поруч нову тему, яку назве ця сама:
       матеріал вийшов із цієї теми, отже й місце його — біля неї. */
    group: t.group, chapter: t.chapter,
    dir: path.join(MF.bookDirOf(book), slug),
  };
}

/* ── етап 1 · підготовка ───────────────────────────────────────────────────── */

const walkMd = (d, out = []) => {
  let e = [];
  try { e = fs.readdirSync(d, { withFileTypes: true }); } catch { return out; }
  for (const x of e) {
    const p = path.join(d, x.name);
    if (x.isDirectory()) walkMd(p, out);
    else if (x.name.endsWith(".md")) out.push(p);
  }
  return out;
};

/**
 * Згадки: абзац до, сама згадка, абзац після. Файли САМОЇ теми виключено — інакше
 * агент побачив би готовий текст і ціль стала б його переказом.
 *
 * ⚠️ Пошук іде за словом, і на омонімах він дає шум: на темі «Одержимість
 * примітивами» всі шість влучань виявилися про синхронізаційні та бітові примітиви.
 * Тому людський шлях стоїть ПЕРШИМ рядком — з нього доречність видно одразу.
 */
function mentions(u, re, { limit = Infinity, roots = ["root"] } = {}) {
  /* Весь список, повними абзацами: обрізане посеред речення нічого не пояснює, а
     пропущена згадка — це пропущений контекст, якого агент потім не матиме. */
  const out = [];
  const flat = (s) => String(s || "").replace(/\s+/g, " ").trim();
  for (const r of roots) {
    for (const f of walkMd(path.join(MF.ROOT, r))) {
      if (f.replace(/\\/g, "/").includes(`/${u.slug}/`)) continue;
      let txt = ""; try { txt = fs.readFileSync(f, "utf8"); } catch { continue; }
      if (!re.test(txt)) continue;
      const rel = path.relative(MF.ROOT, f).split(path.sep).join("/");
      const paras = txt.split(/\n\s*\n/);
      for (let i = 0; i < paras.length && out.length < limit; i++) {
        if (!re.test(paras[i])) continue;
        out.push(`— ${humanPath(rel)}\n  ${rel}\n[абзац до] ${flat(paras[i - 1])}\n` +
          `[згадка] ${flat(paras[i])}\n[абзац після] ${flat(paras[i + 1])}`);
      }
      if (out.length >= limit) break;
    }
  }
  return out.join("\n\n");
}

/**
 * Сусіди по розділу — назвою І АДРЕСОЮ.
 *
 * ⚠️ АДРЕСА ОБОВ'ЯЗКОВА. Доти сюди йшли самі назви, а правила пояснювали письменникові
 * ФОРМУ адреси (`root:<книга>/<тема>`) і не давали жодної справжньої. Наслідок
 * передбачуваний: він складав правдоподібні адреси сам. Заміряно на 36 темах — 61 різна
 * ціль не існує, ~95 входжень, і серед них цілі книги, яких у схемі 7 немає взагалі:
 * `math/`, `physics/`, `os/`, `algorithms/`. Форму знав, слугів не мав.
 */
function neighbours(u) {
  const b = MF.loadBook(MF.bookDirOf(u.book));
  const me = MF.allTopics(b).find((x) => x.slug === u.slug);
  return MF.allTopics(b)
    .filter((t) => t.own && t.chapter === me.chapter && t.slug !== u.slug)
    .map((t) => {
      const d = (t.node.detailed && t.node.detailed.status) || "empty";
      const st = d === "empty" || d === "pending" ? "ще не написана" : "НАПИСАНА";
      return `${t.title} [${st}] — root:${u.book}/${t.slug}`;
    }).join("\n");
}

/**
 * Куди цій одиниці МОЖНА лінкувати: справжні адреси, і більше жодних. Сусіди по розділу
 * плюс теми, у яких згадка вже знайшлася на диску. Порожньо не буває лише тоді, коли
 * тема сама-одна в розділі й ніде не згадана.
 */
function linkable(u) {
  const seen = new Set();
  const out = [];
  const add = (book, slug, title) => {
    const a = `root:${book}/${slug}`;
    if (slug && !seen.has(a)) { seen.add(a); out.push(`${title || slug} — ${a}`); }
  };
  const b = MF.loadBook(MF.bookDirOf(u.book));
  const me = b && MF.allTopics(b).find((x) => x.slug === u.slug);
  if (me) for (const t of MF.allTopics(b))
    if (t.own && t.chapter === me.chapter && t.slug !== u.slug) add(u.book, t.slug, t.title);
  return out.join("\n");
}

/** Усі книги репо назвами. */
const books = () => [...MF.books().entries()]
  .map(([slug, b]) => { const x = MF.loadBook(b.bookDir); return x ? (x.manifest.title || slug) : null; })
  .filter(Boolean).join("\n");

/** Книги з групами й розділами — слугами й назвами — для зведення нових тем. */
function shelf({ skipKinds = [], keep = [] } = {}) {
  const rows = [];
  for (const [slug, b] of MF.books()) {
    const x = MF.loadBook(b.bookDir);
    if (!x || (skipKinds.includes(b.kind || x.manifest.kind) && !keep.includes(slug))) continue;
    rows.push(`${slug} — ${x.manifest.title || slug} [${b.kind || x.manifest.kind || ""}]`);
    for (const [g, gv] of x.groups) {
      rows.push(`  ${g} — ${gv.data.title || g}`);
      for (const c of gv.data.chapters || []) rows.push(`    ${c.slug} — ${c.title || c.slug}`);
    }
  }
  return rows.join("\n");
}

/** Теми одного розділу книги (без розділу — усієї групи): слуг і назва. */
function chapterTopics(book, group, chapter) {
  const b = MF.loadBook(MF.bookDirOf(book));
  if (!b) return [];
  return MF.allTopics(b)
    .filter((t) => t.own && t.group === group && (!chapter || t.chapter === chapter))
    .map((t) => ({ slug: t.slug, title: t.title }));
}

/**
 * Огорожі коду: одиничний «`» рядком — це ``` (158 таких у 11 файлах: формули, які рендер
 * бачить як зламаний інлайн-код); огорожа, не закрита до наступного H2 чи кінця файла, —
 * закривається (3 файли з непарними ```: 140 рядків прози всередині ```csharp). Діапазон
 * `:::code шлях від-до` за межами файла — обрізаємо до файла.
 */
function fixFences(file) {
  let s = "";
  try { s = fs.readFileSync(file, "utf8"); } catch { return { single: 0, closed: 0, ranges: 0 }; }
  let single = 0, closed = 0, ranges = 0;
  const lines = s.split("\n").map((l) => { if (/^`[ \t]*$/.test(l)) { single++; return "```"; } return l; });
  /* ⛔ Закриваємо лише коли огорожа справді незакрита — парність непарна. У парному файлі
     `## ` всередині огорожі законний (приклад markdown у блоці), і закривати там — ламати. */
  const out = [];
  let inFence = false;
  const odd = lines.filter((l) => /^```/.test(l)).length % 2 === 1;
  for (const l of lines) {
    if (/^```/.test(l)) { inFence = !inFence; out.push(l); continue; }
    if (odd && inFence && /^## /.test(l)) { out.push("```"); closed++; inFence = false; }
    out.push(l);
  }
  if (odd && inFence) { out.push("```"); closed++; }
  const dir = path.dirname(file);
  let text = out.join("\n").replace(/^(:::code[^\S\n]+)(\S+)[^\S\n]+(\d+)-(\d+)[^\S\n]*$/gm, (m, pre, rel, a, b) => {
    let n = 0; try { n = fs.readFileSync(path.join(dir, rel), "utf8").split("\n").length; } catch { return m; }
    const from = Math.min(Number(a), n), to = Math.min(Number(b), n);
    if (from === Number(a) && to === Number(b)) return m;
    ranges++;
    return from >= to ? `${pre}${rel}` : `${pre}${rel} ${from}-${to}`;
  });
  if (text !== s) fs.writeFileSync(file, text, "utf8");
  return { single, closed, ranges };
}

/** Директиви `:::code`, які писар загорнув у ```-огорожу (сім разів в одному проєкті), — назовні. */
function unfenceDirectives(file) {
  let s = "";
  try { s = fs.readFileSync(file, "utf8"); } catch { return 0; }
  let n = 0;
  const out = s.replace(/^```[a-z]*\n((?::::code [^\n]+\n)+)```\n/gm, (m, body) => { n++; return body; });
  if (n) fs.writeFileSync(file, out, "utf8");
  return n;
}

/** Зняти лінк на адресу, лишивши слова: `[слова](адреса)` → `слова`. */
function unlink(text, addr) {
  const esc = String(addr).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return String(text || "").replace(new RegExp(`\\[([^\\]]+)\\]\\(${esc}(?:#[^)]*)?\\)`, "g"), "$1");
}

/** Усі теми книги: слуг і назва — для «чи є» етапу 8, бо дубль живе в будь-якому розділі. */
function bookTopics(book) {
  const b = MF.loadBook(MF.bookDirOf(book));
  if (!b) return [];
  return MF.allTopics(b).filter((t) => t.own).map((t) => ({ slug: t.slug, title: t.title }));
}

/** Початок наявної теми — перші речення її статті; не написана — її назва. */
function topicHead(book, slug, n = 8) {
  const dir = path.join(MF.bookDirOf(book), slug);
  for (const f of [`${slug}.md`, `${slug}-d.md`]) {
    let s = "";
    try { s = fs.readFileSync(path.join(dir, f), "utf8"); } catch { continue; }
    const body = s.replace(/^#[^\n]*\n/, "").replace(/<preknowlist>[\s\S]*?<\/preknowlist>/, "").trim();
    const sents = body.split(/(?<=[.!?])\s+/).slice(0, n).join(" ").trim();
    if (sents) return sents;
  }
  const b = MF.loadBook(MF.bookDirOf(book));
  const t = b && MF.allTopics(b).find((x) => x.own && x.slug === slug);
  return t ? `(ще не написана) ${t.title}` : "";
}

/** Шматок тексту довкола адреси лінка — будь-якої; немає — пустота. */
function aroundLink(text, addr, span = 500) {
  const s = String(text || "");
  const i = s.indexOf(String(addr));
  if (i < 0) return "";
  return s.slice(Math.max(0, i - span), i + span).replace(/\s+/g, " ").trim();
}
/** Шматок нашого тексту довкола лінка на ще не заведену тему. */
const linkContext = (text, slug, span = 500) => aroundLink(text, `root:new/${slug}`, span);

/** Початок будь-якого написаного файла — перші речення без H1 і блоку передумов. */
function fileHead(rel, n = 8) {
  let s = "";
  try { s = fs.readFileSync(path.join(MF.ROOT, rel), "utf8"); } catch { return ""; }
  const body = s.replace(/^#[^\n]*\n/, "").replace(/<preknowlist>[\s\S]*?<\/preknowlist>/, "").trim();
  return body.split(/(?<=[.!?])\s+/).slice(0, n).join(" ").replace(/\s+/g, " ").trim();
}

/** Лінки на майбутні теми → справжні адреси; чого в мапі нема — лишається як є. */
function resolveLinks(text, map) {
  return String(text || "").replace(/root:new\/([a-z0-9][a-z0-9-]*)/gi, (m, s) => map[s.toLowerCase()] || m);
}

/** Текст групи → розділи за H2: [{head, body}]. Без H2 — один розділ без заголовка. */
function splitSections(text) {
  const out = [];
  let cur = null;
  for (const line of String(text || "").split("\n")) {
    if (/^## /.test(line)) { cur = { head: line, body: [] }; out.push(cur); continue; }
    if (!cur) { cur = { head: "", body: [] }; out.push(cur); }
    cur.body.push(line);
  }
  return out.map((s) => ({ head: s.head, body: s.body.join("\n").trim() }));
}
const joinSections = (secs) => secs.map((s) => [s.head, s.body].filter(Boolean).join("\n\n")).join("\n\n");

/**
 * Що читач уже знає.
 *
 * КНИГА — сусіди розділу: стаття атом, читач може не знати нічого попереднього, і
 * сусіди потрібні лише для меж.
 *
 * КУРС — ПРОЙДЕНЕ: усе, що стоїть на доріжці ДО цього кроку, у порядку маніфесту —
 * кроки свого тому поіменно (і власні, і ref), попередні томи назвами. Крок курсу є
 * продовженням цих кроків: у тексті вони припускаються відомими, а не пояснюються
 * наново. Позначок «написана / ще ні» тут навмисно немає — читач пройшов крок
 * незалежно від того, чи вже написано текст.
 */
function preknow(u) {
  if (u.kind !== "course") return neighbours(u);
  const b = MF.loadBook(MF.bookDirOf(u.book));
  const all = MF.allTopics(b);
  const at = all.findIndex((x) => x.own && x.slug === u.slug);
  if (at < 0) return "";
  const me = all[at];
  const before = all.slice(0, at);
  const volumes = [...new Set(before.filter((t) => t.group !== me.group).map((t) => t.group))]
    .map((g) => (b.groups.get(g) && b.groups.get(g).data.title) || g);
  const steps = before.filter((t) => t.group === me.group).map((t) => `— ${t.title}`);
  return [
    "Це продовження доріжки: наведені кроки читач уже пройшов, і в тексті вони припускаються відомими.",
    volumes.length ? `Попередні томи: ${volumes.join(" · ")}` : "",
    steps.length ? `Кроки цього тому до цього кроку:\n${steps.join("\n")}` : "Це перший крок тому.",
  ].filter(Boolean).join("\n\n");
}

/** ⛔ Дубль — точно й локально. Слуг є в книзі ⟺ тема існує. */
function isDuplicate(book, slug) {
  const b = MF.loadBook(MF.bookDirOf(book));
  const t = b && MF.allTopics(b).find((x) => x.own && x.slug === slug);
  if (!t) return { exists: false, written: false, hints: DUP.hints(slug, book) || [] };
  const d = (t.node.detailed && t.node.detailed.status) || "empty";
  return {
    exists: true, written: !(d === "empty" || d === "pending"),
    hints: DUP.hints(slug, book) || [],
  };
}

/* ── етап 5 · розмір ───────────────────────────────────────────────────────── */

/** Норми з рішення автора. Базова — без рівня. Четверте число — стеля. */
const BANDS = {
  basic: [500, 500, 500, 1500],
  detail: [1200, 2400, 4000, 10000],
  hist: [600, 1000, 1600, 5000],
  math: [600, 1200, 2000, 6000],
  comp: [800, 1400, 2200, 7000],
  proj: [800, 1200, 1800, 8000],
  api: [700, 1400, 2500, 12000],
};

/**
 * Скільки бракує — у ВІДСОТКАХ, і це число йде дописувачеві, а не письменникові:
 * показане число стає ціллю.
 */
function size(text, type, level) {
  const key = type === "article" ? "detail" : type;
  const band = BANDS[key] || BANDS.detail;
  const words = TXT.proseWords(text);
  const need = type === "basic" ? band[0] : band[Math.max(1, Math.min(3, level || 2)) - 1];
  const short = words < need ? Math.round((1 - words / need) * 100) : 0;
  return { words, need, ceiling: band[3], shortBy: short, over: words > band[3] };
}

/* ── етап 9-10 · зібрання й маніфест ───────────────────────────────────────── */

/** Розділи → один файл. Заголовки пишуть самі письменники, ми лише склеюємо. */
const assemble = (parts) => {
  /* ⛔ ТРЕТЯ ЗАСТАВА ПРОТИ ПОВТОРУ, і вона остання перед диском. Дві попередні стоять у
     розборі відповіді й у групах; ця ловить те, що прослизнуло повз обидві. Повтор
     дешевше зняти тут, ніж потім пояснювати читачеві два однакові розділи. */
  const seen = new Set();
  return parts.map((p) => String(p || "").trim()).filter((p) => {
    if (!p || seen.has(p)) return false;
    seen.add(p);
    return true;
  }).join("\n\n") + "\n";
};

/**
 * ⛔ РОЗМІТКА ФОРМУЛ — ЛОКАЛЬНО, ОДРАЗУ ПІСЛЯ ЗАПИСУ. Нуль токенів, і саме тому це
 * робить конвеєр, а не людина потім.
 *
 * З'їдений бекслеш (`\text{` → таб плюс «ext{») лагодиться сам: підміна однозначна,
 * бо табуляція перед «ext{» у прозі не трапляється. Заміряно на корпусі — 231 такий
 * рядок у 24 темах, і всі вони доїхали до читача як літеральне «ext{Base}».
 *
 * Роздільники НЕ лагодимо ніколи: непарний `$` — це або загублений роздільник, або
 * долар за змістом, і вгадувати тут дорожче, ніж назвати місце. Вони йдуть у стан.
 */
function fixFormulas(file) {
  let s = "";
  try { s = fs.readFileSync(file, "utf8"); } catch { return { fixed: 0, delims: [] }; }
  const e = FRM.eaten(s);
  if (e.length) {
    for (const want of new Set(e.map((x) => x.want)))
      s = s.split(e.find((x) => x.want === want).was).join(want);
    fs.writeFileSync(file, s, "utf8");
  }
  return {
    fixed: e.length,
    delims: FRM.delimiters(s).map((d) => `рядок ${d.line}: ${d.why}`),
    /* Заборонене НЕ лагодимо: прибрати LaTeX означає переписати формулу словами й
       символами, а це робота письменника. Називаємо місце — і цього доти не робив ніхто. */
    banned: FRM.banned(s).map((b) => `рядок ${b.line}: ${b.why} — «${b.was}»`),
  };
}

/**
 * ⛔ КОД ВІД ДЕСЯТИ РЯДКІВ МУСИТЬ ЖИТИ У ФАЙЛІ, А НЕ В ОГОРОЖІ. Правило було, доїжджало
 * й не діяло: сказане нічим не мірялося. Тепер міряється — `text.js` рахує рівно те, що
 * мало виїхати: огорожа з міткою СПРАВЖНЬОЇ мови й довжиною від порогу. Схема, дерево
 * тек і вивід консолі кодом у цьому сенсі не є і в лік не входять.
 *
 * Нічого не переносить: винести код у файли означає ще й переписати посилання в прозі,
 * а це робота письменника. Називає число й місце.
 */
/**
 * ⛔ ДОВГИЙ КОД ВИНОСИМО, А НЕ ДОРІКАЄМО. Правило стояло, чекер потім лише рахував — а
 * рахувати мало: заміряно 49 файлів і 7031 рядок в огорожах по корпусу. Виносити — робота
 * механічна, отже наша: блок у файл поруч, на його місце директива.
 *
 * Це НЕ проєкт: одиниці коду не заводимо, архітектури не питаємо. Просто щоб текст не
 * ставав простирадлом.
 */
const decamp = (file) => DEC.decamp(file, { apply: true }).length;

function checkFences(file) {
  let s = "";
  try { s = fs.readFileSync(file, "utf8"); } catch { return { left: 0, code: 0, missing: [] }; }
  /* ⛔ ДЗЕРКАЛО `--links` ДЛЯ КОДУ. Для фігур перевірка «обіцяно в прозі, а файлу немає»
     була, для коду — ні, хоч дефект той самий і трапляється частіше: директива веде в
     порожнечу, і читач бачить голий рядок замість програми. Шлях у `:::code` — від теки
     теми, тож резолвимо саме звідти. */
  const dir = path.dirname(file);
  const missing = [...String(s).matchAll(/:::code[^\S\n]+(\S+)/g)]
    .map((m) => m[1])
    .filter((rel) => !fs.existsSync(path.join(dir, rel)));
  return { left: TXT.fencedCode(s), code: (s.match(/:::code /g) || []).length, missing };
}

/**
 * ⛔ ФІГУРИ — ТЕЖ ЛОКАЛЬНО, І ТЕЖ ОДРАЗУ. Геометрію міряє `checkers/svg.py`: написи один
 * на одному, лінія крізь напис, вихід за полотно, дрібний шрифт, і — з `--links` —
 * фігура, яку проза обіцяє директивою `![](img/…svg)`, а файлу немає.
 *
 * Нічого не лагодить: перемальовує фігуру своя одиниця `fig`, а тут лише огляд теки.
 *
 * ⚠️ `--links` вмикається ЛИШЕ тоді, коли всі фігури теми вже намальовані. Інакше
 * «обіцяно, а немає» означало б не ваду, а те, що черга ще не дійшла, — і кожен прогін
 * писав би в лог MISS, якого ніхто не робив.
 */
function checkFigures(dir, { links = true } = {}) {
  const r = runSvg([dir, "--min-font", "8", ...(links ? ["--links"] : [])]);
  if (!r.ok) return { issues: [], summary: "python не знайдено — фігури не перевірено" };
  return {
    issues: r.lines.filter((l) => /^(WARN|MISS)/.test(l)),
    summary: r.lines[r.lines.length - 1] || "",
  };
}

/**
 * Ім'я файла несе сама одиниця — і версія, і вставка.
 *
 * ⛔ ЗАГОЛОВОК І БЛОК ПЕРЕДУМОВ СКЛАДАЄ КОНВЕЄР, А НЕ АГЕНТ. Назва лежить у маніфесті,
 * передумови вирішив перший запит, адреси в них справжні — розбір інших не пускає. Просити
 * це в письменника означало б або по блоку в кожній групі, або жодного: обидва варіанти
 * ми вже мали. Тут це два рядки й жодної гілки.
 */
function writeArticle(u, text, preknow) {
  fs.mkdirSync(u.dir, { recursive: true });
  const file = path.join(u.dir, u.file);
  const head = /^\s*#\s/.test(text) ? "" : `# ${u.title}\n\n`;
  const pk = (preknow || []).length
    ? "<preknowlist>\n" + preknow
      .map((x) => `- [${x.title}](${x.addr})${x.why ? " — " + x.why : ""}`).join("\n")
      + "\n</preknowlist>\n\n"
    : "";
  fs.writeFileSync(file, head + pk + text, "utf8");
  return path.relative(MF.ROOT, file).split(path.sep).join("/");
}

/**
 * Код — у файли під носієм і мовою: `<тема>/<носій>/<мова>/<шлях>`. Носій — той `.md`,
 * що посилається на код, тож `proj` і `api` однієї теми не стикаються. Шлях із файла
 * агента береться лише відносний і без `..`: усе інше — не файл проєкту, а втеча з теки.
 */
function writeCode(u, files) {
  /* ⛔ ТЕКА МОВИ — ЧЕСНА. Каркас пише мову вільним рядком: «Python», «C++», «Arduino».
     Без нормалізації це давало теки `python/`, `c++/`, `arduino/` — яких не знає ні
     `langDirs`, ні корпус (там `py/`, `cpp/`, і платформа лягає ПІД мову), а правило
     «пара C↔C++ перевіряється наявністю теки `cpp/`» на такій теці не спрацьовує. */
  const base = path.join(u.dir, u.carrier, TXT.langDir(u.lang));
  const written = [];
  for (const f of files) {
    let rel = String(f.path || "").replace(/\\/g, "/").replace(/^\.?\//, "");
    /* Провідні сегменти, що повторюють носія й мову, зрізаємо: тека мови ВЖЕ є коренем
       проєкту, і «python/…» чи «<носій>/sql/…» — це той самий шлях удвічі. Завдання про
       це каже прямо, але правила про `:::code` описують шлях ВІД ТЕКИ ТЕМИ, і на цьому
       агент двічі поспіль дав саме довгу форму. Зрізати дешевше, ніж отримати
       `python/python/` на диску. */
    for (let i = 0; i < 4; i++) {
      const seg = rel.split("/")[0];
      if (!seg) break;
      if (seg.toLowerCase() === String(u.lang).toLowerCase() || seg === u.carrier) rel = rel.slice(seg.length + 1);
      else break;
    }
    if (!rel || rel.split("/").some((s) => s === "..") || path.isAbsolute(rel))
      throw new Error(`код: шлях «${f.path}» не є відносним шляхом у проєкті`);
    const p = path.join(base, rel);
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, String(f.body || "").replace(/\s*$/, "\n"), "utf8");
    written.push(path.relative(MF.ROOT, p).split(path.sep).join("/"));
  }
  return written;
}

/**
 * Файли коду цієї одиниці, готові до директиви `:::code` — шляхом ВІД ТЕКИ ТЕМИ, як
 * його резолвить рідер. Кличеться вже після того, як код написано (проза чекає на нього
 * на паузі), тож перелік справжній, а не обіцяний.
 */
function codeFiles(u, lang) {
  const carrier = u.file.replace(/\.md$/, "");
  const root = path.join(u.dir, carrier, TXT.langDir(lang));
  const out = [];
  const walk = (d, rel) => {
    let ents = [];
    try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const e of ents.sort((a, b) => a.name.localeCompare(b.name))) {
      const r = rel ? `${rel}/${e.name}` : e.name;
      if (e.isDirectory()) walk(path.join(d, e.name), r);
      else out.push(`${carrier}/${TXT.langDir(lang)}/${r}`);
    }
  };
  walk(root, "");
  return out;
}

/**
 * ⛔ ІМЕНА ФІГУР ДАЄ КОНВЕЄР, А НЕ АГЕНТ. Каркас називає лише номер розділу й задум;
 * ім'я файла виводиться з номера — і те саме ім'я бачать ОБИДВІ сторони: той, хто
 * малює, і той, хто ставить директиву в прозі. Дати агентові вигадувати адресу ми вже
 * пробували на вставках: вийшло правдоподібне ім'я в порожнечу.
 *
 * Дві фігури на один розділ — не помилка: друга дістає суфікс, бо один файл двома
 * задумами не буває.
 */
function figNames(figs) {
  /* Ім'я — за тим, що зображено: каркас чи письмо дають слуг фігури, і він стає іменем
     файла. Без імені — за номером розділу. Ім'я, що вже є (фігура детальної в базовій),
     не чіпаємо. Однакові імена в одній темі дістають суфікс. */
  const seen = new Map();
  return (figs || []).map((f) => {
    if (f.file) return f;
    const base = f.name ? f.name : `fig-${f.section}`;
    const n = (seen.get(base) || 0) + 1;
    seen.set(base, n);
    return { ...f, file: `img/${base}${n > 1 ? "-" + n : ""}.svg` };
  });
}

/**
 * Тексти файлів коду однієї мови — у письмо проєкту йде сам код, не шляхи. Рядки
 * пронумеровано: директива може підключати шматок файла межами рядків, і межі беруться
 * рівно за цією нумерацією.
 */
function codeText(u, lang) {
  return codeFiles(u, lang).map((rel) => {
    let body = "";
    try { body = fs.readFileSync(path.join(u.dir, rel), "utf8"); } catch { return null; }
    const lines = body.trimEnd().split("\n");
    const w = String(lines.length).length;
    return `файл: ${rel}\n${lines.map((l, i) => `${String(i + 1).padStart(w)}│ ${l}`).join("\n")}`;
  }).filter(Boolean).join("\n\n");
}

/** Фігура на диск: `<тема>/img/<ім'я>.svg`. Ім'я вже вирішене — тут лише запис. */
function writeFigure(u, file, svg) {
  const p = path.join(u.dir, file);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, String(svg).trim() + "\n", "utf8");
  return path.relative(MF.ROOT, p).split(path.sep).join("/");
}

/** Один запуск `checkers/svg.py`. Немає Python — не вада конвеєра, а відсутній звіт. */
function runSvg(args) {
  for (const py of ["python", "py -3", "python3"]) {
    const bin = py.split(" ")[0];
    const r = cp.spawnSync(bin, [...py.split(" ").slice(1),
      path.join(__dirname, "..", "checkers", "svg.py"), ...args], { encoding: "utf8" });
    if (r.error || r.status === null) continue;
    return { ok: true, lines: String(r.stdout || "").split("\n").map((x) => x.trim()).filter(Boolean) };
  }
  return { ok: false, lines: [] };
}

/**
 * Геометрія ОДНІЄЇ фігури — оракул для того, хто її щойно намалював. Підлога кегля тут
 * 10, а не 8, як на оглядині теки: 8 терпить давні фігури корпусу, 10 — це те, що
 * правила вимагають від нової.
 *
 * Повертає самі зауваження, без імені файла: адресат один і він його знає.
 */
function checkFigure(u, file) {
  const r = runSvg([path.join(u.dir, file), "--min-font", "10"]);
  return r.ok ? r.lines.filter((l) => /^WARN/.test(l)).map((l) => l.replace(/^WARN\s+[^:]*:\s*/, "")) : [];
}

/** Операції для писаря маніфесту. Статус приходить ззовні — вирішує не цей файл. */
const ops = (u, status) => [
  u.insert
    ? { op: "insert", slug: u.slug, type: u.type, file: u.file, status }
    : { op: "status", slug: u.slug, ver: u.type === "basic" ? "basic" : "detailed", status },
];

/**
 * Ключ пошуку згадок із назви теми — ЦІЛА назва, а не перше слово. З першим словом
 * «Одержимість примітивами» ловила «одержимість простотою» з історії Arduino: пошук за
 * коротким словом дає омонім, і саме так у перший прогін заїхало шість чужих абзаців.
 */
function titleRe(title) {
  const esc = String(title).replace(/[-.*+?^${}()|[\]\\]/g, (c) => "\\" + c);
  return new RegExp(esc.replace(/\s+/g, "\\s+"), "i");
}

module.exports = {
  humanPath, titleRe, unitOf, mentions, neighbours, books, shelf, chapterTopics, bookTopics, topicHead,
  linkContext, aroundLink, fileHead, resolveLinks, unlink, splitSections, joinSections, preknow, isDuplicate,
  size, BANDS, assemble, writeArticle, writeCode, codeFiles, codeText, linkable,
  fixFormulas, decamp, fixFences, unfenceDirectives, checkFences, checkFigures, figNames, writeFigure, checkFigure, ops,
};
