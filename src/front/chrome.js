/* ============================================================================
   chrome.js — ОДИН власник хромованки читача.

   ПРАВИЛО: хром ніколи не висить над текстом. Уся хромованка живе в ОДНОМУ
   липкому рядку — сітці з трьох комірок:

        [ навігація ]   [ назва ]   [ інструменти ]
          ☰   ←          галузь        перемикач
                         заголовок     версій · ⚙

   Комірки сітки не можуть накластися ОДНА НА ОДНУ за побудовою. Саме тому тут
   немає ані `position: fixed` для кнопок, ані відступів-компенсацій у шапці —
   на них стара схема й розсипалася двічі: кнопці треба було 52px, а шапка на
   вузькому лишала 40px; а на лендингу курсу шапку малює bookbuild.js, який про
   кнопку не знав узагалі, тож ← лягала просто на заголовок.

   Через це рядок збирає ЦЕЙ файл — незалежно від того, хто намалював шапку
   (book.js для статті, bookbuild.js для доріжки курсу) і чи завантажений
   book.js взагалі. Шапку без обгортки `.ch-head-main` він загортає сам.

   Меню — ОДНА кнопка з двома станами (☰ показати / ⟨ сховати): на широкому
   екрані вона згортає колонку, на вузькому — відкриває шухляду. Окремих
   «сховати» на краю сайдбару й «✕» у шухляді більше немає: три кнопки на одну
   дію й були тим, що не сходилося у вирівнюванні.
   ========================================================================== */
(function () {
  "use strict";

  var SB_KEY = "courses-sidebar-hidden";
  var menuBtn = null, upBtn = null;

  function el(id) { return document.getElementById(id); }
  function narrow() { return window.matchMedia("(max-width: 680px)").matches; }
  function sbHidden() { try { return localStorage.getItem(SB_KEY) === "1"; } catch (e) { return false; } }
  function setSbHidden(v) {
    try { localStorage.setItem(SB_KEY, v ? "1" : "0"); } catch (e) {}
    document.documentElement.classList.toggle("sb-hidden", v);
  }

  /* Чи видно меню ЗАРАЗ: на вузькому це стан шухляди, на широкому — колонки. */
  function menuOpen() {
    var sb = el("sidebar");
    return narrow() ? !!(sb && sb.classList.contains("open")) : !sbHidden();
  }
  function paintMenu() {
    if (!menuBtn) return;
    var open = menuOpen();
    menuBtn.innerHTML = open ? "⟨" : "☰";
    menuBtn.title = open ? "Сховати меню" : "Показати меню";
    menuBtn.setAttribute("aria-expanded", String(open));
  }

  function ensureButtons() {
    menuBtn = el("menu-btn");
    if (!menuBtn) {
      menuBtn = document.createElement("button");
      menuBtn.id = "menu-btn"; menuBtn.type = "button";
    }
    menuBtn.setAttribute("aria-label", "Показати або сховати меню");

    upBtn = el("up-btn");
    if (!upBtn) {
      upBtn = document.createElement("a");
      upBtn.id = "up-btn"; upBtn.textContent = "←";
      upBtn.setAttribute("aria-label", "На рівень вище");
      upBtn.setAttribute("title", "На рівень вище");
      upBtn.setAttribute("href", "index.html");
    }
  }

  /* Зібрати рядок у щойно намальованій шапці. Ідемпотентно: зібрану шапку
     позначаємо, тож повторний виклик лише перемальовує стан кнопки меню. */
  function mount() {
    ensureButtons();
    var head = document.querySelector("#content .ch-header");
    if (!head) return;
    if (head.getAttribute("data-chrome") === "1") { paintMenu(); return; }

    var hadMain = head.querySelector(":scope > .ch-head-main");
    var main = hadMain || document.createElement("div");
    if (!hadMain) main.className = "ch-head-main";
    var nav = document.createElement("div"); nav.className = "ch-head-nav";
    var tools = document.createElement("div"); tools.className = "ch-head-tools";

    /* Шапка З обгорткою (стаття): сусіди обгортки — це інструменти (перемикач версій).
       Шапка БЕЗ обгортки (лендинг курсу): усі діти — це назва, загортаємо їх. */
    var keptRc = null;   // ⚠ вийнятий вузол ТРЕБА тримати за змінну: після removeChild
                         //   його вже не знайти через getElementById. Панель гинула не тут,
                         //   а від перезапису #content (див. setContent у book.js), але сам
                         //   прийом «вийняти й шукати за id» хибний — тому й тримаємо посилання.
    [].slice.call(head.childNodes).forEach(function (n) {
      if (n === main) return;
      if (n.nodeType === 1 && (n.id === "up-btn" || n.id === "menu-btn" || n.id === "reader-controls")) {
        if (n.id === "reader-controls") keptRc = n;
        head.removeChild(n); return;                       // свої кнопки розставимо самі
      }
      (hadMain ? tools : main).appendChild(n);
    });

    main.setAttribute("role", "button");
    main.setAttribute("tabindex", "0");
    main.setAttribute("aria-expanded", "false");
    main.setAttribute("title", "Показати шлях угору");

    nav.appendChild(menuBtn);
    nav.appendChild(upBtn);
    var rc = keptRc || el("reader-controls");
    if (rc) tools.appendChild(rc);

    head.appendChild(nav);
    head.appendChild(main);
    head.appendChild(tools);
    head.setAttribute("data-chrome", "1");
    paintMenu();
  }

  /* ── ДРАБИНА: панель назви розкриває ввесь шлях угору ─────────────────
     Замість другої-третьої кнопки в рядку — сама назва стає клікабельною і
     показує сходинки від бібліотеки до поточної статті, кожна клікабельна.
     Так «на рівень вище» перестає бути однією стрілкою навмання: видно ВСІ
     рівні одразу, і місця в рядку це не займає взагалі. */
  var ladderShelf = null;                                    // shelf.json — раз на сторінку

  function ladderSteps() {
    var B = window.BOOK || {};
    var out = [{ t: "Бібліотека", h: "index.html", k: "" }];
    var kind = B.kind || B.type || "";
    var sh = ladderShelf, kindInfo = null, group = null;
    ((sh && sh.kinds) || []).forEach(function (k) {
      if (k.kind === kind) kindInfo = k;
      (k.groups || []).forEach(function (g) {
        if ((g.books || []).indexOf(B.bookSlug) !== -1) { group = g; kindInfo = k; }
      });
    });
    if (kindInfo) out.push({ t: kindInfo.shelf || kind, h: "index.html#" + kindInfo.kind, k: "полиця" });
    if (group) out.push({ t: group.title, h: "index.html#" + kindInfo.kind + "/" + group.slug, k: "збірка" });

    var W = B.words || {};
    if (B.title) out.push({ t: B.title, h: "read.html?book=" + encodeURIComponent(B.bookSlug || ""), k: W.book || "книга" });

    // Поточна стаття: галузь/том і сама назва беруться з намальованої шапки.
    var head = document.querySelector("#content .ch-header");
    var lbl = head && head.querySelector(".ch-label");
    var h1 = head && head.querySelector("h1");
    /* Том курсу тепер має власну адресу («#vol=»), тож сходинка стає посиланням.
       У книзі так не можна: галузь — логічна група в маніфесті, окремої адреси
       в неї немає, і сходинка лишається підписом. */
    if (lbl && lbl.textContent.trim()) {
      var lt = lbl.textContent.trim(), volHref = "";
      if (kind === "course") {
        (B.groups || []).forEach(function (g) {
          if (g.title && lt.indexOf(g.title) !== -1) volHref = "read.html?book=" + encodeURIComponent(B.bookSlug || "") + "#vol=" + encodeURIComponent(g.slug || "");
        });
      }
      out.push({ t: lt, h: volHref, k: W.group || "розділ" });
    }
    if (h1 && h1.textContent.trim() && B.title !== h1.textContent.trim())
      out.push({ t: h1.textContent.trim(), h: "", k: "тут" });
    return out;
  }

  function closeLadder() {
    var p = el("ch-ladder");
    if (p) p.remove();
    var b = document.querySelector(".ch-head-main");
    if (b) b.setAttribute("aria-expanded", "false");
  }
  function openLadder() {
    closeLadder();
    var head = document.querySelector("#content .ch-header");
    if (!head) return;
    var steps = ladderSteps();
    var html = '<div id="ch-ladder" class="ch-ladder" role="dialog" aria-label="Шлях угору">' +
      '<ol class="ch-ladder-list">' + steps.map(function (s, i) {
        var body = '<span class="chl-kind">' + (s.k || "") + '</span><span class="chl-ttl">' + s.t.replace(/[<&]/g, "") + '</span>';
        return '<li class="chl-step" style="--d:' + i + '">' +
          (s.h ? '<a class="chl-link" href="' + s.h + '">' + body + '</a>'
               : '<span class="chl-link is-here">' + body + '</span>') + '</li>';
      }).join("") + '</ol></div>';
    head.insertAdjacentHTML("afterend", html);
    var b = head.querySelector(".ch-head-main");
    if (b) b.setAttribute("aria-expanded", "true");
  }

  function initLadder() {
    document.addEventListener("click", function (e) {
      var t = e.target.closest && e.target.closest(".ch-head-main");
      if (t && document.querySelector("#content .ch-header")) {
        e.preventDefault();
        if (el("ch-ladder")) closeLadder(); else openLadder();
        return;
      }
      if (!e.target.closest || !e.target.closest("#ch-ladder")) closeLadder();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeLadder(); });
    window.addEventListener("hashchange", closeLadder);
    if (window.loadShelf) window.loadShelf().then(function (sh) { ladderShelf = sh; });
  }

  var queued = false;
  function schedule() {
    if (queued) return;
    queued = true;
    var run = function () { queued = false; mount(); };
    /* У СХОВАНІЙ вкладці requestAnimationFrame не викликають узагалі — сторінка не
       малює кадрів. Відкрив статтю в фоновій вкладці (середній клік, відновлена
       сесія) — і шапка лишалася б незібраною, а кнопки на body, доки на неї не
       глянути. Для схованої сторінки беремо звичайний таймер. */
    if (document.hidden) setTimeout(run, 0);
    else requestAnimationFrame(run);
  }

  function start() {
    document.documentElement.classList.toggle("sb-hidden", sbHidden());

    /* Слухач — делегований на документ, а не повішений на вузол. Шапку перемальовують
       через innerHTML, тож кнопку разом з нею знищують і створюють наново; слухач на
       вузлі після першого ж перерендера лишався б на мертвому вузлі, і меню тихо
       переставало відповідати. Делегування переживає будь-яку кількість перемальовок. */
    document.addEventListener("click", function (e) {
      var b = e.target.closest && e.target.closest("#menu-btn");
      if (!b) return;
      e.preventDefault();
      var sb = el("sidebar");
      if (narrow()) { if (sb) sb.classList.toggle("open"); }
      else setSbHidden(!sbHidden());
      paintMenu();
    });

    initLadder();
    schedule();
    var c = el("content");
    // Шапка перемальовується на кожному маршруті — і в book.js, і в bookbuild.js.
    // Спостерігач замість гачків у рендерерах: жоден майбутній шлях рендера про рядок не забуде.
    if (c && window.MutationObserver) new MutationObserver(schedule).observe(c, { childList: true, subtree: true });
    var scrim = el("scrim");
    if (scrim) scrim.addEventListener("click", function () {
      var sb = el("sidebar"); if (sb) sb.classList.remove("open");
      paintMenu();
    });
    window.addEventListener("resize", paintMenu);
    // Меню можна згорнути ще й тумблером у панелі-«шестерні» — він міняє клас на <html>.
    // Стежимо за класом, а не за кнопкою: хто б стан не змінив, іконка лишається чесною.
    if (window.MutationObserver) new MutationObserver(paintMenu)
      .observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();

  window.__chromeMount = schedule;   // book.js смикає після власного рендера
})();
