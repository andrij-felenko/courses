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

  var SUBJECT_ACCENT = { physics: "#6b5b95", math: "#3a6b9c", chemistry: "#3a8f80", electronics: "#b06a5a", programming: "#5a5f9c", communications: "#4a8296", algorithms: "#a5648a", philosophy: "#9a7b4f",
    "unix-linux": "#3f6b8a", "cpp-standards": "#6b4f8a", "build-systems": "#8a6a3f" };
  // Книгоподібні види живуть у різних теках, але в ОДНОМУ реєстрі __BOOKS__ і відкриваються як ?book=<slug>.
  var BOOKLIKE_DIRS = ["book/", "catalog/", "reference/"];
  function loadBooklike(slug, i) {
    i = i || 0;
    if (i >= BOOKLIKE_DIRS.length) return Promise.resolve(null);
    return loadOne(BOOKLIKE_DIRS[i] + slug + "/manifest.js", "__BOOKS__")
      .then(function (b) { return b ? { book: b, dir: BOOKLIKE_DIRS[i] } : loadBooklike(slug, i + 1); })
      .catch(function () { return loadBooklike(slug, i + 1); });
  }

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
              full: !!(t.detailed && t.detailed.status === "done"),   // існує повна -d.md версія (done)
              dstatus: (t.detailed && t.detailed.status) || "empty",  // статус детальної (для single-link fallback)
              histories: files(t.hist),                               // 📜 → попапи
              extras: files(t.comp).concat(files(t.math), files(t.proj), files(t.api)) // 🔌🧮⚙️📋 → попапи
            };
          })
        };
      })
    };
  }
  function loadSubjectBook(slug) {
    return loadBooklike(slug).then(function (r) { return r ? adaptSubjectBook(r.book, r.dir) : null; })
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
      return loadBooklike(sj).then(function (r) { return { sj: sj, book: r && r.book }; });
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

  /* ── Затиснути (або правий клік) лінк статті → попап «позначити прочитано/непрочитано».
     Спільний для читача й лендингу курсу (book.js не потрібен). Ключ виводиться з href;
     book.js тримає свій READ-набір у синхроні через подію "courses-read-change". ── */
  (function () {
    var LS = "courses-read";
    function rset() { try { return new Set(JSON.parse(localStorage.getItem(LS) || "[]")); } catch (e) { return new Set(); } }
    function keyFromHref(href) {
      if (!href) return null;
      var m = href.match(/#ch=([^&]+)/); if (!m) return null;
      var slug = decodeURIComponent(m[1]);
      var bm = href.match(/[?&]book=([^&#]+)/); if (bm) return decodeURIComponent(bm[1]) + "/" + slug;   // і course-лінки: книга-джерело
      var gm = href.match(/[?&]guide=([^&#]+)/); if (gm) return decodeURIComponent(gm[1]) + "/" + slug;  // власна стаття курсу
      var B = global.BOOK;   // короткий "#ch=…" — контекст поточної книги (читач)
      return B ? ((B.bookSlug || B.type || "book") + "/" + slug) : null;
    }
    function applyDom(key, on) {
      [].forEach.call(document.querySelectorAll("a[href]"), function (a) {
        if (keyFromHref(a.getAttribute("href")) !== key) return;
        if (a.classList.contains("sb-link")) a.classList.toggle("read", on);
        var it = a.closest ? a.closest(".ch-item") : null; if (it) it.classList.toggle("read", on);
        var gs = a.closest ? a.closest(".guide-step") : null; if (gs) gs.classList.toggle("read", on);
      });
    }
    function toggle(key) {
      var set = rset(), on = !set.has(key);
      if (on) set.add(key); else set.delete(key);
      try { localStorage.setItem(LS, JSON.stringify(Array.from(set))); } catch (e) {}
      applyDom(key, on);
      try { window.dispatchEvent(new CustomEvent("courses-read-change", { detail: { key: key, on: on } })); } catch (e) {}
    }
    var pop = null, timer = null, suppress = false;
    function close() { if (pop) { pop.remove(); pop = null; } }
    function show(x, y, key) {
      close();
      var on = rset().has(key);
      pop = document.createElement("div"); pop.className = "read-pop";
      var b = document.createElement("button"); b.type = "button";
      b.textContent = on ? "✕ Зняти позначку «прочитано»" : "✓ Позначити прочитаною";
      b.addEventListener("click", function (e) { e.preventDefault(); e.stopPropagation(); toggle(key); close(); });
      pop.appendChild(b); document.body.appendChild(pop);
      var r = pop.getBoundingClientRect();
      pop.style.left = Math.max(8, Math.min(x, window.innerWidth - r.width - 8)) + "px";
      pop.style.top = Math.max(8, Math.min(y, window.innerHeight - r.height - 8)) + "px";
    }
    document.addEventListener("pointerdown", function (e) {
      if (pop && pop.contains(e.target)) return;   // тап по самому попапу — не закривати до кліку
      close();
      var a = e.target.closest && e.target.closest("a[href]");
      var key = a ? keyFromHref(a.getAttribute("href")) : null;
      if (!key) return;
      var x = e.clientX, y = e.clientY;
      function fin() { if (timer) { clearTimeout(timer); timer = null; } document.removeEventListener("pointerup", fin); document.removeEventListener("pointercancel", fin); document.removeEventListener("pointermove", mv); }
      function mv(ev) { if (Math.abs(ev.clientX - x) > 8 || Math.abs(ev.clientY - y) > 8) fin(); }   // потягнув — це скрол, не затискання
      timer = setTimeout(function () { timer = null; suppress = true; show(x, y, key); fin(); }, 550);
      document.addEventListener("pointerup", fin);
      document.addEventListener("pointercancel", fin);
      document.addEventListener("pointermove", mv);
    });
    // клік одразу ПІСЛЯ спрацьованого затискання — це відпускання пальця, не перехід за лінком
    document.addEventListener("click", function (e) {
      if (suppress) { suppress = false; e.preventDefault(); e.stopPropagation(); return; }
      if (pop && !pop.contains(e.target)) close();
    }, true);
    // правий клік (десктоп) і довгий тап Android теж ведуть сюди
    document.addEventListener("contextmenu", function (e) {
      var a = e.target.closest && e.target.closest("a[href]");
      var key = a ? keyFromHref(a.getAttribute("href")) : null;
      if (!key) return;
      e.preventDefault();
      if (timer) { clearTimeout(timer); timer = null; }
      show(e.clientX, e.clientY, key);
    });
    window.addEventListener("scroll", close, { passive: true });
  })();

  global.adaptSubjectBook = adaptSubjectBook;
  global.loadSubjectBook = loadSubjectBook;
  global.loadGuide = loadGuide;
  global.renderGuide = renderGuide;
})(window);
