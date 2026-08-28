/* ============================================================================
   book.js — рушій книги (без залежностей)
   • парсер Markdown під конвенції курсу (callout-и 🔧/📜/▶️, фігури+підпис,
     формули в код-блоках, двомовні терміни, перехресні .md-лінки);
   • hash-роутер (#ch=<slug>&at=<якір>) — працює на GitHub Pages без сервера;
   • збірка сайдбару (теми + історії) і мапи курсу.
   Точка входу — window.BOOK із manifest.js.
   ========================================================================== */
(function () {
  "use strict";

  var BOOK = window.BOOK;
  var BASE = BOOK.basePath || "";   // префікс до контенту (embedded/) відносно index.html
  // Префікс розгортання — тека, звідки видно контент root/. Шляхи «від кореня репо»
  // (/root/…) у Markdown резолвимо саме сюди, інакше на Pages «/root/…» пішло б на
  // домен-корінь повз підтеку «/courses/».
  // Рушій живе в src/front/: на проді його викладають у корінь сайту (deploy складає
  // _site з src/front/* + root/), а локально він лишається в підтеці — тож якщо шлях
  // закінчується на src/front/, зрізаємо його, і обидва режими дають той самий корінь.
  var SITE_ROOT = location.pathname.replace(/[^/]*$/, "").replace(/(?:^|\/)src\/front\/$/, "/");

  // Книги й курси — один простір імен; крос-попапи через префікс topic: (v7).
  var SUBJECT_META = {
    physics:        { icon: "⚛️", label: "Фізика" },        math:           { icon: "🧮", label: "Математика" },
    chemistry:      { icon: "⚗️", label: "Хімія" },         electronics:    { icon: "🔌", label: "Електроніка" },
    programming:    { icon: "💻", label: "Програмування" }, communications: { icon: "📡", label: "Зв'язок" },
    algorithms:     { icon: "🧠", label: "Алгоритми" },     philosophy:     { icon: "🦉", label: "Філософія" },
    sensors:        { icon: "🌡️", label: "Сенсори" },       power:          { icon: "🔋", label: "Живлення" },
    connect:        { icon: "📡", label: "Зв'язок" },        boards:         { icon: "🧰", label: "Плати" },
    instruments:    { icon: "🔬", label: "Прилади" }
  };
  var _subjCache = {};
  // версія-файл існує на диску ⟺ її статус НЕ pending/empty (done/update/deeper/recheck)
  function _fileExists(s) { return s === "done" || s === "update" || s === "deeper" || s === "recheck"; }

  // ── Версії статті (коротка/повна) як ОДИН стек із перемикачем зверху ───────
  // URL несе версію: «&v=d» = повна (детальна); без параметра = коротка (базова).
  // Дефолт залежить від входу: зі списку/меню книги → повна (як є); згадка з
  // ІНШОЇ статті (без суфікса) → коротка; навігація В МЕЖАХ статті → поточна версія.
  function verSuffix(ver) { return ver === "d" ? "&v=d" : ""; }
  function chHref(slug, at, ver) { return "#ch=" + slug + (at ? "&at=" + at : "") + verSuffix(ver); }
  function chReadable(c) { return !!(c.hasBasic || c.hasDetailed); }                                  // є що читати (будь-яка версія)
  function chVisible(c) { return chReadable(c) || c.status === "pending" || c.dstatus === "pending"; } // показати (або «незабаром»)
  function menuVer(c) { return c.hasDetailed ? "d" : ""; }
  /* ЯКІ версії має тема — не літерою й не кнопкою, а кольором риски ліворуч
     (див. «версії кольором риски» у CSS). Бліда — коротка, насичена — повна,
     дві барви — обидві. Саме тому три класи, а не прапорець «обидві»: інакше
     тема лише з повною виглядала б як тема лише з короткою. */
  function verClass(c) {
    if (c.hasBasic && c.hasDetailed) return " two-ver";
    if (c.hasDetailed) return " v-full";
    if (c.hasBasic) return " v-basic";
    return "";
  }
  function verHint(c) {
    if (c.hasBasic && c.hasDetailed) return ' title="Є коротка й повна версії"';
    if (c.hasDetailed) return ' title="Лише повна версія"';
    if (c.hasBasic) return ' title="Лише коротка версія"';
    return "";
  }
  /* Написано, але людина ще не перечитала (recheck / update / deeper). Читається як усе інше —
     позначка лише каже читачеві, що текст іще можуть поправити. Прапорець c.draft рахувався
     від початку (див. індексацію), але його ніхто не малював. */
  function betaTag(c) { return c.draft ? ' <span class="beta-tag">beta</span>' : ""; }                                            // відкриття зі списку книги → повна, якщо є

  // типи спец-вставок (підтем): історія / математика / компонент / практика
  var SPEC_META = {
    hist: { emoji: "📜", label: "Історія", modal: "Історична вставка" },
    math: { emoji: "🧮", label: "Математика", modal: "Математична вставка" },
    comp: { emoji: "🔌", label: "Компоненти", modal: "Компонентна вставка" },
    proj: { emoji: "⚙️", label: "Практика", modal: "Практична вставка" },
    api: { emoji: "📋", label: "Довідка/API", modal: "Довідка / API" }
  };
  var SPEC_ORDER = ["hist", "math", "comp", "proj", "api"];
  function specType(name) {                 // тип за іменем файла вставки
    var b = String(name).replace(/^.*\//, "");
    if (/^hist[-.]/i.test(b) || /history/i.test(b) || /-h-/.test(b)) return "hist";   // hist-… / …history… / нове <тема>-h-…
    if (/^math[-.]/i.test(b) || /-m-/.test(b)) return "math";        // нове math-… / старе -m-
    if (/^comp[-.]/i.test(b) || /-c-/.test(b)) return "comp";        // нове comp-… / старе -c-
    if (/^proj[-.]/i.test(b) || /-a-/.test(b)) return "proj";        // нове proj-… / старе -a-
    if (/^api[-.]/i.test(b)) return "api";                            // api- → довідка/інтерфейс
    return "hist";
  }
  function emojiType(e) {                    // тип за emoji в _status.md
    return e === "🧮" ? "math" : e === "🔌" ? "comp" : (e === "⚙️" || e === "⚙") ? "proj" : e === "📋" ? "api" : "hist";
  }
  var $content = document.getElementById("content");
  var $sidebar = document.getElementById("sidebar");

  /* ── Вигляд списку тем: список/плитка + згорнуті галузі (зберігається) ── */
  var NAV = {
    view: (function () { try { return localStorage.getItem("courses-map-view") === "list" ? "list" : "grid"; } catch (e) { return "grid"; } })(),   // книги на 500–1000 тем списком дають ~30 000px прокрутки
    collapsed: (function () { try { return new Set(JSON.parse(localStorage.getItem("courses-collapsed") || "[]")); } catch (e) { return new Set(); } })()
  };
  function saveNav() { try { localStorage.setItem("courses-map-view", NAV.view); localStorage.setItem("courses-collapsed", JSON.stringify(Array.from(NAV.collapsed))); } catch (e) {} }
  function isCollapsed(key) { return NAV.collapsed.has(key); }
  function allGroupKeys() { var out = []; BOOK.modules.forEach(function (m) { if (m.chapters && m.chapters.length) out.push(m.title); }); return out; }

  /* Книгоподібні види (галузі→статті, без порядку): предметна книга й довідник reference/.
     Каталог і курс рендеряться інакше (обкладинка-доріжка, нумеровані кроки). */
  /* v7: `type` — це вид зі shelf.json (sci · eng · hw · sys · cat · com · course),
     а не старі "book"/"reference". Книгоподібне — усе, крім курсу; курс має власну
     шапку з доріжкою. Доки тут стояли старі назви, умова була ХИБНОЮ для всього
     корпусу, і компактна світла шапка книги з перемикачем версій не малювалась ніде. */
  function isBookLike() { return (BOOK.kind || BOOK.type) !== "course"; }

  /* ── Прогрес читання: доскролив до низу статті → «прочитано» (localStorage) ── */
  var READ = (function () { try { return new Set(JSON.parse(localStorage.getItem("courses-read") || "[]")); } catch (e) { return new Set(); } })();
  function readKey(slug) { return (BOOK.bookSlug || BOOK.type || "book") + "/" + slug; }
  function isRead(slug) { return !!slug && READ.has(readKey(slug)); }
  function readClass(slug) { return isRead(slug) ? " read" : ""; }
  function markRead(slug) {
    if (!slug) return;
    var k = readKey(slug);
    if (READ.has(k)) return;
    READ.add(k);
    try { localStorage.setItem("courses-read", JSON.stringify(Array.from(READ))); } catch (e) {}
    [].forEach.call(document.querySelectorAll(".sb-link.active"), function (a) { a.classList.add("read"); });   // підсвітити наживо
  }
  // Попап «прочитано/непрочитано» (bookbuild.js) міняє localStorage сам — тримаємо НАШ набір у синхроні,
  // і на обкладинці перемальовуємо лічильники «прочитано / усього».
  window.addEventListener("courses-read-change", function (e) {
    var d = (e && e.detail) || {}; if (!d.key) return;
    if (d.on) READ.add(d.key); else READ.delete(d.key);
    if (!currentSlug) renderCover();
  });
  var readSpy = null, readTimer = null;
  var READ_DWELL_MS = 7000;   // просто доскролити мало: треба ПРОБУТИ внизу 7 с поспіль
  function setupReadTracking(slug) {
    if (readSpy) { readSpy.disconnect(); readSpy = null; }
    if (readTimer) { clearTimeout(readTimer); readTimer = null; }
    if (isRead(slug) || !window.IntersectionObserver) return;
    var end = document.getElementById("read-end");
    if (!end) return;
    readSpy = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) {
          if (!readTimer) readTimer = setTimeout(function () {
            readTimer = null; markRead(slug);
            if (readSpy) { readSpy.disconnect(); readSpy = null; }
          }, READ_DWELL_MS);
        } else if (readTimer) { clearTimeout(readTimer); readTimer = null; }   // пішов угору раніше — скидаємо
      }
    }, { threshold: 0 });
    readSpy.observe(end);
  }

  // Тулбар над мапою: перемикач список/плитка (лише для книг) + «згорнути галузі».
  function mapToolbar(withView) {
    var keys = allGroupKeys();
    var allCol = keys.length > 0 && keys.every(function (k) { return NAV.collapsed.has(k); });
    var view = withView ? '<div class="map-view" role="group" aria-label="Вигляд тем">' +
      '<button type="button" class="mv-btn' + (NAV.view === "list" ? " on" : "") + '" data-map-view="list" title="Список" aria-label="Список">☰</button>' +
      '<button type="button" class="mv-btn' + (NAV.view === "grid" ? " on" : "") + '" data-map-view="grid" title="Плитка" aria-label="Плитка">▦</button></div>' : "";
    return '<div class="map-tools">' +
      '<button type="button" class="map-collapse-all" data-collapse-all>' + (allCol ? "Розгорнути галузі" : "Згорнути галузі") + "</button>" + view + "</div>";
  }
  // Обгортки згортуваної галузі в сайдбарі (label + опційний лічильник + контейнер лінків).
  function sbGroupOpen(key, labelHtml, countHtml) {
    return '<div class="sb-group-label' + (isCollapsed(key) ? " collapsed" : "") + '" data-collapse-group="' + escapeAttr(key) + '">' +
      '<span class="sb-caret" aria-hidden="true">▾</span><span class="sb-gl-txt">' + labelHtml + "</span>" + (countHtml || "") + "</div><div class=\"sb-group\">";
  }
  function sbGroupClose() { return "</div>"; }
  // Акордеон сайдбару КУРСУ: згорнуто все, крім активного модуля. Стан — сесійний SB_OPEN (НЕ персист,
  // окремий data-атрибут, щоб не чіпати спільний із мапою-обкладинкою courses-collapsed/toggleGroup).
  var SB_OPEN = new Set();
  function sbAccGroupOpen(key, labelHtml, countHtml, activeKey) {
    var open = !activeKey || (key === activeKey) || SB_OPEN.has(key);   // без активного — відкрити всі (безпечний фолбек)
    return '<div class="sb-group-label' + (open ? "" : " collapsed") + '" data-sb-acc="' + escapeAttr(key) + '">' +
      '<span class="sb-caret" aria-hidden="true">▾</span><span class="sb-gl-txt">' + labelHtml + "</span>" + (countHtml || "") + "</div><div class=\"sb-group\">";
  }
  // Хлібні крихти вгорі сайдбару: [{label, href?}] — ОСТАННІЙ сегмент = поточний (жирний), проміжні з href — лінки.
  function sbCrumbs(segs) {
    var h = '<nav class="sb-crumbs">';
    for (var i = 0; i < segs.length; i++) {
      if (i) h += '<span class="sb-cr-sep">›</span>';
      var last = i === segs.length - 1;
      if (segs[i].href && !last) h += '<a class="sb-cr" href="' + segs[i].href + '">' + escapeHtml(segs[i].label) + "</a>";
      else h += '<span class="sb-cr' + (last ? " sb-cr-cur" : "") + '">' + escapeHtml(segs[i].label) + "</span>";
    }
    return h + "</nav>";
  }
  // Лічильник «прочитано/усього» на групі (з наявного READ-набору).
  function grpCount(readN, total) { return total ? '<span class="sb-gl-count" title="прочитано / усього">' + readN + "/" + total + "</span>" : ""; }
  // Розділи (§) ПОТОЧНОЇ статті — вставляються під активним рядком (data-target → scroll-spy підсвічує поточний §).
  function sbSections(chap, sections) {
    if (!sections || !sections.length) return "";
    var vs = verSuffix(currentVer);   // § поточної статті — у тій самій версії, що читаємо
    var h = '<a class="sb-link sb-sec" data-target="top" href="#ch=' + chap.slug + '&at=top' + vs + '">↑ Початок</a>';
    for (var i = 0; i < sections.length; i++) {
      var sec = sections[i];
      h += '<a class="sb-link sb-sec" data-target="' + sec.id + '" href="#ch=' + chap.slug + "&at=" + sec.id + vs + '">§ ' + sec.num + " — " + escapeHtml(sec.title) + "</a>";
    }
    return h;
  }

  function applyMapView() {
    var toc = document.querySelector(".toc");
    if (toc) toc.classList.toggle("map-grid", NAV.view === "grid");
    [].forEach.call(document.querySelectorAll("[data-map-view]"), function (b) { b.classList.toggle("on", b.getAttribute("data-map-view") === NAV.view); });
  }
  function applyGroupCollapsed(key) {
    var col = NAV.collapsed.has(key);
    [].forEach.call(document.querySelectorAll(".module-head[data-collapse-group]"), function (mh) {
      if (mh.getAttribute("data-collapse-group") === key) mh.parentElement.classList.toggle("collapsed", col);
    });
    [].forEach.call(document.querySelectorAll(".sb-group-label[data-collapse-group]"), function (sl) {
      if (sl.getAttribute("data-collapse-group") === key) sl.classList.toggle("collapsed", col);
    });
  }
  function toggleGroup(key) {
    if (NAV.collapsed.has(key)) NAV.collapsed.delete(key); else NAV.collapsed.add(key);
    saveNav(); applyGroupCollapsed(key); updateCollapseAllLabel();
  }
  function toggleAllGroups() {
    var keys = allGroupKeys();
    var allCol = keys.length > 0 && keys.every(function (k) { return NAV.collapsed.has(k); });
    keys.forEach(function (k) { if (allCol) NAV.collapsed.delete(k); else NAV.collapsed.add(k); });
    saveNav(); keys.forEach(applyGroupCollapsed); updateCollapseAllLabel();
  }
  function updateCollapseAllLabel() {
    var keys = allGroupKeys();
    var allCol = keys.length > 0 && keys.every(function (k) { return NAV.collapsed.has(k); });
    [].forEach.call(document.querySelectorAll("[data-collapse-all]"), function (b) { b.textContent = allCol ? "Розгорнути галузі" : "Згорнути галузі"; });
  }

  /* ── Індекси за маніфестом ──────────────────────────────────────────── */
  var FLAT = [];          // усі розділи по порядку (вкл. ще не написані)
  var CH_BY_SLUG = {};    // slug → готовий розділ
  BOOK.modules.forEach(function (m) {
    m.chapters.forEach(function (c) {
      c.module = m;
      c.hasBasic = _fileExists(c.status);
      c.hasDetailed = _fileExists(c.dstatus);            // detailed-основна: тема доступна й лише з детальною
      if (c.dir && (c.hasBasic || c.hasDetailed)) {      // файл існує ⟺ є БУДЬ-ЯКА версія
        c.slug = c.dir.split("/").pop();
        var _prim = c.hasBasic ? c.status : c.dstatus;   // яку версію подамо за замовчуванням
        c.draft = _prim !== "done";                      // deeper/update/recheck — чернетка (читається, позначена)
        CH_BY_SLUG[c.slug] = c;
      }
      FLAT.push(c);
    });
  });

  var currentSlug = null;   // який розділ зараз відрендерено
  var currentVer = "";      // яка версія відрендерена («» базова / «d» детальна)
  var pendingTarget = null; // якір, до якого прокрутитись після рендеру
  var pendingTokens = null; // стек попапів, який треба відкрити після рендеру розділу
  var textCache = {};       // кеш завантажених .md

  /* ── Дрібні утиліти ─────────────────────────────────────────────────── */
  function baseOf(name) { return String(name).replace(/\.md$/i, ""); }
  function escapeHtml(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function escapeAttr(s) { return escapeHtml(s).replace(/"/g, "&quot;"); }
  function slugify(s) {
    return String(s).toLowerCase().replace(/[^\wа-яіїєґ]+/gi, "-").replace(/^-+|-+$/g, "").slice(0, 48);
  }
  function findChapterBySlug(slug) { return CH_BY_SLUG[slug] || null; }

  function fetchText(url) {
    if (textCache[url]) return Promise.resolve(textCache[url]);
    return fetch(url, { cache: "no-cache" }).then(function (res) {
      if (!res.ok) throw new Error(res.status + " " + res.statusText + " — " + url);
      return res.text();
    }).then(function (t) { textCache[url] = t; return t; });
  }

  /* ════════════════════════════════════════════════════════════════════
     1) ІНЛАЙН-РОЗМІТКА: `code`, [лінк](…), **жирний**, *курсив*
     ════════════════════════════════════════════════════════════════════ */
  function renderInline(s, ctx) {
    s = escapeHtml(s);
    var codes = [];
    s = s.replace(/`([^`]+)`/g, function (m, c) { codes.push(c); return "@C" + (codes.length - 1) + "@"; });
    s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function (m, txt, href) {
      var r = resolveHref(href.trim(), txt, ctx);
      if (r.cross) return '<a class="xbook-link" href="#" data-xbook="' + escapeAttr(r.cross) + '">' + txt + "</a>";
      var ext = r.external ? ' target="_blank" rel="noopener"' : "";
      return '<a href="' + escapeAttr(r.href) + '"' + ext + ">" + txt + "</a>";
    });
    s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/__([^_]+)__/g, "<strong>$1</strong>");
    s = s.replace(/\*([^*\n]+)\*/g, "<em>$1</em>");
    s = s.replace(/(^|[\s(«"])_([^_\n]+)_(?=[\s).,;:!?»"]|$)/g, "$1<em>$2</em>");
    s = s.replace(/@C(\d+)@/g, function (m, i) { return "<code>" + codes[+i] + "</code>"; });
    return s;
  }

  /* Крос-посилання root:<книга>/<тема>[/<file>][#<anchor>] → дескриптор для popup (v7) */
  function resolveCrossBook(href) {
    var rest = href.replace(/^root:/i, "");
    var frag = ""; var hi = rest.indexOf("#");
    if (hi >= 0) { frag = rest.slice(hi + 1); rest = rest.slice(0, hi); }
    var segs = rest.split("/").filter(Boolean);
    var book = segs.shift() || "";
    var slug = segs.shift() || "";
    var file = segs.join("/");                 // порожнє → головний файл розділу
    return { href: "#", external: false, cross: [book, slug, file, frag].join("|") };
  }

  /* Перетворення .md-лінків на маршрути книги (#ch=…&at=…) */
  function resolveHref(href, text, ctx) {
    if (/^(https?:|mailto:|tel:)/i.test(href)) return { href: href, external: true };
    if (href.charAt(0) === "#") return { href: href, external: false };
    if (/^root:/i.test(href)) return resolveCrossBook(href);
    var frag = ""; var hi = href.indexOf("#");
    if (hi >= 0) { frag = href.slice(hi + 1); href = href.slice(0, hi); }
    if (!/\.md$/i.test(href)) return { href: href, external: false };

    var parts = href.split("/");
    var file = parts.pop();
    var folder = null;
    for (var k = parts.length - 1; k >= 0; k--) {
      var seg = parts[k];
      if (!seg || seg === "." || seg === "..") continue;
      folder = seg; break;                    // останній значущий сегмент шляху = slug розділу (працює і для chNN-…, і для slug-only)
    }
    var slug = folder || ctx.currentSlug;
    var base = baseOf(file);
    var chap = findChapterBySlug(slug);
    var secM = text && String(text).match(/§\s*(\d+(?:\.\d+){1,2})/);

    var at;
    if (slug === ctx.currentSlug) {
      if (chap && base === baseOf(chap.main)) {
        at = secM ? "sec-" + secM[1].split(".").join("-") : (/^sec-/.test(frag) ? frag : "top");
      } else { at = "hist-" + base; }
      return { href: "#ch=" + slug + "&at=" + at + verSuffix(ctx.ver), external: false };   // та сама стаття → лишаємось у поточній версії
    }
    if (!chap || chap.status !== "done") return { href: "#ch=" + slug, external: false };
    if (base !== baseOf(chap.main)) at = "hist-" + base;
    else at = secM ? "sec-" + secM[1].split(".").join("-") : "";
    return { href: "#ch=" + slug + (at ? "&at=" + at : ""), external: false };
  }

  /* ════════════════════════════════════════════════════════════════════
     2) БЛОК-ПАРСЕР: рядки → токени
     ════════════════════════════════════════════════════════════════════ */
  function mdBlocks(text) {
    var lines = text.replace(/\r\n?/g, "\n").split("\n");
    var blocks = [], i = 0, n = lines.length;
    var reHeading = /^(#{1,6})\s+(.*)$/;
    var reHr = /^\s*(-{3,}|\*{3,}|_{3,})\s*$/;
    var reImg = /^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$/;
    var reListItem = /^\s*([-*+]|\d+\.)\s+/;

    while (i < n) {
      var line = lines[i];
      if (/^\s*$/.test(line)) { i++; continue; }

      // блок «Перед читанням»: <preknowlist> … список передумов … </preknowlist> → згорнутий <details>
      if (/^\s*<preknowlist>\s*$/i.test(line)) {
        i++;
        var pkItems = [];
        while (i < n && !/^\s*<\/preknowlist>\s*$/i.test(lines[i])) {
          var pl = lines[i]; i++;
          if (/^\s*$/.test(pl)) continue;
          if (reListItem.test(pl)) pkItems.push(pl.replace(reListItem, ""));
          else if (pkItems.length) pkItems[pkItems.length - 1] += " " + pl.trim();   // продовження елемента
          else pkItems.push(pl.trim());
        }
        i++; // закривний </preknowlist>
        blocks.push({ type: "preknow", items: pkItems });
        continue;
      }

      // групи «те саме кількома мовами»: :::tabs … фенси з мовою … :::
      var tabsOpen = line.match(/^\s*:::\s*(?:tabs|code)\s*$/);
      if (tabsOpen) {
        i++;
        var tabsArr = [];
        while (i < n && !/^\s*:::\s*$/.test(lines[i])) {
          var f = lines[i].match(/^\s*```(.*)$/);
          if (f) {
            var cbuf = []; i++;
            while (i < n && !/^\s*```\s*$/.test(lines[i])) { cbuf.push(lines[i]); i++; }
            i++; // закривний ```
            tabsArr.push({ lang: f[1].trim(), code: cbuf.join("\n") });
          } else { i++; } // пропускаємо порожні/сторонні рядки між фенсами
        }
        i++; // закривний :::
        if (tabsArr.length > 1) blocks.push({ type: "codetabs", tabs: tabsArr });
        else if (tabsArr.length === 1) blocks.push({ type: "pre", code: tabsArr[0].code, lang: tabsArr[0].lang });
        continue;
      }

      var fence = line.match(/^\s*```(.*)$/);
      if (fence) {
        var buf = []; i++;
        while (i < n && !/^\s*```\s*$/.test(lines[i])) { buf.push(lines[i]); i++; }
        i++;
        blocks.push({ type: "pre", code: buf.join("\n"), lang: fence[1].trim() });
        continue;
      }
      var h = line.match(reHeading);
      if (h) { blocks.push({ type: "heading", level: h[1].length, text: h[2].trim() }); i++; continue; }
      if (reHr.test(line)) { blocks.push({ type: "hr" }); i++; continue; }

      var img = line.match(reImg);
      if (img) {
        var caption = null;
        if (i + 1 < n) {
          var cap = lines[i + 1].match(/^\s*\*(.+)\*\s*$/);
          if (cap) { caption = cap[1]; i++; }
        }
        blocks.push({ type: "figure", alt: img[1], src: img[2], caption: caption });
        i++; continue;
      }
      if (/^\s*>/.test(line)) {
        var q = [];
        while (i < n && /^\s*>/.test(lines[i])) { q.push(lines[i].replace(/^\s*>\s?/, "")); i++; }
        blocks.push({ type: "quote", lines: q });
        continue;
      }
      if (reListItem.test(line)) {
        var ordered = /^\s*\d+\.\s+/.test(line), items = [];
        while (i < n && reListItem.test(lines[i])) {
          items.push(lines[i].replace(reListItem, "")); i++;
          while (i < n && /^\s+\S/.test(lines[i]) && !reListItem.test(lines[i]) && !/^\s*$/.test(lines[i])) {
            items[items.length - 1] += " " + lines[i].trim(); i++;
          }
        }
        blocks.push({ type: "list", ordered: ordered, items: items });
        continue;
      }
      if (line.indexOf("|") >= 0 && i + 1 < n && /-/.test(lines[i + 1]) && /^\s*\|?[\s:|-]+$/.test(lines[i + 1])) {
        var rows = [];
        while (i < n && lines[i].indexOf("|") >= 0 && !/^\s*$/.test(lines[i])) { rows.push(lines[i]); i++; }
        blocks.push({ type: "table", rows: rows });
        continue;
      }
      // абзац
      var pbuf = [line]; i++;
      while (i < n) {
        var l = lines[i];
        if (/^\s*$/.test(l)) break;
        if (reHeading.test(l) || /^\s*```/.test(l) || /^\s*:::/.test(l) || reHr.test(l) || reImg.test(l) ||
            /^\s*>/.test(l) || reListItem.test(l)) break;
        pbuf.push(l); i++;
      }
      blocks.push({ type: "para", text: pbuf.join(" ") });
    }
    return blocks;
  }

  /* ════════════════════════════════════════════════════════════════════
     2.5) КОД: підсвітка синтаксису + вкладки «те саме кількома мовами»
     ════════════════════════════════════════════════════════════════════ */
  var CODE_KW = ("if else elif for while do switch case default break continue return goto yield " +
    "function func fn def lambda class struct enum union interface trait impl namespace module mod package template typename typedef type " +
    "public private protected static const constexpr final abstract virtual override inline extern mutable volatile register " +
    "let var val auto new delete this self super sizeof typeof instanceof operator using include import from export as with " +
    "try catch except finally throw throws raise defer panic recover match when where in of is and or not xor async await go select chan " +
    "void int uint long short char float double bool boolean unsigned signed string str byte rune usize isize " +
    "true false null nil none None True False undefined nullptr NULL pub crate dyn ref move Box Vec Option Result Some Ok Err " +
    "pass global nonlocal del assert print println printf cout cin endl std namespace static_cast reinterpret_cast dynamic_cast const_cast")
    .split(/\s+/).reduce(function (m, w) { m[w] = 1; return m; }, {});

  var LANG_LABELS = {
    c: "C", h: "C", cpp: "C++", "c++": "C++", cxx: "C++", cc: "C++", hpp: "C++",
    py: "Python", python: "Python", micropython: "MicroPython", upy: "MicroPython", js: "JavaScript", javascript: "JavaScript", jsx: "JavaScript",
    ts: "TypeScript", typescript: "TypeScript", tsx: "TypeScript", go: "Go", golang: "Go",
    rust: "Rust", rs: "Rust", java: "Java", kt: "Kotlin", kotlin: "Kotlin", swift: "Swift",
    cs: "C#", csharp: "C#", rb: "Ruby", ruby: "Ruby", php: "PHP", sh: "Shell", bash: "Bash", zsh: "Shell",
    sql: "SQL", html: "HTML", css: "CSS", json: "JSON", yaml: "YAML", yml: "YAML", toml: "TOML",
    lua: "Lua", r: "R", scala: "Scala", dart: "Dart", asm: "Asm", llvm: "LLVM IR", ir: "IR", vhdl: "VHDL", verilog: "Verilog",
    // ПЛАТФОРМИ, не мови. Той самий приклад під різні МК — це вкладки «Arduino / ESP-IDF /
    // STM32», а не «C / C / C»: читачеві треба знати, під що код, а не якою мовою.
    // Підсвітка в усіх — типова C-родина (highlight() бере її за замовчуванням).
    arduino: "Arduino", ino: "Arduino",
    "esp-idf": "ESP-IDF", espidf: "ESP-IDF", esp32: "ESP-IDF",
    stm32: "STM32 HAL", "stm32-hal": "STM32 HAL", "stm32-ll": "STM32 LL",
    zephyr: "Zephyr", "pico-sdk": "Pico SDK", avr: "AVR"
  };
  function langKey(l) { return (l || "").toLowerCase().replace(/^\./, ""); }
  function langLabel(l) {
    var k = langKey(l);
    return LANG_LABELS[k] || (l ? l.charAt(0).toUpperCase() + l.slice(1) : "код");
  }

  // регекс-токенайзер: коментарі / рядки / числа / ключові / виклики. Працює на сирому тексті,
  // кожен шматок екрануємо окремо (тому «<», «>» усередині коду не ламають розмітку).
  function highlight(src, lang) {
    var k = langKey(lang);
    var hashCmt = /^(py|python|micropython|upy|sh|bash|zsh|rb|ruby|r|toml|yaml|yml)$/.test(k);
    var semiCmt = /^(asm|llvm|ir)$/.test(k);
    var out = "", i = 0, N = src.length;
    function span(cls, s) { return '<span class="tok-' + cls + '">' + escapeHtml(s) + "</span>"; }
    var wordCh = /[A-Za-z0-9_$]/, wordStart = /[A-Za-z_$]/, digit = /[0-9]/, numCh = /[0-9a-fA-FxXoObB_.]/;
    while (i < N) {
      var c = src[i], c2 = src[i + 1];
      if (c === "/" && c2 === "/") { var j = src.indexOf("\n", i); if (j < 0) j = N; out += span("cmt", src.slice(i, j)); i = j; continue; }
      if (hashCmt && c === "#") { var j = src.indexOf("\n", i); if (j < 0) j = N; out += span("cmt", src.slice(i, j)); i = j; continue; }
      if (semiCmt && c === ";") { var j = src.indexOf("\n", i); if (j < 0) j = N; out += span("cmt", src.slice(i, j)); i = j; continue; }
      if (c === "/" && c2 === "*") { var j = src.indexOf("*/", i + 2); j = j < 0 ? N : j + 2; out += span("cmt", src.slice(i, j)); i = j; continue; }
      if (c === '"' || c === "'" || c === "`") {
        var q = c, j = i + 1;
        while (j < N) { if (src[j] === "\\") { j += 2; continue; } if (src[j] === q) { j++; break; } j++; }
        out += span("str", src.slice(i, j)); i = j; continue;
      }
      if (digit.test(c) || (c === "." && digit.test(c2 || ""))) {
        var j = i + 1; while (j < N && numCh.test(src[j])) j++;
        out += span("num", src.slice(i, j)); i = j; continue;
      }
      if (wordStart.test(c)) {
        var j = i + 1; while (j < N && wordCh.test(src[j])) j++;
        var w = src.slice(i, j);
        if (CODE_KW[w]) out += span("kw", w);
        else if (src[j] === "(") out += span("fn", w);
        else out += escapeHtml(w);
        i = j; continue;
      }
      out += escapeHtml(c); i++;
    }
    return out;
  }

  function renderCode(code, lang) {
    return '<pre class="code"><code class="lang-' + escapeHtml(langKey(lang)) + '">' + highlight(code, lang) + "</code></pre>";
  }
  function renderCodeTabs(tabs) {
    var bar = "", body = "";
    for (var k = 0; k < tabs.length; k++) {
      var t = tabs[k], on = k === 0, lc = langKey(t.lang);
      bar += '<button class="codetabs__tab' + (on ? " on" : "") + '" type="button" role="tab" data-lang="' +
        escapeHtml(lc) + '" aria-selected="' + (on ? "true" : "false") + '">' + escapeHtml(langLabel(t.lang)) + "</button>";
      body += '<div class="codetabs__panel"' + (on ? "" : " hidden") + ' role="tabpanel">' + renderCode(t.code, t.lang) + "</div>";
    }
    return '<div class="codetabs"><div class="codetabs__bar" role="tablist">' + bar + "</div>" + body + "</div>";
  }

  /* вибір мови коду — СПИСОК ПРІОРИТЕТІВ (топ-1/2/3), спільний на всю сторінку (й попапи),
     із пам'яттю в localStorage. Кнопку-меню пріоритетів додає codelang.js; тут — застосування. */
  function readCodeLangPrio() {
    try {
      var raw = localStorage.getItem("courses-codelang-prio");
      if (raw) { var a = JSON.parse(raw); if (a && typeof a.length === "number") return [].slice.call(a).filter(Boolean); }
      var one = localStorage.getItem("courses-codelang");   // сумісність зі старим одиничним вибором
      return one ? [one] : [];
    } catch (e) { return []; }
  }
  var CODELANG_PRIO = readCodeLangPrio();
  function syncCodeTabs() {
    var boxes = document.querySelectorAll(".codetabs");
    for (var b = 0; b < boxes.length; b++) {
      var box = boxes[b], tabs = box.querySelectorAll(".codetabs__tab"), panels = box.querySelectorAll(".codetabs__panel");
      var idx = -1;
      // обрати НАЙВИЩУ доступну мову зі списку пріоритетів; якщо жодної нема — перша вкладка
      for (var p = 0; p < CODELANG_PRIO.length && idx < 0; p++)
        for (var t = 0; t < tabs.length; t++) { if (tabs[t].getAttribute("data-lang") === CODELANG_PRIO[p]) { idx = t; break; } }
      if (idx < 0) idx = 0;
      for (var t = 0; t < tabs.length; t++) {
        var on = t === idx;
        tabs[t].classList.toggle("on", on);
        tabs[t].setAttribute("aria-selected", on ? "true" : "false");
        if (panels[t]) panels[t].hidden = !on;
      }
    }
  }
  function pickCodeLang(lang) {
    // клік по вкладці підіймає її мову на топ-1, решта пріоритетів зсуваються (макс. 3)
    var next = [lang];
    for (var i = 0; i < CODELANG_PRIO.length && next.length < 3; i++)
      if (CODELANG_PRIO[i] !== lang) next.push(CODELANG_PRIO[i]);
    CODELANG_PRIO = next;
    try {
      localStorage.setItem("courses-codelang-prio", JSON.stringify(next));
      localStorage.setItem("courses-codelang", lang);   // сумісність
    } catch (e) {}
    syncCodeTabs();
    try { window.dispatchEvent(new CustomEvent("codelangchange", { detail: { prio: next, from: "tab" } })); } catch (e) {}
  }
  // зовнішні зміни (меню пріоритетів у codelang.js) → перечитати й пересинхронити
  window.addEventListener("codelangchange", function (e) {
    if (e && e.detail && e.detail.from === "tab") return;   // власний клік уже застосовано
    CODELANG_PRIO = readCodeLangPrio();
    syncCodeTabs();
  });

  /* ════════════════════════════════════════════════════════════════════
     3) ТОКЕНИ → HTML (+ збір секцій і прив'язок історій)
     ════════════════════════════════════════════════════════════════════ */
  function renderTokens(tokens, ctx) {
    var html = "", sections = [];
    for (var t, j = 0; j < tokens.length; j++) {
      t = tokens[j];
      switch (t.type) {
        case "heading":
          html += renderHeading(t, ctx, sections); break;
        case "pre":
          html += renderCode(t.code, t.lang); break;
        case "codetabs":
          html += renderCodeTabs(t.tabs); break;
        case "hr":
          html += "<hr>"; break;
        case "figure":
          html += renderFigure(t, ctx); break;
        case "list":
          var tag = t.ordered ? "ol" : "ul";
          html += "<" + tag + ">" + t.items.map(function (it) { return "<li>" + renderInline(it, ctx) + "</li>"; }).join("") + "</" + tag + ">";
          break;
        case "preknow":
          if (t.items.length) {
            html += '<details class="preknow">' +
              '<summary class="preknow-sum">' +
                '<svg class="preknow-ico" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l9 5-9 5-9-5 9-5zM3 12l9 5 9-5M3 16.5l9 5 9-5"/></svg>' +
                '<span class="preknow-ttl">Перед читанням</span>' +
                '<span class="preknow-count">' + t.items.length + '</span>' +
                '<svg class="preknow-caret" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>' +
              '</summary>' +
              '<ul class="preknow-list">' +
              t.items.map(function (it) { return "<li>" + renderInline(it, ctx) + "</li>"; }).join("") +
              '</ul></details>';
          }
          break;
        case "table":
          html += renderTable(t.rows, ctx); break;
        case "quote":
          html += renderQuote(t, ctx, sections); break;
        case "para":
          html += "<p>" + renderInline(t.text, ctx) + "</p>"; break;
      }
    }
    return { html: html, sections: sections };
  }

  function renderHeading(t, ctx, sections) {
    if (t.level === 2) {
      var m = t.text.match(/^(\d+(?:\.\d+){1,2})\s+(.*)$/);   // «1.1 …» (embedded) або «1.2.3 …» (М.Р.Т)
      if (m) {
        var id = "sec-" + m[1].split(".").join("-");
        sections.push({ num: m[1], title: m[2], id: id });
        return '<span id="' + id + '" class="anc"></span><h2 class="sec-h"><span class="sn">§ ' +
          m[1] + "</span>" + renderInline(m[2], ctx) + "</h2>";
      }
      var hid = "h-" + slugify(t.text);
      return '<span id="' + hid + '" class="anc"></span><h2 class="hist-h">' + renderInline(t.text, ctx) + "</h2>";
    }
    if (t.level === 1) return '<h2 class="hist-h">' + renderInline(t.text, ctx) + "</h2>";
    var tg = t.level === 3 ? "h3" : "h4";
    return "<" + tg + ">" + renderInline(t.text, ctx) + "</" + tg + ">";
  }

  function renderFigure(t, ctx) {
    var src = t.src.trim();
    if (/^\/root\//.test(src)) src = SITE_ROOT + src.slice(1);  // від кореня репо → префікс розгортання
    else if (!/^https?:|^\//.test(src)) src = (ctx.base != null ? ctx.base : BASE) + ctx.dir + "/" + src;
    var h = '<figure><img src="' + escapeAttr(src) + '" alt="' + escapeAttr(t.alt) + '" loading="lazy">';
    if (t.caption) h += "<figcaption>" + renderInline(t.caption, ctx) + "</figcaption>";
    return h + "</figure>";
  }

  function renderTable(rows, ctx) {
    var clean = rows.filter(function (r) { return r.trim(); });
    if (clean.length < 2) return "";
    var split = function (r) { return r.replace(/^\s*\|/, "").replace(/\|\s*$/, "").split("|").map(function (c) { return c.trim(); }); };
    var head = split(clean[0]);
    var body = clean.slice(2).map(split);
    var h = "<table><thead><tr>" + head.map(function (c) { return "<th>" + renderInline(c, ctx) + "</th>"; }).join("") + "</tr></thead><tbody>";
    h += body.map(function (r) { return "<tr>" + r.map(function (c) { return "<td>" + renderInline(c, ctx) + "</td>"; }).join("") + "</tr>"; }).join("");
    return h + "</tbody></table>";
  }

  function renderQuote(t, ctx, sections) {
    var text = t.lines.join("\n").trim();
    var kind = null, icon = null;
    if (/^🔧/.test(text)) { kind = "eng"; icon = "🔧"; }
    else if (/^🏠/.test(text)) { kind = "eng"; icon = "🏠"; }   // «де це вдома» (книга «Хімія»)
    else if (/^🧪/.test(text)) { kind = "eng"; icon = "🧪"; }   // «спробуй сам»
    else if (/^💡/.test(text)) { kind = "nav"; icon = "💡"; }   // «одним реченням»
    else if (/^📜/.test(text)) { kind = "hist"; icon = "📜"; }
    else if (/^🧮/.test(text)) { kind = "math"; icon = "🧮"; }   // математична вставка
    else if (/^(⚙️|⚙)/.test(text)) { kind = "proj"; icon = "⚙️"; }  // алгоритм/проєкт
    else if (/^🔌/.test(text)) { kind = "comp"; icon = "🔌"; }   // компонентна вставка
    else if (/^📋/.test(text)) { kind = "api"; icon = "📋"; }   // довідка/API-вставка
    else if (/^🔗/.test(text)) { kind = "xref"; icon = "🔗"; }   // міст на іншу тему/предмет → крос-попап
    else if (/^(▶️|▶)/.test(text)) { kind = "nav"; icon = "▶️"; }

    if (!kind) {
      var gp = text.split(/\n\s*\n/).map(function (p) { return "<p>" + renderInline(p.replace(/\n/g, " "), ctx) + "</p>"; }).join("");
      return "<blockquote>" + gp + "</blockquote>";
    }
    // знайти посилання на історичні вставки ЦЬОГО розділу (для тизера й сайдбару)
    var primary = null;
    var links = text.match(/\]\(([^)]+\.md)\)/g);
    if (links && ctx.histBases) {
      links.forEach(function (lm) {
        var hp = lm.match(/\]\(([^)]+)\)/)[1];
        var b = baseOf(hp.split("/").pop());
        if (ctx.histBases.has(b)) { if (!primary) primary = b; ctx.attach.push({ base: b, after: sections.length - 1 }); }
      });
    }
    var body = text.replace(/^(🔧|🏠|🧪|💡|📜|🧮|⚙️|⚙|🔌|📋|🔗|▶️|▶)\s*/, "");

    // 🔗-вставка з root:-лінком → УСЯ картка клікабельна → крос-попап на іншу тему
    if (kind === "xref") {
      var bm = body.match(/\]\((root:[^)]+)\)/i);
      if (bm) {
        var cross = resolveCrossBook(bm[1]).cross;
        var flatx = body.replace(/\s*\[([^\]]+)\]\(root:[^)]+\)/ig, "").trim();
        return '<a class="callout callout-nav hist-teaser xref-teaser" href="#" data-xbook="' + escapeAttr(cross) + '" title="Відкрити повну тему">' +
          '<span class="callout-ico">🔗<span class="hist-expand" aria-hidden="true">⤢</span></span>' +
          '<div class="callout-body">' + renderInline(flatx.replace(/\n/g, " "), ctx) + "</div>" +
          '<span class="teaser-share" data-share-token="b:' + escapeAttr(cross) + '" role="button" tabindex="0" title="Копіювати посилання" aria-label="Копіювати посилання">🔗</span>' +
          "</a>";
      }
    }

    // вставка-картка (📜 hist · 🧮 math · 🔌 comp · ⚙️ proj) → УСЯ клікабельна → popup.
    // base беремо з лінка (primary); якщо тизер без лінка — наступна вставка цього типу за порядком.
    if (kind === "hist" || kind === "math" || kind === "comp" || kind === "proj" || kind === "api") {
      var ibase = primary;
      if (!ibase && ctx.insQueue && ctx.insQueue[kind] && ctx.insQueue[kind].length) { ibase = ctx.insQueue[kind].shift(); if (ibase) ctx.attach.push({ base: ibase, after: sections.length - 1 }); }
      if (ibase) {
        var flat = body.replace(/\s*\[([^\]]+)\]\(([^)]+)\)/g, function (m, tx, href) {
          var b = baseOf(href.split("/").pop());
          return (ctx.histBases && ctx.histBases.has(b)) ? "" : tx;   // маркер вставки прибрати; сторонній лінк → текст
        }).trim();
        return '<a class="callout callout-' + kind + ' hist-teaser" href="#" data-hist="' + ibase + '" title="Розгорнути вставку">' +
          '<span class="callout-ico">' + icon + '<span class="hist-expand" aria-hidden="true">⤢</span></span>' +
          '<div class="callout-body">' + renderInline(flat.replace(/\n/g, " "), ctx) + "</div>" +
          '<span class="teaser-share" data-share-token="h:' + ibase + '" role="button" tabindex="0" title="Копіювати посилання" aria-label="Копіювати посилання">🔗</span>' +
          "</a>";
      }
    }

    var paras = body.split(/\n\s*\n/);
    var inner = paras.length === 1
      ? renderInline(paras[0].replace(/\n/g, " "), ctx)
      : paras.map(function (p) { return "<p>" + renderInline(p.replace(/\n/g, " "), ctx) + "</p>"; }).join("");
    return '<div class="callout callout-' + kind + '"><span class="callout-ico">' + icon +
      '</span><div class="callout-body">' + inner + "</div></div>";
  }

  /* ════════════════════════════════════════════════════════════════════
     4) РОЗБІР РОЗДІЛУ Й ІСТОРІЙ
     ════════════════════════════════════════════════════════════════════ */
  function parseMain(text, ctx) {
    var blocks = mdBlocks(text), idx = 0;
    if (blocks[0] && blocks[0].type === "heading" && blocks[0].level === 1) idx = 1;
    var introHtml = "";
    if (!isBookLike()) {   // окремий «вступ» лише у старих embedded-розділах (перед ## секціями);
      var intro = [];            // book-тема — це суцільна стаття, увесь текст іде в тіло
      while (idx < blocks.length && blocks[idx].type === "para") { intro.push(blocks[idx]); idx++; }
      introHtml = intro.map(function (t) { return renderInline(t.text, ctx); }).join("<br><br>");
    }
    var r = renderTokens(blocks.slice(idx), ctx);
    return { introHtml: introHtml, bodyHtml: r.html, sections: r.sections };
  }

  function parseHistory(text, filename, baseCtx) {
    var blocks = mdBlocks(text), idx = 0, title = filename;
    if (blocks[0] && blocks[0].type === "heading" && blocks[0].level === 1) {
      title = blocks[0].text.replace(/^(📜|🧮|🔌|⚙️|⚙)\s*/, "").trim(); idx = 1;
    }
    var introHtml = "";
    if (blocks[idx] && blocks[idx].type === "quote") {
      var qt = blocks[idx].lines.join("\n").trim();
      if (!/^(🔧|📜|▶️|▶)/.test(qt)) { introHtml = renderInline(qt.replace(/\n+/g, " "), baseCtx); idx++; }
    }
    var ctx = Object.assign({}, baseCtx, { attach: [] });
    var r = renderTokens(blocks.slice(idx), ctx);
    return { base: baseOf(filename), title: title, introHtml: introHtml, bodyHtml: r.html };
  }

  /* ════════════════════════════════════════════════════════════════════
     5) РЕНДЕР РОЗДІЛУ
     ════════════════════════════════════════════════════════════════════ */
  // картка-тизер історичної вставки (для авто-банера зверху розділу)
  function histTeaserCard(base, label) {
    var k = (base.match(/^(hist|math|comp|proj|api)-/) || [])[1] || "hist";
    var ic = { hist: "📜", math: "🧮", comp: "🔌", proj: "⚙️", api: "📋" }[k];
    return '<a class="callout callout-' + k + ' hist-teaser" href="#" data-hist="' + base + '" title="Розгорнути вставку">' +
      '<span class="callout-ico">' + ic + '<span class="hist-expand" aria-hidden="true">⤢</span></span>' +
      '<div class="callout-body">' + escapeHtml(label) + "</div>" +
      '<span class="teaser-share" data-share-token="h:' + base + '" role="button" tabindex="0" title="Копіювати посилання" aria-label="Копіювати посилання">🔗</span>' +
      "</a>";
  }

  function renderChapter(chap, ver) {
    var dir = chap.dir;
    // single-link + fallback: v=d → детальна (нема → базова); дефолт → базова (нема → детальна)
    var wantD = (ver === "d");
    var mainFile = wantD ? (chap.hasDetailed ? chap.slug + "-d.md" : chap.main)
                         : (chap.hasBasic ? chap.main : chap.slug + "-d.md");
    var mainUrl = BASE + dir + "/" + mainFile;
    if (!textCache[mainUrl]) setContent('<div class="state"><div class="spinner"></div>Завантаження розділу…</div>');   // кеш є (напр., перемикання версій) → без спінера, миттєво, як stack
    var histFiles = chap.histories || [];
    var allFiles = histFiles.concat(chap.extras || []);   // історії + extras — усі як відкривні модалки
    Promise.all([fetchText(mainUrl)].concat(allFiles.map(function (f) { return fetchText(BASE + dir + "/" + f); })))
      .then(function (texts) {
        var mainText = texts[0], specTexts = texts.slice(1);
        var ctx = {
          currentSlug: chap.slug, dir: dir, ver: ver,
          histBases: new Set(allFiles.map(baseOf)), attach: [],
          insQueue: (function () { var q = { hist: [], math: [], comp: [], proj: [], api: [] }; allFiles.forEach(function (f) { var b = baseOf(f); var k = (b.match(/^(hist|math|comp|proj|api)-/) || [])[1]; if (k && q[k]) q[k].push(b); }); return q; })()
        };
        var pm = parseMain(mainText, ctx);
        var arts = allFiles.map(function (f, k) { var a = parseHistory(specTexts[k], f, ctx); a.type = specType(f); return a; });

        // банер угорі розділу — лише ІСТОРІЇ, на які в тексті немає 📜-тизера (як було)
        var attached = {}; ctx.attach.forEach(function (a) { attached[a.base] = true; });
        var titleByBase = {}; arts.forEach(function (a) { titleByBase[a.base] = a.title; });
        var leftover = allFiles.map(baseOf).filter(function (b) { return !attached[b]; });
        var banner = "";
        if (leftover.length) {
          banner = '<div class="hist-banner"><div class="hist-banner-label">Вставки до теми</div>' +
            leftover.map(function (b) { return histTeaserCard(b, titleByBase[b] || b); }).join("") + "</div>";
        }

        var html = '<span id="top" class="anc"></span>';
        html += chapterHeader(chap, null, ver);
        var introBlock = (pm.introHtml && !isBookLike()) ? '<p class="ch-intro ch-intro-body">' + pm.introHtml + '</p>' : '';
        html += '<div class="sec content-body">' + courseTopNav(chap) + introBlock + banner + pm.bodyHtml + courseBottomNav(chap) +
          '<span id="read-end" class="read-sentinel" aria-hidden="true"></span></div>';
        arts.forEach(function (a) { html += histModal(a); });   // приховані popup-вікна (історії + extras)
        setContent(html);
        document.body.classList.add("reading");

        buildChapterSidebar(chap, pm.sections, ctx.attach, arts);
        setupScrollSpy();
        setupReadTracking(chap.slug);   // доскролив до #read-end → тема прочитана
        scrollToAnchor(pendingTarget); appliedAt = pendingTarget; pendingTarget = null;
        syncModals(pendingTokens || []); pendingTokens = null;     // відновити стек попапів (deep-link / «назад-вперед»)
        if (chap.hasBasic && chap.hasDetailed) {                   // префетч іншої версії → перемикач зверху працює миттєво (обидві в кеші)
          fetchText(BASE + dir + "/" + (wantD ? chap.main : chap.slug + "-d.md")).catch(function () {});
        }
      })
      .catch(function (e) {
        setContent('<div class="state error"><h2>Не вдалося завантажити розділ</h2><p>' +
          escapeHtml(e.message) + '</p><p>Схоже, книгу відкрито без веб-сервера (<code>file://</code>) — браузер блокує завантаження розділів. ' +
          'Поклади її на GitHub Pages (Settings → Pages → from root), або для локального перегляду запусти сервер із кореня репо: <code>python -m http.server</code>.</p>' +
          '<p><a href="#">← На головну</a></p></div>');
        buildCoverSidebar();
      });
  }

  function chapterHeader(chap, introHtml, ver) {
    // Курс-режим: номер поточного кроку (Модуль.Розділ.Крок) дрібним шрифтом у рядку заголовка — висоту панелі не змінює.
    var kn = "";
    if (BOOK.course) {
      var lst = courseNavList(), ci = courseCurrentIndex(chap);
      if (ci >= 0) kn = ' <span class="ch-kn">' + lst[ci].kn + "</span>";
    }
    var vsw = versionSwitch(chap, ver || "");   // перемикач версій — праворуч у панелі (лише коли є обидві)
    if (isBookLike()) {   // стаття книги/довідника: компактна sticky-панель, галузь + назва, відтінок книги
      return '<header class="ch-header ch-header-book" style="--book-accent:' + (BOOK.accent || "") + '"><div class="ch-head-main"><div class="ch-label">' +
        escapeHtml((chap.module && chap.module.title) || "") + "</div><h1>" + escapeHtml(chap.title) + kn + "</h1></div>" + vsw + "</header>";
    }
    var m = chap.module;
    var lbl = "Модуль " + m.n + " · " + escapeHtml(m.title) +
      (BOOK.course ? "" : " &nbsp;/&nbsp; Розділ " + m.n + "." + chap.n);   // у курсі номер кроку — біля заголовка (kn), не «розділ» зі старої нумерації
    var h = '<header class="ch-header"><div class="ch-head-main"><div class="ch-label">' + lbl + "</div><h1>" + escapeHtml(chap.title) + kn + "</h1>";
    if (introHtml) h += '<p class="ch-intro">' + introHtml + "</p>";
    return h + "</div>" + vsw + "</header>";
  }

  function histModal(a) {
    var t = SPEC_META[a.type] || SPEC_META.hist;
    var h = '<div class="hist-modal spec-' + (a.type || "hist") + '" id="histmodal-' + a.base + '" role="dialog" aria-modal="true" aria-label="' +
      escapeAttr(a.title) + '" hidden><div class="hist-modal-backdrop" data-close></div>' +
      '<div class="hist-modal-dialog">' +
      '<button class="hist-modal-share" type="button" data-share aria-label="Копіювати посилання" title="Копіювати посилання на цю вставку">🔗</button>' +
      '<button class="hist-modal-close" type="button" data-close aria-label="Закрити">✕</button>' +
      '<div class="hist-modal-scroll"><div class="hist-modal-head"><div class="hist-art-label">' + t.emoji + " " + t.modal + "</div><h1>" +
      escapeHtml(a.title) + "</h1>";
    if (a.introHtml) h += '<div class="hist-intro">' + a.introHtml + "</div>";
    h += '</div><div class="content-body">' + a.bodyHtml + "</div></div></div></div>";
    return h;
  }

  /* ════════════════════════════════════════════════════════════════════
     6) САЙДБАР РОЗДІЛУ
     ════════════════════════════════════════════════════════════════════ */
  function buildChapterSidebar(chap, sections, attach, arts) {
    if (BOOK.course) { return buildCourseChapterSidebar(chap, sections); }
    if (isBookLike()) { return buildBookChapterSidebar(chap, sections); }
    var titleByBase = {}; arts.forEach(function (a) { titleByBase[a.base] = a.title; });
    var attachedAfter = {}; var attachedSet = {};
    attach.forEach(function (a) {
      (attachedAfter[a.after] = attachedAfter[a.after] || []).push(a.base);
      attachedSet[a.base] = true;
    });
    var slug = chap.slug;
    var usedSub = {};
    function subLink(base) {
      if (usedSub[base]) return "";          // та сама історія може згадуватись кількома callout-ами
      usedSub[base] = true;
      return '<a class="sb-sub" data-hist="' + base + '" href="#">📜 ' +
        escapeHtml(titleByBase[base] || base) + "</a>";
    }

    var s = "";
    if (BOOK.libraryHref) s += '<a class="sb-home" href="' + BOOK.libraryHref + '">← Бібліотека (усі книги)</a>';
    s += '<a class="sb-logo" href="#"><span class="sb-logo-kicker">Зміст книги</span>' +
      '<span class="sb-logo-title">' + escapeHtml(BOOK.shortTitle) + "</span></a>";
    s += sbCrumbs([{ label: (chap.module && chap.module.title) || ("Модуль " + chap.module.n), href: "#" }, { label: chap.title }]);
    var vs = verSuffix(currentVer);   // § поточної статті — у тій самій версії
    s += '<a class="sb-link" data-target="top" href="#ch=' + slug + '&at=top' + vs + '">Вступ</a>';
    (attachedAfter[-1] || []).forEach(function (b) { s += subLink(b); });
    s += '<hr class="sb-divider">';

    sections.forEach(function (sec, idx) {
      s += '<a class="sb-link" data-target="' + sec.id + '" href="#ch=' + slug + "&at=" + sec.id + vs + '">§ ' +
        sec.num + " — " + escapeHtml(sec.title) + "</a>";
      (attachedAfter[idx] || []).forEach(function (b) { s += subLink(b); });
    });

    var leftovers = (chap.histories || []).map(baseOf).filter(function (b) { return !attachedSet[b]; });
    if (leftovers.length) {
      s += '<hr class="sb-divider"><div class="sb-group-label">Історія</div>';
      leftovers.forEach(function (b) { s += subLink(b); });
    }

    // інші спец-вставки (математика / компоненти / практика) — згруповано за типом, клікабельні
    var extraTypes = ["math", "comp", "proj", "api"];
    if (arts.some(function (a) { return extraTypes.indexOf(a.type) >= 0; })) {
      s += '<hr class="sb-divider"><div class="sb-group-label">Вставки до тем</div>';
      extraTypes.forEach(function (type) {
        var items = arts.filter(function (a) { return a.type === type; });
        if (!items.length) return;
        s += '<div class="sb-spec-type">' + SPEC_META[type].emoji + " " + SPEC_META[type].label + " · " + items.length + "</div>";
        items.forEach(function (a) { s += '<a class="sb-sub" data-hist="' + a.base + '" href="#">' + escapeHtml(a.title) + "</a>"; });
      });
    }

    s += chapterPager(chap);
    setSidebar(s);
  }

  function chapterPager(chap) {
    var i = FLAT.indexOf(chap), prev = FLAT[i - 1], next = FLAT[i + 1];
    function cell(c, dir) {
      var label = isBookLike()
        ? (dir === "prev" ? "← Попередня тема" : "Наступна тема →")
        : (dir === "prev" ? "← Попередній розділ" : "Наступний розділ →");
      if (!c) {
        if (dir === "prev") return '<a href="#"><span class="pg-dir">↑ Назад</span><span class="pg-ttl">Зміст книги</span></a>';
        return "";
      }
      var ttl = isBookLike() ? escapeHtml(c.title) : (c.module.n + "." + c.n + " — " + escapeHtml(c.title));
      if (c.slug) {   // є що читати → пейджер зберігає поточну версію (потік читання)
        return '<a href="' + chHref(c.slug, null, currentVer) + '"><span class="pg-dir">' + label + '</span><span class="pg-ttl">' + ttl + "</span></a>";
      }
      return '<div class="pg-soon">' +
        '<span class="pg-dir">' + label + '</span><span class="pg-ttl">' + ttl + " · незабаром</span></div>";
    }
    return '<div class="sb-pager">' + cell(prev, "prev") + cell(next, "next") + "</div>";
  }

  // Сайдбар відкритої статті книги: галузі → теми (без номерів), поточна підсвічена, + пейджер.
  function buildBookChapterSidebar(chap, sections) {
    var s = (BOOK.libraryHref ? '<a class="sb-home" href="' + BOOK.libraryHref + '">← Бібліотека (усі книги)</a>' : "") +
      '<a class="sb-logo" href="#"><span class="sb-logo-kicker">Книга</span>' +
      '<span class="sb-logo-title">' + escapeHtml(BOOK.shortTitle) + "</span></a>" +
      sbCrumbs([{ label: (chap.module && chap.module.title) || "Галузь", href: "#" }, { label: chap.title }]);
    BOOK.modules.forEach(function (m) {
      if (!m.chapters.length) return;
      var real = m.chapters.filter(function (c) { return c.slug && c.status !== "empty"; });
      var readN = real.filter(function (c) { return isRead(c.slug); }).length;
      s += sbGroupOpen(m.title, escapeHtml(m.title), grpCount(readN, real.length));
      m.chapters.forEach(function (c) {
        if (!chVisible(c)) return;
        if (c.slug) {
          var active = c.slug === chap.slug;
          s += '<a class="sb-link' + (active ? " active" : "") + readClass(c.slug) + '" href="' + chHref(c.slug, null, active ? currentVer : menuVer(c)) + '">' + escapeHtml(c.title) + betaTag(c) + "</a>";
          if (active) s += sbSections(chap, sections);   // § поточної статті під активним рядком
        } else {
          s += '<span class="sb-link soon">' + escapeHtml(c.title) + "</span>";
        }
      });
      s += sbGroupClose();
    });
    s += chapterPager(chap);
    setSidebar(s);
  }

  /* ── Курс-режим: тема книги читається В КОНТЕКСТІ курсу (BOOK.course) ────
     Сайдбар, пейджер і нижня кнопка беруться зі структури курсу, а не книги —
     тема формально лежить у book/, але «виглядає» частиною курсу. ──────── */
  function courseSteps() {
    var out = [];
    (BOOK.course.modules || []).forEach(function (m, mi) {
      var mn = m.n || (mi + 1);
      (m.chapters || []).forEach(function (c, ci) {
        var cn = mn + "." + (ci + 1);
        (c.topics || c.steps || []).forEach(function (st, si) {
          var base = { kn: cn + "." + (si + 1), title: st.title, mTitle: m.title, cTitle: c.title };
          if (st.ref) {
            var pr = String(st.ref).split("/");
            base.subject = pr[0]; base.top = pr[pr.length - 1];
          } else if (st.slug) {   // власна стаття курсу — теж повноцінний крок навігації
            base.own = true; base.subject = BOOK.course.slug; base.top = st.slug; base.mSlug = m.slug;
          } else { base.bridge = true; }
          out.push(base);
        });
      });
    });
    return out;
  }
  function courseNavList() { return courseSteps().filter(function (s) { return !s.bridge; }); }
  function courseCurrentIndex(chap) {
    var list = courseNavList();
    for (var i = 0; i < list.length; i++) if (list[i].subject === BOOK.bookSlug && list[i].top === chap.slug) return i;
    return -1;
  }
  function courseStepHref(s) {
    if (s.own) return "read.html?book=" + encodeURIComponent(BOOK.course.slug) + "#ch=" + encodeURIComponent(s.top);
    return "read.html?course=" + encodeURIComponent(BOOK.course.slug) + "&book=" + encodeURIComponent(s.subject) + "#ch=" + encodeURIComponent(s.top);
  }
  function courseHome() { return "read.html?book=" + encodeURIComponent(BOOK.course.slug); }

  function buildCourseChapterSidebar(chap, sections) {
    var cur = courseSteps().filter(function (st) { return !st.bridge && st.subject === BOOK.bookSlug && st.top === chap.slug; })[0];
    var crumbs = [{ label: "Курс", href: courseHome() }];
    if (cur) { crumbs.push({ label: cur.mTitle }); if (cur.cTitle) crumbs.push({ label: cur.cTitle }); crumbs.push({ label: cur.title || chap.title }); }
    else crumbs.push({ label: chap.title });
    var s = '<a class="sb-home" href="' + (BOOK.libraryHref || "index.html") + '">← Бібліотека</a>' +
      '<a class="sb-logo" href="' + courseHome() + '"><span class="sb-logo-kicker">Курс</span>' +
      '<span class="sb-logo-title">' + escapeHtml(BOOK.course.title) + "</span></a>" +
      sbCrumbs(crumbs);
    (BOOK.course.modules || []).forEach(function (m, mi) {
      var mn = m.n || (mi + 1);
      var mSteps = 0, mRead = 0;
      (m.chapters || []).forEach(function (c) { (c.topics || c.steps || []).forEach(function (st) {
        if (st.bridge || (!st.ref && !st.slug)) return;
        mSteps++;
        var sj, tp;
        if (st.ref) { var pr = String(st.ref).split("/"); sj = pr[0]; tp = pr[pr.length - 1]; } else { sj = BOOK.course.slug; tp = st.slug; }
        if (READ.has(sj + "/" + tp)) mRead++;
      }); });
      s += sbAccGroupOpen(m.title, "Модуль " + mn + " · " + escapeHtml(m.title), grpCount(mRead, mSteps), cur && cur.mTitle);   // акордеон: відкрито лише активний модуль + лічильник прочитаних
      (m.chapters || []).forEach(function (c, ci) {
        var cn = mn + "." + (ci + 1);
        if (c.title) s += '<div class="sb-chap">' + cn + " · " + escapeHtml(c.title) + "</div>";
        (c.topics || c.steps || []).forEach(function (st, si) {
          var kn = cn + "." + (si + 1), subj, top, href;
          if (st.ref) {
            var pr = String(st.ref).split("/"); subj = pr[0]; top = pr[pr.length - 1];
            href = "read.html?course=" + encodeURIComponent(BOOK.course.slug) + "&book=" + encodeURIComponent(subj) + "#ch=" + encodeURIComponent(top);
          } else if (st.slug) {   // власна стаття курсу
            subj = BOOK.course.slug; top = st.slug;
            href = "read.html?book=" + encodeURIComponent(BOOK.course.slug) + "#ch=" + encodeURIComponent(st.slug);
          } else {
            s += '<span class="sb-link sb-bridge"><span class="sb-kn">' + kn + "</span>🔗 " + escapeHtml(st.title || "місток") + "</span>"; return;
          }
          var cur = (subj === BOOK.bookSlug && top === chap.slug) ? " active" : "";
          var rd = READ.has(subj + "/" + top) ? " read" : "";   // прочитано (ключ = книга-джерело/тема або курс/slug)
          s += '<a class="sb-link' + cur + rd + '" href="' + href + '"><span class="sb-kn">' + kn + "</span>" + escapeHtml(st.title || top) + "</a>";
          if (cur) s += sbSections(chap, sections);   // § поточного кроку під активним рядком
        });
      });
      s += sbGroupClose();
    });
    s += coursePager(chap);
    setSidebar(s);
  }
  function coursePager(chap) {
    var list = courseNavList(), i = courseCurrentIndex(chap);
    var prev = i > 0 ? list[i - 1] : null, next = (i >= 0 && i < list.length - 1) ? list[i + 1] : null;
    function cell(st, dir) {
      if (!st) {
        if (dir === "prev") return '<a href="' + courseHome() + '"><span class="pg-dir">↑ Курс</span><span class="pg-ttl">Огляд курсу</span></a>';
        return "";
      }
      var label = dir === "prev" ? "← Попередній крок" : "Наступний крок →";
      return '<a href="' + courseStepHref(st) + '"><span class="pg-dir">' + label + '</span><span class="pg-ttl">' +
        st.kn + " · " + escapeHtml(st.title || st.top) + "</span></a>";
    }
    return '<div class="sb-pager">' + cell(prev, "prev") + cell(next, "next") + "</div>";
  }
  // Угорі статті (курс-режим): невеличке посилання на ПОПЕРЕДНІЙ крок.
  function courseTopNav(chap) {
    if (!BOOK.course) return "";
    var list = courseNavList(), i = courseCurrentIndex(chap);
    var prev = i > 0 ? list[i - 1] : null;
    if (prev) return '<a class="course-top" href="' + courseStepHref(prev) + '"><span class="ct-dir">← Попередній крок</span><span class="ct-ttl">' + escapeHtml(prev.title || prev.top) + "</span></a>";
    return '<a class="course-top" href="' + courseHome() + '"><span class="ct-dir">↑ Курс</span><span class="ct-ttl">' + escapeHtml(BOOK.course.title) + "</span></a>";
  }
  // Унизу статті (курс-режим): кнопка до НАСТУПНОГО кроку.
  function courseBottomNav(chap) {
    if (!BOOK.course) return "";
    var list = courseNavList(), i = courseCurrentIndex(chap);
    var next = (i >= 0 && i < list.length - 1) ? list[i + 1] : null;
    if (next) return '<nav class="course-bottom"><a class="cb-btn cb-next" href="' + courseStepHref(next) + '"><span class="cb-dir">Наступний крок →</span><span class="cb-ttl">' + escapeHtml(next.title || next.top) + "</span></a></nav>";
    return '<nav class="course-bottom"><a class="cb-btn cb-next cb-done" href="' + courseHome() + '"><span class="cb-dir">Курс пройдено ✓</span><span class="cb-ttl">До огляду курсу</span></a></nav>';
  }
  // Сегментований перемикач між короткою (<slug>.md) і повною (<slug>-d.md) версіями —
  // у верхній панелі праворуч, миттєвий (обидві версії в кеші, як stack). Лише коли Є ОБИДВІ версії.
  function versionSwitch(chap, ver) {
    if (!(chap.hasBasic && chap.hasDetailed)) return "";   // перемикач лише коли Є ОБИДВІ версії
    var isD = ver === "d";
    function seg(active, href, ico, label) {
      return '<a class="vs-btn' + (active ? " on" : "") + '" href="' + href + '"' + (active ? ' aria-current="true"' : "") +
        ' title="' + escapeAttr(label + " версія") + '"><span class="vs-ico" aria-hidden="true">' + ico +
        '</span><span class="vs-lbl">' + label + "</span></a>";
    }
    return '<div class="ver-switch" role="group" aria-label="Версія статті">' +
      seg(!isD, chHref(chap.slug, null, ""), "📄", "Коротка") +
      seg(isD, chHref(chap.slug, null, "d"), "📖", "Повна") +
      "</div>";
  }

  /* ════════════════════════════════════════════════════════════════════
     7) ОБКЛАДИНКА / МАПА КУРСУ
     ════════════════════════════════════════════════════════════════════ */
  // теми/вставки розділів для змісту — з manifest (chapter.topics[]).
  // Розділ книги-довідника без topics[] лишається без під-тем у списку.
  function coverMapFromManifest() {
    var map = {};
    BOOK.modules.forEach(function (m) {
      m.chapters.forEach(function (c) {
        var mr = m.n + "." + c.n, tps = [], sps = [];
        (c.topics || []).forEach(function (t) {
          if (!t.kind) tps.push({ num: t.mrt || mr, title: (t.title || "").replace(/\s*<!--.*$/, "").trim(), done: t.status === "done" });
          else sps.push({ type: (t.kind === "proj" ? "proj" : t.kind), title: (t.title || "").trim(),
            base: baseOf(String(t.file || "").split("/").pop()), attach: (t.at && t.at !== "chapter") ? t.at : "", done: t.status === "done" });
        });
        map[mr] = { topics: tps, specs: sps };
      });
    });
    return map;
  }
  function plTopics(n) {
    var a = n % 10, b = n % 100;
    if (a === 1 && b !== 11) return n + " тема";
    if (a >= 2 && a <= 4 && (b < 10 || b >= 20)) return n + " теми";
    return n + " тем";
  }

  function renderCover() {
    document.body.classList.remove("reading");
    if (isBookLike()) { setContent(bookCoverHtml()); buildBookSidebar(); return; }
    setContent(coverHtml(coverMapFromManifest()));
    buildCoverSidebar();
  }

  // Обкладинка предметної книги: галузі (БЕЗ номерів) → теми-статті. Книга = набір статей без порядку.
  function bookCoverHtml() {
    var readable = FLAT.filter(function (c) { return c.slug; }).length;
    var fullCount = FLAT.filter(function (c) { return c.full; }).length;
    var live = BOOK.modules.filter(function (m) { return m.chapters.length; });
    var h = '<header class="ch-header ch-header-guide"><div class="ch-label">' +
      (BOOK.type === "reference" ? "Довідник · технологія за розділами" : "Книга · теорія за галузями") + '</div><h1>' + escapeHtml(BOOK.title) + '</h1></header>' +
      '<header class="cover-hero cover-hero-guide" style="--accent:' + (BOOK.accent || "#1d6fa4") + '">' + (BOOK.subtitle ? "<p>" + escapeHtml(BOOK.subtitle) + "</p>" : "") +
      '<div class="cover-stats">' + stat(live.length, "галузей") + stat(readable, "статей") + (fullCount ? stat(fullCount, "повних") : "") +
      "</div></header>" + mapToolbar(true) + '<div class="toc' + (NAV.view === "grid" ? " map-grid" : "") + '">';
    live.forEach(function (m) {
      var d = m.chapters.filter(function (c) { return c.slug; }).length;
      var total = m.chapters.filter(chVisible).length;   // видимі (читабельні + «незабаром») — щоб d ≤ total
      h += '<div class="module-block' + (isCollapsed(m.title) ? " collapsed" : "") + '"><div class="module-head" data-collapse-group="' + escapeAttr(m.title) + '">' +
        '<span class="m-caret" aria-hidden="true">▾</span><span class="m-ttl">' + escapeHtml(m.title) + "</span>" +
        '<span class="m-prog">' + d + " / " + total + "</span></div><div class=\"ch-list\">";
      /* A★: теми стоять ГНІЗДАМИ підрозділів. Підрозділ не окремий рівень моделі,
         але кожна тема несе його назву в c.chap (кладе bookbuild), тож гніздо
         збирається тут. У списковому вигляді гнізд немає — там рядок на тему. */
      var nest = null;
      m.chapters.forEach(function (c) {
        if (!chVisible(c)) return;   // ні тексту, ні «в планах» → не показуємо
        /* Гніздо відкриваємо ПІСЛЯ перевірки видимости: інакше підрозділ, у якому всі
           теми приховані, лишив би заголовок без жодного рядка під ним. */
        if (NAV.view === "grid" && c.chap && c.chap !== nest) {
          if (nest !== null) h += "</div></div>";
          nest = c.chap;
          h += '<div class="ch-nest"><h5 class="nest-ttl">' + escapeHtml(c.chap) + '</h5><div class="nest-body">';
        }
        if (c.slug) {   // є текст → читабельне (зі списку книги відкриваємо повну, якщо є)
          h += '<div class="ch-item done' + readClass(c.slug) + verClass(c) + '"><div class="ch-row"><a class="ch-open"' + verHint(c) + ' href="' + chHref(c.slug, null, menuVer(c)) + '">' +
            '<span class="c-ttl">' + escapeHtml(c.title) + betaTag(c) + "</span>" +
            '<span class="c-go">→</span></a></div></div>';
        } else {
          h += '<div class="ch-item pending"><div class="ch-row"><span class="c-ttl">' + escapeHtml(c.title) +
            '</span><span class="c-badge">незабаром</span></div></div>';
        }
      });
      if (nest !== null) h += "</div></div>";   // A★: закрити останнє гніздо
      h += "</div></div>";
    });
    return h + "</div>";
  }
  function buildBookSidebar() {
    var s = (BOOK.libraryHref ? '<a class="sb-home" href="' + BOOK.libraryHref + '">← Бібліотека (усі книги)</a>' : "") +
      '<a class="sb-logo" href="#"><span class="sb-logo-kicker">' + (BOOK.type === "reference" ? "Довідник" : "Книга") + '</span>' +
      '<span class="sb-logo-title">' + escapeHtml(BOOK.shortTitle) + "</span></a>";
    BOOK.modules.forEach(function (m) {
      if (!m.chapters.length) return;
      s += sbGroupOpen(m.title, escapeHtml(m.title));
      m.chapters.forEach(function (c) {
        if (!chVisible(c)) return;
        if (c.slug) s += '<a class="sb-link' + readClass(c.slug) + '" href="' + chHref(c.slug, null, menuVer(c)) + '">' + escapeHtml(c.title) + betaTag(c) + "</a>";
        else s += '<span class="sb-link soon">' + escapeHtml(c.title) + "</span>";
      });
      s += sbGroupClose();
    });
    setSidebar(s);
  }

  function coverHtml(topics) {
    var doneCount = FLAT.filter(chReadable).length;
    var h = '<header class="ch-header ch-header-guide"><div class="ch-label">' + (BOOK.type === "catalog" ? "Каталог · довідник заліза" : "Курс · " + BOOK.modules.length + " модулів") + '</div><h1>' + escapeHtml(BOOK.title) + '</h1></header>' +
      '<header class="cover-hero cover-hero-guide" style="--accent:' + (BOOK.accent || "#1d6fa4") + '"><p>' + escapeHtml(BOOK.subtitle) + "</p>" +
      '<div class="cover-stats">' +
      stat(BOOK.modules.length, "модулів") + stat(FLAT.length, "розділів") + stat(doneCount, "готових зараз") +
      "</div></header>";

    h += mapToolbar(false) + '<div class="toc">';
    BOOK.modules.forEach(function (m) {
      var done = m.chapters.filter(chReadable).length;
      h += '<div class="module-block' + (isCollapsed(m.title) ? " collapsed" : "") + '"><div class="module-head" data-collapse-group="' + escapeAttr(m.title) + '">' +
        '<span class="m-caret" aria-hidden="true">▾</span><span class="m-num">Модуль ' + m.n + "</span>" +
        '<span class="m-ttl">' + escapeHtml(m.title) + "</span>" +
        '<span class="m-prog">' + done + " / " + m.chapters.length + ' готово</span></div><div class="ch-list">';
      /* A★: у плитці теми стоять ГНІЗДАМИ підрозділів. Підрозділ у моделі рушія не
         окремий рівень, але кожна тема несе його назву в c.chap (кладе bookbuild),
         тож гніздо збирається тут, без правки адаптера. У списку гнізд немає —
         там один рядок на тему, і заголовок лише додав би шуму. */
      var nest = null;
      m.chapters.forEach(function (c) {
        var mr = m.n + "." + c.n;
        if (NAV.view === "grid" && c.chap && c.chap !== nest) {
          if (nest !== null) h += "</div></div>";
          nest = c.chap;
          h += '<div class="ch-nest"><h5 class="nest-ttl">' + escapeHtml(c.chap) + '</h5><div class="nest-body">';
        }
        if (chReadable(c)) {
          var entry = topics[mr] || { topics: [], specs: [] };
          var tops = entry.topics || [], specs = entry.specs || [];
          var tid = "tp-" + mr.replace(/\./g, "-");
          var btnLabel = plTopics(tops.length) + (specs.length ? " · " + specs.length + " вставок" : "");
          h += '<div class="ch-item done' + readClass(c.slug) + verClass(c) + '"><div class="ch-row">' +
            '<a class="ch-open"' + verHint(c) + ' href="' + chHref(c.slug, null, menuVer(c)) + '"><span class="c-num">' + mr + "</span>" +
            '<span class="c-ttl">' + escapeHtml(c.title) + betaTag(c) + "</span>" +
            '<span class="c-go">→</span></a>';
          if (tops.length || specs.length) h += '<button class="ch-exp" type="button" data-exp="' + tid + '" aria-expanded="false">' + btnLabel + "</button>";
          h += "</div>";
          if (tops.length || specs.length) {
            h += '<ul class="ch-topics" id="' + tid + '" hidden>';
            tops.forEach(function (tp) {
              h += '<li class="' + (tp.done ? "t-done" : "t-pending") + '"><a href="#ch=' + c.slug + "&at=sec-" + tp.num.split(".").join("-") + '">' +
                '<span class="t-num">' + tp.num + "</span>" + escapeHtml(tp.title) + "</a></li>";
            });
            SPEC_ORDER.forEach(function (type) {
              var items = specs.filter(function (s) { return s.type === type; });
              if (!items.length) return;
              h += '<li class="t-spec-head">' + SPEC_META[type].emoji + " " + SPEC_META[type].label + "</li>";
              items.forEach(function (s) {
                h += '<li class="t-spec ' + (s.done ? "t-done" : "t-pending") + '"><a href="#ch=' + c.slug + "&at=hist-" + s.base + '">' +
                  '<span class="t-num">' + (s.attach || "") + "</span>" + escapeHtml(s.title) + "</a></li>";
              });
            });
            h += "</ul>";
          }
          h += "</div>";
        } else {
          h += '<div class="ch-item pending"><div class="ch-row">' +
            '<span class="c-num">' + mr + '</span><span class="c-ttl">' + escapeHtml(c.title) + "</span>" +
            '<span class="c-badge">незабаром</span></div></div>';
        }
      });
      if (nest !== null) h += "</div></div>";
      h += "</div></div>";
    });
    return h + "</div>";
  }
  function stat(num, lbl) { return '<div class="stat"><div class="num">' + num + '</div><div class="lbl">' + lbl + "</div></div>"; }

  function buildCoverSidebar() {
    var s = (BOOK.libraryHref ? '<a class="sb-home" href="' + BOOK.libraryHref + '">← Бібліотека (усі книги)</a>' : "") +
      '<a class="sb-logo" href="#"><span class="sb-logo-kicker">' + (BOOK.type === "reference" ? "Довідник" : "Книга") + '</span>' +
      '<span class="sb-logo-title">' + escapeHtml(BOOK.shortTitle) + "</span></a>";
    BOOK.modules.forEach(function (m) {
      s += sbGroupOpen(m.title, "Модуль " + m.n + " · " + escapeHtml(m.title));
      m.chapters.forEach(function (c) {
        if (chReadable(c)) {
          s += '<a class="sb-link' + readClass(c.slug) + '" href="' + chHref(c.slug, null, menuVer(c)) + '">' + m.n + "." + c.n + " · " + escapeHtml(c.title) + betaTag(c) + "</a>";
        } else {
          s += '<span class="sb-link soon">' + m.n + "." + c.n + " · " + escapeHtml(c.title) + "</span>";
        }
      });
      s += sbGroupClose();
    });
    setSidebar(s);
  }

  function renderComingSoon(chap) {
    document.body.classList.remove("reading");
    setContent('<div class="state"><h2>Розділ ' + chap.module.n + "." + chap.n + " — " + escapeHtml(chap.title) + "</h2>" +
      "<p>Цей розділ ще пишеться. Заходь трохи згодом 🙂</p><p><a href=\"#\">← До змісту книги</a></p></div>");
    buildCoverSidebar();
  }

  /* ════════════════════════════════════════════════════════════════════
     8) РОУТЕР + ДОПОМІЖНЕ
     ════════════════════════════════════════════════════════════════════ */
  /* ── Хеш як стан: розділ + якір + СТЕК попапів ───────────────────────────
     pop=<токен>;<токен>…  ·  токен «h:<base>» — локальна вставка розділу,
     «b:<book>|<slug>|<file>|<frag>» — матеріал з іншої книги. */
  function parsePopParam(v) { return v ? v.split(";").filter(Boolean) : []; }
  function tokensToHashPart(tokens) { return (tokens && tokens.length) ? "&pop=" + encodeURIComponent(tokens.join(";")) : ""; }
  function buildHash(slug, at, tokens, ver) {
    var h = "ch=" + encodeURIComponent(slug);
    if (at) h += "&at=" + encodeURIComponent(at);
    if (ver === "d") h += "&v=d";   // версія «липне» до URL — модалки/шер/назад не скидають повну на коротку
    return h + tokensToHashPart(tokens);
  }
  function navUrl(slug, at, tokens, ver) { return "#" + buildHash(slug, at, tokens, ver); }

  function parseHash() {
    var hsh = location.hash.replace(/^#/, "");
    if (!hsh) return { view: "cover", tokens: [] };
    var p = {};
    hsh.split("&").forEach(function (kv) { var a = kv.split("="); p[a[0]] = decodeURIComponent(a[1] || ""); });
    if (!p.ch) return { view: "cover", tokens: [] };
    var at = p.at || null, tokens = parsePopParam(p.pop);
    if (at && at.indexOf("hist-") === 0) { tokens = tokens.concat(["h:" + at.slice(5)]); at = null; }   // легасі-якір історії → токен попапа
    return { view: "chapter", slug: p.ch, at: at, v: p.v || "", tokens: tokens };
  }

  var appliedAt = null;     // який якір уже застосовано (щоб не стрибати догори при закритті попапа)

  /* Кнопка «на рівень вище» (зліва зверху): стаття → зміст книги / лендинг курсу; зміст → бібліотека.
     Вузол ПЕРЕЇЖДЖАЄ всередину .ch-header і позиціюється відносно НЕЇ (book.css): просвіт під
     кнопку й сама кнопка читають одну змінну, тож наїхати на заголовок нічим. Єдина точка, де
     це може зламатись, — innerHTML у setContent; там кнопку виносимо перед записом і вертаємо
     одразу після, тож жодний майбутній шлях рендера про неї не забуде. */
  var upHref = "index.html";
  function ensureUpBtn() {
    var up = document.getElementById("up-btn");
    if (!up) {                                   // хтось таки зітер — відбудовуємо, а не лишаємось без кнопки
      up = document.createElement("a");
      up.id = "up-btn"; up.textContent = "←";
      up.setAttribute("aria-label", "На рівень вище"); up.setAttribute("title", "На рівень вище");
      document.body.appendChild(up);
    }
    up.setAttribute("href", upHref);
    return up;
  }
  /* Розстановку кнопок у комірки шапки веде chrome.js — ОДИН власник на всі шляхи
     рендера (стаття тут, доріжка курсу в bookbuild.js). Тут лишається тільки адреса. */
  function placeUpBtn() {
    ensureUpBtn();
    if (window.__chromeMount) window.__chromeMount();
  }
  function updateUpBtn(view) {
    upHref = (view === "chapter") ? (BOOK.course ? courseHome() : "#") : (BOOK.libraryHref || "index.html");
    placeUpBtn();
  }

  function route() {
    var r = parseHash();
    closeMobileSidebar();
    updateUpBtn(r.view);
    if (r.view === "cover") { syncModals([]); currentSlug = null; appliedAt = null; renderCover(); window.scrollTo(0, 0); return; }
    var chap = CH_BY_SLUG[r.slug];
    if (!chap) {
      syncModals([]);
      var any = null;
      BOOK.modules.forEach(function (m) { m.chapters.forEach(function (c) { if (!c.slug && c.dir && c.dir.split("/").pop() === r.slug) any = c; }); });
      currentSlug = null; appliedAt = null;
      if (any) renderComingSoon(any); else renderCover();
      return;
    }
    if (r.slug === currentSlug && (r.v || "") === (currentVer || "")) {
      if (r.at && r.at !== appliedAt) { scrollToAnchor(r.at); markActive(r.at); appliedAt = r.at; }
      syncModals(r.tokens);
      return;
    }
    currentSlug = r.slug; currentVer = r.v || ""; pendingTarget = r.at || null; pendingTokens = r.tokens || []; renderChapter(chap, r.v || "");
  }

  function scrollToAnchor(at) {
    if (!at) { window.scrollTo(0, 0); return; }
    var el = document.getElementById(at);
    if (el) el.scrollIntoView({ behavior: "auto", block: "start" });
    else window.scrollTo(0, 0);
    markActive(at);
  }
  function markActive(at) {
    var links = $sidebar.querySelectorAll("[data-target]");
    for (var i = 0; i < links.length; i++) links[i].classList.toggle("active", links[i].getAttribute("data-target") === at);
  }

  /* ── Стек попапів: кожен шар — окремий .hist-modal поверх попереднього ──── */
  var modalStack = [];                       // [{ token, kind, el }]
  function modalContainer() {
    var c = document.getElementById("modal-stack");
    if (!c) { c = document.createElement("div"); c.id = "modal-stack"; document.body.appendChild(c); }
    return c;
  }
  function blankLayer() {
    var el = document.createElement("div");
    el.className = "hist-modal modal-layer spec-comp";
    el.setAttribute("role", "dialog"); el.setAttribute("aria-modal", "true");
    el.innerHTML = '<div class="hist-modal-backdrop" data-close></div>' +
      '<div class="hist-modal-dialog"><div class="hist-modal-scroll"><div class="state"><div class="spinner"></div>Завантаження…</div></div></div>';
    return el;
  }
  function histClone(base) {                  // клон прихованої вставки розділу як новий шар
    var src = document.getElementById("histmodal-" + base);
    if (!src) {
      var miss = blankLayer();
      miss.querySelector(".hist-modal-scroll").innerHTML = '<div class="state error">Вставку не знайдено.</div>';
      return miss;
    }
    var el = src.cloneNode(true);
    el.removeAttribute("hidden"); el.removeAttribute("id");
    el.classList.add("modal-layer");
    return el;
  }
  function openModalToken(token) {
    var ci = token.indexOf(":"), kind = token.slice(0, ci), data = token.slice(ci + 1);
    var el = (kind === "h") ? histClone(data) : blankLayer();
    modalContainer().appendChild(el);
    modalStack.push({ token: token, kind: kind, el: el });
    if (kind === "b") fillXbook(el, data);
    refreshModalChrome();
    var sc = el.querySelector(".hist-modal-scroll"); if (sc) sc.scrollTop = 0;
    var cl = el.querySelector(".hist-modal-close"); if (cl) cl.focus();
  }
  function closeTopLayer() {
    var rec = modalStack.pop();
    if (rec && rec.el && rec.el.parentNode) rec.el.parentNode.removeChild(rec.el);
    refreshModalChrome();
  }
  function closeAllModals() { while (modalStack.length) modalStack.pop().el.remove(); refreshModalChrome(); }
  function refreshModalChrome() {
    var n = modalStack.length;
    document.body.classList.toggle("modal-open", n > 0);
    for (var i = 0; i < n; i++) {
      var m = modalStack[i], top = (i === n - 1);
      m.el.style.zIndex = String(1000 + i * 10);
      m.el.classList.toggle("modal-covered", !top);
      var cl = m.el.querySelector(".hist-modal-close");
      if (cl) {
        var back = top && n > 1;
        cl.textContent = back ? "←" : "✕";
        cl.setAttribute("aria-label", back ? "Назад" : "Закрити");
        cl.setAttribute("title", back ? "Назад до попередньої вставки" : "Закрити");
      }
    }
  }
  // звести DOM-стек до списку токенів із хеша: відкрити нові поверх, закрити зайві згори
  function syncModals(tokens) {
    tokens = tokens || [];
    var i = 0;
    while (i < tokens.length && i < modalStack.length && modalStack[i].token === tokens[i]) i++;
    while (modalStack.length > i) closeTopLayer();
    for (var d = i; d < tokens.length; d++) openModalToken(tokens[d]);
  }
  // дії користувача: відкрити попап = новий запис історії; закрити = крок «назад»
  function pushModal(token) {
    var r = parseHash();
    if (r.view !== "chapter") return;
    var tokens = (r.tokens || []).concat([token]);
    history.pushState(null, "", navUrl(r.slug, r.at, tokens, r.v));
    syncModals(tokens);
  }
  function closeViaHistory() { if (modalStack.length) history.back(); }
  // абсолютне посилання, що відкриває конкретний попап над поточним розділом
  function popupShareUrl(token) {
    var slug = currentSlug || parseHash().slug || "";
    return location.origin + location.pathname + location.search + navUrl(slug, null, [token], currentVer);
  }

  /* ── Копіювання посилань + тост «скопійовано» ───────────────────────────── */
  function showToast(msg) {
    var t = document.getElementById("copy-toast");
    if (!t) { t = document.createElement("div"); t.id = "copy-toast"; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add("show");
    clearTimeout(showToast._t); showToast._t = setTimeout(function () { t.classList.remove("show"); }, 1700);
  }
  function fallbackCopy(text) {
    try {
      var ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.focus(); ta.select();
      document.execCommand("copy"); document.body.removeChild(ta);
    } catch (e) { /* ignore */ }
  }
  function copyText(text) {
    var ok = function () { showToast("Посилання скопійовано ✓"); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(ok, function () { fallbackCopy(text); ok(); });
    } else { fallbackCopy(text); ok(); }
  }

  /* ── Крос-попап (v7): root:<книга>/<тема>[/<file>] ─────────────────────────────── */
  // токен шару: «<id|guide/course>|<slug>|<file>|<frag>»
  function fillXbook(el, data) {
    var pp = data.split("|");
    openCrossBook(el, pp[0] || "", pp[1] || "", pp[2] || "", pp[3] || "");
  }
  function setLayerHtml(el, inner) {
    el.innerHTML = inner;
    syncCodeTabs();                                // вкладки коду в попапі — на збережену мову
    var sc = el.querySelector(".hist-modal-scroll"); if (sc) sc.scrollTop = 0;
    refreshModalChrome();                          // оновити кнопку «✕/←» уже після підвантаження
  }
  // ВМІСТ діалогу шару (без зовнішньої .hist-modal — її дає сам шар)
  function xbookShell(reg, slug, frag, headHtml, innerHtml) {
    var openHref = reg ? reg.entry + "#ch=" + encodeURIComponent(slug) + (frag ? "&at=" + encodeURIComponent(frag) : "") : "#";
    var lbl = reg ? reg.icon + " " + escapeHtml(reg.label) : "Інша книга";
    var btn = '<a href="' + escapeAttr(openHref) + '" style="display:inline-block;margin-top:1.1rem;padding:.5rem .9rem;background:#1d6fa4;color:#fff;border-radius:7px;text-decoration:none">' +
      (reg ? "Відкрити «" + escapeHtml(reg.label) + "» →" : "Відкрити →") + "</a>";
    return '<div class="hist-modal-backdrop" data-close></div>' +
      '<div class="hist-modal-dialog">' +
      '<button class="hist-modal-share" type="button" data-share aria-label="Копіювати посилання" title="Копіювати посилання на цю вставку">🔗</button>' +
      '<button class="hist-modal-close" type="button" data-close aria-label="Закрити">✕</button>' +
      '<div class="hist-modal-scroll"><div class="hist-modal-head"><div class="hist-art-label">' + lbl + "</div>" + headHtml + "</div>" +
      '<div class="content-body">' + innerHtml + btn + "</div></div></div>";
  }
  // знайти тему за slug у книзі/курсі (будь-який статус, аби був текст)
  function chapInBookAny(book, slug) {
    var found = null;
    ((book && book.modules) || []).forEach(function (m) {
      (m.chapters || []).forEach(function (c) {
        if (c.dir && c.dir.split("/").pop() === slug) { c.module = c.module || m; found = c; }
      });
    });
    return found;
  }
  var _guideCache = {};
  function loadGuideAsBook(course) {
    if (_guideCache[course]) return Promise.resolve(_guideCache[course]);
    return window.loadGuide(course).then(function (g) {
      var b = (g && window.adaptSubjectBook) ? window.adaptSubjectBook(g, "guide/") : null; _guideCache[course] = b; return b;
    });
  }
  /* Єдиний відкривач крос-попапу. kind: "book" (book/<id>) | "guide" (guide/<course>).
     file: порожнє → головна стаття; "<slug>-d.md" → детальна; "<type>-<name>.md" → вставка (📜/🔌/🧮/⚙️). */
  function openRef(el, kind, id, slug, file, frag) {
    var reg, loader;
    if (kind === "guide") {
      reg = { entry: "read.html?book=" + encodeURIComponent(id), icon: "📘", label: "Курс" };
      loader = loadGuideAsBook(id);
    } else {
      var meta = SUBJECT_META[id] || { icon: "📘", label: id };
      reg = { entry: "read.html?book=" + encodeURIComponent(id), icon: meta.icon, label: meta.label };
      loader = (BOOK && id === BOOK.bookSlug) ? Promise.resolve(BOOK)
        : (_subjCache[id] ? Promise.resolve(_subjCache[id])
          : window.loadBook(id).then(function (b) { _subjCache[id] = b; return b; }));
    }
    function show(head, inner) { setLayerHtml(el, xbookShell(reg, slug, frag, head, inner)); }
    loader.then(function (bk) {
      var chap = bk && chapInBookAny(bk, slug);
      var base = bk ? (bk.basePath || "") : "";   // v7: basePath дає адаптер (root/<dir>/<book>/)
      var dir = chap && chap.dir;

      // ── ВСТАВКА — самостійний файл: відкриваємо НЕЗАЛЕЖНО від статусу/готовності статті ──
      if (file && /^(hist|comp|math|proj|api)-/.test(file)) {
        if (!dir) { show("<h1>" + escapeHtml(slug.replace(/-/g, " ")) + "</h1>", "<p>📝 Вставку не знайдено.</p>"); return; }
        fetchText(base + dir + "/" + file).then(function (text) {
          var ctx = { currentSlug: slug, dir: dir, base: base, histBases: new Set(), attach: [] };
          var a = parseHistory(text, file, ctx);
          show("<h1>" + escapeHtml(a.title) + "</h1>", (a.introHtml ? '<div class="hist-intro">' + a.introHtml + "</div>" : "") + a.bodyHtml);
        }).catch(function (e) {
          show("<h1>" + escapeHtml(slug.replace(/-/g, " ")) + "</h1>", "<p>Не вдалося завантажити вставку (<code>" + escapeHtml(e.message) + "</code>).</p>");
        });
        return;
      }

      // ── СТАТТЯ (головна / детальна) — версійно-свідомо + fallback (single-link §6) ──
      var _hasB = chap && _fileExists(chap.status), _hasD = chap && _fileExists(chap.dstatus);
      if (!dir || (!_hasB && !_hasD)) {
        show("<h1>" + escapeHtml((chap && chap.title) || slug.replace(/-/g, " ")) + "</h1>",
          '<p>📝 ' + (kind === "guide" ? "Крок курсу" : "Ця тема") + ' ще <strong>в розробці</strong>.</p>');
        return;
      }
      // явна детальна: 3-й сегмент «detail» або «<slug>-d.md»; інакше базова. Fallback до наявної версії.
      var _wantD = (file === "detail" || /-d\.md$/.test(file));
      var fname = _wantD ? (_hasD ? chap.main.replace(/\.md$/, "-d.md") : chap.main)
                         : (_hasB ? chap.main : chap.main.replace(/\.md$/, "-d.md"));
      fetchText(base + dir + "/" + fname).then(function (text) {
        var ctx = { currentSlug: slug, dir: dir, base: base, histBases: new Set(), attach: [] };
        var pm = parseMain(text, ctx);
        var body = pm.bodyHtml.replace(/src="(img\/[^"]+)"/g, 'src="' + base + dir + '/$1"');
        show("<h1>" + escapeHtml(chap.title) + "</h1>", body);
      }).catch(function (e) {
        show("<h1>" + escapeHtml(chap.title || slug) + "</h1>", "<p>Не вдалося завантажити (<code>" + escapeHtml(e.message) + "</code>).</p>");
      });
    });
  }
  function openCrossBook(el, book, slug, file, frag) {
    if (window.loadBook) { openRef(el, "book", book, slug, file, frag); return; }
    setLayerHtml(el, xbookShell(null, slug, frag, "<h1>" + escapeHtml(slug || "Розділ") + "</h1>", "<p>Невідома книга <code>" + escapeHtml(book) + "</code>.</p>"));
  }

  var spy = null;
  function setupScrollSpy() {
    if (spy) spy.disconnect();
    var links = [].slice.call($sidebar.querySelectorAll("[data-target]"));
    if (!links.length) return;
    var map = {};
    var anchors = [];
    links.forEach(function (l) {
      var id = l.getAttribute("data-target"); map[id] = l;
      var a = document.getElementById(id); if (a) anchors.push(a);
    });
    spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          links.forEach(function (l) { l.classList.remove("active"); });
          if (map[e.target.id]) map[e.target.id].classList.add("active");
        }
      });
    }, { rootMargin: "-88px 0px -72% 0px", threshold: 0 });
    anchors.forEach(function (a) { spy.observe(a); });
  }

  function setContent(html) {
    var up = document.getElementById("up-btn");                        // innerHTML зітер би вузол разом зі старою шапкою
    if (up && up.parentNode !== document.body) document.body.appendChild(up);
    var rc = document.getElementById("reader-controls");               // те саме й для панелі кнопок: без цього
    if (rc && rc.parentNode !== document.body) document.body.appendChild(rc);   // шестерня зникала на кожному рендері
    $content.innerHTML = html; syncCodeTabs();
    placeUpBtn();                                                      // …і одразу назад у свіжу шапку — без блимання
  }
  function setSidebar(html) {
    $sidebar.innerHTML = html;
    var a = $sidebar.querySelector(".sb-link.active");   // автоскрол до активного рядка (курс на 600+ рядків)
    if (a) { var top = a.getBoundingClientRect().top - $sidebar.getBoundingClientRect().top + $sidebar.scrollTop; $sidebar.scrollTop = top - $sidebar.clientHeight / 2 + a.offsetHeight / 2; }
  }
  function closeMobileSidebar() { $sidebar.classList.remove("open"); }

  /* ── Глобальні елементи UI ──────────────────────────────────────────── */
  function initChrome() {
    if (isBookLike()) document.body.classList.add("book-mode");   // CSS-гачок: лагідні вставки без фону
    if (BOOK.course) document.body.classList.add("course-mode");
    var menu = document.getElementById("menu-btn");
    var scrim = document.getElementById("scrim");
    var top = document.getElementById("back-top");
    // ☰ і затемнення веде chrome.js: одна кнопка на всі ширини, один обробник.
    if (top) {
      top.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
      window.addEventListener("scroll", function () { top.classList.toggle("vis", window.scrollY > 600); });
    }
    // делеговані кліки: відкрити/закрити/поділитися попапом
    document.addEventListener("click", function (e) {
      var ct = e.target.closest && e.target.closest(".codetabs__tab");       // вкладка мови в код-блоці
      if (ct) { e.preventDefault(); pickCodeLang(ct.getAttribute("data-lang")); return; }
      var mv = e.target.closest && e.target.closest("[data-map-view]");      // список ⇄ плитка (мапа книги)
      if (mv) { e.preventDefault(); NAV.view = mv.getAttribute("data-map-view"); saveNav(); applyMapView(); return; }
      var ca = e.target.closest && e.target.closest("[data-collapse-all]");  // згорнути/розгорнути всі галузі
      if (ca) { e.preventDefault(); toggleAllGroups(); return; }
      var acc = e.target.closest && e.target.closest("[data-sb-acc]");        // акордеон сайдбару курсу (сесійний, не персист)
      if (acc) {
        e.preventDefault();
        var willCol = !acc.classList.contains("collapsed");
        acc.classList.toggle("collapsed", willCol);
        var ak = acc.getAttribute("data-sb-acc");
        if (willCol) SB_OPEN.delete(ak); else SB_OPEN.add(ak);
        return;
      }
      var cg = e.target.closest && e.target.closest("[data-collapse-group]"); // згорнути одну галузь (мапа або сайдбар)
      if (cg) { e.preventDefault(); toggleGroup(cg.getAttribute("data-collapse-group")); return; }
      var sh = e.target.closest && e.target.closest("[data-share-token]");   // значок 🔗 на картці-вставці
      if (sh) { e.preventDefault(); e.stopPropagation(); copyText(popupShareUrl(sh.getAttribute("data-share-token"))); return; }
      var dsh = e.target.closest && e.target.closest("[data-share]");        // кнопка 🔗 у самому попапі
      if (dsh) { e.preventDefault(); copyText(location.href); return; }
      var op = e.target.closest && e.target.closest("[data-hist]");
      if (op) { e.preventDefault(); pushModal("h:" + op.getAttribute("data-hist")); return; }
      var xb = e.target.closest && e.target.closest("[data-xbook]");
      if (xb) { e.preventDefault(); pushModal("b:" + (xb.getAttribute("data-xbook") || "")); return; }
      var cl = e.target.closest && e.target.closest("[data-close]");
      if (cl) { e.preventDefault(); closeViaHistory(); return; }            // ✕/фон → крок «назад» (закриває верхній)
      var ex = e.target.closest && e.target.closest("[data-exp]");          // розгорнути/згорнути теми розділу в змісті
      if (ex) {
        e.preventDefault();
        var ul = document.getElementById(ex.getAttribute("data-exp"));
        if (ul) { var open = ul.hidden; ul.hidden = !open; ex.classList.toggle("open", open); ex.setAttribute("aria-expanded", String(open)); }
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && modalStack.length) { e.preventDefault(); closeViaHistory(); }
    });
    // права кнопка на будь-якому «відкривачі» попапа → скопіювати пряме посилання
    document.addEventListener("contextmenu", function (e) {
      var op = e.target.closest && e.target.closest("[data-share-token],[data-hist],[data-xbook]");
      if (!op) return;
      e.preventDefault();
      var token = op.getAttribute("data-share-token")
        || (op.hasAttribute("data-hist") ? "h:" + op.getAttribute("data-hist") : "b:" + (op.getAttribute("data-xbook") || ""));
      copyText(popupShareUrl(token));
    });
  }

  /* ── Старт ──────────────────────────────────────────────────────────── */
  initChrome();
  // якщо стартовий URL уже містить відкриті попапи — підкладемо базові записи історії,
  // щоб «назад»/закриття поверталися до статті, а не виходили зі сторінки
  (function normalizeDeepLink() {
    var r = parseHash();
    if (r.view === "chapter" && r.tokens && r.tokens.length) {
      history.replaceState(null, "", navUrl(r.slug, r.at, [], r.v));
      for (var k = 1; k <= r.tokens.length; k++) history.pushState(null, "", navUrl(r.slug, r.at, r.tokens.slice(0, k), r.v));
    }
  })();
  window.addEventListener("hashchange", route);
  window.addEventListener("popstate", route);
  route();
})();
