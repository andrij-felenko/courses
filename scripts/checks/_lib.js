#!/usr/bin/env node
/* ============================================================================
   _lib.js — спільне ядро конвеєра перевірок Antigravity.

   ТРИ КОДИ ВИХОДУ, однакові для всіх перевірок:
     0 — ПРОЙДЕНО: чисто, або кожен пункт має чинний вирок «ok», або перевірка
         не застосовна до цієї теки (нема чого перевіряти — теж пройдено).
     1 — ДЕФЕКТИ: правити текст. Вирок дав скрипт або агент («defect»).
     2 — ПОТРІБЕН ВИРОК: скрипт витяг пункти, на які ще нема вироку агента.
     3 — ужиток (погані аргументи). Не стан теми.

   ЧОМУ ЦИКЛ СКІНЧЕННИЙ. Пункт на вирок ідентифікується ХЕШЕМ СВОГО ТЕКСТУ,
   а текст пункту виведено з самої статті. Тому:
     • дав вирок «ok» → пункт закрито, поки текст не змінився;
     • дав вирок «defect» → перевірка тримає код 1, доки текст не змінять;
     • текст змінили → пункт зник або став іншим → вирок сам протух, і його
       питають наново.
   Отже стан «усі 12 дають 0» досяжний і стійкий: він означає, що КОЖЕН пункт
   у ПОТОЧНОМУ тексті або чистий, або має вирок із доказом.

   Вироки лежать поза текою книги: scripts/_finish/_verdicts/<тека>/<NN>.json
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { execSync } = require("child_process");

/* Корінь репо беремо від САМОГО скрипта, а не від cwd: агент може запустити команду
   з іншої теки, і тоді відносні шляхи (scripts/textcheck.js, book/…) мовчки розсипались би. */
const ROOT = path.resolve(__dirname, "..", "..");
const PASS = 0, DEFECT = 1, JUDGE = 2, USAGE = 3;

/* Теку теми приймаємо і абсолютну, і відносну — від cwd або від кореня репо. */
function resolveDir(arg) {
  if (!arg) return null;
  const tries = path.isAbsolute(arg) ? [arg] : [path.resolve(process.cwd(), arg), path.resolve(ROOT, arg)];
  for (const p of tries) if (fs.existsSync(p) && fs.statSync(p).isDirectory()) return p;
  return null;
}

/* Інтерпретатор Python: на Windows це часто `py`, а не `python`. Не знайшли — кажемо прямо,
   а не видаємо мовчазне «svgcheck дав зауваження» на порожньому місці. */
let PY = null;
function python() {
  if (PY !== null) return PY;
  for (const c of ["python", "py -3", "python3"]) {
    try { execSync(`${c} -c "pass"`, { stdio: "ignore" }); PY = c; return PY; } catch { }
  }
  PY = "";
  return PY;
}

/* ── §3 + надбавка Antigravity ───────────────────────────────────────────────
   Канон §3 — спільний. Смуги конвеєра підняті рівно на SCALE (дефолт 1.30).
   Підняті ОБИДВА краї: нижній — щоб недописування ловилось, верхній — щоб
   глибина не билася в стелю.
   Правило «базова ≤ ½ детальної» — відношення, від масштабу не залежить.

   ЧОМУ 1.30, І ЧОМУ ЦЕ НЕ ПОВЕРНЕННЯ ДО 1.35. Надбавку тримали на 35%, поки не
   з'ясувалось, куди йшли ті відсотки: не в глибину, а в переказ власних вставок —
   стаття вдруге розповідала те, що вже стоїть у її ж hist- і proj-. Тоді її зрізали
   до 15% і водночас заборонили дубль прямо в промпті автора (§2 write-topic).
   Заборона лишається чинною. А запас на глибину повернено до 30% тепер, коли коло
   суду коштує в рази менше: один суддя на тему замість шести, стеля два кола.
   Тобто платимо за довшу статтю, а не за шість читань тієї самої.               */
const SCALE = Number(process.env.CHECKS_SCALE || 1.30);
/* Надбавка НЕ однакова на всі види файлів — бо різні види впираються в різне.
   detailed 1.40: головна робота теми, і саме їй бракує місця, коли механізм треба
     показати ланка за ланкою, а не «і тому отримуємо».
   api 1.60: у неї найнижчий канонний орієнтир з усіх вставок (1000–2000), а §3 прямо
     називає довідку інтерфейсу тим випадком, де великий неподільний перелік виправданий:
     призначення, параметри, повертані значення, коди помилок, інваріанти, приклад виклику —
     це або є повністю, або довідка не працює. Ділити її на частини шкідливо.
   Решта видів лишається на загальному SCALE.                                        */
const KIND_SCALE = { detailed: 1.40, api: 1.60 };
const scaleOf = (kind) => KIND_SCALE[kind] || SCALE;
const r50 = (x) => Math.round(x / 50) * 50;

const CANON = {
  basic:    { lo: 500,  hi: 1200, max: 1200 },
  detailed: { lo: 1000, hi: 6500, max: 9000 },
};

/* ── СМУГИ ВСТАВОК — задані ПРЯМО, без множника ────────────────────────────────
   Раніше всі п'ять типів жили на спільній смузі 400–5000 × SCALE — спадщина
   часів, коли їх вважали одним класом. Вони не один клас:

     hist  500–4000   історія має що розповісти, але не безмежно;
     math  600–4000   виведення довше за історію, але теж скінченне;
     comp  600–5000   порівняння росте з числом сторін, тому стеля вища;
     api   800–7000   неподільна поверхня чужого стандарту буває дуже великою;
     proj  800–7000   практика з розбором — найбільший тип.

   ЧИСЛА ТУТ ПРО ПРОЗУ, НЕ ПРО ФАЙЛ. proseWords не рахує нічого між огорожами
   коду, тож код у ці смуги не входить і не може «дописати» вставку замість
   тексту. Для proj і api код міряється ОКРЕМО (CODE_FLOOR): вставка цих двох
   типів без коду не виконує того, заради чого її винесли, хоч би скільки прози
   в ній було.

   Виняткова стеля — півтори смуги: понад неї матеріал ділять, а не пишуть.     */
const INSERT_BANDS = {
  hist: { lo: 600, hi: 6000 },
  math: { lo: 600, hi: 6500 },
  comp: { lo: 800, hi: 7500 },
  api:  { lo: 1100, hi: 11000 },
  proj: { lo: 800, hi: 6000 },
};

/* ── СХОДИНКИ РІВНІВ У ВСТАВКАХ — НАРОСТАЮЧІ ──────────────────────────────────
   У статей крок рівний: смуга ділиться на п'ять однакових зон. Для вставок так не
   годиться. Вставка Р1 — дотична, її пишуть кількома абзацами; Р5 — те, заради чого
   тему писали. Рівний крок робить перехід Р1→Р2 таким самим коштовним, як Р4→Р5, і
   тим душить дешевий низ: дотичній вставці нічого сказати на пів тисячі слів понад
   мінімум, і вона доливає води саме там, де води найпомітніше.

   Тому крок росте. Р5 стоїть на ПОЛОВИНІ максимуму — верхня половина смуги лишається
   вільним місцем для теми, яка справді того варта, — а Р1..Р5 розкладені геометрично:

       підлога(вид, рівень) = lo × (Р5 / lo) ^ ((рівень − 1) / 4),   Р5 = hi / 2

   Відношення між сусідніми рівнями стале (≈1.4–1.5), тобто кожен наступний рівень —
   «у півтора раза глибший», а абсолютний крок природно росте: у proj це 300 · 450 ·
   600 · 850 слів. Верх смуги (від Р5 до hi) — та сама однобокість, що й раніше:
   переріс свій рівень і лишився під стелею означає, що рівень недооцінили.          */
const insertFloor = (lo, hi, lv) => r50(lo * Math.pow((hi / 2) / lo, (lv - 1) / 4));

/* ── КОД ЖИВЕ У ФАЙЛАХ, А НЕ В ОГОРОЖАХ ───────────────────────────────────────
   Блок від EXTRACT_MIN рядків виїжджає з прози у файл. Тека названа тим .md,
   у який код вставляють, — саме тому дві кодоносні вставки однієї теми не
   стикаються (а таких тем 56%: proj і api поруч майже завжди):

       <тема>/<ім'я .md без розширення>/<мова>/<файли>

       i2c-expander/i2c-expander-d/c/main.c            детальна стаття
       i2c-expander/proj-interrupt-driver/c/main.c     вставка
       i2c-expander/proj-interrupt-driver/cpp/Ring.hpp

   Тека мови — КОРІНЬ ПРОЄКТУ: усередині діє звичайна для мови розкладка,
   з підтеками включно (rust/src/, go/internal/, пакет у Python). Розбивати
   так, як розбивають у справжніх проєктах; спірно — розбивати.

   Побічний виграш: .h перестав бути безрідним. У пласкій теці його не віднести
   ні до C, ні до C++, і перевірка пари на цьому спотикалася. Тепер мову вирішує
   тека, а спільний заголовок на дві мови став неможливим — отже, неможлива й
   підробка «C++ версії», де той самий .h підключено з .cpp.                    */
const EXTRACT_MIN = 10;

/* Дві драбини підлог, бо однакову роботу різні мови пишуть різною кількістю
   рядків. Обидві починаються з EXTRACT_MIN — з порога винесення: є код, значить
   є файл, а далі рівень тягне вгору.

   Числа тут САНІТАРНІ, не цільові. Повноту забезпечує не лічильник, а бриф:
   письменникові дають прозу, preknowlist і контекст і кажуть реалізувати це
   в коді до кінця. Підлога ловить лише огризок. Тому й порада при недоборі —
   розширити код, у крайньому разі дописати коментарі: коментарі та порожні
   рядки рахуються, бо коментар у коді теж пояснення.                          */
const CODE_FLOOR = {
  low:  [10, 60, 120, 180, 320],   /* C, C++, Go, Java, Rust, asm — багатослівні */
  high: [10, 40,  80, 150, 250],   /* Python, JS, TS, Lua, Ruby — щільні         */
};
const NEEDS_CODE = new Set(["proj", "api"]);

/* мітка огорожі → тека мови + смуга. tier glue — скрипти: файл дістають
   (від EXTRACT_MIN), але підлоги не мають, бо їхній розмір нічого не каже. */
const LANGS = {
  c: ["c", "low"], h: ["c", "low"],
  /* Платформа — це не мова. esp-idf і stm32 пишуться на C, arduino в цьому корпусі
     теж написано C-стилем (формально .ino це C++, але вкладкою він стоїть поруч із
     двома C, як «те саме в іншому середовищі»). Тому вони лягають ПІД мову зайвим
     рівнем: <мова>/<платформа>/. Тека мови лишається чесною, перевірка пари c/↔cpp/
     не плутається, а розрізнення середовищ не губиться.                            */
  arduino: ["c", "low", "arduino"], "esp-idf": ["c", "low", "esp-idf"], stm32: ["c", "low", "stm32"],
  cpp: ["cpp", "low"], "c++": ["cpp", "low"], hpp: ["cpp", "low"],
  rust: ["rust", "low"], go: ["go", "low"], java: ["java", "low"], cs: ["cs", "low"],
  swift: ["swift", "low"], kotlin: ["kotlin", "low"],
  asm: ["asm", "low"], nasm: ["asm", "low"], verilog: ["verilog", "low"], vhdl: ["vhdl", "low"],
  python: ["py", "high"], py: ["py", "high"], micropython: ["py", "high", "micropython"],
  ts: ["ts", "high"], typescript: ["ts", "high"], js: ["js", "high"], javascript: ["js", "high"],
  ruby: ["ruby", "high"], rb: ["ruby", "high"], lua: ["lua", "high"], perl: ["perl", "high"],
  php: ["php", "high"], r: ["r", "high"], matlab: ["matlab", "high"], dart: ["dart", "high"],
  sh: ["sh", "glue"], bash: ["sh", "glue"], zsh: ["sh", "glue"],
  sql: ["sql", "glue"], cmake: ["cmake", "glue"], make: ["make", "glue"], makefile: ["make", "glue"],
};
const DIR_TIER = (() => { const m = {}; for (const v of Object.values(LANGS)) m[v[0]] = v[1]; return m; })();

/* Не код проєкту: файли збірки й обв'язки. Відбираємо за ІМЕНЕМ, а не за
   розширенням — інакше setup.py, conanfile.py і noxfile.py пролізли б у ліміт
   Python як звичайні модулі.                                                  */
const BUILD_FILES = new Set([
  "cmakelists.txt", "makefile", "gnumakefile", "meson.build", "build.ninja", "kconfig", "sdkconfig",
  "setup.py", "setup.cfg", "conanfile.py", "noxfile.py", "fabfile.py", "tasks.py",
  "pyproject.toml", "requirements.txt", "package.json", "package-lock.json", "tsconfig.json",
  "cargo.toml", "cargo.lock", "go.mod", "go.sum", "dockerfile", "build.gradle", "pom.xml",
  "platformio.ini", "readme.md", ".gitignore", ".clang-format", ".editorconfig",
]);
const BUILD_EXT = new Set([".cmake", ".mk", ".toml", ".json", ".yaml", ".yml", ".ini", ".cfg", ".lock", ".md", ".txt"]);

/* Тести з ліміту виключено: тест не має задавати розмір проєкту. Чи покривають
   вони заявлене — судиться змістом, а не рядками.                              */
const TEST_RE = /(^|[\\/])(tests?|spec)([\\/]|$)|(^|[_.-])(test|spec)[_.-]|[_.-](test|spec)\.|^test_/i;

/* ── РІВЕНЬ РОЗКРИТТЯ (1–5) — підлога, не ціль ────────────────────────────────
   Колонка «орієнтир» звідси прибрана двічі й обидва рази з тієї самої причини:
   письменник пише на будь-яке число, яке йому показали. Поки орієнтир стояв,
   детальні вирівнювалися по ньому (заміряно 2026-08-28: медіана 2970 при орієнтирі
   2950, міжквартильний розкид 300 слів на смузі 7700 — довжину задавала таблиця,
   а не предмет). Коли орієнтир прибрали, письмо сповзло на нижній край смуги —
   `proj-` дали медіану 737 при підлозі 650, 55% у першій десятині смуги.

   Тобто число неминуче стає ціллю. Висновок не «прибрати число», а «зробити число
   властивістю ТЕМИ, а не таблиці»: рівень ставить окрема фаза оцінки ПЕРЕД письмом,
   і він у кожної теми свій.

   Механіка навмисно однобока. Смуга виду ділиться на п'ять зон, рівень підіймає
   НИЖНІЙ край на початок своєї зони; верхній край і виняткова стеля лишаються
   спільними для всіх рівнів:

       підлога(вид, рівень) = lo + (рівень − 1) × (hi − lo) / 5

   Верхньої межі рівень не має свідомо. Двостороннє вікно навколо цілі зіштовхнулось
   би з залізним «скорочувати текст заради гейта заборонено»: письменник, у якого тема
   переросла оцінку, опинився б між двома правилами без виходу. Однобока підлога цього
   не робить — переріс свій рівень і лишився під стелею виду означає рівно те, що рівень
   недооцінили, а текст правильний. Тому Р3, яка вийшла на обсяг Р5, дефекту не дає;
   дефект дає Р5, яка вийшла на обсяг Р1.

   Ціна помилки в оцінці лягає на 06-ту: занижений рівень вона судить не лічильником,
   а читанням («рівень ↔ зміст»), бо це єдине місце, де заниження можна впіймати.       */
const SPLIT_NL = new RegExp("\r?\n");
const FENCE = new RegExp("^\s*" + "```");
const LEVELS = 5;
const LEVEL_NAMES = {
  1: "дотична — читач її мине без утрати",
  2: "звичайна — своє місце в розділі, без опор на неї",
  3: "робоча — на неї спираються сусідні теми",
  4: "несуча — без неї розділ не читається",
  5: "наріжна — книга стоїть на ній",
};
const clampLevel = (v) => {
  const n = Math.round(Number(v));
  return Number.isFinite(n) && n >= 1 && n <= LEVELS ? n : null;
};
/* Пороги ГЕЙТА БАЗОВОЇ (§3, ознака 1) — теж × SCALE, і це не сваволя:
   канонні 2250 виведені з самої стелі базової (1200 × 2 ≈ 2400, з допуском 2250), а поріг
   4000 — місце, де тема виросла настільки, що швидкий огляд їй потрібен. Пишучи на 30%
   більше про той самий матеріал, конвеєр зсуває обидві точки на ті самі 30% — інакше
   кожна його стаття автоматично опинялась би в зоні «базова потрібна».                    */
const BASIC_GATE = { low: r50(2250 * scaleOf("detailed")), high: r50(4000 * scaleOf("detailed")) };

/* Смуга виду, з підлогою, піднятою на зону рівня. Рівень не заданий (basic, або
   оцінки ще немає) — підлога лишається нижнім краєм смуги, тобто рівнем 1.       */
function bandOf(kind, level) {
  const ins = INSERT_BANDS[kind];
  let lo, hi, max, soft, k = 1, c = null;
  /* Вставка: hi — це вже МАКСИМУМ (понад нього тему ділять), Р5 стоїть на його
     половині. Зона винятку («чи справді неподільна?») — верхня чверть смуги.      */
  if (ins) { lo = ins.lo; hi = ins.hi; max = hi; soft = r50((hi / 2) * 1.5); }
  else { c = CANON[kind] || CANON.detailed; k = scaleOf(kind);
         lo = r50(c.lo * k); hi = r50(c.hi * k); max = r50(c.max * k); soft = hi; }
  const lv = clampLevel(level);
  const fl = ins
    ? (lv ? insertFloor(lo, hi, lv) : lo)
    : (lv ? r50(lo + ((lv - 1) * (hi - lo)) / LEVELS) : lo);
  return {
    lo, hi, max, soft, scale: k, canon: c,
    level: lv,
    /* «зона» для вироку «на N зон вище свого рівня»: у вставок крок нерівний,
        тож беремо середній — він і так лише для грубої ознаки роздування.   */
    zone: ins ? r50(((hi / 2) - lo) / 4) : r50((hi - lo) / LEVELS),
    floor: fl,
    needsCode: NEEDS_CODE.has(kind),
    codeFloor: NEEDS_CODE.has(kind) ? CODE_FLOOR.low[(lv || 1) - 1] : 0,
  };
}

/* Рядки коду: усе між огорожами, разом із порожніми й коментарями. */
function codeLines(md) {
  let inCode = false, n = 0;
  for (const line of md.split(SPLIT_NL)) {
    if (FENCE.test(line)) { inCode = !inCode; continue; }
    if (inCode) n++;
  }
  return n;
}

/* Тека проєкту конкретного .md: <тека теми>/<ім'я без .md>/ */
function projectDir(topicDir, mdFile) { return path.join(topicDir, path.basename(mdFile, ".md")); }

/* Мовні теки, що СПРАВДІ лежать на диску для цього .md. */
function langDirsOf(topicDir, mdFile) {
  const root = projectDir(topicDir, mdFile);
  let ents = [];
  try { ents = fs.readdirSync(root, { withFileTypes: true }); } catch { return []; }
  const out = [];
  for (const e of ents) {
    if (!e.isDirectory()) continue;
    const tier = DIR_TIER[e.name];
    if (!tier) continue;
    out.push({ lang: e.name, tier, dir: path.join(root, e.name) });
  }
  return out.sort((a, b) => a.lang.localeCompare(b.lang));
}

/* Рядки коду в теці мови: усе, крім файлів збірки й тестів. Порожні рядки
   й коментарі рахуються — див. коментар при CODE_FLOOR.                  */
function codeLinesOfDir(dir) {
  let lines = 0, files = 0, tests = 0, build = 0;
  const walk = (d, rel) => {
    let ents = [];
    try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const e of ents) {
      const p = path.join(d, e.name);
      const r = rel ? rel + "/" + e.name : e.name;
      if (e.isDirectory()) { walk(p, r); continue; }
      const low = e.name.toLowerCase();
      if (BUILD_FILES.has(low) || BUILD_EXT.has(path.extname(low))) { build++; continue; }
      if (TEST_RE.test(r)) { tests++; continue; }
      const t = read(p);
      if (!t.trim()) continue;
      files++;
      lines += t.replace(/\r\n?/g, "\n").replace(/\n+$/, "").split("\n").length;
    }
  };
  walk(dir, "");
  return { lines, files, tests, build };
}

/* Підлога коду для смуги мови на рівні. Скрипти підлоги не мають. */
function codeFloorFor(tier, level) {
  if (tier !== "low" && tier !== "high") return 0;
  return CODE_FLOOR[tier][(clampLevel(level) || 1) - 1];
}

/* Прапорець recode у маніфесті: код перенесено механічно і ще не переписано як
   справжній проєкт. Поки він стоїть, розмір коду МІРЯЄТЬСЯ, але дефекту не дає —
   інакше наступного дня після переїзду червоним засвітилося б 7484 файли, і гейт
   перестав би щось означати. Знімає прапорець той, хто перепише проєкт.

   Antigravity ставить recode ЗАВЖДИ, коли пише код: у Claude код виходить кращий,
   тож усе, написане іншим конвеєром, за означенням чекає на переписування.       */
function recodeOf(dir, file) {
  const M = manifestOf(dir);
  const t = M && M.topic;
  if (!t) return false;
  const slug = path.basename(path.resolve(dir));
  if (file === slug + ".md") return !!(t.basic && t.basic.recode);
  if (file === slug + "-d.md") return !!(t.detailed && t.detailed.recode);
  for (const ty of INSERT_TYPES) for (const i of t[ty] || []) if (i.file === file) return !!i.recode;
  return false;
}

/* ── звідки береться рівень ───────────────────────────────────────────────────
   З БАТЧ-ФАЙЛА, а не з теки теми. Фаза оцінки на старті батчу проходить списком
   тем і кладе кожній `level` туди ж, де лежить сам список:

       scripts/_finish/_batch-<книга>.json   (письмо)
       scripts/_finish/_update-<книга>.json  (дописування)
       [ { "dir": "root/<вид>/<книга>/<тема>", "level": 3,
           "inserts": { "proj-scheduler.md": 2 } }, … ]

   Окремого файлу в теці теми немає навмисно: рівень — це параметр ПРОГОНУ, а не
   властивість статті на диску. Корпус від нього не залежить: не буде батч-файла —
   06-та просто скаже, що фаза оцінки не відпрацювала.

   `inserts` наповнюється по ходу: вставки до письма не існує, її рівень оголошує
   письменник у звіті, а оркестратор дописує сюди перед гейтом.

   Базова рівня НЕ має: її обсяг задає не важливість теми, а залізо §3 «≤ ½
   детальної», і другий важіль тут лише сперечався б із першим.                    */
const BATCHDIR = path.join(ROOT, "scripts", "_finish");
let _levelIndex = null;
function levelIndex() {
  if (_levelIndex) return _levelIndex;
  _levelIndex = new Map();
  let files = [];
  try { files = fs.readdirSync(BATCHDIR).filter((f) => /^_(batch|update)-.*\.json$/.test(f)); } catch { }
  for (const f of files) {
    let j; try { j = JSON.parse(fs.readFileSync(path.join(BATCHDIR, f), "utf8")); } catch { continue; }
    const list = Array.isArray(j) ? j : (j.topics || j.units || []);
    for (const x of list) {
      if (!x || typeof x !== "object" || !x.dir) continue;
      const key = path.resolve(ROOT, x.dir);
      const topic = clampLevel(x.level);
      /* Та сама тема трапляється в кількох батч-файлах (старі прогони нікуди не діваються).
         Запис БЕЗ рівня не затирає запис із рівнем: інакше давній список тем, де рівнів ще
         не було, гасив би оцінку поточного прогону, і тема падала б «рівень не оголошено». */
      const had = _levelIndex.get(key);
      if (had && had.topic && !topic) continue;
      const inserts = { ...(had && had.topic === topic ? had.inserts : {}) };
      for (const [k, v] of Object.entries(x.inserts || {})) inserts[k] = clampLevel(v);
      _levelIndex.set(key, { topic, inserts, from: f });
    }
  }
  return _levelIndex;
}
function readLevel(dir) { return levelIndex().get(path.resolve(dir)) || null; }

/* Рівень конкретного файлу теми: детальна бере рівень теми, вставка — свій,
   базова не має жодного. `undefined` означає «мало бути, але не оголошено». */
function levelFor(lv, item) {
  if (!lv || item.kind === "basic" || item.kind === "other") return null;
  if (item.kind === "detailed") return lv.topic;
  return Object.prototype.hasOwnProperty.call(lv.inserts, item.file) ? lv.inserts[item.file] : undefined;
}

/* ── класифікація файлів теми ─────────────────────────────────────────────── */
const INSERT_TYPES = ["hist", "comp", "math", "proj", "api"];
function classify(file, slug) {
  const base = path.basename(file, ".md");
  if (base === slug) return "basic";
  if (base === slug + "-d") return "detailed";
  const m = base.match(/^(hist|comp|math|proj|api)-/);
  if (m) return m[1];
  return "other";
}
const KIND_LABEL = {
  basic: "базова стаття", detailed: "детальна стаття",
  hist: "вставка hist (історія)", comp: "вставка comp (порівняння)",
  math: "вставка math (виведення)", proj: "вставка proj (практика)",
  api: "вставка api (поверхня)", other: "інше",
};

/* ── читання теми ─────────────────────────────────────────────────────────── */
function readTopic(dir) {
  const slug = path.basename(dir);
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".md")).sort();
  const items = files.map((f) => {
    const p = path.join(dir, f);
    const kind = classify(f, slug);
    return { file: f, path: p, kind, label: KIND_LABEL[kind], text: read(p) };
  });
  return {
    dir, slug, files: items,
    basic: items.find((i) => i.kind === "basic") || null,
    detailed: items.find((i) => i.kind === "detailed") || null,
    inserts: items.filter((i) => INSERT_TYPES.includes(i.kind)),
    prose: items.filter((i) => i.kind === "basic" || i.kind === "detailed"),
    imgDir: path.join(dir, "img"),
  };
}
function read(f) { try { return fs.readFileSync(f, "utf8"); } catch { return ""; } }

/* ── маскування: код-блоки, інлайн-код, URL, цілі лінків ──────────────────── */
function strip(s) {
  return s
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`[^`]*`/g, " ")
    .replace(/\]\([^)]*\)/g, "]")
    .replace(/https?:\/\/\S+/g, " ");
}
function codeBlocks(s) {
  const out = [];
  const re = /```([^\n]*)\n([\s\S]*?)```/g;
  let m, i = 0;
  while ((m = re.exec(s))) out.push({ n: ++i, lang: m[1].trim(), body: m[2] });
  return out;
}
/* проза за §3 — рахує так само, як scripts/wordcount.js (тримати синхронно) */
function proseWords(md) {
  let inCode = false, words = 0;
  for (let line of md.split(/\r?\n/)) {
    const t = line.trim();
    if (/^```/.test(t)) { inCode = !inCode; continue; }
    if (inCode) continue;
    /* Директиви (:::code, :::tabs, :::) — не проза. Раніше код лежав в огорожах і
       відсікався сам; тепер на його місці стоїть посилання, і без цього рядка
       28 104 директиви корпусу дали б близько 120 тисяч фантомних слів — рівно
       в тих файлах, де коду найбільше.                                          */
    if (/^:::/.test(t)) continue;
    if (/^!\[/.test(t)) continue;
    if (/^#{1,6}\s/.test(t)) line = t.replace(/^#{1,6}\s/, "");
    if (/^\|.*\|/.test(t)) continue;
    const s = line
      .replace(/`[^`]*`/g, " ")
      .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
      .replace(/\[[^\]]*\]\([^)]*\)/g, (x) => x.replace(/\]\([^)]*\)/, "").replace(/^\[/, ""))
      .replace(/^>\s*/, "").replace(/^[-*]\s+/, "").replace(/[*_#>`~]/g, " ");
    const m = s.match(/[\p{L}\p{N}’'\-]+/gu);
    if (m) words += m.length;
  }
  return words;
}

/* ── маніфест книги, до якої належить тема ────────────────────────────────────
   ДВА ДЕРЕВА, і поки триває перенос — обидва живі:

     v7  root/<вид>/<книга>/<тема>          маніфест: root/<вид>/<книга>/manifest.json
                                            (шапка + окремий <група>.json на кожну групу)
     v6  <вид>/<книга>/<секція>/<слуг>      маніфест: <вид>/<книга>/manifest.js

   У v7 тема лежить ПЛАСКО під книгою — секції в шляху немає, вона тільки в маніфесті.
   Розбір v7 живе в scripts/lib/manifest7.js: один розбір на весь тулінг, щоб не
   повторилася історія v6, де чотири скрипти читали схему кожен по-своєму.          */
function manifestOf(dir) {
  const M7 = require("../lib/manifest7.js");
  if (M7.isV7(dir)) {
    const bookDir = M7.bookDirOfTopic(dir);
    if (!bookDir) return null;
    const b = M7.loadBook(bookDir);
    if (!b) return null;
    const slug = path.basename(path.resolve(dir));
    const topics = M7.allTopics(b).filter((t) => t.own).map((t) => t.node);
    return {
      path: b.mfPath,
      kind: b.manifest.kind || path.basename(path.dirname(bookDir)),
      book: b.manifest.slug || path.basename(bookDir),
      isGuide: (b.manifest.kind || "") === "course",
      all: topics,
      topic: topics.find((t) => t.slug === slug) || null,
    };
  }

  const rel = path.relative(ROOT, path.resolve(dir)).split(/[\\/]/);
  if (rel.length < 3) return null;
  const [kind, book] = rel;
  const mfPath = path.join(ROOT, kind, book, "manifest.js");
  if (!fs.existsSync(mfPath)) return null;
  let m, isGuide = false;
  try {
    /* масиви засіваємо самі: маніфест починається з `window.__BOOKS__ = window.__BOOKS__ || []`,
       але покладатися на це не варто — без засіву падає весь розбір і тема виглядає «без маніфесту» */
    const sb = { __BOOKS__: [], __GUIDES__: [] };
    new Function("window", fs.readFileSync(mfPath, "utf8"))(sb);
    isGuide = Array.isArray(sb.__GUIDES__) && sb.__GUIDES__.length;
    m = (isGuide ? sb.__GUIDES__ : sb.__BOOKS__ || [])[0];
  } catch { return null; }
  if (!m) return null;

  const topics = [];
  if (isGuide) {
    (m.modules || []).forEach((mod) => (mod.chapters || [{ steps: mod.steps || [] }]).forEach(
      (ch) => (ch.steps || []).forEach((s) => { if (s.slug) topics.push(s); })));
    (m.sections || []).forEach((s) => (s.topics || []).forEach((t) => topics.push(t)));
  } else {
    (m.sections || []).forEach((s) => (s.topics || []).forEach((t) => topics.push(t)));
  }
  const slug = path.basename(path.resolve(dir));
  return { path: mfPath, kind, book, isGuide, all: topics, topic: topics.find((t) => t.slug === slug) || null };
}

/* Черга нових тем Antigravity — теми, які ще не в маніфесті, але вже вирішено завести.
   Лінк на таку тему битим НЕ вважається: її зареєструє finish-batch наприкінці батчу.

   Читаємо ЧЕРГИ ВСІХ КНИГ, а не лише своєї. Поняття з чужої галузі заводять у ту книгу,
   якій воно належить (стаття з фізики → тема в math), і лінк на неї стоїть одразу. Поки
   тут дивилися лише свою чергу, такий лінк оголошувався битим — тобто правило «заводь у
   сусідню книгу» каралося перевіркою 05, і автор мусив або прибрати лінк, або відмовитись
   від теми. Слуги в корпусі унікальні, тож плаский список безпечний. */
function queuedTopics(dir) {
  const qdir = path.join(ROOT, "scripts", "_finish");
  let files = [];
  try { files = fs.readdirSync(qdir).filter((f) => /^_ag-newtopics-.+\.json$/.test(f)); } catch { return []; }
  const out = [];
  for (const f of files) {
    try {
      JSON.parse(fs.readFileSync(path.join(qdir, f), "utf8"))
        .filter((t) => !t.applied).forEach((t) => out.push(t.slug));
    } catch { }
  }
  return out;
}

/* ── зовнішні команди ─────────────────────────────────────────────────────── */
function run(cmd) {
  try { return { out: execSync(cmd, { cwd: ROOT, maxBuffer: 64 * 1024 * 1024 }).toString(), code: 0 }; }
  catch (e) { return { out: ((e.stdout || "") + (e.stderr || "")).toString(), code: e.status || 1 }; }
}

/* ── сховище вироків ──────────────────────────────────────────────────────── */
const VDIR = path.join(ROOT, "scripts", "_finish", "_verdicts");
const norm = (s) => s.replace(/\s+/g, " ").trim();
const keyOf = (file, item) => crypto.createHash("sha1").update(file + "|" + norm(item)).digest("hex").slice(0, 12);
function topicKey(dir) { return path.relative(ROOT, path.resolve(dir)).replace(/[\\/]/g, "__"); }
function verdictPath(dir, check) { return path.join(VDIR, topicKey(dir), check + ".json"); }
function itemsPath(dir, check) { return path.join(VDIR, topicKey(dir), check + ".items.json"); }
function loadVerdicts(dir, check) {
  try { return JSON.parse(fs.readFileSync(verdictPath(dir, check), "utf8")); } catch { return {}; }
}
function saveVerdicts(dir, check, data) {
  const p = verdictPath(dir, check);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(data, null, 2), "utf8");
}
function saveItems(dir, check, items) {
  const p = itemsPath(dir, check);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(items, null, 2), "utf8");
}
function loadItems(dir, check) {
  try { return JSON.parse(fs.readFileSync(itemsPath(dir, check), "utf8")); } catch { return []; }
}

/* ── єдиний вивід і вихід ─────────────────────────────────────────────────── */
let CHECK_NO = "00", CHECK_TITLE = "";
function head(no, title, dir) {
  CHECK_NO = no; CHECK_TITLE = title;
  console.log(`\n=== ПЕРЕВІРКА ${no}: ${title} ===`);
  console.log(`тека: ${dir}`);
}

/* ПРОЙДЕНО без питань (нема матеріалу / все чисто) */
function pass(note) {
  console.log("\nРЕЗУЛЬТАТ: ПРОЙДЕНО" + (note ? "  — " + note : ""));
  process.exit(PASS);
}

/* Механічні дефекти: вирок дав скрипт, вироку агента не треба. */
function defects(list, hint) {
  console.log("");
  if (!list.length) return pass();
  console.log(`РЕЗУЛЬТАТ: ДЕФЕКТІВ ${list.length}` + (hint ? `  (${hint})` : ""));
  list.forEach((b, i) => console.log(`  ${i + 1}. ${b}`));
  console.log("\nВиправ перелічене й прожени цю саму команду знову.");
  process.exit(DEFECT);
}

/* Пункти на вирок агента. items: [{file, text, ask?}]
   Кожен пункт зіставляється з чинним вироком за хешем свого тексту.       */
function adjudicate(dir, items, ask) {
  const V = loadVerdicts(dir, CHECK_NO);
  const enriched = items.map((it, i) => {
    const key = keyOf(it.file, it.text);
    const v = V[key];
    return { n: i + 1, key, file: it.file, kind: it.kind || "", text: norm(it.text), verdict: v || null };
  });
  saveItems(dir, CHECK_NO, enriched);

  const open = enriched.filter((e) => !e.verdict);
  const bad = enriched.filter((e) => e.verdict && e.verdict.status === "defect");
  const ok = enriched.filter((e) => e.verdict && e.verdict.status === "ok");

  console.log(`\nпунктів: ${enriched.length} · з вироком «ok»: ${ok.length} · визнано дефектом: ${bad.length} · без вироку: ${open.length}`);

  if (bad.length) {
    console.log(`\n--- ВИЗНАНО ДЕФЕКТОМ (правити текст) ---`);
    bad.forEach((e) => {
      console.log(`  [${e.n}] ${e.file}${e.kind ? " (" + KIND_LABEL[e.kind] + ")" : ""}: ${e.text.slice(0, 200)}`);
      console.log(`       вирок: ${e.verdict.proof}`);
    });
    console.log(`\nРЕЗУЛЬТАТ: ДЕФЕКТІВ ${bad.length} — переписати має АВТОР, не перевіряльник.`);
    console.log(`Після правки текст пункту зміниться, і вирок протухне сам — прожени перевірку знову.`);
    process.exit(DEFECT);
  }
  if (!open.length) pass(`усі ${enriched.length} пунктів мають вирок «ok» із доказом`);

  console.log(`\n--- ПУНКТИ БЕЗ ВИРОКУ ---`);
  open.forEach((e) => {
    console.log(`  [${e.n}] ${e.file}${e.kind ? " (" + KIND_LABEL[e.kind] + ")" : ""}: ${e.text.slice(0, 260)}`);
  });
  console.log(`\nЩО ЗРОБИТИ: ${ask}`);
  console.log(`На КОЖЕН пункт запиши вирок із доказом:`);
  console.log(`  node scripts/checks/verdict.js ${CHECK_NO} "${dir}" --item <N> --status ok|defect --proof "<чим доведено>"`);
  console.log(`Без доказу вирок не приймається. Не вгадуй — перевіряй.`);
  process.exit(JUDGE);
}

module.exports = {
  PASS, DEFECT, JUDGE, USAGE, ROOT, SCALE, INSERT_TYPES, KIND_LABEL, BASIC_GATE,
  LEVELS, LEVEL_NAMES, clampLevel, readLevel, levelFor, codeLines, CODE_FLOOR, NEEDS_CODE,
  EXTRACT_MIN, LANGS, DIR_TIER, BUILD_FILES, TEST_RE,
  projectDir, langDirsOf, codeLinesOfDir, codeFloorFor, recodeOf,
  bandOf, classify, readTopic, read, strip, codeBlocks, proseWords, run, resolveDir, python,
  manifestOf, queuedTopics,
  head, pass, defects, adjudicate,
  keyOf, norm, loadVerdicts, saveVerdicts, loadItems, saveItems, verdictPath, itemsPath, topicKey,
};
