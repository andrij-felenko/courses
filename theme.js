/* ============================================================================
   theme.js — перемикач теми читання: ☀️ денний / 🌆 вечірній / 🌙 нічний.
   Вибір зберігається в localStorage і застосовується до <html data-theme>.
   Підключається на index.html і read.html; кнопку додає сам.
   (Раннє застосування — інлайн-скриптом у <head>, щоб не було спалаху.)
   ========================================================================== */
(function () {
  "use strict";
  var KEY = "courses-theme";
  var ORDER = ["day", "evening", "night"];
  var META = {
    day:     { icon: "☀️", label: "Денний" },
    evening: { icon: "🌆", label: "Вечірній" },
    night:   { icon: "🌙", label: "Нічний" }
  };
  function get() { try { var t = localStorage.getItem(KEY); return META[t] ? t : "day"; } catch (e) { return "day"; } }
  function save(t) { try { localStorage.setItem(KEY, t); } catch (e) {} }
  function apply(t) { document.documentElement.setAttribute("data-theme", t); }

  apply(get());   // на випадок, якщо інлайн-апплай у <head> не спрацював

  function build() {
    if (document.getElementById("theme-btn") || !document.body) return;
    var b = document.createElement("button");
    b.id = "theme-btn"; b.type = "button"; b.setAttribute("aria-label", "Перемкнути тему читання");
    function paint() {
      var t = get(), m = META[t];
      b.innerHTML = '<span class="th-ico" aria-hidden="true">' + m.icon + '</span><span class="th-lbl">' + m.label + "</span>";
      b.title = "Тема: " + m.label + " — натисни, щоб змінити";
    }
    b.addEventListener("click", function () {
      var t = ORDER[(ORDER.indexOf(get()) + 1) % ORDER.length];
      save(t); apply(t); paint();
    });
    paint();
    (document.getElementById("reader-controls") || document.body).appendChild(b);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
