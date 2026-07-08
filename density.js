/* ============================================================================
   density.js — перемикач ЩІЛЬНОСТІ інтерфейсу (окрема вісь від кольор-теми).
   «Затишна» (cozy, як було) ⇄ «Компактна» (compact, профі-стиль: пласко й щільно).
   Зберігається в localStorage; застосовується до <html data-density>.
   Кнопку додає сам (зліва від лупи). Ранній apply — інлайном у <head>, щоб не блимало.
   ========================================================================== */
(function () {
  "use strict";
  var KEY = "courses-density";
  function get() { try { return localStorage.getItem(KEY) === "compact" ? "compact" : "cozy"; } catch (e) { return "cozy"; } }
  function apply(v) { document.documentElement.setAttribute("data-density", v); }
  apply(get());   // на випадок, якщо інлайн-apply у <head> не спрацював

  function build() {
    if (document.getElementById("density-btn") || !document.body) return;
    var b = document.createElement("button");
    b.id = "density-btn"; b.type = "button"; b.setAttribute("aria-label", "Щільність інтерфейсу");
    b.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>';
    function paint() {
      var v = get();
      b.classList.toggle("on", v === "compact");
      b.title = "Щільність: " + (v === "compact" ? "Компактна" : "Затишна") + " — натисни, щоб змінити";
    }
    b.addEventListener("click", function () {
      var v = get() === "compact" ? "cozy" : "compact";
      try { localStorage.setItem(KEY, v); } catch (e) {}
      apply(v); paint();
    });
    paint();
    (document.getElementById("reader-controls") || document.body).appendChild(b);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
