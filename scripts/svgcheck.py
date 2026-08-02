# -*- coding: utf-8 -*-
"""svgcheck — ЛОКАЛЬНА геометрична перевірка згенерованих SVG (жодних агентів і токенів).
Замінює LLM-переогляд кожного файлу: textbox()/fitbox() зі svgkit уже гарантують,
що текст не вилазить за СВОЮ рамку; цей скрипт ловить усе інше, що заважає ЗРОЗУМІТИ фігуру.

Що перевіряє:
  • елементи поза viewBox (хибні координати) і rect, що вилазить за край;
  • нечитабельно дрібний шрифт;
  • ТЕКСТ↔ТЕКСТ — написи перетинаються;
  • ЛІНІЯ/КОНТУР↔ТЕКСТ — крізь напис проходить <line>, <polyline>, <polygon>, <path>
    (M/L/H/V/C/Q/S/A/Z, включно з відносними) або РАМКА rect/circle/ellipse;
  • НАПИС ЗА ПОЛОТНОМ — bbox тексту зрізаний краєм (типово: text-anchor="end" з довгим рядком);
  • БЛОКИ НАЛАЗЯТЬ — два залитих rect частково накривають один одного (вкладеність і тло — норма);
  • --links: усі svg, підключені в .md теми, справді існують у img/.

Обережність: якщо у файлі є <g transform=…> (координати дітей зміщені), геометричні перевірки
пропускаються — краще мовчати, ніж вигадувати перетини; так само пропускаються <text transform=…>.

    python svgcheck.py <тека|файл> [--min-font 9] [--tol 6] [--links]

Код виходу 0 — чисто; 1 — є зауваження (стислий звіт: до 4 зауважень на файл, з координатами).
"""
import sys, os, re, glob


# ── (v6) bbox тексту й перетини — перевірка накладання ───────────────────────
def _vlen(s):
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')):
        s = s.replace(a, b)
    return len(s)


def _text_boxes(s):
    """bbox кожного <text> (враховує <tspan>-рядки, text-anchor, bold). Ширина — як у svgkit (0.57/0.62)."""
    boxes = []
    for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", s, re.S):
        attrs, inner = m.group(1), m.group(2)
        if "transform=" in attrs:            # повернутий/зсунутий напис — координати не в системі полотна, не судимо
            continue

        def at(name, d=None):
            mm = re.search(r'\b%s="([^"]*)"' % name, attrs)
            return mm.group(1) if mm else d
        try:
            x = float(at("x", "0")); y = float(at("y", "0")); size = float(at("font-size", "14"))
        except ValueError:
            continue
        anchor = at("text-anchor", "start")
        # для ДЕТЕКЦІЇ накладання беремо РЕАЛЬНУ ширину гліфа (≈0.5·size), а не svgkit-ву «із запасом» 0.57 —
        # інакше bbox надто широкий і дає фантомні перетини
        k = 0.54 if 'font-weight="700"' in attrs else 0.50
        rows = []  # (baseline_y, left, right)
        tspans = re.findall(r"<tspan\b([^>]*)>(.*?)</tspan>", inner, re.S)
        if tspans:
            by = y
            for ta, tc in tspans:
                mdy = re.search(r'\bdy="(-?[\d.]+)"', ta); by += float(mdy.group(1)) if mdy else 0.0
                mx = re.search(r'\bx="(-?[\d.]+)"', ta); lx = float(mx.group(1)) if mx else x
                w = _vlen(re.sub(r"<[^>]+>", "", tc)) * size * k
                left = lx - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
                rows.append((by, left, left + w))
        else:
            w = _vlen(re.sub(r"<[^>]+>", "", inner)) * size * k
            left = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
            rows.append((y, left, left + w))
        top = min(by - size * 0.72 for by, _, _ in rows)
        bot = max(by + size * 0.16 for by, _, _ in rows)
        L = min(l for _, l, _ in rows); R = max(r for _, _, r in rows)
        if R > L and bot > top:
            boxes.append((L, top, R, bot))
    return boxes


def _pts(s):
    """Числа з points="x,y x,y …" → [(x, y), …]."""
    nums = [float(v) for v in re.findall(r"-?[\d.]+", s)]
    return list(zip(nums[0::2], nums[1::2]))


def _path_segments(d, curve_steps=4):
    """Груба полілінія з path d=…: M/L/H/V/Z точно, C/Q семплюємо, A — хордою.
    Потрібно, бо стрілки, дуги й ламані у фігурах — це <path>, а не <line>."""
    segs, cur, start = [], (0.0, 0.0), (0.0, 0.0)
    toks = re.findall(r"([MmLlHhVvCcSsQqTtAaZz])|(-?[\d.]+(?:e-?\d+)?)", d)
    items, cmd, nums = [], None, []
    for c, n in toks:
        if c:
            if cmd:
                items.append((cmd, nums))
            cmd, nums = c, []
        elif cmd:
            nums.append(float(n))
    if cmd:
        items.append((cmd, nums))

    def bez(p0, ctrl, p1, quad=False):
        out = []
        for i in range(1, curve_steps + 1):
            t = i / float(curve_steps)
            if quad:
                x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * ctrl[0][0] + t * t * p1[0]
                y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * ctrl[0][1] + t * t * p1[1]
            else:
                x = ((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * ctrl[0][0]
                     + 3 * (1 - t) * t * t * ctrl[1][0] + t ** 3 * p1[0])
                y = ((1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * ctrl[0][1]
                     + 3 * (1 - t) * t * t * ctrl[1][1] + t ** 3 * p1[1])
            out.append((x, y))
        return out

    for c, n in items:
        rel = c.islower()
        C = c.upper()
        i = 0
        while True:
            if C == "Z":
                if cur != start:
                    segs.append((cur[0], cur[1], start[0], start[1]))
                cur = start
                break
            need = {"M": 2, "L": 2, "T": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "A": 7}[C]
            if i + need > len(n):
                break
            a = n[i:i + need]; i += need
            if C in ("M", "L", "T"):
                p = (cur[0] + a[0], cur[1] + a[1]) if rel else (a[0], a[1])
                if C != "M":
                    segs.append((cur[0], cur[1], p[0], p[1]))
                else:
                    start = p
                cur = p
                if C == "M":
                    C = "L"                     # наступні пари після M — це L
            elif C == "H":
                p = (cur[0] + a[0], cur[1]) if rel else (a[0], cur[1])
                segs.append((cur[0], cur[1], p[0], p[1])); cur = p
            elif C == "V":
                p = (cur[0], cur[1] + a[0]) if rel else (cur[0], a[0])
                segs.append((cur[0], cur[1], p[0], p[1])); cur = p
            elif C in ("C", "S", "Q", "A"):
                if C == "C":
                    c1 = (cur[0] + a[0], cur[1] + a[1]) if rel else (a[0], a[1])
                    c2 = (cur[0] + a[2], cur[1] + a[3]) if rel else (a[2], a[3])
                    p = (cur[0] + a[4], cur[1] + a[5]) if rel else (a[4], a[5])
                    pts = bez(cur, (c1, c2), p)
                elif C == "Q":
                    c1 = (cur[0] + a[0], cur[1] + a[1]) if rel else (a[0], a[1])
                    p = (cur[0] + a[2], cur[1] + a[3]) if rel else (a[2], a[3])
                    pts = bez(cur, (c1,), p, quad=True)
                elif C == "S":
                    c1 = (cur[0] + a[0], cur[1] + a[1]) if rel else (a[0], a[1])
                    p = (cur[0] + a[2], cur[1] + a[3]) if rel else (a[2], a[3])
                    pts = bez(cur, (c1, c1), p)
                else:                            # A — дугу беремо хордою (консервативно)
                    p = (cur[0] + a[5], cur[1] + a[6]) if rel else (a[5], a[6])
                    pts = [p]
                prev = cur
                for q in pts:
                    segs.append((prev[0], prev[1], q[0], q[1])); prev = q
                cur = prev
            if i >= len(n):
                break
    return segs


def _seg_lines(s):
    """УСІ лінії фігури, а не лише <line>: polyline/polygon/path і РАМКИ прямокутників,
    кіл та еліпсів (їх контур теж не має різати написи)."""
    segs = []
    for m in re.finditer(r"<line\b([^>]*)/?>", s):
        a = m.group(1)

        def g(n):
            mm = re.search(r'\b%s="(-?[\d.]+)"' % n, a)
            return float(mm.group(1)) if mm else None
        p = (g("x1"), g("y1"), g("x2"), g("y2"))
        if None not in p:
            segs.append(p)
    for m in re.finditer(r'<(polyline|polygon)\b[^>]*\bpoints="([^"]+)"[^>]*>', s):
        pts = _pts(m.group(2))
        if m.group(1) == "polygon" and len(pts) > 2:
            pts = pts + [pts[0]]
        for i in range(len(pts) - 1):
            segs.append((pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]))
    for m in re.finditer(r'<path\b[^>]*\bd="([^"]+)"[^>]*>', s):
        segs.extend(_path_segments(m.group(1)))
    for m in re.finditer(r"<rect\b([^>]*)>", s):
        a = m.group(1)

        def g(n, d=None):
            mm = re.search(r'\b%s="(-?[\d.]+)"' % n, a)
            return float(mm.group(1)) if mm else d
        x, y, w, h = g("x"), g("y"), g("width"), g("height")
        if None in (x, y, w, h):
            continue
        segs += [(x, y, x + w, y), (x + w, y, x + w, y + h), (x + w, y + h, x, y + h), (x, y + h, x, y)]
    for m in re.finditer(r"<(circle|ellipse)\b([^>]*)>", s):
        a = m.group(2)

        def g(n, d=None):
            mm = re.search(r'\b%s="(-?[\d.]+)"' % n, a)
            return float(mm.group(1)) if mm else d
        cx, cy = g("cx", 0.0), g("cy", 0.0)
        rx = g("r") if m.group(1) == "circle" else g("rx")
        ry = rx if m.group(1) == "circle" else g("ry")
        if not rx or not ry:
            continue
        import math
        prev = None
        for k in range(17):                       # 16-кутник — досить для контролю перетинів
            ang = 2 * math.pi * k / 16.0
            p = (cx + rx * math.cos(ang), cy + ry * math.sin(ang))
            if prev:
                segs.append((prev[0], prev[1], p[0], p[1]))
            prev = p
    return segs


def _solid_boxes(s, canvas=None):
    """Видимі прямокутні блоки (мають fill і не є прозорим тлом) — для контролю зіткнень блоків.
    Тло/панель на все полотно (≥70% площі) НЕ рахуємо блоком: під ним і мають лежати інші."""
    boxes = []
    area_all = (canvas[0] * canvas[1]) if canvas else None
    for m in re.finditer(r"<rect\b([^>]*)>", s):
        a = m.group(1)

        def g(n, d=None):
            mm = re.search(r'\b%s="(-?[\d.]+)"' % n, a)
            return float(mm.group(1)) if mm else d
        x, y, w, h = g("x"), g("y"), g("width"), g("height")
        if None in (x, y, w, h) or w <= 0 or h <= 0:
            continue
        fill = re.search(r'\bfill="([^"]*)"', a)
        fill = fill.group(1) if fill else ""
        if fill in ("none", "transparent"):
            continue
        if area_all and (w * h) >= 0.70 * area_all:
            continue
        boxes.append((x, y, x + w, y + h))
    return boxes


def _area_overlap(a, b):
    """Частка площі меншого bbox, що перекрита більшим (0..1)."""
    ox = min(a[2], b[2]) - max(a[0], b[0])
    oy = min(a[3], b[3]) - max(a[1], b[1])
    if ox <= 0 or oy <= 0:
        return 0.0
    sm = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return (ox * oy) / sm if sm > 0 else 0.0


def _seg_hits_box(seg, box, shrink=0.22):
    """Чи проходить відрізок НАСКРІЗЬ крізь напис. Вимоги, щоб не ловити стрілки-вказівники:
    обидва кінці ПОЗА bbox (лінія не впирається в напис, а перетинає його) + внутрішній семпл у ядрі bbox."""
    x1, y1, x2, y2 = seg

    def outside(px, py):
        return not (box[0] <= px <= box[2] and box[1] <= py <= box[3])
    if not (outside(x1, y1) and outside(x2, y2)):
        return False
    mx = (box[2] - box[0]) * shrink; my = (box[3] - box[1]) * shrink
    rx0, ry0, rx1, ry1 = box[0] + mx, box[1] + my, box[2] - mx, box[3] - my
    if rx1 <= rx0 or ry1 <= ry0:
        return False
    inside = 0
    for i in range(1, 40):  # лише ВНУТРІШНІ семпли, не кінці
        t = i / 40.0
        px = x1 + (x2 - x1) * t; py = y1 + (y2 - y1) * t
        if rx0 <= px <= rx1 and ry0 <= py <= ry1:
            inside += 1
            if inside >= 2:      # обидва кінці поза bbox + прохід крізь ядро = наскрізний різ, не дотик
                return True
    return False


def check_svg(path, min_font=9, tol=6.0):
    issues = []
    try:
        s = open(path, encoding="utf-8").read()
    except Exception as e:
        return ["не прочитати: %s" % e]

    m = re.search(r'viewBox="([^"]+)"', s)
    if not m:
        return ["немає viewBox"]
    vb = re.split(r"[ ,]+", m.group(1).strip())
    if len(vb) < 4:
        return ["дивний viewBox: %s" % m.group(1)]
    try:
        x0, y0, W, H = (float(vb[0]), float(vb[1]), float(vb[2]), float(vb[3]))
    except ValueError:
        return ["дивний viewBox: %s" % m.group(1)]
    xmax, ymax = x0 + W, y0 + H

    # координати-атрибути поза межами полотна
    axes = [("x", x0, xmax), ("cx", x0, xmax), ("x1", x0, xmax), ("x2", x0, xmax),
            ("y", y0, ymax), ("cy", y0, ymax), ("y1", y0, ymax), ("y2", y0, ymax)]
    for attr, lo, hi in axes:
        for val in re.findall(r'\b%s="(-?[\d.]+)"' % attr, s):
            try:
                v = float(val)
            except ValueError:
                continue
            if v < lo - tol or v > hi + tol:
                issues.append("%s=%.0f поза [%.0f..%.0f]" % (attr, v, lo, hi))
                break  # одного прикладу на атрибут досить

    # rect, що вилазить правим/нижнім краєм
    for rm in re.finditer(r'<rect x="(-?[\d.]+)" y="(-?[\d.]+)" width="([\d.]+)" height="([\d.]+)"', s):
        rx, ry, rw, rh = map(float, rm.groups())
        if rx + rw > xmax + tol or ry + rh > ymax + tol:
            issues.append("rect виходить за межі (правий/нижній край %.0f×%.0f у %.0f×%.0f)"
                          % (rx + rw, ry + rh, xmax, ymax))
            break

    # нечитабельно дрібний шрифт
    for fs in re.findall(r'font-size="(\d+)"', s):
        if int(fs) < min_font:
            issues.append("шрифт %spx < %d" % (fs, min_font))
            break

    # Геометрію судимо лише в чистій системі координат: якщо є <g transform=…>, координати дітей
    # зміщені/повернуті, і будь-який висновок про перетини був би вигаданим — тихо пропускаємо.
    if re.search(r"<g\b[^>]*transform=", s):
        return issues

    # (v6) накладання тексту: текст↔текст і текст↔лінія (текст має бути поза чужими написами й лініями).
    # Пороги свідомо КОНСЕРВАТИВНІ (реальний шматок перекриття, а не дотик) — bbox оцінюється грубо.
    tb = _text_boxes(s)
    done_tt = False
    for i in range(len(tb)):
        for j in range(i + 1, len(tb)):
            ox = min(tb[i][2], tb[j][2]) - max(tb[i][0], tb[j][0])
            oy = min(tb[i][3], tb[j][3]) - max(tb[i][1], tb[j][1])
            if ox > 6 and oy > 7:                      # перекриття ≈ пів-символа × пів-рядка
                issues.append("текст накладається на текст (написи перетинаються)")
                done_tt = True
                break
        if done_tt:
            break
    segs = _seg_lines(s)
    for box in tb:
        for sg in segs:
            if _seg_hits_box(sg, box):
                issues.append("лінія/контур перетинає текст біля (%.0f,%.0f) — напис має стояти ПОЗА лініями"
                              % (box[0], box[1]))
                break
        else:
            continue
        break

    # напис, зрізаний краєм полотна (bbox тексту вилазить за viewBox; поріг — реальне зрізання, не піксель)
    CLIP = max(tol, 8.0)
    for box in tb:
        if box[0] < x0 - CLIP or box[1] < y0 - CLIP or box[2] > xmax + CLIP or box[3] > ymax + CLIP:
            issues.append("напис вилазить за полотно (bbox %.0f..%.0f × %.0f..%.0f у %.0f×%.0f) — розсунь viewBox"
                          % (box[0], box[2], box[1], box[3], xmax, ymax))
            break

    # блоки, що ЧАСТКОВО налазять один на одного (вкладеність — норма: панель у панелі)
    sb = _solid_boxes(s, (W, H))
    done_bb = False
    T = 2.0                                   # допуск вкладеності: піксельні виступи — не зіткнення
    for i in range(len(sb)):
        for j in range(i + 1, len(sb)):
            a, b = sb[i], sb[j]
            contains = (a[0] <= b[0] + T and a[1] <= b[1] + T and a[2] >= b[2] - T and a[3] >= b[3] - T) or \
                       (b[0] <= a[0] + T and b[1] <= a[1] + T and b[2] >= a[2] - T and b[3] >= a[3] - T)
            if contains:
                continue
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 2 and oy > 2 and _area_overlap(a, b) > 0.25:
                issues.append("блоки налазять один на одного (%.0f%% меншого, біля (%.0f,%.0f)) — рознеси"
                              % (100 * _area_overlap(a, b), max(a[0], b[0]), max(a[1], b[1])))
                done_bb = True
                break
        if done_bb:
            break

    return issues


def check_links(d):
    """ЛОКАЛЬНО: чи існують усі svg, які підключають .md цієї теми (стаття + вставки).
    Ловить випадок «фігуру обіцяно в тексті, а файлу нема» — без грепу агентом."""
    missing, refs = [], 0
    for md in glob.glob(os.path.join(d, "*.md")):
        try:
            s = open(md, encoding="utf-8").read()
        except Exception:
            continue
        for link in re.findall(r"!\[[^\]]*\]\(([^)]+\.svg)\)", s):
            refs += 1
            name = os.path.basename(link)
            if not os.path.exists(os.path.join(d, "img", name)):
                missing.append((os.path.basename(md), name))
    return refs, missing


def main():
    for stream in (sys.stdout, sys.stderr):           # звіт містить кирилицю — не залежати від кодування консолі
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    d = pos[0] if pos else "."
    min_font, tol = 9, 6.0
    if "--min-font" in sys.argv:
        min_font = int(sys.argv[sys.argv.index("--min-font") + 1])
    if "--tol" in sys.argv:
        tol = float(sys.argv[sys.argv.index("--tol") + 1])

    if os.path.isfile(d):
        files = [d]
    else:
        files = sorted(glob.glob(os.path.join(d, "**", "*.svg"), recursive=True))

    bad = 0
    for f in files:
        iss = check_svg(f, min_font, tol)
        if iss:
            bad += 1
            try:
                rel = os.path.relpath(f, d)
            except ValueError:
                rel = f
            print("WARN %s: %s" % (rel, "; ".join(iss[:4])))

    miss = []
    if "--links" in sys.argv and os.path.isdir(d):
        refs, miss = check_links(d)
        for md, name in miss:
            print("MISS %s: підключено img/%s, а файлу НЕМА (згенеруй у figs.py)" % (md, name))
        if refs and not miss:
            print("Підключень у .md: %d — усі файли на місці" % refs)

    print("SVG перевірено: %d; із зауваженнями: %d%s" % (len(files), bad, ("; відсутніх фігур: %d" % len(miss)) if miss else ""))
    sys.exit(1 if (bad or miss) else 0)


if __name__ == "__main__":
    main()
