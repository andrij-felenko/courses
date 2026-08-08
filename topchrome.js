/* ============================================================================
   topchrome.js — кнопка «на рівень вище» (←) на ВУЗЬКОМУ екрані показується
   лише тоді, коли потрібна. Вона fixed і висить над липкою шапкою статті, тож
   постійна присутність з'їдає рядок назви. Правило просте:

     • гортаємо вниз (читаємо)      → ← їде вгору й зникає;
     • гортаємо вгору або ми вгорі  → ← повертається;
     • ширина > 680px               → нічого не робимо (кнопка стоїть завжди).

   ☰ не чіпаємо: меню потрібне будь-якої миті, і воно стоїть з самого краю,
   де шапка й так тримає відступ. Клас вішається на <body>: `up-hidden` (CSS
   у book.css, мобільний блок). Самовбудовується — як theme.js / density.js;
   працює і в читачі статті (book.js), і на лендингу курсу (bookbuild.js).
   ========================================================================== */
(function () {
  "use strict";

  var MQ = window.matchMedia("(max-width: 680px)");
  var TOP_ZONE = 90;   // біля верху сторінки кнопка видима завжди
  var DEAD = 8;        // мертва зона: дрібне тремтіння пальця не блимає кнопкою

  var last = window.scrollY || window.pageYOffset || 0;
  var hidden = false;
  var ticking = false;

  function set(v) {
    if (v === hidden || !document.body) return;
    hidden = v;
    document.body.classList.toggle("up-hidden", v);
  }

  function measure() {
    ticking = false;
    var y = window.scrollY || window.pageYOffset || 0;

    if (!MQ.matches) { set(false); last = y; return; }            // широкий екран — кнопка постійна
    var sb = document.getElementById("sidebar");
    if (sb && sb.classList.contains("open")) { set(false); last = y; return; }   // шухляда відкрита — не смикаємось
    if (y <= TOP_ZONE) { set(false); last = y; return; }          // вгорі сторінки — показана

    var d = y - last;
    if (d > DEAD) { set(true); last = y; }                        // вниз — ховаємо
    else if (d < -DEAD) { set(false); last = y; }                 // вгору — повертаємо
    // |d| ≤ DEAD → last не оновлюємо, щоб дрібні рухи накопичувались
  }

  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(measure);
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("hashchange", function () { last = 0; set(false); });   // нова стаття → кнопка на місці

  if (MQ.addEventListener) MQ.addEventListener("change", function () { set(false); });
  else if (MQ.addListener) MQ.addListener(function () { set(false); });

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", measure);
  else measure();
})();
