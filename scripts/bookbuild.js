/* ============================================================================
   bookbuild.js (v5) — адаптер маніфестів у формат рушія (book.js).
   Тільки нова структура: book/<subject> та guide/<course> (схема AUTHORING §2 v4),
   читач — read.html?book=<id> / ?guide=<course>. Легасі per-module прибрано (v5).
   ========================================================================== */
(function (global) {
  "use strict";

  function fetchText(url) {
    return fetch(url, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status + " — " + url);
      return r.text();
    });
  }
  function _esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function loadOne(path, key) {
    return fetchText(path).then(function (src) { var sb = {}; try { new Function("window", src)(sb); } catch (e) {} return (sb[key] || [])[0] || null; });
  }

  var SUBJECT_ACCENT = { physics: "#6b5b95", math: "#3a6b9c", chemistry: "#3a8f80", electronics: "#b06a5a", programming: "#5a5f9c", communications: "#4a8296", algorithms: "#a5648a", philosophy: "#9a7b4f" };

  /* book/<subject> або guide/<course> (та сама схема §2 v4) → формат рушія BOOK.
     Версія доступна читачу ⟺ її статус "done" (basic → chapter.status; detailed → chapter.full).
     Крок-`ref` у guide не має slug → відсіюємо (це не стаття, а вказівник; рендериться окремо в renderGuide). */
  function adaptSubjectBook(b, dir) {
    if (!b) return null;
    dir = dir || "book/";
    return {
      title: b.title, shortTitle: b.title, subtitle: b.subtitle || "", libraryHref: "index.html",
      basePath: dir + b.slug + "/", type: b.type || "book", bookSlug: b.slug, accent: SUBJECT_ACCENT[b.slug] || "#1d6fa4",
      modules: (b.sections || []).map(function (sec, i) {
        return {
          n: i + 1, slug: sec.slug, title: sec.title,
          chapters: (sec.topics || []).filter(function (t) { return t && t.slug; }).map(function (t, j) {
            var files = function (a) { return (a || []).map(function (o) { return typeof o === "string" ? o : o.file; }); };
            return {
              n: j + 1, title: t.title, status: (t.basic && t.basic.status) || "empty",
              dir: sec.slug + "/" + t.slug, main: t.slug + ".md",
              full: !!(t.detailed && t.detailed.status === "done"),   // існує повна -d.md версія
              histories: files(t.hist),                               // 📜 → попапи
              extras: files(t.comp).concat(files(t.math), files(t.proj)) // 🔌🧮⚙️ → попапи
            };
          })
        };
      })
    };
  }
  function loadSubjectBook(slug) {
    return loadOne("book/" + slug + "/manifest.js", "__BOOKS__")
      .then(function (b) { return adaptSubjectBook(b, "book/"); })
      .catch(function () { return loadOne("catalog/" + slug + "/manifest.js", "__BOOKS__").then(function (b) { return adaptSubjectBook(b, "catalog/"); }); })
      .catch(function () { return null; });
  }
  function loadGuide(slug) { return loadOne("guide/" + slug + "/manifest.js", "__GUIDES__"); }

  /* Курс guide/<course>: впорядкована доріжка (Модуль i · крок i.j — нумерація з ПОРЯДКУ масивів).
     section = модуль; topic = крок: `ref` → вказівник на book-атом; інакше → власна стаття курсу. */
  function renderGuide(g) {
    var host = document.getElementById("content"), sb = document.getElementById("sidebar");
    if (!g) { if (host) host.innerHTML = '<div class="state error">Курс не знайдено</div>'; return; }
    document.title = g.title + " — курс";
    var mods = g.sections || [], nStep = 0;
    mods.forEach(function (m) { nStep += ((m.topics) || []).length; });
    var h = '<header class="cover-hero"><div class="kicker">Курс · доріжка крізь книги</div><h1>' + _esc(g.title) + '</h1>' +
      '<p>' + _esc(g.subtitle || "Кожен крок — або тема предметної книги, або власна стаття курсу, що спирається на пройдене.") + '</p>' +
      '<div class="cover-stats"><div class="stat"><div class="num">' + mods.length + '</div><div class="lbl">модулів</div></div>' +
      '<div class="stat"><div class="num">' + nStep + '</div><div class="lbl">кроків</div></div></div></header><div class="toc guide-toc">';
    mods.forEach(function (m, mi) {
      var mn = mi + 1;
      h += '<div class="module-block" id="gm-' + mn + '"><div class="module-head"><span class="m-num">Модуль ' + mn +
        '</span><span class="m-ttl">' + _esc(m.title) + '</span></div><ol class="guide-steps">';
      (m.topics || []).forEach(function (s, si) {
        var kn = mn + "." + (si + 1);
        if (s.ref) {
          var pr = String(s.ref).split("/").filter(Boolean), subj = pr[0], top = pr[pr.length - 1];
          h += '<li class="guide-step"><a href="read.html?course=' + encodeURIComponent(g.slug) + '&book=' + encodeURIComponent(subj) + '#ch=' + encodeURIComponent(top) + '">' +
            '<span class="gs-num">' + kn + '</span><span class="gs-ico">📖</span><span class="gs-ttl">' + _esc(s.title || top) +
            '</span><span class="gs-subj">' + _esc(subj) + '</span></a></li>';
        } else {
          var avail = !!(s.basic && s.basic.status === "done");
          h += '<li class="guide-step own' + (avail ? '' : ' stub') + '"><a href="read.html?guide=' + encodeURIComponent(g.slug) + '&module=' + encodeURIComponent(m.slug) + '#ch=' + encodeURIComponent(s.slug) + '">' +
            '<span class="gs-num">' + kn + '</span><span class="gs-ico">📘</span><span class="gs-ttl">' + _esc(s.title || s.slug) +
            '</span><span class="gs-subj">' + (avail ? 'стаття курсу' : 'у роботі') + '</span></a></li>';
        }
      });
      h += '</ol></div>';
    });
    if (host) host.innerHTML = h + '</div>';
    if (sb) {
      var s = '<a class="sb-home" href="index.html">← Бібліотека (усі книги)</a>' +
        '<a class="sb-logo" href="#"><span class="sb-logo-kicker">Курс</span><span class="sb-logo-title">' + _esc(g.title) + '</span></a>';
      mods.forEach(function (m, mi) {
        var mn = mi + 1;
        s += '<a class="sb-link sb-mod" href="#gm-' + mn + '">Модуль ' + mn + ' · ' + _esc(m.title) + '</a>';
      });
      sb.innerHTML = s;
    }
  }

  global.adaptSubjectBook = adaptSubjectBook;
  global.loadSubjectBook = loadSubjectBook;
  global.loadGuide = loadGuide;
  global.renderGuide = renderGuide;
})(window);
