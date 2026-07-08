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
      modules: (b.sections || b.modules || []).map(function (sec, i) {
        var tops = (sec.topics && sec.topics.length) ? sec.topics
          : (sec.chapters || []).reduce(function (a, c) { return a.concat(c.steps || []); }, []);  // v5 guide: modules→chapters→steps
        return {
          n: i + 1, slug: sec.slug, title: sec.title,
          chapters: tops.filter(function (t) { return t && t.slug; }).map(function (t, j) {
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

  /* Курс guide/<course>: впорядкована доріжка (Модуль·Розділ·Крок — нумерація з ПОРЯДКУ масивів;
     модуль без розділів — Модуль·Крок). Крок: `ref` → вказівник на book-атом; інакше → власна стаття курсу. */
  function renderGuide(g) {
    var host = document.getElementById("content"), sb = document.getElementById("sidebar");
    if (!g) { if (host) host.innerHTML = '<div class="state error">Курс не знайдено</div>'; return; }
    document.title = g.title + " — курс";
    // Дві схеми: нова (section→topics, плоско) і стара (module→chapters→steps).
    var mods = g.sections || g.modules || [];
    function chaptersOf(m) { return (m.chapters && m.chapters.length) ? m.chapters : [{ title: null, steps: m.topics || [] }]; }
    var nStep = 0, nChap = 0, hasChap = false;
    mods.forEach(function (m) { chaptersOf(m).forEach(function (c) { nStep += (c.steps || []).length; if (c.title) { nChap++; hasChap = true; } }); });

    // прочитані теми (той самий localStorage, що й у book.js; ключ = <книга|курс>/<slug>)
    var READ = (function () { try { return new Set(JSON.parse(localStorage.getItem("courses-read") || "[]")); } catch (e) { return new Set(); } })();

    // Статус «написано» для ref-кроків лежить у маніфесті книги-цілі → підвантажуємо їх,
    // будуємо карту written["<книга>/<slug>"], і аж тоді малюємо (own-кроки мають статус у самому курсі).
    var subjSet = {};
    mods.forEach(function (m) { chaptersOf(m).forEach(function (c) { (c.steps || []).forEach(function (s) {
      if (s.ref) { var sj = String(s.ref).split("/").filter(Boolean)[0]; if (sj) subjSet[sj] = 1; }
    }); }); });
    Promise.all(Object.keys(subjSet).map(function (sj) {
      return loadOne("book/" + sj + "/manifest.js", "__BOOKS__")
        .catch(function () { return loadOne("catalog/" + sj + "/manifest.js", "__BOOKS__").catch(function () { return null; }); })
        .then(function (b) { return { sj: sj, book: b }; });
    })).then(function (loaded) {
      var written = {};   // "<книга>/<slug>" → true, якщо є написана версія (basic АБО detailed = done)
      loaded.forEach(function (x) {
        if (!x.book) return;
        (x.book.sections || x.book.modules || []).forEach(function (sec) {
          (sec.topics || []).forEach(function (t) {
            if (t && t.slug && ((t.basic && t.basic.status === "done") || (t.detailed && t.detailed.status === "done"))) written[x.sj + "/" + t.slug] = true;
          });
        });
      });
      paint(written);
    });

    function isWritten(s, written) {
      if (s.ref) { var pr = String(s.ref).split("/").filter(Boolean); return !!written[pr[0] + "/" + pr[pr.length - 1]]; }
      if (s.slug) return (s.basic && s.basic.status === "done") || (s.detailed && s.detailed.status === "done");
      return false;
    }

    function paint(written) {
      // скільки написано / прочитано / усього статей (ref + власні; містки не рахуємо)
      var nWritten = 0, nArt = 0, nRead = 0;
      mods.forEach(function (m) { chaptersOf(m).forEach(function (c) { (c.steps || []).forEach(function (s) {
        if (!(s.ref || s.slug)) return;
        nArt++;
        if (isWritten(s, written)) nWritten++;
        var pr = s.ref ? String(s.ref).split("/").filter(Boolean) : null;
        var rk = pr ? (pr[0] + "/" + pr[pr.length - 1]) : (g.slug + "/" + s.slug);
        if (READ.has(rk)) nRead++;
      }); }); });

      function stepHtml(m, s, kn) {
        var w = isWritten(s, written);
        if (s.ref) {
          var pr = String(s.ref).split("/").filter(Boolean), subj = pr[0], top = pr[pr.length - 1];
          var rd = READ.has(subj + "/" + top) ? " read" : "";
          return '<li class="guide-step' + (w ? '' : ' soon') + rd + '"><a href="read.html?course=' + encodeURIComponent(g.slug) + '&book=' + encodeURIComponent(subj) + '#ch=' + encodeURIComponent(top) + '">' +
            '<span class="gs-num">' + kn + '</span><span class="gs-ico">📖</span><span class="gs-ttl">' + _esc(s.title || top) + '</span>' +
            (w ? '<span class="gs-subj">' + _esc(subj) + '</span>' : '<span class="gs-soon">незабаром</span>') + '</a></li>';
        }
        if (s.slug) {
          var rdo = READ.has(g.slug + "/" + s.slug) ? " read" : "";
          return '<li class="guide-step own' + (w ? '' : ' soon') + rdo + '"><a href="read.html?guide=' + encodeURIComponent(g.slug) + '&module=' + encodeURIComponent(m.slug) + '#ch=' + encodeURIComponent(s.slug) + '">' +
            '<span class="gs-num">' + kn + '</span><span class="gs-ico">📘</span><span class="gs-ttl">' + _esc(s.title || s.slug) + '</span>' +
            (w ? '<span class="gs-subj gs-own">стаття курсу</span>' : '<span class="gs-soon">незабаром</span>') + '</a></li>';
        }
        return '<li class="guide-step bridge"><span class="gs-num">' + kn + '</span>🔗 ' + _esc(s.title || 'місток') + '</li>';
      }

      var h = '<header class="ch-header ch-header-guide"><div class="ch-label">Курс · доріжка крізь книги</div><h1>' + _esc(g.title) + '</h1></header>' +
        '<header class="cover-hero cover-hero-guide">' +
        '<p>' + _esc(g.subtitle || "Кожен крок — або тема предметної книги, або власна стаття курсу, що спирається на пройдене.") + '</p>' +
        '<div class="cover-stats"><div class="stat"><div class="num">' + mods.length + '</div><div class="lbl">модулів</div></div>' +
        (hasChap ? '<div class="stat"><div class="num">' + nChap + '</div><div class="lbl">розділів</div></div>' : '') +
        '<div class="stat"><div class="num">' + nStep + '</div><div class="lbl">тем</div></div>' +
        '<div class="stat stat-written"><div class="num">' + nWritten + '<span class="stat-of"> / ' + nArt + '</span></div><div class="lbl">написано</div></div>' +
        '<div class="stat"><div class="num">' + nRead + '</div><div class="lbl">прочитано</div></div>' +
        '</div></header><div class="toc guide-toc">';
      mods.forEach(function (m, mi) {
        var mn = mi + 1;
        h += '<div class="module-block" id="gm-' + mn + '"><div class="module-head"><span class="m-num">Модуль ' + mn +
          '</span><span class="m-ttl">' + _esc(m.title) + '</span></div>';
        chaptersOf(m).forEach(function (c, ci) {
          var cn = mn + "." + (ci + 1);   // нумерація Модуль·Розділ·Крок — розділ і крок з позиції в маніфесті
          if (c.title) h += '<div class="guide-chap-head"><span class="gc-num">' + cn + '</span><span class="gc-ttl">' + _esc(c.title) + '</span></div>';
          h += '<ol class="guide-steps">';
          (c.steps || []).forEach(function (s, si) { h += stepHtml(m, s, (c.title ? cn : mn) + "." + (si + 1)); });
          h += '</ol>';
        });
        h += '</div>';
      });
      if (host) host.innerHTML = h + '</div>';
      if (sb) {
        // згортувані панелі модулів (як у книгах); стан — той самий localStorage, що й у book.js
        var COL = (function () { try { return new Set(JSON.parse(localStorage.getItem("courses-collapsed") || "[]")); } catch (e) { return new Set(); } })();
        var s = '<a class="sb-home" href="index.html">← Бібліотека (усі книги)</a>' +
          '<a class="sb-logo" href="#"><span class="sb-logo-kicker">Курс</span><span class="sb-logo-title">' + _esc(g.title) + '</span></a>';
        mods.forEach(function (m, mi) {
          var mn = mi + 1;
          s += '<div class="sb-group-label' + (COL.has(m.title) ? ' collapsed' : '') + '" data-collapse-group="' + _esc(m.title) + '">' +
            '<span class="sb-caret" aria-hidden="true">▾</span><span class="sb-gl-txt">Модуль ' + mn + ' · ' + _esc(m.title) + '</span></div><div class="sb-group">';
          var k = 0;
          chaptersOf(m).forEach(function (c) {
            (c.steps || []).forEach(function (st) {
              k++;
              var kn = mn + '.' + k, w = isWritten(st, written);
              if (st.ref) {
                var pr = String(st.ref).split('/').filter(Boolean), subj = pr[0], top = pr[pr.length - 1];
                s += '<a class="sb-link' + (w ? '' : ' soon') + (READ.has(subj + '/' + top) ? ' read' : '') + '" href="read.html?course=' + encodeURIComponent(g.slug) +
                  '&book=' + encodeURIComponent(subj) + '#ch=' + encodeURIComponent(top) + '"><span class="sb-kn">' + kn + '</span>' + _esc(st.title || top) + '</a>';
              } else if (st.slug) {
                s += '<a class="sb-link' + (w ? '' : ' soon') + (READ.has(g.slug + '/' + st.slug) ? ' read' : '') + '" href="read.html?guide=' + encodeURIComponent(g.slug) +
                  '&module=' + encodeURIComponent(m.slug || '') + '#ch=' + encodeURIComponent(st.slug) + '"><span class="sb-kn">' + kn + '</span>' + _esc(st.title || st.slug) + '</a>';
              } else {
                s += '<span class="sb-link sb-bridge"><span class="sb-kn">' + kn + '</span>🔗 ' + _esc(st.title || 'місток') + '</span>';
              }
            });
          });
          s += '</div>';
        });
        sb.innerHTML = s;
        sb.addEventListener('click', function (e) {
          var cg = e.target.closest && e.target.closest('[data-collapse-group]');
          if (!cg) return;
          var key = cg.getAttribute('data-collapse-group');
          if (COL.has(key)) COL.delete(key); else COL.add(key);
          cg.classList.toggle('collapsed', COL.has(key));
          try { localStorage.setItem('courses-collapsed', JSON.stringify(Array.from(COL))); } catch (err) {}
        });
        // меню-кнопка (☰) + scrim + ✕ на вузькому екрані: book.js на лендингу курсу НЕ вантажиться, тож вішаємо тут
        var menuBtn = document.getElementById("menu-btn"), scrim = document.getElementById("scrim"), closeBtn = document.getElementById("sidebar-close");
        if (menuBtn) menuBtn.onclick = function () { sb.classList.toggle("open"); };
        if (scrim) scrim.onclick = function () { sb.classList.remove("open"); };
        if (closeBtn) closeBtn.onclick = function () { sb.classList.remove("open"); };
      }
    }
  }

  global.adaptSubjectBook = adaptSubjectBook;
  global.loadSubjectBook = loadSubjectBook;
  global.loadGuide = loadGuide;
  global.renderGuide = renderGuide;
})(window);
