/* ============================================================================
   bookbuild.js — складання книги з per-module manifest.js (без залежностей)

   Кожен МОДУЛЬ книги живе у власному файлі `<book>/<module>/manifest.js`, що
   реєструє себе:  (window.__MODREG__ = window.__MODREG__ || []).push({ ...модуль });

   Кореневий ІНДЕКС книги (manifest*.js) задає лише мету й список модулів:
     window.BOOK_META    = { title, subtitle, shortTitle, basePath, libraryHref };
     window.BOOK_MODULES = [ "block-1-…/manifest.js",   // зовнішній per-module
                             { n:2, slug:"…", chapters:[…] } ];  // або inline (legacy)

   assembleBook() фетчить рядки-URL, бере inline-обʼєкти як є, сортує за n і
   ВИВОДИТЬ chapter.histories[]/extras[] зі списку chapter.topics[]
   (kind:"hist" → histories; "comp"/"math"/"proj" → extras), зберігаючи порядок,
   яким вони стоять у topics[]. Так рушій (book.js) отримує звичні поля.

   Зворотна сумісність: книга БЕЗ BOOK_MODULES працює як раніше (window.BOOK
   задається індексом напряму) — нічого складати не треба.
   ========================================================================== */
(function (global) {
  "use strict";

  function extend(dst, src) {
    for (var k in src) { if (Object.prototype.hasOwnProperty.call(src, k)) dst[k] = src[k]; }
    return dst;
  }

  function fetchText(url) {
    return fetch(url, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status + " — " + url);
      return r.text();
    });
  }

  // Виконати текст per-module manifest: він робить window.__MODREG__.push({…}) —
  // лишаємо запис у реальному window.__MODREG__.
  function evalModule(src, url) {
    try {
      new Function("window", src)(global);            // eslint-disable-line no-new-func
    } catch (e) {
      throw new Error("manifest-модуль не виконується (" + url + "): " + e.message);
    }
  }

  var SPEC_KINDS = { comp: 1, math: 1, proj: 1 };

  // Вивести histories[]/extras[] із topics[] (як їх очікує рушій). Якщо поля вже
  // задані явно (legacy inline-модуль) — не чіпаємо.
  function deriveChapter(c) {
    if (!c || !c.topics) return c;
    if (!c.histories) {
      var hist = [];
      c.topics.forEach(function (t) { if (t && t.kind === "hist" && t.file) hist.push(t.file); });
      c.histories = hist;
    }
    if (!c.extras) {
      var extra = [];
      c.topics.forEach(function (t) { if (t && t.kind && SPEC_KINDS[t.kind] && t.file) extra.push(t.file); });
      c.extras = extra;
    }
    return c;
  }

  function finishModules(mods) {
    mods.sort(function (a, b) { return (a.n || 0) - (b.n || 0); });
    mods.forEach(function (m) { (m.chapters || []).forEach(deriveChapter); });
    return mods;
  }

  /* Зібрати book = {…meta, modules:[…]} зі списку модулів (URL-и та/або inline).
     basePath — префікс до module-файлів (як правило meta.basePath).
     ВАЖЛИВО: модулі реєструються у СПІЛЬНОМУ window.__MODREG__, тож паралельні
     виклики (4 книги в бібліотеці воднораз) СЕРІАЛІЗУЄМО чергою — інакше гонитва
     за __MODREG__ перемішує/губить модулі. */
  var _queue = Promise.resolve();
  function assembleBook(meta, modules, basePath) {
    var p = _queue.then(function () { return _assembleBook(meta, modules, basePath); });
    _queue = p.then(function () {}, function () {});   // черга триває незалежно від успіху
    return p;
  }
  function _assembleBook(meta, modules, basePath) {
    meta = meta || {};
    basePath = basePath != null ? basePath : (meta.basePath || "");
    global.__MODREG__ = [];
    var inline = [];
    var jobs = (modules || []).map(function (entry) {
      if (typeof entry === "string") {
        return fetchText(basePath + entry).then(function (src) { evalModule(src, entry); });
      }
      inline.push(entry);
      return Promise.resolve();
    });
    return Promise.all(jobs).then(function () {
      var mods = (global.__MODREG__ || []).slice().concat(inline);
      global.__MODREG__ = [];
      return extend(extend({}, meta), { modules: finishModules(mods) });
    });
  }

  /* Зчитати індекс іншої книги (текст manifest*.js) і повернути готовий book.
     Працює для нового формату (BOOK_META + BOOK_MODULES) і для legacy (window.BOOK). */
  function bookFromIndexSrc(src, basePath) {
    var sandbox = {};
    try { new Function("window", src)(sandbox); } catch (e) { return Promise.resolve(null); }  // eslint-disable-line no-new-func
    if (sandbox.BOOK_MODULES) {
      return assembleBook(sandbox.BOOK_META, sandbox.BOOK_MODULES, basePath != null ? basePath : (sandbox.BOOK_META && sandbox.BOOK_META.basePath));
    }
    return Promise.resolve(sandbox.BOOK || null);   // legacy книга
  }

  /* Бутстрап entry-сторінки: зібрати window.BOOK (якщо індекс дав BOOK_MODULES),
     тоді підвантажити рушій engineUrl. Legacy-книгу пускаємо одразу. */
  function bootBook(engineUrl) {
    function inject() {
      var s = document.createElement("script");
      s.src = engineUrl;
      document.body.appendChild(s);
    }
    if (global.BOOK_MODULES) {
      assembleBook(global.BOOK_META, global.BOOK_MODULES, global.BOOK_META && global.BOOK_META.basePath)
        .then(function (book) { global.BOOK = book; inject(); })
        .catch(function (e) {
          var host = document.getElementById("content") || document.body;
          host.innerHTML = '<div class="state error"><h2>Не вдалося зібрати книгу</h2><p><code>' +
            String(e && e.message ? e.message : e) + "</code></p></div>";
        });
    } else {
      inject();   // legacy: window.BOOK уже заданий індексом
    }
  }

  global.assembleBook = assembleBook;
  global.bookFromIndexSrc = bookFromIndexSrc;
  global.bootBook = bootBook;
})(window);
