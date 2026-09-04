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
const MF = require("../lib/manifest.js");
const TXT = require("../lib/text.js");
const DUP = require("../lib/dupes.js");
const FRM = require("../checkers/formulas.js");

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
function mentions(u, re, { limit = 6, roots = ["root"] } = {}) {
  const out = [];
  for (const r of roots) {
    for (const f of walkMd(path.join(MF.ROOT, r))) {
      if (f.replace(/\\/g, "/").includes(`/${u.slug}/`)) continue;
      let txt = ""; try { txt = fs.readFileSync(f, "utf8"); } catch { continue; }
      if (!re.test(txt)) continue;
      const rel = path.relative(MF.ROOT, f).split(path.sep).join("/");
      const paras = txt.split(/\n\s*\n/);
      for (let i = 0; i < paras.length && out.length < limit; i++) {
        if (!re.test(paras[i]) || paras[i].length < 120) continue;
        const cut = (s, n) => String(s || "").replace(/\s+/g, " ").slice(0, n).trim();
        out.push(`— ${humanPath(rel)}\n  ${rel}\n[абзац до] ${cut(paras[i - 1], 280)}\n` +
          `[згадка] ${cut(paras[i], 380)}\n[абзац після] ${cut(paras[i + 1], 280)}`);
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

/** Усі книги репо назвами — для каркаса статті. */
const books = () => [...MF.books().entries()]
  .map(([slug, b]) => { const x = MF.loadBook(b.bookDir); return x ? (x.manifest.title || slug) : null; })
  .filter(Boolean).join("\n");

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
const assemble = (parts) => parts.map((p) => String(p || "").trim()).filter(Boolean).join("\n\n") + "\n";

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
  return { fixed: e.length, delims: FRM.delimiters(s).map((d) => `рядок ${d.line}: ${d.why}`) };
}

/** Ім'я файла несе сама одиниця — і версія, і вставка. Тут лише запис. */
function writeArticle(u, text) {
  fs.mkdirSync(u.dir, { recursive: true });
  const file = path.join(u.dir, u.file);
  fs.writeFileSync(file, text, "utf8");
  return path.relative(MF.ROOT, file).split(path.sep).join("/");
}

/**
 * Код — у файли під носієм і мовою: `<тема>/<носій>/<мова>/<шлях>`. Носій — той `.md`,
 * що посилається на код, тож `proj` і `api` однієї теми не стикаються. Шлях із файла
 * агента береться лише відносний і без `..`: усе інше — не файл проєкту, а втеча з теки.
 */
function writeCode(u, files) {
  const base = path.join(u.dir, u.carrier, u.lang);
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
  const root = path.join(u.dir, carrier, String(lang).toLowerCase());
  const out = [];
  const walk = (d, rel) => {
    let ents = [];
    try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const e of ents.sort((a, b) => a.name.localeCompare(b.name))) {
      const r = rel ? `${rel}/${e.name}` : e.name;
      if (e.isDirectory()) walk(path.join(d, e.name), r);
      else out.push(`${carrier}/${String(lang).toLowerCase()}/${r}`);
    }
  };
  walk(root, "");
  return out;
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
  humanPath, titleRe, unitOf, mentions, neighbours, books, preknow, isDuplicate,
  size, BANDS, assemble, writeArticle, writeCode, codeFiles, linkable, fixFormulas, ops,
};
