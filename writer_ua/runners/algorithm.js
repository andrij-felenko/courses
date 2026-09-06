#!/usr/bin/env node
/* ============================================================================
   algorithm.js — ВНУТРІШНІЙ РІВЕНЬ: десять етапів над ОДНІЄЮ одиницею.

   Оркестратор дає чергу й стан; цей файл робить із однієї одиниці один файл. Межа
   між ними тримається на трьох речах, які приходять у `ctx`:

     ctx.set(поле, значення)   заповнити етап — поле заповнене, етап пройдено
     ctx.call(мітка, fn)       ОДИН запит до агента, з межею очікування
     ctx.enqueue(одиниці)      докласти в чергу: вставки, код, базову

   ⛔ ЛОКАЛЬНЕ РОБИТЬСЯ ЛОКАЛЬНО. Підготовка, розмір, зібрання, операції в маніфест —
   у `local.js`, нуль токенів. Агента кличемо лише там, де потрібне судження.

   ПОРЯДОК ПЕРЕВІРОК: розмір (локально) → викладка (онлайн, до 7 кіл) → формули
   (онлайн, раз) → код C/C++ (онлайн, без тексту). Він не довільний: розмір перший, бо
   викладка — єдине повне перечитування, і судити нею недописаний текст означало б
   питати вдруге. Після перепису розмір НЕ перевіряється знову — інакше коло
   «дописали → переписали → знову мало».
   ========================================================================== */
"use strict";
const P = require("./prompt.js");
const R = require("./parse.js");
const LOC = require("./local.js");
const MF = require("../lib/manifest.js");
const path = require("path");

const MAX_LAYOUT = 7;      // стеля кіл викладки; вичерпали — вважаємо написаною
const KEEP_SHARE = 0.75;   // скільки прози перепис МУСИТЬ зберегти; менше — це втрата, не правка
const MAX_SIZE_ROUNDS = 2; // скільки разів дописуємо за розміром
const MAX_FIG_ROUNDS = 4;  // скільки разів перемальовуємо фігуру за геометрією
/* ⚠️ Було 2, і це давало фігурі втричі менше спроб, ніж прозі (стеля викладки — 7).
   Канон вимагав не ліміту спроб, а результату: «доки зауважень нуль». Числом його не
   замінити, але 2 було просто мало: одна вада в написах з'їдала обидва кола. */

/**
 * Верхній наявний рівень із переліку «що можна додати» — і тільки він.
 * Рівні: 5 точно треба · 4 треба для розуміння · 3 для глибшого засвоєння ·
 * 2 засвоїмо простіше · 1 доповнює тему. Дописувати все підряд означало б
 * ростити статтю тим, що сам письменник поставив унизу.
 */
function topAdditions(list) {
  const top = (list || [])[0];
  if (!top) return "";
  return (list || []).filter((x) => x.level === top.level)
    .map((x) => `${x.level} | ${x.what}`).join("\n");
}

/** Обов'язкові блоки: немає — це помилка кроку, а не привід вгадувати. */
function need(res, tags, where) {
  const got = R.want(res, tags);
  if (got.missing.length) throw new Error(`${where}: у відповіді немає ${got.missing.join(", ")}`);
  return got.data;
}

/**
 * @param {object} unit  {book, slug, type, version, …} з local.unitOf
 * @param {object} ctx   від оркестратора: set/get/call/enqueue/state/run
 * @param {object} o     {ask, mentionRe, status}
 *        ask(prompt, label) → текст відповіді. Це ЄДИНЕ місце, де конвеєр торкається
 *        агента; чим саме він викликається — Claude, Antigravity, підробка — цей файл
 *        не знає й знати не повинен.
 */
async function algorithm(unit, ctx, o = {}) {
  const ask = o.ask;
  if (typeof ask !== "function") throw new Error("немає ask() — нічим питати агента");
  const u = unit;

  /* Код — своя дорога: ціль → архітектура → файли. Прози в нього немає, і етапи розміру
     й викладки йому нічого не сказали б. */
  if (u.type === "code") return codeAlgorithm(u, ctx, o);
  /* Фігура — теж своя: один задум, один файл, і коло ладу замикає локальний оракул. */
  if (u.type === "fig") return figAlgorithm(u, ctx, o);

  /* ── 1 · ПІДГОТОВКА · локально ─────────────────────────────────────────── */
  if (!ctx.get("prep")) {
    const dup = LOC.isDuplicate(u.book, u.slug);
    if (dup.written) throw new Error(`тема вже написана — це дубль, писати нічого`);
    ctx.set("prep", {
      /* ⚠️ Ключ пошуку — ЦІЛА назва теми, а не перше її слово. З першим словом
         «Одержимість примітивами» ловила «одержимість простотою» з історії Arduino:
         пошук за словом дає омонім, і чим коротше слово, тим більше шуму. */
      mentions: LOC.mentions(u, o.mentionRe || LOC.titleRe(u.title)),
      neighbours: LOC.neighbours(u),
      preknow: LOC.preknow(u),
      dupeHints: dup.hints,
    });
  }
  const prep = ctx.get("prep");
  const passed = prep.preknow || LOC.preknow(u);

  /* ── 2 · ЦІЛЬ Й ПЕРЕДУМОВИ · агент ─────────────────────────────────────── */
  if (!ctx.get("goal")) {
    const res = await ctx.call("ціль", () => ask(P.goal(u, {
      mentions: prep.mentions, linkable: LOC.linkable(u),
    }), "ціль"));
    const d = need(res, ["ЦІЛЬ"], "ціль");
    ctx.set("goal", {
      text: d["ЦІЛЬ"],
      /* Блок передумов нарешті має господаря. Доти правило про нього їхало письменникові,
         слота у відповіді не було, споживача теж — тобто його не писав ніхто. */
      preknow: R.preknow(R.blocks(res)["ПЕРЕДУМОВИ"] || ""),
    });
  }
  const goal = ctx.get("goal");
  const preknowText = (goal.preknow || [])
    .map((x) => `${x.title} — ${x.addr}${x.why ? " — " + x.why : ""}`).join("\n");

  /* ── 2б · РІВЕНЬ І ВСТАВКИ · агент ─────────────────────────────────────── */
  if (!ctx.get("scope")) {
    const res = await ctx.call("рівень і вставки", () => ask(P.scope(u, {
      goal: goal.text, preknow: preknowText, books: LOC.books(),
    }), "рівень і вставки"));
    const b = R.blocks(res);
    const lv = parseInt(b["РІВЕНЬ"] || "", 10);
    ctx.set("scope", {
      level: lv >= 1 && lv <= 3 ? lv : null,
      inserts: R.inserts(b["ВСТАВКИ"] || ""),
      code: R.code(b["КОД"] || ""),
      missingTopics: R.lines(b["БРАКУЄ ТЕМ"] || ""),
    });
  }
  const sc = ctx.get("scope");

  /* ── 3 · КАРКАС · агент ────────────────────────────────────────────────── */
  if (!ctx.get("karkas")) {
    const res = await ctx.call("каркас", () => ask(P.karkas(u, {
      goal: goal.text, level: sc.level, preknow: passed,
      inserts: sc.inserts.map((x) => `${x.insert}-${x.name || u.slug}: ${x.about}`).join("\n"),
    }), "каркас"));
    const b = R.blocks(res);
    const secs = R.sections(b["РОЗДІЛИ"] || b["КРОКИ"] || b["ПОДІЇ"] || b["ВАРІАНТИ"] || "");
    if (!secs.length) throw new Error("каркас: не повернув жодного пункту");
    /* Каркас відповідає рівно за три речі: що за розділи, як їх групувати, де фігури. */
    ctx.set("karkas", {
      sections: secs,
      groups: R.groups(b["ГРУПИ"] || "").length ? R.groups(b["ГРУПИ"]) : [secs.map((s) => s.n)],
      figs: LOC.figNames(R.figures(b["ФІГУРИ"] || "")),
    });
  }
  const k = ctx.get("karkas");

  /* Вставки типу 2 і код — окремі одиниці; вони стають у ту саму чергу батчу.
     Тип 1 у статтю не входить: він іде в нові теми на етап 8. Тип 3 лишається
     парою речень у тексті й одиницею не стає. */
  /* ⛔ ПИТАННЯ ПРО C І C++ СТОЇТЬ ДО ПИСЬМА, А НЕ ПІСЛЯ. Доти воно було етапом 7б —
     після письма й після викладки, — і друга мова ставала одиницею черги, коли стаття
     вже зібрана й більше не відкривається. Наслідок був детермінований: тека `cpp/` на
     диску є, директиви `:::code` на неї в прозі немає, вкладки `:::tabs` не виникає
     ніколи. Тепер обидві мови стають одиницями ДО паузи, і письменник дістає справжні
     шляхи обох. */
  if (!ctx.get("code") && sc.code.length) {
    const langs = [...new Set(sc.code.map((c) => c.lang))].join(", ");
    const res = await ctx.call("код c/c++", () => ask(P.codeLangs(u, { dir: u.dir, langs }), "код c/c++"));
    const b = R.blocks(res);
    const want = [];
    if (R.yes(b["C"]) && !/(^|,\s*)c(\s*,|$)/i.test(langs)) want.push("c");
    if (R.yes(b["CPP"]) && !/c\+\+|cpp/i.test(langs)) want.push("cpp");
    ctx.set("code", { c: b["C"] || "", cpp: b["CPP"] || "", want });
  }
  const extraLangs = (ctx.get("code") || {}).want || [];

  const codeUnits = [
    ...codeUnitsOf(u, sc.code, sc.level),
    ...extraLangs.map((l) => ({
      ...LOC.unitOf(u.book, u.slug, "code", ""),
      id: `${u.book}/${u.slug}:code-${l}`, type: "code", lang: l, level: sc.level,
      /* ⚠️ ОПИС БЕРЕМО З КАРКАСА, А НЕ «ТЕ САМЕ, ЩО ДЕСЬ». Ця одиниця тепер стає в чергу
         РАЗОМ із першою мовою, а не після неї, тож копіювати їй нічого: вона реалізує ту
         саму задачу самостійно. Сказати «те саме, що вже є» означало б послати її по код,
         якого ще немає. */
      about: (sc.code || []).map((c) => `розділ ${c.section}: ${c.what}`).join("\n"),
      carrier: u.file.replace(/\.md$/, ""), parent: u.id,
    })),
  ];
  /* ⛔ ДРУГА МОВА МУСИТЬ ДОЇХАТИ Й У ПРОЗУ. Переїзд питання на етап 3 зробив паузу
     чесною — стаття чекає обидві мови, — але прив'язку коду до розділів будували з
     `sc.code`, де другої мови немає й бути не може: її назвав не каркас, а окремий запит.
     Отже тека `cpp/` з'являлась, а директиви на неї не було, і вкладки `:::tabs` не
     виникало — рівно той дефект, який переїзд мав закрити. Тут ми дописуємо рядки другої
     мови до тих самих розділів, де код уже замовлено. */
  const codeRows = [
    ...sc.code,
    ...extraLangs.flatMap((l) => [...new Set(sc.code.map((c) => c.section))].map((sec) => ({
      section: sec, lang: l,
      what: `той самий приклад мовою ${l} — постав його вкладкою «:::tabs» поруч із першою мовою`,
    }))),
  ];
  const figUnits = figUnitsOf(u, k, goal, sc.level);
  if (!ctx.get("sections")) {
    /* Код — ПЕРШИМ у чергу: на нього чекає ця сама стаття, а вставки не чекає ніхто. */
    /* Фігури йдуть одразу за кодом, але НІЧОГО НЕ ЗАТРИМУЮТЬ: прозі потрібне саме лише
       ім'я файла, а його даємо ми. Чекати на малюнок означало б тримати готову статтю
       заручницею фігури — і провалена фігура забирала б із собою написану статтю. */
    const more = [...codeUnits, ...figUnits];
    for (const ins of sc.inserts.filter((x) => x.kind === 2))
      more.push({
        ...LOC.unitOf(u.book, u.slug, ins.insert, "", ins.name ? `${ins.insert}-${ins.name}` : ""),
        about: ins.about, section: ins.section,
      });
    if (more.length) ctx.enqueue(more);

    /* ⏸ ПАУЗА НА КОД. Проза посилається на файли, яких ще немає, тож писати її зараз
       означало б обіцяти читачеві те, чого не бачив і сам письменник. Одиниця віддає
       своє місце в пулі й стає знову в чергу, щойно код буде написано. */
    const waitFor = codeUnits.map((c) => c.id).filter((id) => !ctx.isDone(id));
    if (waitFor.length)
      throw Object.assign(new Error(`чекає на код: ${waitFor.join(", ")}`), { pause: true, waitFor });
  }

  /* ── 4 · ПИСЬМО · агенти, групами ──────────────────────────────────────── */
  if (!ctx.get("sections")) {
    const written = [];
    let theses = [];
    for (const g of k.groups) {
      const mine = k.sections.filter((s) => g.includes(s.n));
      /* ⚠️ ІМ'Я ВСТАВКИ Й СПРАВЖНІ ШЛЯХИ КОДУ — В ЗАВДАННЯ, А НЕ САМ ЛИШЕ ОПИС. Письменник
         мусить поставити на них лінк і директиву, а вигадати адресу він не може: діставши
         тільки «про що», він написав `hist-information-hiding.md` там, де вставка зветься
         `hist-enforced-hiding.md`, і лінк вийшов битий. Код на цей момент уже на диску —
         пауза для того й стоїть, — тож перелічуємо реальні файли. */
      const bound = [...sc.inserts.filter((x) => x.kind === 2 && g.includes(x.section))
        .map((x) => {
          const file = x.name ? `${x.insert}-${x.name}.md` : `${x.insert}-${u.slug}.md`;
          return `розділ ${x.section}: вставка «${x.about}»\n` +
            `  інтегрувати як вставку, лінк рівно такий: root:${u.book}/${u.slug}/${file}`;
        }),
      /* Код без розділу — до кожної групи: шляхи справжні, і письменник цитує їх там,
         де доречно. Просити ще й розділ означало б ділити одне рішення на два запити. */
      ...codeRows.filter((c) => c.section === null || g.includes(c.section)).map((c) => {
        const files = LOC.codeFiles(u, c.lang);
        return `розділ ${c.section}: код ${c.lang} — ${c.what}\n` +
          (files.length
            ? `  інтегрувати директивами «:::code <шлях>», шляхи рівно такі:\n${files.map((f) => `    ${f}`).join("\n")}`
            : `  файлів ще немає — не посилайся на них`);
      }),
      /* ⚠️ ФІГУРУ ЗАМОВЛЯЄ КАРКАС, А СТАВИТЬ ПИСЬМЕННИК. Він знає своє місце в розділі
         й напише підпис зі змісту. Ім'я файла даємо МИ: інакше повториться те, що вже
         було з іменами вставок — правдоподібна адреса в нікуди. */
      ...(k.figs || []).filter((f) => g.includes(f.section)).map((f) =>
        `розділ ${f.section}: фігура — ${f.what}\n` +
        `  постав рівно так: ![{опис, що показано і що з неї видно}](${f.file})\n` +
        `  підпис — звичайним реченням курсивом наступним рядком, без номера й без «Рис.»`,
      )].join("\n");

      const res = await ctx.call(`письмо ${g.join(",")}`, () => ask(P.write(u, {
        goal: goal.text, level: sc.level,
        sections: mine.map((s) => `${s.n} | важливість: ${s.importance} | ${s.text}`).join("\n"),
        theses: theses.join("\n"), inserts: bound, passed, linkable: LOC.linkable(u),
        opory: preknowText,
      }), `письмо ${g.join(",")}`));

      const d = need(res, ["ТЕКСТ"], `письмо ${g.join(",")}`);
      const b = R.blocks(res);
      theses = theses.concat(R.lines(b["ТЕЗИ"] || ""));
      written.push({
        group: g, text: d["ТЕКСТ"], theses: R.lines(b["ТЕЗИ"] || ""),
        add: R.additions(b["ЩО ДОДАТИ"] || ""),
        squeeze: R.empty(b["ЩО ЗЖАТИ"]) ? "" : b["ЩО ЗЖАТИ"],
        newTopics: R.empty(b["НОВІ ТЕМИ"]) ? [] : R.lines(b["НОВІ ТЕМИ"]),
      });
    }
    ctx.set("sections", written);
  }
  let parts = ctx.get("sections");

  /* ── 5 · РОЗМІР · локально → дописування ───────────────────────────────── */
  if (!ctx.get("size")) {
    let rounds = 0, s = LOC.size(LOC.assemble(parts.map((p) => p.text)), u.type, sc.level);
    while (s.shortBy > 0 && rounds < MAX_SIZE_ROUNDS) {
      /* ⚠️ Дописуємо не «до числа», а НАЗВАНИМ матеріалом — і беремо з нього рівно
         найважливіше: письменник ранжує, що можна додати, від 5 до 1, а сюди йде лише
         верхній рівень із наявних. Дописали його — наступне коло візьме той, що став
         верхнім тепер. Так обсяг росте від «точно треба» вниз, а не абичим.
         Нема чого назвати — рахуємо як пройдене; за домовленістю це рідкість, бо
         порожнім перелік не буває. */
      const hungry = parts.filter((p) => (p.add || []).length);
      if (!hungry.length) break;
      for (const p of hungry) {
        const res = await ctx.call(`дописування ${p.group.join(",")}`, () => ask(P.extend(u, {
          goal: goal.text, level: sc.level,
          section: p.group.join(", "), text: p.text,
          neighbours: parts.filter((x) => x !== p).flatMap((x) => x.theses).join("\n"),
          add: topAdditions(p.add), linkable: LOC.linkable(u),
        }), `дописування ${p.group.join(",")}`));
        const d = need(res, ["ТЕКСТ"], "дописування");
        const b = R.blocks(res);
        p.text = d["ТЕКСТ"];
        p.theses = R.lines(b["ТЕЗИ"] || p.theses.join("\n"));
        p.add = R.additions(b["ЩО ДОДАТИ"] || "");
        p.squeeze = R.empty(b["ЩО ЗЖАТИ"]) ? "" : b["ЩО ЗЖАТИ"];
        /* Дописування народжує найбільше нового тексту, отже й найбільше нових тем.
           Доти хвіст наказу їх просив, а контракт не приймав — вони гинули тут. */
        if (!R.empty(b["НОВІ ТЕМИ"]))
          p.newTopics = [...(p.newTopics || []), ...R.lines(b["НОВІ ТЕМИ"])];
      }
      rounds++;
      s = LOC.size(LOC.assemble(parts.map((x) => x.text)), u.type, sc.level);
    }

    /* ── стиснення: дзеркало дописування ─────────────────────────────────────
       Перевищили стелю — стискаємо НАЗВАНИМ матеріалом, тим, що письменник сам
       поклав у «Що зжати». Нема чого назвати — лишаємо як є: сліпе обрубання по
       числу думати не вміє й рве нитку посередині. Факт лягає в стан і в лог. */
    let squeezed = 0;
    const cantCut = [], splitOff = [];
    while (s.over && squeezed < MAX_SIZE_ROUNDS) {
      const fat = parts.filter((p) => p.squeeze);
      if (!fat.length) break;
      for (const p of fat) {
        const res = await ctx.call(`стиснення ${p.group.join(",")}`, () => ask(P.compress(u, {
          goal: goal.text, level: sc.level,
          section: p.group.join(", "), text: p.text,
          neighbours: parts.filter((x) => x !== p).flatMap((x) => x.theses).join("\n"),
          squeeze: p.squeeze,
        }), `стиснення ${p.group.join(",")}`));
        const d = need(res, ["ТЕКСТ"], "стиснення");
        const b = R.blocks(res);
        p.text = d["ТЕКСТ"];
        p.theses = R.lines(b["ТЕЗИ"] || p.theses.join("\n"));
        p.squeeze = R.empty(b["ЩО ЗЖАТИ"]) ? "" : b["ЩО ЗЖАТИ"];
        /* ⛔ ДВА ВИХОДИ СТИСКАЧА ЧИТАЮТЬСЯ, А НЕ ПРОСЯТЬСЯ ДАРМА. «Не ріжеться» — єдиний
           спосіб відмовитися, і без цього рядка розділ, щойно оголошений недоторканним,
           ішов на друге коло. «Окрема тема» лягає в те саме місце, що й нові теми
           письменника: місце для неї в конвеєрі є, треба було лише донести. */
        if (!R.empty(b["НЕ РІЖЕТЬСЯ"])) {
          cantCut.push(`розділи ${p.group.join(",")}: ${b["НЕ РІЖЕТЬСЯ"]}`);
          p.squeeze = "";                       // більше не пропонуємо його різати
        }
        if (!R.empty(b["ОКРЕМА ТЕМА"])) splitOff.push(...R.lines(b["ОКРЕМА ТЕМА"]));
      }
      squeezed++;
      s = LOC.size(LOC.assemble(parts.map((x) => x.text)), u.type, sc.level);
    }
    ctx.set("size", {
      ...s, rounds, squeezed, stillOver: s.over, cantCut, splitOff,
      nothingToSqueeze: s.over && !parts.some((p) => p.squeeze),
    });
    ctx.set("sections", parts);
  }

  /* ── 6 · ВИКЛАДКА · агент, до 7 кіл ────────────────────────────────────── */
  if (!ctx.get("layout")) {
    let attempt = 0, ok = false, why = [], shrank = null;
    while (attempt < MAX_LAYOUT) {
      const text = LOC.assemble(parts.map((p) => p.text));
      const res = await ctx.call(`викладка ${attempt + 1}`, () => ask(P.layout(u, {
        goal: goal.text, level: sc.level, text, passed,
      }), `викладка ${attempt + 1}`));
      const b = R.blocks(res);
      if (R.yes(b["ОК"])) { ok = true; break; }
      why = R.defects(b["НЕ ТАК"] || "");
      if (!why.length) { ok = true; break; }
      attempt++;
      const rw = await ctx.call(`перепис ${attempt}`, () => ask(P.rewrite(u, {
        goal: goal.text, paragraphs: text, attempt, maxAttempts: MAX_LAYOUT,
        linkable: LOC.linkable(u),
        defect: why.map((d) => `${d.where} :: ${d.why}`).join("\n"),
      }), `перепис ${attempt}`));
      const d = need(rw, ["ТЕКСТ"], "перепис");

      /* ⛔ ЗАСТАВА ПРОТИ З'ЇДЕНОГО ТЕКСТУ. Відповідь перепису замінює СТАТТЮ ЦІЛКОМ, тож
         короткий переказ замість тексту знищує написане мовчки. Один раз це вже сталося:
         2080 слів прози до перепису, 616 після. Перевірка локальна й коштує нуль — просто
         рахуємо прозу до й після; втратив чверть — це не правка, а втрата, і ми її не
         приймаємо: лишається попередній текст, коло ладу спиняється, випадок іде в лог. */
      const was = LOC.size(text, u.type, sc.level).words;
      const now = LOC.size(d["ТЕКСТ"], u.type, sc.level).words;
      if (now < was * KEEP_SHARE) {
        shrank = { was, now, share: Math.round((now / was) * 100) };
        break;                        // текст лишається попередній, неторканий
      }

      parts = [{ group: parts.flatMap((p) => p.group), text: d["ТЕКСТ"], theses: parts.flatMap((p) => p.theses), add: "" }];
      ctx.set("sections", parts);
    }
    /* Вичерпали спроби — вважаємо написаною, і випадок іде в лог помилок батчу.
       З'їдений перепис — те саме: текст лишається останній цілий, а `shrank` каже, на
       чому спинились і скільки прози втратив би текст, якби відповідь прийняли. */
    ctx.set("layout", { ok, attempts: attempt, why: ok ? [] : why, gaveUp: !ok || !!shrank, shrank });
  }

  /* ── 7 · ФОРМУЛИ · агент, один раз ─────────────────────────────────────── */
  if (!ctx.get("formulas") && (u.type === "article" || u.type === "math")) {
    const text = LOC.assemble(parts.map((p) => p.text));
    const lines = text.split("\n").filter((l) => /[=≈]\s*[-\d]/.test(l)).slice(0, 60).join("\n");
    if (lines) {
      const res = await ctx.call("формули", () => ask(P.formulas(u, { lines }), "формули"));
      ctx.set("formulas", R.lines(R.blocks(res)["ЗАМІНИ"] || ""));
    } else ctx.set("formulas", []);
  }

  /* ── 8 · ВІДКЛАДЕНЕ ────────────────────────────────────────────────────── */
  if (!ctx.get("deferred")) {
    /* ⛔ ГЕЙТ БАЗОВОЇ: ОБСЯГ ЛОКАЛЬНО, ЗМІСТ — АГЕНТОМ. Три зони рахуються тут за нуль
       токенів, і нижня зона закриває питання без жодного запиту: коротка детальна сама і
       є входом у тему. Агента кличемо лише там, де рішення справді змістове.
       Доти тут стояло `basicNeeded: null` — крок був заявлений і не зроблений, а всі
       чотири ознаки лежали в `process.md`, якого не читає ніхто. */
    let basic = null;
    if (u.type === "article" && !u.insert) {
      const words = LOC.size(LOC.assemble(parts.map((p) => p.text)), u.type, sc.level).words;
      if (words < 2250) basic = { need: false, why: `детальна ${words} слів — коротка сама є входом`, asked: false };
      else {
        const zone = words > 4000
          ? `${words} слів — це зона «базова ПОТРІБНА», дефолт «ні» тут не діє`
          : `${words} слів — це середня зона, вирішує зміст`;
        const res = await ctx.call("чи треба базова", () => ask(P.basicNeeded(u, {
          goal: goal.text, level: sc.level, zone,
          text: LOC.assemble(parts.map((p) => p.text)),
        }), "чи треба базова"));
        const b = R.blocks(res);
        basic = { need: R.yes(b["ТРЕБА"]), why: b["ЧОМУ"] || "", words, asked: true };
      }
    }
    ctx.set("deferred", {
      newTopics: [
        ...sc.inserts.filter((x) => x.kind === 1).map((x) => `${x.about} (назвав каркас)`),
        ...parts.flatMap((p) => (p.newTopics || []).map((t) => `${t} (назвав письменник)`)),
        ...sc.missingTopics.map((t) => `${t} (назвав каркас, з переліку книг)`),
      ],
      basicNeeded: basic,
      /* Матеріал, що переріс тему, стискач назвав окремо — він теж нова тема. */
      splitOff: (ctx.get("size") || {}).splitOff || [],
    });
  }

  /* ── 9 · ЗІБРАННЯ · локально ───────────────────────────────────────────── */
  if (!ctx.get("figures")) {
    const file = LOC.writeArticle(u, LOC.assemble(parts.map((p) => p.text)), goal.preknow);
    /* ⛔ РОЗМІТКУ ФОРМУЛ ПЕРЕВІРЯЄМО ТУТ, А НЕ ПОТІМ РУКАМИ. Нуль токенів: з'їдений
       бекслеш лагодиться сам, непарні роздільники лягають у стан і в лог батчу. Доти
       сито жило збоку окремою командою — і 231 побитий рядок доїхав до читача. */
    const frm = LOC.fixFormulas(path.join(MF.ROOT, file));
    /* Фігури — там само й тим само коштом, але тут це ОГЛЯД УСІЄЇ ТЕКИ, а не коло ладу:
       кожну фігуру вже довела до чистого своя одиниця `fig`. Лишається те, чого одна
       фігура про себе не знає: обіцяна прозою й відсутня, чужа стара з дрібним шрифтом.
       `--links` вмикається лише тоді, коли черга фігур цієї теми вже пройдена. */
    const pending = (k.figs || []).map((f) => figId(u, f)).filter((id) => !ctx.isDone(id));
    const fig = LOC.checkFigures(u.dir, { links: !pending.length });
    /* Спершу виносимо довгий код у файли, і лише тоді рахуємо, що лишилось. */
    const moved = LOC.decamp(path.join(MF.ROOT, file));
    const fen = { ...LOC.checkFences(path.join(MF.ROOT, file)), moved };
    ctx.set("figures", { file, formulas: frm, svg: { ...fig, pending }, fences: fen });
  }

  /* ── 10 · ОПЕРАЦІЇ В МАНІФЕСТ ──────────────────────────────────────────── */
  if (!ctx.get("ops")) {
    const ops = LOC.ops(u, o.status || "recheck");
    /* ⛔ ВЕРДИКТ ГЕЙТА МУСИТЬ КУДИСЬ ІТИ. Доти він лягав у стан, якого не читає жоден
       рядок репо, — тобто запит коштував увесь текст статті заради відповіді, яку
       викидали. Тепер він стає операцією: `pending` — базову писати, `empty` — не треба.
       Це рівно ті два з трьох виходів, які описує процес; третій (детальна ще не
       написана) сюди не доходить за побудовою. */
    const basic = (ctx.get("deferred") || {}).basicNeeded;
    if (basic && !u.insert && u.type === "article")
      ops.push({ op: "status", slug: u.slug, ver: "basic", status: basic.need ? "pending" : "empty" });
    ctx.set("ops", ops);
  }

  return { file: ctx.get("figures").file, ops: ctx.get("ops") };
}

/* ── фігура як одиниця ─────────────────────────────────────────────────────── */

/**
 * Адреса одиниці фігури. Виводиться з імені файла, тож і той, хто ставить у чергу, і
 * той, хто потім питає «чи вже намальовано», рахують її однаково й без маніфесту.
 */
const figId = (u, f) => `${u.book}/${u.slug}:${f.file.replace(/^img\//, "").replace(/\.svg$/, "")}`;

/**
 * Одиниці фігур із каркаса: по одній на ФІГУРУ, бо фігура — це один файл і один задум.
 *
 * ⚠️ МАЛЮЄ ОКРЕМА ОДИНИЦЯ, А НЕ ПИСЬМЕННИК. Доти каркас фігуру замовляв, проза на неї
 * посилалася — а файла не малював ніхто: директива вела в порожнечу, і `--links` це
 * бачив уже після читача. Малювання винесено тим самим ходом, що й код.
 *
 * Ціль теми їде з одиницею: фігура має показати те саме, що доводить стаття, а статті
 * вона не бачить.
 */
function figUnitsOf(u, k, goal, level) {
  return (k.figs || []).map((f) => ({
    ...LOC.unitOf(u.book, u.slug, "fig", ""),
    id: figId(u, f),
    type: "fig", figFile: f.file, section: f.section, about: f.what,
    goal: (goal && goal.text) || "", level: level || null,
    parent: u.id,
  }));
}

/** Схоже на цілий SVG-файл? Обрубок не має ні затирати намальоване, ні лягати на диск. */
const wholeSvg = (s) => /<svg[\s>]/i.test(String(s || "")) && /<\/svg>/i.test(String(s || ""));

/**
 * Дорога фігури: намалювати → зміряти локально → перемалювати назване. Прози немає,
 * маніфесту немає — фігуру реєструє директива в тексті, тож `ops` порожні НАВМИСНО.
 *
 * ⛔ ГЕОМЕТРІЮ СУДИТЬ ОРАКУЛ, А НЕ АГЕНТ. `svg.py` міряє точно й коштує нуль, тому коло
 * ладу тут замкнене локально: агент бачить рівно ті місця, які машина назвала. Без
 * цього кола малювання наосліп давало б те саме, що дало письмо без перевірок.
 */
async function figAlgorithm(u, ctx, o) {
  const ask = o.ask;

  if (!ctx.get("prep")) ctx.set("prep", { file: u.figFile, section: u.section, what: u.about });

  if (!ctx.get("sections")) {
    const res = await ctx.call("фігура", () => ask(P.figure(u, {
      goal: u.goal, what: u.about, section: u.section, file: u.figFile, level: u.level,
    }), "фігура"));
    const d = need(res, ["SVG"], "фігура");
    if (!wholeSvg(d["SVG"])) throw new Error("фігура: у відповіді не цілий svg-файл");
    ctx.set("sections", { svg: d["SVG"] });
  }

  if (!ctx.get("figures")) {
    let svg = ctx.get("sections").svg;
    let file = LOC.writeFigure(u, u.figFile, svg);
    let iss = LOC.checkFigure(u, u.figFile), rounds = 0;
    while (iss.length && rounds < MAX_FIG_ROUNDS) {
      rounds++;
      const res = await ctx.call(`фігура-лад ${rounds}`, () => ask(P.figureFix(u, {
        what: u.about, file: u.figFile, svg, issues: iss.join("\n"), attempt: rounds,
      }), `фігура-лад ${rounds}`));
      const d = need(res, ["SVG"], "перемальовування");
      /* Обрубок замість файла лишає на диску попередню фігуру: вона гірша за задум, але
         вона є, а половина svg не показує нічого. Коло спиняється, випадок іде в стан. */
      if (!wholeSvg(d["SVG"])) break;
      svg = d["SVG"];
      file = LOC.writeFigure(u, u.figFile, svg);
      iss = LOC.checkFigure(u, u.figFile);
    }
    ctx.set("figures", { file, issues: iss, rounds });
  }

  if (!ctx.get("ops")) ctx.set("ops", []);
  return { file: ctx.get("figures").file, ops: [] };
}

/* ── код як одиниця ────────────────────────────────────────────────────────── */

/**
 * Одиниці коду з каркаса: по одній на МОВУ, бо тека мови — корінь проєкту, і два
 * рядки каркаса на одну мову — це два файли одного проєкту, а не два проєкти.
 * Носій — файл статті, що на код посилається: саме він дає ім'я теці.
 */
function codeUnitsOf(u, code, level) {
  const byLang = new Map();
  for (const c of code || []) {
    const lang = String(c.lang || "").trim().toLowerCase();
    if (!lang) continue;
    if (!byLang.has(lang)) byLang.set(lang, []);
    byLang.get(lang).push(`розділ ${c.section}: ${c.what}`);
  }
  return [...byLang.entries()].map(([lang, what]) => ({
    ...LOC.unitOf(u.book, u.slug, "code", ""),
    id: `${u.book}/${u.slug}:code-${lang}`,
    /* Рівень одиниця коду успадковує: свого запиту про рівень у неї немає й не треба. */
    type: "code", lang, level, about: what.join("\n"),
    carrier: u.file.replace(/\.md$/, ""), parent: u.id,
  }));
}

/**
 * Дорога коду: ціль → архітектура → файли на диск. Ті самі поля стану, що й у
 * статті, — «sections» тут це файли, «figures» — що записано. У маніфест код не
 * йде: його реєструє посилання `:::code` у прозі, тож `ops` порожні НАВМИСНО.
 */
async function codeAlgorithm(u, ctx, o) {
  const ask = o.ask;

  if (!ctx.get("prep")) ctx.set("prep", { carrier: u.carrier, lang: u.lang, about: u.about });

  if (!ctx.get("goal")) {
    const res = await ctx.call("ціль", () => ask(P.goal(u, { mentions: "" }), "ціль"));
    const d = need(res, ["ЦІЛЬ"], "ціль");
    const lv = R.blocks(res)["РІВЕНЬ"];
    ctx.set("goal", { text: d["ЦІЛЬ"], level: lv ? parseInt(lv, 10) || null : null });
  }
  const goal = ctx.get("goal");

  if (!ctx.get("karkas")) {
    const res = await ctx.call("архітектура", () => ask(P.karkas(u, {
      goal: goal.text, level: u.level, preknow: "", inserts: "",
    }), "архітектура"));
    const b = R.blocks(res);
    const files = R.lines(b["ФАЙЛИ"] || "");
    if (!files.length) throw new Error("архітектура: не повернула жодного файла");
    ctx.set("karkas", { files, classes: R.lines(b["КЛАСИ"] || ""), structure: b["СТРУКТУРА"] || "" });
  }
  const k = ctx.get("karkas");

  if (!ctx.get("sections")) {
    const res = await ctx.call("код", () => ask(P.codeWrite(u, {
      goal: goal.text, level: u.level,
      files: k.files.join("\n"), classes: k.classes.join("\n"), structure: k.structure,
    }), "код"));
    const files = R.files(res);
    if (!files.length) throw new Error("код: у відповіді немає жодного блоку <ФАЙЛ>");
    ctx.set("sections", files);
  }

  if (!ctx.get("figures")) ctx.set("figures", { files: LOC.writeCode(u, ctx.get("sections")) });
  if (!ctx.get("ops")) ctx.set("ops", []);
  return { files: ctx.get("figures").files, ops: [] };
}

module.exports = {
  algorithm, codeAlgorithm, codeUnitsOf, figAlgorithm, figUnitsOf, figId,
  MAX_LAYOUT, MAX_SIZE_ROUNDS, MAX_FIG_ROUNDS,
};
