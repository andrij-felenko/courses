/* ============================================================================
   library.js — стартова сторінка-«бібліотека» зі списком книг.
   Читає window.LIBRARY (масив {id, entry, accent, icon, book}), де book —
   це той самий об'єкт window.BOOK із відповідного manifest.

   Статистику тем/спец-тем рахуємо ЖИВЦЕМ із _status.md кожного модуля
   (basePath + module.slug + "/_status.md") — їх веде /loop, тож числа завжди
   актуальні й нічого не треба дублювати в маніфест.
     • тема          — рядок «- <статус> 2.1.3 Назва» (номер М.Р.Т)
     • спец-тема      — рядок «- <статус> 📜/🧮/🔌/⚙️ …» (вставка до теми)
     • готова         — статус 🟢 (🔄 написано-але-в-редактурі НЕ рахуємо як готову)
   ========================================================================== */
(function () {
  "use strict";
  var LIB = window.LIBRARY || [];
  var root = document.getElementById("library-root");
  if (!root) return;

  function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  /* ── розбір одного _status.md ───────────────────────────────────────── */
  var SPECIAL = ["📜", "🧮", "🔌", "⚙️", "⚙"];
  function parseStatus(text) {
    var s = { topics: 0, topicsDone: 0, spec: 0, specDone: 0 };
    var lines = String(text).split(/\r?\n/);
    for (var i = 0; i < lines.length; i++) {
      var m = lines[i].match(/^\s*-\s*(🟢|🔄|🟡|⬜)\s+(.*)$/u);
      if (!m) continue;
      var done = m[1] === "🟢";
      var c = m[2];
      var isSpec = false;
      for (var k = 0; k < SPECIAL.length; k++) { if (c.indexOf(SPECIAL[k]) === 0) { isSpec = true; break; } }
      if (isSpec) { s.spec++; if (done) s.specDone++; }
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

  /* завантажити й скласти статистику тем по всіх модулях книги */
  function loadBookStats(item) {
    var b = item.book || {};
    item.chap = chapterCounts(b);
    var urls = (b.modules || []).map(function (m) { return (b.basePath || "") + m.slug + "/_status.md"; });
    return Promise.all(urls.map(fetchText)).then(function (texts) {
      var agg = { topics: 0, topicsDone: 0, spec: 0, specDone: 0 };
      texts.forEach(function (t) { var r = parseStatus(t); agg.topics += r.topics; agg.topicsDone += r.topicsDone; agg.spec += r.spec; agg.specDone += r.specDone; });
      item.topics = agg;
    });
  }

  /* ── рендер ─────────────────────────────────────────────────────────── */
  function statRow(label, done, total) {
    return '<div class="lib-stat-row"><span class="lib-stat-k">' + label + "</span>" +
      '<span class="lib-stat-v"><b>' + done + "</b> / " + total + "</span></div>";
  }

  function card(item) {
    var b = item.book || {};
    var c = item.chap || { done: 0, total: 0, mods: 0 };
    var t = item.topics || { topics: 0, topicsDone: 0, spec: 0, specDone: 0 };
    var pct = t.topics ? Math.round(t.topicsDone / t.topics * 100) : (c.total ? Math.round(c.done / c.total * 100) : 0);
    var rows = statRow("Розділи", c.done, c.total) + statRow("Теми", t.topicsDone, t.topics);
    if (t.spec > 0) rows += statRow("Спец. теми", t.specDone, t.spec);
    return '<a class="lib-card" href="' + esc(item.entry) + '" style="--accent:' + esc(item.accent || "#1d6fa4") + '">' +
      '<div class="lib-cover"><span class="lib-ico">' + (item.icon || "📘") + "</span>" +
      '<span class="lib-short">' + esc(b.shortTitle || b.title) + "</span></div>" +
      '<div class="lib-body">' +
        "<h2>" + esc(b.title) + "</h2>" +
        "<p>" + esc(b.subtitle) + "</p>" +
        '<div class="lib-stats">' + rows + "</div>" +
        '<div class="lib-bar" title="' + pct + '% тем готово"><span style="width:' + pct + '%"></span></div>' +
        '<div class="lib-foot"><span class="lib-modnote">' + c.mods + " модулів</span>" +
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
  // спершу показуємо все, що знаємо з маніфесту; теми підтягуємо з _status.md і дорендеровуємо
  LIB.forEach(function (it) { it.chap = chapterCounts(it.book || {}); });
  Promise.all(LIB.map(loadBookStats)).then(render).catch(render);
})();
