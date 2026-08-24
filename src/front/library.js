/* ============================================================================
   library.js (v7) — стартова сторінка-«бібліотека».

   Полиці приходять із root/shelf.json: один запис на вид (sci · eng · course ·
   hw · sys), кожен зі своїм заголовком полиці, словником (`words`) і питанням,
   на яке вид відповідає (`asks`). Додав вид або книгу в shelf.json — полиця
   зʼявилась тут сама, правити цей файл не треба.

   ДВА вигляди (html[data-libview], перемикач #view-btn, localStorage):
     "tabs" — сегмент-контрол у hero, видно одну полицю (дефолт);
     "one"  — усі полиці на одній сторінці з заголовками-«рейками».
   Рендериться ОДИН DOM: перемикання виглядів — лише CSS + клас .off на секціях.
   ========================================================================== */
(function () {
  "use strict";
  var root = document.getElementById("library-root");
  if (!root) return;
  function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function cap(s) { return String(s || "").charAt(0).toUpperCase() + String(s || "").slice(1); }

  var READ = (function () { try { return new Set(JSON.parse(localStorage.getItem("courses-read") || "[]")); } catch (e) { return new Set(); } })();

  /* Оформлення книг — суто фронтова справа (у контенті його нема). Нема запису —
     працює запасний варіант виду, тож нова книга зʼявляється й без правки цих мап. */
  var ICON = {
    physics: "⚛️", math: "🧮", chemistry: "⚗️", electronics: "🔌", programming: "💻",
    communications: "📡", algorithms: "🧠", philosophy: "🦉",
    embedded: "🤖", "embedded-ultra": "⚡", "basic-chemistry": "⚗️", progarch: "🏛️", unix: "🧭",
    boards: "🧩", connect: "📶", sensors: "🌡️", power: "🔋", actuators: "⚙️", instruments: "🔬", components: "🔩",
    "unix-linux": "🐧", "cpp-standards": "🧾", python: "🐍", "build-systems": "🔨", "media-vision": "🎞️", qgroundcontrol: "🛰️"
  };
  var ACCENT = {
    physics: "#6b5b95", math: "#3a6b9c", chemistry: "#3a8f80", electronics: "#b06a5a", programming: "#5a5f9c",
    communications: "#4a8296", algorithms: "#a5648a", philosophy: "#9a7b4f",
    embedded: "#c1683f", "embedded-ultra": "#a8492f", "basic-chemistry": "#2f9e8f", progarch: "#5a6b9c", unix: "#3d8a6b",
    boards: "#3f7d52", connect: "#3d7d92", sensors: "#c0803a", power: "#b0563f", actuators: "#5f6b8c",
    instruments: "#3f8a76", components: "#8a7355",
    "unix-linux": "#3f6b8a", "cpp-standards": "#6b4f8a", python: "#4a7a9c", "build-systems": "#8a6a3f",
    "media-vision": "#3f8a7a", qgroundcontrol: "#8a4f5f"
  };
  var KIND_ICON = { sci: "📚", eng: "🛠️", course: "🎓", hw: "🗂️", sys: "📗" };
  var KIND_ACCENT = { sci: "#3a6b9c", eng: "#b06a5a", course: "#16a34a", hw: "#5b6b7c", sys: "#4a6070" };
  var KIND_CTA = { course: "Пройти →", hw: "Відкрити →", sys: "Відкрити →" };
  /* Підпис лічильника груп — множина від words.group (українська множина неправильна,
     тож тримаємо готові форми, а не доклеюємо закінчення). */
  var KIND_GROUPS = { sci: "Галузі", eng: "Технології", course: "Томи", hw: "Групи", sys: "Модулі" };

  /* Опис книги береться з її manifest.json (`subtitle`). Тут — лише запасні описи
     для тих, що ще не мають свого; коли subtitle зʼявиться, він переможе. */
  var DESC = {
    physics: "Як влаштований світ: рух, енергія, поля, кванти.",
    math: "Мова науки: числа, форми, функції, логіка міркувань.",
    chemistry: "Речовини, атоми й перетворення — з чого все зроблено.",
    electronics: "Струм, сигнали, схеми, сенсори — як працює залізо.",
    programming: "Архітектура, мови, ОС, мережі — як думає машина.",
    communications: "Хвилі, кодування, протоколи — як передаються дані.",
    algorithms: "Структури даних, складність, пошук, навчання машин.",
    philosophy: "Знання, буття, розум і добро — великі питання.",
    embedded: "Від заряду й струму до власного пристрою: фізика, схемотехніка, мікроконтролери й автономні системи — крок за кроком.",
    "embedded-ultra": "Ембеддед за два дні: від напруги й транзистора до GPIO, шин, RTOS і OTA. Стислий зріз, без заглиблень.",
    "basic-chemistry": "Хімія для початківців: від атома й періодичної таблиці до реакцій, розчинів, органіки та розрахунків задач.",
    progarch: "Архітектура програмних систем: модульність, межі, залежності й масштаб — як будувати та підтримувати великий код.",
    unix: "Unix і Linux послідовно: від оболонки й файлів до процесів, прав і мережі — доріжка крізь довідник.",
    boards: "Плати й модулі-розширення: що на борту, живлення, як під'єднати.",
    connect: "Радіомодулі й канали передавання даних: характеристики та підключення.",
    sensors: "Давачі: рух, середовище, світло, звук — що вимірюють і як під'єднати.",
    power: "Живлення: перетворювачі, захист і акумулятори — струм і напруга під контролем.",
    actuators: "Виконавчі механізми: мотори, серводвигуни, драйвери — рух і сила.",
    instruments: "Вимірювальні прилади: мультиметри, генератори, аналізатори сигналів.",
    components: "Дискретні компоненти: резистори, конденсатори, напівпровідники.",
    "unix-linux": "Unix і Linux: як влаштована система, а не набір команд — процеси, пам'ять, файли, ядро.",
    "cpp-standards": "Стандарти C++: механіка мови, стандартна бібліотека й що приніс кожен реліз.",
    "build-systems": "Системи збірки: CMake, залежності й тулчейни — як із дерева вихідників постає артефакт.",
    "media-vision": "GStreamer і OpenCV як системи: конвеєр медіа й модель пам'яті зображень.",
    qgroundcontrol: "QGroundControl зсередини: підсистеми наземної станції, план, карта, відео, розширення."
  };

  /* Версія ЧИТАБЕЛЬНА, якщо статус не "empty"/"pending"; ЗАПЛАНОВАНА, якщо не "empty".
     Рахунок — по ТЕМАХ: тема «написана», якщо готова ХОЧ ОДНА версія (базова АБО детальна). */
  function verReadable(v) { return !!(v && v.status && v.status !== "empty" && v.status !== "pending"); }
  function verPlanned(v) { return !!(v && v.status && v.status !== "empty"); }

  /* Книга v7 → рядок для картки. `loadBook` (bookbuild.js) уже дав і адаптовану
     структуру, і сирі групи — рахуємо по сирих, бо там є ще й ref-кроки. */
  function stat(b) {
    var groups = b.groups || [];
    var chapters = 0, planned = 0, done = 0, refs = [], read = 0, written = {};
    groups.forEach(function (g) {
      (g.chapters || []).forEach(function (c) {
        if (c.title) chapters++;
        (c.topics || []).forEach(function (t) {
          if (!t) return;
          if (t.ref) {
            var pr = String(t.ref).split("/").filter(Boolean);
            var rb = pr[0], rt = pr[pr.length - 1];
            planned++; refs.push({ book: rb, slug: rt });
            if (READ.has(rb + "/" + rt)) read++;
            return;
          }
          if (!t.slug) return;                                   // місток — не стаття
          if (verPlanned(t.basic) || verPlanned(t.detailed)) planned++;
          if (verReadable(t.basic) || verReadable(t.detailed)) { done++; written[t.slug] = 1; }
          if (READ.has(b.bookSlug + "/" + t.slug)) read++;
        });
      });
    });
    return {
      slug: b.bookSlug, title: b.title, kind: b.kind, words: b.words || {},
      subtitle: b.subtitle || "", groups: groups.length, chapters: chapters,
      planned: planned, done: done, read: read, refs: refs, written: written
    };
  }

  /* ── Картка книги (одна форма на всі види; вид дає слова й підпис) ───── */
  function card(s) {
    var accent = ACCENT[s.slug] || KIND_ACCENT[s.kind] || "#1d6fa4";
    var ico = ICON[s.slug] || KIND_ICON[s.kind] || "📘";
    var desc = s.subtitle || DESC[s.slug] || "";
    var W = s.words || {};
    var complete = s.planned > 0 && s.done === s.planned;
    var pct = s.planned ? Math.round(s.done / s.planned * 100) : 0;
    var partial = s.done > 0 && !complete;
    var doneVal = complete ? String(s.planned) : ('<b>' + s.done + '</b> / ' + s.planned);
    var isCourse = s.kind === "course";

    var rows =
      '<div class="lib-stat-row"><span class="lib-stat-k">' + esc(KIND_GROUPS[s.kind] || cap(W.group || "Групи")) + '</span><span class="lib-stat-v">' + s.groups + '</span></div>' +
      (s.chapters ? '<div class="lib-stat-row"><span class="lib-stat-k">Розділи</span><span class="lib-stat-v">' + s.chapters + '</span></div>' : '') +
      '<div class="lib-stat-row"><span class="lib-stat-k">Написано</span><span class="lib-stat-v">' + doneVal + '</span></div>' +
      (isCourse ? '<div class="lib-stat-row"><span class="lib-stat-k">Прочитано</span><span class="lib-stat-v">' + s.read + '</span></div>' : '');

    var foot = complete ? (isCourse ? esc(W.book || "курс") + ' повний' : 'готова')
      : (s.done ? pct + '% написано' : 'у роботі');

    return '<a class="lib-card lib-card-' + esc(s.kind) + '" href="read.html?book=' + esc(s.slug) + '" style="--accent:' + accent + '">' +
      '<div class="lib-cover"><span class="lib-kind lib-kind-' + esc(s.kind) + '">' + esc(cap(W.book || "")) + '</span>' +
      '<span class="lib-cover-ttl">' + esc(s.title) + '</span></div>' +
      '<span class="lib-ico">' + ico + '</span>' +
      '<div class="lib-body"><p class="lib-desc">' + esc(desc) + '</p>' +
      '<div class="lib-stats">' + rows + '</div>' +
      (partial ? '<div class="lib-bar" title="' + pct + '% готово"><span style="width:' + pct + '%"></span></div>' : '') +
      '<div class="lib-foot"><span class="lib-modnote">' + foot + '</span>' +
      '<span class="lib-cta">' + (KIND_CTA[s.kind] || "Читати →") + '</span></div>' +
      '</div></a>';
  }

  /* ── Вигляд (одна сторінка ⇄ вкладки) і активна вкладка ─────────────── */
  var TABS = [];   // заповнюється з shelf.json
  function getView() { try { return localStorage.getItem("courses-lib-view") === "one" ? "one" : "tabs"; } catch (e) { return "tabs"; } }
  function setView(v) {
    document.documentElement.setAttribute("data-libview", v);
    try { localStorage.setItem("courses-lib-view", v); } catch (e) {}
    paintViewBtn();
  }
  function initialTab(shelves) {
    var hsh = (location.hash || "").slice(1);
    if (TABS.indexOf(hsh) >= 0) return hsh;
    try { var t = localStorage.getItem("courses-lib-tab"); if (TABS.indexOf(t) >= 0) return t; } catch (e) {}
    for (var i = 0; i < shelves.length; i++) if (shelves[i].items.length) return shelves[i].kind;   // перша непорожня
    return TABS[0];
  }

  function segBtn(tab, ico, lbl, count, active) {
    return '<button class="lib-seg-btn' + (active ? ' is-active' : '') + '" role="tab" id="segtab-' + tab +
      '" data-tab="' + tab + '" aria-selected="' + (active ? 'true' : 'false') +
      '" aria-controls="shelf-' + tab + '" tabindex="' + (active ? '0' : '-1') + '">' +
      '<span class="lib-seg-ico" aria-hidden="true">' + ico + '</span>' +
      '<span class="lib-seg-lbl">' + lbl + '</span>' +
      '<span class="lib-seg-count">' + count + '</span></button>';
  }
  function sectHead(ttl, count, note) {
    return '<div class="lib-sect-head"><h2 class="lib-sect-ttl">' + ttl + '</h2>' +
      '<span class="lib-sect-count">' + count + '</span><span class="lib-sect-line"></span>' +
      (note ? '<span class="lib-sect-note">' + note + '</span>' : '') + '</div>';
  }

  function render(shelves) {
    var cur = initialTab(shelves), curIdx = TABS.indexOf(cur);
    if (curIdx < 0) curIdx = 0;
    var lead = shelves.filter(function (s) { return s.items.length; })
      .map(function (s) { return '<b>' + esc(s.shelf.toLowerCase()) + '</b> — ' + esc(s.asks); }).join("; ");

    var h = '<header class="lib-hero"><div class="lib-hero-row"><div class="lib-hero-txt">' +
      '<div class="kicker">Бібліотека</div><h1>Мої книги</h1>' +
      '<p>' + (lead || "Полиці зʼявляться, коли книги переїдуть у нове дерево.") + '.</p></div>' +
      '<nav class="lib-hero-nums" aria-label="Полиці бібліотеки">' +
      shelves.map(function (s) {
        return '<a href="#sect-' + esc(s.kind) + '" data-goto="' + esc(s.kind) + '"><span class="num">' + s.items.length +
          '</span><span class="lbl">' + esc(s.shelf) + '</span></a>';
      }).join("") +
      '</nav></div>' +
      '<div class="lib-seg" role="tablist" aria-label="Полиці бібліотеки" data-active="' + curIdx + '">' +
      '<span class="lib-seg-thumb" aria-hidden="true"></span>' +
      shelves.map(function (s) {
        return segBtn(s.kind, KIND_ICON[s.kind] || "📘", s.shelf, s.items.length, s.kind === cur);
      }).join("") +
      '</div></header><div class="lib-flow">';

    shelves.forEach(function (s) {
      h += '<section class="lib-sect' + (s.kind !== cur ? ' off' : '') + '" id="sect-' + esc(s.kind) + '">' +
        sectHead(esc(s.shelf), s.items.length, esc(s.asks)) +
        '<div class="lib-shelf lib-shelf-' + esc(s.kind) + '" id="shelf-' + esc(s.kind) + '" role="tabpanel" aria-labelledby="segtab-' + esc(s.kind) + '">' +
        (s.items.length ? s.items.map(card).join("")
          : '<p class="lib-empty">Ця полиця поки порожня — книги переїжджають у нове дерево.</p>') +
        '</div></section>';
    });

    root.innerHTML = h + '</div>';
    document.title = "Бібліотека — мої книги";
    initSeg();
    buildViewBtn();
  }

  function initSeg() {
    var seg = root.querySelector(".lib-seg");
    if (!seg) return;
    var btns = [].slice.call(seg.querySelectorAll(".lib-seg-btn"));
    function activate(name, focusBtn) {
      var i = TABS.indexOf(name); if (i < 0) i = 0;
      seg.setAttribute("data-active", String(i));
      btns.forEach(function (b, j) {
        var on = (j === i);
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-selected", on ? "true" : "false");
        b.tabIndex = on ? 0 : -1;
        if (on && focusBtn) b.focus();
      });
      TABS.forEach(function (t, j) {
        var sect = root.querySelector("#sect-" + t);
        if (!sect) return;
        if (j === i) {
          sect.classList.remove("off");
          var p = sect.querySelector(".lib-shelf");
          if (p) { p.classList.remove("shelf-in"); void p.offsetWidth; p.classList.add("shelf-in"); }
        } else sect.classList.add("off");
      });
      try { localStorage.setItem("courses-lib-tab", TABS[i]); } catch (e) {}
      if (history.replaceState) history.replaceState(null, "", "#" + TABS[i]);
    }
    btns.forEach(function (b) {
      b.addEventListener("click", function () { activate(b.getAttribute("data-tab"), false); });
    });
    seg.addEventListener("keydown", function (e) {
      var i = Number(seg.getAttribute("data-active")) || 0, n = TABS.length, j = -1;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") j = (i + 1) % n;
      else if (e.key === "ArrowLeft" || e.key === "ArrowUp") j = (i - 1 + n) % n;
      else if (e.key === "Home") j = 0;
      else if (e.key === "End") j = n - 1;
      if (j >= 0) { e.preventDefault(); activate(TABS[j], true); }
    });
    [].forEach.call(root.querySelectorAll(".lib-hero-nums a"), function (a) {
      a.addEventListener("click", function (ev) {
        ev.preventDefault();
        var name = a.getAttribute("data-goto");
        if (getView() === "tabs") { activate(name, false); return; }
        var sect = root.querySelector("#sect-" + name);
        if (sect) sect.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
    root._activateTab = activate;
  }

  /* Кнопка перемикання вигляду (⊞ вкладки ⇄ ▤ одна сторінка) */
  var viewBtn = null;
  function paintViewBtn() {
    if (!viewBtn) return;
    var one = getView() === "one";
    viewBtn.textContent = one ? "▤" : "⊞";
    viewBtn.title = one ? "Вигляд: одна сторінка — клік: вкладки" : "Вигляд: вкладки — клік: одна сторінка";
  }
  function buildViewBtn() {
    if (document.getElementById("view-btn")) return;
    viewBtn = document.createElement("button");
    viewBtn.id = "view-btn"; viewBtn.type = "button";
    viewBtn.setAttribute("aria-label", "Перемкнути вигляд бібліотеки");
    viewBtn.addEventListener("click", function () {
      var v = getView() === "one" ? "tabs" : "one";
      setView(v);
      if (v === "tabs" && root._activateTab) root._activateTab(root.querySelector(".lib-seg-btn.is-active").getAttribute("data-tab"), false);
    });
    document.body.appendChild(viewBtn);
    paintViewBtn();
  }

  /* ── Завантаження: shelf.json → усі книги всіх видів ─────────────────── */
  loadShelf().then(function (sh) {
    if (!sh || !sh.kinds) throw new Error("root/shelf.json не прочитався");
    TABS = sh.kinds.map(function (k) { return k.kind; });
    var jobs = [];
    sh.kinds.forEach(function (k) {
      (k.books || []).forEach(function (slug) { jobs.push(loadBook(slug)); });
    });
    return Promise.all(jobs).then(function (all) {
      var bySlug = {};
      all.forEach(function (b) { if (b) bySlug[b.bookSlug] = stat(b); });
      // ref-кроки курсу написані, якщо тема написана в книзі-цілі
      Object.keys(bySlug).forEach(function (k) {
        var s = bySlug[k];
        s.refs.forEach(function (rf) {
          var tgt = bySlug[rf.book];
          if (tgt && tgt.written[rf.slug]) s.done++;
        });
      });
      return sh.kinds.map(function (k) {
        return {
          kind: k.kind, shelf: k.shelf, asks: k.asks || "", words: k.words || {},
          items: (k.books || []).map(function (sl) { return bySlug[sl]; }).filter(Boolean)
        };
      });
    });
  }).then(render)
    .catch(function (e) { root.innerHTML = '<div class="state error"><h2>Помилка</h2><p><code>' + esc(e && e.message) + '</code></p></div>'; });
})();
