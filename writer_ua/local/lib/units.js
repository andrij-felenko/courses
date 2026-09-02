#!/usr/bin/env node
/* ============================================================================
   units.js — ОДИНИЦЯ РОБОТИ і МОВА ВІДБОРУ. Спільна для `find` і `status`.

   НАВІЩО. Пошук ганяють постійно й недбало, а зміна статусу — це запис. Злиті в
   одну команду, вони означають, що одруківка у фільтрі мовчки щось перепише. Тож
   команди дві, а мова відбору ОДНА — і живе вона тут, щоб не розійтися.

   ЩО ТАКЕ ОДИНИЦЯ. Статус, рівень і прапорець `recode` висять не на темі, а на
   ВЕРСІЇ (`basic`/`detailed`) і на КОЖНІЙ вставці окремо. Тому одиниця відбору —
   не тема, а те, що має власний статус:

     embedded/cherha-oflainu:detailed          версія
     embedded/cherha-oflainu:basic             версія
     embedded/cherha-oflainu:proj-queue        вставка (файл без .md)

   Тема цілком адресується без двокрапки — `embedded/cherha-oflainu`; `parseAddr` таку
   адресу приймає, але в ОДИНИЦЮ вона поки не резолвиться: одиниця — це те, що має
   власний статус, а тема цілком його не має.

   ⛔ Вказівник (`ref`) статусу теж не має, і `status` його ніколи не пише — отже, він
   НЕ адресується: `slug` у нього `null`, `addrOf` вертає `null`. Інакше адреса виходила
   б тризначною («книга/книга/тема»), і `parseAddr` її не розбирав би.

   Маніфест читається ЛИШЕ через scripts/lib/manifest7.js (CLAUDE.md: один модуль
   читає й пише схему 7). Тут — жодного власного розбору JSON.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("../../../scripts/lib/manifest7.js");

const ROOT = M7.ROOT;
const CONTENT = M7.CONTENT;
const INSERTS = M7.INSERT_TYPES;                       // hist comp math proj api
const VERSIONS = ["basic", "detailed"];
const TYPES = [...VERSIONS, ...INSERTS];
const STATUSES = ["done", "pending", "empty", "update", "deeper", "recheck"];

/* ── адреса ────────────────────────────────────────────────────────────────── */

/** `книга/тема:тип` → {book, slug, part}. `part` порожній для теми цілком. */
function parseAddr(s) {
  const str = String(s || "").trim();
  if (!str) return null;
  const colon = str.indexOf(":");
  const head = colon < 0 ? str : str.slice(0, colon);
  const part = colon < 0 ? "" : str.slice(colon + 1);
  const slash = head.indexOf("/");
  if (slash < 0) return null;
  const book = head.slice(0, slash);
  const slug = head.slice(slash + 1);
  if (!book || !slug || slug.includes("/")) return null;
  return { book, slug, part };
}

/** Адреса одиниці; `null` для вказівника — він не адресується. */
const addrOf = (u) => (u.slug == null ? null : `${u.book}/${u.slug}` + (u.part ? `:${u.part}` : ""));

/* ── перелік одиниць ───────────────────────────────────────────────────────── */

/* Той самий маніфест хочуть і bookList (за назвою), і enumerate (за темами). Кеш, щоб
   не платити за читання книги двічі на один прогін. */
const _loaded = new Map();
function loadBook(dir) {
  if (!_loaded.has(dir)) _loaded.set(dir, M7.loadBook(dir));
  return _loaded.get(dir);
}

/** Книги полиці як [{slug, kind, title, dir}], з фільтром за видом і слугом. */
function bookList({ kinds, books } = {}) {
  const out = [];
  for (const [slug, b] of M7.books()) {
    if (kinds && kinds.length && !kinds.includes(b.kind)) continue;
    if (books && books.length && !books.includes(slug)) continue;
    /* назва книги живе тільки в її manifest.json; вигадувати з слуга — брехати */
    const book = loadBook(b.bookDir);
    out.push({ slug, kind: b.kind, title: (book && book.manifest.title) || null, dir: b.bookDir });
  }
  return out;
}

/** Шлях до файла одиниці. Версії мають сталі імена, вставка — своє з маніфесту. */
function fileOf(u) {
  if (u.slug == null) return null;                     // вказівник свого файла не має
  const dir = path.join(u.bookDir, u.slug);
  if (u.part === "basic") return path.join(dir, u.slug + ".md");
  if (u.part === "detailed") return path.join(dir, u.slug + "-d.md");
  if (u.file) return path.join(dir, u.file);
  return null;
}

/** Тека коду одиниці: названа .md-носієм, тож proj і api однієї теми не стикаються. */
function codeDirOf(u) {
  const f = fileOf(u);
  return f ? f.replace(/\.md$/, "") : null;
}

/**
 * Усі одиниці корпусу (або відібраної його частини) плоским списком.
 * Диск НЕ чіпається — це робить фільтр, і лише коли його про це просять.
 */
function enumerate({ kinds, books } = {}) {
  const out = [];
  for (const b of bookList({ kinds, books })) {
    const book = loadBook(b.dir);
    if (!book) continue;
    for (const t of M7.allTopics(book)) {
      const base = {
        book: b.slug, kind: b.kind, bookDir: b.dir,
        group: t.group, chapter: t.chapter, title: t.title,
      };
      if (!t.own) {                                    // вказівник на чужу статтю
        out.push({ ...base, slug: null, part: "", ref: t.ref, node: t.node });
        continue;
      }
      const n = t.node;
      for (const v of VERSIONS) {
        if (!n[v]) continue;
        out.push({
          ...base, slug: t.slug, part: v, node: n[v], topic: n,
          status: n[v].status, level: n[v].level ?? null, recode: !!n[v].recode,
        });
      }
      for (const ins of INSERTS)
        for (const it of n[ins] || [])
          out.push({
            ...base, slug: t.slug, part: String(it.file || "").replace(/\.md$/, ""),
            insert: ins, file: it.file, node: it, topic: n,
            status: it.status, level: it.level ?? null, recode: !!it.recode,
          });
    }
  }
  return out;
}

/* ── фільтр ────────────────────────────────────────────────────────────────── */

/** `2`, `2-4`, `3-` → предикат. Порожній рівень не проходить жодного діапазону. */
function levelPred(spec) {
  const str = String(spec).trim();
  /* `--level ""` мовчки означало «без фільтра» — тепер це така сама одруківка, як `abc` */
  if (!str) throw new Error("не розумію --level (порожньо)");
  const m = /^(\d*)(?:-(\d*))?$/.exec(str);
  if (!m) throw new Error(`не розумію --level ${spec}`);
  const lo = m[1] === "" ? -Infinity : Number(m[1]);
  const hi = m[2] === undefined ? (m[1] === "" ? Infinity : lo) : (m[2] === "" ? Infinity : Number(m[2]));
  return (v) => v != null && v >= lo && v <= hi;
}

/** Глоб `*` по слугу; без `*` — точний збіг. */
function globPred(spec) {
  if (!spec.includes("*")) return (s) => s === spec;
  const re = new RegExp("^" + spec.split("*").map((x) => x.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join(".*") + "$");
  return (s) => re.test(s);
}

/**
 * Відбір за розібраними прапорцями. Диск читається тільки під --file/--code,
 * і лише для тих одиниць, що дійшли до цієї перевірки.
 */
function filter(units, f = {}) {
  let out = units;
  const has = (arr) => arr && arr.length;

  if (has(f.group)) out = out.filter((u) => f.group.includes(u.group));
  if (has(f.chapter)) out = out.filter((u) => f.chapter.includes(u.chapter));
  if (has(f.type)) out = out.filter((u) => f.type.includes(u.insert || u.part));
  if (has(f.status)) out = out.filter((u) => f.status.includes(u.status));
  if (has(f.notStatus)) out = out.filter((u) => !f.notStatus.includes(u.status));
  if (f.level !== undefined) { const p = levelPred(f.level); out = out.filter((u) => p(u.level)); }
  if (f.recode === true) out = out.filter((u) => u.recode);
  if (f.recode === false) out = out.filter((u) => !u.recode);
  if (f.ref === true) out = out.filter((u) => !!u.ref);
  if (f.ref === false) out = out.filter((u) => !u.ref);
  if (f.slug) { const p = globPred(f.slug); out = out.filter((u) => u.slug != null && p(u.slug)); }
  if (f.title) {
    const q = f.title.toLocaleLowerCase("uk");
    out = out.filter((u) => (u.title || "").toLocaleLowerCase("uk").includes(q));
  }
  /* «шляху немає» = «файла немає»: інакше вказівники випадали б з ОБОХ відповідей,
     і `--has-file` + `--no-file` не давали б усього. Те саме для теки коду. */
  if (f.file !== undefined) {
    out = out.filter((u) => { const p = fileOf(u); return (!!p && fs.existsSync(p)) === f.file; });
  }
  if (f.code !== undefined) {
    out = out.filter((u) => {
      const d = codeDirOf(u);
      const yes = !!d && fs.existsSync(d) && fs.statSync(d).isDirectory();
      return yes === f.code;
    });
  }
  return out;
}

/* ── розбір спільних прапорців ─────────────────────────────────────────────── */

const list = (v) => String(v).split(",").map((x) => x.trim()).filter(Boolean);

/**
 * Розбирає спільну частину CLI. Повертає {flags, rest} — `rest` це те, чого
 * ця мова не знає, і власні прапорці команди розбирає вже вона сама.
 * ⛔ Невідомий прапорець НЕ ковтається мовчки: команда мусить сама його впізнати
 *    або впасти — інакше одруківка у фільтрі означала б ширший відбір, ніж хотіли.
 */
function parseArgs(argv) {
  const f = {}; const rest = [];
  const need = (i, name) => {
    const v = argv[i + 1];
    if (v === undefined || v.startsWith("--")) throw new Error(`${name} без значення`);
    return v;
  };
  /* перелічний прапорець ПОВТОРЮЄТЬСЯ в об'єднання: `--status done --status recheck`
     колись мовчки лишав саме останнє, і відбір виходив утричі вужчий, ніж просили */
  const add = (key, i, name) => {
    f[key] = [...new Set([...(f[key] || []), ...list(need(i, name))])];
  };
  /* одиничному прапорцю об'єднувати нічого, тож повтор — це одруківка, а не намір */
  const one = (key, i, name) => {
    if (f[key] !== undefined) throw new Error(`${name} двічі — значення в нього одне`);
    f[key] = need(i, name);
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    switch (a) {
      case "--kind": add("kinds", i, a); i++; break;
      case "--book": add("books", i, a); i++; break;
      case "--group": add("group", i, a); i++; break;
      case "--chapter": add("chapter", i, a); i++; break;
      case "--type": add("type", i, a); i++; break;
      case "--status": add("status", i, a); i++; break;
      case "--not-status": add("notStatus", i, a); i++; break;
      case "--slug": one("slug", i, a); i++; break;
      case "--title": one("title", i, a); i++; break;
      case "--level": one("level", i, a); i++; break;
      case "--recode": f.recode = true; break;
      case "--no-recode": f.recode = false; break;
      case "--ref": f.ref = true; break;
      case "--own": f.ref = false; break;
      case "--has-file": f.file = true; break;
      case "--no-file": f.file = false; break;
      case "--has-code": f.code = true; break;
      case "--no-code": f.code = false; break;
      default: rest.push(a);
    }
  }
  return { flags: f, rest };
}

/** Перевірка значень — щоб `--status recheсk` із кирилицею не дав тихо нуль рядків. */
function validate(f) {
  const bad = [];
  const known = (arr, ok, what) => (arr || []).forEach((v) => { if (!ok.includes(v)) bad.push(`${what}: ${v}`); });
  known(f.status, STATUSES, "статус");
  known(f.notStatus, STATUSES, "статус");
  known(f.type, TYPES, "тип");
  known(f.kinds, [...new Set([...M7.books().values()].map((b) => b.kind))], "вид");
  const bookSlugs = new Set(M7.books().keys());
  (f.books || []).forEach((b) => { if (!bookSlugs.has(b)) bad.push(`книга: ${b}`); });
  if (bad.length) throw new Error("невідоме значення — " + bad.join(", "));

  if (f.level !== undefined) levelPred(f.level);        // одруківка в рівні падає тут, а не мовчить

  /* Групу й розділ звіряємо зі СПРАВЖНІМИ слугами відібраних книг: без цього одруківка
     в `--group` давала тихий нуль, який читається як «нічого не лишилося». */
  if ((f.group && f.group.length) || (f.chapter && f.chapter.length)) {
    const groups = new Set(), chapters = new Set();
    for (const b of bookList({ kinds: f.kinds, books: f.books })) {
      const book = loadBook(b.dir);
      if (!book) continue;
      for (const g of M7.groupSlugs(book)) {
        groups.add(g);
        for (const c of M7.chapterSlugs(book, g)) chapters.add(c);
      }
    }
    (f.group || []).forEach((v) => { if (!groups.has(v)) bad.push(`група: ${v}`); });
    (f.chapter || []).forEach((v) => { if (!chapters.has(v)) bad.push(`розділ: ${v}`); });
    if (bad.length) throw new Error("невідоме значення — " + bad.join(", "));
  }
}

/** Ключ, яким адреса зустрічається з одиницею. Для вказівника ключа немає. */
const keyOf = (u) => (u.slug == null ? null : `${u.book}/${u.slug}:${u.part}`);

/** Одиниці за списком адрес (вхід `status`-а з труби):
 *  {units, missing — таких адрес нема, ambiguous — адреса вказує на двох}. */
function byAddrs(addrs) {
  const want = new Map();                                // ключ → {addr, book}, розібрано ОДИН раз
  for (const a of addrs) {
    const p = parseAddr(a);
    if (!p) throw new Error(`не розумію адресу: ${a}`);
    want.set(`${p.book}/${p.slug}:${p.part}`, { addr: a, book: p.book });
  }
  const books = [...new Set([...want.values()].map((w) => w.book))];
  const all = enumerate({ books });
  const got = new Map(); const clash = new Map();
  for (const u of all) {
    const k = keyOf(u);
    if (k === null || !want.has(k)) continue;
    if (!got.has(k)) { got.set(k, u); continue; }
    /* Той самий файл вставки, зареєстрований під двома типами, дає дві одиниці з однією
       адресою. Це вада ДАНИХ корпусу; мовчки віддати останню — сховати її. */
    const types = clash.get(k) || [got.get(k).insert || got.get(k).part];
    types.push(u.insert || u.part);
    clash.set(k, types);
  }
  const missing = [...want.entries()].filter(([k]) => !got.has(k)).map(([, w]) => w.addr);
  /* Неоднозначну адресу ПРОПУСКАЄМО, а не падаємо на ній: у корпусі така одна, і
     кинутий виняток убивав трубу з двадцяти п'яти тисяч адрес через єдину ваду
     даних. Викликач її показує — так само, як `find` показує повторені адреси. */
  const ambiguous = [...clash].map(([k, types]) => ({ addr: want.get(k).addr, types }));
  for (const [k] of clash) got.delete(k);
  return { units: [...got.values()], missing, ambiguous };
}

/* ── труба як джерело адрес ────────────────────────────────────────────────── */

/**
 * `given` — чи джерело адрес узагалі є, і це НЕ те саме, що «прийшла хоч одна
 * адреса». Порожня труба означає «нічого не надійшло», а не «візьми фільтри»:
 * інакше `find … --ids | status --book X --set … --apply` при нулі знахідок
 * мовчки провалився б на фільтр і переписав усю книгу.
 *
 * Труба й перенаправлений файл — джерело; термінал і /dev/null — ні. Розрізняємо
 * бітами типу в `mode`, бо на Windows Node каже `isFIFO() === false` навіть для
 * справжньої труби, і покладатися на нього не можна.
 */
function stdinAddrs() {
  let kind = 0;
  try { kind = (fs.fstatSync(0).mode & 0o170000) >>> 0; } catch { return { given: false, addrs: [] }; }
  if (kind !== 0o010000 && kind !== 0o100000) return { given: false, addrs: [] };
  let raw = "";
  try { raw = fs.readFileSync(0, "utf8"); } catch { return { given: true, addrs: [] }; }
  return { given: true, addrs: raw.split(/\r?\n/).map((s) => s.trim()).filter((s) => s && !s.startsWith("#")) };
}

module.exports = {
  ROOT, CONTENT, TYPES, VERSIONS, INSERTS, STATUSES,
  parseAddr, addrOf, fileOf, codeDirOf,
  bookList, enumerate, filter, parseArgs, validate, byAddrs, stdinAddrs,
};
