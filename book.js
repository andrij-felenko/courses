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
  var $content = document.getElementById("content");
  var $sidebar = document.getElementById("sidebar");

  /* ── Індекси за маніфестом ──────────────────────────────────────────── */
  var FLAT = [];          // усі розділи по порядку (вкл. ще не написані)
  var CH_BY_SLUG = {};    // slug → готовий розділ
  BOOK.modules.forEach(function (m) {
    m.chapters.forEach(function (c) {
      c.module = m;
      if (c.status === "done" && c.dir) {
        c.slug = c.dir.split("/").pop();
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

  /* Перетворення .md-лінків на маршрути книги (#ch=…&at=…) */
  function resolveHref(href, text, ctx) {
    if (/^(https?:|mailto:|tel:)/i.test(href)) return { href: href, external: true };
    if (href.charAt(0) === "#") return { href: href, external: false };
    var frag = ""; var hi = href.indexOf("#");
    if (hi >= 0) { frag = href.slice(hi + 1); href = href.slice(0, hi); }
    if (!/\.md$/i.test(href)) return { href: href, external: false };

    var parts = href.split("/");
    var file = parts.pop();
    var folder = null;
    for (var k = parts.length - 1; k >= 0; k--) { if (/^ch\d+-/.test(parts[k])) { folder = parts[k]; break; } }
    var slug = folder || ctx.currentSlug;
    var base = baseOf(file);
    var chap = findChapterBySlug(slug);
    var secM = text && String(text).match(/§\s*(\d+)\.(\d+)/);

    var at;
    if (slug === ctx.currentSlug) {
      if (chap && base === baseOf(chap.main)) {
        at = secM ? "sec-" + secM[1] + "-" + secM[2] : (/^sec-/.test(frag) ? frag : "top");
      } else { at = "hist-" + base; }
      return { href: "#ch=" + slug + "&at=" + at, external: false };
    }
    if (!chap || chap.status !== "done") return { href: "#ch=" + slug, external: false };
    if (base !== baseOf(chap.main)) at = "hist-" + base;
    else at = secM ? "sec-" + secM[1] + "-" + secM[2] : "";
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
      var m = t.text.match(/^(\d+)\.(\d+)\s+(.*)$/);
      if (m) {
        var id = "sec-" + m[1] + "-" + m[2];
        sections.push({ num: m[1] + "." + m[2], title: m[3], id: id });
        return '<span id="' + id + '" class="anc"></span><h2 class="sec-h"><span class="sn">§ ' +
          m[1] + "." + m[2] + "</span>" + renderInline(m[3], ctx) + "</h2>";
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
    if (!/^https?:|^\//.test(src)) src = BASE + ctx.dir + "/" + src;
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
    else if (/^📜/.test(text)) { kind = "hist"; icon = "📜"; }
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
    var body = text.replace(/^(🔧|📜|▶️|▶️?)\s*/, "");

    // 📜-вставка цього розділу → клікабельний тизер, що відкриває popup (а не лінк у кінець)
    if (kind === "hist" && primary) {
      var flat = body.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function (m, tx, href) {
        var b = baseOf(href.split("/").pop());
        return (ctx.histBases && ctx.histBases.has(b)) ? "**" + tx + "**" : tx;   // прибрати анкери: вся картка клікабельна
      });
      return '<a class="callout callout-hist hist-teaser" href="#" data-hist="' + primary + '">' +
        '<span class="callout-ico">📜</span><div class="callout-body">' + renderInline(flat.replace(/\n/g, " "), ctx) +
        '<span class="hist-open">📖 Відкрити вставку →</span></div></a>';
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
    var intro = [];
    while (idx < blocks.length && blocks[idx].type === "para") { intro.push(blocks[idx]); idx++; }
    var introHtml = intro.map(function (t) { return renderInline(t.text, ctx); }).join("<br><br>");
    var r = renderTokens(blocks.slice(idx), ctx);
    return { introHtml: introHtml, bodyHtml: r.html, sections: r.sections };
  }

  function parseHistory(text, filename, baseCtx) {
    var blocks = mdBlocks(text), idx = 0, title = filename;
    if (blocks[0] && blocks[0].type === "heading" && blocks[0].level === 1) {
      title = blocks[0].text.replace(/^📜\s*/, "").trim(); idx = 1;
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
  function renderChapter(chap) {
    setContent('<div class="state"><div class="spinner"></div>Завантаження розділу…</div>');
    var dir = chap.dir;
    var histFiles = chap.histories || [];
    Promise.all([fetchText(BASE + dir + "/" + chap.main)].concat(histFiles.map(function (h) { return fetchText(BASE + dir + "/" + h); })))
      .then(function (texts) {
        var mainText = texts[0], histTexts = texts.slice(1);
        var ctx = {
          currentSlug: chap.slug, dir: dir,
          histBases: new Set(histFiles.map(baseOf)), attach: []
        };
        var pm = parseMain(mainText, ctx);
        var arts = histFiles.map(function (h, k) { return parseHistory(histTexts[k], h, ctx); });

        var html = '<span id="top" class="anc"></span>';
        html += chapterHeader(chap, pm.introHtml);
        html += '<div class="sec content-body">' + pm.bodyHtml + "</div>";
        arts.forEach(function (a) { html += histModal(a); });   // приховані popup-вікна
        setContent(html);

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
    var m = chap.module;
    var h = '<header class="ch-header"><div class="ch-label">Модуль ' + m.n + " · " + escapeHtml(m.title) +
      " &nbsp;/&nbsp; Розділ " + chap.n + "</div><h1>" + escapeHtml(chap.title) + "</h1>";
    if (introHtml) h += '<p class="ch-intro">' + introHtml + "</p>";
    return h + "</header>";
  }

  function histModal(a) {
    var h = '<div class="hist-modal" id="histmodal-' + a.base + '" role="dialog" aria-modal="true" aria-label="' +
      escapeAttr(a.title) + '" hidden><div class="hist-modal-backdrop" data-close></div>' +
      '<div class="hist-modal-dialog"><button class="hist-modal-close" type="button" data-close aria-label="Закрити">✕</button>' +
      '<div class="hist-modal-scroll"><div class="hist-modal-head"><div class="hist-art-label">📜 Історична вставка</div><h1>' +
      escapeHtml(a.title) + "</h1>";
    if (a.introHtml) h += '<div class="hist-intro">' + a.introHtml + "</div>";
    h += '</div><div class="content-body">' + a.bodyHtml + "</div></div></div></div>";
    return h;
  }

  /* ════════════════════════════════════════════════════════════════════
     6) САЙДБАР РОЗДІЛУ
     ════════════════════════════════════════════════════════════════════ */
  function buildChapterSidebar(chap, sections, attach, arts) {
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
    s += '<a class="sb-logo" href="#"><span class="sb-logo-kicker">Зміст книги</span>' +
      '<span class="sb-logo-title">' + escapeHtml(BOOK.shortTitle) + "</span></a>";
    s += '<a class="sb-back" href="#">← Усі модулі та розділи</a>';
    s += '<div class="sb-group-label">Модуль ' + chap.module.n + "</div>";
    s += '<div class="sb-chap">Розділ ' + chap.n + ". " + escapeHtml(chap.title) + "</div>";
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

    s += chapterPager(chap);
    setSidebar(s);
  }

  function chapterPager(chap) {
    var i = FLAT.indexOf(chap), prev = FLAT[i - 1], next = FLAT[i + 1];
    function cell(c, dir) {
      var label = dir === "prev" ? "← Попередній розділ" : "Наступний розділ →";
      if (!c) {
        if (dir === "prev") return '<a href="#"><span class="pg-dir">↑ Назад</span><span class="pg-ttl">Зміст книги</span></a>';
        return "";
      }
      if (c.status === "done") {
        return '<a href="#ch=' + c.slug + '"><span class="pg-dir">' + label + '</span><span class="pg-ttl">' +
          c.n + ". " + escapeHtml(c.title) + "</span></a>";
      }
      return '<div style="display:block;background:#16242f;border:1px solid #28404f;border-radius:7px;padding:.55rem .75rem;opacity:.6">' +
        '<span class="pg-dir">' + label + '</span><span class="pg-ttl">' + c.n + ". " + escapeHtml(c.title) + " · незабаром</span></div>";
    }
    return '<div class="sb-pager">' + cell(prev, "prev") + cell(next, "next") + "</div>";
  }

  /* ════════════════════════════════════════════════════════════════════
     7) ОБКЛАДИНКА / МАПА КУРСУ
     ════════════════════════════════════════════════════════════════════ */
  function renderCover() {
    var doneCount = FLAT.filter(function (c) { return c.status === "done"; }).length;
    var h = '<header class="cover-hero"><div class="kicker">Курс · ' + BOOK.modules.length + " модулів</div>" +
      "<h1>" + escapeHtml(BOOK.title) + "</h1><p>" + escapeHtml(BOOK.subtitle) + "</p>" +
      '<div class="cover-stats">' +
      stat(BOOK.modules.length, "модулів") +
      stat(FLAT.length, "розділів") +
      stat(doneCount, "готових зараз") +
      "</div></header>";

    h += '<div class="toc">';
    BOOK.modules.forEach(function (m) {
      var done = m.chapters.filter(function (c) { return c.status === "done"; }).length;
      h += '<div class="module-block"><div class="module-head"><span class="m-num">Модуль ' + m.n + "</span>" +
        '<span class="m-ttl">' + escapeHtml(m.title) + "</span>" +
        '<span class="m-prog">' + done + " / " + m.chapters.length + ' готово</span></div><div class="ch-grid">';
      m.chapters.forEach(function (c) {
        if (c.status === "done") {
          var hc = (c.histories || []).length;
          h += '<a class="ch-card done" href="#ch=' + c.slug + '"><span class="c-num">' + c.n + "</span>" +
            '<span class="c-body"><span class="c-ttl">' + escapeHtml(c.title) + "</span>" +
            '<span class="c-meta">' + (hc ? hc + " історич. вставок · " : "") + "читати →</span></span></a>";
        } else {
          h += '<div class="ch-card pending"><span class="c-num">' + c.n + "</span>" +
            '<span class="c-body"><span class="c-ttl">' + escapeHtml(c.title) + "</span>" +
            '<span class="c-badge">незабаром</span></span></div>';
        }
      });
      h += "</div></div>";
    });
    h += "</div>";
    setContent(h);
    buildCoverSidebar();
  }
  function stat(num, lbl) { return '<div class="stat"><div class="num">' + num + '</div><div class="lbl">' + lbl + "</div></div>"; }

  function buildCoverSidebar() {
    var s = '<a class="sb-logo" href="#"><span class="sb-logo-kicker">Книга</span>' +
      '<span class="sb-logo-title">' + escapeHtml(BOOK.shortTitle) + "</span></a>";
    BOOK.modules.forEach(function (m) {
      s += '<div class="sb-group-label">Модуль ' + m.n + " · " + escapeHtml(m.title) + "</div>";
      m.chapters.forEach(function (c) {
        if (c.status === "done") {
          s += '<a class="sb-link" href="#ch=' + c.slug + '">' + c.n + ". " + escapeHtml(c.title) + "</a>";
        } else {
          s += '<span class="sb-link" style="opacity:.45;cursor:default">' + c.n + ". " + escapeHtml(c.title) + "</span>";
        }
      });
    });
    setSidebar(s);
  }

  function renderComingSoon(chap) {
    setContent('<div class="state"><h2>Розділ ' + chap.n + ". " + escapeHtml(chap.title) + "</h2>" +
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
    if (chap.status !== "done") { currentSlug = null; renderComingSoon(chap); return; }
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
      var cl = e.target.closest && e.target.closest("[data-close]");
      if (cl) { e.preventDefault(); closeAllModals(); }
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeAllModals(); });
  }

  /* ── Старт ──────────────────────────────────────────────────────────── */
  initChrome();
  window.addEventListener("hashchange", route);
  route();
})();
