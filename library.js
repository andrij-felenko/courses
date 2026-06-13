/* ============================================================================
   library.js — стартова сторінка-«бібліотека» зі списком книг.
   Читає window.LIBRARY (масив {id, entry, accent, icon, book}), де book —
   це той самий об'єкт window.BOOK із відповідного manifest.

   Статистику тем/спец-тем рахуємо ЖИВЦЕМ із _status.md кожного модуля
   (basePath + module.slug + "/_status.md") — їх веде /loop, тож завжди актуально.
     • тема         — рядок «- <статус> 2.1.3 Назва» (номер М.Р.Т)
     • спец-тема    — «- <статус> 📜/🧮/🔌/⚙️ …», рахуємо ОКРЕМО по типах:
                       📜 історія · 🧮 математика · 🔌 компоненти · ⚙️ проєкти
     • готова       — статус 🟢 (🔄 «написано, в редактурі» НЕ рахуємо як готову)
   ========================================================================== */
(function () {
  "use strict";
  var LIB = window.LIBRARY || [];
  var root = document.getElementById("library-root");
  if (!root) return;

  function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  // emoji → ключ типу спец-теми (⚙ і ⚙️ → той самий proj)
  var SPEC = [
    { e: "📜", key: "hist" }, { e: "🧮", key: "math" },
    { e: "🔌", key: "comp" }, { e: "⚙️", key: "proj" }, { e: "⚙", key: "proj" }
  ];
  // порядок і підписи рядків спец-тем у картці
  var SPEC_ROWS = [
    { key: "hist", label: "📜 Історія" }, { key: "math", label: "🧮 Математика" },
    { key: "comp", label: "🔌 Компоненти" }, { key: "proj", label: "⚙️ Проєкти" }
  ];
  function emptyStats() {
    return { topics: 0, topicsDone: 0, hist: { t: 0, d: 0 }, math: { t: 0, d: 0 }, comp: { t: 0, d: 0 }, proj: { t: 0, d: 0 } };
  }
  function parseStatus(text, s) {
    var lines = String(text).split(/\r?\n/);
    for (var i = 0; i < lines.length; i++) {
      var m = lines[i].match(/^\s*-\s*(🟢|🔄|🟡|⬜)\s+(.*)$/u);
      if (!m) continue;
      var done = m[1] === "🟢", c = m[2], type = null;
      for (var k = 0; k < SPEC.length; k++) { if (c.indexOf(SPEC[k].e) === 0) { type = SPEC[k].key; break; } }
      if (type) { s[type].t++; if (done) s[type].d++; }
      else if (/^\d+(\.\d+)+/.test(c)) { s.topics++; if (done) s.topicsDone++; }
    }
    return s;
  }

  function chapterCounts(book) {
    var done = 0, total = 0;
    (book.modules || []).forEach(function (m) {
      (m.chapters || []).forEach(function (c) { total++; if (c.status === "done") done++; });
    });
    return { done: done, total: total, mods: (book.modules || []).length };
  }

  function fetchText(url) {
    return fetch(url, { cache: "no-cache" }).then(function (r) { return r.ok ? r.text() : ""; }).catch(function () { return ""; });
  }

  // Лічба тем/спец-тем — з manifest (chapter.topics[]); розділ книги-довідника = тема.
  function loadBookStats(item) {
    var b = item.book || {};
    item.chap = chapterCounts(b);
    var s = emptyStats();
    (b.modules || []).forEach(function (m) {
      (m.chapters || []).forEach(function (c) {
        if (c.topics && c.topics.length) {
          c.topics.forEach(function (t) {
            var done = t.status === "done";
            if (!t.kind) { s.topics++; if (done) s.topicsDone++; }
            else { var k = (t.kind === "proj" ? "proj" : t.kind); if (s[k]) { s[k].t++; if (done) s[k].d++; } }
          });
        } else { s.topics++; if (c.status === "done") s.topicsDone++; }
      });
    });
    item.topics = s;
    return Promise.resolve();
  }

  /* ── рендер ─────────────────────────────────────────────────────────── */
  function statRow(label, done, total, sub) {
    return '<div class="lib-stat-row' + (sub ? " lib-stat-sub" : "") + '"><span class="lib-stat-k">' + label + "</span>" +
      '<span class="lib-stat-v"><b>' + done + "</b> / " + total + "</span></div>";
  }

  function card(item) {
    var b = item.book || {};
    var c = item.chap || { done: 0, total: 0, mods: 0 };
    var t = item.topics || emptyStats();
    var pct = t.topics ? Math.round(t.topicsDone / t.topics * 100) : (c.total ? Math.round(c.done / c.total * 100) : 0);
    var rows = statRow("Розділи", c.done, c.total) + statRow("Теми", t.topicsDone, t.topics);
    var specTotal = t.hist.t + t.math.t + t.comp.t + t.proj.t;
    if (specTotal > 0) {
      rows += '<div class="lib-stat-head">Спец-теми за типом</div>';
      SPEC_ROWS.forEach(function (r) { if (t[r.key].t > 0) rows += statRow(r.label, t[r.key].d, t[r.key].t, true); });
    }
    return '<a class="lib-card" href="' + esc(item.entry) + '" style="--accent:' + esc(item.accent || "#1d6fa4") + '">' +
      '<div class="lib-cover"><span class="lib-ico">' + (item.icon || "📘") + "</span>" +
      '<span class="lib-short">' + esc(b.shortTitle || b.title) + "</span></div>" +
      '<div class="lib-body">' +
        "<h2>" + esc(b.title) + "</h2>" +
        "<p>" + esc(b.subtitle) + "</p>" +
        '<div class="lib-stats">' + rows + "</div>" +
        '<div class="lib-bar" title="' + pct + '% тем готово"><span style="width:' + pct + '%"></span></div>' +
        '<div class="lib-foot"><span class="lib-modnote">' + c.mods + " модулів" + (c.done === 0 ? " · в розробці" : "") + "</span>" +
        '<span class="lib-cta">Читати →</span></div>' +
      "</div></a>";
  }

  function render() {
    var h = '<header class="lib-hero">' +
      '<div class="kicker">Бібліотека</div>' +
      "<h1>Мої книги</h1>" +
      "<p>Книги, написані під мене й зібрані просто в браузері з Markdown. " +
      "Обери книгу — і читай її повноцінно, з навігацією, фігурами й історіями.</p>" +
      "</header>";
    h += '<div class="lib-shelf">' + LIB.map(card).join("") + "</div>";
    root.innerHTML = h;
    document.title = "Бібліотека — мої книги";
  }

  if (!LIB.length) {
    root.innerHTML = '<div class="state error"><h2>Бібліотека порожня</h2>' +
      "<p>Жоден <code>manifest</code> не завантажився. Перевір <code>index.html</code> " +
      "(чи підключені manifest-файли перед <code>library.js</code>) і запусти через веб-сервер.</p></div>";
    return;
  }
  // Книга нового формату приходить як meta+modules — складаємо її через bookbuild.js;
  // legacy-книга вже має готовий it.book.
  function ensureBook(it) {
    if (it.book) return Promise.resolve(it.book);
    if (it.modules && window.assembleBook) {
      return assembleBook(it.meta, it.modules, it.meta && it.meta.basePath)
        .then(function (b) { it.book = b; return b; })
        .catch(function () { it.book = {}; return it.book; });
    }
    it.book = {}; return Promise.resolve(it.book);
  }
  Promise.all(LIB.map(ensureBook)).then(function () {
    LIB.forEach(function (it) { it.chap = chapterCounts(it.book || {}); });
    return Promise.all(LIB.map(loadBookStats));
  }).then(render).catch(render);
})();
