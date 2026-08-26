/* ============================================================================
   sidebar-toggle.js — згортання/розгортання лівого бічного меню на ШИРОКОМУ екрані.
   На десктопі сайдбар — постійна колонка; сховати її можна ДВОМА кнопками:
     • «⟨» (#sb-hide) — прямо на сайдбарі, у правому верхньому куті (коли він відкритий);
     • тумблер у панелі-«шестерні» (#sidebar-toggle).
   Повернути: ☰ (#menu-btn, з'являється зліва зверху) або той самий тумблер.
   Стан у localStorage. На вузькому екрані сайдбар — шухляда (☰/✕), тож ці кнопки
   неактуальні й ховаються (CSS). Самовбудовується (як theme.js/density.js).
   ========================================================================== */
(function () {
  "use strict";
  var KEY = "courses-sidebar-hidden";
  function get() { try { return localStorage.getItem(KEY) === "1"; } catch (e) { return false; } }
  function apply(v) { document.documentElement.classList.toggle("sb-hidden", v); }
  apply(get());   // ранній apply інлайном у <head> усуває блимання; тут — на випадок

  var paint = function () {};
  function set(v) {
    try { localStorage.setItem(KEY, v ? "1" : "0"); } catch (e) {}
    apply(v); paint();
  }

  function build() {
    if (document.getElementById("sidebar-toggle") || !document.body) return;
    var b = document.createElement("button");
    b.id = "sidebar-toggle"; b.type = "button";
    b.setAttribute("aria-label", "Показати або сховати бічне меню");
    b.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/></svg>';
    paint = function () {
      var hidden = get();
      b.classList.toggle("on", !hidden);   // «увімкнено» = меню показане
      b.setAttribute("aria-pressed", hidden ? "false" : "true");
      b.title = hidden ? "Показати бічне меню" : "Сховати бічне меню";
    };
    b.addEventListener("click", function () { set(!get()); });
    paint();
    (document.getElementById("reader-controls") || document.body).appendChild(b);   // у панель кнопок (шестерня лишається зверху)

    // ☰ і кнопку «сховати» на краю сайдбару цей файл БІЛЬШЕ НЕ ЧІПАЄ: меню веде chrome.js
    // однією кнопкою в рядку шапки. Поки власників було двоє, обробники билися — клік
    // спершу проходив через тутешній, потім через делегований, і меню відмовлялося вертатись.
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
