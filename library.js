/* ============================================================================
   library.js — стартова сторінка-«бібліотека» з ДВОМА підвкладками:
   📚 Книги — предметні книги book/<subject> (теорія за галузями);
   🎓 Курси — guide/<course> (доріжки-посилання крізь книги).
   Реєстр — window.SUBJECT_BOOKS / window.GUIDE_COURSES (books-index.js).
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

  function loadBook(slug) {
    return fetchText("book/" + slug + "/manifest.js").then(function (src) {
      var b = manifestObj(src, "__BOOKS__");
      var topics = 0, done = 0;
      ((b && b.sections) || []).forEach(function (sec) { (sec.topics || []).forEach(function (t) { var st = t.basic && t.basic.status; if (st !== "empty") topics++; if (st === "done") done++; }); });
      return { slug: slug, title: (b && b.title) || slug, branches: ((b && b.sections) || []).length, topics: topics, done: done };
    });
  }
  function loadGuide(slug) {
    return fetchText("guide/" + slug + "/manifest.js").then(function (src) {
      var g = manifestObj(src, "__GUIDES__");
      var steps = 0;
      ((g && g.modules) || []).forEach(function (m) { (m.chapters || []).forEach(function (c) { steps += (c.steps || []).length; }); });
      return { slug: slug, title: (g && g.title) || slug, modules: ((g && g.modules) || []).length, steps: steps };
    });
  }

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
    return '<a class="lib-card lib-card-guide" href="read.html?guide=' + esc(g.slug) + '" style="--accent:#16a34a">' +
      '<div class="lib-cover"><span class="lib-ico">🎓</span><span class="lib-cover-ttl">' + esc(g.title) + '</span></div>' +
      '<div class="lib-body"><p class="lib-desc">Курс — доріжка крізь предметні книги, що веде темами по черзі й сплітає їх у навчання.</p>' +
      '<div class="lib-foot"><span class="lib-modnote">' + g.modules + ' модулів · ' + g.steps + ' кроків</span>' +
      '<span class="lib-cta">Пройти →</span></div></div></a>';
  }

  function render(books, guides) {
    var h = '<header class="lib-hero"><div class="kicker">Бібліотека</div><h1>Мої книги</h1>' +
      '<p>Предметні <b>книги</b> — теорія за галузями науки; <b>курси</b> — доріжки, що сплітають теми в навчання.</p>' +
      '<div class="lib-tabs"><button class="lib-tab active" data-tab="books">📚 Книги (' + books.length + ')</button>' +
      '<button class="lib-tab" data-tab="guides">🎓 Курси (' + guides.length + ')</button></div></header>';
    h += '<div class="lib-shelf" id="tab-books">' + books.map(bookCard).join("") + '</div>';
    h += '<div class="lib-shelf" id="tab-guides" hidden>' + guides.map(guideCard).join("") + '</div>';
    root.innerHTML = h;
    document.title = "Бібліотека — мої книги";
    var tabs = [].slice.call(root.querySelectorAll(".lib-tab"));
    tabs.forEach(function (t) {
      t.addEventListener("click", function () {
        tabs.forEach(function (x) { x.classList.remove("active"); });
        t.classList.add("active");
        var which = t.getAttribute("data-tab");
        root.querySelector("#tab-books").hidden = (which !== "books");
        root.querySelector("#tab-guides").hidden = (which !== "guides");
      });
    });
  }

  Promise.all([Promise.all(BOOKS.map(loadBook)), Promise.all(GUIDES.map(loadGuide))])
    .then(function (r) { render(r[0], r[1]); })
    .catch(function (e) { root.innerHTML = '<div class="state error"><h2>Помилка</h2><p><code>' + esc(e && e.message) + '</code></p></div>'; });
})();
