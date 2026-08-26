/* ============================================================================
   bookbuild.js (v7) — адаптер дерева root/ у формат рушія (book.js).

   Дерево v7:
     root/shelf.json                    види: sci · eng · course · hw · sys
     root/<dir>/<book>/manifest.json    { schema:7, kind, slug, title, groups:[…] }
     root/<dir>/<book>/<group>.json     { …, chapters:[ {slug,title,topics:[…]} ] }
                                        необов'язкове megachapters:[{title,chapters:[слуг…]}]
                                        — НАКЛАДКА на показ; правда лишається в chapters[],
                                        адреса й нумерація від неї не залежать. Поки не читаємо.
     root/<dir>/<book>/<topic>/<topic>.md        базова
     root/<dir>/<book>/<topic>/<topic>-d.md      детальна
     root/<dir>/<book>/<topic>/<type>-<name>.md  вставки
     root/<dir>/<book>/<topic>/img/*.svg         фігури

   Теми лежать ПЛАСКО під книгою — групи й розділи логічні, тек під них нема.
   Група зі слугом "." зберігається у файлі "_.json" (книга без поділу на групи).

   Адреса теми (канон v7): коротка `<book>/<topic>` — вона ж ключ прогресу читання
   в localStorage і вона ж `ref` у курсах. Слуг книги глобально унікальний, тож вид
   (kind) знаходиться через shelf.json, а не пишеться в адресі.
   ========================================================================== */
(function (global) {
  "use strict";

  /* Префікс розгортання. Рушій живе в src/front/: на проді deploy кладе його в корінь
     сайту (_site = src/front/* + root/), а локально він лишається в підтеці — тож якщо
     шлях сторінки закінчується на src/front/, зрізаємо його. Обидва режими дають той
     самий корінь, і «root/…» резолвиться однаково. */
  var SITE_ROOT = location.pathname.replace(/[^/]*$/, "").replace(/(?:^|\/)src\/front\/$/, "/");
  var CONTENT = SITE_ROOT + "root/";   // корінь дерева контенту

  function fetchText(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status + " — " + url);
      return r.text();
    });
  }
  function fetchJSON(url) { return fetchText(url).then(JSON.parse); }
  function _esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  /* Написано ⟺ файл існує. done | update | deeper | recheck — усе це наявний текст
     (три останні лише позначаються чернеткою). pending/empty — тексту нема. */
  function _written(s) { return s === "done" || s === "update" || s === "deeper" || s === "recheck"; }

  var ACCENT = {
    physics: "#6b5b95", math: "#3a6b9c", chemistry: "#3a8f80", electronics: "#b06a5a",
    programming: "#5a5f9c", communications: "#4a8296", algorithms: "#a5648a", philosophy: "#9a7b4f",
    "unix-linux": "#3f6b8a", "cpp-standards": "#6b4f8a", "build-systems": "#8a6a3f"
  };
  var KIND_ACCENT = { sci: "#3a6b9c", eng: "#b06a5a", course: "#1d6fa4", hw: "#16a34a", sys: "#6b4f8a" };
  /* Родовий відмінок від words.book — для підпису «стаття <чого>». Українська відміна
     неправильна, тож тримаємо готові форми, а не доклеюємо закінчення. */
  var KIND_OF = { sci: "науки", eng: "напрямку", course: "курсу", hw: "класу", sys: "системи" };

  /* ── shelf.json: реєстр видів і книг (вантажиться раз на сторінку) ───────── */
  var _shelfP = null;
  function loadShelf() {
    if (!_shelfP) _shelfP = fetchJSON(CONTENT + "shelf.json").catch(function () { return null; });
    return _shelfP;
  }

  /* Слуг книги → її вид. Слуг унікальний по всьому дереву, тож шукаємо в усіх видах. */
  function kindOf(shelf, bookSlug) {
    var ks = (shelf && shelf.kinds) || [];
    for (var i = 0; i < ks.length; i++) {
      if ((ks[i].books || []).indexOf(bookSlug) !== -1) return ks[i];
    }
    return null;
  }

  function groupFile(g) { return (g === "." ? "_" : g) + ".json"; }

  /* ── Книга v7 → формат рушія BOOK ────────────────────────────────────────
     modules  ← групи; chapters ← теми групи (розділи сплющуються, назва розділу
     лишається на темі полем `chap`, щоб сайдбар міг показати підзаголовок).
     Крок-`ref` не має slug — у рушій не йде (це вказівник, його малює renderGuide). */
  function adapt(man, groups, kindInfo, base) {
    var files = function (a) { return (a || []).map(function (o) { return typeof o === "string" ? o : o.file; }); };
    return {
      title: man.title,
      shortTitle: man.title,
      subtitle: man.subtitle || "",
      libraryHref: "index.html",
      basePath: base,                       // "root/course/embedded/"
      type: man.kind,                       // sci | eng | course | hw | sys
      kind: man.kind,
      words: (kindInfo && kindInfo.words) || {},
      shelf: (kindInfo && kindInfo.shelf) || "",
      bookSlug: man.slug,
      accent: ACCENT[man.slug] || KIND_ACCENT[man.kind] || "#1d6fa4",
      groups: groups,                       // сирі групи — для лендингу курсу (renderGuide)
      modules: groups.map(function (g, i) {
        var tops = [];
        (g.chapters || []).forEach(function (c) {
          (c.topics || []).forEach(function (t) { if (t) tops.push({ t: t, chap: c.title }); });
        });
        return {
          n: i + 1, slug: g.slug, title: g.title,
          chapters: tops.filter(function (x) { return x.t.slug; }).map(function (x, j) {
            var t = x.t;
            return {
              n: j + 1, title: t.title, chap: x.chap,
              status: (t.basic && t.basic.status) || "empty",
              dir: t.slug,                                        // теми пласко під книгою
              main: t.slug + ".md",
              full: !!(t.detailed && _written(t.detailed.status)),
              dstatus: (t.detailed && t.detailed.status) || "empty",
              histories: files(t.hist),
              extras: files(t.comp).concat(files(t.math), files(t.proj), files(t.api))
            };
          })
        };
      })
    };
  }

  /* Книга за слугом: shelf → manifest.json → усі <group>.json → формат рушія. */
  var _bookCache = {};
  function loadBook(slug) {
    if (!slug) return Promise.resolve(null);
    if (_bookCache[slug]) return _bookCache[slug];
    _bookCache[slug] = loadShelf().then(function (sh) {
      var k = kindOf(sh, slug);
      if (!k) return null;                                    // книга ще не переїхала в root/
      var base = CONTENT + k.dir + "/" + slug + "/";
      return fetchJSON(base + "manifest.json").then(function (man) {
        var gs = man.groups || [];
        return Promise.all(gs.map(function (g) {
          return fetchJSON(base + groupFile(g)).catch(function () { return null; });
        })).then(function (loaded) { return adapt(man, loaded.filter(Boolean), k, base); });
      });
    }).catch(function () { return null; });
    return _bookCache[slug];
  }

  /* ── Лендинг курсу: впорядкована доріжка (Група·Розділ·Крок за порядком у маніфесті).
     Крок `ref` → вказівник на тему іншої книги; крок `slug` → власна стаття курсу. ── */
  /* Бейдж кроку називає книгу, з якої взято тему. Слуг (`math-numeric`) читачеві
     нічого не каже, тож ставимо українську назву, а коли книга входить у збірку —
     «Збірка: Книга» через двокрапку. Назва лежить у manifest.json книги, а збірка —
     у shelf.json; тягнемо лише ті книги, на які курс справді посилається, і лише раз. */
  var _nameCache = {};
  function fillBookNames(host) {
    var badges = [].slice.call(host.querySelectorAll(".gs-subj[data-book]"));
    if (!badges.length) return;
    var want = {};
    badges.forEach(function (e) { want[e.getAttribute("data-book")] = 1; });
    loadShelf().then(function (sh) {
      var inGroup = {}, dirOf = {};
      ((sh && sh.kinds) || []).forEach(function (k) {
        (k.books || []).forEach(function (s) { dirOf[s] = k.dir; });
        (k.groups || []).forEach(function (g) { (g.books || []).forEach(function (s) { inGroup[s] = g.title; }); });
      });
      return Promise.all(Object.keys(want).map(function (slug) {
        if (_nameCache[slug]) return null;
        if (!dirOf[slug]) { _nameCache[slug] = slug; return null; }   // книга ще не переїхала — лишаємо слуг
        return fetchJSON(CONTENT + dirOf[slug] + "/" + slug + "/manifest.json")
          .then(function (m) { _nameCache[slug] = (inGroup[slug] ? inGroup[slug] + ": " : "") + (m.title || slug); })
          .catch(function () { _nameCache[slug] = slug; });
      }));
    }).then(function () {
      badges.forEach(function (e) {
        var n = _nameCache[e.getAttribute("data-book")];
        if (n) { e.textContent = n; e.title = e.getAttribute("data-book"); }
      });
    }).catch(function () {});
  }

  function renderGuide(b) {
    var host = document.getElementById("content"), sb = document.getElementById("sidebar");
    if (!b) { if (host) host.innerHTML = '<div class="state error">Курс не знайдено</div>'; return; }
    var W = b.words || {};
    document.title = b.title + " — " + (W.book || "курс");
    var mods = b.groups || [];
    var nStep = 0, nChap = 0, hasChap = false;
    mods.forEach(function (m) {
      (m.chapters || []).forEach(function (c) {
        nStep += (c.topics || []).length;
        if (c.title) { nChap++; hasChap = true; }
      });
    });

    var READ = (function () { try { return new Set(JSON.parse(localStorage.getItem("courses-read") || "[]")); } catch (e) { return new Set(); } })();

    // Статус «написано» для ref-кроків лежить у книзі-цілі → підвантажуємо ці книги
    // й будуємо карту written["<book>/<topic>"]. Книга, що ще не в root/, дасть null —
    // її кроки лишаться «незабаром», без помилки.
    var want = {};
    mods.forEach(function (m) { (m.chapters || []).forEach(function (c) { (c.topics || []).forEach(function (s) {
      if (s && s.ref) { var pr = String(s.ref).split("/").filter(Boolean); if (pr[0]) want[pr[0]] = 1; }
    }); }); });
    Promise.all(Object.keys(want).map(loadBook)).then(function (loaded) {
      var written = {};
      loaded.forEach(function (tb) {
        if (!tb) return;
        (tb.modules || []).forEach(function (mo) {
          (mo.chapters || []).forEach(function (ch) {
            if (_written(ch.status) || ch.full) written[tb.bookSlug + "/" + ch.dir] = true;
          });
        });
      });
      paint(written);
    });

    function refKey(s) { var pr = String(s.ref).split("/").filter(Boolean); return pr[0] + "/" + pr[pr.length - 1]; }
    function isWritten(s, written) {
      if (s.ref) return !!written[refKey(s)];
      if (s.slug) return (s.basic && _written(s.basic.status)) || (s.detailed && _written(s.detailed.status));
      return false;
    }

    /* ── ТОМ = КНИГА КУРСУ ────────────────────────────────────────────────
       Той самий рівень, що збірка в бібліотеці: курс показує СПИСОК томів, том
       відкриває свою доріжку. Доти курс вивалював усі кроки одним полотном —
       у `embedded` це 2411 рядків на сторінку, де жоден том не видно як ціле.
       Рівень тримає адреса: «#vol=<слуг>»; без неї — список. */
    function curVol() {
      var m = /(?:^|[#&])vol=([^&]+)/.exec(location.hash || "");
      return m ? decodeURIComponent(m[1]) : "";
    }
    function volSlug(m, mi) { return m.slug || String(mi + 1); }
    function volStats(m, written) {
      var st = { chap: 0, steps: 0, wr: 0, rd: 0 };
      (m.chapters || []).forEach(function (c) {
        if (c.title) st.chap++;
        (c.topics || []).forEach(function (s) {
          if (!(s.ref || s.slug)) return;
          st.steps++;
          if (isWritten(s, written)) st.wr++;
          if (READ.has(s.ref ? refKey(s) : (b.bookSlug + "/" + s.slug))) st.rd++;
        });
      });
      return st;
    }
    function volCard(m, mi, written) {
      var st = volStats(m, written), pct = st.steps ? Math.round(st.wr / st.steps * 100) : 0;
      /* Опис тому — його ж розділи: власного тексту в томі немає, а перелік
         розділів каже про зміст точніше за будь-який підсумок. */
      var chaps = (m.chapters || []).map(function (c) { return c.title; }).filter(Boolean);
      return '<a class="lib-card lib-card-course" href="#vol=' + encodeURIComponent(volSlug(m, mi)) +
        '" style="--accent:' + (b.accent || "#1d6fa4") + ';--p:' + pct + '">' +
        '<span class="lc-fill" aria-hidden="true"></span>' +
        '<div class="lc-head"><h3 class="lc-ttl">' + _esc(m.title) + '</h3>' +
        '<span class="lc-ico" aria-hidden="true">' + (mi + 1) + '</span></div>' +
        '<p class="lc-desc">' + _esc(chaps.join(" · ")) + '</p>' +
        '<div class="lc-foot"><span class="lc-left">' + (st.chap ? "розділів " + st.chap + " · " : "") +
        "тем " + st.steps + '</span>' +
        '<span class="lc-right">' + st.wr + ' / ' + st.steps + '<i>написано</i></span></div>' +
        '<div class="lc-read"><span class="lc-read-track"><i style="width:' +
        (st.steps ? Math.round(st.rd / st.steps * 100) : 0) + '%"></i></span>' +
        '<span class="lc-read-num">' + st.rd + ' / ' + st.steps + ' прочитано</span></div></a>';
    }


    function paint(written) {
      var nWritten = 0, nArt = 0, nRead = 0;
      mods.forEach(function (m) { (m.chapters || []).forEach(function (c) { (c.topics || []).forEach(function (s) {
        if (!(s.ref || s.slug)) return;
        nArt++;
        if (isWritten(s, written)) nWritten++;
        var rk = s.ref ? refKey(s) : (b.bookSlug + "/" + s.slug);
        if (READ.has(rk)) nRead++;
      }); }); });

      function stepHtml(s, kn) {
        var w = isWritten(s, written);
        if (s.ref) {
          var pr = String(s.ref).split("/").filter(Boolean), bk = pr[0], top = pr[pr.length - 1];
          var rd = READ.has(bk + "/" + top) ? " read" : "";
          return '<li class="guide-step' + (w ? '' : ' soon') + rd + '"><a href="read.html?course=' + encodeURIComponent(b.bookSlug) + '&book=' + encodeURIComponent(bk) + '#ch=' + encodeURIComponent(top) + '">' +
            '<span class="gs-num">' + kn + '</span><span class="gs-ico">📖</span><span class="gs-ttl">' + _esc(s.title || top) + '</span>' +
            (w ? '<span class="gs-subj" data-book="' + _esc(bk) + '">' + _esc(bk) + '</span>' : '<span class="gs-soon">незабаром</span>') + '</a></li>';
        }
        if (s.slug) {
          var rdo = READ.has(b.bookSlug + "/" + s.slug) ? " read" : "";
          return '<li class="guide-step own' + (w ? '' : ' soon') + rdo + '"><a href="read.html?book=' + encodeURIComponent(b.bookSlug) + '#ch=' + encodeURIComponent(s.slug) + '">' +
            '<span class="gs-num">' + kn + '</span><span class="gs-ico">📘</span><span class="gs-ttl">' + _esc(s.title || s.slug) + '</span>' +
            (w ? '<span class="gs-subj gs-own">стаття ' + _esc(KIND_OF[b.kind] || "курсу") + '</span>' : '<span class="gs-soon">незабаром</span>') + '</a></li>';
        }
        return '<li class="guide-step bridge"><span class="gs-num">' + kn + '</span>🔗 ' + _esc(s.title || 'місток') + '</li>';
      }

      var h = '<header class="ch-header ch-header-guide"><div class="ch-label">' + _esc(b.shelf || "Курс") + ' · доріжка крізь книги</div><h1>' + _esc(b.title) + '</h1></header>' +
        '<header class="cover-hero cover-hero-guide">' +
        '<p>' + _esc(b.subtitle || "Кожен крок — або тема предметної книги, або власна стаття курсу, що спирається на пройдене.") + '</p>' +
        '<div class="cover-stats"><div class="stat"><div class="num">' + mods.length + '</div><div class="lbl">' + _esc((W.group || "том") + "ів") + '</div></div>' +
        (hasChap ? '<div class="stat"><div class="num">' + nChap + '</div><div class="lbl">розділів</div></div>' : '') +
        '<div class="stat"><div class="num">' + nStep + '</div><div class="lbl">тем</div></div>' +
        '<div class="stat stat-written"><div class="num">' + nWritten + '<span class="stat-of"> / ' + nArt + '</span></div><div class="lbl">написано</div></div>' +
        '<div class="stat"><div class="num">' + nRead + '</div><div class="lbl">прочитано</div></div>' +
        '</div></header><div class="toc guide-toc">';
      var vol = curVol();
      var shown = mods, listMode = false;
      if (mods.length > 1) {
        var pickIdx = -1;
        mods.forEach(function (m, mi) { if (volSlug(m, mi) === vol) pickIdx = mi; });
        if (pickIdx < 0) { listMode = true; shown = []; }               // без #vol= — показуємо список томів
        else shown = [{ m: mods[pickIdx], i: pickIdx }];
      } else shown = mods.map(function (m, mi) { return { m: m, i: mi }; });

      if (listMode) {
        h += '<div class="lib-shelf lib-shelf-course vol-grid">' + mods.map(function (m, mi) { return volCard(m, mi, written); }).join("") + '</div>';
      } else {
        // У курсі з одним томом рівня списку немає — і повертатися нікуди.
        if (mods.length > 1) h += '<a class="lib-back vol-back" href="#">← ' + _esc(b.title) + '</a>';
        shown.forEach(function (x) {
          var m = x.m, mn = x.i + 1;
          h += '<div class="module-block" id="gm-' + mn + '"><div class="module-head"><span class="m-num">' +
            _esc(cap(W.group || "Том")) + ' ' + mn + '</span><span class="m-ttl">' + _esc(m.title) + '</span></div>';
          (m.chapters || []).forEach(function (c, ci) {
            var cn = mn + "." + (ci + 1);
            if (c.title) h += '<div class="guide-chap-head"><span class="gc-num">' + cn + '</span><span class="gc-ttl">' + _esc(c.title) + '</span></div>';
            h += '<ol class="guide-steps">';
            (c.topics || []).forEach(function (s, si) { h += stepHtml(s, (c.title ? cn : mn) + "." + (si + 1)); });
            h += '</ol>';
          });
          h += '</div>';
        });
      }
      if (host) { host.innerHTML = h + '</div>'; fillBookNames(host); }
      if (!renderGuide._volWired) {                                     // рівень тому живе в адресі
        renderGuide._volWired = true;
        window.addEventListener("hashchange", function () {
          if (/(^|[#&])ch=/.test(location.hash || "")) return;          // стаття — не наша справа
          if (curVol() !== paint._vol) paint(written);
        });
      }
      paint._vol = curVol();
      if (sb) {
        var COL = (function () { try { return new Set(JSON.parse(localStorage.getItem("courses-collapsed") || "[]")); } catch (e) { return new Set(); } })();
        var s = '<a class="sb-home" href="index.html">← Бібліотека (усі книги)</a>' +
          '<a class="sb-logo" href="#"><span class="sb-logo-kicker">' + _esc(cap(W.book || "Курс")) + '</span><span class="sb-logo-title">' + _esc(b.title) + '</span></a>';
        mods.forEach(function (m, mi) {
          var mn = mi + 1;
          s += '<div class="sb-group-label' + (COL.has(m.title) ? ' collapsed' : '') + '" data-collapse-group="' + _esc(m.title) + '">' +
            '<span class="sb-caret" aria-hidden="true">▾</span><span class="sb-gl-txt">' + _esc(cap(W.group || "Том")) + ' ' + mn + ' · ' + _esc(m.title) + '</span></div><div class="sb-group">';
          var k = 0;
          (m.chapters || []).forEach(function (c) {
            (c.topics || []).forEach(function (st) {
              k++;
              var kn = mn + '.' + k, w = isWritten(st, written);
              if (st.ref) {
                var pr = String(st.ref).split('/').filter(Boolean), bk = pr[0], top = pr[pr.length - 1];
                s += '<a class="sb-link' + (w ? '' : ' soon') + (READ.has(bk + '/' + top) ? ' read' : '') + '" href="read.html?course=' + encodeURIComponent(b.bookSlug) +
                  '&book=' + encodeURIComponent(bk) + '#ch=' + encodeURIComponent(top) + '"><span class="sb-kn">' + kn + '</span>' + _esc(st.title || top) + '</a>';
              } else if (st.slug) {
                s += '<a class="sb-link' + (w ? '' : ' soon') + (READ.has(b.bookSlug + '/' + st.slug) ? ' read' : '') + '" href="read.html?book=' + encodeURIComponent(b.bookSlug) +
                  '#ch=' + encodeURIComponent(st.slug) + '"><span class="sb-kn">' + kn + '</span>' + _esc(st.title || st.slug) + '</a>';
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
        var menuBtn = document.getElementById("menu-btn"), scrim = document.getElementById("scrim"), closeBtn = document.getElementById("sidebar-close");
        if (menuBtn) menuBtn.onclick = function () { sb.classList.toggle("open"); };
        if (scrim) scrim.onclick = function () { sb.classList.remove("open"); };
        if (closeBtn) closeBtn.onclick = function () { sb.classList.remove("open"); };
      }
    }
  }

  function cap(s) { return String(s || "").charAt(0).toUpperCase() + String(s || "").slice(1); }

  /* ── Затиснути (або правий клік) лінк статті → попап «позначити прочитано/непрочитано».
     Спільний для читача й лендингу курсу. Ключ = коротка адреса v7 `<book>/<topic>`;
     book.js тримає свій READ-набір у синхроні через подію "courses-read-change". ── */
  (function () {
    var LS = "courses-read";
    function rset() { try { return new Set(JSON.parse(localStorage.getItem(LS) || "[]")); } catch (e) { return new Set(); } }
    function keyFromHref(href) {
      if (!href) return null;
      var m = href.match(/#ch=([^&]+)/); if (!m) return null;
      var slug = decodeURIComponent(m[1]);
      var bm = href.match(/[?&]book=([^&#]+)/); if (bm) return decodeURIComponent(bm[1]) + "/" + slug;   // книга, що ТРИМАЄ статтю
      var B = global.BOOK;   // короткий "#ch=…" — контекст поточної книги (читач)
      return B ? (B.bookSlug + "/" + slug) : null;
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
      if (pop && pop.contains(e.target)) return;
      close();
      var a = e.target.closest && e.target.closest("a[href]");
      var key = a ? keyFromHref(a.getAttribute("href")) : null;
      if (!key) return;
      var x = e.clientX, y = e.clientY;
      function fin() { if (timer) { clearTimeout(timer); timer = null; } document.removeEventListener("pointerup", fin); document.removeEventListener("pointercancel", fin); document.removeEventListener("pointermove", mv); }
      function mv(ev) { if (Math.abs(ev.clientX - x) > 8 || Math.abs(ev.clientY - y) > 8) fin(); }
      timer = setTimeout(function () { timer = null; suppress = true; show(x, y, key); fin(); }, 550);
      document.addEventListener("pointerup", fin);
      document.addEventListener("pointercancel", fin);
      document.addEventListener("pointermove", mv);
    });
    document.addEventListener("click", function (e) {
      if (suppress) { suppress = false; e.preventDefault(); e.stopPropagation(); return; }
      if (pop && !pop.contains(e.target)) close();
    }, true);
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

  global.CONTENT_ROOT = CONTENT;
  global.loadShelf = loadShelf;
  global.loadBook = loadBook;
  global.kindOf = kindOf;
  global.renderGuide = renderGuide;
  global._written = _written;
})(window);
