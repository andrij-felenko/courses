#!/usr/bin/env node
/* ============================================================================
   move.js — ПЕРЕЙМЕНУВАТИ або ПЕРЕКЛАСТИ тему, не лишивши по собі битих лінків.

   Сам `git mv` тривіальний; робота — у чотирьох речах, яких він не робить:

     1. запис у маніфесті (слуг теми, її розділ, назва);
     2. усі посилання `root:<книга>/<тема>` по КОРПУСУ — а в них ще й ХВІСТ: 14 104
        посилання цілять не в тему, а в конкретний файл (`root:книга/dto/dto.md`),
        і версійні файли звуться слугом, тож разом із текою переїжджають і вони.
        Переписати саму лише тему — лишити `…/dto-new/dto.md`, тобто биту адресу;
     3. усі `"ref"` на цю тему в маніфестах ІНШИХ книг — курси посилаються сюди;
     4. директиви `:::code` у прозі САМОЇ теми: шлях у них відлічується від теки
        теми й починається іменем теки коду, тобто слугом (`:::code dto/py/…`,
        `:::code dto-d/ts/…`). Перейменувати теку й лишити директиву — це зламати
        кожен код-блок теми; по корпусу таких рядків 7927 у 2585 темах.

   Пропустиш будь-яку — і лагодити доведеться руками по всьому дереву.

   ⚠️ ГРУПА Й РОЗДІЛ У ШЛЯХУ НЕ ЖИВУТЬ. Тема лежить пласко під книгою, тож
   перекладання в інший розділ (`--to-chapter`) — це ПРАВКА JSON, і жодного файла
   не рухає. Файли рухає тільки зміна слуга (`--to`).

   ⛔ Між книгами так не переносимо: це два різні маніфести, і чесно робиться парою
   «завести в цільовій + зняти з джерела», зі своїм рішенням про долю статусів.

   ПОРЯДОК ЗАПИСУ: ТЕКСТ → ФАЙЛИ → МАНІФЕСТ, і він не довільний. Правки тексту
   зібрані за СТАРИМИ шляхами, тож робити їх треба, поки ті шляхи ще існують: у
   корпусі 4657 тем посилаються самі на себе, і при зворотному порядку такий файл
   уже переїхав, а запис у нього падає ENOENT посеред роботи — теки перенесено,
   частину чужих файлів переписано, маніфест не оновлено. Маніфест іде останнім,
   бо доки він каже стару адресу, стан на диску ще читається як «недороблене».

   ПЕРЕДПОЛІТ. Усе, що можна перевірити наперед, перевіряється ДО першого запису:
   джерела переносу на місці, цілі вільні, файли для правки пишуться, і сам
   писар маніфесту насухо не заперечує. Не пройшло — не починаємо взагалі.

   Файли рухаємо через `git mv` (історія лишається); нетрековане — звичайним
   перейменуванням. Маніфест пишеться ЛИШЕ через `writer_ua/lib/manifest.js`.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const cp = require("child_process");
const MF = require("../lib/manifest.js");
const DUP = require("../lib/dupes.js");

const HELP = `
move — перейменувати тему або перекласти її в інший розділ

  node writer_ua/local/move.js --from <книга>/<тема> [що] [--apply]

ЩО
  --to <новий-слуг>          перейменувати: тека, файли, теки коду,
                             директиви :::code, лінки по корпусу, ref у курсах
  --to-chapter <гр>/<розд>   перекласти в інший розділ ТІЄЇ Ж книги (лише JSON)
  --group-title "Назва"      назва НОВОЇ групи — без неї неіснуюча не заводиться
  --chapter-title "Назва"    назва НОВОГО розділу — так само
  --title "Нова назва"       заодно змінити назву теми

ЗАПИС
  (типово)   сухий прогін: що поїде, що перепишеться, скільки лінків,
             що на це каже писар маніфесту і чи схожий новий слуг на наявні
  --apply    зробити

Хоч одне з --to / --to-chapter / --title обов'язкове.
⛔ Між книгами не переносить — це пара «завести там + зняти тут».
`;

const rel = (p) => path.relative(MF.ROOT, p).replace(/\\/g, "/");
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/* ── слуг ──────────────────────────────────────────────────────────────────── */

/**
 * Присуд про слуг — той самий, що в `add.js`: ASCII, малими, дефісами й БЕЗ номерів
 * (ні в голові, ні хвостом `-2`). Номер у слугу означає, що поняття назвали двічі й
 * розрізнили лічильником, — а нумерації канон не має ніде, тож `dto-2` це не
 * ім'я, а ознака невирішеного дубля. Ціною ловляться й імена стандартів (`iso-8601`):
 * механічно вони від лічильника не відрізняються, і краще перепитати людину, ніж
 * пропустити `cache-2`.
 *
 * ⚠️ Правило спільне з `add.js` і продубльоване свідомо: його місце — `lib/units.js`,
 * куди воно й переїде, коли обидві команди можна буде правити одночасно.
 */
function slugFault(s) {
  if (!/^[a-z][a-z0-9-]*$/.test(s)) return "слуг це ASCII малими з дефісами й починається з літери";
  if (/-\d+$/.test(s)) return "у хвості номер — це нумерація, а канон її не має ніде";
  if (/--|-$/.test(s)) return "подвійний або кінцевий дефіс";
  return null;
}

/* ── git ───────────────────────────────────────────────────────────────────── */

function tracked(p) {
  try {
    cp.execFileSync("git", ["ls-files", "--error-unmatch", rel(p)],
      { cwd: MF.ROOT, stdio: "pipe" });
    return true;
  } catch { return false; }
}

/** Перенос із збереженням історії; нетрековане — звичайним rename. */
function movePath(from, to) {
  fs.mkdirSync(path.dirname(to), { recursive: true });
  if (tracked(from)) {
    cp.execFileSync("git", ["mv", rel(from), rel(to)], { cwd: MF.ROOT, stdio: "pipe" });
  } else fs.renameSync(from, to);
}

/* ── обхід корпусу ─────────────────────────────────────────────────────────── */

function walk(dir, out = []) {
  let ents = [];
  try { ents = fs.readdirSync(dir, { withFileTypes: true }); } catch { return out; }
  for (const e of ents) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else out.push(p);
  }
  return out;
}

/**
 * Посилання на тему в прозі. Шукаємо `root:<книга>/<слуг>` із межею після слуга,
 * щоб `cache` не влучив у `cache-lines`: далі або кінець, або `/файл`, або те, що
 * в адресі стояти не може.
 *
 * ХВІСТ ловимо ОКРЕМОЮ групою й лише тоді, коли він є іменем ВЕРСІЇ старої теми —
 * `<слуг>.md` або `<слуг>-d.md`. Ці два файли звуться слугом і їдуть разом із текою,
 * тож їхнє ім'я — частина того самого перейменування. Вставки мають власні імена
 * (`proj-mapping.md`, `hist-dto.md`) і не рухаються, тому будь-який інший хвіст
 * лишається байт-у-байт: група просто не збігається й посилання правиться лише в
 * частині теми.
 */
function linkRe(book, slug) {
  return new RegExp(`(root:${esc(book)}/)${esc(slug)}(?![a-z0-9-])(/${esc(slug)}(-d)?\\.md)?`, "gi");
}

/** Хвіст, що лишився старим після заміни, — для пост-перевірки. */
function tailRe(book, newSlug, oldSlug) {
  return new RegExp(`root:${esc(book)}/${esc(newSlug)}/${esc(oldSlug)}(-d)?\\.md`, "gi");
}

/**
 * Директива `:::code` у прозі теми. Шлях у ній локальний — від теки ТЕМИ — і
 * починається .md-носієм: `<слуг>` для базової, `<слуг>-d` для детальної. Межа та
 * сама за змістом, що в `linkRe`: після імені мусить іти `/`, інакше `dto` влучив
 * би в `dto-other`. Відступ буває (директива всередині списку), тому `^\s*`.
 */
function codeRe(slug) {
  return new RegExp(`^(\\s*:::code\\s+)${esc(slug)}(-d)?(?=/)`, "gm");
}

/* ── звіт писаря маніфесту ────────────────────────────────────────────────────────── */

const REPORT = [["renamed", "слуг"], ["moved", "розділ"], ["retitled", "назва"],
  ["group", "нова група"], ["chapter", "новий розділ"]];

const report = (r) => {
  const parts = REPORT.filter(([k]) => r[k]).map(([k, name]) => `${name} ${r[k]}`);
  return `змін ${r.changed}` + (parts.length ? ` (${parts.join(", ")})` : "");
};

/**
 * Підказки про можливий дубль для нового слуга. Друкуються ЗАВЖДИ й до запису:
 * `--to` вводить у корпус нове ім'я поняття, і саме тут його ще дешево передумати.
 * Не блокують — об'єднувати теми чи ні, вирішує людина.
 */
function hints(bookSlug, oldSlug, newSlug) {
  let out;
  try { out = DUP.hints(newSlug, bookSlug); }
  catch (e) {
    /* Мовчазний збій підказок — це найгірше з можливого: людина вирішить, що
       сигналів немає, тоді як їх просто не рахували. */
    console.error(`move: підказки про дублі не порахувалися (${e.message}) — новий слуг звір руками`);
    return;
  }
  /* Стара тема ще в маніфесті й на перейменуванні майже завжди «схожа» на нову
     (`cache` → `cache-lines` — вкладений слуг). Але вона ж цією командою і зникає,
     тож це не дубль, а власна тінь: показувати її — вчити гортати підказки. */
  const live = out.filter((h) => !h.includes(`схожа на: ${oldSlug} —`));
  /* Порожній результат кажемо вголос: інакше «підказок нема» не відрізнити від
     «підказок не рахували», а різниця між ними — уся цінність перевірки. */
  if (!live.length) { console.log(`\nможливі дублі для «${newSlug}»: сигналів немає`); return; }
  console.log(`\nможливі дублі для «${newSlug}» (не блокують — вирішує людина):`);
  live.forEach((h) => console.log("  ⚠ " + h));
}

/* ── головне ───────────────────────────────────────────────────────────────── */

/* Білий перелік ключів. Невідомий прапорець — це одруківка (`--tochapter` замість
   `--to-chapter`), і ковтати її мовчки означає зробити не те, що просили: команда
   пройде, а половина наміру зникне. */
const VALUE_KEYS = ["from", "to", "to-chapter", "title", "group-title", "chapter-title"];
const BOOL_KEYS = ["apply"];

function main(argv) {
  if (argv.includes("--help") || argv.includes("-h") || !argv.length) { console.log(HELP.trim()); return 0; }

  const o = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) throw new Error(`не розумію: ${a}`);
    const k = a.slice(2);
    if (BOOL_KEYS.includes(k)) { o[k] = true; continue; }
    if (!VALUE_KEYS.includes(k))
      throw new Error(`невідомий прапорець: ${a} — знаю ${[...VALUE_KEYS, ...BOOL_KEYS].map((x) => "--" + x).join(" ")}`);
    const v = argv[i + 1];
    if (v === undefined || v.startsWith("--")) throw new Error(`${a} без значення`);
    if (k in o) throw new Error(`${a} двічі`);
    o[k] = v; i++;
  }

  if (!o.from) throw new Error("--from без значення: потрібне <книга>/<тема>");
  const [bookSlug, slug, ...tail] = o.from.split("/");
  if (!bookSlug || !slug || tail.length) throw new Error("--from хоче рівно <книга>/<тема>");
  if (!o.to && !o["to-chapter"] && !o.title)
    throw new Error("що робимо — --to, --to-chapter або --title");
  /* Назва для нової групи чи розділу без самого перекладання нічого не заводить —
     отже, або одруківка, або людина чекала не того. */
  if ((o["group-title"] || o["chapter-title"]) && !o["to-chapter"])
    throw new Error("--group-title/--chapter-title мають сенс лише з --to-chapter");

  const shelf = MF.books().get(bookSlug);
  if (!shelf) throw new Error(`книги «${bookSlug}» немає`);
  const bookDir = shelf.bookDir;
  const book = MF.loadBook(bookDir);
  const t = MF.findTopic(book, slug);
  if (!t) throw new Error(`теми «${slug}» у книзі «${bookSlug}» немає`);

  const topicDir = path.join(bookDir, slug);
  const plan = [], ops = [], moves = [];
  /* Передполіт судить ДО-стан, а `moves` виконуються по черзі, тож внутрішні шляхи
     в них уже під новою текою. Тому що перевіряти — тримаємо окремо. */
  const mustExist = [], mustBeFree = [];
  let newSlug = slug;

  /* ── зміна слуга: файли й теки ── */
  if (o.to) {
    newSlug = o.to;
    if (newSlug.includes("/")) throw new Error("--to хоче тільки слуг, без книги: між книгами ця команда не переносить");
    const fault = slugFault(newSlug);
    if (fault) throw new Error(`«${newSlug}» не є слугом: ${fault}`);
    if (newSlug === slug) throw new Error("--to збігається зі старим слугом");
    if (MF.findTopic(book, newSlug)) throw new Error(`слуг «${newSlug}» у книзі вже зайнятий`);

    if (fs.existsSync(topicDir)) {
      const to = path.join(bookDir, newSlug);
      if (fs.existsSync(to)) throw new Error(`тека «${rel(to)}» уже є`);
      moves.push([topicDir, to]);
      mustExist.push(topicDir); mustBeFree.push(to);
      /* Версії названі слугом, тож їдуть і вони — разом зі своїми теками коду,
         бо тека коду зветься .md-носієм. Вставки мають власні імена й лишаються. */
      for (const [from, name] of [[slug + ".md", newSlug + ".md"], [slug + "-d.md", newSlug + "-d.md"]]) {
        for (const [a, b] of [[from, name], [from.replace(/\.md$/, ""), name.replace(/\.md$/, "")]]) {
          if (!fs.existsSync(path.join(topicDir, a))) continue;
          moves.push([path.join(to, a), path.join(to, b)]);
          mustExist.push(path.join(topicDir, a));
          /* Ціль судимо в СТАРІЙ теці: вона поїде цілком, тож зайняте ім'я всередині
             неї буде зайняте й у новій. */
          mustBeFree.push(path.join(topicDir, b));
        }
      }
    } else plan.push(`теки ${rel(topicDir)} на диску немає — рухати нічого`);

    ops.push({ op: "rename", slug, to: newSlug, title: o.title });
    plan.push(`слуг    ${bookSlug}/${slug} → ${bookSlug}/${newSlug}`);
    moves.forEach(([a, b]) => plan.push(`        ${rel(a)} → ${rel(b)}`));
  }

  /* ── перекладання в інший розділ: сама лише правка JSON ── */
  if (o["to-chapter"]) {
    const [g, ch, ...more] = o["to-chapter"].split("/");
    if (!g || !ch || more.length) throw new Error("--to-chapter хоче <група>/<розділ>");
    /* `relocate` кличе `getGroup`/`getChapter`, а ті неіснуюче МОВЧКИ створюють. Тож
       одруківка в слугу заводила б порожню групу замість перекладання, і сухий прогін
       про це не казав. Заводимо нове лише тоді, коли на нього є явна назва. */
    const newGroup = !MF.groupSlugs(book).has(g);
    const newChapter = newGroup || !MF.chapterSlugs(book, g).has(ch);
    if (newGroup && !o["group-title"])
      throw new Error(`групи «${g}» у книзі «${bookSlug}» немає — якщо заводимо нову, дай --group-title "Назва"`);
    if (newChapter && !o["chapter-title"])
      throw new Error(`розділу «${ch}»${newGroup ? "" : ` в групі «${g}»`} немає — якщо заводимо новий, дай --chapter-title "Назва"`);
    if (!newGroup && o["group-title"])
      console.error(`move: увага — група «${g}» уже є, --group-title не вживається`);
    if (!newChapter && o["chapter-title"])
      console.error(`move: увага — розділ «${ch}» уже є, --chapter-title не вживається`);

    ops.push({
      op: "relocate", slug: newSlug, group: g, chapter: ch,
      groupTitle: o["group-title"], chapterTitle: o["chapter-title"],
    });
    plan.push(`розділ  ${t.group}/${t.chapter} → ${g}/${ch}   (у шляху розділу немає — рухається лише JSON)`);
    if (newGroup) plan.push(`        ⚠ група «${g}» НОВА — буде заведена з назвою «${o["group-title"]}»`);
    if (newChapter) plan.push(`        ⚠ розділ «${ch}» НОВИЙ — буде заведений з назвою «${o["chapter-title"]}»`);
  }

  /* Назву з `--to` несе сама операція `rename`, окремої не треба — але показати
     її мусимо в ОБОХ випадках: мовчки змінена назва це зміна, якої не показали. */
  if (o.title) {
    if (!o.to) ops.push({ op: "retitle", slug: newSlug, title: o.title });
    plan.push(`назва   «${t.title}» → «${o.title}»`);
  }

  /* ── лінки, ref і директиви :::code ── */
  const re = o.to ? linkRe(bookSlug, slug) : null;
  const cre = o.to ? codeRe(slug) : null;
  const refFrom = `${bookSlug}/${slug}`, refTo = `${bookSlug}/${newSlug}`;
  const edits = [];   // {path, text, links, refs, code}
  if (o.to) {
    for (const f of walk(MF.CONTENT)) {
      const ext = path.extname(f);
      if (ext !== ".md" && ext !== ".json") continue;
      let src;
      try { src = fs.readFileSync(f, "utf8"); } catch { continue; }
      let links = 0, tails = 0, refs = 0, code = 0, out = src;
      if (ext === ".md") {
        out = out.replace(re, (m, head, tail, d) => {
          links++;
          if (!tail) return head + newSlug;
          tails++;
          return `${head}${newSlug}/${newSlug}${d || ""}.md`;
        });
        /* Директиви правимо ТІЛЬКИ у прозі самої теми: шлях у них відлічується від
           теки теми, тож те саме ім'я в чужій темі означає зовсім інший файл. */
        if (path.dirname(f) === topicDir)
          out = out.replace(cre, (m, head, d) => { code++; return head + newSlug + (d || ""); });
      } else {
        /* У маніфестах міняємо лише значення `ref` — і рівно повний збіг, щоб не
           влучити в чужу тему, чий слуг починається так само. */
        out = out.replace(/"ref"\s*:\s*"([^"]+)"/g, (m, v) =>
          v === refFrom ? (refs++, m.replace(v, refTo)) : m);
      }
      if (links || refs || code) edits.push({ path: f, text: out, links, tails, refs, code });
    }
    const sum = (k) => edits.reduce((s, e) => s + e[k], 0);
    const files = (k) => edits.filter((e) => e[k]).length;
    plan.push(`лінки   ${sum("links")} у ${files("links")} файлах`);
    plan.push(`хвіст   ${sum("tails")} з них цілять у файл версії (${slug}.md / ${slug}-d.md) — ім'я в хвості теж їде`);
    plan.push(`ref     ${sum("refs")} у ${files("refs")} маніфестах`);
    plan.push(`:::code ${sum("code")} у ${files("code")} файлах теми   (шлях у директиві починається слугом)`);
  }

  console.log(plan.join("\n"));

  /* Що станеться з маніфестом, судить писар маніфесту, а не ми: ті самі операції насухо,
     і в план іде ЙОГО звіт, а не наш переказ його правил (як у status.js). */
  const dry = MF.applyOps(bookDir, ops, { dry: true });
  console.log(`маніфест ${report(dry)}`);
  dry.skipped.forEach((s) => console.log("        пропущено: " + s));
  dry.errors.forEach((e) => console.error("move: маніфест — " + e));

  if (o.to) hints(bookSlug, slug, newSlug);

  if (!o.apply) {
    console.log("\nсухий прогін — щоб зробити, додай --apply");
    return dry.errors.length ? 1 : 0;
  }

  /* ── передполіт ──────────────────────────────────────────────────────────────
     Напівзроблена робота тут найдорожча: теки перенесено, чужі файли переписано, а
     маніфест іще старий — і збирати це доводиться руками. Тож усе, що можна знати
     наперед, з'ясовуємо ДО першого запису й не починаємо взагалі. */
  const fail = [];
  if (dry.errors.length) fail.push("писар маніфесту має заперечення (вище) — маніфест не запишеться");
  for (const p of mustExist) if (!fs.existsSync(p)) fail.push(`нема на місці: ${rel(p)}`);
  for (const p of mustBeFree) if (fs.existsSync(p)) fail.push(`ціль зайнята: ${rel(p)}`);
  for (const e of edits) {
    try { fs.accessSync(e.path, fs.constants.W_OK); }
    catch { fail.push(`не пишеться: ${rel(e.path)}`); }
  }
  if (fail.length)
    throw new Error("передполіт не пройдено, НІЧОГО не зроблено:\n  " + fail.join("\n  "));

  /* ── робимо: ТЕКСТ → ФАЙЛИ → МАНІФЕСТ (чому саме так — у шапці) ── */
  let written = 0, moved = 0;
  try {
    for (const e of edits) { fs.writeFileSync(e.path, e.text, "utf8"); written++; }
    for (const [a, b] of moves) { movePath(a, b); moved++; }
  } catch (err) {
    /* Обірвалося посеред — кажемо прямо, звідки підбирати. Мовчазний виняток тут
       лишав би людину з деревом, про стан якого вона нічого не знає. */
    console.error(`move: обірвалося посеред роботи — ${err.message}`);
    console.error(`move: уже зроблено: переписано файлів ${written} з ${edits.length}, перенесено ${moved} з ${moves.length}`);
    console.error("move: МАНІФЕСТ НЕ ОНОВЛЕНО — він і далі знає стару адресу; звіряй `git status` і доробляй руками");
    return 1;
  }
  const rep = MF.applyOps(bookDir, ops);

  console.log(`\nперенесено файлів: ${moved}   переписано файлів: ${written}   маніфест: ${rep.changed}`);
  rep.skipped.forEach((s) => console.log("  пропущено: " + s));
  if (rep.errors.length) { rep.errors.forEach((x) => console.error("move: " + x)); return 1; }

  /* ── перевірка: чи не лишилося старої адреси ── */
  if (o.to) {
    let left = 0;
    for (const f of walk(MF.CONTENT)) {
      const ext = path.extname(f);
      if (ext !== ".md" && ext !== ".json") continue;
      let src = ""; try { src = fs.readFileSync(f, "utf8"); } catch { continue; }
      if (ext === ".md") {
        left += (src.match(linkRe(bookSlug, slug)) || []).length;
        /* Тема вже переїхала, тож стару адресу тут ловить не сам слуг, а ХВІСТ:
           `root:книга/dto-new/dto.md` — тема нова, файл давно зветься інакше. */
        left += (src.match(tailRe(bookSlug, newSlug, slug)) || []).length;
      } else left += (src.match(new RegExp(`"ref"\\s*:\\s*"${esc(refFrom)}"`, "g")) || []).length;
    }
    /* Директиви судимо в НОВІЙ теці теми, а не по корпусу: шлях у них локальний, і
       старе ім'я в чужій темі — то її власний файл, а не наш недогляд. */
    const newDir = path.join(bookDir, newSlug);
    let ents = []; try { ents = fs.readdirSync(newDir); } catch { }
    for (const f of ents) {
      if (!f.endsWith(".md")) continue;
      let src = ""; try { src = fs.readFileSync(path.join(newDir, f), "utf8"); } catch { continue; }
      left += (src.match(codeRe(slug)) || []).length;
    }
    console.log(left ? `⚠ старої адреси лишилося: ${left} — подивись руками` : "старої адреси не лишилося");
    return left ? 1 : 0;
  }
  return 0;
}

if (require.main === module) {
  try { process.exit(main(process.argv.slice(2))); }
  catch (e) { console.error("move: " + e.message); process.exit(2); }
}
module.exports = { main };
