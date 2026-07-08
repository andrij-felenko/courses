/* ============================================================================
   sidebar-toggle.js — згортання/розгортання лівого бічного меню на ШИРОКОМУ екрані.
   На десктопі сайдбар — постійна колонка; ця кнопка дає її сховати (читання на всю
   ширину). Стан у localStorage. На вузькому екрані сайдбар — шухляда (☰/✕), тож
   тут кнопка неактуальна й ховається (CSS). Самовбудовується (як theme.js/density.js).
   ========================================================================== */
(function () {
  "use strict";
  var KEY = "courses-sidebar-hidden";
  function get() { try { return localStorage.getItem(KEY) === "1"; } catch (e) { return false; } }
  function apply(v) { document.documentElement.classList.toggle("sb-hidden", v); }
  apply(get());   // ранній apply інлайном у <head> усуває блимання; тут — на випадок

  function build() {
    if (document.getElementById("sidebar-toggle") || !document.body) return;
    var b = document.createElement("button");
    b.id = "sidebar-toggle"; b.type = "button";
    b.setAttribute("aria-label", "Показати або сховати бічне меню");
    b.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/></svg>';
    function paint() {
      var hidden = get();
      b.classList.toggle("on", !hidden);   // «увімкнено» = меню показане
      b.setAttribute("aria-pressed", hidden ? "false" : "true");
      b.title = hidden ? "Показати бічне меню" : "Сховати бічне меню";
    }
    b.addEventListener("click", function () {
      var v = !get();
      try { localStorage.setItem(KEY, v ? "1" : "0"); } catch (e) {}
      apply(v); paint();
    });
    paint();
    (document.getElementById("reader-controls") || document.body).appendChild(b);   // у панель кнопок (шестерня лишається зверху)
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
