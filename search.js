/* ============================================================================
   search.js — пошук по сайту-бібліотеці як окреме popup-вікно.
   Кнопка-лупа (зліва від перемикача теми) відкриває модалку з:
     • полем пошуку (анімована поява);
     • фільтрами: книга → розділ;
     • галочкою «шукати також у тексті» (типово вимкнена).
   За замовчуванням шукає ЛИШЕ по назвах тем (H1) і заголовках (search-index.json,
   Рівень 1). З галочкою — довантажує повний текст (search-fulltext.json, Рівень 2).
   Самовбудовується на index.html і read.html (як theme.js) — розмітка не потрібна.
   ========================================================================== */
(function () {
  "use strict";
  var BASE = location.pathname.replace(/[^/]*$/, "");   // тека сторінки = корінь (JSON-и поруч)
  var INDEX = null, FULL = null, fullLoading = null;
  var indexLoading = fetchJSON("search-index.json").then(function (d) { INDEX = d || []; });

  var state = { kind: "", book: "", sec: "", inText: false, cur: -1 };
  var el = {};   // посилання на елементи модалки

  function fetchJSON(name) {
    return fetch(BASE + name, { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });
  }
  function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function norm(s) { return String(s).toLowerCase().replace(/['’ʼ`]/g, ""); }

  function highlight(text, words) {
    var low = norm(text), marks = [];
    words.forEach(function (w) {
      var from = 0, i;
      while ((i = low.indexOf(w, from)) !== -1) { marks.push([i, i + w.length]); from = i + w.length; }
    });
    if (!marks.length) return esc(text);
    marks.sort(function (a, b) { return a[0] - b[0]; });
    var merged = [];
    marks.forEach(function (m) { if (merged.length && m[0] <= merged[merged.length - 1][1]) merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], m[1]); else merged.push(m.slice()); });
    var res = "", pos = 0;
    merged.forEach(function (m) { res += esc(text.slice(pos, m[0])) + "<mark>" + esc(text.slice(m[0], m[1])) + "</mark>"; pos = m[1]; });
    return res + esc(text.slice(pos));
  }

  /* --- пошук: Рівень 1 (назви тем + заголовки), з фільтрами книга/розділ ----- */
  function passesFilter(e) {
    if (state.kind && e.k !== state.kind) return false;
    if (state.book && e.b !== state.book) return false;
    if (state.sec && e.sec !== state.sec) return false;
    return true;
  }
  function searchIndex(words) {
    var res = [];
    for (var i = 0; i < INDEX.length; i++) {
      var e = INDEX[i];
      if (!passesFilter(e)) continue;
      var title = norm(e.title), rank = 0, hitHead = null;
      if (words.every(function (w) { return title.indexOf(w) !== -1; }))
        rank = title.indexOf(words[0]) === 0 ? 100 : 80;
      if (e.h) for (var j = 0; j < e.h.length; j++) {
        var ht = norm(e.h[j].t);
        if (words.every(function (w) { return ht.indexOf(w) !== -1; })) { hitHead = e.h[j]; rank = Math.max(rank, 60); break; }
      }
      if (!rank) continue;
      res.push({ e: e, i: i, rank: rank, head: hitHead, lvl: 1 });
    }
    return res;
  }
  function searchFull(words, taken) {
    if (!FULL || !FULL.docs) return [];
    var res = [];
    for (var i = 0; i < FULL.docs.length; i++) {
      if (taken[i]) continue;
      var e = INDEX[i]; if (!e || !passesFilter(e)) continue;
      var blob = FULL.docs[i];
      if (words.every(function (w) { return blob.indexOf(w) !== -1; })) res.push({ e: e, i: i, rank: 20, head: null, lvl: 2 });
    }
    return res;
  }
  function hrefFor(hit) {
    var h = hit.e.href;
    if (hit.head && hit.head.a) h += (h.indexOf("#") === -1 ? "#" : "&") + "at=" + hit.head.a;
    return BASE + h;
  }
  function kindPri(e) { return e.k === "guide" ? 0 : 1; }   // курси — головне, тож попереду книг
  function rankSort(a, b) { return b.rank - a.rank || kindPri(a.e) - kindPri(b.e) || norm(a.e.title).localeCompare(norm(b.e.title)); }   // релевантність первинна; тип — тай-брейк

  /* --- фільтри: книги з індексу, розділи обраної книги ------------------------ */
  var KIND_LABEL = { book: "Книги", guide: "Курси", catalog: "Каталоги", reference: "Довідники" };
  var KIND_ONE = { book: "Книга", guide: "Курс", catalog: "Каталог", reference: "Довідник" };
  var KIND_ALL = { book: "Усі книги", guide: "Усі курси", catalog: "Усі каталоги", reference: "Усі довідники" };
  var KIND_ALLSEC = { book: "Усі розділи", guide: "Усі модулі", catalog: "Усі родини", reference: "Усі розділи" };
  function kindsPresent() {
    var seen = {}; (INDEX || []).forEach(function (e) { if (e.k) seen[e.k] = 1; });
    return ["guide", "book", "catalog", "reference"].filter(function (k) { return seen[k]; });
  }
  function bookList(kind) {
    var seen = {}, out = [];
    (INDEX || []).forEach(function (e) { if ((!kind || e.k === kind) && !seen[e.b]) { seen[e.b] = 1; out.push({ slug: e.b, title: e.bt }); } });
    out.sort(function (a, b) { return a.title.localeCompare(b.title); });
    return out;
  }
  function secList(book) {
    var seen = {}, out = [];
    (INDEX || []).forEach(function (e) { if (e.b === book && e.sec && !seen[e.sec]) { seen[e.sec] = 1; out.push(e.sec); } });
    return out;
  }
  function bookKind(slug) { var e = (INDEX || []).filter(function (x) { return x.b === slug; })[0]; return e ? e.k : "book"; }
  function chip(label, active, dataAttr, dataVal) {
    return '<button type="button" class="sm-chip' + (active ? ' on' : '') + '" ' + dataAttr + '="' + esc(dataVal) + '" aria-pressed="' + (active ? 'true' : 'false') + '">' + esc(label) + '</button>';
  }
  function renderFilters() {
    // Рівень A — тип контенту (сегмент), лише якщо типів кілька
    if (el.types) {
      var kinds = kindsPresent(), th = "";
      if (kinds.length > 1) {
        th = chip('Усе', !state.kind, 'data-kind', '');
        kinds.forEach(function (k) { th += chip(KIND_LABEL[k] || k, state.kind === k, 'data-kind', k); });
      }
      el.types.innerHTML = th;
    }
    // Рівень B — конкретна книга/курс/каталог у межах типу
    var books = bookList(state.kind);
    var bh = chip(state.kind ? (KIND_ALL[state.kind] || 'Усе') : 'Усе', !state.book, 'data-book', '');
    books.forEach(function (b) { bh += chip(b.title, state.book === b.slug, 'data-book', b.slug); });
    el.books.innerHTML = bh;
    // Рівень C — розділ/модуль/родина (ярлик за типом)
    if (state.book) {
      var secs = secList(state.book), kw = bookKind(state.book);
      var sh = chip(KIND_ALLSEC[kw] || 'Усі розділи', !state.sec, 'data-sec', '');
      secs.forEach(function (s) { sh += chip(s, state.sec === s, 'data-sec', s); });
      el.secs.innerHTML = sh;
      el.secs.hidden = false;
    } else { el.secs.innerHTML = ''; el.secs.hidden = true; }
  }

  /* --- рендер результатів ----------------------------------------------------- */
  function plural(n) {
    var d = n % 10, dd = n % 100;
    var w = (d === 1 && dd !== 11) ? 'результат' : (d >= 2 && d <= 4 && (dd < 12 || dd > 14)) ? 'результати' : 'результатів';
    return n + ' ' + w;
  }
  function welcomeHtml() {
    return '<div class="sm-welcome">' +
      '<div class="sm-w-ttl">Пошук по бібліотеці</div>' +
      '<div class="sm-w-txt">Почни писати — шукаю в назвах тем і заголовках. Обери тип угорі, щоб звузити до книг / курсів / каталогів; «Глибше» додасть пошук у тексті статей.</div>' +
      '<div class="sm-w-keys"><kbd>/</kbd> відкрити <span>·</span> <kbd>↑</kbd><kbd>↓</kbd> вибір <span>·</span> <kbd>↵</kbd> перейти <span>·</span> <kbd>Esc</kbd> закрити</div>' +
      '</div>';
  }
  function renderResults(hits, words, total) {
    state.cur = -1;
    if (!words.length) { el.results.innerHTML = welcomeHtml(); el.hint.textContent = ''; return; }
    if (!hits.length) { el.results.innerHTML = '<div class="sm-empty">Нічого не знайдено' + (state.inText ? '' : ' — спробуй увімкнути «шукати в тексті»') + '.</div>'; el.hint.textContent = ''; return; }
    var h = '';
    hits.forEach(function (hit, idx) {
      var e = hit.e;
      var crumb = (e.k ? '<span class="sm-kind sm-kind-' + esc(e.k) + '">' + esc(KIND_ONE[e.k] || e.k) + '</span>' : '') + esc(e.bt) + (e.sec ? ' · ' + esc(e.sec) : '');
      var sub = hit.head ? '<span class="sm-sub">↳ ' + highlight(hit.head.t, words) + '</span>'
        : (hit.lvl === 2 ? '<span class="sm-sub sm-inbody">знайдено в тексті статті</span>' : '');
      h += '<a class="sm-item" role="option" id="sm-opt-' + idx + '" aria-selected="false" data-idx="' + idx + '" href="' + esc(hrefFor(hit)) + '">' +
        '<span class="sm-crumb">' + crumb + '</span>' +
        '<span class="sm-title">' + highlight(e.title, words) + '</span>' + sub + '</a>';
    });
    el.results.innerHTML = h;
    var tot = (total != null ? total : hits.length);
    el.hint.textContent = plural(tot) + (tot > hits.length ? ' · показано ' + hits.length : '');
  }

  function run() {
    if (!INDEX) { if (el.input && norm(el.input.value.trim()).length >= 2 && el.hint) el.hint.textContent = 'Завантажую індекс…'; indexLoading.then(run); return; }
    var q = norm(el.input.value.trim());
    var words = q.length >= 2 ? q.split(/\s+/).filter(function (w) { return w.length >= 2; }) : [];
    if (el.scope) el.scope.hidden = !words.length;   // scope-фільтри — лише коли є запит
    if (!words.length) { renderResults([], words); return; }
    var l1 = searchIndex(words).sort(rankSort);
    var hits = l1;
    if (state.inText) {
      if (!FULL) { loadFull().then(run); el.hint.textContent = 'Довантажую текст статей…'; }
      else {
        var taken = {}; l1.forEach(function (hit) { taken[hit.i] = 1; });
        hits = l1.concat(searchFull(words, taken).sort(rankSort));
      }
    }
    renderResults(hits.slice(0, 60), words, hits.length);
  }
  function loadFull() {
    if (FULL) return Promise.resolve();
    if (!fullLoading) fullLoading = fetchJSON("search-fulltext.json").then(function (d) { FULL = d || { docs: [] }; });
    return fullLoading;
  }

  /* --- відкриття / закриття з анімацією --------------------------------------- */
  var closeTimer = null;
  function open() {
    if (!el.modal) return;
    clearTimeout(closeTimer);
    el.modal.hidden = false;
    void el.modal.offsetWidth;                 // reflow → щоб transition спрацював
    el.modal.classList.add('open');
    document.documentElement.style.overflow = 'hidden';
    if (!el.filtersReady && INDEX) { renderFilters(); el.filtersReady = true; }
    else indexLoading.then(function () { if (!el.filtersReady) { renderFilters(); el.filtersReady = true; } });
    run();   // показати привітальний (або попередній) стан одразу
    setTimeout(function () { el.input.focus(); el.input.select(); }, 60);
  }
  function close() {
    if (!el.modal) return;
    el.modal.classList.remove('open');
    document.documentElement.style.overflow = '';
    closeTimer = setTimeout(function () { el.modal.hidden = true; }, 220);
  }

  /* --- побудова DOM ----------------------------------------------------------- */
  function build() {
    if (document.getElementById('search-btn') || !document.body) return;

    var btn = document.createElement('button');
    btn.id = 'search-btn'; btn.type = 'button';
    btn.setAttribute('aria-label', 'Пошук по сайту');
    btn.title = 'Пошук (/)';
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>';
    (document.getElementById("reader-controls") || document.body).appendChild(btn);

    var modal = document.createElement('div');
    modal.id = 'search-modal'; modal.hidden = true;
    modal.innerHTML =
      '<div class="sm-backdrop"></div>' +
      '<div class="sm-panel" role="dialog" aria-modal="true" aria-label="Пошук по сайту">' +
        '<div class="sm-head">' +
          '<svg class="sm-mag" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>' +
          '<input class="sm-input" type="search" autocomplete="off" spellcheck="false" placeholder="Тема, заголовок…" aria-label="Запит">' +
          '<button class="sm-close" type="button" aria-label="Закрити">✕</button>' +
        '</div>' +
        '<label class="sm-mode"><input type="checkbox"><span>Глибше — шукати й у тексті статей</span></label>' +
        '<div class="sm-chips sm-types" role="group" aria-label="Тип"></div>' +
        '<div class="sm-scope" hidden>' +
          '<div class="sm-chips sm-books"></div>' +
          '<div class="sm-chips sm-secs" hidden></div>' +
        '</div>' +
        '<div class="sm-results" role="listbox"></div>' +
        '<div class="sm-hint"></div>' +
      '</div>';
    document.body.appendChild(modal);

    el.modal = modal;
    el.input = modal.querySelector('.sm-input');
    el.results = modal.querySelector('.sm-results');
    el.hint = modal.querySelector('.sm-hint');
    el.books = modal.querySelector('.sm-books');
    el.secs = modal.querySelector('.sm-secs');
    el.types = modal.querySelector('.sm-types');
    el.scope = modal.querySelector('.sm-scope');
    el.check = modal.querySelector('.sm-mode input');

    btn.addEventListener('click', open);
    modal.querySelector('.sm-close').addEventListener('click', close);
    modal.querySelector('.sm-backdrop').addEventListener('click', close);

    var t = null;
    el.input.addEventListener('input', function () { clearTimeout(t); t = setTimeout(run, 110); });

    el.check.addEventListener('change', function () {
      state.inText = el.check.checked;
      if (state.inText && !FULL) loadFull().then(run); else run();
    });

    // кліки по чипах фільтрів (делегування)
    el.books.addEventListener('click', function (ev) {
      var c = ev.target.closest && ev.target.closest('[data-book]'); if (!c) return;
      state.book = c.getAttribute('data-book'); state.sec = ''; renderFilters(); run();
    });
    el.secs.addEventListener('click', function (ev) {
      var c = ev.target.closest && ev.target.closest('[data-sec]'); if (!c) return;
      state.sec = c.getAttribute('data-sec'); renderFilters(); run();
    });
    el.types.addEventListener('click', function (ev) {
      var c = ev.target.closest && ev.target.closest('[data-kind]'); if (!c) return;
      state.kind = c.getAttribute('data-kind'); state.book = ''; state.sec = ''; renderFilters(); run();
    });

    // клавіатура в результатах
    el.input.addEventListener('keydown', function (ev) {
      var items = [].slice.call(el.results.querySelectorAll('.sm-item'));
      if (ev.key === 'Escape') { close(); return; }
      if (ev.key === 'Enter') { var pick = state.cur >= 0 ? state.cur : 0; if (items[pick]) location.href = items[pick].getAttribute('href'); return; }
      if (!items.length) return;
      if (ev.key === 'ArrowDown') { ev.preventDefault(); state.cur = Math.min(state.cur + 1, items.length - 1); }
      else if (ev.key === 'ArrowUp') { ev.preventDefault(); state.cur = Math.max(state.cur - 1, -1); }   // з першого — назад у поле
      else return;
      items.forEach(function (it, i) { var on = i === state.cur; it.classList.toggle('sm-active', on); it.setAttribute('aria-selected', on ? 'true' : 'false'); });
      el.input.setAttribute('aria-activedescendant', state.cur >= 0 ? 'sm-opt-' + state.cur : '');
      if (state.cur >= 0 && items[state.cur]) items[state.cur].scrollIntoView({ block: 'nearest' });
    });

    // глобальні гарячі клавіші: «/» або Ctrl/⌘+K відкривають; тільки поза полями вводу
    document.addEventListener('keydown', function (ev) {
      var typing = /^(INPUT|TEXTAREA|SELECT)$/.test((ev.target && ev.target.tagName) || '') || (ev.target && ev.target.isContentEditable);
      if ((ev.key === '/' && !typing) || ((ev.ctrlKey || ev.metaKey) && (ev.key === 'k' || ev.key === 'K'))) {
        ev.preventDefault(); open();
      }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();
