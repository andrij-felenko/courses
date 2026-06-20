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
  // Префікс розгортання — тека, де лежить read.html/index.html (корінь репо в URL).
  // На GitHub Pages це «/courses/», локально — шлях до файлу. Шляхи «від кореня репо»
  // (/book/…, /guide/…, /catalog/…) у Markdown резолвимо саме сюди, інакше на Pages
  // «/book/…» пішло б на домен-корінь повз підтеку «/courses/».
  var SITE_ROOT = location.pathname.replace(/[^/]*$/, "");

  // Реєстр книг для крос-книжкових лінків [текст](book:<id>/<slug>[/<file>][#<topic>]).
  // Маніфест іншої книги тягнемо ліниво (при першому кліку) і кешуємо в _book.
  var XBOOK = {
    electronics: { manifest: "manifest.js",      basePath: "embedded/",   entry: "electronics.html", icon: "⚡",  label: "Вбудована електроніка" },
    chem:        { manifest: "manifest-chem.js", basePath: "chemistry/",  entry: "chem.html",        icon: "⚗️", label: "Хімія" },
    math:        { manifest: "manifest-math.js", basePath: "math/",       entry: "math.html",        icon: "🧮", label: "Математика" },
    components:  { manifest: "manifest-comp.js", basePath: "components/", entry: "comp.html",        icon: "🔌", label: "Компоненти" }
  };
  // Предметні книги book/<id> — для крос-попапів book:<id>/<slug> у новій структурі.
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

  // типи спец-вставок (підтем): історія / математика / компонент / практика
  var SPEC_META = {
    hist: { emoji: "📜", label: "Історія", modal: "Історична вставка" },
    math: { emoji: "🧮", label: "Математика", modal: "Математична вставка" },
    comp: { emoji: "🔌", label: "Компоненти", modal: "Компонентна вставка" },
    proj: { emoji: "⚙️", label: "Практика", modal: "Практична вставка" }
  };
  var SPEC_ORDER = ["hist", "math", "comp", "proj"];
  function specType(name) {                 // тип за іменем файла вставки
    var b = String(name).replace(/^.*\//, "");
    if (/^hist[-.]/i.test(b) || /history/i.test(b) || /-h-/.test(b)) return "hist";   // hist-… / …history… / нове <тема>-h-…
    if (/^math[-.]/i.test(b) || /-m-/.test(b)) return "math";        // нове math-… / старе -m-
    if (/^comp[-.]/i.test(b) || /-c-/.test(b)) return "comp";        // нове comp-… / старе -c-
    if (/^proj[-.]/i.test(b) || /-a-/.test(b)) return "proj";        // нове proj-… / старе -a-
    return "hist";
  }
  function emojiType(e) {                    // тип за emoji в _status.md
    return e === "🧮" ? "math" : e === "🔌" ? "comp" : (e === "⚙️" || e === "⚙") ? "proj" : "hist";
  }
  var $content = document.getElementById("content");
  var $sidebar = document.getElementById("sidebar");

  /* ── Індекси за маніфестом ──────────────────────────────────────────── */
  var FLAT = [];          // усі розділи по порядку (вкл. ще не написані)
  var CH_BY_SLUG = {};    // slug → готовий розділ
  BOOK.modules.forEach(function (m) {
    m.chapters.forEach(function (c) {
      c.module = m;
      if (c.dir && c.status && c.status !== "empty") {   // done/deeper/update — текст Є, отже читабельне
        c.slug = c.dir.split("/").pop();
        c.draft = c.status !== "done";                   // deeper/update — чернетка (читається, але позначена)
        CH_BY_SLUG[c.slug] = c;
      }
      FLAT.push(c);
    });
  });

  var currentSlug = null;   // який розділ зараз відрендерено
  var pendingTarget = null; // якір, до якого прокрутитись після рендеру
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

  /* Крос-книжкове посилання book:<id>/<slug>[/<file>][#<topic>] → дескриптор для popup */
  function resolveCrossBook(href) {
    var rest = href.replace(/^book:/i, "");
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
    if (/^book:/i.test(href)) return resolveCrossBook(href);
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
      return { href: "#ch=" + slug + "&at=" + at, external: false };
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

      var fence = line.match(/^\s*```(.*)$/);
      if (fence) {
        var buf = []; i++;
        while (i < n && !/^\s*```\s*$/.test(lines[i])) { buf.push(lines[i]); i++; }
        i++;
        blocks.push({ type: "pre", code: buf.join("\n") });
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
        if (reHeading.test(l) || /^\s*```/.test(l) || reHr.test(l) || reImg.test(l) ||
            /^\s*>/.test(l) || reListItem.test(l)) break;
        pbuf.push(l); i++;
      }
      blocks.push({ type: "para", text: pbuf.join(" ") });
    }
    return blocks;
  }

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
          html += "<pre><code>" + escapeHtml(t.code) + "</code></pre>"; break;
        case "hr":
          html += "<hr>"; break;
        case "figure":
          html += renderFigure(t, ctx); break;
        case "list":
          var tag = t.ordered ? "ol" : "ul";
          html += "<" + tag + ">" + t.items.map(function (it) { return "<li>" + renderInline(it, ctx) + "</li>"; }).join("") + "</" + tag + ">";
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
    if (/^\/(?:book|guide|catalog)\//.test(src)) src = SITE_ROOT + src.slice(1);  // від кореня репо → префікс розгортання
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
    var body = text.replace(/^(🔧|🏠|🧪|💡|📜|🧮|⚙️|⚙|🔌|🔗|▶️|▶)\s*/, "");

    // 🔗-вставка з book:-лінком → УСЯ картка клікабельна → крос-попап на іншу тему/предмет
    if (kind === "xref") {
      var bm = body.match(/\]\((book:[^)]+)\)/i);
      if (bm) {
        var cross = resolveCrossBook(bm[1]).cross;
        var flatx = body.replace(/\s*\[([^\]]+)\]\(book:[^)]+\)/ig, "").trim();
        return '<a class="callout callout-nav hist-teaser xref-teaser" href="#" data-xbook="' + escapeAttr(cross) + '" title="Відкрити повну тему">' +
          '<span class="callout-ico">🔗<span class="hist-expand" aria-hidden="true">⤢</span></span>' +
          '<div class="callout-body">' + renderInline(flatx.replace(/\n/g, " "), ctx) + "</div></a>";
      }
    }

    // вставка-картка (📜 hist · 🧮 math · 🔌 comp · ⚙️ proj) → УСЯ клікабельна → popup.
    // base беремо з лінка (primary); якщо тизер без лінка — наступна вставка цього типу за порядком.
    if (kind === "hist" || kind === "math" || kind === "comp" || kind === "proj") {
      var ibase = primary;
      if (!ibase && ctx.insQueue && ctx.insQueue[kind] && ctx.insQueue[kind].length) { ibase = ctx.insQueue[kind].shift(); if (ibase) ctx.attach.push({ base: ibase, after: sections.length - 1 }); }
      if (ibase) {
        var flat = body.replace(/\s*\[([^\]]+)\]\(([^)]+)\)/g, function (m, tx, href) {
          var b = baseOf(href.split("/").pop());
          return (ctx.histBases && ctx.histBases.has(b)) ? "" : tx;   // маркер вставки прибрати; сторонній лінк → текст
        }).trim();
        return '<a class="callout callout-' + kind + ' hist-teaser" href="#" data-hist="' + ibase + '" title="Розгорнути вставку">' +
          '<span class="callout-ico">' + icon + '<span class="hist-expand" aria-hidden="true">⤢</span></span>' +
          '<div class="callout-body">' + renderInline(flat.replace(/\n/g, " "), ctx) + "</div></a>";
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
    if (BOOK.type !== "book") {   // окремий «вступ» лише у старих embedded-розділах (перед ## секціями);
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
    var k = (base.match(/^(hist|math|comp|proj)-/) || [])[1] || "hist";
    var ic = { hist: "📜", math: "🧮", comp: "🔌", proj: "⚙️" }[k];
    return '<a class="callout callout-' + k + ' hist-teaser" href="#" data-hist="' + base + '" title="Розгорнути вставку">' +
      '<span class="callout-ico">' + ic + '<span class="hist-expand" aria-hidden="true">⤢</span></span>' +
      '<div class="callout-body">' + escapeHtml(label) + "</div></a>";
  }

  function renderChapter(chap) {
    setContent('<div class="state"><div class="spinner"></div>Завантаження розділу…</div>');
    var dir = chap.dir;
    var histFiles = chap.histories || [];
    var allFiles = histFiles.concat(chap.extras || []);   // історії + extras — усі як відкривні модалки
    Promise.all([fetchText(BASE + dir + "/" + chap.main)].concat(allFiles.map(function (f) { return fetchText(BASE + dir + "/" + f); })))
      .then(function (texts) {
        var mainText = texts[0], specTexts = texts.slice(1);
        var ctx = {
          currentSlug: chap.slug, dir: dir,
          histBases: new Set(allFiles.map(baseOf)), attach: [],
          insQueue: (function () { var q = { hist: [], math: [], comp: [], proj: [] }; allFiles.forEach(function (f) { var b = baseOf(f); var k = (b.match(/^(hist|math|comp|proj)-/) || [])[1]; if (k && q[k]) q[k].push(b); }); return q; })()
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
        html += chapterHeader(chap, pm.introHtml);
        html += '<div class="sec content-body">' + courseTopNav(chap) + versionLink(chap) + banner + pm.bodyHtml + courseBottomNav(chap) + "</div>";
        arts.forEach(function (a) { html += histModal(a); });   // приховані popup-вікна (історії + extras)
        setContent(html);
        document.body.classList.add("reading");

        buildChapterSidebar(chap, pm.sections, ctx.attach, arts);
        setupScrollSpy();
        scrollToAnchor(pendingTarget); pendingTarget = null;
      })
      .catch(function (e) {
        setContent('<div class="state error"><h2>Не вдалося завантажити розділ</h2><p>' +
          escapeHtml(e.message) + '</p><p>Схоже, книгу відкрито без веб-сервера (<code>file://</code>) — браузер блокує завантаження розділів. ' +
          'Поклади її на GitHub Pages (Settings → Pages → from root), або для локального перегляду запусти сервер із кореня репо: <code>python -m http.server</code>.</p>' +
          '<p><a href="#">← На головну</a></p></div>');
        buildCoverSidebar();
      });
  }

  function chapterHeader(chap, introHtml) {
    if (BOOK.type === "book") {   // стаття книги: компактна sticky-панель, галузь + назва, відтінок книги
      return '<header class="ch-header ch-header-book" style="--book-accent:' + (BOOK.accent || "") + '"><div class="ch-label">' +
        escapeHtml((chap.module && chap.module.title) || "") + "</div><h1>" + escapeHtml(chap.title) + "</h1></header>";
    }
    var m = chap.module;
    var h = '<header class="ch-header"><div class="ch-label">Модуль ' + m.n + " · " + escapeHtml(m.title) +
      " &nbsp;/&nbsp; Розділ " + m.n + "." + chap.n + "</div><h1>" + escapeHtml(chap.title) + "</h1>";
    if (introHtml) h += '<p class="ch-intro">' + introHtml + "</p>";
    return h + "</header>";
  }

  function histModal(a) {
    var t = SPEC_META[a.type] || SPEC_META.hist;
    var h = '<div class="hist-modal spec-' + (a.type || "hist") + '" id="histmodal-' + a.base + '" role="dialog" aria-modal="true" aria-label="' +
      escapeAttr(a.title) + '" hidden><div class="hist-modal-backdrop" data-close></div>' +
      '<div class="hist-modal-dialog"><button class="hist-modal-close" type="button" data-close aria-label="Закрити">✕</button>' +
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
    if (BOOK.course) { return buildCourseChapterSidebar(chap); }
    if (BOOK.type === "book") { return buildBookChapterSidebar(chap); }
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
    s += '<a class="sb-back" href="#">← Усі модулі та розділи</a>';
    s += '<div class="sb-group-label">Модуль ' + chap.module.n + "</div>";
    s += '<div class="sb-chap">Розділ ' + chap.module.n + "." + chap.n + " — " + escapeHtml(chap.title) + "</div>";
    s += '<a class="sb-link" data-target="top" href="#ch=' + slug + '&at=top">Вступ</a>';
    (attachedAfter[-1] || []).forEach(function (b) { s += subLink(b); });
    s += '<hr class="sb-divider">';

    sections.forEach(function (sec, idx) {
      s += '<a class="sb-link" data-target="' + sec.id + '" href="#ch=' + slug + "&at=" + sec.id + '">§ ' +
        sec.num + " — " + escapeHtml(sec.title) + "</a>";
      (attachedAfter[idx] || []).forEach(function (b) { s += subLink(b); });
    });

    var leftovers = (chap.histories || []).map(baseOf).filter(function (b) { return !attachedSet[b]; });
    if (leftovers.length) {
      s += '<hr class="sb-divider"><div class="sb-group-label">Історія</div>';
      leftovers.forEach(function (b) { s += subLink(b); });
    }

    // інші спец-вставки (математика / компоненти / практика) — згруповано за типом, клікабельні
    var extraTypes = ["math", "comp", "proj"];
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
      var label = BOOK.type === "book"
        ? (dir === "prev" ? "← Попередня тема" : "Наступна тема →")
        : (dir === "prev" ? "← Попередній розділ" : "Наступний розділ →");
      if (!c) {
        if (dir === "prev") return '<a href="#"><span class="pg-dir">↑ Назад</span><span class="pg-ttl">Зміст книги</span></a>';
        return "";
      }
      var ttl = BOOK.type === "book" ? escapeHtml(c.title) : (c.module.n + "." + c.n + " — " + escapeHtml(c.title));
      if (c.status === "done") {
        return '<a href="#ch=' + c.slug + '"><span class="pg-dir">' + label + '</span><span class="pg-ttl">' + ttl + "</span></a>";
      }
      return '<div style="display:block;background:#16242f;border:1px solid #28404f;border-radius:7px;padding:.55rem .75rem;opacity:.6">' +
        '<span class="pg-dir">' + label + '</span><span class="pg-ttl">' + ttl + " · незабаром</span></div>";
    }
    return '<div class="sb-pager">' + cell(prev, "prev") + cell(next, "next") + "</div>";
  }

  // Сайдбар відкритої статті книги: галузі → теми (без номерів), поточна підсвічена, + пейджер.
  function buildBookChapterSidebar(chap) {
    var s = (BOOK.libraryHref ? '<a class="sb-home" href="' + BOOK.libraryHref + '">← Бібліотека (усі книги)</a>' : "") +
      '<a class="sb-logo" href="#"><span class="sb-logo-kicker">Книга</span>' +
      '<span class="sb-logo-title">' + escapeHtml(BOOK.shortTitle) + "</span></a>" +
      '<a class="sb-back" href="#">← Усі галузі</a>';
    BOOK.modules.forEach(function (m) {
      if (!m.chapters.length) return;
      s += '<div class="sb-group-label">' + escapeHtml(m.title) + "</div>";
      m.chapters.forEach(function (c) {
        if (c.slug) {
          s += '<a class="sb-link' + (c.slug === chap.slug ? " active" : "") + '" href="#ch=' + c.slug + '">' + escapeHtml(c.title) + "</a>";
        } else {
          s += '<span class="sb-link" style="opacity:.4;cursor:default">' + escapeHtml(c.title) + "</span>";
        }
      });
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
        (c.steps || []).forEach(function (st, si) {
          var base = { kn: cn + "." + (si + 1), title: st.title, mTitle: m.title, cTitle: c.title };
          if (!st.ref) { base.bridge = true; out.push(base); return; }
          var pr = String(st.ref).split("/");
          base.subject = pr[0]; base.top = pr[pr.length - 1];
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
    return "read.html?course=" + encodeURIComponent(BOOK.course.slug) + "&book=" + encodeURIComponent(s.subject) + "#ch=" + encodeURIComponent(s.top);
  }
  function courseHome() { return "read.html?guide=" + encodeURIComponent(BOOK.course.slug); }

  function buildCourseChapterSidebar(chap) {
    var s = '<a class="sb-home" href="' + (BOOK.libraryHref || "index.html") + '">← Бібліотека</a>' +
      '<a class="sb-logo" href="' + courseHome() + '"><span class="sb-logo-kicker">Курс</span>' +
      '<span class="sb-logo-title">' + escapeHtml(BOOK.course.title) + "</span></a>" +
      '<a class="sb-back" href="' + courseHome() + '">← Огляд курсу</a>';
    (BOOK.course.modules || []).forEach(function (m, mi) {
      var mn = m.n || (mi + 1);
      s += '<div class="sb-group-label">Модуль ' + mn + " · " + escapeHtml(m.title) + "</div>";
      (m.chapters || []).forEach(function (c, ci) {
        var cn = mn + "." + (ci + 1);
        s += '<div class="sb-chap">' + cn + " · " + escapeHtml(c.title) + "</div>";
        (c.steps || []).forEach(function (st, si) {
          var kn = cn + "." + (si + 1);
          if (!st.ref) { s += '<span class="sb-link sb-bridge"><span class="sb-kn">' + kn + "</span>🔗 " + escapeHtml(st.title || "місток") + "</span>"; return; }
          var pr = String(st.ref).split("/"), subj = pr[0], top = pr[pr.length - 1];
          var cur = (subj === BOOK.bookSlug && top === chap.slug) ? " active" : "";
          s += '<a class="sb-link' + cur + '" href="read.html?course=' + encodeURIComponent(BOOK.course.slug) + "&book=" +
            encodeURIComponent(subj) + "#ch=" + encodeURIComponent(top) + '"><span class="sb-kn">' + kn + "</span>" + escapeHtml(st.title || top) + "</a>";
        });
      });
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
  // Компактне посилання між короткою (<slug>.md) і повною (<slug>-d.md) версіями статті.
  // Показуємо лише коли повна версія існує (chap.full); інакше — нічого (стаття просто коротка).
  function versionLink(chap) {
    if (!chap.full) return "";
    return '<a class="ver-link" href="#ch=' + chap.slug + '&v=d"><span class="vl-ico">📖</span>Повна версія цієї теми →</a>';
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
    if (BOOK.type === "book") { setContent(bookCoverHtml()); buildBookSidebar(); return; }
    setContent(coverHtml(coverMapFromManifest()));
    buildCoverSidebar();
  }

  // Обкладинка предметної книги: галузі (БЕЗ номерів) → теми-статті. Книга = набір статей без порядку.
  function bookCoverHtml() {
    var readable = FLAT.filter(function (c) { return c.slug; }).length;
    var fullCount = FLAT.filter(function (c) { return c.full; }).length;
    var live = BOOK.modules.filter(function (m) { return m.chapters.length; });
    var h = '<header class="cover-hero"><div class="kicker">Книга · теорія за галузями</div>' +
      "<h1>" + escapeHtml(BOOK.title) + "</h1>" + (BOOK.subtitle ? "<p>" + escapeHtml(BOOK.subtitle) + "</p>" : "") +
      '<div class="cover-stats">' + stat(live.length, "галузей") + stat(readable, "статей") + (fullCount ? stat(fullCount, "повних") : "") +
      "</div></header><div class=\"toc\">";
    live.forEach(function (m) {
      var d = m.chapters.filter(function (c) { return c.slug; }).length;
      h += '<div class="module-block"><div class="module-head"><span class="m-ttl">' + escapeHtml(m.title) + "</span>" +
        '<span class="m-prog">' + d + " / " + m.chapters.length + "</span></div><div class=\"ch-list\">";
      m.chapters.forEach(function (c) {
        if (c.slug) {   // є текст → читабельне (коротка або повна версія)
          h += '<div class="ch-item done"><div class="ch-row"><a class="ch-open" href="#ch=' + c.slug + '">' +
            '<span class="c-ttl">' + escapeHtml(c.title) + "</span>" +
            '<span class="c-go">' + (c.status === "done" ? "читати →" : "коротко →") + "</span></a></div></div>";
        } else {
          h += '<div class="ch-item pending"><div class="ch-row"><span class="c-ttl">' + escapeHtml(c.title) +
            '</span><span class="c-badge">незабаром</span></div></div>';
        }
      });
      h += "</div></div>";
    });
    return h + "</div>";
  }
  function buildBookSidebar() {
    var s = (BOOK.libraryHref ? '<a class="sb-home" href="' + BOOK.libraryHref + '">← Бібліотека (усі книги)</a>' : "") +
      '<a class="sb-logo" href="#"><span class="sb-logo-kicker">Книга</span>' +
      '<span class="sb-logo-title">' + escapeHtml(BOOK.shortTitle) + "</span></a>";
    BOOK.modules.forEach(function (m) {
      if (!m.chapters.length) return;
      s += '<div class="sb-group-label">' + escapeHtml(m.title) + "</div>";
      m.chapters.forEach(function (c) {
        if (c.slug) s += '<a class="sb-link" href="#ch=' + c.slug + '">' + escapeHtml(c.title) + "</a>";
        else s += '<span class="sb-link" style="opacity:.4;cursor:default">' + escapeHtml(c.title) + "</span>";
      });
    });
    setSidebar(s);
  }

  function coverHtml(topics) {
    var doneCount = FLAT.filter(function (c) { return c.status === "done"; }).length;
    var h = '<header class="cover-hero"><div class="kicker">Курс · ' + BOOK.modules.length + " модулів</div>" +
      "<h1>" + escapeHtml(BOOK.title) + "</h1><p>" + escapeHtml(BOOK.subtitle) + "</p>" +
      '<div class="cover-stats">' +
      stat(BOOK.modules.length, "модулів") + stat(FLAT.length, "розділів") + stat(doneCount, "готових зараз") +
      "</div></header>";

    h += '<div class="toc">';
    BOOK.modules.forEach(function (m) {
      var done = m.chapters.filter(function (c) { return c.status === "done"; }).length;
      h += '<div class="module-block"><div class="module-head"><span class="m-num">Модуль ' + m.n + "</span>" +
        '<span class="m-ttl">' + escapeHtml(m.title) + "</span>" +
        '<span class="m-prog">' + done + " / " + m.chapters.length + ' готово</span></div><div class="ch-list">';
      m.chapters.forEach(function (c) {
        var mr = m.n + "." + c.n;
        if (c.status === "done") {
          var entry = topics[mr] || { topics: [], specs: [] };
          var tops = entry.topics || [], specs = entry.specs || [];
          var tid = "tp-" + mr.replace(/\./g, "-");
          var btnLabel = plTopics(tops.length) + (specs.length ? " · " + specs.length + " вставок" : "");
          h += '<div class="ch-item done"><div class="ch-row">' +
            '<a class="ch-open" href="#ch=' + c.slug + '"><span class="c-num">' + mr + "</span>" +
            '<span class="c-ttl">' + escapeHtml(c.title) + "</span>" +
            '<span class="c-go">читати →</span></a>';
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
      h += "</div></div>";
    });
    return h + "</div>";
  }
  function stat(num, lbl) { return '<div class="stat"><div class="num">' + num + '</div><div class="lbl">' + lbl + "</div></div>"; }

  function buildCoverSidebar() {
    var s = (BOOK.libraryHref ? '<a class="sb-home" href="' + BOOK.libraryHref + '">← Бібліотека (усі книги)</a>' : "") +
      '<a class="sb-logo" href="#"><span class="sb-logo-kicker">Книга</span>' +
      '<span class="sb-logo-title">' + escapeHtml(BOOK.shortTitle) + "</span></a>";
    BOOK.modules.forEach(function (m) {
      s += '<div class="sb-group-label">Модуль ' + m.n + " · " + escapeHtml(m.title) + "</div>";
      m.chapters.forEach(function (c) {
        if (c.status === "done") {
          s += '<a class="sb-link" href="#ch=' + c.slug + '">' + m.n + "." + c.n + " · " + escapeHtml(c.title) + "</a>";
        } else {
          s += '<span class="sb-link" style="opacity:.45;cursor:default">' + m.n + "." + c.n + " · " + escapeHtml(c.title) + "</span>";
        }
      });
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
  function parseHash() {
    var hsh = location.hash.replace(/^#/, "");
    if (!hsh) return { view: "cover" };
    var p = {};
    hsh.split("&").forEach(function (kv) { var a = kv.split("="); p[a[0]] = decodeURIComponent(a[1] || ""); });
    if (p.ch) return { view: "chapter", slug: p.ch, at: p.at || null };
    return { view: "cover" };
  }

  function route() {
    var r = parseHash();
    closeMobileSidebar();
    closeAllModals();
    if (r.view === "cover") { currentSlug = null; renderCover(); window.scrollTo(0, 0); return; }
    var chap = CH_BY_SLUG[r.slug];
    if (!chap) {
      var any = null;
      BOOK.modules.forEach(function (m) { m.chapters.forEach(function (c) { if (c.status !== "done" && c.slug === r.slug) any = c; }); });
      currentSlug = null;
      if (any) renderComingSoon(any); else renderCover();
      return;
    }
    if (r.slug === currentSlug) { scrollToAnchor(r.at); markActive(r.at); return; }
    currentSlug = r.slug; pendingTarget = r.at || null; renderChapter(chap);
  }

  function scrollToAnchor(at) {
    if (!at) { window.scrollTo(0, 0); return; }
    if (at.indexOf("hist-") === 0) { openHist(at.slice(5)); return; }   // deep-link на історію → popup
    var el = document.getElementById(at);
    if (el) el.scrollIntoView({ behavior: "auto", block: "start" });
    else window.scrollTo(0, 0);
    markActive(at);
  }
  function markActive(at) {
    var links = $sidebar.querySelectorAll("[data-target]");
    for (var i = 0; i < links.length; i++) links[i].classList.toggle("active", links[i].getAttribute("data-target") === at);
  }

  /* ── Popup історичної вставки ───────────────────────────────────────── */
  function openHist(base) {
    closeAllModals();
    var m = document.getElementById("histmodal-" + base);
    if (!m) return;
    m.hidden = false;
    document.body.classList.add("modal-open");
    var sc = m.querySelector(".hist-modal-scroll"); if (sc) sc.scrollTop = 0;
    var cl = m.querySelector(".hist-modal-close"); if (cl) cl.focus();
  }
  function closeAllModals() {
    var ms = document.querySelectorAll(".hist-modal");
    for (var i = 0; i < ms.length; i++) ms[i].hidden = true;
    document.body.classList.remove("modal-open");
  }

  /* ── Крос-книжковий popup: матеріал з ІНШОЇ книги (book:<id>/<slug>…) ──── */
  function loadXBook(id) {
    var reg = XBOOK[id];
    if (!reg) return Promise.reject(new Error("Невідома книга: " + id));
    if (reg._book) return Promise.resolve(reg._book);
    if (reg.basePath === BASE) { reg._book = BOOK; return Promise.resolve(BOOK); }
    return fetchText(reg.manifest).then(function (src) {
      // Новий формат індексу (BOOK_META+BOOK_MODULES) збираємо через bookbuild.js;
      // legacy (window.BOOK у самому файлі) — як раніше.
      var p = window.bookFromIndexSrc
        ? window.bookFromIndexSrc(src, reg.basePath)
        : Promise.resolve((function () { try { return new Function("window", src + "\n;return window.BOOK;")({}); } catch (e) { return null; } })());
      return Promise.resolve(p).then(function (book) { reg._book = book; return book; });
    });
  }
  function chapInBook(book, slug) {
    var found = null;
    ((book && book.modules) || []).forEach(function (m) {
      (m.chapters || []).forEach(function (c) {
        if (c.status === "done" && c.dir && c.dir.split("/").pop() === slug) { c.module = c.module || m; found = c; }
      });
    });
    return found;
  }
  function xbookHost() {
    var h = document.getElementById("xbook-host");
    if (!h) { h = document.createElement("div"); h.id = "xbook-host"; document.body.appendChild(h); }
    return h;
  }
  function showXbookModal(html) {
    var host = xbookHost();
    host.innerHTML = html;
    document.body.classList.add("modal-open");
    var sc = host.querySelector(".hist-modal-scroll"); if (sc) sc.scrollTop = 0;
    var cl = host.querySelector(".hist-modal-close"); if (cl) cl.focus();
  }
  function xbookShell(reg, slug, frag, headHtml, innerHtml) {
    var openHref = reg ? reg.entry + "#ch=" + encodeURIComponent(slug) + (frag ? "&at=" + encodeURIComponent(frag) : "") : "#";
    var lbl = reg ? reg.icon + " Інша книга · " + escapeHtml(reg.label) : "Інша книга";
    var btn = '<a href="' + escapeAttr(openHref) + '" style="display:inline-block;margin-top:1.1rem;padding:.5rem .9rem;background:#1d6fa4;color:#fff;border-radius:7px;text-decoration:none">' +
      (reg ? "Відкрити книгу «" + escapeHtml(reg.label) + "» →" : "Відкрити книгу →") + "</a>";
    return '<div class="hist-modal spec-comp xbook-modal" role="dialog" aria-modal="true">' +
      '<div class="hist-modal-backdrop" data-close></div>' +
      '<div class="hist-modal-dialog"><button class="hist-modal-close" type="button" data-close aria-label="Закрити">✕</button>' +
      '<div class="hist-modal-scroll"><div class="hist-modal-head"><div class="hist-art-label">' + lbl + "</div>" + headHtml + "</div>" +
      '<div class="content-body">' + innerHtml + btn + "</div></div></div></div>";
  }
  // знайти тему за slug у будь-якій предметній книзі (будь-який статус, аби був текст)
  function chapInBookAny(book, slug) {
    var found = null;
    ((book && book.modules) || []).forEach(function (m) {
      (m.chapters || []).forEach(function (c) {
        if (c.dir && c.dir.split("/").pop() === slug) { c.module = c.module || m; found = c; }
      });
    });
    return found;
  }
  // book:<id>/<slug> у НОВІЙ структурі book/<id> → попап зі статтею тієї теми
  function openBookRef(subject, slug, frag) {
    closeAllModals();
    var meta = SUBJECT_META[subject] || { icon: "📘", label: subject };
    var reg = { entry: "read.html?book=" + encodeURIComponent(subject), icon: meta.icon, label: meta.label };
    function show(head, inner) { showXbookModal(xbookShell(reg, slug, frag, head, inner)); }
    var loader = (subject === BOOK.bookSlug) ? Promise.resolve(BOOK)
      : (_subjCache[subject] ? Promise.resolve(_subjCache[subject])
        : window.loadSubjectBook(subject).then(function (b) { _subjCache[subject] = b; return b; }));
    loader.then(function (bk) {
      var chap = bk && chapInBookAny(bk, slug);
      if (!chap || !chap.dir || chap.status === "empty") {
        show("<h1>" + escapeHtml((chap && chap.title) || slug.replace(/-/g, " ")) + "</h1>",
          '<p>📝 Ця тема ще <strong>в розробці</strong> — її напишуть за першим посиланням сюди.</p>');
        return;
      }
      var base = bk.basePath || ("book/" + subject + "/");
      fetchText(base + chap.dir + "/" + chap.main).then(function (text) {
        var ctx = { currentSlug: slug, dir: chap.dir, base: base, histBases: new Set(), attach: [] };
        var pm = parseMain(text, ctx);
        var body = pm.bodyHtml.replace(/src="(img\/[^"]+)"/g, 'src="' + base + chap.dir + '/$1"');
        show("<h1>" + escapeHtml(chap.title) + "</h1>", body);
      }).catch(function (e) {
        show("<h1>" + escapeHtml(chap.title || slug) + "</h1>", "<p>Не вдалося завантажити (<code>" + escapeHtml(e.message) + "</code>).</p>");
      });
    });
  }
  function openCrossBook(book, slug, file, frag) {
    if (window.loadSubjectBook && SUBJECT_META[book]) { openBookRef(book, slug, frag); return; }
    closeAllModals();
    var reg = XBOOK[book];
    if (!reg) { showXbookModal(xbookShell(null, slug, frag, "<h1>" + escapeHtml(slug || "Розділ") + "</h1>", "<p>Невідома книга <code>" + escapeHtml(book) + "</code>.</p>")); return; }
    loadXBook(book).then(function (bk) {
      var chap = bk && chapInBook(bk, slug);
      if (!chap) {
        var title = slug ? slug.replace(/-/g, " ") : ((bk && bk.title) || reg.label);
        showXbookModal(xbookShell(reg, slug, frag, "<h1>" + escapeHtml(title) + "</h1>",
          '<p>📝 Ця тема ще <strong>в розробці</strong>. Її напишуть за першим посиланням сюди. ' +
          "Поки що відкрий книгу — там видно загальну мапу й сусідні теми.</p>"));
        return;
      }
      var fname = file || chap.main;
      fetchText(reg.basePath + chap.dir + "/" + fname).then(function (text) {
        var ctx = { currentSlug: slug, dir: chap.dir, base: reg.basePath, histBases: new Set(), attach: [] };
        var a = parseHistory(text, fname, ctx);
        showXbookModal(xbookShell(reg, slug, frag, "<h1>" + escapeHtml(a.title) + "</h1>",
          (a.introHtml ? '<div class="hist-intro">' + a.introHtml + "</div>" : "") + a.bodyHtml));
      }).catch(function (e) {
        showXbookModal(xbookShell(reg, slug, frag, "<h1>" + escapeHtml(chap.title || slug) + "</h1>",
          "<p>Не вдалося завантажити матеріал (<code>" + escapeHtml(e.message) + "</code>).</p>"));
      });
    }).catch(function () {
      showXbookModal(xbookShell(reg, slug, frag, "<h1>" + escapeHtml(slug) + "</h1>",
        '<p>Не вдалося завантажити маніфест книги «' + escapeHtml(reg.label) + "».</p>"));
    });
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

  function setContent(html) { $content.innerHTML = html; }
  function setSidebar(html) { $sidebar.innerHTML = html; }
  function closeMobileSidebar() { $sidebar.classList.remove("open"); }

  /* ── Глобальні елементи UI ──────────────────────────────────────────── */
  function initChrome() {
    if (BOOK.type === "book") document.body.classList.add("book-mode");   // CSS-гачок: лагідні вставки без фону
    if (BOOK.course) document.body.classList.add("course-mode");
    var menu = document.getElementById("menu-btn");
    var scrim = document.getElementById("scrim");
    var top = document.getElementById("back-top");
    if (menu) menu.addEventListener("click", function () { $sidebar.classList.toggle("open"); });
    if (scrim) scrim.addEventListener("click", closeMobileSidebar);
    if (top) {
      top.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
      window.addEventListener("scroll", function () { top.classList.toggle("vis", window.scrollY > 600); });
    }
    // делеговані кліки: відкрити/закрити popup історичної вставки
    document.addEventListener("click", function (e) {
      var op = e.target.closest && e.target.closest("[data-hist]");
      if (op) { e.preventDefault(); openHist(op.getAttribute("data-hist")); return; }
      var xb = e.target.closest && e.target.closest("[data-xbook]");
      if (xb) {
        e.preventDefault();
        var pp = (xb.getAttribute("data-xbook") || "").split("|");
        openCrossBook(pp[0] || "", pp[1] || "", pp[2] || "", pp[3] || "");
        return;
      }
      var cl = e.target.closest && e.target.closest("[data-close]");
      if (cl) { e.preventDefault(); closeAllModals(); return; }
      var ex = e.target.closest && e.target.closest("[data-exp]");   // розгорнути/згорнути теми розділу в змісті
      if (ex) {
        e.preventDefault();
        var ul = document.getElementById(ex.getAttribute("data-exp"));
        if (ul) { var op = ul.hidden; ul.hidden = !op; ex.classList.toggle("open", op); ex.setAttribute("aria-expanded", String(op)); }
      }
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeAllModals(); });
  }

  /* ── Старт ──────────────────────────────────────────────────────────── */
  initChrome();
  window.addEventListener("hashchange", route);
  route();
})();
