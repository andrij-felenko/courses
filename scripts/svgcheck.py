# -*- coding: utf-8 -*-
"""svgcheck — швидка геометрична перевірка згенерованих SVG.
Замінює LLM-переогляд кожного файлу: textbox()/fitbox() зі svgkit уже гарантують,
що текст не вилазить за СВОЮ рамку; цей скрипт ловить інше — елементи поза viewBox
(хибні координати), нечитабельно дрібний шрифт і (v6) НАКЛАДАННЯ тексту на
чужий текст чи лінії (текст має бути поза чужими лініями й написами).

    python svgcheck.py <тека> [--min-font 9] [--tol 6]

Код виходу 0 — чисто; 1 — є зауваження (друкує стислий звіт, по 1 прикладу на тип).
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


def _seg_lines(s):
    segs = []
    for m in re.finditer(r"<line\b([^>]*)/>", s):
        a = m.group(1)

        def g(n):
            mm = re.search(r'\b%s="(-?[\d.]+)"' % n, a)
            return float(mm.group(1)) if mm else None
        p = (g("x1"), g("y1"), g("x2"), g("y2"))
        if None not in p:
            segs.append(p)
    return segs


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
        if any(_seg_hits_box(sg, box) for sg in segs):
            issues.append("лінія перетинає текст (напис не поза лініями)")
            break

    return issues


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
    print("SVG перевірено: %d; із зауваженнями: %d" % (len(files), bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
