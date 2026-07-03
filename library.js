/* ============================================================================
   library.js — стартова сторінка-«бібліотека»: Курси · Книги · Каталоги.
   Реєстр — window.SUBJECT_BOOKS / GUIDE_COURSES / CATALOG_BOOKS (books-index.js).
   ДВА вигляди (html[data-libview], перемикач #view-btn, localStorage):
     "tabs" — сегмент-контрол у hero, видно одну категорію (дефолт);
     "one"  — усі три секції на одній сторінці з заголовками-«рейками».
   Рендериться ОДИН DOM: перемикання виглядів — лише CSS + клас .off на секціях.
   ========================================================================== */
(function () {
  "use strict";
  var root = document.getElementById("library-root");
  if (!root) return;
  function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function fetchText(u) { return fetch(u, { cache: "no-cache" }).then(function (r) { return r.ok ? r.text() : ""; }).catch(function () { return ""; }); }
  function manifestObj(src, key) { var sb = {}; try { new Function("window", src)(sb); } catch (e) {} return (sb[key] || [])[0] || null; }

  var BOOKS = window.SUBJECT_BOOKS || [];
  var GUIDES = window.GUIDE_COURSES || [];
  var CATALOGS = window.CATALOG_BOOKS || [];
  var ICON = { physics: "⚛️", math: "🧮", chemistry: "⚗️", electronics: "🔌", programming: "💻", communications: "📡", algorithms: "🧠", philosophy: "🦉" };
  var ACCENT = { physics: "#6b5b95", math: "#3a6b9c", chemistry: "#3a8f80", electronics: "#b06a5a", programming: "#5a5f9c", communications: "#4a8296", algorithms: "#a5648a", philosophy: "#9a7b4f" };
  var DESC = {
    physics: "Як влаштований світ: рух, енергія, поля, кванти.",
    math: "Мова науки: числа, форми, функції, логіка міркувань.",
    chemistry: "Речовини, атоми й перетворення — з чого все зроблено.",
    electronics: "Струм, сигнали, схеми, сенсори — як працює залізо.",
    programming: "Архітектура, мови, ОС, мережі — як думає машина.",
    communications: "Хвилі, кодування, протоколи — як передаються дані.",
    algorithms: "Структури даних, складність, пошук, навчання машин.",
    philosophy: "Знання, буття, розум і добро — великі питання."
  };
  // Курси — власні іконка, колір і опис (щоб не були однаково-зелені).
  var GUIDE_ICON = { embedded: "🤖", "basic-chemistry": "⚗️" };
  var GUIDE_ACCENT = { embedded: "#c1683f", "basic-chemistry": "#2f9e8f" };
  var GUIDE_DESC = {
    embedded: "Від заряду й струму до власного пристрою: фізика, схемотехніка, мікроконтролери й автономні системи — крок за кроком.",
    "basic-chemistry": "Хімія для початківців: від атома й періодичної таблиці до реакцій, розчинів, органіки та розрахунків задач."
  };
  // Каталоги — «залізні» акценти: текстоліт для плат, ефір для зв'язку.
  var CAT_ICON = { boards: "🧩", connect: "📶" };
  var CAT_ACCENT = { boards: "#3f7d52", connect: "#3d7d92" };
  var CAT_DESC = {
    boards: "Плати й модулі-розширення: що на борту, живлення, як під'єднати.",
    connect: "Радіомодулі й канали передавання даних: характеристики та підключення."
  };

  // Тема ІСНУЄ, якщо написана хоч одна версія (basic АБО detailed): статус не "empty"/"pending".
  // Тема ЗАПЛАНОВАНА, якщо хоч одна версія не "empty".
  function verReadable(v) { return !!(v && v.status && v.status !== "empty" && v.status !== "pending"); }
  function verPlanned(v) { return !!(v && v.status && v.status !== "empty"); }
  function loadShelfItem(base, slug) {
    return fetchText(base + "/" + slug + "/manifest.js").then(function (src) {
      var b = manifestObj(src, "__BOOKS__");
      var planned = 0, exist = 0;
      ((b && b.sections) || []).forEach(function (sec) {
        (sec.topics || []).forEach(function (t) {
          if (verPlanned(t.basic) || verPlanned(t.detailed)) planned++;
          if (verReadable(t.basic) || verReadable(t.detailed)) exist++;
        });
      });
      return { slug: slug, title: (b && b.title) || slug, branches: ((b && b.sections) || []).length, topics: planned, done: exist };
    });
  }
  function loadBook(slug) { return loadShelfItem("book", slug); }
  function loadCatalog(slug) { return loadShelfItem("catalog", slug); }
  // Курси у двох схемах: нова (sections→topics) і стара (modules→chapters→steps).
  function loadGuide(slug) {
    return fetchText("guide/" + slug + "/manifest.js").then(function (src) {
      var g = manifestObj(src, "__GUIDES__");
      var mods = (g && (g.sections || g.modules)) || [];
      var steps = 0, chapters = 0;
      mods.forEach(function (m) {
        if (m.chapters && m.chapters.length) m.chapters.forEach(function (c) { chapters++; steps += (c.steps || []).length; });
        else steps += (m.topics || []).length;
      });
      return { slug: slug, title: (g && g.title) || slug, modules: mods.length, chapters: chapters, steps: steps };
    });
  }

  /* ── Картки ─────────────────────────────────────────────────────────── */
  function bookCard(b) {
    var pct = b.topics ? Math.round(b.done / b.topics * 100) : 0;
    var partial = b.done > 0 && b.done < b.topics;
    var complete = b.topics > 0 && b.done === b.topics;
    var topicsVal = complete ? String(b.topics)                          // усе готово — лише всього, без галочки
      : ('<b>' + b.done + '</b> / ' + b.topics);                          // інакше — готово / всього (напр. 60 / 72)
    return '<a class="lib-card" href="read.html?book=' + esc(b.slug) + '" style="--accent:' + (ACCENT[b.slug] || "#1d6fa4") + '">' +
      '<div class="lib-cover"><span class="lib-ico">' + (ICON[b.slug] || "📘") + '</span>' +
      '<span class="lib-cover-ttl">' + esc(b.title) + '</span></div>' +
      '<div class="lib-body"><p class="lib-desc">' + esc(DESC[b.slug] || "") + '</p>' +
      '<div class="lib-stats">' +
        '<div class="lib-stat-row"><span class="lib-stat-k">Галузі</span><span class="lib-stat-v">' + b.branches + '</span></div>' +
        '<div class="lib-stat-row"><span class="lib-stat-k">Теми</span><span class="lib-stat-v">' + topicsVal + '</span></div>' +
      '</div>' +
      (partial ? '<div class="lib-bar" title="' + pct + '% готово"><span style="width:' + pct + '%"></span></div>' : '') +
      '<div class="lib-foot"><span class="lib-modnote">' + (b.done ? (partial ? pct + '% готово' : 'готова') : 'у роботі') + '</span>' +
      '<span class="lib-cta">Читати →</span></div>' +
      '</div></a>';
  }
  function guideCard(g) {
    var accent = GUIDE_ACCENT[g.slug] || "#16a34a";
    var ico = GUIDE_ICON[g.slug] || "🎓";
    var desc = GUIDE_DESC[g.slug] || "Курс — доріжка крізь предметні книги, що веде темами по черзі й сплітає їх у навчання.";
    var chaptersRow = g.chapters ? '<div class="lib-stat-row"><span class="lib-stat-k">Розділи</span><span class="lib-stat-v">' + g.chapters + '</span></div>' : "";
    return '<a class="lib-card lib-card-guide" href="read.html?guide=' + esc(g.slug) + '" style="--accent:' + accent + '">' +
      '<div class="lib-cover"><span class="lib-kind">Курс</span><span class="lib-ico">' + ico + '</span>' +
      '<span class="lib-cover-ttl">' + esc(g.title) + '</span></div>' +
      '<div class="lib-body"><p class="lib-desc">' + esc(desc) + '</p>' +
      '<div class="lib-stats">' +
        '<div class="lib-stat-row"><span class="lib-stat-k">Модулі</span><span class="lib-stat-v">' + g.modules + '</span></div>' +
        chaptersRow +
        '<div class="lib-stat-row"><span class="lib-stat-k">Теми</span><span class="lib-stat-v">' + g.steps + '</span></div>' +
      '</div>' +
      '<div class="lib-foot"><span class="lib-modnote">Доріжка крізь книги</span>' +
      '<span class="lib-cta">Пройти →</span></div></div></a>';
  }
  function catalogCard(c) {
    var pct = c.topics ? Math.round(c.done / c.topics * 100) : 0;
    var partial = c.done > 0 && c.done < c.topics;
    var topicsVal = (c.topics > 0 && c.done === c.topics) ? String(c.topics) : ('<b>' + c.done + '</b> / ' + c.topics);
    return '<a class="lib-card lib-card-cat" href="read.html?book=' + esc(c.slug) + '" style="--accent:' + (CAT_ACCENT[c.slug] || "#5b6b7c") + '">' +
      '<div class="lib-cover"><span class="lib-kind lib-kind-cat">Каталог</span><span class="lib-ico">' + (CAT_ICON[c.slug] || "🗂️") + '</span>' +
      '<span class="lib-cover-ttl">' + esc(c.title) + '</span></div>' +
      '<div class="lib-body"><p class="lib-desc">' + esc(CAT_DESC[c.slug] || "") + '</p>' +
      '<div class="lib-stats">' +
        '<div class="lib-stat-row"><span class="lib-stat-k">Розділи</span><span class="lib-stat-v">' + c.branches + '</span></div>' +
        '<div class="lib-stat-row"><span class="lib-stat-k">Обʼєкти</span><span class="lib-stat-v">' + topicsVal + '</span></div>' +
      '</div>' +
      (partial ? '<div class="lib-bar" title="' + pct + '% готово"><span style="width:' + pct + '%"></span></div>' : '') +
      '<div class="lib-foot"><span class="lib-modnote">Довідник заліза</span>' +
      '<span class="lib-cta">Відкрити →</span></div></div></a>';
  }

  /* ── Вигляд (одна сторінка ⇄ вкладки) і активна вкладка ─────────────── */
  var TABS = ["guides", "books", "cats"];
  function getView() { try { return localStorage.getItem("courses-lib-view") === "one" ? "one" : "tabs"; } catch (e) { return "tabs"; } }
  function setView(v) {
    document.documentElement.setAttribute("data-libview", v);
    try { localStorage.setItem("courses-lib-view", v); } catch (e) {}
    paintViewBtn();
  }
  function initialTab() {
    var hsh = (location.hash || "").slice(1);
    if (TABS.indexOf(hsh) >= 0) return hsh;                       // #books / #cats — дипліншем
    try { var t = localStorage.getItem("courses-lib-tab"); if (TABS.indexOf(t) >= 0) return t; } catch (e) {}
    return "guides";                                              // курси головні
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

  function render(books, guides, cats) {
    var cur = initialTab(), curIdx = TABS.indexOf(cur);
    var h = '<header class="lib-hero"><div class="lib-hero-row"><div class="lib-hero-txt">' +
      '<div class="kicker">Бібліотека</div><h1>Мої книги</h1>' +
      '<p><b>Курси</b> ведуть темами по черзі й сплітають їх у навчання; <b>книги</b> — теорія за галузями; <b>каталоги</b> — довідники конкретних плат і модулів.</p></div>' +
      '<nav class="lib-hero-nums" aria-label="Розділи бібліотеки">' +
        '<a href="#sect-guides" data-goto="guides"><span class="num">' + guides.length + '</span><span class="lbl">Курси</span></a>' +
        '<a href="#sect-books" data-goto="books"><span class="num">' + books.length + '</span><span class="lbl">Книги</span></a>' +
        '<a href="#sect-cats" data-goto="cats"><span class="num">' + cats.length + '</span><span class="lbl">Каталоги</span></a>' +
      '</nav></div>' +
      '<div class="lib-seg" role="tablist" aria-label="Розділи бібліотеки" data-active="' + curIdx + '">' +
        '<span class="lib-seg-thumb" aria-hidden="true"></span>' +
        segBtn("guides", "🎓", "Курси", guides.length, cur === "guides") +
        segBtn("books", "📚", "Книги", books.length, cur === "books") +
        segBtn("cats", "🗂️", "Каталоги", cats.length, cur === "cats") +
      '</div></header>';
    h += '<div class="lib-flow">';
    h += '<section class="lib-sect' + (cur !== "guides" ? ' off' : '') + '" id="sect-guides">' +
      sectHead("Курси", guides.length, "послідовні доріжки — почни тут") +
      '<div class="lib-shelf lib-shelf-guides" id="shelf-guides" role="tabpanel" aria-labelledby="segtab-guides">' + guides.map(guideCard).join("") + '</div></section>';
    h += '<section class="lib-sect' + (cur !== "books" ? ' off' : '') + '" id="sect-books">' +
      sectHead("Книги", books.length, "теорія за галузями, довільний порядок") +
      '<div class="lib-shelf" id="shelf-books" role="tabpanel" aria-labelledby="segtab-books">' + books.map(bookCard).join("") + '</div></section>';
    h += '<section class="lib-sect' + (cur !== "cats" ? ' off' : '') + '" id="sect-cats">' +
      sectHead("Каталоги", cats.length, "довідники плат і модулів") +
      '<div class="lib-shelf lib-shelf-cats" id="shelf-cats" role="tabpanel" aria-labelledby="segtab-cats">' + cats.map(catalogCard).join("") + '</div></section>';
    h += '</div>';
    root.innerHTML = h;
    document.title = "Бібліотека — мої книги";
    initSeg();
    buildViewBtn();
  }

  /* Сегмент: перемикання вкладок (діє лише у вигляді "tabs" — CSS ховає .off) */
  function initSeg() {
    var seg = root.querySelector(".lib-seg");
    var btns = [].slice.call(seg.querySelectorAll(".lib-seg-btn"));
    function activate(name, focusBtn) {
      var i = TABS.indexOf(name); if (i < 0) i = 0;
      seg.setAttribute("data-active", String(i));               // рухає thumb чистим CSS
      btns.forEach(function (b, j) {
        var on = (j === i);
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-selected", on ? "true" : "false");
        b.tabIndex = on ? 0 : -1;                               // roving tabindex
        if (on && focusBtn) b.focus();
      });
      TABS.forEach(function (t, j) {
        var sect = root.querySelector("#sect-" + t);
        if (j === i) {
          sect.classList.remove("off");
          var p = sect.querySelector(".lib-shelf");
          p.classList.remove("shelf-in"); void p.offsetWidth;   // рестарт входу
          p.classList.add("shelf-in");
        } else sect.classList.add("off");
      });
      try { localStorage.setItem("courses-lib-tab", TABS[i]); } catch (e) {}
      if (history.replaceState) history.replaceState(null, "", "#" + TABS[i]);
    }
    btns.forEach(function (b) {
      b.addEventListener("click", function () { activate(b.getAttribute("data-tab"), false); });
    });
    seg.addEventListener("keydown", function (e) {              // ARIA tabs: стрілки/Home/End
      var i = Number(seg.getAttribute("data-active")) || 0, n = TABS.length, j = -1;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") j = (i + 1) % n;
      else if (e.key === "ArrowLeft" || e.key === "ArrowUp") j = (i - 1 + n) % n;
      else if (e.key === "Home") j = 0;
      else if (e.key === "End") j = n - 1;
      if (j >= 0) { e.preventDefault(); activate(TABS[j], true); }
    });
    // лічильники-якорі в hero: в one-вигляді скролять до секції, в tabs — активують вкладку
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

  /* Кнопка перемикання вигляду (⊞ вкладки ⇄ ▤ одна сторінка) — лише тут, у бібліотеці */
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
      if (v === "tabs" && root._activateTab) root._activateTab(initialTab(), false);  // синхронізувати сегмент
    });
    document.body.appendChild(viewBtn);
    paintViewBtn();
  }

  Promise.all([
    Promise.all(BOOKS.map(loadBook)),
    Promise.all(GUIDES.map(loadGuide)),
    Promise.all(CATALOGS.map(loadCatalog))
  ]).then(function (r) { render(r[0], r[1], r[2]); })
    .catch(function (e) { root.innerHTML = '<div class="state error"><h2>Помилка</h2><p><code>' + esc(e && e.message) + '</code></p></div>'; });
})();
