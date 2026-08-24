/* ============================================================================
   codelang.js — пріоритет мов коду (Топ-1/2/3) для багатомовних блоків :::tabs
   + згортання панелі кнопок читача в одну «шестерню» (завжди): клік → модальна панель
     кнопок над напівпрозорим фоном, розкриття вліво; авто-закриття за 10с бездіяльності.

   • Кнопка #codelang-btn показує топ-1 мову; клік — попап вибору трьох пріоритетів.
   • Стан у localStorage("courses-codelang-prio") = JSON-масив ключів мов, порядок = пріоритет.
     book.js читає той самий ключ і в кожному блоці показує НАЙВИЩУ доступну мову.
   • Обмін — через подію window "codelangchange".
   Самовбудовується (як theme.js). Кнопки складаються у спільний контейнер #reader-controls.
   ========================================================================== */
(function () {
  "use strict";
  var KEY = "courses-codelang-prio", KEY_OLD = "courses-codelang";
  var LANGS = [
    ["cpp", "C++"], ["c", "C"], ["python", "Python"], ["micropython", "MicroPython"],
    ["js", "JavaScript"], ["ts", "TypeScript"], ["go", "Go"], ["rust", "Rust"],
    ["java", "Java"], ["sh", "Shell"]
  ];
  function labelOf(k) {
    for (var i = 0; i < LANGS.length; i++) if (LANGS[i][0] === k) return LANGS[i][1];
    return k ? k.charAt(0).toUpperCase() + k.slice(1) : "";
  }
  function readPrio() {
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) { var a = JSON.parse(raw); if (a && typeof a.length === "number") return [].slice.call(a).filter(Boolean); }
      var one = localStorage.getItem(KEY_OLD);
      return one ? [one] : [];
    } catch (e) { return []; }
  }
  function writePrio(arr) {
    var clean = [];
    for (var i = 0; i < arr.length; i++) { var k = arr[i]; if (k && clean.indexOf(k) === -1) clean.push(k); }
    clean = clean.slice(0, 3);
    try {
      localStorage.setItem(KEY, JSON.stringify(clean));
      if (clean[0]) localStorage.setItem(KEY_OLD, clean[0]); else localStorage.removeItem(KEY_OLD);
    } catch (e) {}
    try { window.dispatchEvent(new CustomEvent("codelangchange", { detail: { prio: clean, from: "menu" } })); } catch (e) {}
    return clean;
  }
  function host() { return document.getElementById("reader-controls") || document.body; }

  var btn, pop, gear;

  function optionsFor(current) {
    var h = '<option value="">—</option>';
    for (var i = 0; i < LANGS.length; i++)
      h += '<option value="' + LANGS[i][0] + '"' + (LANGS[i][0] === current ? " selected" : "") + ">" + LANGS[i][1] + "</option>";
    return h;
  }
  function buildRows() {
    var prio = readPrio(), names = ["Топ-1", "Топ-2", "Топ-3"], rows = "";
    for (var i = 0; i < 3; i++)
      rows += '<label class="cl-row"><span>' + names[i] + '</span><select data-slot="' + i + '">' + optionsFor(prio[i] || "") + "</select></label>";
    return rows;
  }
  function refreshPop() { if (pop) { var r = pop.querySelector(".cl-rows"); if (r) r.innerHTML = buildRows(); } }
  function paintBtn() {
    if (!btn) return;
    var top = readPrio()[0];
    btn.querySelector(".cl-lbl").textContent = top ? labelOf(top) : "Авто";
    btn.title = top ? ("Мова коду: " + labelOf(top) + " — натисни, щоб змінити пріоритети") : "Пріоритет мов коду";
  }
  function positionPop() {
    if (!btn || !pop) return;
    var r = btn.getBoundingClientRect();
    pop.style.top = (r.bottom + 8) + "px";
    pop.style.right = Math.max(8, window.innerWidth - r.right) + "px";
  }
  function openPop() { refreshPop(); paintBtn(); pop.hidden = false; positionPop(); if (btn) btn.setAttribute("aria-expanded", "true"); }
  function closePop() { if (pop) pop.hidden = true; if (btn) btn.setAttribute("aria-expanded", "false"); }

  function build() {
    if (document.getElementById("codelang-btn") || !document.body) return;

    // ── кнопка мови коду (показує топ-1) ──
    btn = document.createElement("button");
    btn.id = "codelang-btn"; btn.type = "button";
    btn.setAttribute("aria-label", "Пріоритет мов коду");
    btn.setAttribute("aria-haspopup", "true");
    btn.setAttribute("aria-expanded", "false");
    btn.innerHTML =
      '<svg class="cl-ico" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 8l-4 4 4 4M16 8l4 4-4 4"/></svg>' +
      '<span class="cl-lbl"></span>';
    host().appendChild(btn);

    // ── попап пріоритетів (у body, щоб не був flex-елементом панелі) ──
    pop = document.createElement("div");
    pop.id = "codelang-pop"; pop.hidden = true;
    pop.innerHTML =
      '<div class="cl-ttl">Пріоритет мов коду</div>' +
      '<div class="cl-hint">У блоці з кількома мовами показувати найвищу доступну.</div>' +
      '<div class="cl-rows">' + buildRows() + "</div>" +
      '<button type="button" class="cl-reset">Скинути (авто)</button>';
    document.body.appendChild(pop);

    paintBtn();

    btn.addEventListener("click", function (e) { e.stopPropagation(); if (pop.hidden) openPop(); else closePop(); });
    pop.addEventListener("click", function (e) { e.stopPropagation(); });
    pop.addEventListener("change", function (e) {
      if (!(e.target && e.target.matches && e.target.matches("select[data-slot]"))) return;
      var sels = pop.querySelectorAll("select[data-slot]"), arr = [];
      for (var i = 0; i < sels.length; i++) arr.push(sels[i].value);
      writePrio(arr); refreshPop(); paintBtn();
    });
    pop.querySelector(".cl-reset").addEventListener("click", function () { writePrio([]); refreshPop(); paintBtn(); });

    // ── «шестерня»: ЗАВЖДИ згортає всі кнопки-налаштування в модальну панель (розкриття вліво) ──
    gear = document.createElement("button");
    gear.id = "controls-toggle"; gear.type = "button";
    gear.setAttribute("aria-label", "Налаштування читача");
    gear.title = "Налаштування";
    gear.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 11-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 114 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 110 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>';
    var h = host();
    h.insertBefore(gear, h.firstChild);   // шестерня — праворуч (row-reverse), панель розкривається ВЛІВО
    var backdrop = document.createElement("div");   // напівпрозорий фон-модальність під панеллю
    backdrop.id = "rc-backdrop";
    document.body.appendChild(backdrop);
    var autoT = null;
    function armAuto() { clearTimeout(autoT); autoT = setTimeout(closePanel, 10000); }   // авто-закриття за 10с бездіяльності
    function openPanel() { h.classList.add("open"); backdrop.classList.add("show"); armAuto(); }
    function closePanel() { clearTimeout(autoT); h.classList.remove("open"); backdrop.classList.remove("show"); closePop(); }
    backdrop.addEventListener("click", closePanel);
    gear.addEventListener("click", function (e) { e.stopPropagation(); if (h.classList.contains("open")) closePanel(); else openPanel(); });

    // клік у панелі: тему (день/ніч) і мову коду (підменю) лишаємо відкритими (скидаємо таймер), решта кнопок — закриває панель
    h.addEventListener("click", function (e) {
      var b = e.target.closest && e.target.closest("button");
      if (!b || b === gear) return;
      if (b.id === "theme-btn" || b.id === "codelang-btn") { armAuto(); return; }
      closePanel();
    });
    // пауза авто-закриття, поки курсор над панеллю чи попапом мов
    function pauseAuto() { clearTimeout(autoT); }
    function resumeAuto() { if (h.classList.contains("open")) armAuto(); }
    h.addEventListener("mouseenter", pauseAuto); h.addEventListener("mouseleave", resumeAuto);
    pop.addEventListener("mouseenter", pauseAuto); pop.addEventListener("mouseleave", resumeAuto);

    // закриття кліком поза панеллю/попапом та по Escape; репозиція попапу при resize
    document.addEventListener("click", function (e) {
      if (!pop.hidden && !pop.contains(e.target) && !btn.contains(e.target)) closePop();
      if (h.classList.contains("open") && !h.contains(e.target) && !pop.contains(e.target) && e.target !== backdrop) closePanel();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closePanel(); });
    window.addEventListener("resize", function () { if (!pop.hidden) positionPop(); });

    // клік по вкладці коду (book.js) підняв топ-1 → оновити кнопку й меню
    window.addEventListener("codelangchange", function () { paintBtn(); refreshPop(); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
